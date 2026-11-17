#!/usr/bin/env bash
# Run on the existing Odoo 17 demo, after staging the new add-on in incoming/payment_onvo.
set -euo pipefail
cd /home/ubuntu/onvo-odoo
[ -f incoming/payment_onvo/__manifest__.py ]
mkdir -p backups
backup="backups/payment_onvo-$(date -u +%Y%m%dT%H%M%SZ).tar.gz"
tar -czf "$backup" payment_onvo
sudo docker compose stop odoo
cp -R incoming/payment_onvo/. payment_onvo/
if sudo docker compose run --rm -T odoo odoo -d onvo_demo -u payment_onvo --stop-after-init; then
  sudo docker compose start odoo
else
  tar -xzf "$backup"
  sudo docker compose start odoo
  exit 1
fi
