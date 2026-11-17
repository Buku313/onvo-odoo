# Release record — 2026-11-17

Publisher: ONVOPay · Support: antonio@onvopay.com · Free · LGPL-3

## Compatibility release 0.2.0 (beta)

| Odoo | Add-on version | Test runtime | Result |
| --- | --- | --- | --- |
| 17 | 17.0.0.2.0 | Official Odoo 17 / PostgreSQL 15 | Passed |
| 18 | 18.0.0.2.0 | Official Odoo 18 / PostgreSQL 15 | Passed |
| 19 | 19.0.0.2.0 | Official Odoo 19 / PostgreSQL 15 | Passed |
| 20 | 20.0.0.2.0 | Official Odoo 20 / PostgreSQL 16 | Passed |

Evidence: https://github.com/Buku313/onvo-odoo/actions/runs/44115523495
Tested common source commit: `5951b8decbf2a43e66a5f030023dd5484f0f9276`.

The suite runs a fresh module installation, Odoo rendering of the checkout redirect, provider/payment-method registration, session reuse and database uniqueness, signed HTTP webhooks, rejected forged/stale/wrong-mode callbacks, amount validation, duplicate success handling, mode/key checks, and scheduled reconciliation. Four standalone security tests cover signature rotation/tampering, URL restrictions and money validation. ONVO API responses are mocked. Proprietary Enterprise is not separately exercised.

The first-beta Odoo 17 local demo database was also upgraded successfully: its payment method association was repaired and the provider remained disabled with no credentials changed.

## Changes

- Explicitly associate the ONVO payment method and module with the provider; fixes missing checkout-method availability in the first beta.
- Supply the payment method icon and active state.
- Support Odoo 18+ scheduled-action schema and Odoo 19+ database constraints.
- Adapt to Odoo 20's Live switch, provider-owned payment methods and replay-safe payment-write contract.
- Use the actual version in ONVO attribution metadata.
- Produce one add-on folder, ZIP and marketplace branch for each major version.
- Add the exact private-repository submission instructions in ODOO_APPS_UPLOAD.md.

## Hosting and publication

Private repository: https://github.com/Buku313/onvo-odoo

Hosted Odoo 17 demo: https://onvo-odoo.18.207.41.62.sslip.io/shop

AWS Lightsail instance: `onvo-odoo-demo`, us-east-1, small_3_0, USD 12/month. Static IP: `onvo-odoo-demo-ip`. The owner explicitly requested keeping the server on 2026-11-17. It has not been deleted.

The ONVO provider remains disabled while the owner supplies sandbox credentials. Odoo Apps registration is NOT submitted and no marketplace scanner access has been granted. These account steps are explained in ODOO_APPS_UPLOAD.md.

## Before production activation

- Configure dedicated ONVO sandbox credentials and signed webhook endpoint.
- Verify an actual complete payment, return, webhook retry and reconciliation.
- Capture real screenshots for the listing and remove beta wording only after acceptance.
- Have ONVO issue/recognize the actual referral code. `integration=onvo_odoo` is an attribution identifier, not automatic commission enrollment.

## Known scope

CRC/USD one-time hosted payments only. No saved cards, recurring billing, refunds from Odoo, manual capture, POS or payouts. No automatic migration from `payment_onvopaycard`. Future Odoo major versions require separate validation. Odoo Online SaaS does not accept this custom Python add-on.

ONVO's published checkout-creation schema does not document an idempotency key. An ambiguous timeout or rolled-back database write can leave an unrecorded ONVO session; exactly-once session creation is not claimed. Reconciliation itself uses a read-only API request and is safe to replay.

## Primary references

- https://www.odoo.com/documentation/20.0/administration/supported_versions.html
- https://github.com/odoo/odoo/tree/20.0/addons/payment
- https://docs.onvopay.com/en/checkout/one-time-links
- https://docs.onvopay.com/en/webhooks/verify-signatures
- https://docs.onvopay.com/en/webhooks/events
- https://apps.odoo.com/apps/vendor-guidelines
- https://apps.odoo.com/apps/upload
- https://apps.odoo.com/apps/faq
