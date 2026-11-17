from odoo import api, SUPERUSER_ID
from odoo.addons.payment_onvo.branding import update_default_images


def migrate(cr, version):
    update_default_images(api.Environment(cr, SUPERUSER_ID, {}))
