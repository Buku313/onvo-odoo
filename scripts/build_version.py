#!/usr/bin/env python3
"""Build a versioned Odoo add-on from this branch without changing the source tree."""
import argparse
import ast
import hashlib
from pathlib import Path
import shutil
import zipfile

SUPPORTED = (17, 18, 19, 20)


def build(version, destination):
    if version not in SUPPORTED:
        raise ValueError('Only tested Odoo major versions may be built')
    root = Path(__file__).resolve().parents[1]
    source = root / 'payment_onvo'
    target = destination / 'payment_onvo'
    if target.exists():
        raise FileExistsError(f'Refusing to overwrite {target}')
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    manifest_path = target / '__manifest__.py'
    manifest = ast.literal_eval(manifest_path.read_text())
    old_version = manifest['version']
    version_string = f'{version}.0.0.2.0'
    manifest_path.write_text(manifest_path.read_text().replace(old_version, version_string))
    (target / 'const.py').write_text(f'INTEGRATION_VERSION = {version_string!r}\n')
    cron = target / 'data/ir_cron.xml'
    text = cron.read_text().replace('<field name="numbercall">-1</field>', '')
    if version == 17:
        text = text.replace('</record>', '<field name="numbercall">-1</field>\n</record>')
    cron.write_text(text)
    if version >= 20:
        provider_data = target / 'data/payment_provider_data.xml'
        provider_data.write_text('''<odoo noupdate="1">
<record id="payment_provider_onvo" model="payment.provider">
<field name="name">ONVO</field><field name="code">onvo</field>
<field name="is_live" eval="False"/><field name="is_published" eval="False"/>
<field name="module_id" ref="base.module_payment_onvo"/>
<field name="redirect_form_view_id" ref="redirect_form"/>
</record>
<record id="payment_method_onvo" model="payment.method">
<field name="name">ONVO</field><field name="code">onvo</field><field name="sequence">20</field><field name="active" eval="True"/><field name="image" type="base64" file="payment_onvo/static/description/icon.png"/>
<field name="provider_id" ref="payment_provider_onvo"/>
</record>
</odoo>
''')
        view = target / 'views/payment_provider_views.xml'
        view.write_text(view.read_text().replace("state != 'disabled'", "(is_live or is_published)"))
    migration_root = target / 'migrations'
    for migration in list(migration_root.iterdir()):
        if migration.is_dir():
            migration.rename(migration_root / version_string) if migration.name != version_string else None
    description = target / 'static/description/index.html'
    import re
    text = re.sub(r'Odoo (?:17|18|19|20)(?!\d)', f'Odoo {version}', description.read_text())
    description.write_text(text)
    return target, version_string


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('version', type=int, choices=SUPPORTED)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--zip', action='store_true')
    args = parser.parse_args()
    target, version = build(args.version, args.output.resolve())
    if args.zip:
        archive = args.output / f'payment_onvo-{version}.zip'
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            for path in sorted(target.rglob('*')):
                if path.is_file():
                    z.write(path, path.relative_to(target.parent))
        archive.with_suffix('.zip.sha256').write_text(hashlib.sha256(archive.read_bytes()).hexdigest() + '  ' + archive.name + '\n')
        print(archive)
    else:
        print(target)


if __name__ == '__main__':
    main()
