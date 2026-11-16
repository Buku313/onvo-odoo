# Release record — 2026-11-16

Publisher confirmed by user: ONVOPay. Support: antonio@onvopay.com.

## Implemented and verified

- Standalone `payment_onvo`; no dependency on customer-specific code.
- Odoo 17.0.0.1.0 beta package with hosted Checkout and signed webhooks.
- Fresh Odoo 17 install succeeds.
- Pure security tests: signature rotation, stale/future timestamps, tampered bodies, redirect allowlist, minor units and payment mismatches.
- Odoo tests: checkout creation and reuse, reconciliation, repeated success notifications, amount mismatch and test/live key mismatch.

## Hosting and distribution

- Private repository: https://github.com/Buku313/onvo-odoo (branch `17.0`).
- HTTPS demo: https://onvo-odoo.18.207.41.62.sslip.io/shop
- AWS Lightsail: `onvo-odoo-demo`, us-east-1, small_3_0, USD 12/month. Static IP resource: `onvo-odoo-demo-ip`.
- ONVO provider is disabled; owner will supply test credentials later.
- Nine Odoo tests and four standalone security tests passed. GitHub CI passed on the initial release commit.
- Odoo Apps registration has NOT been submitted. Browser automation failed during the submission workflow.

## Before publication / live activation

- Free connector confirmed by publisher.
- Complete an actual ONVO test checkout, return, signed webhook and reconciliation.
- Capture real configuration and checkout screenshots.
- Authenticate Odoo Apps publisher account and register the standalone Git repository's 17.0 branch.
- Set the hosted demo URL after deployment verification.
- Use beta wording until sandbox acceptance is complete.

## Known operational constraints

- ONVO's published OpenAPI schema does not document an idempotency key for checkout creation. A network timeout after ONVO creates a session can leave an orphan session. Do not claim exactly-once creation across network or database failures.
- No automatic migration from payment_onvopaycard.
- Odoo 18/19 compatibility is not claimed.
- Refunds, subscriptions and tokenization are outside this release.

## Primary references

- https://docs.onvopay.com/en/checkout/one-time-links
- https://docs.onvopay.com/en/webhooks/verify-signatures
- https://docs.onvopay.com/en/webhooks/events
- https://docs.onvopay.com/openapi.yaml
- https://apps.odoo.com/apps/vendor-guidelines
- https://apps.odoo.com/apps/upload
- https://github.com/odoo/odoo/tree/17.0/addons/payment

## Marketplace registration

Register `ssh://git@github.com/Buku313/onvo-odoo#17.0` at https://apps.odoo.com/apps/upload after signing into the intended publisher account. The repository is private. Odoo documents granting its `online-odoo` GitHub account repository access; no scanner access has been granted yet. Prefer the narrowest access supported and verify its effective permissions before granting.

No official partner/referral code has been issued by this work. `integration=onvo_odoo` identifies traffic from the plugin. ONVO must recognize the optional referral code for any partner or commission program.
