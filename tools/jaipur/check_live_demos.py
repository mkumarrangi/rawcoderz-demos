"""Read-only check that the campaign links resolve to the matching demos."""
from pathlib import Path
import concurrent.futures, html, json, re, urllib.request
HERE=Path(__file__).resolve().parent
OUT=HERE.parents[1]/'rawcoderz/jaipur/outreach'
OUT.mkdir(exist_ok=True)
brands=json.loads((HERE/'brands.json').read_text(encoding='utf-8'))
def check(b):
 url='https://demo.rawcoderz.com/rawcoderz/jaipur/'+b['slug']+'/'
 try:
  request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(request,timeout=30) as response:
   content=response.read().decode('utf-8')
   title=html.unescape(re.search(r'<title>(.*?)</title>',content,re.S).group(1))
   return {'brand':b['name'],'slug':b['slug'],'url':url,'status':response.status,'matchesBrand':b['name'] in title,'title':title}
 except Exception as error:return {'brand':b['name'],'slug':b['slug'],'url':url,'error':str(error)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(check,brands))
(OUT/'demo-link-checks.json').write_text(json.dumps({'checkedDate':'2026-10-11','results':results},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
failures=[r for r in results if r.get('status')!=200 or not r.get('matchesBrand')]
print(json.dumps({'checked':len(results),'passed':len(results)-len(failures),'failures':failures},indent=2))
