"""Verify standalone file references and save the delivery QA summary."""
from pathlib import Path
from html.parser import HTMLParser
from PIL import Image,ImageOps,ImageDraw
import json,re
HERE=Path(__file__).resolve().parent
OUT=HERE.parents[1]/'rawcoderz/jaipur'
brands=json.loads((HERE/'brands.json').read_text(encoding='utf-8'))
results=json.loads((HERE/'qa/results.json').read_text(encoding='utf-8'))
final=json.loads((HERE/'qa/final-check.json').read_text(encoding='utf-8'))
assert results['passed']==28 and not results['failures'], 'Browser checks must pass first'
assert not final['failures'], 'Visual checks must pass first'
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  for key in ('href','src'):
   target=a.get(key,'')
   if not target or target.startswith(('#','http:','https:','data:','mailto:','tel:')):continue
   assert (self.base/target.split('?')[0].split('#')[0]).is_file(), f'Missing {self.base}/{target}'
total=0
for b in brands:
 folder=OUT/b['slug'];parser=Links();parser.base=folder;parser.feed((folder/'index.html').read_text(encoding='utf-8'))
 for url in re.findall(r'url\("([^\"]+)"\)',(folder/'styles.css').read_text(encoding='utf-8')):
  if not url.startswith('data:'):assert (folder/url).is_file()
 data=json.loads((folder/'site-data.js').read_text(encoding='utf-8').removeprefix('window.BRAND = ').strip().removesuffix(';'))
 assert len(data['menu'])==8
 for item in data['menu']:assert (folder/item['image']).is_file()
 assert len(list((folder/'assets').glob('license-*.txt')))==2
 size=sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())
 assert max(p.stat().st_size for p in folder.rglob('*') if p.is_file())<25*1024*1024
 total+=size
parser=Links();parser.base=OUT;parser.feed((OUT/'index.html').read_text(encoding='utf-8'))
representatives=['the-messy-door-cafe','cosmos-cafe','kanha','tansukh','la-fiamma','tapri','curious-life','anokhi-cafe']
sheet=Image.new('RGB',(1200,4*447),'#f3efe5');draw=ImageDraw.Draw(sheet)
for i,slug in enumerate(representatives):
 with Image.open(HERE/'qa'/f'{slug}-desktop.png') as im:
  crop=im.crop((0,0,1440,950)).resize((590,389),Image.Resampling.LANCZOS)
  x,y=(i%2)*600,(i//2)*447;sheet.paste(crop,(x,y));draw.text((x+10,y+405),slug,fill='#193f35')
sheet.save(HERE/'qa/desktop-directions.jpg',quality=90)
sheet=Image.new('RGB',(4*220,7*552),'#f3efe5');draw=ImageDraw.Draw(sheet)
for i,b in enumerate(brands):
 with Image.open(HERE/'qa'/f'{b["slug"]}-mobile.png') as im:
  crop=im.crop((0,0,390,930)).resize((210,500),Image.Resampling.LANCZOS)
  x,y=(i%4)*220,(i//4)*552;sheet.paste(crop,(x,y));draw.text((x+4,y+512),b['slug'][:28],fill='#193f35')
sheet.save(HERE/'qa/mobile-directions.jpg',quality=90)
report=f'''# Jaipur demo verification

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

The 28 standalone brand folders total approximately {total/1024/1024:.1f} MiB. Each folder can be uploaded separately; every individual file is below [Cloudflare Pages' documented 25 MiB file limit](https://developers.cloudflare.com/pages/get-started/direct-upload/).

Representative desktop screenshots and all mobile screenshots were captured in `tools/jaipur/qa/` for visual review. Checks do not establish brand approval, dietary accuracy, inbox activity, production accessibility certification or business operating details.
'''
(OUT/'QA-REPORT.md').write_text(report,encoding='utf-8')
print(json.dumps({'standaloneSites':28,'menuItems':224,'totalMiB':round(total/1024/1024,1),'references':'all present'},indent=2))
