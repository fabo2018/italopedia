#!/usr/bin/env python3
"""
Fix cookie consent banner across all 84 HTML pages.

Bugs fixed:
1. gc() used '\\s' in a JS string literal — in a string, \\s becomes 's' (not
   a regex whitespace class), so the cookie was not found if italopedia_consent
   was not the FIRST cookie in document.cookie (it never is — _ga, __cf_bm etc.
   appear first). Fix: replace regex approach with a reliable split(';') loop.

2. sc() missing max-age= — adds max-age as a belt-and-suspenders alongside
   expires= for older browser compatibility.

3. Preferences applied too late — apply(c) was inside DOMContentLoaded.
   Since the banner script is at the end of <body>, the DOM is already parsed
   when the script runs. Move banner show/hide + apply() to immediate execution
   so GA4 consent + AdSense fire as early as possible on every page load.
"""

import os, glob, re

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Old strings to replace ────────────────────────────────────────────────

OLD_GC = (
    "function gc(){var m=document.cookie.match(new RegExp('(?:^|;\\s*)'"
    "+CNAME+'=([^;]*)'));try{return m?JSON.parse(decodeURIComponent(m[1])):null}"
    "catch(e){return null}}"
)

NEW_GC = (
    "function gc(){var cs=document.cookie.split(';');"
    "for(var i=0;i<cs.length;i++){var c=cs[i].trim();"
    "if(c.indexOf(CNAME+'=')===0){"
    "try{return JSON.parse(decodeURIComponent(c.slice(CNAME.length+1)));}"
    "catch(e){return null;}}}"
    "return null;}"
)

OLD_SC = (
    "function sc(v){var d=new Date();d.setTime(d.getTime()+DAYS*864e5);"
    "document.cookie=CNAME+'='+encodeURIComponent(JSON.stringify(v))"
    "+';expires='+d.toUTCString()+';path=/;SameSite=Lax'}"
)

NEW_SC = (
    "function sc(v){var d=new Date();d.setTime(d.getTime()+DAYS*864e5);"
    "document.cookie=CNAME+'='+encodeURIComponent(JSON.stringify(v))"
    "+';expires='+d.toUTCString()+';max-age='+DAYS*86400+';path=/;SameSite=Lax'}"
)

# The old DOMContentLoaded block — including the two lines at the start
# that read cookie and conditionally show banner or apply prefs.
OLD_DCL = """\
document.addEventListener('DOMContentLoaded',function(){
  var c=gc();
  if(!c){show('cc-banner');loadAds(false)}
  else{apply(c)}
  var ab=el('cc-accept-btn');if(ab)ab.addEventListener('click',function(){var c={necessary:true,analytics:true,advertising:true,functional:true,ts:Date.now()};sc(c);hide('cc-banner');closeModal();apply(c)});
  var rb=el('cc-reject-btn');if(rb)rb.addEventListener('click',function(){var c={necessary:true,analytics:false,advertising:false,functional:false,ts:Date.now()};sc(c);hide('cc-banner');closeModal();apply(c)});
  var cb=el('cc-customize-btn');if(cb)cb.addEventListener('click',openModal);
  var sb=el('cc-save-btn');if(sb)sb.addEventListener('click',function(){
    var a=el('cc-t-analytics'),ad=el('cc-t-advertising'),f=el('cc-t-functional');
    var c={necessary:true,analytics:a?a.checked:false,advertising:ad?ad.checked:false,functional:f?f.checked:false,ts:Date.now()};
    sc(c);hide('cc-banner');closeModal();apply(c);
  });
  var xb=el('cc-close-btn');if(xb)xb.addEventListener('click',closeModal);
  var ov=el('cc-overlay');if(ov)ov.addEventListener('click',closeModal);
});"""

# New version: apply preferences IMMEDIATELY (script is at end of <body>,
# DOM is already parsed), wire event listeners in DOMContentLoaded.
NEW_DCL = """\
var _cc=gc();
if(_cc){apply(_cc);}else{loadAds(false);show('cc-banner');}
document.addEventListener('DOMContentLoaded',function(){
  var ab=el('cc-accept-btn');if(ab)ab.addEventListener('click',function(){var c={necessary:true,analytics:true,advertising:true,functional:true,ts:Date.now()};sc(c);hide('cc-banner');closeModal();apply(c)});
  var rb=el('cc-reject-btn');if(rb)rb.addEventListener('click',function(){var c={necessary:true,analytics:false,advertising:false,functional:false,ts:Date.now()};sc(c);hide('cc-banner');closeModal();apply(c)});
  var cb=el('cc-customize-btn');if(cb)cb.addEventListener('click',openModal);
  var sb=el('cc-save-btn');if(sb)sb.addEventListener('click',function(){
    var a=el('cc-t-analytics'),ad=el('cc-t-advertising'),f=el('cc-t-functional');
    var c={necessary:true,analytics:a?a.checked:false,advertising:ad?ad.checked:false,functional:f?f.checked:false,ts:Date.now()};
    sc(c);hide('cc-banner');closeModal();apply(c);
  });
  var xb=el('cc-close-btn');if(xb)xb.addEventListener('click',closeModal);
  var ov=el('cc-overlay');if(ov)ov.addEventListener('click',closeModal);
});"""

# ── Process all HTML files ────────────────────────────────────────────────

all_html = sorted(glob.glob(os.path.join(BASE, '**', '*.html'), recursive=True))
all_html = [f for f in all_html if '/assets/' not in f.replace('\\', '/')]

updated = 0
errors = []

for fpath in all_html:
    try:
        with open(fpath, encoding='utf-8') as f:
            content = f.read()

        if 'italopedia_consent' not in content:
            continue

        orig = content

        if OLD_GC in content:
            content = content.replace(OLD_GC, NEW_GC)
        if OLD_SC in content:
            content = content.replace(OLD_SC, NEW_SC)
        if OLD_DCL in content:
            content = content.replace(OLD_DCL, NEW_DCL)

        if content != orig:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
            updated += 1

    except Exception as e:
        errors.append(f'{fpath}: {e}')

print(f'Updated {updated} files.')
if errors:
    print('Errors:')
    for e in errors:
        print(f'  {e}')
