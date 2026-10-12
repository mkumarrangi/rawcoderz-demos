"""Create personalised outreach drafts only. Never sends email or messages."""
from pathlib import Path
from email.message import EmailMessage
from email import policy
import json,re,urllib.parse

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
OUT=ROOT/'rawcoderz/jaipur/outreach'
OUT.mkdir(exist_ok=True)
EMAILS=OUT/'email-drafts';EMAILS.mkdir(exist_ok=True)
brands=json.loads((HERE/'brands.json').read_text(encoding='utf-8'))
copyRows=json.loads((HERE/'outreach-copy.json').read_text(encoding='utf-8'))
plainPhrases={'coffee-first':'coffee','coffee-led':'coffee','blue-toned':'blue','editorial-style':'editorial','coffee-and-bakery':'coffee and bakery','pizza-first':'pizza','dining-led':'dining','Rajasthan-inspired':'Rajasthani','flavour-led':'Indian dining','chai-first':'chai','fresh-food-focused':'fresh food','bistro-style':'bistro','phone-friendly':'mobile','browser-based':'web','an app-free route':'a route in the browser','coffee-and-food pairing':'coffee and food pairing','chai-and-snack pairing':'chai and snack pairing','one-outlet pilot idea':'pilot at one outlet','one-outlet pilot':'pilot at one outlet'}
for row in copyRows:
 for key in ('subject','intro','benefit','whatsapp','cta'):
  if key in row:
   for old,new in plainPhrases.items():row[key]=row[key].replace(old,new)
copy={row['slug']:row for row in copyRows}
assert len(copy)==len(brands)==28
base='https://demo.rawcoderz.com/rawcoderz/jaipur/'
sender={'name':'Mukesh Kumar','company':'Rawcoderz','email':'mukesh.kumar@rawcoderz.com','phone':'+91 86969 75043','website':'https://www.rawcoderz.com/'}
contactSignature=f"{sender['name']}\n{sender['company']} | {sender['website']}\n{sender['email']} | {sender['phone']}"
signature='Best,\n'+contactSignature
disclosure='The menu and prices are samples; ordering is a demo.'
defaultCTA='Would you be open to a 10-minute walkthrough?'
display={'tansukh':'Tansukh','lmb':'LMB','chokhi-dhani':'Chokhi Dhani','the-karchi-restaurant':'The Karchi','on-the-house':'On The House','tapri':'Tapri','curious-life':'Curious Life'}
phoneUpdates={
 'the-social-belly':[
  {'number':'919929936808','label':'+91 99299 36808','sourceLabel':'District business listing','source':'https://www.district.in/dining/jaipur/the-social-belly-jagatpura','status':'Public listing; WhatsApp availability unconfirmed'}],
 'the-bhatura-project':[
  {'number':'919928333300','label':'+91 99283 33300','sourceLabel':'District business listing','source':'https://www.district.in/dining/jaipur/the-bhatura-project-raja-park','status':'Public listing; WhatsApp availability unconfirmed'},
  {'number':'919414072370','label':'+91 94140 72370','sourceLabel':'District alternative contact','source':'https://www.district.in/dining/jaipur/the-bhatura-project-raja-park','status':'Alternative on the same listing; WhatsApp availability unconfirmed'}],
 'the-karchi-restaurant':[
  {'number':'918440800404','label':'+91 84408 00404','sourceLabel':'District business listing','source':'https://www.district.in/dining/jaipur/the-karchi-raja-park','status':'Conflicting listing numbers; confirm the venue'},
  {'number':'918949601506','label':'+91 89496 01506','sourceLabel':'Magicpin conflicting contact','source':'https://magicpin.in/Jaipur/Raja-Park/Restaurant/The-Karchi/store/1b6a181','status':'Conflicts with District; confirm the venue'}],
 'la-fiamma':[
  {'number':'919352524740','label':'+91 93525 24740','sourceLabel':'C Scheme Zomato contact listing','source':'https://www.zomato.com/jaipur/la-fiamma-c-scheme/order','status':'Conflicting listing numbers; confirm the intended outlet'},
  {'number':'919041301638','label':'+91 90413 01638','sourceLabel':'Claimed C Scheme Tripadvisor listing','source':'https://www.tripadvisor.in/Restaurant_Review-g304555-d34567765-Reviews-La_Fiamma-Jaipur_Jaipur_District_Rajasthan.html','status':'Conflicts with Zomato; confirm the intended outlet'}],
}

