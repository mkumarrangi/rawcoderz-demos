"""Build 28 standalone, dependency-free Jaipur restaurant concepts."""
from pathlib import Path
from PIL import Image, ImageOps
import json, html, shutil, re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'rawcoderz' / 'jaipur'
CACHE = HERE / 'cache'
BRANDS = json.loads((HERE / 'brands.json').read_text(encoding='utf-8'))
ASSETS = json.loads((CACHE / 'manifest.json').read_text(encoding='utf-8'))
CSS = (HERE / 'site.css').read_text(encoding='utf-8')
JS = (HERE / 'app.js').read_text(encoding='utf-8')
E = lambda s: html.escape(str(s), quote=True)
ICONS = {
 'arrow': '<path d="M5 12h14m-6-6 6 6-6 6"/>',
 'bag': '<path d="M6 7h12l2 14H4L6 7Zm3 0V5a3 3 0 0 1 6 0v2"/>',
 'menu': '<path d="M5 8h14M5 16h14"/>',
 'close': '<path d="m6 6 12 12M6 18 18 6"/>',
 'search': '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
 'leaf': '<path d="M20 4C11 3 3 7 5 15c7 5 15-1 15-11ZM4 21 15 10"/>',
 'cup': '<path d="M4 8h12v6a6 6 0 0 1-12 0V8Zm12 0h2a3 3 0 0 1 0 6h-2M5 22h12M7 3v2M12 2v3"/>',
 'pin': '<path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 0 1 14 0Z"/><circle cx="12" cy="10" r="2"/>',
 'spark': '<path d="m12 2 2.8 7.2L22 12l-7.2 2.8L12 22l-2.8-7.2L2 12l7.2-2.8L12 2Z"/>',
 'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v.1"/>',
 'check': '<path d="m5 12 4 4L19 6"/>',
}
def icon(name): return f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'

# Illustrative menus, never presented as the venue's actual products or prices.
# name, description, INR, photo category
BANK = {
 'coffee': [
  ('Flat white', 'A double espresso, silky milk and a beautifully small pause.', 180, 'coffee'),
  ('Iced latte', 'Espresso over ice, finished with cold milk.', 210, 'espresso'),
  ('Cappuccino', 'A familiar favourite with a soft, foamy finish.', 180, 'pour')],
 'filter': [
  ('Slow pour-over', 'A clean, gentle cup. Take a moment with it.', 240, 'pour'),
  ('Cold brew', 'Slow-steeped coffee, poured over ice.', 230, 'espresso'),
  ('Black coffee', 'Simply coffee. Brewed for your next slow morning.', 170, 'coffee')],
 'chai': [
  ('Adrak chai', 'A warming cup with ginger and a little everyday joy.', 80, 'tea'),
  ('Masala chai', 'Tea, milk and a comforting blend of whole spices.', 70, 'tea'),
  ('Elaichi chai', 'Cardamom-scented chai for a softer sort of afternoon.', 80, 'tea')],
 'bubble': [
  ('Brown sugar milk tea', 'Milk tea with chewy pearls and a brown sugar swirl.', 230, 'espresso'),
  ('Iced matcha milk tea', 'A mellow, milky green tea with a cool finish.', 250, 'tea'),
  ('Classic pearl tea', 'A playful tea break with a little extra texture.', 210, 'tea')],
 'pizza': [
  ('Margherita', 'Tomato, mozzarella and basil. The lovely original.', 390, 'pizza'),
  ('Pesto paneer pizza', 'Basil pesto, paneer and a generous cheese finish.', 490, 'pizza'),
  ('Smoky garden pizza', 'Roasted vegetables, tomato and mozzarella.', 450, 'pizza')],
 'pasta': [
  ('Pesto primavera', 'Pasta, green pesto and a colourful vegetable finish.', 350, 'pasta'),
  ('Pomodoro pasta', 'A bright tomato sauce with basil and garlic.', 320, 'pasta'),
  ('Creamy mushroom pasta', 'Mushrooms and a mellow cream sauce.', 360, 'pasta')],
 'burger': [
  ('Garden crunch burger', 'A vegetable patty, crisp greens and house-style sauce.', 260, 'burger'),
  ('Paneer stack burger', 'Spiced paneer, fresh vegetables and a soft bun.', 290, 'burger'),
  ('Classic veggie burger', 'All the familiar layers, ready for a hungry afternoon.', 230, 'burger')],
 'noodle': [
  ('Chilli garlic noodles', 'Tossed vegetables, garlic and a little chilli warmth.', 240, 'pasta'),
  ('Vegetable noodle bowl', 'A generous bowl of noodles and colourful vegetables.', 230, 'pasta'),
  ('Sesame noodle bowl', 'Noodles with sesame, greens and a savoury finish.', 260, 'pasta')],
 'garden': [
  ('Seasonal garden bowl', 'Leaves, grains and a bright seasonal dressing.', 290, 'salad'),
  ('Avocado sourdough', 'Sourdough, avocado, greens and lemon.', 330, 'bread'),
  ('Roasted vegetable plate', 'A colourful plate with herbs and a little crunch.', 310, 'salad')],
 'breakfast': [
  ('Morning sourdough', 'Toasted sourdough, greens and a fresh start.', 280, 'bread'),
  ('Breakfast garden bowl', 'A bright bowl of vegetables, grains and good textures.', 290, 'salad'),
  ('Butter croissant', 'Golden layers for a slower morning.', 170, 'croissant')],
 'bakery': [
  ('Butter croissant', 'Flaky, buttery layers. Especially good with coffee.', 170, 'croissant'),
  ('Cinnamon morning bun', 'Soft pastry with cinnamon and a sweet finish.', 190, 'bread'),
  ('Toasted sourdough', 'A golden toast with butter on the side.', 150, 'bread')],
 'sandwich': [
  ('Pesto garden sandwich', 'Roasted vegetables, pesto and toasted bread.', 260, 'bread'),
  ('Paneer & greens wrap', 'Warm paneer, crisp leaves and a soft wrap.', 280, 'salad'),
  ('Cheese toastie', 'A golden sandwich with a melting cheese centre.', 220, 'bread')],
 'dessert': [
  ('Chocolate celebration cake', 'A rich chocolate slice for a sweet little moment.', 240, 'cake'),
  ('Warm chocolate brownie', 'A soft chocolate centre with a cosy finish.', 180, 'cake'),
  ('Sweet pastry of the day', 'An illustrative bakery selection for your coffee break.', 190, 'croissant')],
 'cooler': [
  ('Lemon mint cooler', 'Lemon, mint and plenty of ice.', 150, 'tea'),
  ('Peach iced tea', 'A bright, cold tea with a peachy finish.', 170, 'tea'),
  ('Rose lassi', 'A creamy yoghurt drink with a soft rose note.', 160, 'tea')],
 'chaat': [
  ('Papdi chaat', 'Crisp papdi, yoghurt and a lively chutney finish.', 150, 'indian'),
  ('Samosa chaat', 'Warm samosa, chole and sweet-tangy chutneys.', 160, 'curry'),
  ('Aloo tikki chaat', 'Golden potato patties with yoghurt and chutneys.', 140, 'indian')],
 'snack': [
  ('Masala toast', 'Toasted bread with a spiced vegetable filling.', 180, 'bread'),
  ('Paneer bites', 'A warm, spiced paneer plate to share.', 240, 'curry'),
  ('Garden small plate', 'A colourful little plate for the middle of the table.', 220, 'salad')],
 'indian': [
  ('Paneer masala', 'Paneer in a rich, warmly spiced tomato gravy.', 320, 'curry'),
  ('Dal makhani', 'A slow-style black lentil preparation with a creamy finish.', 290, 'indian'),
  ('Seasonal vegetable curry', 'A comforting vegetable preparation with Indian spices.', 280, 'curry')],
 'rajasthani': [
  ('Dal baati plate', 'A sample Rajasthani plate with dal, baati and accompaniments.', 340, 'indian'),
  ('Gatte ki sabzi', 'Gram-flour dumplings in a warmly spiced gravy.', 290, 'curry'),
  ('Rajasthani sharing plate', 'An illustrative selection for a little more of Rajasthan.', 420, 'indian')],
 'thali': [
  ('Rajasthani thali', 'A sample selection of curries, breads, rice and a sweet finish.', 420, 'indian'),
  ('Comfort mini thali', 'A smaller sample meal with dal, vegetables and bread.', 290, 'curry'),
  ('Family meal plate', 'A generous illustrative selection for a relaxed lunch.', 390, 'indian')],
 'bread': [
  ('Garlic naan', 'Soft bread with garlic and a buttery finish.', 90, 'bread'),
  ('Tandoori roti', 'A simple whole-wheat bread for your favourite curry.', 50, 'bread'),
  ('Butter naan', 'A soft, buttery bread for the table.', 80, 'bread')],
 'mithai': [
  ('Kaju katli', 'A delicate cashew sweet. Sample portion: 250 g.', 220, 'mithai'),
  ('Gulab jamun', 'Two soft sweets with a fragrant syrup finish.', 110, 'mithai'),
  ('Festive mithai selection', 'An illustrative assortment for a sweet little celebration.', 260, 'mithai')],
 'gift': [
  ('Celebration box', 'A sample assorted mithai box, imagined for gifting.', 590, 'mithai'),
  ('Little joy box', 'A smaller illustrative sweet assortment for a thoughtful gift.', 390, 'mithai'),
  ('Family sweets box', 'A sample festive selection to bring to the table.', 790, 'mithai')],
 'bhatura': [
  ('Classic chole bhature', 'Fluffy bhature, warming chole and familiar accompaniments.', 220, 'indian'),
  ('Punjabi chole plate', 'A comforting chole preparation for a hearty meal.', 180, 'curry'),
  ('Bhature sharing plate', 'A generous sample plate made for hungry company.', 290, 'indian')],
 'kulcha': [
  ('Amritsari kulcha', 'A warm stuffed bread served with chole.', 230, 'bread'),
  ('Paneer kulcha', 'A soft bread with a spiced paneer centre.', 260, 'bread'),
  ('Aloo kulcha', 'Potato-stuffed bread with a familiar Punjabi finish.', 220, 'bread')],
 'continental': [
  ('Grilled garden plate', 'Vegetables, greens and a light herb finish.', 350, 'salad'),
  ('Pesto pasta', 'Pasta with basil pesto and seasonal vegetables.', 350, 'pasta'),
  ('Bistro sourdough', 'A toasted garden sandwich for a relaxed lunch.', 290, 'bread')],
}

