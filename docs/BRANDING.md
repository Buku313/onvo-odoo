# Payment branding

The ONVO wordmark paths come from the public navigation logo at https://onvopay.com/, retrieved 2026-11-17. The letter shapes and proportions are preserved. The wordmark is rendered in dark navy on a light background for legibility.

- `payment_onvo/static/img/onvo-wordmark.svg`: source wordmark.
- `payment_onvo/static/img/payment_method.svg` and `.png`: compact checkout badge.
- `payment_onvo/static/img/provider_icon.svg`: square provider/app icon source.
- `payment_onvo/static/description/icon.png`: square provider/app icon.

These are vector compositions rendered with `rsvg-convert`, not AI-generated approximations of the logo. The existing marketplace cover remains unchanged.

To regenerate the PNG files from the repository root:

```sh
rsvg-convert payment_onvo/static/img/payment_method.svg -o payment_onvo/static/img/payment_method.png
rsvg-convert payment_onvo/static/img/provider_icon.svg -o payment_onvo/static/description/icon.png
```

Odoo resizes the payment method image to its standard small checkout dimensions. The badge intentionally carries only ONVO branding: individual payment methods vary by merchant account, mode and device. It does not advertise Apple Pay before merchant activation and acceptance testing.

On upgrade, `branding.update_default_images` fills missing images and replaces the previous bundled green icon. It preserves other merchant-supplied images. `legacy_icon.png` is retained only to recognize that previous default. Credentials, mode, publication status, payment methods and existing transactions are not changed by this artwork migration.
