#!/usr/bin/env python3
"""
Sostituisce i Beehiiv embed (iframe bianco) con form native brandizzate.
Uso: python3 fix_newsletter_forms.py           → dry-run
     python3 fix_newsletter_forms.py --apply   → applica
Idempotente.
"""

import sys, re
from pathlib import Path

ROOT    = Path(__file__).parent
APPLY   = "--apply" in sys.argv

BEEHIIV_SCRIPT = '<script async src="https://subscribe-forms.beehiiv.com/v3/loader.js" data-beehiiv-form="83935e9a-30fd-4975-a79a-e10be8100271"></script>'

# ── Replacement for <div class="newsletter-embed">…</div> ────────────────────
EMBED_OLD = f'<div class="newsletter-embed">{BEEHIIV_SCRIPT}</div>'
EMBED_NEW = (
    '<div class="newsletter-embed">'
      '<div class="nl-embed-card">'
        '<div class="nl-embed-title">Italopedia Weekly</div>'
        '<div class="nl-embed-sub">Free · 4,200+ readers · No spam</div>'
        '<form onsubmit="nlSubscribe(this,event)">'
          '<div class="form-field">'
            '<label class="form-label">Your email address</label>'
            '<input class="form-input" type="email" placeholder="you@example.com" required/>'
          '</div>'
          '<button class="form-submit" type="submit">Get the free guide →</button>'
        '</form>'
        '<span class="nl-msg"></span>'
        '<p class="nl-embed-note">Unsubscribe anytime · one email per week</p>'
      '</div>'
    '</div>'
)

# ── Replacement for bare script in footer ────────────────────────────────────
FOOTER_NEW = (
    '<form class="nl-footer-form" onsubmit="nlSubscribe(this,event)">'
      '<input class="form-input" type="email" placeholder="your@email.com" required/>'
      '<button class="form-submit" type="submit">Subscribe →</button>'
    '</form>'
)

def process(path):
    html = path.read_text(encoding="utf-8", errors="replace")
    if BEEHIIV_SCRIPT not in html:
        return False  # already done or no embed

    new = html
    # 1. Replace newsletter-embed div first (more specific)
    new = new.replace(EMBED_OLD, EMBED_NEW)
    # 2. Replace any remaining bare script (footer)
    new = new.replace(BEEHIIV_SCRIPT, FOOTER_NEW)

    if new == html:
        return False
    if APPLY:
        path.write_text(new, encoding="utf-8")
    return True

def main():
    files = sorted(ROOT.glob("**/*.html"))
    changed = []
    for p in files:
        if process(p):
            changed.append(p.relative_to(ROOT))

    label = "APPLIED" if APPLY else "DRY-RUN"
    print(f"[{label}] {len(changed)} file modificati")
    for f in changed:
        print(f"  {f}")

if __name__ == "__main__":
    main()