def category_type(category):
 c=category.lower()
 for key, words in [
  ('bubble',['bubble']),('filter',['filter']),('coffee',['coffee','espresso']),
  ('chai',['chai']),('pizza',['pizza']),('pasta',['pasta']),('burger',['burger']),
  ('noodle',['noodle']),('thali',['thali','family meal','meals']),('gift',['gift']),
  ('mithai',['mithai']),('bhatura',['bhature']),('kulcha',['kulcha']),
  ('bread',['bread','tandoor']),('rajasthani',['rajasthani']),
  ('indian',['indian']),('continental',['continental','bistro']),
  ('breakfast',['breakfast']),('bakery',['bakery']),('sandwich',['sandwich','wrap']),
  ('garden',['garden']),('dessert',['dessert','sweet']),('cooler',['cooler','refreshment','lassi']),
  ('chaat',['chaat','desi snack','kachori']),('snack',['snack','quick bite','small plate','village bite','cafe plate'])]:
  if any(word in c for word in words):return key
 return 'snack'

def food_art(primary, accent):
 # Original decorative mithai illustration, avoiding another venue's branded products.
 return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480"><rect width="640" height="480" fill="{accent}"/><path d="M0 30h640M0 450h640" stroke="{primary}" opacity=".25"/><ellipse cx="320" cy="264" rx="239" ry="164" fill="#fff5dc"/><ellipse cx="320" cy="264" rx="212" ry="140" fill="none" stroke="{primary}" stroke-width="2" opacity=".4"/><g stroke="#caa768" stroke-width="2"><path d="m180 270 95-75 95 75-95 75Z" fill="#f1ddb4"/><path d="m290 200 95-75 95 75-95 75Z" fill="#f7e9cb"/><path d="m310 335 95-75 95 75-95 75Z" fill="#f1ddb4"/></g><g fill="#a87943"><ellipse cx="279" cy="264" rx="5" ry="15" transform="rotate(30 279 264)"/><ellipse cx="388" cy="195" rx="5" ry="15" transform="rotate(-20 388 195)"/><ellipse cx="405" cy="329" rx="5" ry="15" transform="rotate(35 405 329)"/></g><g fill="{primary}"><circle cx="184" cy="166" r="42"/><circle cx="156" cy="358" r="33"/></g><g fill="#e9b954" opacity=".8"><circle cx="176" cy="155" r="3"/><circle cx="193" cy="177" r="3"/><circle cx="166" cy="176" r="2"/><circle cx="150" cy="350" r="3"/><circle cx="165" cy="367" r="3"/></g></svg>'''

