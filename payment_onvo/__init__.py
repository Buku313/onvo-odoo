from . import controllers, models, wizard
from odoo.addons.payment import setup_provider, reset_payment_provider


def post_init_hook(env):
    setup_provider(env, 'onvo')


def uninstall_hook(env):
    reset_payment_provider(env, 'onvo')
