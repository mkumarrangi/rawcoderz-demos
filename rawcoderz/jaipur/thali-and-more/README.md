# Thali and More — independent website concept

Open `index.html` directly, or serve this folder with any static server. This folder is a complete standalone site; it does not depend on its parent or other brand folders.

## Cloudflare Pages

For Direct Upload, upload the contents of this folder (with `index.html` at the upload root). For Git deployment, choose no framework, use `exit 0` as the build command and this folder as the output directory. No install step, environment variables or server are required. The `_headers` file asks crawlers not to index the demo. No deployment has been performed. See [Cloudflare Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/) and [static HTML settings](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/).

## Experience

- Responsive landing page; thali art direction.
- Local Fraunces / Outfit typography, local images, scroll reveals and motion preference support.
- Three menu categories, search, sample customisations, quantities, removable cart lines and browser cart persistence isolated to this brand.
- Dine-in or pickup simulation. Add `?table=7` to prefill a table number for a QR-style demo.
- No backend, payment, kitchen integration, real order, reservation, or customer contact collection. Kitchen notes are never transmitted. Cart contents remain only in the visitor's browser.

## Brand and content status

Olive logo-led palette with warm cream and terracotta accents.

All menu items, descriptions, recipes, dietary labels, options and prices are illustrative. Photography is a visual reference rather than a claim about the exact dish. Address information is taken from the prospect register and must be confirmed. This is an independent Rawcoderz concept, not an official or endorsed website. Obtain brand approval and replace sample content before production.

## Public reference assets

- paneer: https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=1440&q=82
- bread: https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1440&q=82
- table: https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1440&q=82
- indian: https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=1440&q=82
- cake: https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=1440&q=82
- Logo: https://thaliandmore.co.in/img/logo.png

Fonts are self-hosted Latin subsets from Google Fonts; the respective open font licence files are included in `assets`. Stock photos are from the linked Unsplash image URLs. Brand logos and brand-owned images are public reference assets used only for that brand's private demo; ownership remains with the rights holders. Original food and drink illustrations, when present, were drawn for this concept.

## Updating

Edit `site-data.js` for the sample menu, `index.html` for content, and `styles.css` for styling. The source generator is `tools/jaipur/build.py` in the workspace and will overwrite generated site files when run. Set lasting changes in the generator, CSS source, JS source or `brands.json` before rebuilding.
