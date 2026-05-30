#!/usr/bin/env python3
"""
GDPR implementation for italopedia.com:
  1. Rewrite privacy/index.html with full GDPR privacy policy
  2. Rewrite cookies/index.html with full GDPR cookie policy
  3. Create /cookie-policy/ redirect → /cookies/
  4. Create /privacy-policy/ redirect → /privacy/
  5. Inject cookie consent banner (HTML/CSS/JS) into every page
  6. Remove inline AdSense from <head> (loaded by consent JS)
  7. Update every footer: Privacy Policy · Cookie Policy · Cookie Settings
  8. Commit message reminder at end
"""
import os, re, glob

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Helper: depth-aware prefix ────────────────────────────────────────────
def get_prefix(filepath):
    """Return relative URL prefix (e.g. '../../') for a given HTML file."""
    rel = os.path.relpath(filepath, BASE)
    parts = rel.replace('\\', '/').split('/')
    depth = len(parts) - 1          # subtract the filename
    if depth == 0:
        return './'
    return '../' * depth

# ── 1. PAGE SHELL helper ──────────────────────────────────────────────────
def page_shell(title, desc, canonical, eyebrow, h1, hero_desc, content_html, prefix):
    """Return a complete static-page HTML document."""
    adsense_pub = 'ca-pub-5146830468822913'
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{title} — Italopedia</title>
<meta name="description" content="{desc}"/>
<meta name="robots" content="noindex"/>
<meta name="theme-color" content="#1a1610"/>
<link rel="canonical" href="https://italopedia.com/{canonical}/"/>
<meta property="og:type" content="website"/>
<meta property="og:title" content="{title} — Italopedia"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:url" content="https://italopedia.com/{canonical}/"/>
<meta property="og:site_name" content="Italopedia"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&family=Syne:wght@400;500;600;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="{prefix}assets/css/main.css"/>
<link rel="icon" type="image/svg+xml" href="{prefix}favicon.svg"/>
</head>
<body>
<nav class="topnav"><div class="nav-inner">
  <a href="{prefix}" class="nav-logo">Italo<span>pedia</span><span class="tld">.com</span></a>
  <div class="nav-links">
    <a href="{prefix}visas/" class="nav-link">Visas</a>
    <a href="{prefix}residency/" class="nav-link">Residency</a>
    <a href="{prefix}taxes/" class="nav-link">Taxes</a>
    <a href="{prefix}healthcare/" class="nav-link">Healthcare</a>
    <a href="{prefix}property/" class="nav-link">Property</a>
    <a href="{prefix}citizenship/" class="nav-link">Citizenship</a>
    <a href="{prefix}regions/" class="nav-link">Regions</a>
    <a href="{prefix}cost-of-living/" class="nav-link">Cost of Living</a>
  </div>
  <div class="nav-right">
    <button class="nav-icon-btn" data-search-trigger>⌕</button>
    <a href="{prefix}newsletter/" class="nav-cta">Free Guide ↓</a>
    <button class="mobile-toggle">☰</button>
  </div>
</div></nav>
<section class="static-hero"><div class="static-hero-inner">
  <div class="breadcrumb dark"><a href="{prefix}">Home</a><span class="sep">›</span><span class="current">{h1}</span></div>
  <div class="static-eyebrow">{eyebrow}</div>
  <h1>{h1}</h1>
  <p class="static-hero-desc">{hero_desc}</p>
</div></section>
<div class="static-body-text">{content_html}</div>
{footer_html(prefix)}
<div class="search-overlay" id="searchOverlay"><div class="search-box">
  <div class="search-input-wrap"><span class="search-input-icon">⌕</span>
    <input class="search-input" type="text" id="searchInput" placeholder="Search 62 guides…" autocomplete="off"/>
    <button class="search-close" onclick="closeSearch()">✕</button></div>
  <div class="search-results" id="searchResults"></div>
  <div class="search-hint">⌘ K to open · ESC to close · ↵ to visit</div>
