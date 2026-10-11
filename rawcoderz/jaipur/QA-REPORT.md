# Jaipur demo verification

Verified locally on 11 October 2026 in headless Google Chrome on Windows. No live deployment, email delivery, real ordering, payment or kitchen integration was tested or performed.

- **28 / 28 brand sites passed** the automated desktop and mobile interaction checks; the collection gallery also passed.
- Desktop width: 1440 px. Mobile widths: 390 px and 320 px. No horizontal page overflow was detected. Main heading text was checked for clipping at 320 px.
- Eight sample menu entries loaded per brand (224 total). Category filtering, search results and empty search states passed for every brand.
- Item options, computed sample totals, quantities, removals, browser cart persistence and empty cart states passed for every brand.
- Simulated table checkout passed for every brand. Mobile pickup checkout and QR-style table prefill passed for eight representative sites.
- Brand cart isolation, malformed saved cart handling, keyboard Escape / focus return, reduced motion, normal ribbon animation and opening a standalone site directly from a local file passed.
- No failed resources or page script errors were recorded in the final interaction run. Local HTML, CSS, image and font references were also checked on disk.
- Local font files loaded for all 28 sites. Both font licence files are included in every brand folder. Visible primary action button contrast was checked at 4.5:1 or better.
- All sites include an independent-demo notice, illustrative menu labels and an explicit confirmation that no real order or payment occurs.

The 28 standalone brand folders total approximately 15.6 MiB. Each folder can be uploaded separately; every individual file is below [Cloudflare Pages' documented 25 MiB file limit](https://developers.cloudflare.com/pages/get-started/direct-upload/).

Representative desktop screenshots and all mobile screenshots were captured in `tools/jaipur/qa/` for visual review. Checks do not establish brand approval, dietary accuracy, inbox activity, production accessibility certification or business operating details.
