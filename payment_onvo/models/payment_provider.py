import requests
from odoo import _, api, fields, models, release
from odoo.exceptions import ValidationError
from ..security import SUPPORTED_CURRENCIES


MODE_FIELDS = ('is_live', 'is_published', 'active') if release.version_info[0] >= 20 else ('state',)


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[('onvo', 'ONVO')], ondelete={'onvo': 'set default'})
    onvo_secret_key = fields.Char(string='ONVO Secret Key', groups='base.group_system', copy=False, required_if_provider='onvo')
    onvo_webhook_secret = fields.Char(string='ONVO Webhook Signing Secret', groups='base.group_system', copy=False, required_if_provider='onvo')
    onvo_data_consent = fields.Boolean(string='Send payment information to ONVO', copy=False,
        help='Send the amount, currency, transaction reference, buyer email, integration identifier and optional referral code to ONVO to process checkout. Card details are entered on ONVO.')
    onvo_referral_code = fields.Char(string='ONVO Referral Code', groups='base.group_system',
        help='Optional ONVO-issued partner code. Sent in checkout metadata for attribution; commission eligibility is managed by ONVO.')
    onvo_webhook_url = fields.Char(compute='_compute_onvo_webhook_url')

    def _compute_onvo_webhook_url(self):
        for provider in self:
            provider.onvo_webhook_url = '%s/payment/onvo/webhook/%s' % (provider.get_base_url().rstrip('/'), provider.id)

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
                raise ValidationError(_('Use an ONVO secret key matching the provider mode.'))
            if not (provider.onvo_webhook_secret or '').startswith('whsec_'):
                raise ValidationError(_('Configure the ONVO signed webhook secret.'))
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
