# Rawcoderz — Connected dining concept

A buildless, browser-local sales demonstration for cafés, restaurants and food businesses.

## Experience
- Eight visual chapters: table scan, menu, order tracking, waiter requests, digital bills, feedback, owner view, virtual café.
- One connected demo visit: chosen items and prices flow to kitchen status, digital receipt and feedback.
- Optional pairing suggestion; owner-controlled sold-out state updates the guest menu.
- Guest/team request acknowledgement, private feedback follow-up and an activity log.
- Guided story, manual/connected workflow comparison, editable impact assumptions and a downloadable discovery brief.
- Illustrated café/kitchen tour, loyalty and reservation concepts.

## Boundaries
No payment gateway, POS, notification service, persistence or real booking backend is connected. Receipt and planning-brief downloads stay local. Data resets on reload. The impact calculator is a scenario model, not a measured result or revenue/staffing guarantee. The virtual tour uses illustrations rather than real 360-degree imagery.

## Source
`dist/index.html` contains the experience; `style.css` and `app.js` provide the original café foundation; `growth.css` and `growth.js` extend the business journey. `.openai/hosting.json` retains the existing private Site identity. See `RESEARCH.md` for primary sources and production scoping.

## Verification
- JavaScript syntax checks passed.
- Browser-tested explicit pairing: ₹180 drink + ₹140 croissant = ₹320, preserved through kitchen and bill.
- Kitchen preparing/ready/served updates and guest visibility tested.
- Simulated payment changes bill to receipt; downloaded receipt inspected for table, items, amount and demo status.
- Two-star feedback text reaches the owner with a follow-up flag; reviewed state works.
- Table-specific waiter request and guest acknowledgement tested.
- Owner sold-out toggle removes the ability to order the croissant.
- Calculator tested at 0% and 100% adoption and with invalid days; formulas are visible.
- Custom module selection and discovery-brief download tested.
- Responsive widths of 390px and 320px verified without horizontal page overflow.

## Preview
Serve `dist/` with a local static HTTP server. No installation or build is needed.
