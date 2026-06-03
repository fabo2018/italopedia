/* ═══════════════════════════════════════════
   ITALOPEDIA — main.js
   Shared client interactions
═══════════════════════════════════════════ */

/* ── Newsletter subscribe ───────────────── */
function kitSubscribe(form, e) {
  e.preventDefault();
  var email = form.querySelector('[type="email"]').value.trim();
  if (!email) return;
  var btn = form.querySelector('[type="submit"]');
  var msgEl = form.querySelector('.kit-msg');
  var origText = btn.textContent;
  btn.disabled = true;
  btn.textContent = '...';
  var body = 'email_address=' + encodeURIComponent(email);
  fetch('https://app.kit.com/forms/7288c7a93d/subscriptions', {
    method: 'POST',
    mode: 'no-cors',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: body
  }).then(function() {
    btn.textContent = '✓ Subscribed';
    form.querySelector('[type="email"]').value = '';
    if (msgEl) msgEl.textContent = '✓ You\'re in — check your inbox.';
  }).catch(function() {
    btn.disabled = false;
    btn.textContent = origText;
    if (msgEl) msgEl.textContent = '✗ Something went wrong — try again.';
  });
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
