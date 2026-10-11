(() => {
  'use strict';
  const data = window.BRAND;
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const money = n => new Intl.NumberFormat('en-IN', {style:'currency',currency:'INR',maximumFractionDigits:0}).format(n);
  const esc = value => String(value).replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  const icons = {plus:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>',arrow:'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>'};
  const key = 'rawcoderz-jaipur-cart-v1-' + data.slug;
  const imageAlt = item => `Illustrative ${item.category.toLowerCase()} ${item.image.endsWith('.svg') ? 'artwork' : 'photography'}`;
  const itemById = new Map(data.menu.map(item => [item.id,item]));
  let cart = [], selected = null, optionQty = 1, category = 'All';
  let lastFocus = null, toastTimer;
  try {
    const saved = JSON.parse(localStorage.getItem(key) || '[]');
    if(Array.isArray(saved)) cart = saved.slice(0,72).filter(line => itemById.has(line.id) && Number.isInteger(line.choice) && line.choice>=0 && line.choice<itemById.get(line.id).options.length && Number.isInteger(line.qty) && line.qty>=1 && line.qty<=99).map(line=>({id:line.id,choice:line.choice,qty:line.qty}));
  } catch { cart = []; }
  const itemCount = () => cart.reduce((sum,line)=>sum+line.qty,0);
  const linePrice = line => itemById.get(line.id).price + itemById.get(line.id).options[line.choice].extra;
  const subtotal = () => cart.reduce((sum,line)=>sum+linePrice(line)*line.qty,0);
  const notify = message => {
    const box = $('.live-message'); box.textContent = message; box.classList.add('show');
    clearTimeout(toastTimer); toastTimer=setTimeout(()=>box.classList.remove('show'),2600);
  };
  function save() {
    try {localStorage.setItem(key,JSON.stringify(cart));} catch { /* The demo still works without persistent browser storage. */ }
    $$('[data-cart-count]').forEach(el=>el.textContent=itemCount());
    $$('[data-cart-total]').forEach(el=>el.textContent=money(subtotal()));
    $$('[data-cart]').forEach(el=>el.setAttribute('aria-label',`Open your order, ${itemCount()} items, ${money(subtotal())}`));
  }
  function open(dialog) { lastFocus=document.activeElement; dialog.showModal(); }
  function close(dialog) { dialog.close(); if(lastFocus?.isConnected)lastFocus.focus(); }
  function renderMenu() {
    const query=$('#menu-search').value.trim().toLowerCase();
    const matches=data.menu.filter(item=>(category==='All'||item.category===category)&&`${item.name} ${item.description}`.toLowerCase().includes(query));
    $('#menu-grid').innerHTML=matches.length?matches.map(item=>`
      <article class="dish">
        <div class="dish-image"><img src="${esc(item.image)}" alt="${esc(imageAlt(item))}" loading="lazy" width="480" height="400"><span class="dish-label">${esc(item.category)}</span></div>
        <div class="dish-details"><div class="dish-top"><h3>${esc(item.name)}</h3><span class="price">${money(item.price)}${item.unit?` <small>/ ${esc(item.unit)}</small>`:''}</span></div>
        <p class="dish-description">${esc(item.description)}</p><div class="dish-bottom"><span class="diet"><i class="veg-dot" aria-hidden="true"></i>Veg concept</span><button class="add-button" data-add="${item.id}" aria-label="Customize and add ${esc(item.name)}">Add to order ${icons.plus}</button></div></div>
      </article>`).join(''):'<p class="menu-empty">Nothing here just yet.<br><button class="text-link" data-clear-search>Show the whole menu</button></p>';
    $('#menu-count').textContent=`${matches.length} sample items`;
  }
  function optionTotal() {
    const choice=Number($('#item-options input:checked').value);
    $('#option-total').textContent=money((selected.price+selected.options[choice].extra)*optionQty);
    $('#option-quantity').textContent=optionQty;
    $('[data-option-minus]').disabled=optionQty<=1;
    $('[data-option-plus]').disabled=optionQty>=99;
  }
  function configure(id) {
    selected=itemById.get(id); if(!selected)return;
    optionQty=1; $('#item-title').textContent=selected.name;
    $('#item-photo').src=selected.image; $('#item-photo').alt=imageAlt(selected);
    $('#item-description').textContent=selected.description;
    $('#option-label').textContent=selected.optionLabel;
    $('#item-options').innerHTML=selected.options.map((option,index)=>`<label><input type="radio" name="item-option" value="${index}" ${index===0?'checked':''}>${esc(option.label)}${option.extra?` +${money(option.extra)}`:''}</label>`).join('');
    optionTotal(); open($('#item-dialog'));
  }
  function addSelected() {
    const choice=Number($('#item-options input:checked').value);
    const existing=cart.find(line=>line.id===selected.id&&line.choice===choice);
    if(existing)existing.qty=Math.min(99,existing.qty+optionQty);else cart.push({id:selected.id,choice,qty:optionQty});
    save(); close($('#item-dialog')); notify(`${selected.name} added to your demo order`);
    const trigger=$('[data-cart]');trigger.classList.remove('cart-bump');void trigger.offsetWidth;trigger.classList.add('cart-bump');
  }
  function renderCart(focusKey) {
    const box=$('#cart-lines');
    box.innerHTML=cart.length?cart.map((line,index)=>{
      const item=itemById.get(line.id), option=item.options[line.choice];
      return `<article class="cart-line"><img src="${esc(item.image)}" alt="" width="60" height="65"><div><h3>${esc(item.name)}</h3><p>${esc(option.label)}</p><div class="quantity"><button data-line="${index}" data-delta="-1" aria-label="Decrease ${esc(item.name)} quantity" ${line.qty<=1?'disabled':''}>−</button><output aria-label="Quantity">${line.qty}</output><button data-line="${index}" data-delta="1" aria-label="Increase ${esc(item.name)} quantity" ${line.qty>=99?'disabled':''}>+</button></div><button class="remove" data-remove="${index}" aria-label="Remove ${esc(item.name)}">Remove</button></div><span class="cart-line-price">${money(linePrice(line)*line.qty)}</span></article>`;
    }).join(''):`<div class="cart-empty"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 7h12l2 14H4L6 7Zm3 0V5a3 3 0 0 1 6 0v2"/></svg><h3>A little room for joy.</h3><p>Your order is empty. Find something you love on the menu.</p><button class="button" data-close>Explore the menu ${icons.arrow}</button></div>`;
    $('#cart-subtotal').textContent=money(subtotal());
    $('#checkout-button').disabled=!cart.length;
    if(focusKey)$(focusKey,box)?.focus();
  }
  const tableParam=Number(new URLSearchParams(location.search).get('table'));
  if(Number.isInteger(tableParam)&&tableParam>=1&&tableParam<=99){
    $('#table-number').value=tableParam;$('#table-context').textContent=`Table ${tableParam} · demo ordering`;
  }
  function setService() {
    const dineIn=$('#service-mode').value==='dine-in';
    $('#table-field').hidden=!dineIn;$('#pickup-field').hidden=dineIn;
    $('#table-number').required=dineIn;$('#table-number').disabled=!dineIn;
    $('#pickup-time').required=!dineIn;$('#pickup-time').disabled=dineIn;
  }
  function checkout() {
    if(!cart.length)return;
    close($('#cart-dialog'));$('#order-content').hidden=false;$('#order-success').hidden=true;
    $('#order-form').reset();
    if(Number.isInteger(tableParam)&&tableParam>=1&&tableParam<=99)$('#table-number').value=tableParam;
    $('#checkout-total').textContent=money(subtotal());setService();open($('#order-dialog'));
  }
  document.addEventListener('click',event=>{
    const button=event.target.closest('button'); if(!button)return;
    if(button.hasAttribute('data-add'))configure(button.dataset.add);
    if(button.hasAttribute('data-cart')){renderCart();open($('#cart-dialog'));}
    if(button.hasAttribute('data-close'))close(button.closest('dialog'));
    if(button.hasAttribute('data-filter')){
      category=button.dataset.filter;$$('[data-filter]').forEach(el=>el.setAttribute('aria-pressed',String(el===button)));renderMenu();
    }
    if(button.hasAttribute('data-clear-search')){$('#menu-search').value='';category='All';$$('[data-filter]').forEach(el=>el.setAttribute('aria-pressed',String(el.dataset.filter==='All')));renderMenu();}
    if(button.hasAttribute('data-option-minus')){optionQty=Math.max(1,optionQty-1);optionTotal();}
    if(button.hasAttribute('data-option-plus')){optionQty=Math.min(99,optionQty+1);optionTotal();}
    if(button.hasAttribute('data-confirm-add'))addSelected();
    if(button.hasAttribute('data-delta')){
      const index=Number(button.dataset.line);if(!cart[index])return;
      cart[index].qty=Math.max(1,Math.min(99,cart[index].qty+Number(button.dataset.delta)));save();renderCart(`[data-line="${index}"][data-delta="${button.dataset.delta}"]`);
    }
    if(button.hasAttribute('data-remove')){cart.splice(Number(button.dataset.remove),1);save();renderCart();$('#cart-dialog .close').focus();}
    if(button.id==='checkout-button')checkout();
    if(button.id==='mobile-toggle'){
      const panel=$('#mobile-nav');const expanded=button.getAttribute('aria-expanded')==='true';panel.hidden=expanded;button.setAttribute('aria-expanded',String(!expanded));
    }
  });
  $('#item-options').addEventListener('change',optionTotal);
  $('#menu-search').addEventListener('input',renderMenu);
  $('#service-mode').addEventListener('change',setService);
  $$('#mobile-nav a').forEach(link=>link.addEventListener('click',()=>{$('#mobile-nav').hidden=true;$('#mobile-toggle').setAttribute('aria-expanded','false');}));
  $('#order-form').addEventListener('submit',event=>{
    event.preventDefault();if(!cart.length)return;
    const mode=$('#service-mode').value==='dine-in'?`Table ${$('#table-number').value}`:`Pickup at ${$('#pickup-time').value}`;
    $('#demo-ticket').textContent=`DEMO ${Math.random().toString(36).slice(2,7).toUpperCase()} · ${mode}`;
    $('#demo-ticket-total').textContent=`${itemCount()} items · sample total ${money(subtotal())}`;
    $('#order-content').hidden=true;$('#order-success').hidden=false;cart=[];save();$('#order-success h3').focus();
  });
  $$('dialog').forEach(dialog=>{
    dialog.addEventListener('click',event=>{if(event.target===dialog){const rect=dialog.getBoundingClientRect();if(event.clientX<rect.left||event.clientX>rect.right||event.clientY<rect.top||event.clientY>rect.bottom)close(dialog);}});
  });
  if(!matchMedia('(prefers-reduced-motion: reduce)').matches&&'IntersectionObserver' in window){
    document.body.classList.add('has-motion');
    const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('visible');observer.unobserve(entry.target);}}),{threshold:.08});
    $$('.reveal').forEach(el=>observer.observe(el));
  }
  renderMenu();save();setService();
})();