def write(path,text):path.write_text(text,encoding='utf-8',newline='\n')
def save_eml(filename,recipient,subject,body):
 msg=EmailMessage(policy=policy.SMTP)
 msg['From']=f"{sender['name']} - {sender['company']} <{sender['email']}>"
 msg['Reply-To']=sender['email']
 msg['To']=recipient;msg['Subject']=subject
 msg.set_content(body)
 (EMAILS/(filename+'.eml')).write_bytes(msg.as_bytes())

rows=[]
for b in brands:
 c=copy[b['slug']];short=display.get(b['slug'],b['name']);url=base+b['slug']+'/'
 body=f"Hi {short} team,\n\n{c['intro']}\n\n{c['benefit']}\n\nView your demo: {url}\n\n{disclosure}\n\n{c.get('cta',defaultCTA)}\n\n{signature}"
 row={'brand':b['name'],'slug':b['slug'],'recipient':b['email'],'recipientStatus':b['emailQuality'],'channel':'email' if b['email'] else 'WhatsApp','demoUrl':url,'subject':c['subject'],'emailBody':body,'priority':b['priority'],'phones':[]}
 if not b['email']:
  message=f"Hi {short} team, we’re Rawcoderz. {c['whatsapp']}\n\nDemo: {url}\n\nIt uses sample content; no real orders are taken. Would the owner or manager be open to a quick 10-minute walkthrough?\n\n{contactSignature}"
  phones=phoneUpdates.get(b['slug'])
  if not phones:
   digits=re.sub(r'\D','',b['phone'])
   assert re.fullmatch(r'91[6-9]\d{9}',digits),f'No usable candidate phone: {b["slug"]}'
   phones=[{'number':digits,'label':b['phone'],'sourceLabel':'Original supplied prospect response','source':'../source-response.md','status':'Supplied number; business match and WhatsApp availability unconfirmed'}]
  row['whatsappBody']=message
  row['phones']=[dict(p,chatUrl='https://wa.me/'+p['number']+'?text='+urllib.parse.quote(message,safe='')) for p in phones]
 rows.append(row)
 if b['email'] and b['slug'] not in ('kanha','tansukh'):save_eml(b['slug'],b['email'],c['subject'],body)

groupSubject='Two visual-menu concepts for Kanha and Tansukh'
groupBody=f'''Hi Kanha team,

We’re Rawcoderz, and we built two website concepts: one for Kanha’s sweets, quick bites and meals, and one for Tansukh’s dining experience.

Both show how guests could browse a visual menu, choose preferences and build a table or pickup order on their phones.

Kanha demo: {base}kanha/
Tansukh demo: {base}tansukh/

{disclosure}

Would your operations team be open to a 10-minute walkthrough of a one-outlet pilot alongside your current setup?

{signature}'''
save_eml('kanha-and-tansukh','info@kanha.co',groupSubject,groupBody)
group={'recipient':'info@kanha.co','subject':groupSubject,'body':groupBody}
assert len(list(EMAILS.glob('*.eml')))==14
assert sum(r['channel']=='WhatsApp' for r in rows)==13

preferred=['curious-life','tapri','cafe-lazymojo','on-the-house','anokhi-cafe','niros','spice-court','kanha','tansukh','rawat-misthan-bhandar','lmb','chokhi-dhani','handi','thali-and-more','cafe-bluez']
rows.sort(key=lambda r:preferred.index(r['slug']) if r['slug'] in preferred else 100+next(b['index'] for b in brands if b['slug']==r['slug']))
write(OUT/'drafts.json',json.dumps({'date':'2026-10-11','sent':False,'sender':sender,'brands':rows,'recommendedGroupEmail':group},ensure_ascii=False,indent=2)+'\n')

