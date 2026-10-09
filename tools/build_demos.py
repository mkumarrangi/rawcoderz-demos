"""Build one concept homepage per prospect from public facts only.

Usage (from the repo root): python3 tools/build_demos.py prospects.json .
prospects.json: list of objects with slug, business, phone, rating, reviews,
maps_url, city, state, address (optional), services (optional list),
why_extra (optional list of [big, small] pairs, e.g. ["Since 1950", "Three generations"]).
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = open(os.path.join(HERE, "roof_template.html"), encoding="utf-8").read()
CONTACT = "mukesh.kumar@rawcoderz.com"

DEFAULT_SERVICES = [
    ("Roof repair", "Leaks, missing shingles and flashing fixed before they spread."),
    ("Roof replacement", "Full tear-off and new roof, with a clear written quote."),
    ("Inspections", "A straight answer on your roof's condition, with photos."),
]


def e(v):
    return html.escape(str(v), quote=True)


def tel(phone):
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) == 10:
        digits = "1" + digits
    return "+" + digits if digits else ""


def build(p):
    name = p["business"]
    phone = p.get("phone") or ""
    t = tel(phone)
    call = f'<a class="call" href="tel:{e(t)}">Call {e(phone)}</a>' if phone else '<a class="call" href="#q">Free quote</a>'
    mobile_call = f'<a class="b" href="tel:{e(t)}">Call</a>' if phone else ""
    rating, reviews = p.get("rating"), p.get("reviews")
    stars = ""
    if rating and reviews:
        stars = f'<span class="stars"><span>★★★★★</span>{e(rating)} on Google · {e(reviews)} reviews</span>'
    maps = f'<a href="{e(p["maps_url"])}" target="_blank" rel="noopener">Read the reviews on Google</a>' if p.get("maps_url") else ""
    city = p.get("city") or "Tampa"
    area_label = f"{city}, {p.get('state') or 'FL'} roofing"
    lede_tail = f"Call {phone} or send a request below." if phone else "Send a request below."
    services = p.get("services") or []
    svc_pairs = [(s, "") for s in services][:6] if services else DEFAULT_SERVICES
    svc_html = "".join(
        f'<div class="svc"><h3>{e(a)}</h3>' + (f"<p>{e(b)}</p>" if b else "") + "</div>" for a, b in svc_pairs
    )
    why = []
    for big, small in p.get("why_extra") or []:
        why.append(f"<div><b>{e(big)}</b>{e(small)}</div>")
    if rating and reviews:
        why.append(f"<div><b>{e(rating)} ★</b>Average from {e(reviews)} Google reviews</div>")
    why.append("<div><b>30 sec</b>To request a free quote, day or night</div>")
    why.append(f"<div><b>Local</b>Serving {e(city)} and nearby areas</div>")
    address_line = f" · {e(p['address'])}" if p.get("address") else ""
    out = TEMPLATE
    repl = {
        "{{name}}": e(name),
        "{{contact_email}}": e(CONTACT),
        "{{call_button}}": call,
        "{{mobile_call}}": mobile_call,
        "{{area_label}}": e(area_label),
        "{{lede_tail}}": e(lede_tail),
        "{{stars_badge}}": stars,
        "{{maps_link}}": maps,
        "{{services}}": svc_html,
        "{{why}}": "".join(why),
        "{{city}}": e(city),
        "{{address_line}}": address_line,
        "{{phone_text}}": e(phone),
    }
    for k, v in repl.items():
        out = out.replace(k, v)
    assert "{{" not in out, "unfilled placeholder"
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
