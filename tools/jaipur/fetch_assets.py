"""Fetch public reference assets and local fonts for the Jaipur concept demos."""
from pathlib import Path
import concurrent.futures, json, re, urllib.request, urllib.parse

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / 'cache'
CACHE.mkdir(exist_ok=True)
PHOTOS = {
 'coffee': '1509042239860-f550ce710b93',
 'pour': '1495474472287-4d71bcdd2085',
 'espresso': '1514432324607-a09d9b4aefdd',
 'pizza': '1513104890138-7c749659a591',
 'burger': '1568901346375-23c9450c58cd',
 'pasta': '1473093295043-cdd812d0e601',
 'salad': '1512621776951-a57141f2eefd',
 'indian': '1546833999-b9f581a1996d',
 'bread': '1509440159596-0249088772ff',
 'croissant': '1555507036-ab1f4038808a',
 'plated': '1414235077428-338989a2e8c0',
 'kitchen': '1556911220-bff31c812dba',
 'table': '1517248135467-4c7edcad34c4',
 'cake': '1578985545062-69928b1d9587',
 'tea': '1544787219-7f47ccb76574',
 'curry': '1565557623262-b51c2513a641',
 'paneer': '1631452180519-c014fe946bc7',
 'margherita': '1571407970349-bc81e7e96d47',
 'veg-pizza': '1574071318508-1cdbab80d002',
}
URLS = {k: f'https://images.unsplash.com/photo-{v}?auto=format&fit=crop&w=1440&q=82' for k,v in PHOTOS.items()}
URLS.update({
 'kanha-logo': 'https://kanha.co/wp-content/uploads/2023/11/Logo-for-brands.png',
 'tansukh-logo': 'https://kanha.co/wp-content/uploads/2023/10/tansukh-logo.png',
 'rawat-logo': 'https://rawatmisthanbhandar.in/assets/img/logo/nav-log.png',
 'tapri-logo': 'https://tapri.net/image/catalog/s-logo.png',
 'curious-life-logo': 'https://curiouslifecoffee.com/wp-content/uploads/2019/10/cropped-new-logo-1.png',
 'lmb-logo': 'https://lmbsweets.com/wp-content/uploads/2020/09/LMBLogoUpdated.png',
 'thali-and-more-logo': 'https://thaliandmore.co.in/img/logo.png',
 'niros-logo': 'https://nirosindia.com/wp-content/uploads/2018/01/logo.png',
 'chokhi-dhani-logo': 'https://chokhidhani.com/village-fair-restaurant-jaipur/wp-content/uploads/2022/07/logo.png',
 'sweets': 'https://lmbsweets.com/wp-content/uploads/2022/07/LMB-Diwali-26-1-68-scaled.jpg',
 'kachori': 'https://lmbsweets.com/wp-content/uploads/2021/02/59.jpg',
 'tapri-room': 'https://tapri.net/image/cache/catalog/Home%20Page%20Slider/9-697x471.jpg',
 'niros-room': 'https://nirosindia.com/wp-content/uploads/2018/01/slider.jpg',
 'chokhi-food': 'https://chokhidhani.com/village-fair-restaurant-jaipur/wp-content/uploads/2026/09/Food.jpg',
 'kanha-group-logo': 'https://kanha.co/wp-content/uploads/2026/01/Kanha-Group-Logo.png',
 'kanha-food': 'https://kanha.co/wp-content/uploads/2023/10/QSR-03.jpg',
 'rawat-food': 'https://rawatmisthanbhandar.in/assets/img/banner/banner14.png',
 'rawat-snacks': 'https://rawatmisthanbhandar.in/assets/img/banner/banner12.png',
 'kanha-katli': 'https://kanha.co/wp-content/uploads/2023/10/Kaju-Katli.png',
 'kanha-jamun': 'https://kanha.co/wp-content/uploads/2023/10/Gulab-Jamun.png',
})

def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'})
 with urllib.request.urlopen(req,timeout=40) as response:return response.read()

def fetch(pair):
 key,url=pair
 suffix='.png' if key.endswith('-logo') else '.jpg'
 target=CACHE/(key+suffix)
 try:
  if not target.exists():target.write_bytes(get(url))
  return key,{'file':target.name,'url':url,'bytes':target.stat().st_size}
 except Exception as error:return key,{'url':url,'error':str(error)}

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
 manifest=dict(ex.map(fetch,URLS.items()))

fonts=['Fraunces','DM Sans','Cormorant Garamond','Manrope','Barlow Condensed','Work Sans','DM Serif Display','Outfit','Syne']
for family in fonts:
 key='font-'+family.lower().replace(' ','-')
 try:
  css=get('https://fonts.googleapis.com/css2?family='+urllib.parse.quote(family)+':wght@400&display=swap').decode()
  matches=re.findall(r'src:\s*url\(([^)]+)\)',css)
  if not matches:raise RuntimeError('Font file URL absent')
  # Google Fonts places the Latin subset last. Keep fonts self-hosted.
  url=matches[-1];target=CACHE/(key+'.woff2')
  target.write_bytes(get(url))
  manifest[key]={'file':target.name,'url':url,'family':family,'bytes':target.stat().st_size}
 except Exception as error:manifest[key]={'error':str(error),'family':family}
def license_font(family):
 slug=family.lower().replace(' ','')
 url=f'https://raw.githubusercontent.com/google/fonts/main/ofl/{slug}/OFL.txt'
 target=CACHE/('license-'+family.lower().replace(' ','-')+'.txt')
 if not target.exists():target.write_bytes(get(url))
 return family
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 list(ex.map(license_font,fonts))
(CACHE/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'downloaded':sum('file' in item for item in manifest.values()),'failures':{k:v for k,v in manifest.items() if 'error' in v}},indent=2))