def menu_art(kind,b):
 base=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 480"><rect width="640" height="480" fill="{b["bg"]}"/><circle cx="320" cy="240" r="190" fill="{b["accent"]}" opacity=".45"/>'
 if kind=='burger':
  drawing='<ellipse cx="320" cy="389" rx="160" ry="17" fill="#293f3020"/><path d="M163 226c0-136 314-136 314 0Z" fill="#d99a48"/><path d="M169 221c10-115 292-115 302 0" fill="none" stroke="#f0bb6c" stroke-width="15"/><g fill="#fff2c9"><ellipse cx="246" cy="176" rx="4" ry="9" transform="rotate(-35 246 176)"/><ellipse cx="311" cy="158" rx="4" ry="9"/><ellipse cx="365" cy="173" rx="4" ry="9" transform="rotate(30 365 173)"/><ellipse cx="411" cy="194" rx="4" ry="9"/></g><path d="m164 238 25-12 24 15 34-14 32 16 27-14 28 14 30-14 24 14 29-14 25 13 33-8v25H164Z" fill="#71924a"/><rect x="172" y="263" width="296" height="22" rx="11" fill="#cc5340"/><path d="m178 287 67-5 79 26 76-26 63 5-14 28H190Z" fill="#e8bd50"/><rect x="166" y="315" width="308" height="29" rx="14" fill="#6f5b38"/><path d="M172 352h296c0 57-296 57-296 0Z" fill="#d99a48"/>'
 else:
  liquid='#b88c68' if kind=='bubble' else '#d8a768'
  drawing=f'<ellipse cx="320" cy="410" rx="98" ry="13" fill="#293f3018"/><path d="m349 69-24 246" fill="none" stroke="{b["primary"]}" stroke-width="15"/><path d="m231 146 29 241c5 29 115 29 120 0l29-241Z" fill="#fffaf0" stroke="#284f4a" stroke-width="3"/><path d="m242 202 22 178c5 20 108 20 112 0l23-178Z" fill="{liquid}"/><ellipse cx="320" cy="203" rx="78" ry="16" fill="#e5c59a"/><path d="m253 167 13 155" stroke="#fff" stroke-width="8" opacity=".6"/>'
  if kind=='bubble':
   drawing+='<g fill="#4e3630"><circle cx="283" cy="365" r="11"/><circle cx="309" cy="378" r="12"/><circle cx="338" cy="365" r="12"/><circle cx="359" cy="386" r="10"/><circle cx="291" cy="391" r="9"/><circle cx="331" cy="390" r="9"/></g>'
  else:drawing+='<g fill="#fff4d3" opacity=".8"><rect x="268" y="216" width="39" height="36" rx="7" transform="rotate(12 268 216)"/><rect x="326" y="249" width="39" height="36" rx="7" transform="rotate(-16 326 249)"/></g><path d="M367 166q-32-26-41 1 29 24 41-1Z" fill="#71924a"/>'
 return base+drawing+'</svg>'

def contrast(hexcolor):
 def lum(color):
  rgb=[int(color[i:i+2],16)/255 for i in (1,3,5)]
  linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
  return sum(a*b for a,b in zip(linear,[.2126,.7152,.0722]))
 luminance=lum(hexcolor)
 ratio=lambda color:(max(luminance,lum(color))+.05)/(min(luminance,lum(color))+.05)
 preferred=max(('#18231e','#fffdf5'),key=ratio)
 return preferred if ratio(preferred)>=4.5 else max(('#000000','#ffffff'),key=ratio)

def font_file(name):return 'font-'+name.lower().replace(' ','-')
def write(path, text):path.write_text(text,encoding='utf-8',newline='\n')
OPTIMIZED={}
def copy_photo(key, destination, width=1200):
 target=destination/(key+'.webp')
 cachekey=(key,width)
 if cachekey not in OPTIMIZED:
  original=CACHE/ASSETS[key]['file']
  tmp=CACHE/f'optimized-{key}-{width}.webp'
  if not tmp.exists() or tmp.stat().st_mtime<original.stat().st_mtime:
   with Image.open(original) as im:
    im=ImageOps.exif_transpose(im).convert('RGB')
    im.thumbnail((width,width*2),Image.Resampling.LANCZOS)
    im.save(tmp,'WEBP',quality=82,method=5)
  OPTIMIZED[cachekey]=tmp
 shutil.copyfile(OPTIMIZED[cachekey],target)
 return 'assets/'+target.name

def choose_hero(b):
 if b.get('hero'):return b['hero']
 return {'cafe':'coffee','coffee':'pour','pizza':'pizza','chaat':'indian','garden':'salad','burger':'burger','bhatura':'indian','indian':'curry','sweets':'indian','chai':'tea'}.get(b['menuType'],'coffee')

def make_menu(b):
 items=[]
 for i,category in enumerate(b['categories']):
  kind=category_type(category)
  entries=BANK[kind][:3 if i<2 else 2]
  for j,(name,desc,price,photo) in enumerate(entries):
   if kind in ('coffee','filter','chai','bubble','cooler'):
    optionLabel='Your cup';options=[{'label':'Regular','extra':0},{'label':'Large','extra':40}]
   elif kind in ('pizza','pasta','burger','sandwich'):
    optionLabel='Make it yours';options=[{'label':'Classic','extra':0},{'label':'Extra cheese','extra':40}]
   elif kind in ('indian','rajasthani','chaat','thali','bhatura','kulcha','snack','noodle'):
    optionLabel='Spice preference';options=[{'label':'Mild','extra':0},{'label':'Medium','extra':0},{'label':'Hot','extra':0}]
   else:
    optionLabel='Serving';options=[{'label':'One sample serving','extra':0},{'label':'Two sample servings','extra':price}]
   if b['slug']=='kanha' and kind=='mithai': photo=['kanha-katli','kanha-jamun','kanha-katli'][j]
   if b['slug']=='lmb' and 'kachori' in category.lower():photo='kachori'
   if b['slug']=='chokhi-dhani' and kind in ('rajasthani','thali'):photo='chokhi-food'
   items.append({'id':f'dish-{len(items)+1}','name':name,'description':desc,'price':price,'category':category,'photo':photo,'optionLabel':optionLabel,'options':options})
 return items