</div></div>
<script>window.SITE_PREFIX="{prefix}";</script>
<script src="{prefix}assets/js/search-index.js"></script>
<script src="{prefix}assets/js/main.js"></script>
{cookie_banner_html(prefix)}
</body>
</html>'''


def footer_html(prefix):
    return f'''<footer class="footer"><div class="footer-inner">
  <div class="footer-top">
    <div class="footer-brand-col">
      <a href="{prefix}" class="footer-logo">Italo<span>pedia</span></a>
      <p class="footer-brand-desc">The complete English-language reference for Americans moving to and living in Italy. Written from Torino, verified against official Italian sources.</p>
      <span class="footer-stamp">📍 Torino, Italy</span>
    </div>
    <div><div class="footer-col-title">Categories</div><ul class="footer-links">
      <li><a href="{prefix}visas/">Visas</a></li><li><a href="{prefix}residency/">Residency</a></li>
      <li><a href="{prefix}taxes/">Taxes</a></li><li><a href="{prefix}healthcare/">Healthcare</a></li>
      <li><a href="{prefix}property/">Property</a></li><li><a href="{prefix}citizenship/">Citizenship</a></li>
      <li><a href="{prefix}regions/">Regions</a></li><li><a href="{prefix}cost-of-living/">Cost of Living</a></li>
    </ul></div>
    <div><div class="footer-col-title">Resources</div><ul class="footer-links">
      <li><a href="{prefix}resources/">Free resources</a></li><li><a href="{prefix}shop/">Shop guides</a></li>
      <li><a href="{prefix}consult/">Book a 1:1 consult</a></li><li><a href="{prefix}newsletter/">Newsletter</a></li>
      <li><a href="{prefix}checklist/">Free checklist</a></li><li><a href="{prefix}about/">About Fabrizio</a></li>
      <li><a href="{prefix}contact/">Contact</a></li>
    </ul></div>
    <div><div class="footer-col-title">Popular guides</div><ul class="footer-links">
      <li><a href="{prefix}visas/elective-residence-visa/">Elective Residence Visa</a></li>
      <li><a href="{prefix}taxes/flat-tax-regime/">Italian Flat Tax</a></li>
      <li><a href="{prefix}citizenship/jure-sanguinis/">Citizenship by Descent</a></li>
      <li><a href="{prefix}residency/permesso-di-soggiorno/">Permesso di Soggiorno</a></li>
      <li><a href="{prefix}cost-of-living/">Cost of Living</a></li>
    </ul></div>
  </div>
  <div class="footer-bottom">
    <div class="footer-copy">© <span data-year>2025</span> Italopedia · All rights reserved · Made with espresso in Torino</div>
    <div class="footer-legal">
      <a href="{prefix}privacy/">Privacy Policy</a>
      <a href="{prefix}terms/">Terms</a>
      <a href="{prefix}cookies/">Cookie Policy</a>
      <a href="{prefix}affiliate-disclosure/">Affiliate Disclosure</a>
      <a href="{prefix}disclaimer/">Disclaimer</a>
      <button class="cc-footer-btn" onclick="italopediaConsent.openModal()">Cookie Settings</button>
    </div>
  </div>
</div></footer>'''


# ── 2. COOKIE CONSENT BANNER ──────────────────────────────────────────────
def cookie_banner_html(prefix):
    return f'''<!-- COOKIE CONSENT -->
