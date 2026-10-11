const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {chromium} = require('C:/Users/mkuma/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const brands = JSON.parse(fs.readFileSync(path.join(__dirname,'brands.json'),'utf8'));
const qa = path.join(__dirname,'qa'); fs.mkdirSync(qa,{recursive:true});
const base = process.env.JAIPUR_PREVIEW_URL || 'http://127.0.0.1:8766/';
const results = [], failures = [];
const representatives = new Set(['kanha','tansukh','la-fiamma','tapri','curious-life','the-messy-door-cafe','cosmos-cafe','anokhi-cafe']);
const browserErrors=[];
async function checkLayout(page, label) {
  const result = await page.evaluate(() => ({
    overflow:document.documentElement.scrollWidth>innerWidth+1,
    missing:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.getAttribute('src')),
    fonts:document.fonts.status,
    h1:[...document.querySelectorAll('h1')].length,
    title:document.title,
    clipped:[...document.querySelectorAll('.hero h1,.eyebrow,.brand,.dish,.hero-description')].filter(el=>el.getBoundingClientRect().right>innerWidth+2||el.getBoundingClientRect().left<-2).map(el=>el.className||el.tagName)
  }));
  assert(!result.overflow,`${label}: horizontal page overflow`);
  assert.deepEqual(result.missing,[],`${label}: missing images`);
  assert.deepEqual(result.clipped,[],`${label}: content outside viewport`);
  assert.equal(result.h1,1,`${label}: one main heading`);
}
async function scrollAll(page) {
  await page.evaluate(()=>document.querySelectorAll('img').forEach(img=>img.loading='eager'));
  await page.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=650){scrollTo(0,y);await new Promise(r=>setTimeout(r,25));}scrollTo(0,0);});
  await page.waitForFunction(()=>[...document.images].every(i=>i.complete));
}
async function addFirst(page,qty=1) {
  await page.locator('[data-filter="All"]').click();
  await page.locator('[data-add]').first().click();
  await page.locator('#item-dialog').waitFor({state:'visible'});
  if(qty>1)await page.locator('[data-option-plus]').click();
  await page.locator('#item-options input').last().check();
  const price=await page.locator('#option-total').textContent();
  assert(price.includes('₹'),'rupee sample price');
  await page.locator('[data-confirm-add]').click();
  await page.locator('#item-dialog').waitFor({state:'hidden'});
}
async function openCart(page){await page.locator('.nav-actions [data-cart]').click();}
async function functional(page,brand){
  assert.equal(await page.locator('.dish').count(),8,'eight sample items');
  const first=await page.evaluate(()=>BRAND.menu[0]);
  await page.locator('[data-filter]').nth(1).click();
  assert.equal(await page.locator('.dish').count(),3,'category filter');
  await page.locator('#menu-search').fill('zzq-impossible');
  assert.equal(await page.locator('.dish').count(),0,'empty search state');
  await page.locator('[data-clear-search]').click();
  assert.equal(await page.locator('.dish').count(),8,'clear search');
  await page.locator('#menu-search').fill(first.name);
  assert((await page.locator('.dish').count())>=1,'search results');
  await page.locator('#menu-search').fill('');
  await addFirst(page,2);
  assert.equal(await page.locator('.nav-actions [data-cart-count]').textContent(),'2','cart count');
  const expected=(first.price+first.options.at(-1).extra)*2;
  assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem('rawcoderz-jaipur-cart-v1-'+BRAND.slug))[0].qty),2);
  await page.reload();await page.evaluate(()=>document.fonts.ready);
  assert.equal(await page.locator('.nav-actions [data-cart-count]').textContent(),'2','cart persists on reload');
  await openCart(page);
  const subtotal=await page.locator('#cart-subtotal').textContent();
  assert.equal(Number(subtotal.replace(/[^\d]/g,'')),expected,'correct customisation subtotal');
  await page.locator('[data-delta="1"]').click();
  assert.equal(await page.locator('.cart-line output').textContent(),'3','cart quantity increase');
  await page.locator('[data-delta="-1"]').click();
  assert.equal(await page.locator('.cart-line output').textContent(),'2','cart quantity decrease');
  await page.locator('#checkout-button').click();
  await page.locator('#table-number').fill('7');
  await page.locator('#order-note').fill('Demo note: less spicy');
  await page.locator('#order-form button[type=submit]').click();
  assert((await page.locator('#demo-ticket').textContent()).includes('Table 7'),'table ticket');
  assert(await page.locator('#order-success').isVisible(),'success visible');
  assert(!(await page.locator('#order-content').isVisible()),'form hidden on success');
  assert.equal(await page.locator('.nav-actions [data-cart-count]').textContent(),'0','cart clears after demo');
  await page.locator('#order-success [data-close]').click();
  await openCart(page);
  assert(await page.locator('.cart-empty').isVisible(),'empty cart');
  assert(await page.locator('#checkout-button').isDisabled(),'empty cart cannot checkout');
  await page.keyboard.press('Escape');
  assert(!(await page.locator('#cart-dialog').isVisible()),'Escape closes dialog');
  await addFirst(page);
  await openCart(page);await page.locator('[data-remove]').click();
  assert.equal(await page.locator('.cart-line').count(),0,'remove cart line');
  await page.keyboard.press('Escape');
}
async function testBrand(browser,brand){
  const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  const page=await context.newPage();const errors=[],bad=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('response',r=>{if(r.status()>=400)bad.push(r.url()+':'+r.status());});
  page.on('requestfailed',r=>bad.push(r.url()+':'+r.failure()?.errorText));
  try{
    await page.goto(base+brand.slug+'/index.html?table=7',{waitUntil:'networkidle'});
    await page.evaluate(()=>document.fonts.ready);await scrollAll(page);
    await checkLayout(page,brand.slug+' desktop');
    await functional(page,brand);
    await page.evaluate(()=>scrollTo(0,0));
    if(representatives.has(brand.slug))await page.screenshot({path:path.join(qa,brand.slug+'-desktop.png'),fullPage:true});
    await page.setViewportSize({width:390,height:844});
    await page.goto(base+brand.slug+'/index.html?table=7',{waitUntil:'networkidle'});
    await scrollAll(page);await checkLayout(page,brand.slug+' mobile');
    await page.locator('#mobile-toggle').click();
    assert(await page.locator('#mobile-nav').isVisible(),'mobile nav opens');
    await page.locator('#mobile-nav a').first().click();
    assert(!(await page.locator('#mobile-nav').isVisible()),'mobile nav closes on link');
    await page.evaluate(()=>scrollTo(0,0));
    await page.screenshot({path:path.join(qa,brand.slug+'-mobile.png'),fullPage:true});
    if(representatives.has(brand.slug)){
      await addFirst(page);await page.locator('.mobile-cart').click();
      await page.locator('#checkout-button').click();
      assert.equal(await page.locator('#table-number').inputValue(),'7','QR table prefill');
      await page.locator('#service-mode').selectOption('pickup');
      assert(await page.locator('#table-number').isDisabled(),'hidden table disabled');
      await page.locator('#pickup-time').fill('18:30');
      await page.locator('#order-form button[type=submit]').click();
      assert((await page.locator('#demo-ticket').textContent()).includes('Pickup at 18:30'),'pickup ticket');
      await page.locator('#order-success [data-close]').click();
    }
    await page.setViewportSize({width:320,height:740});
    await checkLayout(page,brand.slug+' narrow mobile');
    assert.deepEqual(errors,[],'no runtime errors');assert.deepEqual(bad,[],'no failed resources');
    results.push({slug:brand.slug,status:'passed',desktop:1440,mobile:[390,320],sampleItems:8});
    process.stdout.write('PASS '+brand.slug+'\n');
  }catch(e){failures.push({slug:brand.slug,error:e.message,errors,bad});process.stdout.write('FAIL '+brand.slug+': '+e.message+'\n');await page.screenshot({path:path.join(qa,brand.slug+'-failure.png'),fullPage:true}).catch(()=>{});}
  await context.close();
}
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const work=[...brands];await Promise.all(Array.from({length:3},async()=>{while(work.length)await testBrand(browser,work.shift());}));
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 try{
  await page.goto(base,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
  assert.equal(await page.locator('.site-card:visible').count(),28);
  await page.locator('[data-kind-filter=cafe]').click();assert.equal(await page.locator('.site-card:visible').count(),15);
  await page.locator('[data-kind-filter=resto]').click();assert.equal(await page.locator('.site-card:visible').count(),13);
  await page.locator('[data-kind-filter=all]').click();await page.locator('#brand-search').fill('Kanha');assert.equal(await page.locator('.site-card:visible').count(),2);
  await page.locator('#brand-search').fill('no-such-cafe');assert(await page.locator('.no-results').isVisible());await page.locator('#brand-search').fill('');
  await scrollAll(page);await checkLayout(page,'gallery desktop');await page.screenshot({path:path.join(qa,'gallery-desktop.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});await checkLayout(page,'gallery mobile');await page.screenshot({path:path.join(qa,'gallery-mobile.png'),fullPage:true});
  process.stdout.write('PASS gallery\n');
 }catch(e){failures.push({slug:'gallery',error:e.message});process.stdout.write('FAIL gallery: '+e.message+'\n');}
 // A corrupt saved cart must not prevent ordering; each brand has its own key.
 try{
  await page.goto(base+'kanha/index.html');await page.evaluate(()=>{localStorage.setItem('rawcoderz-jaipur-cart-v1-kanha','[{"id":"missing","qty":999,"choice":0}]');});await page.reload();
  assert.equal(await page.locator('.nav-actions [data-cart-count]').textContent(),'0');
  await addFirst(page);await page.goto(base+'la-fiamma/index.html');assert.equal(await page.locator('.nav-actions [data-cart-count]').textContent(),'0');
  await page.goto(base+'tapri/index.html');await page.emulateMedia({reducedMotion:'reduce'});await page.reload();
  assert.equal(await page.locator('.ribbon-track').evaluate(el=>getComputedStyle(el).animationName),'none');
  process.stdout.write('PASS storage isolation, malformed data and reduced motion\n');
 }catch(e){failures.push({slug:'shared-behaviour',error:e.message});}
 await browser.close();
 fs.writeFileSync(path.join(qa,'results.json'),JSON.stringify({passed:results.length,results,failures},null,2));
 process.stdout.write(JSON.stringify({passed:results.length,failed:failures.length})+'\n');
 process.exitCode=failures.length?1:0;
})();
