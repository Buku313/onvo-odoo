"""Run in Odoo shell on the NEW demo database only. Secrets arrive via environment."""
import os
base_url = os.environ['ONVO_DEMO_URL']
admin = env.ref('base.user_admin')
admin.write({'login':'antonio@onvopay.com', 'email':'antonio@onvopay.com',
             'password':os.environ['ONVO_ADMIN_PASSWORD'], 'name':'ONVOPay Demo Administrator'})
env.company.write({'name':'ONVOPay · Odoo Sandbox', 'email':'antonio@onvopay.com',
                   'country_id':env.ref('base.cr').id, 'currency_id':env.ref('base.USD').id})
params=env['ir.config_parameter'].sudo()
params.set_param('web.base.url', base_url)
params.set_param('web.base.url.freeze', True)
params.set_param('auth_signup.invitation_scope', 'b2b')
# The public storefront contains only synthetic test data.
website=env['website'].search([], limit=1)
website.write({'name':'ONVO Checkout Demo', 'domain':base_url})
product=env['product.template'].search([('default_code','=','ONVO-DEMO-USD')], limit=1)
if not product:
 product=env['product.template'].create({'name':'ONVO Test Payment · USD 1.00', 'default_code':'ONVO-DEMO-USD',
    'type':'service', 'list_price':1.0, 'taxes_id':[(5,0,0)], 'website_published':True,
    'description_sale':'Sandbox demonstration only. No physical product or live charge.'})
website.homepage_url='/shop'
provider=env.ref('payment_onvo.payment_provider_onvo')
provider.write({'is_published':False})
secret=os.environ.get('ONVO_SECRET_KEY','')
webhook=os.environ.get('ONVO_WEBHOOK_SECRET','')
if secret and webhook:
 if not secret.startswith('onvo_test_secret_') or not webhook.startswith('whsec_'):
  raise ValueError('Only sandbox credentials are accepted by demo bootstrap')
 provider.write({'onvo_secret_key':secret,'onvo_webhook_secret':webhook,'onvo_data_consent':True,
    'state':'test','is_published':True,'onvo_referral_code':os.environ.get('ONVO_REFERRAL_CODE','')})
env.cr.commit()
print('Demo initialized; ONVO provider state:',provider.state)
print('Webhook URL:',provider.onvo_webhook_url)
