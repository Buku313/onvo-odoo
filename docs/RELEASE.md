# Release record — 2026-11-17

Publisher: ONVOPay · Support: antonio@onvopay.com · Free · LGPL-3

## Apple Pay self-service release 0.5.0 (beta)

- Add an Apple Pay provider tab with ONVO Dashboard activation steps, device troubleshooting and live-mode guidance.
- Add an administrator-only sandbox wizard for USD 1.00 / CRC 1,000.00 test links. Repeated clicks reuse the test session; the link can be copied to an Apple device.
- Add a payment-result check through the existing server-side reconciliation. Checkout completion is not presented as proof of wallet identity or Apple Pay activation.
- Reject live mode, non-administrators, mismatched test transactions and disallowed companies before any test checkout request.
- Add a token-protected test return page that works without the original shop session or a sales order.

Local Odoo 17 upgrade and all 19 integration tests passed, plus four standalone security tests. The suite covers test totals, reuse, payment-result refresh, live-mode and public-user rejection, transaction binding and cross-device return verification. Odoo 20 uses its new `ir.access` format with an administrator grant and an owner-only record rule for the transient wizard.

| Odoo | Tested commit | Successful CI run |
| --- | --- | --- |
| 17 | `a797952` | https://github.com/Buku313/onvo-odoo/actions/runs/44157735898 (all four versions) |
| 18 | `efae2ac` | https://github.com/Buku313/onvo-odoo/actions/runs/44157736285 |
| 19 | `755573f` | https://github.com/Buku313/onvo-odoo/actions/runs/44157736696 |
| 20 | `2710b8a` | https://github.com/Buku313/onvo-odoo/actions/runs/44157736228 |

The comprehensive B2B document-payment model, terms catalog and implementation plan are proposals. They cover merchant/customer-configurable deposits and terms; no B2B policies, customer invoices or outbound messages were activated by the planning work.

The retained Odoo 17 demo was upgraded to 17.0.0.5.0 after all compatibility runs passed. Its administrator test wizard created an actual ONVO sandbox session, reused it on a repeated action, rendered a token-protected return page with HTTP 200 without a shop session, and refreshed the state after the session was expired. The provider remained published in test mode. No card/Wallet charge was submitted; full Apple Pay acceptance still requires a merchant/device test.

## Payment branding release 0.4.0 (beta)

- Use ONVO's current public wordmark in a compact checkout badge and square provider/app icon.
- Supply the payment-method image and provider image on new installations for Odoo 17–20.
- Upgrade the old bundled image and fill missing images, while retaining merchant-customized artwork and all payment settings.
- Document the hosted Apple Pay rollout and a separate optional embedded SDK implementation in APPLE_PAY_PLAN.md. This release does not activate Apple Pay or accept merchant terms.

The hosted provider has since been enabled in test mode using the owner's credentials. ONVO accepted the API key, actual sandbox Checkout session creation and redirect rendering succeeded, and the smoke session was expired/cancelled. A locally generated signed webhook probe returned 200 and an unsigned probe returned 403. These probes do not establish delivery from ONVO or a completed card/wallet payment.

Validation: the Odoo 17 upgrade and all 13 integration tests passed. The artwork migration was separately checked against Odoo's resized images: legacy defaults are replaced, missing provider images are filled, custom artwork is retained, and payment settings are unchanged. Four standalone security tests passed. Fresh-install CI passed for every version:

| Odoo | Tested commit | Successful CI run |
| --- | --- | --- |
| 17 | `c643fff` | https://github.com/Buku313/onvo-odoo/actions/runs/44151355299 (all four versions) |
| 18 | `29bc528` | https://github.com/Buku313/onvo-odoo/actions/runs/44151562783 |
| 19 | `1920869` | https://github.com/Buku313/onvo-odoo/actions/runs/44151562540 |
| 20 | `eb3d025` | https://github.com/Buku313/onvo-odoo/actions/runs/44151563191 |

Hosted Odoo 17 was upgraded to 17.0.0.4.0. Both image fields match the new artwork after Odoo resizing. The public checkout payment-method image was downloaded and verified against the stored field. The shop returned HTTP 200 and the provider remained published in test mode. The provider's administration image is access-controlled; anonymous requests for that image return Odoo's placeholder, while the public payment-method image is available normally.

## Setup and marketplace release 0.3.0 (beta)

- Add the shared ONVO cover to the manifest and HTML listing for every supported major version.
- Organize credentials into three numbered steps, with masked fields, key examples and a native copy button for the webhook URL.
- Explain ONVO Dashboard endpoint creation, the exact event, signed format, HTTPS requirements, test connection and the test-to-live transition.
- Give actionable mode/key and webhook-secret errors without exposing secret values.
- Keep unsaved providers from presenting invalid webhook URLs; retain the correct URL while editing a saved provider.
- Derive package versions from the manifest and retain each migration's original release suffix when building other Odoo versions.

Local Odoo 17 installation and all 13 integration tests passed, along with four standalone security tests. The common source and each marketplace branch passed GitHub Actions on the corresponding official Odoo images. API responses are mocked; real ONVO sandbox acceptance still needs the owner's test credentials.

| Odoo | Version | Tested source | Successful CI run |
| --- | --- | --- | --- |
| 17 | 17.0.0.3.0 | `72edf54` | https://github.com/Buku313/onvo-odoo/actions/runs/44136506036 (all four versions) |
| 18 | 18.0.0.3.0 | `6028eb2` | https://github.com/Buku313/onvo-odoo/actions/runs/44136506371 |
| 19 | 19.0.0.3.0 | `dc91905` | https://github.com/Buku313/onvo-odoo/actions/runs/44136508563 |
| 20 | 20.0.0.3.0 | `d7fd03e` | https://github.com/Buku313/onvo-odoo/actions/runs/44136506288 |

The retained Odoo 17 demo was upgraded successfully to 17.0.0.3.0 with a source backup. Its ONVO provider remains disabled awaiting sandbox credentials. All four source branches include the cover and new description. Refresh them with **Scan** in Odoo Apps **My Repos**; the browser's automatic approval review failed before access to those controls, so the scans were not triggered by this release workflow.

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

Repository: https://github.com/Buku313/onvo-odoo (currently public; visibility not changed by this release)

Hosted Odoo 17 demo: https://onvo-odoo.18.207.41.62.sslip.io/shop

AWS Lightsail instance: `onvo-odoo-demo`, us-east-1, small_3_0, USD 12/month. Static IP: `onvo-odoo-demo-ip`. The owner explicitly requested keeping the server on 2026-11-17. It has not been deleted.

The ONVO provider is now published in test mode. The owner registered all four branches and all four Odoo Apps listings were verified public on 2026-11-17. Source updates require a fresh scan of the existing repositories; see ODOO_APPS_UPLOAD.md.

## Before production activation

- Sandbox credentials are configured; confirm the ONVO endpoint is active and its dashboard connection test succeeds.
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
