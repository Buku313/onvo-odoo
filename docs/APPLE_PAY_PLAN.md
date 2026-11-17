# Apple Pay rollout plan

Status: the hosted self-service setup tab and sandbox test-link wizard are implemented in release 0.5.0; see [merchant setup instructions](APPLE_PAY_SETUP.md). The owner reports Apple Pay activated on the test account. A completed wallet payment and delivery from ONVO still need acceptance testing. The embedded SDK flow remains planned.

## Phase 1 — Apple Pay in the existing hosted checkout

Keep the current Odoo → ONVO Checkout → Odoo flow. ONVO documents this route as dashboard configuration, with no SDK or Odoo-domain registration required. The merchant account must be activated, card payments enabled, and Apple Pay enabled separately for test and live modes under **Settings → Payment methods**. The merchant handles the Apple Pay terms acceptance in that dashboard. Wait for its Apple registration to finish.

Use a compatible Apple device with a card in Wallet. ONVO says its test mode simulates charges but uses the real Wallet flow; Apple's sandbox cards are not the prescribed test method. ONVO currently documents Costa Rica accounts, CRC/USD, and Visa, Mastercard and American Express for Apple Pay. Source: [ONVO Apple Pay guide](https://docs.onvopay.com/en/payments/apple-pay).

Acceptance work:

1. Create an Odoo test order and confirm Apple Pay appears on the ONVO-hosted page for an eligible device. Check normal fallback when Wallet is unavailable.
2. Complete test payments in CRC and USD. Verify the paid Checkout session against the Odoo order's amount, currency, identity and test mode, and confirm the transaction reaches **Done**.
3. Verify a real signed `checkout_session.succeeded` delivery from ONVO, its retry, the browser return and scheduled reconciliation. Repeating notifications must not duplicate fulfillment.
4. Exercise cancellation, failed authorization and abandoned checkout. Odoo must not mark these paid.
5. Repeat the payment flow across Odoo 17–20. Capture the observed device/browser, Odoo version and result; mock tests alone do not prove Wallet compatibility.

Release gate: completed test-payment and webhook evidence, merchant approval to activate live Apple Pay, matching live credentials/webhook, and a separately authorized live-payment check. Only then advertise Apple Pay as available for the specific merchant. Do not promise that the button appears on every device.

## Phase 2 — optional Apple Pay directly inside Odoo

This is a separate implementation, only if an embedded payment sheet is desired. ONVO's documented ingredients are its publishable key, ONVO.js, Apple's web SDK, a registered HTTPS domain and its unchanged domain-association file. It uses payment intents instead of the current hosted Checkout session. Sources: [ONVO Apple Pay integration](https://docs.onvopay.com/en/payments/apple-pay), [ONVO domain registration API](https://docs.onvopay.com/en/api/registrar-un-dominio-de-metodos-de-pago).

Proposed implementation:

- Add an explicit embedded-wallet option while retaining hosted checkout as fallback. Store the publishable key separately from the server-only secret key.
- Serve the association file at the required `/.well-known/` path with a direct HTTPS 200 response, register each actual button-serving domain and surface registration/availability failures to the administrator.
- Load the documented SDKs, check availability and open the payment sheet directly from the buyer's click. Follow Apple's official button requirements.
- Add authenticated order-bound server routes to create/confirm payment intents. Compute totals on the server, check ownership, currency, mode and provider, lock the transaction, and design recovery for ambiguous API outcomes.
- Add signed payment-intent webhook handling and a reconciliation adapter; preserve all existing Checkout webhook/return behavior. Never treat browser callbacks as proof of payment. Verify the applicable intent events against ONVO's schema during implementation.
- Test expired/single-use wallet credentials, concurrent submits, cancelled sheets, failures, retries, multiple websites/companies and Odoo 17–20 frontend differences. Do not reuse wallet credentials for recurring billing.

No SDK, domain registration, merchant-term acceptance, live activation or Apple Pay branding was added by this planning task.
