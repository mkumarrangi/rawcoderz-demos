from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import json
p=Path(__file__).resolve().parent
m=json.loads((p/'cache/manifest.json').read_text())
keys=[k for k in m if not k.startswith(('font','license')) and not k.endswith('logo')]
canvas=Image.new('RGB',(1000,((len(keys)+4)//5)*180),'#f1ede2')
d=ImageDraw.Draw(canvas)
for i,key in enumerate(keys):
    with Image.open(p/'cache'/m[key]['file']) as im:
        x,y=(i%5)*200,(i//5)*180
        canvas.paste(ImageOps.fit(im.convert('RGB'),(190,150)),(x,y))
        d.text((x+5,y+155),key,fill='#222')
(p/'qa').mkdir(exist_ok=True)
canvas.save(p/'qa/assets.jpg')
