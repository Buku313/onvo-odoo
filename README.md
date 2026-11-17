# ONVO Checkout for Odoo 17–20

Publisher: **ONVOPay** · Support: **antonio@onvopay.com** · Free · LGPL-3

One connector, with matching builds and Git branches for Odoo **17, 18, 19 and 20**. Release `X.0.0.5.0` remains a beta until a completed ONVO sandbox payment and an actual ONVO webhook delivery are verified. Real test-session creation has succeeded on the hosted demo. Automated tests mock ONVO's API and do not replace payment acceptance testing.

[Odoo Apps publishing instructions](docs/ODOO_APPS_UPLOAD.md) · [Release record](docs/RELEASE.md)

[Apple Pay self-service setup](docs/APPLE_PAY_SETUP.md) · [Apple Pay rollout plan](docs/APPLE_PAY_PLAN.md) · [Payment branding](docs/BRANDING.md)

Planned B2B expansion: [payment model](docs/B2B_PAYMENT_MODEL.md), [comprehensive payment-term catalog](docs/B2B_TERMS_CATALOG.md), and [implementation/acceptance plan](docs/B2B_IMPLEMENTATION_PLAN.md). These describe future quote/invoice collection features; they are not claims of functionality in the current connector.

## Installation

Download the ZIP matching your Odoo major version from this repository's Releases or the [Odoo Apps listing](https://apps.odoo.com/apps/modules/17.0/payment_onvo). Copy its `payment_onvo` folder into an addons directory, restart Odoo, update the Apps list, remove the Apps filter and install **ONVO Checkout**. Do not install all four packages together.

Targets are Community and Enterprise installations that allow Python add-ons, including Odoo.sh and self-hosted servers. Odoo Online SaaS cannot install this add-on. Community containers are used for automated compatibility tests; no proprietary Enterprise runtime is bundled or independently certified by this project. Future major versions require explicit compatibility testing.

## Configure ONVO

1. Open the ONVO payment provider under Accounting / Website configuration.
2. Get your secret API key from the [ONVO Dashboard](https://onvopay.com/). Paste `onvo_test_secret_key_...` in **Secret API key**. Hosted checkout needs no publishable key.
3. Use the **copy button** beside **Webhook URL**. In ONVO test mode, open **Developers → Webhooks → Add webhook**, paste the URL and subscribe to `checkout_session.succeeded`. ONVO requires a public HTTPS domain on port 443; localhost and bare IP addresses will not work. Correct Odoo's website/base URL first if the displayed URL is wrong.
4. Paste the endpoint's `whsec_...` secret in **Webhook signing secret**, then confirm the data-transfer checkbox. This secret is separate from the API key. Retrieve it again through **Reveal signing secret** on the ONVO endpoint if needed.
5. Odoo 17–19: choose **Test Mode**. Odoo 20: leave **Live** off and keep the provider active. Save both secrets, the mode and consent together. In ONVO, use the endpoint's **Test connection** and confirm success. This checks webhook delivery/signing, not API-key validity or a payment.
6. Publish the provider when ready to test checkout. Complete a sandbox payment in USD or CRC and verify its Odoo transaction reaches **Done**. Test cancellation, duplicate webhook delivery and pending-payment reconciliation too.
7. To go live, obtain a matching live secret API key and create a live-mode webhook. Replace **both** secrets, switch Odoo to live mode and save together. Repeat the ONVO connection test. Test and live endpoints have separate signing secrets.

See [ONVO's signed webhook guide](https://docs.onvopay.com/en/webhooks). Endpoint creation is done in the Dashboard; ONVO does not expose it through API keys. The previous `X-Webhook-Secret` format is not supported.

If checkout says no payment option is available, check the provider's mode, publication status, website/company, supported currency and country restrictions, and that its ONVO payment method is active. In test mode, use an authorized test user; Odoo can hide test providers from public visitors.

ONVO's hosted page controls payment methods offered to the merchant. This connector supports one-time automatic capture in CRC and USD. Saved cards, refunds from Odoo, subscriptions, manual capture, POS and payouts are outside this release.

## Apple Pay self-service setup

Open the ONVO provider's **Apple Pay** tab. It links to the ONVO Dashboard activation steps and provides **Create a test checkout** for Settings administrators. Select a test amount, create a link, open it on an Apple device with Wallet, choose Apple Pay, then use **Check payment result** in Odoo. The tool rejects live mode and reuses an existing session within the same test window. No extra publishable key, SDK or Odoo-domain registration is required for this hosted flow.

The owner has activated Apple Pay for the demo's test account. Individual merchants enable it for their own accounts in ONVO. Odoo shows checkout completion, not an independently verified Apple Pay activation status; full device/Wallet acceptance remains a manual test.

## Data and referral attribution

Odoo sends amount, currency, transaction reference, buyer email, `integration=onvo_odoo`, the connector version and an optional ONVO referral code directly to ONVO. Card details are entered on ONVO. Session and payment identifiers are stored in Odoo. The connector has no separate telemetry or activation service.

Configure an ONVO-issued partner code in **ONVO Referral Code** when available. The metadata does not itself enroll a merchant in a partner program or guarantee commission. ONVO must recognize the attribution agreement and code.

Browser returns use a random per-transaction token and cannot assert payment success. Webhook signatures are checked against the raw request body and a five-minute timestamp tolerance. Odoo independently fetches and validates session identity, mode, amount and currency. Completed transactions are not completed again on duplicate notification. A scheduled action reconciles pending sessions.

## Upgrading the first beta

Upgrade `payment_onvo` through Apps after replacing the folder. The `X.0.0.2.0` migration links the payment method and module to the existing provider without replacing its credentials. This is not a migration from the separate legacy `payment_onvopaycard` module, nor an upgrade of an Odoo database across major versions.

## Build and test locally

Use Python 3 and Docker. Create `.env` with a random `POSTGRES_PASSWORD`.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_version.py 20 --output build/odoo20 --zip
POSTGRES_VERSION=16 ODOO_VERSION=20.0 ADDONS_PATH=./build/odoo20/payment_onvo docker compose -p onvo-test20 up -d db
POSTGRES_VERSION=16 ODOO_VERSION=20.0 ADDONS_PATH=./build/odoo20/payment_onvo docker compose -p onvo-test20 run --rm odoo odoo -d onvo_test20 -i payment_onvo --without-demo=all --test-enable --test-tags /payment_onvo --stop-after-init
```

Odoo 20 needs PostgreSQL 16 or newer; the test uses an isolated Compose project to keep that data separate from PostgreSQL 15. Never attach an existing PostgreSQL data volume to a different major image. Use 17, 18 or 19 similarly. The build command refuses to overwrite an existing output folder. Use a fresh output folder for each build. GitHub Actions runs the four-version test matrix. Do not advertise compatibility solely because a ZIP can be generated.

## Hosted sandbox

https://onvo-odoo.18.207.41.62.sslip.io/shop

The existing Odoo 17 demo is retained at the owner's request. It costs USD 12/month on AWS Lightsail. Its ONVO provider is published in test mode with credentials stored only on the server. Real test-session creation and a locally signed webhook probe have passed; completing a payment and confirming delivery from ONVO remain acceptance tasks. The demo is not a production store.

Secrets and local deployment records are excluded from Git. The server administrator login is not published in this repository.
