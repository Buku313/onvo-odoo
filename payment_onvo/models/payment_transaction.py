import logging
from datetime import timedelta
import secrets
from urllib.parse import quote, urlencode
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from ..security import checkout_url, minor_amount, validate_payment, SUPPORTED_CURRENCIES

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    onvo_next_sync = fields.Datetime(default=fields.Datetime.now, copy=False, index=True)
    onvo_session_id = fields.Char(copy=False, readonly=True, index=True)
    onvo_checkout_url = fields.Char(copy=False, readonly=True, groups='base.group_system')
    onvo_return_token = fields.Char(copy=False, readonly=True, groups='base.group_system')

    _sql_constraints = [('onvo_session_unique', 'unique(provider_id, onvo_session_id)', 'An ONVO session can only belong to one transaction.')]

    def _onvo_lock(self):
        self.ensure_one()
        self.env.cr.execute('SELECT id FROM payment_transaction WHERE id = %s FOR UPDATE', [self.id])
        self.invalidate_recordset()

    def _get_specific_rendering_values(self, processing_values):
        result = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'onvo':
            return result
        self._onvo_lock()
        if self.state in ('done', 'authorized', 'cancel', 'error'):
            raise ValidationError(_('This payment is no longer available for checkout.'))
        if self.currency_id.name not in SUPPORTED_CURRENCIES or self.operation != 'online_redirect':
            raise ValidationError(_('ONVO supports one-time redirect payments in CRC and USD.'))
        if self.onvo_session_id:
            return {'api_url': checkout_url(self.onvo_checkout_url)}
        token = secrets.token_urlsafe(32)
        return_url = self.provider_id.get_base_url().rstrip('/') + '/payment/onvo/return?' + urlencode({'tx': self.id, 'token': token})
        session = self.provider_id._onvo_request('checkout/sessions/one-time-link', {
            'lineItems': [{'quantity': 1, 'unitAmount': minor_amount(self.amount), 'currency': self.currency_id.name, 'description': self.reference}],
            'customerEmail': self.partner_email or '',
            'redirectUrl': return_url, 'cancelUrl': return_url,
            'captureMethod': 'automatic',
            'metadata': {'odoo_reference': self.reference, 'integration': 'onvo_odoo',
                         'integration_version': '17.0.0.1.0',
                         'referral_code': self.provider_id.onvo_referral_code or ''},
        })
        if not isinstance(session.get('id'), str) or not session['id']:
            raise ValidationError(_('ONVO did not return a checkout session.'))
        try:
            url = checkout_url(session.get('url'))
        except ValueError as exc:
            raise ValidationError(_('ONVO returned an invalid checkout URL.')) from exc
        self.write({'onvo_session_id': session['id'], 'onvo_checkout_url': url, 'onvo_return_token': token})
        self._set_pending()
        return {'api_url': url}

    def _onvo_sync(self):
        self.ensure_one()
        self._onvo_lock()
        if self.provider_code != 'onvo' or not self.onvo_session_id or self.state == 'done':
            return
        data = self.provider_id._onvo_request('checkout/sessions/' + quote(self.onvo_session_id, safe=''))
        try:
            paid = validate_payment(data, self.onvo_session_id, self.amount, self.currency_id.name,
                                    'test' if self.provider_id.state == 'test' else 'live')
        except ValueError as exc:
            raise ValidationError(_('ONVO payment verification failed: %s', str(exc))) from exc
        if paid:
            self.provider_reference = data['paymentIntentId']
            self._set_done(extra_allowed_states=('cancel', 'error'))
        elif data.get('status') == 'expired':
            self._set_canceled()
        elif self.state == 'draft':
            self._set_pending()

    @api.model
    def _cron_onvo_sync(self):
        transactions = self.search([('provider_code', '=', 'onvo'), ('state', '=', 'pending'),
            ('onvo_session_id', '!=', False), ('provider_id.state', '!=', 'disabled'),
            ('onvo_next_sync', '<=', fields.Datetime.now())], limit=50, order='onvo_next_sync, id')
        for tx in transactions:
            tx.onvo_next_sync = fields.Datetime.now() + timedelta(minutes=5)
            try:
                with self.env.cr.savepoint():
                    tx._onvo_sync()
            except ValidationError:
                _logger.warning('ONVO reconciliation deferred for transaction %s', tx.id)