index='\n'.join(f'| {r["brand"]} | {r["recipient"] or "Email missing — use WhatsApp"} | [View demo]({r["demoUrl"]}) |' for r in rows)
sections=[]
for i,r in enumerate(rows,1):
 note='Published candidate email; see the contact register for its source.' if r['recipient'] else 'No email on file. Use the personalised WhatsApp draft instead; email copy is retained here for reference.'
 if r['slug'] in ('kanha','tansukh'):note+=' Shared group inbox: use the combined draft below instead of sending both individual drafts.'
 sections.append(f'''## {i:02}. {r['brand']}

Recipient: {r['recipient'] or 'Pending — no email address available'}  
Contact status: {r['recipientStatus']}  
{note}

**Subject: {r['subject']}**

{r['emailBody']}
''')
write(OUT/'personalised-emails.md',f'''# Personalised Jaipur outreach emails

Prepared: 11 October 2026. Drafts only; nothing has been sent.

Sender: {sender['name']} — {sender['company']} <{sender['email']}>  
Website: {sender['website']} · Phone: {sender['phone']}

All 28 brand drafts contain the correct deployed demo URL. Fifteen brand records have published candidate email addresses (14 unique inboxes). The other 13 have personalised [WhatsApp messages](whatsapp-messages.md). Sources and contact caveats are in the [email register](../email-contacts.md).

Kanha and Tansukh share `info@kanha.co`: use the combined email at the end, rather than two separate introductions. Fourteen addressed `.eml` files are in [email-drafts](email-drafts/README.md), covering the 15 brands with published email contacts. The 28 individual drafts below are retained so every brand has its own copy.

The demo is linked in each message; no ZIP or website files need to be attached. All 28 live URLs returned HTTP 200 and the matching brand page on 11 October 2026. Menu and price disclosures remain in the copy because these are concepts.

## Recipient and demo index

| Brand | Email / route | Demo |
| --- | --- | --- |
{index}

{chr(10).join(sections)}
## Recommended combined email — Kanha and Tansukh

Recipient: info@kanha.co  
Use this instead of the two individual emails above.

**Subject: {groupSubject}**

{groupBody}
''')

whatsapp=[]
for i,r in enumerate((r for r in rows if r['channel']=='WhatsApp'),1):
 phoneLines='\n'.join(f'- {p["label"]}: [Open WhatsApp with draft]({p["chatUrl"]}) · [Source]({p["source"]}) · {p["status"]}.' for p in r['phones'])
 whatsapp.append(f'''## {i:02}. {r['brand']}

{phoneLines}

**Message to copy:**

{r['whatsappBody']}
''')
write(OUT/'whatsapp-messages.md',f'''# Personalised WhatsApp messages — 13 Jaipur prospects

Prepared: 11 October 2026. These are the 13 brands without a published email in our register. Nothing has been sent.

Every message includes {sender['name']}'s Rawcoderz signature, website, business email and phone number.

Each link opens a chat with the draft filled in; you review the business identity and choose whether to send. WhatsApp registration has not been tested. Nine numbers come from the original supplied prospect response; four brands have listing-sourced contact candidates or updates. La Fiamma and The Karchi have conflicting listing numbers; the alternatives are kept visible. The Bhatura Project lists two numbers on the same District page.

The demo URL is already included in each message. No file attachment is needed. Original listing sources are linked next to the numbers. The “no real orders” sentence explains the demo accurately.

{chr(10).join(whatsapp)}
''')

