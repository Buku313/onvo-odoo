from unittest.mock import patch
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestOnvo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.provider = cls.env.ref('payment_onvo.payment_provider_onvo')
        cls.provider.write({'state':'test', 'onvo_secret_key':'onvo_test_secret_fixture',
            'onvo_webhook_secret':'whsec_fixture', 'onvo_data_consent':True})
        cls.partner = cls.env['res.partner'].create({'name':'Checkout Test', 'email':'test@example.com'})
        cls.method = cls.env.ref('payment_onvo.payment_method_onvo')

    def make_tx(self):
        return self.env['payment.transaction'].create({'provider_id':self.provider.id,
            'payment_method_id':self.method.id, 'reference':'ONVO-TEST', 'amount':25,
            'currency_id':self.env.ref('base.USD').id, 'partner_id':self.partner.id,
            'operation':'online_redirect'})

    def test_create_and_reuse_checkout(self):
        tx = self.make_tx()
        with patch.object(type(self.provider), '_onvo_request', return_value={
            'id':'cs_test', 'url':'https://checkout.onvopay.com/pay/cs_test'}) as api:
            result = tx._get_specific_rendering_values({})
            self.assertEqual(tx.state, 'pending')
            self.assertEqual(result['api_url'], 'https://checkout.onvopay.com/pay/cs_test')
            self.assertEqual(api.call_args.args[1]['lineItems'][0]['unitAmount'], 2500)
            tx._get_specific_rendering_values({})
            self.assertEqual(api.call_count, 1)

    def test_reconciliation_and_duplicate(self):
        tx = self.make_tx()
        tx.write({'onvo_session_id':'cs_test', 'state':'pending'})
        response = {'id':'cs_test', 'mode':'test', 'paymentStatus':'paid', 'status':'complete',
                    'amountTotal':2500, 'currency':'USD', 'paymentIntentId':'pi_test'}
        with patch.object(type(self.provider), '_onvo_request', return_value=response) as api:
            tx._onvo_sync()
            self.assertEqual(tx.state, 'done')
            self.assertEqual(tx.provider_reference, 'pi_test')
            tx._onvo_sync()
            self.assertEqual(api.call_count, 1)

    def test_mismatch_never_marks_paid(self):
        tx = self.make_tx()
        tx.write({'onvo_session_id':'cs_test', 'state':'pending'})
        response = {'id':'cs_test', 'mode':'test', 'paymentStatus':'paid', 'status':'complete',
                    'amountTotal':1, 'currency':'USD', 'paymentIntentId':'pi_test'}
        with patch.object(type(self.provider), '_onvo_request', return_value=response):
            with self.assertRaises(ValidationError): tx._onvo_sync()
        self.assertEqual(tx.state, 'pending')

    def test_test_mode_rejects_live_key(self):
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.provider.onvo_secret_key = 'onvo_live_secret_fixture'
