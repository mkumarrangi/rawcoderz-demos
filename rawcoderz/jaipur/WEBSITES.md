# Jaipur website collection

28 standalone website concepts, created for the Rawcoderz outreach project. [Open the gallery](index.html).

Each brand folder contains its own HTML, CSS, JavaScript, local fonts, local assets, favicon, crawler headers and README. No shared runtime, dependency installation or build is needed. Open any `index.html` directly or serve the folder locally.

## Included

Every site has a brand-specific visual direction, responsive layouts, hover and scroll animation, reduced-motion support, sample menu search and categories, item options, quantity controls, persistent cart, and simulated dine-in or pickup checkout. `?table=7` demonstrates prefilled table ordering.

## Deploying on Cloudflare Pages

Deploy one brand folder per project, with that folder's `index.html` at the upload root. These files are already the complete output. For Direct Upload, drag the brand folder into the Pages uploader. For Git deployment choose no framework, use `exit 0` as the build command, and set the output directory to `rawcoderz/jaipur/<brand-folder>` relative to the repository root. No deployment was made by this task. See [Cloudflare Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/) and [static HTML settings](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/).

## Content status

All menus, prices, dish recipes, options and dietary labels are illustrative. No live ordering, payments, reservations, messages or personal contact collection take place. Only cart selections are saved in the visitor's browser. Public brand logos or photos are used as references for the corresponding brand only; nine concepts have official logo references. Other palettes and wordmarks are creative directions rather than verified official guidelines. See each folder README and [art direction](ART-DIRECTION.md) for sources.

Original prospect, email and qualification registers are preserved. The demos do not assert that the businesses lack websites, need the system, or have authorised this work. Before public production, confirm the venue's content, rights, prices, branch details and operating integration.

## All sites

| Brand | Standalone folder | Art direction | Primary / accent |
| --- | --- | --- | --- |
| [The Messy Door Cafe](the-messy-door-cafe/index.html) | `the-messy-door-cafe/` | collage | #e45480 / #d8ed9c |
| [Cosmos Cafe](cosmos-cafe/index.html) | `cosmos-cafe/` | orbit | #c58b5e / #bdd0d7 |
| [The Rustic Spot Cafe](the-rustic-spot-cafe/index.html) | `the-rustic-spot-cafe/` | workshop | #b55735 / #7c8659 |
| [Bulb Cafe](bulb-cafe/index.html) | `bulb-cafe/` | garden | #e7b72e / #8da36e |
| [C4 Chaska](c4-chaska/index.html) | `c4-chaska/` | street | #dc4a32 / #edb637 |
| [How About Coffee](how-about-coffee/index.html) | `how-about-coffee/` | postcard | #bb6445 / #a4ad7c |
| [The Social Belly](the-social-belly/index.html) | `the-social-belly/` | conservatory | #576c46 / #b9ba82 |
| [Pocket Beans](pocket-beans/index.html) | `pocket-beans/` | pocket | #da6b30 / #dabd80 |
| [Cheesy Crazy Cafe](cheesy-crazy-cafe/index.html) | `cheesy-crazy-cafe/` | checker | #f5c82f / #e75e3b |
| [Cafe Bluez](cafe-bluez/index.html) | `cafe-bluez/` | deco | #2b58a0 / #ceaa5e |
| [Brew & Bite](brew-and-bite/index.html) | `brew-and-bite/` | journal | #6b5d48 / #8b977c |
| [The Bhatura Project](the-bhatura-project/index.html) | `the-bhatura-project/` | poster | #dd9d26 / #b9442e |
| [The karchi Restaurant](the-karchi-restaurant/index.html) | `the-karchi-restaurant/` | engraved | #a14b37 / #b29864 |
| [Kanha](kanha/index.html) | `kanha/` | celebration | #1a507b / #d1aa50 |
| [Tansukh / Tan-Sukh by Kanha](tansukh/index.html) | `tansukh/` | royal | #b83222 / #4f973e |
| [La Fiamma](la-fiamma/index.html) | `la-fiamma/` | oven | #d8412b / #a8ad69 |
| [Rawat Misthan Bhandar](rawat-misthan-bhandar/index.html) | `rawat-misthan-bhandar/` | bazaar | #ba2d29 / #e0bf38 |
| [LMB / Laxmi Misthan Bhandar](lmb/index.html) | `lmb/` | heritage | #872b37 / #bd9651 |
| [Niros](niros/index.html) | `niros/` | brasserie | #347c50 / #c3a774 |
| [Chokhi Dhani Village Restaurant](chokhi-dhani/index.html) | `chokhi-dhani/` | village | #943a20 / #d09a40 |
| [Thali and More](thali-and-more/index.html) | `thali-and-more/` | thali | #73832d / #c9733b |
| [Spice Court](spice-court/index.html) | `spice-court/` | courtyard | #31513f / #b6965b |
| [Handi Restaurant](handi/index.html) | `handi/` | ember | #d16a35 / #b99756 |
| [Tapri (Central)](tapri/index.html) | `tapri/` | chai | #657f2e / #d5b13e |
| [Curious Life Coffee Roasters](curious-life/index.html) | `curious-life/` | roastery | #c36764 / #93a394 |
| [Cafe LazyMojo](cafe-lazymojo/index.html) | `cafe-lazymojo/` | lazy | #265f57 / #dd8f6a |
| [On The House (OTH)](on-the-house/index.html) | `on-the-house/` | bistro | #294759 / #c4a36a |
| [Anokhi Cafe](anokhi-cafe/index.html) | `anokhi-cafe/` | blockprint | #334d76 / #ad7159 |

## Source and rebuild

The source is in `tools/jaipur/`: `brands.json`, `site.css`, `app.js`, `fetch_assets.py` and `build.py`. The output sites need no Python or Node runtime. Rebuilding requires Python with Pillow and an asset cache (populate it with `fetch_assets.py`). The generator overwrites generated site files; make lasting changes in the source first.
