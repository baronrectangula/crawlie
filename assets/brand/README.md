# Brand assets

Logos, mascot, app icons, and favicons for Crawlie. SVG lettering is outlined and requires no fonts.

| Path | Contents |
| --- | --- |
| `svg/` | Mascot, wordmark, primary logo, horizontal/vertical lockups, and icon masters |
| `png/logos/` | Raster versions of the logos |
| `png/app-icons/` | Square icons at 1024, 512, 256, 192, 180, 128, and 64 px |
| `png/badges/` | Rounded icons at the same sizes |
| `png/favicons/` | 16, 32, and 48 px PNGs and multi-size ICO files |
| `web/` | Default favicons, Apple touch icon, and web manifest |
| `source/` | Editable polygon data, reference image, and build scripts |
| `asset-index.csv` | File sizes and SHA-256 checksums |

[Preview gallery](preview.html) · [Contact sheet](preview/contact-sheet.png)

## Variants

`black` and `white` have transparent backgrounds. `black-on-white` and `white-on-black` include a background. Rounded badges have transparent corners.

Use SVGs for logos, square PNGs for app icons, and the simplified favicon artwork at 16–48 px. Preserve aspect ratio. The web set uses white artwork on black.

## Web setup

Copy `web/` into the site's public `/brand/` directory, or adjust the paths below:

```html
<link rel="icon" href="/brand/favicon.ico" sizes="16x16 32x32 48x48">
<link rel="icon" type="image/png" sizes="16x16" href="/brand/favicon-16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/brand/favicon-32.png">
<link rel="icon" type="image/png" sizes="48x48" href="/brand/favicon-48.png">
<link rel="icon" type="image/svg+xml" sizes="any" href="/brand/favicon.svg">
<link rel="apple-touch-icon" sizes="180x180" href="/brand/apple-touch-icon.png">
<link rel="manifest" href="/brand/site.webmanifest">
<meta name="theme-color" content="#000000">
```

Set the manifest's `start_url` and `scope` for the app. Its icons use `purpose: "any"`, not `maskable`.

## Rebuild

Requires Python 3.10+, Pillow, and `rsvg-convert`. From the repository root:

```sh
python3 assets/brand/source/build.py
python3 assets/brand/source/validate.py
```