def render_site(b, menu, hero, small, story, logo):
 name=E(b['name']); short=E({'tansukh':'Tansukh','chokhi-dhani':'Chokhi Dhani','lmb':'LMB','curious-life':'Curious Life','rawat-misthan-bhandar':'Rawat','the-karchi-restaurant':'The Karchi'}.get(b['slug'],b['name']))
 brand=(f'<img src="{logo}" alt="{name}" width="170" height="70">' if logo else f'<span class="brand-icon">{icon("cup" if b["group"]=="cafe" else "spark")}</span><span>{short}<span class="brand-sub">Jaipur · a dining concept</span></span>')
 if logo and b['slug'] in ('kanha','rawat-misthan-bhandar','tapri'):
  brand=f'<img class="small-mark" src="{logo}" alt="" width="60" height="60"><span>{short}<span class="brand-sub">Jaipur · a dining concept</span></span>'
 filters=''.join(f'<button class="filter" data-filter="{E(c)}" aria-pressed="{str(i==0).lower()}">{E(c)}</button>' for i,c in enumerate(['All']+b['categories']))
 ribbon=''.join(f'<span>{E(c)}</span>' for c in b['categories']*4)
 categorytext=' · '.join(b['categories'])
 heroAlt='Public venue reference photograph' if b.get('hero') and b['hero'] not in ('tea','coffee','pizza') else 'Atmospheric food and café photography'
 if b['slug']=='lmb':heroAlt='LMB gift box from the public brand website'
 floating={'collage':'Stay a little longer.','orbit':'Take your time.','workshop':'Good food. Good company.','garden':'A bright little break.','street':'Big on chaska!','postcard':'Wish you were here.','conservatory':'A little greener.','pocket':'Good things, small moments.','checker':'Say cheese!','deco':'A little blue. A little bliss.','journal':'Coffee & a good page.','poster':'Bring your appetite.','engraved':'A little comfort.','celebration':'For every little celebration.','royal':'Make a meal of it.','oven':'A slice of the good life.','bazaar':'A little more Jaipur.','heritage':'Sweetly, Jaipur.','brasserie':'An evening, well spent.','village':'A taste of Rajasthan.','thali':'A little of everything.','courtyard':'Slow down. Settle in.','ember':'Bring on the flavour.','chai':'Ek chai aur?','roastery':'Good coffee, simply.','lazy':'Stay for another.','bistro':'Make yourself at home.','blockprint':'Fresh. Thoughtful. Unhurried.'}[b['layout']]
 storyIntro={
  'coffee':'The ritual is simple: a good cup, something delicious and a little room to breathe. This concept brings the menu to your table, so the moment stays yours.',
  'pizza':'Something to share, something to savour. Explore the menu, choose your extras and put together your table’s favourites in one easy place.',
  'sweets':'A treat for today. A box for someone you love. This concept makes it easy to browse sweet moments and assemble a sample order at your own pace.',
  'indian':'Some meals are made for conversation. Browse the dishes, choose your preferences and build a sample order while everyone settles in.',
  'garden':'Bright plates, gentle moments and a little everyday colour. This concept leaves more time for the food and the company.',
  'chai':'One more cup, one more conversation. Explore chai and snacks, make your choices and keep the good moments going.',
 }.get(b['menuType'],'Your favourites, a new discovery and a table full of good company. Browse, customise and build a sample order whenever you’re ready.')
 return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="{b['primary']}"><meta name="robots" content="noindex,nofollow"><meta name="description" content="An independent {name} website concept with an interactive sample menu and table ordering demo, created by Rawcoderz."><title>{name} · Jaipur dining concept</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="preload" href="assets/{font_file(b['displayFont'])}.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="styles.css"><script src="site-data.js" defer></script><script src="app.js" defer></script></head>
