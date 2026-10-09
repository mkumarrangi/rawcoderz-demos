"""Build one concept homepage per prospect from public facts only.

Usage (from the repo root): python3 tools/build_demos.py prospects.json .

prospects.json is a list of objects. Required: slug, business, phone, rating,
reviews, maps_url, city, state. Optional (leave out anything you can't verify):
  address      street address shown in the footer
  services     list of service names exactly as the business lists them
  why_extra    list of [big, small] facts, e.g. ["Since 1950", "Three generations of Tampa roofers"]
  theme        storm | gulf | signal | grove (color scheme; vary it between prospects)
  headline     hero headline built from a real fact, e.g. "Tampa roofs, done right since 1950"
  license      state contractor license, e.g. "CCC056926" (only if published by them)
  areas        sentence naming the areas they list, e.g. "South Tampa, Lutz, Odessa and Westchase"
  hours        sentence with their Google hours, e.g. "Open weekdays 7 AM to 5:30 PM."
  quotes       up to 3 verbatim testimonials from their own website: [{"text": "...", "name": "John S."}]
               (trim with an ellipsis if needed; first name plus last initial)
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = open(os.path.join(HERE, "roof_template.html"), encoding="utf-8").read()
CONTACT = "mukesh.kumar@rawcoderz.com"

THEMES = {
    "storm":  dict(ink="#12283C", ink2="#1C3A55", accent="#F2B705", accent_ink="#12283C", accent_deep="#8F6400"),
    "gulf":   dict(ink="#0C3638", ink2="#145052", accent="#FF8A3D", accent_ink="#1B1206", accent_deep="#B04A14"),
    "signal": dict(ink="#23262B", ink2="#33373E", accent="#D42A32", accent_ink="#FFFFFF", accent_deep="#B3202A"),
    "grove":  dict(ink="#1C3528", ink2="#284A38", accent="#E6C140", accent_ink="#1C2612", accent_deep="#836810"),
}

ICONS = {
    "repair": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3.6 17.4a1.4 1.4 0 0 0 2 2l5.7-5.7a4 4 0 0 0 5.4-5.4l-2.5 2.5-2-2z"/>',
    "roof": '<path d="M2.5 12 12 4.5l9.5 7.5"/><path d="M5.5 10v9.5h13V10"/><path d="M10 19.5v-5h4v5"/>',
    "storm": '<path d="M7 16a4.5 4.5 0 1 1 1-8.9A6 6 0 0 1 19.5 9a3.5 3.5 0 0 1-1 7"/><path d="m12.5 12-2.5 4.5h4L11.5 21"/>',
    "inspect": '<circle cx="10.5" cy="10.5" r="6"/><path d="m15 15 5.5 5.5"/>',
    "commercial": '<path d="M4 20.5V5.5l8-2.5v17.5"/><path d="M12 9.5h8v11"/><path d="M2.5 20.5h19"/><path d="M7 8h2M7 11.5h2M7 15h2M15 13h2M15 16.5h2"/>',
    "water": '<path d="M12 3.5s6.5 7 6.5 11a6.5 6.5 0 0 1-13 0c0-4 6.5-11 6.5-11z"/>',
    "tarp": '<path d="M3 18.5 12 5l9 13.5z"/><path d="M8 18.5 12 12l4 6.5"/>',
    "measure": '<path d="M3.5 16.5 16.5 3.5l4 4-13 13z"/><path d="m7 13 2 2M10 10l2 2M13 7l2 2"/>',
    "coat": '<rect x="3.5" y="4" width="14" height="5" rx="1.2"/><path d="M17.5 6.5h3v5.5H11v3"/><path d="M10 15h2v6h-2z"/>',
    "window": '<rect x="5" y="4" width="14" height="16" rx="1.5"/><path d="M12 4v16M5 12h14"/>',
    "wind": '<path d="M3 9h11a3 3 0 1 0-3-3"/><path d="M3 14h15a3 3 0 1 1-3 3"/><path d="M3 11.5h7"/>',
    "money": '<rect x="2.5" y="6" width="19" height="12" rx="2"/><circle cx="12" cy="12" r="2.6"/><path d="M6 9.5v5M18 9.5v5"/>',
    "build": '<path d="M13.5 5.5 18.5 10.5"/><path d="m11 8 5 5-8.5 8.5-5-5z"/><path d="M14.5 4.5l2-2 5 5-2 2"/>',
}

# Plain descriptions of what each kind of job is. They describe the service, never promise outcomes.
SERVICE_COPY = [
    ("storm", "storm", "Damage from wind, hail or a fallen branch, assessed and repaired."),
    ("insurance", "storm", "Damage from wind, hail or a fallen branch, assessed and repaired."),
    ("leak", "repair", "Find where the water gets in and fix it before it reaches the ceiling."),
    ("repair", "repair", "Leaks, lifted shingles, cracked tiles and worn flashing."),
    ("replacement", "roof", "Tear-off and a complete new roof system."),
    ("new roof", "roof", "A complete roof system for a new build or a full replacement."),
    ("inspection", "inspect", "A look at your roof's condition and what it needs next."),
    ("shingle", "roof", "Architectural and 3-tab shingle roofs, repaired or replaced."),
    ("tile", "roof", "Concrete and clay tile, including the underlayment Florida tile roofs depend on."),
    ("metal", "roof", "Standing seam and metal panel roofs built for wind and long service."),
    ("flat", "roof", "Low-slope and flat roofs for homes, additions and carports."),
    ("commercial", "commercial", "Flat and low-slope roofs for offices, retail and warehouses."),
    ("residential", "roof", "Repairs and replacements for single-family homes."),
    ("water mitigation", "water", "Drying out and stopping further damage after water gets inside."),
    ("tarp", "tarp", "Emergency tarping to keep the rain out until the repair."),
    ("fascia", "measure", "Rotted fascia and soffit replaced so the roof edge stays sealed."),
    ("coating", "coat", "Elastomeric coatings that seal and extend the life of a flat roof."),
    ("drywall", "build", "Ceiling and wall repairs once the roof above is fixed."),
    ("skylight", "window", "Skylights installed, replaced or resealed so they stop leaking."),
    ("wind mitigation", "wind", "Roof work done to the standards that can lower windstorm insurance premiums."),
    ("financing", "money", "Monthly payment options for a roof that can't wait."),
    ("construction", "build", "New construction from the foundation to the roof."),
    ("remodel", "build", "Kitchens, bathrooms and whole-home renovations."),
    ("addition", "build", "Extra bedrooms, suites and living space built onto your home."),
    ("gutter", "water", "Gutters that carry water away from the roof edge and foundation."),
]
DEFAULT_SERVICES = ["Roof repair", "Roof replacement", "Storm damage", "Roof inspections"]


def e(v):
    return html.escape(str(v), quote=True)


def tel(phone):
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) == 10:
        digits = "1" + digits
    return "+" + digits if digits else ""


def svc_row(name):
    low = name.lower()
    icon, text = "roof", ""
    for key, ic, copy in SERVICE_COPY:
        if key in low:
            icon, text = ic, copy
            break
    svg = f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[icon]}</svg>'
    return f"<li>{svg}<div><h3>{e(name)}</h3>" + (f"<p>{e(text)}</p>" if text else "") + "</div></li>"


STAR = "M10 1.2l2.7 5.6 6.1.8-4.5 4.2 1.1 6.1L10 15l-5.4 2.9 1.1-6.1L1.2 7.6l6.1-.8z"


def stars(rating, on_dark):
    pct = max(0.0, min(1.0, float(rating) / 5.0)) * 100
    base = "rgba(255,255,255,.25)" if on_dark else "#D6DDDD"
    row = "".join(f'<path transform="translate({i * 22.5} 0)" d="{STAR}"/>' for i in range(5))
    svg = lambda fill: f'<svg viewBox="0 0 110 20" fill="{fill}" aria-hidden="true">{row}</svg>'
    return (f'<span class="stars" role="img" aria-label="{e(rating)} out of 5 stars">{svg(base)}'
            f'<span class="fill" style="width:{pct:.1f}%">{svg("var(--accent)")}</span></span>')


def build(p):
    name = p["business"]
    short = p.get("short") or name
    phone = p.get("phone") or ""
    t = THEMES.get(p.get("theme") or "storm", THEMES["storm"])
    phone_svg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M5 3.5h3.5l1.8 4.6-2.3 1.4a11 11 0 0 0 6.5 6.5l1.4-2.3 4.6 1.8V19a1.8 1.8 0 0 1-1.9 1.8A16.5 16.5 0 0 1 3.2 5.4 1.8 1.8 0 0 1 5 3.5z"/></svg>'
    call = (f'<a class="btn call" href="tel:{e(tel(phone))}">{phone_svg}<span>{e(phone)}</span></a>' if phone
            else '<a class="btn call" href="#quote"><span>Free quote</span></a>')
    call_big = (f'<a class="btn call" href="tel:{e(tel(phone))}">{phone_svg}Call {e(phone)}</a>' if phone else "")
    bar_call = (f'<a class="btn call" href="tel:{e(tel(phone))}">{phone_svg}Call</a>' if phone else "")
    rating, reviews = p.get("rating"), p.get("reviews")
    city = p.get("city") or "Tampa"
    state = p.get("state") or "FL"

    proof = []
    if rating and reviews:
        link = f' <a href="{e(p["maps_url"])}" target="_blank" rel="noopener">Read them</a>' if p.get("maps_url") else ""
        proof.append(f'<li><b>{stars(rating, True)}{e(rating)}</b>From {e(reviews)} Google reviews.{link}</li>')
    for big, small in p.get("why_extra") or []:
        proof.append(f"<li><b>{e(big)}</b>{e(small)}</li>")
    if p.get("license"):
        proof.append(f'<li><b>Licensed</b>Florida contractor license {e(p["license"])}</li>')

    services = p.get("services") or DEFAULT_SERVICES
    quotes = [q for q in (p.get("quotes") or []) if q.get("text") and q.get("name")][:3]
    if quotes:
        lead, rest = quotes[0], quotes[1:]
        side = "".join(f'<blockquote><p>“{e(q["text"])}”</p><cite>{e(q["name"])}</cite></blockquote>' for q in rest)
        score = ""
        if rating and reviews:
            more = f'<a href="{e(p["maps_url"])}" target="_blank" rel="noopener">Read all {e(reviews)} on Google</a>' if p.get("maps_url") else ""
            score = f'<div class="score">{stars(rating, False)}<b>{e(rating)}</b><span>from {e(reviews)} Google reviews</span>{more}</div>'
        reviews_section = (
            '<section id="reviews"><div class="wrap"><h2 class="t">What customers say</h2>'
            '<p class="intro">From reviews already published on their own website.</p>'
            f'<div class="revs"><blockquote class="lead-q"><p>“{e(lead["text"])}”</p><cite>{e(lead["name"])}</cite></blockquote>'
            f'<div class="side-q">{side}</div></div>{score}</div></section>')
        nav_reviews = '<a href="#reviews">Reviews</a>'
    elif rating and reviews:
        more = f'<a href="{e(p["maps_url"])}" target="_blank" rel="noopener">Read them on Google</a>' if p.get("maps_url") else ""
        reviews_section = (
            '<section id="reviews"><div class="wrap"><h2 class="t">What customers say</h2>'
            '<p class="intro">The live site would show a few of these reviews right here.</p>'
            f'<div class="score">{stars(rating, False)}<b>{e(rating)}</b><span>from {e(reviews)} Google reviews</span>{more}</div></div></section>')
        nav_reviews = '<a href="#reviews">Reviews</a>'
    else:
        reviews_section, nav_reviews = "", ""

    areas = p.get("areas")
    zip_hint = {"Tampa": "33602"}.get(city, "")
    repl = {
        "{{name}}": e(name),
        "{{short}}": e(short),
        "{{contact_email}}": e(CONTACT),
        "{{mark_sub}}": f"<small>{e(city)}, {e(state)} roofing</small>",
        "{{nav_reviews}}": nav_reviews,
        "{{call_button}}": call,
        "{{call_big}}": call_big,
        "{{bar_call}}": bar_call,
        "{{place_line}}": e(p.get("place_line") or f"Roofing in {city}, {state}"),
        "{{headline}}": e(p.get("headline") or f"Roof repair and replacement in {city}"),
        "{{lede}}": (e(p.get("lede")) if p.get("lede") else
                     "Tell us what's going on and get a quote" + (f', or call <a href="tel:{e(tel(phone))}">{e(phone)}</a>.' if phone else ".")),
        "{{proof}}": "".join(proof),
        "{{zip_hint}}": zip_hint,
        "{{services_intro}}": e(p.get("services_intro") or f"The work {short} takes on, from a single leak to a whole new roof."),
        "{{services}}": "".join(svc_row(s) for s in services[:6]),
        "{{reviews_section}}": reviews_section,
        "{{area_title}}": e(p.get("area_title") or f"Serving {city} and nearby"),
        "{{area_text}}": e(p.get("area_text") or (f"Including {areas}." if areas else f"Homes and businesses across {city} and the surrounding area.")),
        "{{hours_line}}": e(p.get("hours") or ""),
        "{{address_line}}": f"<br>{e(p['address'])}" if p.get("address") else "",
        "{{phone_text}}": e(phone),
        "{{license_line}}": f"<br>License {e(p['license'])}" if p.get("license") else "",
        "{{biz_json}}": json.dumps({"name": name, "phone": phone}).replace("</", "<\\/"),
        "{{c_ink}}": t["ink"], "{{c_ink2}}": t["ink2"], "{{c_accent}}": t["accent"],
        "{{c_accent_ink}}": t["accent_ink"], "{{c_accent_deep}}": t["accent_deep"],
    }
    out = TEMPLATE
    for k, v in repl.items():
        out = out.replace(k, v)
    left = re.findall(r"\{\{[a-z_]+\}\}", out)
    assert not left, f"unfilled placeholders: {left}"
    return out


def main():
    src, out_dir = sys.argv[1], sys.argv[2]
    prospects = json.load(open(src, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    for p in prospects:
        d = os.path.join(out_dir, p["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(build(p))
    with open(os.path.join(out_dir, "_headers"), "w") as f:
        f.write("/*\n  X-Robots-Tag: noindex, nofollow\n")
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write('<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex">'
                '<title>Rawcoderz concept previews</title><body style="font-family:system-ui;padding:40px">'
                '<p>Concept previews by Rawcoderz. Each preview is private to the business it was made for.</p>')
    with open(os.path.join(out_dir, "robots.txt"), "w") as f:
        f.write("User-agent: *\nDisallow: /\n")
    print(f"built {len(prospects)} demos into {out_dir}")


if __name__ == "__main__":
    main()
