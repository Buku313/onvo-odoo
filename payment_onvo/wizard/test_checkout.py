from odoo import _, fields, models
from odoo.exceptions import ValidationError
from ..security import checkout_url


class OnvoTestCheckout(models.TransientModel):
    _name = 'payment.onvo.test.checkout'
    _description = 'ONVO sandbox checkout test'

    provider_id = fields.Many2one('payment.provider', required=True, readonly=True)
    currency = fields.Selection([('USD', 'USD 1.00'), ('CRC', 'CRC 1,000.00')],
        string='Test amount', required=True, default='USD')
    transaction_id = fields.Many2one('payment.transaction', readonly=True, copy=False)
    checkout_url = fields.Char(related='transaction_id.onvo_checkout_url', readonly=True)
    payment_state = fields.Selection(related='transaction_id.state', string='Checkout status', readonly=True)

    def _check_test(self):
        self.ensure_one()
        self.provider_id._onvo_check_self_test_access()
        if self.transaction_id and (
            self.transaction_id.provider_id != self.provider_id
            or not self.transaction_id.onvo_is_setup_test
            or self.transaction_id.currency_id.name != self.currency
            or self.transaction_id.amount != (1 if self.currency == 'USD' else 1000)
            or not self.transaction_id.reference.startswith('ONVO-SELFTEST-')
        ):
            raise ValidationError(_('This checkout does not belong to this setup test. Start a new test.'))

    def _reopen(self):
        # Re-read related values after reconciliation in its payment-write context.
        self.invalidate_recordset(['payment_state', 'checkout_url'])
        return {
            'type': 'ir.actions.act_window', 'name': _('Test Apple Pay on ONVO'),
            'res_model': self._name, 'res_id': self.id, 'view_mode': 'form',
            'view_id': self.env.ref('payment_onvo.onvo_test_checkout_form').id,
            'target': 'new',
        }

    def action_create_link(self):
        self._check_test()
        # Serialize repeated clicks on the same wizard before creating a remote session.
        self.flush_recordset()
        self.env.cr.execute('SELECT id FROM payment_onvo_test_checkout WHERE id = %s FOR UPDATE', [self.id])
        self.invalidate_recordset()
        self._check_test()
        if not self.transaction_id:
            currency = self.env['res.currency'].with_context(active_test=False).search([
                ('name', '=', self.currency)], limit=1)
            if not currency or not currency.active:
                raise ValidationError(_('Activate this test currency in Odoo or choose the other test amount.'))
            method = self.provider_id.payment_method_ids.filtered(lambda m: m.code == 'onvo' and m.active)[:1]
            if not method:
                raise ValidationError(_('Activate the ONVO payment method on this provider first.'))
            self.transaction_id = self.env['payment.transaction'].create({
                'provider_id': self.provider_id.id, 'payment_method_id': method.id,
                'reference': self.env['payment.transaction']._compute_reference(
                    'onvo', prefix='ONVO-SELFTEST-%s' % self.id),
                'amount': 1 if self.currency == 'USD' else 1000, 'currency_id': currency.id,
                'partner_id': self.env.user.partner_id.id, 'operation': 'online_redirect',
                'onvo_is_setup_test': True,
            })
        if self.transaction_id.state in ('done', 'authorized', 'cancel', 'error'):
            raise ValidationError(_('This test has finished. Close this window and start a new test.'))
        self.transaction_id._get_processing_values()
        return self._reopen()

    def action_open_checkout(self):
        self._check_test()
        if not self.checkout_url or self.payment_state in ('done', 'authorized', 'cancel', 'error'):
            raise ValidationError(_('Create a new test link before opening checkout.'))
        return {'type': 'ir.actions.act_url', 'url': checkout_url(self.checkout_url), 'target': 'new'}

    def action_check_result(self):
        self._check_test()
        if not self.transaction_id:
            raise ValidationError(_('Create a test link first.'))
        self.transaction_id._onvo_sync()
        return self._reopen()
