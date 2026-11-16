"""Demo-only presentation; run using Odoo shell on onvo_demo."""
assert env.cr.dbname == 'onvo_demo', 'This script is only for the demo database'
views = [
 ('onvo_demo.sandbox_banner', 'ONVO demo sandbox notice', 'website.layout', '''
<xpath expr="//main" position="before">
  <div class="alert alert-info mb-0 rounded-0 text-center" role="status">
    <strong>ONVO sandbox demo</strong> — No real charges.
    <span t-if="request.env.ref('payment_onvo.payment_provider_onvo').sudo().state == 'disabled'">
      Test checkout is awaiting account setup. You can browse the demo store now.
    </span>
  </div>
</xpath>'''),
 ('onvo_demo.payment_setup_notice', 'ONVO demo checkout setup notice', 'website_sale.payment', '''
<xpath expr="//t[@name='website_sale_non_free_cart']/div[@t-else]" position="replace">
  <div t-else="" class="alert alert-info mt-4" role="status">
    <t t-set="hide_payment_button" t-value="True"/>
    <t t-if="request.env.ref('payment_onvo.payment_provider_onvo').sudo().state == 'disabled'">
      <strong>ONVO test checkout is not active yet.</strong>
      <p class="mb-0">This demo is waiting for its ONVO sandbox account setup. Your order has not been charged. You can continue browsing and return when test payments are enabled.</p>
    </t>
    <t t-else="">
      <strong>No payment method is available for this order.</strong>
      <p class="mb-0">Contact antonio@onvopay.com for help with this sandbox demo.</p>
    </t>
  </div>
</xpath>'''),
]
for key, name, parent, arch in views:
 view = env['ir.ui.view'].search([('key','=',key)], limit=1)
 values={'name':name,'key':key,'type':'qweb','inherit_id':env.ref(parent).id,'arch_db':arch,'active':True}
 if view: view.write(values)
 else: env['ir.ui.view'].create(values)
env.cr.commit()
print('Sandbox banner and checkout setup message installed.')
