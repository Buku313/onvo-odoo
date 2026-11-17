"""Upgrade bundled artwork without replacing a merchant's custom images."""
import base64
from pathlib import Path
from odoo.tools import image_process


def update_default_images(env):
    static = Path(__file__).parent / 'static'
    legacy = (static / 'img/legacy_icon.png').read_bytes()
    targets = (
        ('payment_onvo.payment_method_onvo', 'image', 'img/payment_method.png'),
        ('payment_onvo.payment_provider_onvo', 'image_128', 'description/icon.png'),
    )
    for xml_id, field_name, filename in targets:
        record = env.ref(xml_id)
        current = record[field_name]
        field = record._fields[field_name]
        old_default = image_process(legacy, size=(field.max_width, field.max_height))
        if not current or base64.b64decode(current) == old_default:
            record.write({field_name: base64.b64encode((static / filename).read_bytes())})
