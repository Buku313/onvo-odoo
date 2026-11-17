# Set up Apple Pay with ONVO Checkout

Open the **ONVO** payment provider in Odoo, then its **Apple Pay** tab. Your existing secret API key and signed webhook are sufficient for hosted checkout; there is no additional Odoo-domain registration or SDK installation.

## 1. Activate Apple Pay in ONVO

Use **Open ONVO Dashboard**, then go to **Settings → Payment methods**. In test mode, turn on card payments and Apple Pay. Complete account activation and the merchant terms in ONVO if requested; wait for the Apple registration status to finish there. Test and live activation are separate.

## 2. Create a test link in Odoo

Save your ONVO provider in test mode. In Odoo 17–19, choose **Test Mode**. In Odoo 20, leave **Live** off and keep the provider active. Configure both secrets and confirm the data-transfer checkbox first.

On the **Apple Pay** tab, choose **Create a test checkout**. Select **USD 1.00** or **CRC 1,000.00**, then **Create test link**. The selected currency and ONVO payment method must be active in Odoo.

Use **Open test checkout**, or copy the link to your own compatible Apple device with a card in Wallet. Choose Apple Pay on ONVO's page and complete the sandbox payment. ONVO documents a real Wallet flow with simulated charges in its test mode. These setup checkouts do not create sales orders.

## 3. Check the result

Return to the test window and choose **Check payment result**. Odoo checks ONVO's session and displays its transaction state. **Done** means checkout completion; it does not identify which payment method you selected. Choose Apple Pay on the payment page to exercise that wallet.

If you close the window, the test remains in Odoo's payment transactions with a reference beginning `ONVO-SELFTEST-`. The existing webhook and scheduled reconciliation can still update it. Opening the setup tool again starts a new test.

## If the button is missing

Look on ONVO's payment page after leaving Odoo. Check the device's Wallet card, merchant activation, completed Apple registration, and the matching test/live switches for card payments and Apple Pay. Use USD or CRC with an eligible Costa Rica account. ONVO handles device/payment-method availability on its hosted page.

## Going live

Enable Apple Pay in ONVO's live mode when ready. Update Odoo with matching live API and webhook secrets and switch its provider to live mode together. Confirm webhook delivery and the live payment flow under your normal launch approval process. The self-service test tool rejects live-mode providers and keys on the server; it cannot create a live payment.

Source: [ONVO's Apple Pay guide](https://docs.onvopay.com/en/payments/apple-pay).

## Administrator and developer notes

- Only Odoo Settings administrators can use the setup wizard. It respects the current allowed companies and does not elevate access.
- The API secret stays server-side. Links use the existing ONVO-hosted checkout URL validation and signed return flow.
- Repeated clicks within one test reuse its session. Checking the result performs the existing read-only session reconciliation.
- The public availability API is documented for an embedded button's domain. This hosted flow does not interpret that endpoint as merchant activation status or add an unverified local activation toggle.
- This release provides setup guidance and a test workflow. It does not add an embedded SDK or independently attest to Apple Pay activation or device compatibility.
