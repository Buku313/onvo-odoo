from unittest.mock import patch
from psycopg2 import IntegrityError
from odoo.tools import mute_logger
from ..const import INTEGRATION_VERSION
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import AccessError, ValidationError


@tagged('post_install', '-at_install')
class TestOnvo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.provider = cls.env.ref('payment_onvo.payment_provider_onvo')
        mode_values = {'state': 'test'} if 'state' in cls.provider._fields else {'is_live': False, 'is_published': True}
        cls.provider.write({**mode_values, 'onvo_secret_key':'onvo_test_secret_fixture',
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
            result = tx._get_processing_values()
            self.assertEqual(tx.state, 'pending')
            self.assertIn('https://checkout.onvopay.com/pay/cs_test', result['redirect_form_html'])
            self.assertEqual(api.call_args.args[1]['lineItems'][0]['unitAmount'], 2500)
            self.assertEqual(api.call_args.args[1]['metadata']['integration_version'], INTEGRATION_VERSION)
            values = tx._get_processing_values()
            self.assertIn('https://checkout.onvopay.com/pay/cs_test', values['redirect_form_html'])
            self.assertEqual(api.call_count, 1)

    def test_reconciliation_and_duplicate(self):
        tx = self.make_tx()
        tx.with_context(payment_safe_write=True).write({'onvo_session_id':'cs_test', 'state':'pending'})
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
        tx.with_context(payment_safe_write=True).write({'onvo_session_id':'cs_test', 'state':'pending'})
        response = {'id':'cs_test', 'mode':'test', 'paymentStatus':'paid', 'status':'complete',
                    'amountTotal':1, 'currency':'USD', 'paymentIntentId':'pi_test'}
        with patch.object(type(self.provider), '_onvo_request', return_value=response):
            with self.assertRaises(ValidationError): tx._onvo_sync()
        self.assertEqual(tx.state, 'pending')

    def test_test_mode_rejects_live_key(self):
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            self.provider.onvo_secret_key = 'onvo_live_secret_fixture'

    def test_webhook_url_uses_saved_provider_identity(self):
        with patch.object(type(self.provider), 'get_base_url', return_value='https://shop.example.com/'):
            self.provider.invalidate_recordset(['onvo_webhook_url'])
            expected = 'https://shop.example.com/payment/onvo/webhook/%s' % self.provider.id
            self.assertEqual(self.provider.onvo_webhook_url, expected)
            draft = self.provider.new({}, origin=self.provider)
            self.assertEqual(draft.onvo_webhook_url, expected)
            self.assertFalse(self.provider.new({}).onvo_webhook_url)

    def test_session_uniqueness_is_enforced(self):
        tx = self.make_tx()
        tx.with_context(payment_safe_write=True).write({'onvo_session_id': 'cs_unique'})
        self.env.flush_all()
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'), self.env.cr.savepoint():
            other = tx.copy({'reference': 'ONVO-OTHER', 'onvo_session_id': 'cs_unique'})
            other.flush_recordset()

    def test_provider_is_registered_for_redirect_checkout(self):
        self.assertIn(self.method, self.provider.payment_method_ids)
        self.assertEqual(self.provider.redirect_form_view_id, self.env.ref('payment_onvo.redirect_form'))
        self.assertTrue(self.env.ref('payment_onvo.ir_cron_onvo_sync').active)

    def test_scheduled_reconciliation(self):
        tx = self.make_tx()
        tx.with_context(payment_safe_write=True).write({'onvo_session_id': 'cs_cron', 'state': 'pending'})
        response = {'id': 'cs_cron', 'mode': 'test', 'paymentStatus': 'paid', 'status': 'complete',
                    'amountTotal': 2500, 'currency': 'USD', 'paymentIntentId': 'pi_cron'}
        with patch.object(type(self.provider), '_onvo_request', return_value=response):
            self.env['payment.transaction']._cron_onvo_sync()
        self.assertEqual(tx.state, 'done')

    def make_setup_test(self, currency='USD'):
        return self.env['payment.onvo.test.checkout'].create({
            'provider_id': self.provider.id, 'currency': currency})

    def test_setup_link_reuses_session_and_checks_payment(self):
        wizard = self.make_setup_test()
        with patch.object(type(self.provider), '_onvo_request', return_value={
            'id': 'cs_setup', 'url': 'https://checkout.onvopay.com/pay/cs_setup'}) as api:
            wizard.action_create_link()
            wizard.action_create_link()
            self.assertEqual(api.call_count, 1)
            self.assertEqual(api.call_args.args[1]['lineItems'][0]['unitAmount'], 100)
            self.assertEqual(wizard.payment_state, 'pending')
            self.assertEqual(wizard.action_open_checkout()['url'], 'https://checkout.onvopay.com/pay/cs_setup')
        with patch.object(type(self.provider), '_onvo_request', return_value={
            'id': 'cs_setup', 'mode': 'test', 'status': 'complete', 'paymentStatus': 'paid',
            'amountTotal': 100, 'currency': 'USD', 'paymentIntentId': 'pi_setup'}):
            wizard.action_check_result()
        self.assertEqual(wizard.transaction_id.state, 'done')
        self.assertEqual(wizard.payment_state, 'done')
        with self.assertRaises(ValidationError):
            wizard.action_open_checkout()

    def test_setup_link_crc_total(self):
        self.env.ref('base.CRC').active = True
        wizard = self.make_setup_test('CRC')
        with patch.object(type(self.provider), '_onvo_request', return_value={
            'id': 'cs_setup_crc', 'url': 'https://checkout.onvopay.com/pay/cs_setup_crc'}) as api:
            wizard.action_create_link()
            item = api.call_args.args[1]['lineItems'][0]
            self.assertEqual((item['unitAmount'], item['currency']), (100000, 'CRC'))

    def test_setup_link_rejects_live_mode_before_api_call(self):
        wizard = self.make_setup_test()
        live_values = {'state': 'enabled'} if 'state' in self.provider._fields else {'is_live': True}
        self.provider.write({**live_values, 'onvo_secret_key': 'onvo_live_secret_fixture'})
        with patch.object(type(self.provider), '_onvo_request') as api:
            with self.assertRaises(ValidationError):
                wizard.action_create_link()
            with self.assertRaises(ValidationError):
                self.provider.action_onvo_test_checkout()
            api.assert_not_called()

    def test_setup_link_rejects_public_user(self):
        public = self.env.ref('base.public_user')
        with patch.object(type(self.provider), '_onvo_request') as api:
            with self.assertRaises(AccessError):
                self.provider.with_user(public).action_onvo_test_checkout()
            with self.assertRaises(AccessError):
                self.env['payment.onvo.test.checkout'].with_user(public).create({
                    'provider_id': self.provider.id, 'currency': 'USD'})
            api.assert_not_called()

    def test_setup_link_cannot_attach_unrelated_transaction(self):
        wizard = self.make_setup_test()
        wizard.transaction_id = self.make_tx()
        with patch.object(type(self.provider), '_onvo_request') as api:
            with self.assertRaises(ValidationError):
                wizard.action_check_result()
            api.assert_not_called()
