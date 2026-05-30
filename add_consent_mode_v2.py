#!/usr/bin/env python3
"""
1. Inject Google Consent Mode v2 + GA4 script into <head> of every HTML page
2. Update inline banner JS:
   - Remove loadGA4() (GA4 is always loaded now)
   - Add updateCM() that calls gtag('consent','update',…) based on user choices
   - Replace apply(c) to use updateCM instead of loadGA4
"""
import os, re, glob

BASE = os.path.dirname(os.path.abspath(__file__))
GA4_ID = 'G-THJ4KV6KR2'

# ── Block to inject right after <head> ────────────────────────────────────
HEAD_BLOCK = f'''<!-- Google Consent Mode v2 -->
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('consent', 'default', {{
  'analytics_storage': 'denied',
  'ad_storage': 'denied',
  'ad_user_data': 'denied',
  'ad_personalization': 'denied',
  'wait_for_update': 500
}});
</script>
<!-- Google tag (GA4) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('js', new Date());
gtag('config', '{GA4_ID}');
</script>'''

HEAD_RE = re.compile(r'<head>', re.IGNORECASE)

# ── Banner JS changes ─────────────────────────────────────────────────────
# 1. Remove loadGA4 function definition
LOAD_GA4_FN_RE = re.compile(
    r"function loadGA4\(\)\{[^}]+\}",
    re.DOTALL
)

# 2. Replace apply(c) — remove loadGA4 call, add updateCM call
OLD_APPLY = "function apply(c){if(c.analytics)loadGA4();loadAds(c.advertising)}"
NEW_APPLY = (
    "function updateCM(c){"
    "if(typeof gtag!=='function')return;"
    "if(c.analytics)gtag('consent','update',{'analytics_storage':'granted'});"
    "if(c.advertising)gtag('consent','update',{"
    "'ad_storage':'granted','ad_user_data':'granted','ad_personalization':'granted'"
    "});}"
    "function apply(c){updateCM(c);loadAds(c.advertising)}"
)

# ── Process files ─────────────────────────────────────────────────────────
all_html = sorted(glob.glob(os.path.join(BASE, '**', '*.html'), recursive=True))
# Skip assets
all_html = [f for f in all_html if '/assets/' not in f.replace('\\', '/')]

head_injected  = 0
banner_updated = 0
errors = []

for fpath in all_html:
    try:
        with open(fpath, encoding='utf-8') as f:
            content = f.read()
        orig = content

        # ── 1. Inject head block (skip if already done) ──────────────────
        if 'Consent Mode v2' not in content and HEAD_RE.search(content):
            content = HEAD_RE.sub('<head>\n' + HEAD_BLOCK, content, count=1)
            head_injected += 1

        # ── 2. Update banner JS ──────────────────────────────────────────
        if 'function loadGA4()' in content:
            # Remove loadGA4 function body
            content = LOAD_GA4_FN_RE.sub('', content)
            banner_updated += 1

        if OLD_APPLY in content:
            content = content.replace(OLD_APPLY, NEW_APPLY)

        if content != orig:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)

    except Exception as e:
        errors.append(f'{fpath}: {e}')

print(f'\n✅ Consent Mode v2 + GA4 injected in <head>: {head_injected} files')
print(f'✅ Banner JS updated (loadGA4 → updateCM):   {banner_updated} files')
if errors:
    print('\n⚠️  Errors:')
    for e in errors: print(f'  {e}')
