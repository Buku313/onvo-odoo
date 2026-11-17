"""Upgrade bundled artwork without replacing a merchant's custom images."""
import base64
from pathlib import Path


def update_default_images(env):
    static = Path(__file__).parent / 'static'
    legacy = base64.b64encode((static / 'img/legacy_icon.png').read_bytes())
    targets = (
        ('payment_onvo.payment_method_onvo', 'image', 'img/payment_method.png'),
        ('payment_onvo.payment_provider_onvo', 'image_128', 'description/icon.png'),
    )
    for xml_id, field_name, filename in targets:
        record = env.ref(xml_id)
        current = record[field_name]
        old_default = record._fields[field_name].convert_to_cache(legacy, record)
        if not current or base64.b64decode(current) == base64.b64decode(old_default):
            record.write({field_name: base64.b64encode((static / filename).read_bytes())})
