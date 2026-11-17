import hmac
import json
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError
from werkzeug.exceptions import BadRequest, Forbidden, ServiceUnavailable
from ..security import verify_signature


class OnvoController(http.Controller):
    @http.route('/payment/onvo/return', type='http', auth='public', methods=['GET'], save_session=False)
    def payment_return(self, tx=None, token='', **kwargs):
        try:
            transaction = request.env['payment.transaction'].sudo().browse(int(tx)).exists()
        except (ValueError, TypeError):
            raise Forbidden()
        if (not transaction or transaction.provider_code != 'onvo' or not token
                or not token.isascii() or not hmac.compare_digest(transaction.onvo_return_token or '', token)):
            raise Forbidden()
        # Browser parameters never establish the payment result.
        try:
            transaction._onvo_sync()
        except ValidationError:
            pass  # A signed webhook or the reconciliation job can recover later.
        response = request.redirect('/payment/status', 303)
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Cache-Control'] = 'no-store'
        return response

    @http.route('/payment/onvo/webhook/<int:provider_id>', type='http', auth='public', methods=['POST'], csrf=False, save_session=False)
    def webhook(self, provider_id, **kwargs):
        provider = request.env['payment.provider'].sudo().browse(provider_id).exists()
        if not provider or provider.code != 'onvo' or not provider._onvo_enabled():
            raise Forbidden()
        raw = request.httprequest.get_data()
        if len(raw) > 262144:
            raise BadRequest()
        if not verify_signature(raw, request.httprequest.headers.get('X-Onvo-Signature', ''), provider.onvo_webhook_secret):
            raise Forbidden()
        try:
            event = json.loads(raw)
            if not isinstance(event, dict):
                raise ValueError()
            if event.get('mode') != provider._onvo_mode():
                raise ValueError()
            if event.get('type') == 'webhook_endpoint.test':
                return request.make_json_response({'received': True})
            if event.get('type') != 'checkout_session.succeeded':
                return request.make_json_response({'received': True})
            obj = event['data']['object']
            if not isinstance(obj, dict) or not isinstance(obj.get('id'), str) or not obj['id']:
                raise ValueError()
        except (ValueError, KeyError, TypeError):
            raise BadRequest()
        transaction = request.env['payment.transaction'].sudo().search([
            ('provider_id', '=', provider.id), ('onvo_session_id', '=', obj['id'])], limit=1)
        if transaction:
            try:
                transaction._onvo_sync()
            except ValidationError:
                # Non-2xx asks ONVO to retry. Never accept a failed reconciliation silently.
                raise ServiceUnavailable()
        return request.make_json_response({'received': True})