<body class="theme-{b['layout']}"><a class="skip" href="#main">Skip to content</a>
<div class="demo-line"><span>Independent concept · Rawcoderz</span><span>Explore the sample menu & try a demo order</span></div>
<header class="site-header"><nav class="nav wrap" aria-label="Main navigation"><a class="brand" href="#" aria-label="{name} home">{brand}</a><div class="nav-links"><a href="#menu">The menu</a><a href="#story">The feeling</a><a href="#visit">Find us</a></div><div class="nav-actions"><button class="icon-button" data-cart aria-label="Open your order">{icon('bag')}<span class="cart-count" data-cart-count>0</span></button><a class="button" href="#menu">Explore menu {icon('arrow')}</a><button class="icon-button mobile-menu" id="mobile-toggle" aria-label="Toggle navigation" aria-expanded="false" aria-controls="mobile-nav">{icon('menu')}</button></div></nav><div class="mobile-nav-panel" id="mobile-nav" hidden><a href="#menu">Menu</a><a href="#story">The feeling</a><a href="#visit">Find us</a></div></header>
<main id="main"><section class="hero" aria-labelledby="hero-title"><div class="hero-inner wrap"><div class="hero-copy"><p class="eyebrow">{E(b['kicker'])}</p><h1 id="hero-title">{b['title']}</h1><p class="hero-description">{E(b['description'])}</p><div class="hero-actions"><a class="button" href="#menu">Find your favourite {icon('arrow')}</a><a class="text-link" href="#story">Stay for the feeling {icon('arrow')}</a></div><div class="hero-meta"><span>{E(b['area'].split('/')[0].strip())} · Jaipur</span><span id="table-context">Your table. Your pace.</span></div></div><div class="hero-art"><figure class="hero-main"><img src="{hero}" alt="{heroAlt}" width="1200" height="1100" fetchpriority="high"><figcaption class="photo-note">Concept imagery · sample menu</figcaption></figure><figure class="hero-small"><img src="{small}" alt="Illustrative food and drink detail" width="480" height="480"></figure><div class="seal"><span>A little</span>{icon('spark')}<span>Jaipur joy</span></div><span class="art-number">{str(b['index']+1).zfill(2)} / Jaipur, thoughtfully served</span><span class="floating-note">{E(floating)}</span><div class="hero-decor" aria-hidden="true"></div></div></div></section>
<div class="category-ribbon" aria-hidden="true"><div class="ribbon-track">{ribbon}</div></div>
<section id="menu" class="section wrap" aria-labelledby="menu-title"><div class="section-head reveal"><div><p class="section-label">01 / Find your favourite</p><h2 id="menu-title">A menu for<br>your kind of moment.</h2></div><p>{E(b['menuIntro'])}<br>Browse, customise, and try a table or pickup order.</p></div><div class="menu-toolbar"><div class="categories" role="group" aria-label="Menu categories">{filters}</div><label class="menu-search" for="menu-search">{icon('search')}<input type="search" id="menu-search" placeholder="Find something delicious" aria-label="Search sample menu" autocomplete="off"></label></div><p class="sample-note">{icon('info')}<span>Illustrative menu, prices & imagery. This is a concept, not the venue’s live menu. <span id="menu-count">8 sample items</span>.</span></p><div class="menu-grid" id="menu-grid" aria-live="polite" aria-label="Sample menu items"></div><noscript><p>Enable JavaScript to explore the interactive sample menu and ordering demo.</p></noscript></section>
<section id="story" class="section story" aria-labelledby="story-title"><div class="wrap story-grid"><div class="story-images reveal"><img class="large" src="{story}" alt="{'Public brand dining reference' if b['slug'] in ('kanha','niros','tapri','rawat-misthan-bhandar') else 'Illustrative café and dining atmosphere'}" loading="lazy" width="900" height="1100"><img class="small" src="{small}" alt="A food and drink mood for this concept" loading="lazy" width="480" height="480"><span class="story-caption">A visual mood for the concept · not a live kitchen feed</span></div><div class="story-copy reveal"><p class="section-label">02 / More than a menu</p><h2 id="story-title">{E(b['storyTitle'])}</h2><p>{E(storyIntro)}</p><div class="story-points"><div><small>Choose with ease</small><strong>Your preferences.</strong></div><div><small>Keep the moment</small><strong>Your own pace.</strong></div></div><a class="text-link" href="#menu">Something delicious awaits {icon('arrow')}</a></div></div></section>
<section id="visit" class="section wrap visit" aria-labelledby="visit-title"><div class="visit-copy reveal"><p class="section-label">03 / A little closer</p><h2 id="visit-title">Meet you<br>in Jaipur.</h2><p>{E(b['address'])}</p><p class="form-note">Location reference for the concept. Confirm the matching outlet, hours and details before visiting.</p><a class="text-link" href="{E(b['maps'])}" target="_blank" rel="noopener noreferrer">Find on Google Maps {icon('pin')}</a></div><div class="visit-art reveal"><div><p class="section-label">Good choices. Less waiting.</p><h3>Your next favourite<br>starts here.</h3><p>Choose your dishes, add your preferences and try the ordering experience.</p><a class="button" href="#menu">Let’s find something good {icon('arrow')}</a></div></div></section></main>
<footer class="footer wrap"><div class="footer-top"><p class="footer-wordmark">{short}<span style="display:block;font-family:var(--body);font-size:9px;letter-spacing:.12em;margin-top:10px">JAIPUR · A DINING CONCEPT</span></p><div class="footer-links"><a href="#menu">The menu</a><a href="#story">The feeling</a><a href="#visit">Find us</a></div></div><div class="footer-note"><p>Independent website concept by Rawcoderz. Not affiliated with or endorsed by {name}. All menu descriptions, prices and ordering flows are illustrative. No real orders, payments or personal contact details are collected.</p><span>Made for good food & good company.</span></div></footer>
<button class="mobile-cart" data-cart aria-label="Open your order"><span>{icon('bag')}Your order · <span data-cart-count>0</span> items</span><span><span data-cart-total>₹0</span>{icon('arrow')}</span></button>
<div class="live-message" role="status" aria-live="polite"></div>
<dialog id="item-dialog" aria-labelledby="item-title" aria-describedby="item-description"><div class="dialog-inner"><div class="dialog-head"><h2 id="item-title">Make it yours</h2><button class="icon-button close" data-close aria-label="Close item options">{icon('close')}</button></div><img class="dialog-photo" id="item-photo" src="{small}" alt="Illustrative food" width="480" height="180"><p class="dialog-description" id="item-description"></p><fieldset class="options-fieldset"><legend class="field-label" id="option-label">Your preferences</legend><div class="option-choices" id="item-options"></div></fieldset><div class="dialog-total"><div class="quantity"><button data-option-minus aria-label="Decrease quantity">−</button><output id="option-quantity" aria-label="Quantity">1</output><button data-option-plus aria-label="Increase quantity">+</button></div><button class="button" data-confirm-add>Add · <span id="option-total">₹0</span> {icon('bag')}</button></div><p class="form-note">Sample options and prices. No real order will be placed.</p></div></dialog>
<dialog class="cart-dialog" id="cart-dialog" aria-labelledby="cart-title"><div class="dialog-inner"><div class="dialog-head"><h2 id="cart-title">Your little order.</h2><button class="icon-button close" data-close aria-label="Close your order">{icon('close')}</button></div><div class="cart-lines" id="cart-lines"></div><div class="cart-summary"><div class="summary-row"><span>Sample total</span><strong id="cart-subtotal">₹0</strong></div><button class="button" id="checkout-button">Try demo checkout {icon('arrow')}</button><p class="sample-note">Sample total only. No payment, tax calculation or real order.</p></div></div></dialog>
<dialog id="order-dialog" aria-labelledby="order-title"><div class="dialog-inner"><div class="dialog-head"><h2 id="order-title">At your own pace.</h2><button class="icon-button close" data-close aria-label="Close demo checkout">{icon('close')}</button></div><div id="order-content"><p class="dialog-description">Try the flow. Nothing is sent to the restaurant.</p><form id="order-form"><label class="field-label" for="service-mode">How would you enjoy it?</label><select id="service-mode"><option value="dine-in">At the table · demo</option><option value="pickup">Pick it up · demo</option></select><div id="table-field"><label class="field-label" for="table-number">Table number</label><input id="table-number" type="number" min="1" max="99" placeholder="e.g. 7" inputmode="numeric" required></div><div id="pickup-field" hidden><label class="field-label" for="pickup-time">Preferred pickup time</label><input id="pickup-time" type="time"></div><label class="field-label" for="order-note">Kitchen note (optional)</label><textarea id="order-note" maxlength="240" rows="2" placeholder="Try a note, like less spicy please"></textarea><p class="form-note">Notes stay in this page and are discarded on reset. Do not enter personal information. All dishes and prices are illustrative; dietary details are not verified.</p><div class="summary-row"><span>Sample total</span><strong id="checkout-total">₹0</strong></div><button class="button checkout-submit" type="submit">Complete demo order {icon('arrow')}</button></form></div><div class="success" id="order-success" hidden><span class="success-icon">{icon('check')}</span><h3 tabindex="-1">That felt easy.</h3><p id="demo-ticket"></p><p id="demo-ticket-total"></p><p>Demo complete. No order was sent, no table or pickup was reserved, and no payment was taken.</p><button class="button" data-close>Back to the good stuff {icon('arrow')}</button></div></div></dialog>
</body></html>'''

def build_brand(b):
 folder=OUT/b['slug'];assets=folder/'assets';assets.mkdir(parents=True,exist_ok=True)
 used={}
 def photo(key, width=1200):
  key={'curry':'paneer','pizza':'veg-pizza','burger':'coffee'}.get(key,key)
  if key not in used:used[key]=copy_photo(key,assets,width)
  return used[key]
 hero=photo(choose_hero(b))
 smallKey={'coffee':'croissant','cafe':'pizza','pizza':'pasta','chaat':'tea','garden':'bread','burger':'coffee','bhatura':'curry','indian':'bread','sweets':'tea','chai':'bread'}.get(b['menuType'],'coffee')
 if b['slug']=='kanha':smallKey='kanha-katli'
 if b['slug']=='lmb':smallKey='kachori'
 small=photo(smallKey,650)
 storyKey={'kanha':'kanha-food','niros':'niros-room','tapri':'tapri-room','rawat-misthan-bhandar':'rawat-snacks','lmb':'sweets','chokhi-dhani':'chokhi-food'}.get(b['slug'],'table')
 story=photo(storyKey,1000)
 logo=None
 if b.get('logo'):
  original=CACHE/ASSETS[b['logo']]['file'];shutil.copyfile(original,assets/'logo.png');logo='assets/logo.png'
 menu=make_menu(b)
 for item in menu:
  key=item.pop('photo')
  kind=category_type(item['category'])
  if key=='burger' or kind in ('bubble','cooler'):
   artkind='burger' if key=='burger' else kind
   write(assets/(artkind+'.svg'),menu_art(artkind,b));item['image']='assets/'+artkind+'.svg'
  elif key=='mithai':
   write(assets/'mithai.svg',food_art(b['primary'],b['accent']));item['image']='assets/mithai.svg'
  else:item['image']=photo(key,600)
 fontcss=''
 for family in (b['displayFont'],b['bodyFont']):
  key=font_file(family);shutil.copyfile(CACHE/ASSETS[key]['file'],assets/(key+'.woff2'))
  license_path=CACHE/('license-'+family.lower().replace(' ','-')+'.txt')
  if license_path.exists():shutil.copyfile(license_path,assets/license_path.name)
  assert (assets/(key+'.woff2')).read_bytes()[:4]==b'wOF2',f'Expected WOFF2: {family}'
  fontcss+=f'@font-face{{font-family:"{family}";src:url("assets/{key}.woff2") format("woff2");font-weight:400;font-style:normal;font-display:swap}}\n'
 variables=f''':root{{--primary:{b['primary']};--bg:{b['bg']};--ink:{b['ink']};--accent:{b['accent']};--on-primary:{contrast(b['primary'])};--seal-ink:{contrast(b['accent'])};--line:color-mix(in srgb,var(--ink) 20%,transparent);--muted:color-mix(in srgb,var(--ink) 76%,var(--bg));--display:"{b['displayFont']}";--body:"{b['bodyFont']}"}}\n'''
 write(folder/'styles.css',fontcss+variables+CSS)
 write(folder/'app.js',JS)
 write(folder/'site-data.js','window.BRAND = '+json.dumps({'slug':b['slug'],'name':b['name'],'categories':b['categories'],'menu':menu},ensure_ascii=False,indent=2)+';\n')
 page=render_site(b,menu,hero,small,story,logo)
 page=page.replace('class="option-choices"','class="option-grid"').replace('<form id="order-form">','<form class="order-form" id="order-form">')
 write(folder/'index.html',page)
 initial=''.join(word[0] for word in b['name'].split() if word[0].isalpha())[:2].upper()
 write(assets/'favicon.svg',f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80"><rect width="80" height="80" rx="20" fill="{b["primary"]}"/><text x="40" y="50" text-anchor="middle" font-family="Georgia,serif" font-size="30" fill="{contrast(b["primary"])}">{initial}</text></svg>')
 for old in assets.glob('*.webp'):
  if old.stem in ASSETS and old.stem not in used:old.unlink()
 write(folder/'_headers','/*\n  X-Robots-Tag: noindex, nofollow\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n')
 sources='\n'.join(f'- {key}: {ASSETS[key]["url"]}' for key in used)
 if b.get('logo'):sources+=f'\n- Logo: {ASSETS[b["logo"]]["url"]}'
 write(folder/'README.md',f'''# {b['name']} — independent website concept

