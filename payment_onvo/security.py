"""Pure validation helpers; no credentials or customer data are logged."""
import hashlib
import hmac
import re
import time
from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import urlsplit

SUPPORTED_CURRENCIES = ('CRC', 'USD')


def minor_amount(amount):
    value = Decimal(str(amount))
    if not value.is_finite() or value <= 0:
        raise ValueError('Amount must be positive')
    return int((value * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def checkout_url(value):
    if not isinstance(value, str):
        raise ValueError('Missing checkout URL')
    parsed = urlsplit(value)
    if (parsed.scheme != 'https' or parsed.hostname not in
            ('checkout.onvopay.com', 'pay.onvopay.com', 'cart.onvopay.com')
            or parsed.username or parsed.password or parsed.port not in (None, 443)):
        raise ValueError('Invalid ONVO checkout URL')
    return value


def verify_signature(raw_body, header, secret, now=None):
    if not secret or not isinstance(header, str) or len(header) > 4096:
        return False
    pairs = [part.strip().split('=', 1) for part in header.split(',') if '=' in part]
    stamps = [v for k, v in pairs if k == 't']
    if len(stamps) != 1 or not re.fullmatch(r'[0-9]{1,12}', stamps[0]):
        return False
    stamp = int(stamps[0])
    if abs((time.time() if now is None else now) - stamp) > 300:
        return False
    expected = hmac.new(secret.encode(), str(stamp).encode() + b'.' + raw_body, hashlib.sha256).hexdigest()
    return any(re.fullmatch(r'[0-9a-fA-F]{64}', v) and hmac.compare_digest(expected, v.lower())
               for k, v in pairs if k == 'v1')


def validate_payment(data, session_id, amount, currency, mode):
    if not isinstance(data, dict) or data.get('id') != session_id:
        raise ValueError('Checkout session mismatch')
    if data.get('mode') != mode:
        raise ValueError('Checkout mode mismatch')
    if data.get('paymentStatus') != 'paid':
        return False
    if data.get('status') != 'complete':
        raise ValueError('Checkout is not complete')
    if data.get('currency', '').upper() != currency or data.get('amountTotal') != minor_amount(amount):
        raise ValueError('Checkout amount or currency mismatch')
    if not isinstance(data.get('paymentIntentId'), str) or not data['paymentIntentId']:
        raise ValueError('Missing payment intent')
    return True