<style>
#cc-banner{{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid var(--color-border,#e8e0d0);box-shadow:0 -4px 20px rgba(0,0,0,.08);z-index:9999;padding:1.25rem 1.5rem;display:none}}
#cc-banner.cc-on{{display:block}}
.cc-inner{{max-width:1100px;margin:0 auto;display:flex;flex-wrap:wrap;gap:.75rem 1.5rem;align-items:center}}
.cc-text{{flex:1 1 280px;display:flex;align-items:flex-start;gap:.75rem}}
.cc-icon{{font-size:1.5rem;flex-shrink:0;margin-top:.1rem}}
.cc-text strong{{display:block;margin-bottom:.2rem;font-family:var(--font-heading,"Syne"),sans-serif;font-size:.95rem}}
.cc-text p{{margin:0;font-size:.82rem;color:var(--color-muted,#666);line-height:1.5}}
.cc-actions{{display:flex;gap:.5rem;flex-shrink:0;flex-wrap:wrap}}
.cc-links{{width:100%;font-size:.78rem;color:var(--color-muted,#999)}}
.cc-links a{{color:inherit;text-decoration:underline}}
.cc-btn{{padding:.5rem 1.1rem;border-radius:6px;font-size:.82rem;font-weight:600;cursor:pointer;border:2px solid var(--color-primary,#2d6a4f);font-family:inherit;transition:background .15s,color .15s}}
.cc-btn-outline{{background:transparent;color:var(--color-primary,#2d6a4f)}}
.cc-btn-outline:hover{{background:var(--color-primary,#2d6a4f);color:#fff}}
.cc-btn-primary{{background:var(--color-primary,#2d6a4f);color:#fff}}
.cc-btn-primary:hover{{opacity:.88}}
#cc-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:9999}}
#cc-overlay.cc-on{{display:block}}
#cc-modal{{display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:min(480px,94vw);background:#fff;border-radius:12px;box-shadow:0 20px 60px rgba(0,0,0,.22);z-index:10000;overflow:hidden}}
#cc-modal.cc-on{{display:block}}
.cc-modal-head{{display:flex;justify-content:space-between;align-items:center;padding:1.1rem 1.4rem;border-bottom:1px solid var(--color-border,#e8e0d0)}}
.cc-modal-head h3{{margin:0;font-size:1rem;font-family:var(--font-heading,"Syne"),sans-serif}}
.cc-close{{background:none;border:none;font-size:1.3rem;cursor:pointer;color:var(--color-muted,#888);line-height:1;padding:.2rem .5rem;font-family:inherit}}
.cc-modal-body{{padding:.25rem 1.4rem}}
.cc-row{{display:flex;align-items:center;justify-content:space-between;padding:.85rem 0;border-bottom:1px solid var(--color-border,#f0ebe0)}}
.cc-row:last-child{{border-bottom:none}}
.cc-row-info strong{{display:block;font-size:.88rem;margin-bottom:.12rem}}
.cc-row-info span{{font-size:.78rem;color:var(--color-muted,#888)}}
.cc-always{{font-size:.78rem;color:var(--color-primary,#2d6a4f);font-weight:600}}
.cc-toggle{{position:relative;display:inline-block;width:42px;height:23px;flex-shrink:0}}
.cc-toggle input{{opacity:0;width:0;height:0}}
.cc-slider{{position:absolute;cursor:pointer;inset:0;background:#ccc;border-radius:23px;transition:.2s}}
.cc-slider:before{{position:absolute;content:"";height:17px;width:17px;left:3px;bottom:3px;background:#fff;border-radius:50%;transition:.2s}}
.cc-toggle input:checked+.cc-slider{{background:var(--color-primary,#2d6a4f)}}
.cc-toggle input:checked+.cc-slider:before{{transform:translateX(19px)}}
.cc-modal-foot{{padding:1.1rem 1.4rem;border-top:1px solid var(--color-border,#e8e0d0)}}
.cc-btn-full{{width:100%;display:block;text-align:center}}
.cc-footer-btn{{background:none;border:none;cursor:pointer;color:inherit;font-size:inherit;padding:0;text-decoration:underline;font-family:inherit}}
@media(max-width:600px){{.cc-inner{{flex-direction:column}}.cc-actions{{width:100%;justify-content:stretch}}.cc-actions .cc-btn{{flex:1}}}}
</style>

<div id="cc-banner" role="dialog" aria-label="Cookie consent">
  <div class="cc-inner">
    <div class="cc-text">
      <span class="cc-icon">🍪</span>
      <div>
        <strong>We use cookies</strong>
        <p>We use cookies to analyze traffic, personalize ads, and improve your experience. You can accept all, reject non-essential, or customize your preferences.</p>
      </div>
    </div>
    <div class="cc-actions">
      <button class="cc-btn cc-btn-outline" id="cc-customize-btn">Customize</button>
      <button class="cc-btn cc-btn-outline" id="cc-reject-btn">Reject All</button>
      <button class="cc-btn cc-btn-primary" id="cc-accept-btn">Accept All</button>
    </div>
    <div class="cc-links">
      <a href="{prefix}privacy/">Privacy Policy</a> · <a href="{prefix}cookies/">Cookie Policy</a>
    </div>
  </div>
</div>

<div id="cc-overlay"></div>
<div id="cc-modal" role="dialog" aria-modal="true" aria-label="Cookie preferences">
  <div class="cc-modal-head">
    <h3>Cookie Preferences</h3>
    <button class="cc-close" id="cc-close-btn" aria-label="Close">✕</button>
  </div>
  <div class="cc-modal-body">
    <div class="cc-row">
      <div class="cc-row-info"><strong>Strictly Necessary</strong><span>Essential for the site to function</span></div>
      <span class="cc-always">Always active</span>
    </div>
    <div class="cc-row">
      <div class="cc-row-info"><strong>Analytics</strong><span>Help us understand site usage</span></div>
      <label class="cc-toggle"><input type="checkbox" id="cc-t-analytics"><span class="cc-slider"></span></label>
    </div>
    <div class="cc-row">
      <div class="cc-row-info"><strong>Advertising</strong><span>Personalized ads via Google</span></div>
      <label class="cc-toggle"><input type="checkbox" id="cc-t-advertising"><span class="cc-slider"></span></label>
    </div>
    <div class="cc-row">
      <div class="cc-row-info"><strong>Functional</strong><span>Enhanced features &amp; preferences</span></div>
      <label class="cc-toggle"><input type="checkbox" id="cc-t-functional"><span class="cc-slider"></span></label>
    </div>
  </div>
  <div class="cc-modal-foot">
    <button class="cc-btn cc-btn-primary cc-btn-full" id="cc-save-btn">Save My Preferences</button>
  </div>
</div>

<script>
(function(){{
'use strict';
var CNAME='italopedia_consent',DAYS=365,PUB='ca-pub-5146830468822913',GA4='G-XXXXXXXXXX';
function gc(){{var m=document.cookie.match(new RegExp('(?:^|;\\s*)'+CNAME+'=([^;]*)'));try{{return m?JSON.parse(decodeURIComponent(m[1])):null}}catch(e){{return null}}}}
function sc(v){{var d=new Date();d.setTime(d.getTime()+DAYS*864e5);document.cookie=CNAME+'='+encodeURIComponent(JSON.stringify(v))+';expires='+d.toUTCString()+';path=/;SameSite=Lax'}}
function addScript(src,attrs){{var s=document.createElement('script');s.async=true;s.src=src;if(attrs)Object.keys(attrs).forEach(function(k){{s[k]=attrs[k]}});document.head.appendChild(s)}}
function loadGA4(){{if(window._ga4l)return;window._ga4l=1;addScript('https://www.googletagmanager.com/gtag/js?id='+GA4);window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}window.gtag=gtag;gtag('js',new Date());gtag('config',GA4,{{anonymize_ip:true}})}}
function loadAds(pers){{if(window._adsl)return;window._adsl=1;window.adsbygoogle=window.adsbygoogle||[];if(!pers)window.adsbygoogle.requestNonPersonalizedAds=1;addScript('https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client='+PUB,{{crossOrigin:'anonymous'}})}}
function apply(c){{if(c.analytics)loadGA4();loadAds(c.advertising)}}
function el(id){{return document.getElementById(id)}}
function show(id){{var e=el(id);if(e)e.classList.add('cc-on')}}
function hide(id){{var e=el(id);if(e)e.classList.remove('cc-on')}}
function openModal(){{
  var c=gc();
  var a=el('cc-t-analytics'),ad=el('cc-t-advertising'),f=el('cc-t-functional');
  if(c){{if(a)a.checked=!!c.analytics;if(ad)ad.checked=!!c.advertising;if(f)f.checked=!!c.functional}}
  show('cc-overlay');show('cc-modal');
}}
function closeModal(){{hide('cc-overlay');hide('cc-modal')}}
window.italopediaConsent={{openModal:openModal}};
document.addEventListener('DOMContentLoaded',function(){{
  var c=gc();
  if(!c){{show('cc-banner');loadAds(false)}}
  else{{apply(c)}}
  var ab=el('cc-accept-btn');if(ab)ab.addEventListener('click',function(){{var c={{necessary:true,analytics:true,advertising:true,functional:true,ts:Date.now()}};sc(c);hide('cc-banner');closeModal();apply(c)}});
  var rb=el('cc-reject-btn');if(rb)rb.addEventListener('click',function(){{var c={{necessary:true,analytics:false,advertising:false,functional:false,ts:Date.now()}};sc(c);hide('cc-banner');closeModal();apply(c)}});
  var cb=el('cc-customize-btn');if(cb)cb.addEventListener('click',openModal);
  var sb=el('cc-save-btn');if(sb)sb.addEventListener('click',function(){{
    var a=el('cc-t-analytics'),ad=el('cc-t-advertising'),f=el('cc-t-functional');
    var c={{necessary:true,analytics:a?a.checked:false,advertising:ad?ad.checked:false,functional:f?f.checked:false,ts:Date.now()}};
    sc(c);hide('cc-banner');closeModal();apply(c);
  }});
  var xb=el('cc-close-btn');if(xb)xb.addEventListener('click',closeModal);
  var ov=el('cc-overlay');if(ov)ov.addEventListener('click',closeModal);
}});
}})();
</script>'''


# ── 3. PRIVACY POLICY CONTENT ─────────────────────────────────────────────
PRIVACY_CONTENT = '''<p><strong>Last updated: May 30, 2026</strong></p>

<h2>1. Data Controller</h2>
<p>The data controller for Italopedia.com is:<br/>
<strong>Fabrizio Boggio</strong> · Turin, Italy<br/>
Email: <a href="mailto:info@italopedia.com">info@italopedia.com</a> · Website: <a href="https://www.italopedia.com">italopedia.com</a></p>

<h2>2. Introduction</h2>
<p>This Privacy Policy explains how Italopedia.com collects, uses, and protects your personal data. We comply with:</p>
<ul>
  <li><strong>EU General Data Protection Regulation (GDPR)</strong> — Regulation (EU) 2016/679</li>
  <li><strong>Italian Privacy Code</strong> — D.Lgs. 196/2003 as amended by D.Lgs. 101/2018</li>
  <li><strong>ePrivacy Directive</strong> — Directive 2002/58/EC</li>
</ul>

<h2>3. Data We Collect</h2>

<h3>3.1 Data You Provide Directly</h3>
<p><strong>Newsletter (Beehiiv):</strong> Email address, name (optional), subscription date.<br/>
<strong>Contact / email:</strong> Your email, name (if provided), message content.<br/>
<strong>Consultation booking (Calendly + Stripe):</strong> Name, email, payment information (processed by Stripe — we do not store card details), booking details.<br/>
<strong>Digital products (Gumroad):</strong> Name, email, payment (processed by Gumroad).</p>

<h3>3.2 Data Collected Automatically</h3>
<p><strong>Server logs:</strong> IP address (anonymized), browser type, pages visited, referring URL, date/time.<br/>
<strong>Analytics (Google Analytics 4 — with consent):</strong> Pages visited, approximate location, device type, session duration.<br/>
<strong>Advertising (Google AdSense — with consent):</strong> Ad interactions, interest-based profiling for ad targeting.</p>

<h2>4. Legal Basis for Processing (GDPR Article 6)</h2>
<table>
  <thead><tr><th>Processing Activity</th><th>Legal Basis</th></tr></thead>
  <tbody>
    <tr><td>Newsletter subscription</td><td>Consent (Art. 6(1)(a))</td></tr>
    <tr><td>Contact form responses</td><td>Legitimate interests (Art. 6(1)(f))</td></tr>
    <tr><td>Consultation booking</td><td>Contract performance (Art. 6(1)(b))</td></tr>
    <tr><td>Digital product purchase</td><td>Contract performance (Art. 6(1)(b))</td></tr>
    <tr><td>Analytics (with consent)</td><td>Consent (Art. 6(1)(a))</td></tr>
    <tr><td>Advertising cookies (with consent)</td><td>Consent (Art. 6(1)(a))</td></tr>
    <tr><td>Security and fraud prevention</td><td>Legitimate interests (Art. 6(1)(f))</td></tr>
  </tbody>
</table>

<h2>5. How We Use Your Data</h2>
<p>We use your personal data to: deliver the newsletter; respond to inquiries; process consultation bookings and digital product purchases; improve our website; display relevant advertising (with consent); comply with legal obligations; prevent fraud.</p>
<p>We do <strong>not</strong> sell your personal data, use it for automated legal decision-making, or transfer it outside the EEA without appropriate safeguards (see Section 7).</p>

<h2>6. Cookies</h2>
<p>We use cookies and similar technologies. For full details, see our <a href="../cookies/">Cookie Policy</a>.</p>
<ul>
  <li><strong>Strictly necessary:</strong> Required for site function. No consent required.</li>
  <li><strong>Analytics cookies:</strong> Measure website traffic. Require consent.</li>
  <li><strong>Advertising cookies:</strong> Used by Google AdSense. Require consent.</li>
  <li><strong>Functional cookies:</strong> Remember preferences. Require consent.</li>
</ul>
<p>Manage preferences at any time via the <button class="cc-footer-btn" onclick="italopediaConsent.openModal()">Cookie Settings</button> panel or by emailing info@italopedia.com.</p>

<h2>7. Data Sharing and Third Parties</h2>
<table>
  <thead><tr><th>Service</th><th>Purpose</th><th>Privacy Policy</th></tr></thead>
  <tbody>
    <tr><td><strong>Google Analytics</strong></td><td>Website analytics</td><td><a href="https://policies.google.com/privacy" target="_blank" rel="noopener">policies.google.com/privacy</a></td></tr>
    <tr><td><strong>Google AdSense</strong></td><td>Advertising</td><td><a href="https://policies.google.com/privacy" target="_blank" rel="noopener">policies.google.com/privacy</a></td></tr>
    <tr><td><strong>Beehiiv</strong></td><td>Newsletter delivery</td><td><a href="https://www.beehiiv.com/privacy" target="_blank" rel="noopener">beehiiv.com/privacy</a></td></tr>
    <tr><td><strong>Stripe</strong></td><td>Payment processing</td><td><a href="https://stripe.com/privacy" target="_blank" rel="noopener">stripe.com/privacy</a></td></tr>
    <tr><td><strong>Gumroad</strong></td><td>Digital product sales</td><td><a href="https://gumroad.com/privacy" target="_blank" rel="noopener">gumroad.com/privacy</a></td></tr>
    <tr><td><strong>Calendly</strong></td><td>Booking management</td><td><a href="https://calendly.com/privacy" target="_blank" rel="noopener">calendly.com/privacy</a></td></tr>
    <tr><td><strong>Cloudflare</strong></td><td>CDN and hosting</td><td><a href="https://www.cloudflare.com/privacypolicy/" target="_blank" rel="noopener">cloudflare.com/privacypolicy</a></td></tr>
  </tbody>
</table>
<p>Data transfers to the U.S. are covered by Standard Contractual Clauses (SCCs) and the EU-U.S. Data Privacy Framework where applicable.</p>

<h2>8. Data Retention</h2>
<table>
  <thead><tr><th>Data Type</th><th>Retention Period</th></tr></thead>
  <tbody>
    <tr><td>Newsletter subscriber data</td><td>Until unsubscribe + 30 days</td></tr>
    <tr><td>Contact/inquiry emails</td><td>2 years from last contact</td></tr>
    <tr><td>Consultation booking records</td><td>5 years (Italian accounting obligations)</td></tr>
    <tr><td>Purchase records</td><td>10 years (D.Lgs. 127/1991)</td></tr>
    <tr><td>Analytics data</td><td>14 months (Google Analytics default)</td></tr>
    <tr><td>Server access logs</td><td>12 months</td></tr>
  </tbody>
</table>

<h2>9. Your Rights Under GDPR</h2>
<p>You have the right to: <strong>access</strong> your data (Art. 15); <strong>rectify</strong> inaccurate data (Art. 16); <strong>erase</strong> your data (Art. 17); <strong>restrict</strong> processing (Art. 18); <strong>data portability</strong> (Art. 20); <strong>object</strong> to processing based on legitimate interests (Art. 21); <strong>withdraw consent</strong> at any time (Art. 7(3)); and not be subject to automated decision-making (Art. 22).</p>
<p>To exercise any right: Email <a href="mailto:info@italopedia.com">info@italopedia.com</a> — subject line "GDPR Request — [Your Right]". We respond within <strong>30 days</strong>. We may verify your identity before processing requests.</p>

<h2>10. Right to Lodge a Complaint</h2>
<p>You may lodge a complaint with the Italian data protection authority:<br/>
<strong>Garante per la Protezione dei Dati Personali</strong><br/>
Piazza Venezia 11, 00187 Roma · <a href="https://www.garanteprivacy.it" target="_blank" rel="noopener">garanteprivacy.it</a> · garante@gpdp.it</p>

<h2>11. Children's Privacy</h2>
<p>Our website is not directed at children under 16. We do not knowingly collect data from children under 16. Contact us immediately at info@italopedia.com if you believe we have done so.</p>

<h2>12. Security</h2>
<p>We use HTTPS encryption, access controls, and regular security reviews. We will notify you and relevant authorities promptly in the event of a data breach affecting your rights and freedoms.</p>

<h2>13. Affiliate Disclosure</h2>
<p>Some links are affiliate links — if you click and purchase, we may earn a commission at no cost to you. Affiliate relationships are disclosed with "affiliate link" labels. Tracking uses cookies (see Cookie Policy).</p>

<h2>14. Changes to This Policy</h2>
<p>We update the "Last updated" date at the top of this page when this policy changes. We will notify newsletter subscribers of material changes and request fresh consent where required by law.</p>

<h2>15. Contact Us</h2>
<p><strong>Fabrizio Boggio</strong> · <a href="mailto:info@italopedia.com">info@italopedia.com</a> · Turin, Italy<br/>
Response time: within 5 business days.</p>'''


# ── 4. COOKIE POLICY CONTENT ──────────────────────────────────────────────
COOKIE_CONTENT = '''<p><strong>Last updated: May 30, 2026</strong><br/>
<strong>Data Controller:</strong> Fabrizio Boggio — <a href="mailto:info@italopedia.com">info@italopedia.com</a> — Turin, Italy</p>

<h2>1. What Are Cookies?</h2>
<p>Cookies are small text files stored on your device when you visit a website. They allow the site to recognize your device on return visits. We also use related technologies including local/session storage, pixel tags, and web beacons — referred to collectively as "cookies" in this policy.</p>
<p><strong>Legal basis:</strong> EU ePrivacy Directive (2002/58/EC) and GDPR (Regulation 2016/679), as implemented in Italy by D.Lgs. 196/2003 and Provvedimento del Garante Privacy 10 giugno 2021.</p>

<h2>2. Cookie Categories</h2>

<h3>Category 1: Strictly Necessary Cookies ✅ Always Active</h3>
<p>Essential for the website to function. No consent required.</p>
<table>
  <thead><tr><th>Cookie</th><th>Provider</th><th>Purpose</th><th>Duration</th></tr></thead>
  <tbody>
    <tr><td><code>cf_clearance</code></td><td>Cloudflare</td><td>Security — prevents bot access</td><td>Session / 1 year</td></tr>
    <tr><td><code>__cf_bm</code></td><td>Cloudflare</td><td>Bot management</td><td>30 minutes</td></tr>
    <tr><td><code>italopedia_consent</code></td><td>Italopedia</td><td>Stores your cookie consent preferences</td><td>12 months</td></tr>
  </tbody>
</table>

<h3>Category 2: Analytics Cookies 📊 Require Consent</h3>
<p>Help us understand how visitors use our site. Data is aggregated and anonymized.</p>
<table>
  <thead><tr><th>Cookie</th><th>Provider</th><th>Purpose</th><th>Duration</th></tr></thead>
  <tbody>
    <tr><td><code>_ga</code></td><td>Google Analytics 4</td><td>Distinguishes unique users</td><td>2 years</td></tr>
    <tr><td><code>_ga_*</code></td><td>Google Analytics 4</td><td>Session state</td><td>2 years</td></tr>
    <tr><td><code>_gid</code></td><td>Google Analytics 4</td><td>Distinguishes users (24hr)</td><td>24 hours</td></tr>
  </tbody>
</table>
<p>IP anonymization is enabled. Data shared with Google LLC (USA) under Standard Contractual Clauses.<br/>
Opt out: <a href="https://tools.google.com/dlpage/gaoptout" target="_blank" rel="noopener">tools.google.com/dlpage/gaoptout</a></p>

<h3>Category 3: Advertising Cookies 📢 Require Consent</h3>
<p>Used to deliver relevant advertisements. May track you across multiple websites.</p>
<table>
  <thead><tr><th>Cookie</th><th>Provider</th><th>Purpose</th><th>Duration</th></tr></thead>
  <tbody>
    <tr><td><code>__gads</code></td><td>Google AdSense</td><td>Ad frequency and performance</td><td>13 months</td></tr>
    <tr><td><code>__gpi</code></td><td>Google AdSense</td><td>Ad personalization</td><td>13 months</td></tr>
    <tr><td><code>IDE</code></td><td>Google DoubleClick</td><td>Cross-site ad tracking</td><td>13 months</td></tr>
    <tr><td><code>NID</code></td><td>Google</td><td>Ad personalization</td><td>6 months</td></tr>
  </tbody>
</table>
<p>Opt out of personalized ads: <a href="https://adssettings.google.com" target="_blank" rel="noopener">adssettings.google.com</a> · <a href="https://www.youronlinechoices.eu" target="_blank" rel="noopener">youronlinechoices.eu</a></p>

<h3>Category 4: Functional Cookies ⚙️ Require Consent</h3>
<table>
  <thead><tr><th>Cookie</th><th>Provider</th><th>Purpose</th><th>Duration</th></tr></thead>
  <tbody>
    <tr><td><code>beehiiv_*</code></td><td>Beehiiv</td><td>Newsletter subscription state</td><td>1 year</td></tr>
    <tr><td><code>calendly_*</code></td><td>Calendly</td><td>Booking widget preferences</td><td>Session</td></tr>
  </tbody>
</table>

<h2>3. Third-Party Cookies</h2>
<table>
  <thead><tr><th>Third Party</th><th>When Present</th><th>Their Policy</th></tr></thead>
  <tbody>
    <tr><td>YouTube</td><td>If video embeds are present</td><td><a href="https://policies.google.com/privacy" target="_blank" rel="noopener">policies.google.com/privacy</a></td></tr>
    <tr><td>Calendly</td><td>On booking pages</td><td><a href="https://calendly.com/privacy" target="_blank" rel="noopener">calendly.com/privacy</a></td></tr>
    <tr><td>Gumroad</td><td>On product pages</td><td><a href="https://gumroad.com/privacy" target="_blank" rel="noopener">gumroad.com/privacy</a></td></tr>
    <tr><td>Beehiiv</td><td>On newsletter signup forms</td><td><a href="https://www.beehiiv.com/privacy" target="_blank" rel="noopener">beehiiv.com/privacy</a></td></tr>
  </tbody>
</table>

<h2>4. How Cookie Consent Works on This Site</h2>
<p>On your first visit, a consent banner appears. You can:</p>
<ul>
  <li><strong>Accept All</strong> — enables all cookie categories</li>
  <li><strong>Reject All</strong> — only strictly necessary cookies are set</li>
  <li><strong>Customize</strong> — choose which categories to enable or disable</li>
</ul>
<p>Your preferences are saved in the <code>italopedia_consent</code> cookie for 12 months. Change them at any time via <button class="cc-footer-btn" onclick="italopediaConsent.openModal()">Cookie Settings</button> in the page footer.</p>
<p><strong>GDPR compliance:</strong> Consent is obtained before non-essential cookies are set. Rejecting is as easy as accepting. No pre-ticked boxes. Consent is freely given, specific, informed, and unambiguous.</p>

<h2>5. Managing Cookies in Your Browser</h2>
<p><strong>Chrome:</strong> Settings → Privacy and Security → Cookies<br/>
<strong>Firefox:</strong> Settings → Privacy &amp; Security → Cookies and Site Data<br/>
<strong>Safari:</strong> Preferences → Privacy → Manage Website Data<br/>
<strong>Edge:</strong> Settings → Cookies and site permissions</p>
<p>Blocking all cookies may break some site functionality, including consent preference storage.</p>

<h2>6. Do Not Track (DNT)</h2>
<p>Our website does not respond differently to DNT signals, as there is no universal standard. We rely on our cookie consent system for compliance instead.</p>

<h2>7. Updates to This Policy</h2>
<p>We update this policy when we add new cookies, when third-party providers change their practices, or when legal requirements change. Material changes will be communicated via the cookie consent banner.</p>

<h2>8. Contact</h2>
<p><strong>Email:</strong> <a href="mailto:info@italopedia.com">info@italopedia.com</a> · Subject: Cookie Policy Inquiry<br/>
For broader privacy matters, see our full <a href="../privacy/">Privacy Policy</a>.<br/>
<strong>Supervisory authority:</strong> <a href="https://www.garanteprivacy.it" target="_blank" rel="noopener">Garante per la Protezione dei Dati Personali</a></p>'''


# ── 5. REDIRECT PAGE helper ───────────────────────────────────────────────
def redirect_page(target_url, title):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>{title} — Italopedia</title>
<link rel="canonical" href="https://italopedia.com{target_url}"/>
<meta http-equiv="refresh" content="0; url={target_url}"/>
</head>
<body>
<p>Redirecting to <a href="{target_url}">{title}</a>…</p>
</body>
</html>'''


# ── 6. FOOTER REPLACEMENT in existing pages ───────────────────────────────
FOOTER_LEGAL_NEW = '''<div class="footer-legal">
      <a href="{p}privacy/">Privacy Policy</a>
      <a href="{p}terms/">Terms</a>
      <a href="{p}cookies/">Cookie Policy</a>
      <a href="{p}affiliate-disclosure/">Affiliate Disclosure</a>
      <a href="{p}disclaimer/">Disclaimer</a>
      <button class="cc-footer-btn" onclick="italopediaConsent.openModal()">Cookie Settings</button>
    </div>'''

# Match existing footer-legal block (various formats)
FOOTER_LEGAL_RE = re.compile(
    r'<div class="footer-legal">.*?</div>',
    re.DOTALL
)

# ── 7. ADSENSE in head — remove it (consent JS loads it) ─────────────────
ADSENSE_HEAD_RE = re.compile(
    r'\s*<script[^>]*pagead2\.googlesyndication\.com[^>]*></script>',
    re.IGNORECASE
)

# ── 8. INJECT banner before </body> ───────────────────────────────────────
# We insert just before the first <script>window.SITE_PREFIX or before </body>
INJECT_BEFORE_RE = re.compile(r'(<script>window\.SITE_PREFIX)', re.IGNORECASE)
BODY_CLOSE_RE    = re.compile(r'</body>', re.IGNORECASE)

def inject_banner(content, prefix):
    banner = cookie_banner_html(prefix)
    # Try to inject before the SITE_PREFIX script line
    if INJECT_BEFORE_RE.search(content):
        def repl_prefix(m): return banner + '\n' + m.group(1)
        return INJECT_BEFORE_RE.sub(repl_prefix, content, count=1)
    # Fallback: inject before </body>
    def repl_body(m): return banner + '\n</body>'
    return BODY_CLOSE_RE.sub(repl_body, content, count=1)


# ══════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════
updated = []
errors  = []

# ── Step 1: Write /privacy/index.html ────────────────────────────────────
priv_path = os.path.join(BASE, 'privacy', 'index.html')
priv_html = page_shell(
    title     = 'Privacy Policy',
    desc      = 'How Italopedia collects, uses, and protects your personal information. Full GDPR-compliant privacy policy.',
    canonical = 'privacy',
    eyebrow   = 'Legal · Updated May 2026',
    h1        = 'Privacy Policy',
    hero_desc = 'How Italopedia collects, uses, and protects your personal information. GDPR-compliant, written in plain English.',
    content_html = PRIVACY_CONTENT,
    prefix    = '../'
)
os.makedirs(os.path.dirname(priv_path), exist_ok=True)
with open(priv_path, 'w', encoding='utf-8') as f: f.write(priv_html)
updated.append('✅ privacy/index.html — full GDPR privacy policy')

# ── Step 2: Write /cookies/index.html ────────────────────────────────────
cook_path = os.path.join(BASE, 'cookies', 'index.html')
cook_html = page_shell(
    title     = 'Cookie Policy',
    desc      = 'Full GDPR-compliant cookie policy for Italopedia — which cookies we use, why, and how to control them.',
    canonical = 'cookies',
    eyebrow   = 'Legal · Updated May 2026',
    h1        = 'Cookie Policy',
    hero_desc = 'Which cookies Italopedia uses, why, and how to control them. Compliant with GDPR and the Italian Garante.',
    content_html = COOKIE_CONTENT,
    prefix    = '../'
)
os.makedirs(os.path.dirname(cook_path), exist_ok=True)
with open(cook_path, 'w', encoding='utf-8') as f: f.write(cook_html)
updated.append('✅ cookies/index.html — full GDPR cookie policy')

# ── Step 3: Create /cookie-policy/ and /privacy-policy/ redirects ────────
for folder, target, title in [
    ('cookie-policy',  '/cookies/',  'Cookie Policy'),
    ('privacy-policy', '/privacy/',  'Privacy Policy'),
]:
    rdir = os.path.join(BASE, folder)
    os.makedirs(rdir, exist_ok=True)
    rpath = os.path.join(rdir, 'index.html')
    with open(rpath, 'w', encoding='utf-8') as f:
        f.write(redirect_page(target, title))
    updated.append(f'✅ {folder}/index.html — redirect to {target}')

# ── Step 4 & 5 & 6: Process every HTML file ──────────────────────────────
all_html = glob.glob(os.path.join(BASE, '**', '*.html'), recursive=True)
# Exclude the pages we already wrote above and the redirect pages
skip = {
    os.path.join(BASE, 'privacy', 'index.html'),
    os.path.join(BASE, 'cookies', 'index.html'),
    os.path.join(BASE, 'cookie-policy', 'index.html'),
    os.path.join(BASE, 'privacy-policy', 'index.html'),
}

banner_injected = 0
footer_updated  = 0
adsense_removed = 0

for fpath in sorted(all_html):
    if fpath in skip:
        continue
    # Skip script/asset files
    if '/assets/' in fpath.replace('\\', '/'):
        continue

    prefix = get_prefix(fpath)

    with open(fpath, encoding='utf-8') as f:
        content = f.read()

    orig = content

    # a) Remove AdSense from <head>
    new, n = ADSENSE_HEAD_RE.subn('', content)
    if n:
        content = new
        adsense_removed += 1

    # b) Update footer-legal
    new_legal = FOOTER_LEGAL_NEW.replace('{p}', prefix)
    new, n = FOOTER_LEGAL_RE.subn(new_legal, content)
    if n:
        content = new
        footer_updated += 1

    # c) Inject banner (only if not already present)
    if 'cc-banner' not in content:
        content = inject_banner(content, prefix)
        banner_injected += 1

    if content != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)

updated.append(f'✅ AdSense removed from <head> in {adsense_removed} files')
updated.append(f'✅ Footer updated (Cookie Settings added) in {footer_updated} files')
updated.append(f'✅ Cookie consent banner injected in {banner_injected} files')

# ── Report ────────────────────────────────────────────────────────────────
print('\n' + '='*60)
print('GDPR IMPLEMENTATION COMPLETE')
print('='*60)
for u in updated: print(u)
if errors:
    print('\n⚠️  ERRORS:')
    for e in errors: print(f'  {e}')
print('\n⚠️  NOTE: Replace GA4_ID "G-XXXXXXXXXX" in banner JS with your real GA4 Measurement ID')
print('='*60)
