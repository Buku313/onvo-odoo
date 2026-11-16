import hashlib
import hmac
import importlib.util
import unittest
from pathlib import Path
spec = importlib.util.spec_from_file_location('security', Path(__file__).parents[1] / 'payment_onvo/security.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


class SecurityTests(unittest.TestCase):
    def test_signature_and_rotation(self):
        body = b'{"id":"evt_1"}'
        signature = hmac.new(b'whsec_test', b'1000.' + body, hashlib.sha256).hexdigest()
        header = 't=1000,v1=' + '0' * 64 + ',v1=' + signature
        self.assertTrue(s.verify_signature(body, header, 'whsec_test', now=1000))
        for payload, head, secret, now in [(body+b' ', header, 'whsec_test', 1000),
            (body, header, 'wrong', 1000), (body, header, 'whsec_test', 1301),
            (body, header, 'whsec_test', 699), (body, header+',t=1000', 'whsec_test', 1000),
            (body, 't=nan,v1=bad', 'whsec_test', 1000)]:
            self.assertFalse(s.verify_signature(payload, head, secret, now=now))

    def test_exact_amounts(self):
        self.assertEqual(s.minor_amount('2100.89'), 210089)
        self.assertEqual(s.minor_amount(0.29), 29)
        for value in [0, -1, 'NaN', 'Infinity']:
            with self.assertRaises(ValueError): s.minor_amount(value)

    def test_redirect_allowlist(self):
        self.assertEqual(s.checkout_url('https://checkout.onvopay.com/pay/123'), 'https://checkout.onvopay.com/pay/123')
        for value in ['https://checkout.onvopay.com.evil.test/', 'http://checkout.onvopay.com/',
                      'https://evil.test', 'https://user@checkout.onvopay.com/', '//checkout.onvopay.com/', None]:
            with self.assertRaises(ValueError): s.checkout_url(value)

    def test_payment_validation(self):
        data = {'id':'cs_1', 'mode':'test', 'status':'complete', 'paymentStatus':'paid',
                'amountTotal':210089, 'currency':'CRC', 'paymentIntentId':'pi_1'}
        self.assertTrue(s.validate_payment(data, 'cs_1', '2100.89', 'CRC', 'test'))
        for key, value in [('id','other'),('mode','live'),('amountTotal',1),('currency','USD'),
                           ('status','open'),('paymentIntentId','')]:
            with self.assertRaises(ValueError):
                s.validate_payment(dict(data, **{key:value}), 'cs_1', '2100.89', 'CRC', 'test')
        self.assertFalse(s.validate_payment(dict(data, paymentStatus='unpaid'), 'cs_1', '2100.89', 'CRC', 'test'))
