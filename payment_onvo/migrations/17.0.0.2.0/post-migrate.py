from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    provider = env.ref('payment_onvo.payment_provider_onvo')
    method = env.ref('payment_onvo.payment_method_onvo')
    method.active = True
    provider.write({'payment_method_ids': [(4, method.id)],
                    'module_id': env.ref('base.module_payment_onvo').id})