emlLinks='\n'.join(f'- [{path.stem.replace("-"," ")}]({path.name})' for path in sorted(EMAILS.glob('*.eml')))
write(EMAILS/'README.md',f'''# Addressed email drafts

14 RFC 822 `.eml` files, covering 15 brands with published candidate emails. Kanha and Tansukh are combined into one email because they share the group inbox.

Sender: {sender['name']} — {sender['company']} <{sender['email']}>. This address is set in the From and Reply-To fields of every file. Each body includes the Rawcoderz website, business email and phone number.

Open in a mail client as a draft/template if supported, or copy the subject and body from [the full email document](../personalised-emails.md). Nothing was sent. Opening/import behaviour varies between mail clients.

Listing-sourced recipients still need a business identity check; see [the contact register](../../email-contacts.md). These files contain plain-text demo links, not attachments or tracking pixels.

{emlLinks}
''')

routing=[]
for slug,phones in phoneUpdates.items():
 name=next(r['brand'] for r in rows if r['slug']==slug)
 routing.append(f'## {name}\n\n'+'\n'.join(f'- **{p["label"]}** — [{p["sourceLabel"]}]({p["source"]}). {p["status"]}.' for p in phones))
write(OUT/'contact-routing.md',f'''# WhatsApp contact follow-up

Reviewed: 11 October 2026. These notes supplement the original prospect register. Published phone numbers do not establish that WhatsApp is enabled or identify the person making buying decisions. No messages or calls were made.

The Social Belly, The Bhatura Project and The Karchi previously had no phone in the supplied response. The following restaurant listings provide candidate numbers. La Fiamma’s existing conflict is also retained. Original prospect descriptions and phone provenance have not been silently replaced.

{(chr(10)*2).join(routing)}

All other WhatsApp fallback numbers are copied from the supplied prospect response and remain unconfirmed. The Social Belly recruitment-only WhatsApp number was not substituted for its general restaurant contact.
''')

write(OUT/'README.md',f'''# Jaipur outreach pack

Sender: {sender['name']} — {sender['company']} <{sender['email']}>  
Website: {sender['website']} · Phone: {sender['phone']}

All email and WhatsApp drafts include these contact details in a short signature. The email draft files also use the business email in their From and Reply-To fields.

- [All 28 personalised email drafts](personalised-emails.md), each with its own live demo link.
- [14 addressed email draft files](email-drafts/README.md), covering 15 brands; Kanha and Tansukh share one combined introduction.
- [13 personalised WhatsApp messages](whatsapp-messages.md) for brands without email addresses, with prefilled chat links and phone provenance.
- [Contact routing and newly found phone numbers](contact-routing.md).
- [Demo URL check results](demo-link-checks.json): all 28 matching brand pages returned HTTP 200 on 11 October 2026.

Nothing has been sent. Published emails and phone numbers remain candidate contacts; listing-only and conflicting details are marked. The message copy contains no invented testimonials, guaranteed queue reductions, pricing promises, or claims that a business has no website. The demo uses sample menus and prices, and no real order is taken.

Copy a subject and body into your email app, or open an addressed `.eml` where supported. For WhatsApp, open the prefilled link, confirm the venue identity and review the text before sending. The demo is already linked in every message; no website ZIP or file attachment is necessary.
''')

register=ROOT/'rawcoderz/jaipur/README.md';text=register.read_text(encoding='utf-8')
if '## Prepared outreach drafts' not in text:
 write(register,text.rstrip()+'''\n\n## Prepared outreach drafts

[Open the outreach pack](outreach/README.md): 28 personalised email drafts, 14 addressed `.eml` files (Kanha and Tansukh combined), and 13 WhatsApp fallback messages. Each includes the corresponding live demo URL. [Phone follow-up](outreach/contact-routing.md) supplements the original records for The Social Belly, The Bhatura Project and The Karchi, and preserves La Fiamma's conflicting contact candidates. No outreach has been sent.
''')
print(json.dumps({'brandDrafts':len(rows),'addressedEmailFiles':14,'WhatsAppDrafts':13,'output':str(OUT)},indent=2))
