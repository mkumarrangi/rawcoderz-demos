# Dining demo research — 13 October 2026

## Product direction
Present business mechanisms through a connected guest / team journey, rather than claiming guaranteed revenue or staffing reductions. Keep staff-assisted service available. The demo is browser-local; it does not integrate with the vendors researched.

## Primary sources and design implications
- Square QR ordering: https://squareup.com/us/en/online-ordering/qr-code-ordering — table mapping and routing to POS/kitchen. Demonstrate table identity traveling with an order.
- Square KDS: https://squareup.com/us/en/point-of-sale/restaurants/kitchen-display-system — digital tickets and fulfillment tracking. Show received, preparing, ready, served as distinct states.
- Petpooja Scan & Order: https://www.petpooja.com/poss/scan-and-order — availability controls and table-linked ordering. Demonstrate a sold-out toggle that affects the guest menu. Internet and POS integration are production dependencies, not existing features of this prototype.
- Square Feedback: https://squareup.com/help/us/en/article/5241-get-started-with-square-feedback — private feedback through digital receipts. Show every rating in the owner view, with a follow-up flag for a low score; do not selectively solicit public reviews.
- Lightspeed option sets: https://o-series-support.lightspeedhq.com/hc/en-us/articles/31329501877659-Creating-and-selling-with-Option-Sets — modifiers and upsell prompts. Make a pairing suggestion optional, clearly priced, and explicitly added by the guest.
- Lightspeed Tableside: https://www.lightspeedhq.com/uk/pos/restaurant/tableside/ — staff-assisted ordering and payment. Preserve personal service instead of making phones mandatory.

## Business case
Potential levers: less order transcription and bill handling, optional basket additions, clearer staff requests, quicker issue visibility, repeat visits through opt-in loyalty. Actual outcomes depend on adoption, service design, training, demand and integration quality.

Calculator formulas (illustrative assumptions, not vendor statistics):
- monthly digital orders = daily orders × operating days × adoption fraction
- staff hours potentially freed = monthly digital orders × assumed minutes saved / 60
- possible extra gross sales = monthly digital orders × assumed add-on acceptance × add-on price
- paper bills avoided = monthly digital orders, assuming one digital receipt replaces one printed bill
Do not translate hours into promised headcount cuts or sales into profit. No double counting table-turn revenue. Display all assumptions, allow zero values, and disclose excluded software/payment costs.

## Production scoping
Validate POS/payment APIs, item and modifier mapping, tax configuration, kitchen stations, connectivity fallback, duplicate-order prevention, staff access, receipt delivery consent and retention rules before estimating a real implementation. The demo makes no claim that integrations already exist.
