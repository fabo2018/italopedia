#!/usr/bin/env python3
"""
Replace all fake newsletter forms with real Beehiiv embed.
1. Homepage: replace <form class="newsletter-form"> inside newsletter section
2. Newsletter page: same
3. All pages footer: add Beehiiv embed between footer-top and footer-bottom
"""

import os, re, glob

BASE = os.path.dirname(os.path.abspath(__file__))

BEEHIIV_SCRIPT = '<script async src="https://subscribe-forms.beehiiv.com/v3/loader.js" data-beehiiv-form="83935e9a-30fd-4975-a79a-e10be8100271"></script>'

# Replacement for the fake <form class="newsletter-form">...</form>
FORM_RE = re.compile(r'<form class="newsletter-form".*?</form>', re.DOTALL)

# Footer newsletter block (inserted between footer-top and footer-bottom)
FOOTER_NL_BLOCK = f'''    <div class="footer-newsletter">
      <p class="footer-newsletter-label">Free weekly guide — join 4,200+ readers</p>
      {BEEHIIV_SCRIPT}
    </div>'''

# CSS for footer newsletter block — added once to index.html (already has main.css)
# We'll inline a small style in the footer block itself
FOOTER_NL_BLOCK_STYLED = f'''    <div class="footer-newsletter" style="border-top:1px solid var(--color-border,#2a2520);padding:1.5rem 0 1rem;margin-top:.5rem">
      <p style="font-size:.85rem;color:rgba(250,247,240,.55);margin:0 0 .75rem;font-family:var(--font-heading,'Syne'),sans-serif;letter-spacing:.04em;text-transform:uppercase">Free weekly guide — join 4,200+ readers</p>
      {BEEHIIV_SCRIPT}
    </div>'''

# Anchor strings for footer insertion
FOOTER_BOTTOM_RE = re.compile(r'(<div class="footer-bottom">)')

# Old-format footer (site-footer): insert before </footer>
SITE_FOOTER_NL = f'''  <div style="border-top:1px solid rgba(255,255,255,.1);padding:1.25rem 0 .5rem;margin-top:1rem">
    <p style="font-size:.8rem;color:rgba(250,247,240,.5);margin:0 0 .75rem">Free weekly guide — join 4,200+ readers</p>
    {BEEHIIV_SCRIPT}
  </div>
</div></footer>'''

SITE_FOOTER_RE = re.compile(r'</div></footer>')

updated = []
skipped = []

all_html = sorted(glob.glob(os.path.join(BASE, '**', '*.html'), recursive=True))
all_html = [f for f in all_html if '/assets/' not in f.replace('\\', '/')]

for fpath in all_html:
    rel = os.path.relpath(fpath, BASE).replace('\\', '/')
    with open(fpath, encoding='utf-8') as f:
        content = f.read()
    orig = content
    changed = []

    # ── 1. Replace fake form (homepage + newsletter page) ─────────────────
    if FORM_RE.search(content):
        content = FORM_RE.sub(
            f'<div class="newsletter-embed">{BEEHIIV_SCRIPT}</div>',
            content
        )
        changed.append('form→beehiiv')

    # ── 2. Footer: add newsletter embed (all pages that have a footer) ────
    # Skip if already added
    if 'beehiiv.com' in content and 'footer-newsletter' in content:
        skipped.append(f'already has footer embed: {rel}')
    elif FOOTER_BOTTOM_RE.search(content):
        # New-style footer
        content = FOOTER_BOTTOM_RE.sub(
            FOOTER_NL_BLOCK_STYLED + '\n    \\1',
            content,
            count=1
        )
        changed.append('footer-nl added (new-style)')
    elif SITE_FOOTER_RE.search(content):
        # Old-style footer (site-footer class) — only one closing </div></footer>
        content = SITE_FOOTER_RE.sub(SITE_FOOTER_NL, content, count=1)
        changed.append('footer-nl added (old-style)')

    if content != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        updated.append(f'  ✅ {rel}: {", ".join(changed)}')

print(f'\nUpdated {len(updated)} files:')
for u in updated: print(u)
if skipped:
    print(f'\nSkipped:')
    for s in skipped: print(f'  {s}')
