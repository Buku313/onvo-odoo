# Publish ONVO Checkout on Odoo Apps

Publisher: **ONVOPay** · Support: **antonio@onvopay.com** · Price: **Free**

Odoo Apps reads a Git repository. You register each version branch; you do not upload the ZIP to the marketplace. The ZIPs are for direct installation.

## 1. Give the Odoo scanner access to this private repository

Open https://github.com/Buku313/onvo-odoo/settings/access and use the repository's collaborator controls to invite **online-odoo**. This is the exact account in Odoo's official FAQ, not `odoo-online`. Grant access only to this repository, not an entire organization. Check the permission GitHub will grant before confirming: personal repositories may offer broader collaborator access than a read-only organization role. If that is unacceptable, arrange an alternative with Odoo Apps support instead of granting broader access silently.

Wait for the scanner account to have access before scanning. Keeping GitHub private does not prevent users from downloading the free add-on's source after it is published on Odoo Apps.

Source: https://apps.odoo.com/apps/faq

## 2. Sign in to the intended publisher account

Go to https://apps.odoo.com/apps/upload and sign in with the Odoo account that should own ONVOPay's app listing. The manifest sets the author and support email; it does not choose the account that owns the listing.

## 3. Register all four version branches

Register these URLs individually:

| Odoo | Repository URL |
| --- | --- |
| 17 | `ssh://git@github.com/Buku313/onvo-odoo#17.0` |
| 18 | `ssh://git@github.com/Buku313/onvo-odoo#18.0` |
| 19 | `ssh://git@github.com/Buku313/onvo-odoo#19.0` |
| 20 | `ssh://git@github.com/Buku313/onvo-odoo#20.0` |

Odoo scans the `payment_onvo` folder at each branch's root. Use the same technical module name for every version so Odoo can associate the versions. Review the repository scan result and resolve any reported errors. Registration and scanning do not guarantee immediate publication; use the status shown by Odoo.

## 4. Check the generated listing

The listing is generated from `payment_onvo/__manifest__.py` and `payment_onvo/static/description/index.html`.

Verify:

- Name: ONVO Checkout; author: ONVOPay; support: antonio@onvopay.com.
- Free price: the manifest deliberately has no `price` field.
- Correct Odoo version and LGPL-3 license.
- English description, icon and accurate beta scope.
- External ONVO account requirement and data-transfer/referral disclosure.

Add screenshots from a real sandbox checkout before presenting the release as production-ready. Do not claim Odoo endorsement merely because the app is listed. Keep the beta label until an actual ONVO sandbox payment and signed webhook are verified. Avoid external store/promotional links and JavaScript in the listing HTML.

Source: https://apps.odoo.com/apps/vendor-guidelines

## 5. Publish updates

Change the source, increment the release version, test it on each target Odoo version, and push the matching version branches. Rescan/update each registered repository in the Odoo Apps publisher interface. Never overwrite an existing release ZIP with different contents under the same version.

## What users install

Users choose the package matching their Odoo major version. The Python add-on is intended for Odoo Community or Enterprise installations that allow custom modules, including Odoo.sh and self-hosted servers. Standard Odoo Online SaaS cannot install this Python add-on. Future Odoo major versions need another tested release; “17 and up” currently means 17, 18, 19 and 20.

The connector supports one-time CRC/USD hosted Checkout, signed webhooks, server-side verification and pending-payment reconciliation. It does not add POS, subscriptions, saved cards, refunds from Odoo or payouts. Referral metadata identifies the integration; any commercial referral credit still requires an ONVO-recognized code.

## Current account steps still needed

No Odoo scanner access has been granted and no marketplace registration has been submitted by this work. Complete steps 1–3 from your accounts. Your hosted demo is being kept running as requested; ONVO checkout remains disabled until you supply your sandbox credentials.