Open `index.html` directly, or serve this folder with any static server. This folder is a complete standalone site; it does not depend on its parent or other brand folders.

## Cloudflare Pages

For Direct Upload, upload the contents of this folder (with `index.html` at the upload root). For Git deployment, choose no framework, use `exit 0` as the build command and this folder as the output directory. No install step, environment variables or server are required. The `_headers` file asks crawlers not to index the demo. No deployment has been performed. See [Cloudflare Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/) and [static HTML settings](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/).

## Experience

- Responsive landing page; {b['layout']} art direction.
- Local {b['displayFont']} / {b['bodyFont']} typography, local images, scroll reveals and motion preference support.
- Three menu categories, search, sample customisations, quantities, removable cart lines and browser cart persistence isolated to this brand.
- Dine-in or pickup simulation. Add `?table=7` to prefill a table number for a QR-style demo.
- No backend, payment, kitchen integration, real order, reservation, or customer contact collection. Kitchen notes are never transmitted. Cart contents remain only in the visitor's browser.

## Brand and content status

{b['branding']}

All menu items, descriptions, recipes, dietary labels, options and prices are illustrative. Photography is a visual reference rather than a claim about the exact dish. Address information is taken from the prospect register and must be confirmed. This is an independent Rawcoderz concept, not an official or endorsed website. Obtain brand approval and replace sample content before production.

## Public reference assets

{sources}

Fonts are self-hosted Latin subsets from Google Fonts; the respective open font licence files are included in `assets`. Stock photos are from the linked Unsplash image URLs. Brand logos and brand-owned images are public reference assets used only for that brand's private demo; ownership remains with the rights holders. Original food and drink illustrations, when present, were drawn for this concept.

## Updating

