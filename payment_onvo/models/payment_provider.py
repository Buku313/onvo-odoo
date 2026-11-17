import requests
from odoo import _, api, fields, models, release
from odoo.exceptions import ValidationError
from ..security import SUPPORTED_CURRENCIES


MODE_FIELDS = ('is_live', 'is_published', 'active') if release.version_info[0] >= 20 else ('state',)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('onvo', 'ONVO')], ondelete={'onvo': 'set default'})
    onvo_secret_key = fields.Char(string='Secret API key', groups='base.group_system', copy=False,
        required_if_provider='onvo',
        help='Copy your secret API key from the ONVO Dashboard. Use onvo_test_secret_key_... in test mode or onvo_live_secret_key_... in live mode. A public / publishable key is not needed for hosted checkout.')
    onvo_webhook_secret = fields.Char(string='Webhook signing secret', groups='base.group_system', copy=False,
        required_if_provider='onvo',
        help='Copy the whsec_... signing secret from this endpoint in ONVO > Developers > Webhooks. This is different from your API key. The endpoint and API key must use the same test or live mode.')
    onvo_data_consent = fields.Boolean(string='Send payment information to ONVO', copy=False,
        help='Send the amount, currency, transaction reference, buyer email, integration identifier and optional referral code to ONVO to process checkout. Card details are entered on ONVO.')
    onvo_referral_code = fields.Char(string='ONVO Referral Code', groups='base.group_system',
        help='Optional ONVO-issued partner code. Sent in checkout metadata for attribution; commission eligibility is managed by ONVO.')
    onvo_webhook_url = fields.Char(string='Webhook URL', compute='_compute_onvo_webhook_url',
        help='Copy this exact URL into ONVO > Developers > Webhooks. Your Odoo site must have a publicly reachable HTTPS domain on port 443. Save a new provider before copying its URL.')

    def _compute_onvo_webhook_url(self):
        for provider in self:
            provider.onvo_webhook_url = (
                '%s/payment/onvo/webhook/%s' % (provider.get_base_url().rstrip('/'), provider._origin.id)
                if provider._origin.id else False)

    def _onvo_mode(self):
        self.ensure_one()
        if release.version_info[0] >= 20:
            return 'live' if self.is_live else 'test'
        return 'test' if self.state == 'test' else 'live'

    def _onvo_enabled(self):
        self.ensure_one()
        if release.version_info[0] >= 20:
            return self.active and bool(self.onvo_secret_key and self.onvo_webhook_secret and self.onvo_data_consent)
        return self.state != 'disabled'

    def _onvo_requires_configuration(self):
        if release.version_info[0] >= 20:
            return self.active and (self.is_live or self.is_published or self.onvo_secret_key)
        return self.state != 'disabled'

    @api.constrains(*MODE_FIELDS, 'code', 'onvo_secret_key', 'onvo_webhook_secret', 'onvo_data_consent')
    def _check_onvo_configuration(self):
        for provider in self.filtered(lambda p: p.code == 'onvo' and p._onvo_requires_configuration()):
            mode = provider._onvo_mode()
            if not (provider.onvo_secret_key or '').startswith('onvo_%s_secret_' % mode):
                raise ValidationError(_(
                    'The ONVO provider is in %(mode)s mode. Paste a secret API key starting with '
                    'onvo_%(mode)s_secret_ from the ONVO Dashboard. A publishable key will not work.',
                    mode=mode))
            if not (provider.onvo_webhook_secret or '').startswith('whsec_'):
                raise ValidationError(_(
                    'Paste the whsec_... signing secret from ONVO > Developers > Webhooks. '
                    'Create a signed endpoint with the Webhook URL shown in Odoo and subscribe '
                    'to checkout_session.succeeded. This secret is different from your API key.'))
            if not provider.onvo_data_consent:
                raise ValidationError(_('Confirm the payment data transfer to ONVO before enabling checkout.'))

    def _get_default_payment_method_codes(self):
        return ['onvo'] if self.code == 'onvo' else super()._get_default_payment_method_codes()

    def _get_supported_currencies(self):
        currencies = super()._get_supported_currencies()
        return currencies.filtered(lambda c: c.name in SUPPORTED_CURRENCIES) if self.code == 'onvo' else currencies

    def _onvo_request(self, endpoint, payload=None):
        self.ensure_one()
        self._check_onvo_configuration()
        if not self._onvo_enabled():
            raise ValidationError(_('ONVO is disabled.'))
        try:
            response = requests.request('POST' if payload is not None else 'GET',
                'https://api.onvopay.com/v1/' + endpoint,
                headers={'Authorization': 'Bearer ' + self.onvo_secret_key},
                json=payload, timeout=(5, 20), allow_redirects=False)
            if not 200 <= response.status_code < 300:
                raise ValidationError(_('ONVO request failed (HTTP %s). Check your merchant configuration.', response.status_code))
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError('Invalid JSON object')
            return data
        except (requests.RequestException, ValueError) as exc:
            raise ValidationError(_('ONVO could not be reached or returned an invalid response. Please retry.')) from exc
