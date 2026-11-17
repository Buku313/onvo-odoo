import hashlib
import hmac
import json
import time
from unittest.mock import patch
from odoo.tests import HttpCase, tagged


@tagged('post_install', '-at_install')
class TestOnvoHttp(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.provider = cls.env.ref('payment_onvo.payment_provider_onvo')
        mode_values = {'state': 'test'} if 'state' in cls.provider._fields else {'is_live': False, 'is_published': True}
        cls.provider.write({**mode_values, 'onvo_secret_key':'onvo_test_secret_fixture',
            'onvo_webhook_secret':'whsec_fixture', 'onvo_data_consent':True})

    def post_event(self, event, signed=True, age=0):
        body = json.dumps(event).encode()
        stamp = str(int(time.time()) - age)
        signature = hmac.new(b'whsec_fixture', stamp.encode()+b'.'+body, hashlib.sha256).hexdigest()
        return self.url_open('/payment/onvo/webhook/%s' % self.provider.id, data=body,
            headers={'Content-Type':'application/json', 'X-Onvo-Signature':
                     't='+stamp+',v1='+signature if signed else 't=1,v1=forged'})

    def test_signed_test_event(self):
        response = self.post_event({'type':'webhook_endpoint.test','mode':'test'})
        self.assertEqual(response.status_code, 200)

    def test_forged_and_old_webhooks_rejected(self):
        event = {'type':'webhook_endpoint.test','mode':'test'}
        self.assertEqual(self.post_event(event, signed=False).status_code, 403)
        self.assertEqual(self.post_event(event, age=301).status_code, 403)

    def test_wrong_mode_rejected(self):
        self.assertEqual(self.post_event({'type':'webhook_endpoint.test','mode':'live'}).status_code, 400)

    def test_return_requires_token(self):
        self.assertEqual(self.url_open('/payment/onvo/return?tx=1&token=forged').status_code, 403)

    def test_signed_checkout_reconciles_via_api(self):
        tx = self.env['payment.transaction'].create({'provider_id':self.provider.id,
            'payment_method_id':self.env.ref('payment_onvo.payment_method_onvo').id,
            'reference':'ONVO-HTTP', 'amount':25, 'currency_id':self.env.ref('base.USD').id,
            'partner_id':self.env.ref('base.partner_admin').id, 'operation':'online_redirect',
            'state':'pending', 'onvo_session_id':'cs_http'})
        event = {'type':'checkout_session.succeeded','mode':'test','data':{'object':{'id':'cs_http'}}}
        response = {'id':'cs_http','mode':'test','paymentStatus':'paid','status':'complete',
            'amountTotal':2500,'currency':'USD','paymentIntentId':'pi_http'}
        with patch.object(type(self.provider), '_onvo_request', return_value=response):
            self.assertEqual(self.post_event(event).status_code, 200)
        tx.invalidate_recordset()
        self.assertEqual(tx.state, 'done')

    def test_setup_return_works_without_shop_session(self):
        tx = self.env['payment.transaction'].create({'provider_id':self.provider.id,
            'payment_method_id':self.env.ref('payment_onvo.payment_method_onvo').id,
            'reference':'ONVO-SELFTEST-HTTP', 'amount':1, 'currency_id':self.env.ref('base.USD').id,
            'partner_id':self.env.ref('base.partner_admin').id, 'operation':'online_redirect',
            'state':'pending', 'onvo_session_id':'cs_setup_http', 'onvo_is_setup_test':True,
            'onvo_return_token':'setup-http-token'})
        url = '/payment/onvo/return?tx=%s&token=setup-http-token' % tx.id
        with patch.object(type(self.provider), '_onvo_request', return_value={
            'id':'cs_setup_http', 'mode':'test', 'paymentStatus':'unpaid', 'status':'open'}):
            response = self.url_open(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('not confirmed yet', response.text)
        with patch.object(type(self.provider), '_onvo_request', return_value={
            'id':'cs_setup_http', 'mode':'test', 'paymentStatus':'paid', 'status':'complete',
            'amountTotal':100, 'currency':'USD', 'paymentIntentId':'pi_setup_http'}):
            response = self.url_open(url)
        self.assertIn('Your test payment is confirmed.', response.text)
        self.assertEqual(response.headers['Cache-Control'], 'no-store')
        self.assertEqual(self.url_open(url.replace('setup-http-token', 'forged')).status_code, 403)