Edit `site-data.js` for the sample menu, `index.html` for content, and `styles.css` for styling. The source generator is `tools/jaipur/build.py` in the workspace and will overwrite generated site files when run. Set lasting changes in the generator, CSS source, JS source or `brands.json` before rebuilding.
''')
 b['previewHero']=hero
 return folder

def portfolio():
 cards=''
 for b in sorted(BRANDS,key=lambda b:(b['index']<13,b['index'])):
  title=E(b['name']);tag='Official visual references' if b.get('logo') else 'Creative brand direction'
  cards+=f'''<a class="site-card" href="{b['slug']}/index.html" data-kind="{b['group']}" data-name="{E(b['name'].lower())}" style="--card-color:{b['primary']};--card-bg:{b['bg']};--card-ink:{b['ink']}"><div class="card-visual"><img src="{b['slug']}/{b['previewHero']}" alt="{title} concept preview" loading="lazy" width="700" height="600"><span class="card-number">{str(b['index']+1).zfill(2)} / 28</span><span class="palette"><i style="background:{b['primary']}"></i><i style="background:{b['accent']}"></i><i style="background:{b['bg']}"></i></span><span class="card-theme">{E(b['layout'])}</span></div><div class="card-body"><p>{'Café' if b['group']=='cafe' else 'Restaurant & food brand'} <span>↗</span></p><h2>{title}</h2><small>{tag} · {E(b['displayFont'])}</small></div></a>'''
 firstfont=OUT/BRANDS[0]['slug']/'assets'/f'{font_file("Fraunces")}.woff2'
 galleryassets=OUT/'assets';galleryassets.mkdir(exist_ok=True)
 shutil.copyfile(firstfont,galleryassets/'fraunces.woff2')
 shutil.copyfile(CACHE/ASSETS['font-dm-sans']['file'],galleryassets/'dm-sans.woff2')
 for family in ('fraunces','dm-sans'):
  shutil.copyfile(CACHE/f'license-{family}.txt',galleryassets/f'license-{family}.txt')
 write(OUT/'index.html',f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="#193f35"><title>Jaipur, at your table · Rawcoderz concepts</title><meta name="description" content="28 independent restaurant and café website concepts for Jaipur. Explore the designs and try the sample ordering flows."><link rel="stylesheet" href="gallery.css"><script src="gallery.js" defer></script></head><body><a class="skip" href="#sites">Skip to concepts</a><header class="gallery-nav"><a href="#" class="wordmark">rawcoderz<span>JAIPUR COLLECTION / 2026</span></a><a href="WEBSITES.md">Project notes ↗</a></header><main><section class="gallery-hero"><div><p class="eyebrow">Made for the Pink City</p><h1>Jaipur,<br>at your <em>table.</em></h1><p class="hero-intro">Good food deserves a beautiful first impression. Twenty-eight independent website concepts, each with a different personality and an easier way to order.</p><a class="gallery-cta" href="#sites">Explore the collection <span>↓</span></a></div><div class="hero-mosaic" aria-hidden="true"><figure class="mosaic-one"><img src="la-fiamma/assets/pizza.webp" alt="" width="700" height="800"><figcaption>A LITTLE MORE FLAVOUR.</figcaption></figure><figure class="mosaic-two"><img src="how-about-coffee/assets/pour.webp" alt="" width="600" height="700"></figure><div class="collection-seal">28<br><span>different<br>personalities</span></div><p>Food. Feeling.<br>A fresh possibility.</p></div></section><div class="collection-line"><span>Individually styled.</span><span>Locally inspired.</span><span>Ready to explore.</span><span>Built by Rawcoderz.</span></div><section class="collection" id="sites"><div class="collection-head"><div><p class="eyebrow">The collection</p><h2>Pick a place.<br>Meet its personality.</h2></div><p>Each folder is a complete standalone website.<br>All menus and ordering flows are illustrative.</p></div><div class="gallery-toolbar"><div role="group" aria-label="Filter concepts"><button data-kind-filter="all" aria-pressed="true">All 28</button><button data-kind-filter="cafe" aria-pressed="false">Cafés</button><button data-kind-filter="resto" aria-pressed="false">Restaurants</button></div><label for="brand-search">Find a brand <input id="brand-search" type="search" placeholder="Kanha, Tapri, La Fiamma…"></label></div><p class="result-count" id="result-count" aria-live="polite">28 concepts to explore</p><div class="site-grid">{cards}</div><p class="no-results" hidden>No matching concept. Try another name or category.</p></section></main><footer class="gallery-footer"><p class="wordmark">rawcoderz</p><p>Independent demos. Brand ownership remains with the respective businesses.<br>No affiliation, endorsement or live ordering. Created for review and personalisation.</p><a href="#">Back to the top ↑</a></footer></body></html>''')
 write(OUT/'gallery.css','''@font-face{font-family:Fraunces;src:url(assets/fraunces.woff2) format('woff2');font-display:swap}@font-face{font-family:DM;src:url(assets/dm-sans.woff2) format('woff2');font-display:swap}*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:40px}body{margin:0;background:#f4f0e6;color:#193f35;font:14px/1.6 DM,sans-serif}a{color:inherit;text-decoration:none}button,input{font:inherit}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #c55a3e;outline-offset:5px}img{display:block;width:100%;height:100%;object-fit:cover}h1,h2,p,figure{margin:0}h1,h2{font-family:Fraunces,serif;font-weight:400;letter-spacing:-.055em;line-height:1}.skip{position:fixed;top:-70px;left:15px;background:#193f35;color:#fff;padding:12px;z-index:100}.skip:focus{top:15px}.gallery-nav{margin:auto;width:90%;max-width:1420px;height:110px;border-bottom:1px solid #193f3526;display:flex;align-items:center;justify-content:space-between}.wordmark{font-size:26px;font-weight:600;letter-spacing:-.07em}.wordmark span{display:block;font-size:8px;letter-spacing:.19em;font-weight:400;margin-top:3px}.gallery-nav>a:last-child{font-size:11px}.gallery-hero{max-width:1420px;width:90%;margin:auto;display:grid;grid-template-columns:1fr 1fr;gap:6%;align-items:center;padding:75px 0 100px}.eyebrow{text-transform:uppercase;font-size:9px;letter-spacing:.22em;margin-bottom:28px}.gallery-hero h1{font-size:clamp(80px,8.9vw,138px)}h1 em{color:#c05b42;font-weight:400}.hero-intro{max-width:370px;font-size:13px;margin:30px 0;color:#193f35ba}.gallery-cta{display:inline-flex;align-items:center;gap:70px;border-bottom:1px solid #193f35;padding:10px 0;font-size:12px}.gallery-cta span{font-size:24px}.hero-mosaic{height:560px;position:relative}.mosaic-one{position:absolute;inset:0 0 13% 22%;transform:rotate(5deg);background:#c05b42;padding:10px 10px 35px}.mosaic-one img{height:100%}.mosaic-one figcaption{font-size:8px;letter-spacing:.16em;color:#fff6e6;text-align:center;padding-top:10px}.mosaic-two{position:absolute;left:0;bottom:0;width:48%;height:48%;transform:rotate(-9deg);border:9px solid #f4f0e6}.collection-seal{position:absolute;left:8%;top:0;background:#e5b958;color:#193f35;width:130px;height:130px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-direction:column;font:44px/.8 Fraunces;transform:rotate(-12deg)}.collection-seal span{font:9px/1.5 DM;text-transform:uppercase;letter-spacing:.1em;margin-top:12px;text-align:center}.hero-mosaic>p{position:absolute;bottom:3%;right:2%;font:23px/1.2 Fraunces;transform:rotate(5deg)}.collection-line{background:#193f35;color:#f4f0e6;display:flex;justify-content:space-evenly;gap:20px;padding:22px 5%;font-family:Fraunces;font-size:24px;white-space:nowrap;overflow:hidden}.collection-line span::before{content:'✳';margin-right:20px;color:#e5b958}.collection{max-width:1420px;width:90%;margin:auto;padding:100px 0}.collection-head{display:flex;align-items:end;justify-content:space-between;gap:40px;margin-bottom:45px}.collection-head h2{font-size:60px}.collection-head>p{font-size:12px;color:#193f35ac}.gallery-toolbar{border-block:1px solid #193f3526;padding:18px 0;display:flex;justify-content:space-between;gap:30px;align-items:center}.gallery-toolbar button{background:none;color:inherit;border:1px solid transparent;padding:9px 17px;font-size:11px;cursor:pointer}.gallery-toolbar button[aria-pressed=true]{background:#193f35;color:#f4f0e6}.gallery-toolbar label{font-size:0}.gallery-toolbar input{background:none;border:0;border-bottom:1px solid #193f3540;font-size:12px;color:#193f35;width:220px;padding:10px 0}.result-count{font-size:10px;color:#193f35a6;margin:22px 0}.site-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:45px 28px}.site-card{display:block;border-bottom:1px solid #193f3529;padding-bottom:22px;transition:transform .3s}.site-card[hidden]{display:none}.site-card:hover{transform:translateY(-6px)}.card-visual{height:290px;position:relative;padding:25px 37px;background:var(--card-bg);overflow:hidden}.card-visual img{transform:rotate(-4deg);width:100%;height:100%;transition:transform .5s}.site-card:nth-child(3n+2) img{border-radius:48% 48% 0 0;transform:rotate(0)}.site-card:nth-child(3n) img{transform:rotate(4deg);border-radius:50%}.site-card:hover img{transform:rotate(0) scale(1.05)}.card-number{position:absolute;top:13px;left:14px;font-size:8px;color:var(--card-ink)}.card-theme{position:absolute;bottom:12px;left:14px;font-size:8px;text-transform:uppercase;letter-spacing:.12em;color:var(--card-ink)}.palette{display:flex;position:absolute;bottom:14px;right:14px}.palette i{width:18px;height:18px;border-radius:50%;border:1px solid #fff7;margin-left:-3px}.card-body{padding-top:18px}.card-body>p{font-size:8px;text-transform:uppercase;letter-spacing:.13em;display:flex;justify-content:space-between}.card-body>p span{font-size:18px}.card-body h2{font-size:30px;margin:5px 0 13px;line-height:1.1}.card-body small{font-size:9px;color:#193f35a6}.no-results{padding:70px 0;font:32px Fraunces}.gallery-footer{background:#193f35;color:#f4f0e6;padding:45px 5%;display:flex;align-items:center;justify-content:space-between;gap:30px}.gallery-footer>p:nth-child(2){font-size:10px;color:#f4f0e6a8}.gallery-footer a{font-size:11px}@media(max-width:1000px){.hero-mosaic{height:460px}.site-grid{grid-template-columns:repeat(2,1fr)}.collection-line{font-size:20px}.collection-line span:last-child{display:none}.card-visual{height:300px}}@media(max-width:650px){.gallery-nav{height:90px}.wordmark{font-size:24px}.gallery-hero{display:block;padding:45px 0 65px}.gallery-hero h1{font-size:88px}.hero-intro{font-size:12px;max-width:300px}.hero-mosaic{height:410px;margin-top:60px}.mosaic-one{inset:0 0 15% 20%}.mosaic-two{height:50%;width:49%}.collection-seal{width:100px;height:100px;font-size:36px}.collection-seal span{font-size:7px}.hero-mosaic>p{font-size:20px}.collection-line{justify-content:flex-start;font-size:20px;gap:30px}.collection{padding:65px 0}.collection-head{display:block}.collection-head h2{font-size:47px}.collection-head>p{margin-top:22px;font-size:11px}.gallery-toolbar{display:block}.gallery-toolbar button{padding:9px 12px}.gallery-toolbar input{margin-top:15px;width:100%}.site-grid{gap:32px 16px}.card-visual{height:210px;padding:26px 18px}.card-body h2{font-size:23px}.card-body small{font-size:8px}.card-body>p{font-size:7px;letter-spacing:.05em}.palette i{width:15px;height:15px}.gallery-footer{display:block;padding-block:35px}.gallery-footer>p:nth-child(2){margin:20px 0}.gallery-footer a{display:inline-block;margin-top:5px}}@media(max-width:380px){.site-grid{grid-template-columns:1fr}.card-visual{height:310px}.gallery-hero h1{font-size:77px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important}}
''')
 write(OUT/'gallery.js','''(() => {const cards=[...document.querySelectorAll('.site-card')],buttons=[...document.querySelectorAll('[data-kind-filter]')],search=document.querySelector('#brand-search');let kind='all';function filter(){const query=search.value.trim().toLowerCase();let count=0;cards.forEach(card=>{const match=(kind==='all'||card.dataset.kind===kind)&&card.dataset.name.includes(query);card.hidden=!match;if(match)count++;});document.querySelector('#result-count').textContent=`${count} concepts to explore`;document.querySelector('.no-results').hidden=!!count;}buttons.forEach(button=>button.addEventListener('click',()=>{kind=button.dataset.kindFilter;buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));filter();}));search.addEventListener('input',filter);})();\n''')
 gallery=OUT/'index.html'
 write(gallery,gallery.read_text(encoding='utf-8').replace('la-fiamma/assets/pizza.webp','la-fiamma/assets/veg-pizza.webp').replace('<title>','<link rel="icon" href="kanha/assets/favicon.svg" type="image/svg+xml"><title>'))

