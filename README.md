# ONVO Checkout for Odoo

Publisher: **ONVOPay** · Support: **antonio@onvopay.com**

Standalone Odoo 17 payment provider using ONVO hosted Checkout. Version `17.0.0.1.0` is a beta. Production readiness requires an actual ONVO sandbox checkout and signed webhook delivery, beyond the automated mock API tests.

## Hosted demo

https://onvo-odoo.18.207.41.62.sslip.io/shop

The storefront is online. ONVO payment acceptance is disabled until the owner adds sandbox credentials and completes a test checkout. This is a demo, not a production store.

## Install

Copy `payment_onvo` into an Odoo 17 addons directory, restart Odoo, update the Apps list, remove the Apps filter and install **ONVO Checkout**. Odoo Community and Enterprise on your own infrastructure or Odoo.sh are supported targets. Odoo Online SaaS cannot install custom Python modules.

1. Open Accounting → Configuration → Payment Providers → ONVO.
2. Set the provider to test mode with an `onvo_test_secret_...` key.
3. Create a signed ONVO webhook at the URL displayed in the provider. Subscribe to `checkout_session.succeeded`.
4. Enter the endpoint's `whsec_...` secret and confirm the data-transfer notice.
5. Publish the provider when ready for a sandbox checkout. Complete a test payment and verify its Odoo transaction becomes Done.
6. For live use, configure a live endpoint and matching live key before enabling production mode.

The merchant's ONVO account controls which payment methods appear in hosted Checkout. This release supports CRC and USD, one-time automatic capture. It does not claim refund, saved-card, recurring billing, manual capture, POS or payout support.

## Data flow

Odoo sends amount, currency, transaction reference and buyer email directly to ONVO. Card details stay on ONVO. The connector stores session and payment identifiers in Odoo and uses no third-party telemetry or activation service. Existing `payment_onvopaycard` data is not migrated; this module is installed separately.

Browser returns are authenticated with a per-transaction random token. They cannot supply a successful payment status. Signed webhook events are checked against the raw body and a five-minute timestamp tolerance. Odoo then fetches the session using the merchant's secret key and verifies its identity, mode, amount and currency before completion. Repeated completion notifications do not re-complete the transaction. Pending sessions are also polled by a scheduled action.

## Referral attribution

Every checkout includes `integration=onvo_odoo` and the connector version in ONVO metadata. An optional ONVO-issued referral code can be configured by the administrator and is sent as `referral_code`. This is disclosed in the data-transfer notice. It does not automatically enroll a merchant into a partner program or promise commission; ONVO must confirm the attribution contract and issue the actual code.

## Local test environment

Create `.env` with a random `POSTGRES_PASSWORD`. Run:

```sh
docker compose up -d db
docker compose run --rm odoo odoo -d onvo_test -i payment_onvo --without-demo=all --test-enable --test-tags /payment_onvo --stop-after-init
python3 -m unittest discover -s tests -v
```

`compose.yaml` binds Odoo to localhost only. An internet deployment additionally requires HTTPS, a non-default administrator password, a fixed database filter, private PostgreSQL networking, backups and ONVO sandbox credentials. Never publish the default Odoo admin account.

## Release

Only `payment_onvo/` belongs in the installable ZIP. Keep the branch named `17.0` for the Odoo Apps repository scanner. Marketplace content is in `payment_onvo/static/description/`. Screenshots, live test URL and sandbox acceptance must be settled before submission. Public documentation references are listed in `docs/RELEASE.md`.

License: LGPL-3.0. ONVO and Odoo names identify the integrated services.
