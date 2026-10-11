const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('C:/Users/mkuma/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const brands=JSON.parse(fs.readFileSync(path.join(__dirname,'brands.json'),'utf8'));
const failures=[];
function luminance(rgb){return rgb.slice(0,3).map(c=>{c/=255;return c<=.04045?c/12.92:((c+.055)/1.055)**2.4}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);}
function contrast(a,b){const x=luminance(a.match(/[\d.]+/g).map(Number)),y=luminance(b.match(/[\d.]+/g).map(Number));return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:320,height:740},reducedMotion:'reduce'});
 for(const b of brands){
  await page.goto('http://127.0.0.1:8766/'+b.slug+'/index.html',{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  const details=await page.evaluate(()=>({
   overflow:document.documentElement.scrollWidth>innerWidth+1,
   clippedHeading:document.querySelector('h1').scrollWidth>document.querySelector('h1').clientWidth+2,
   fonts:[...document.fonts].map(f=>f.status),
   buttons:[...document.querySelectorAll('a.button,button.button')].filter(el=>el.getBoundingClientRect().width).map(el=>({fg:getComputedStyle(el).color,bg:getComputedStyle(el).backgroundColor,text:el.textContent.trim()}))
  }));
  const issues=[];
  if(details.overflow)issues.push('page overflow');if(details.clippedHeading)issues.push('heading text clipped');
  if(details.fonts.some(f=>f!=='loaded'))issues.push('font not loaded');
  for(const button of details.buttons)if(contrast(button.fg,button.bg)<4.5)issues.push('button contrast '+button.text);
  if(issues.length)failures.push({brand:b.slug,issues});
 }
 await page.setViewportSize({width:1440,height:1000});await page.emulateMedia({reducedMotion:'no-preference'});
 await page.goto('http://127.0.0.1:8766/la-fiamma/index.html',{waitUntil:'networkidle'});
 assert.equal(await page.locator('.ribbon-track').evaluate(el=>getComputedStyle(el).animationName),'marquee');
 await page.locator('[data-add]').first().click();await page.keyboard.press('Escape');
 assert.equal(await page.evaluate(()=>document.activeElement?.hasAttribute('data-add')),true,'keyboard focus returns to menu item');
 await page.goto('file:///C:/comeback/rawcoderdemo/rawcoderz/jaipur/la-fiamma/index.html',{waitUntil:'load'});
 assert.equal(await page.locator('.dish').count(),8,'works from a standalone local file');
 await page.locator('[data-add]').first().click();await page.locator('[data-confirm-add]').click();
 assert.equal(await page.locator('.nav-actions [data-cart-count]').textContent(),'1');
 await page.goto('http://127.0.0.1:8766/',{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
 await page.screenshot({path:path.join(__dirname,'qa','gallery-cover.png'),fullPage:false});
 await browser.close();fs.writeFileSync(path.join(__dirname,'qa','final-check.json'),JSON.stringify({checked:brands.length,keyboard:true,filePreview:true,motion:true,failures},null,2));
 process.stdout.write(JSON.stringify({checked:brands.length,failures},null,2)+'\n');process.exitCode=failures.length?1:0;
})();