def documents():
 rows='\n'.join(f'| [{b["name"]}]({b["slug"]}/index.html) | `{b["slug"]}/` | {b["layout"]} | {b["primary"]} / {b["accent"]} |' for b in BRANDS)
 write(OUT/'WEBSITES.md',f'''# Jaipur website collection

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
{rows}

## Source and rebuild

The source is in `tools/jaipur/`: `brands.json`, `site.css`, `app.js`, `fetch_assets.py` and `build.py`. The output sites need no Python or Node runtime. Rebuilding requires Python with Pillow and an asset cache (populate it with `fetch_assets.py`). The generator overwrites generated site files; make lasting changes in the source first.
''')
 art='\n'.join(f'| {b["name"]} | {b["layout"]} | {b["displayFont"]} + {b["bodyFont"]} | {b["branding"]} |' for b in BRANDS)
 write(OUT/'ART-DIRECTION.md',f'''# Brand-specific art direction

Each concept has a distinct palette, type pairing, hero treatment, image framing and menu treatment. This is a design study, not an official rebrand. Public reference logo colours informed nine concepts; no official brand guideline document was supplied.

| Brand | Direction | Type | Brand status |
| --- | --- | --- | --- |
{art}

Photograph provenance is recorded in each site's README. Stock imagery is illustrative and does not depict the actual kitchens. Genuine brand-owned reference photos are identified there and confined to that brand's folder. The “feeling” section provides room for a future approved kitchen story without fabricating staff, procedures or credentials.
''')
 readme=OUT/'README.md';text=readme.read_text(encoding='utf-8')
 addition='\n## Website demos\n\n[Browse the 28 website concepts](index.html) or read the [site index and deployment notes](WEBSITES.md). Every brand has a separate standalone folder with an interactive sample ordering experience.\n'
 if '## Website demos' not in text:write(readme,text+addition)

if __name__=='__main__':
 for brand in BRANDS:build_brand(brand)
 portfolio();documents()
 print(json.dumps({'sites':len(BRANDS),'menuItems':len(BRANDS)*8,'output':str(OUT)},indent=2))
