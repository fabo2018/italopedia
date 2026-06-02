/* ═══════════════════════════════════════════
   ITALOPEDIA — main.js
   Shared client interactions
═══════════════════════════════════════════ */

/* ── Newsletter subscribe ───────────────── */
function nlSubscribe(form, e) {
  e.preventDefault();
  var email = form.querySelector('[type="email"]').value.trim();
  if (!email) return;
  var btn = form.querySelector('[type="submit"]');
  btn.disabled = true;
  btn.textContent = '...';
  var msgEl = (form.closest('.newsletter-form') || form).querySelector('.nl-msg');
  function success() {
    var txt = '✓ You\'re in — check your inbox.';
    if (msgEl) { msgEl.textContent = txt; }
    else { var s = document.createElement('span'); s.style.cssText='color:var(--paper);font-size:14px;display:block;margin-top:10px'; s.textContent = txt; form.appendChild(s); }
    btn.textContent = '✓';
  }
  function fallback() {
    window.open('https://www.beehiiv.com/subscribe/83935e9a-30fd-4975-a79a-e10be8100271', '_blank');
    var txt = '→ Complete signup in the tab that just opened.';
    if (msgEl) { msgEl.textContent = txt; }
    btn.disabled = false; btn.textContent = 'Subscribe →';
  }
  fetch('https://app.beehiiv.com/subscriptions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email, publicationId: '83935e9a-30fd-4975-a79a-e10be8100271', referringSite: location.hostname })
  }).then(function(r) {
    if (r.ok || r.status === 201) { success(); } else { fallback(); }
  }).catch(fallback);
}

(function(){
  'use strict';

  // ── Mobile nav toggle ──────────────────────
  var mt = document.querySelector('.mobile-toggle');
  var nl = document.querySelector('.nav-links');
  if(mt && nl){
    mt.addEventListener('click', function(){
      nl.classList.toggle('open');
      mt.textContent = nl.classList.contains('open') ? '✕' : '☰';
    });
  }

  // ── FAQ toggles ────────────────────────────
  document.querySelectorAll('.faq-q').forEach(function(q){
    q.addEventListener('click', function(){
      var item = q.closest('.faq-item');
      if(item) item.classList.toggle('open');
    });
  });

  // ── Search overlay ─────────────────────────
  var searchOverlay = document.getElementById('searchOverlay');
  var searchInput = document.getElementById('searchInput');
  var searchResults = document.getElementById('searchResults');

  function openSearch(){
    if(!searchOverlay) return;
    searchOverlay.classList.add('open');
    setTimeout(function(){ searchInput && searchInput.focus(); }, 50);
  }
  function closeSearch(){
    if(!searchOverlay) return;
    searchOverlay.classList.remove('open');
  }
  window.openSearch = openSearch;
  window.closeSearch = closeSearch;

  document.querySelectorAll('[data-search-trigger]').forEach(function(b){
    b.addEventListener('click', openSearch);
  });
  if(searchOverlay){
    searchOverlay.addEventListener('click', function(e){
      if(e.target === searchOverlay) closeSearch();
    });
  }
  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape') closeSearch();
    if((e.metaKey || e.ctrlKey) && e.key === 'k'){
      e.preventDefault(); openSearch();
    }
  });

  // ── Search index (client-side, simple) ─────
  var INDEX = window.SEARCH_INDEX || [];
  var PREFIX = window.SITE_PREFIX || '';

  function renderResults(items){
    if(!searchResults) return;
    if(!items.length){
      searchResults.innerHTML = '<div class="search-hint" style="padding:32px 22px">No matches. Try "visa", "permesso", "flat tax", "citizenship", "Tuscany"…</div>';
      return;
    }
    searchResults.innerHTML = items.slice(0,8).map(function(it){
      return '<a class="search-result-item" href="'+PREFIX+it.url+'">'
        + '<div class="search-result-cat">'+it.cat+'</div>'
        + '<div><div class="search-result-title">'+it.title+'</div>'
        + '<div class="search-result-excerpt">'+it.excerpt+'</div></div>'
        + '</a>';
    }).join('');
  }

  if(searchInput){
    renderResults(INDEX);
    searchInput.addEventListener('input', function(){
      var q = this.value.toLowerCase().trim();
      if(!q){ renderResults(INDEX); return; }
      var hits = INDEX.filter(function(it){
        return (it.title + ' ' + it.cat + ' ' + it.excerpt + ' ' + (it.tags||'')).toLowerCase().indexOf(q) !== -1;
      });
      renderResults(hits);
    });
  }

  // ── Smooth-scroll anchors ──────────────────
  document.querySelectorAll('a[href^="#"]').forEach(function(a){
    a.addEventListener('click', function(e){
      var id = a.getAttribute('href');
      if(id.length > 1){
        var t = document.querySelector(id);
        if(t){ e.preventDefault(); t.scrollIntoView({behavior:'smooth', block:'start'}); }
      }
    });
  });

  // ── TOC active highlight (article pages) ───
  var tocLinks = document.querySelectorAll('.toc-list a[href^="#"]');
  if(tocLinks.length){
    var headings = Array.prototype.map.call(tocLinks, function(l){
      return document.querySelector(l.getAttribute('href'));
    }).filter(Boolean);
    function updateToc(){
      var y = window.scrollY + 120;
      var active = headings[0];
      headings.forEach(function(h){
        if(h.offsetTop <= y) active = h;
      });
      tocLinks.forEach(function(l){
        l.style.color = '';
        if(active && l.getAttribute('href') === '#'+active.id){
          l.style.color = 'var(--red)';
        }
      });
    }
    window.addEventListener('scroll', updateToc, {passive:true});
    updateToc();
  }

  // ── Year stamp in footer ───────────────────
  document.querySelectorAll('[data-year]').forEach(function(el){
    el.textContent = new Date().getFullYear();
  });

})();
