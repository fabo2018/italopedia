#!/usr/bin/env python3
"""
Step 1: Add noindex to legal/transactional pages that are missing it.
Step 2: Remove all non-editorial URLs from sitemap.xml.

Pages kept indexable (revenue/lead-gen): consult, newsletter, resources, contact, about.
Pages made noindex: privacy-policy, cookie-policy, terms, disclaimer, affiliate-disclosure.
Already noindex (untouched): checkout, thank-you, cookies, privacy, shop/success.
"""
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))

# Pages that need noindex added (currently missing it)
NEEDS_NOINDEX = [
    "privacy-policy/index.html",
    "cookie-policy/index.html",
    "terms/index.html",
    "disclaimer/index.html",
    "affiliate-disclosure/index.html",
]

# All URLs to strip from sitemap (noindex pages + already-noindex pages)
SITEMAP_REMOVE = [
    "https://italopedia.com/checkout/",
    "https://italopedia.com/thank-you/",
    "https://italopedia.com/cookies/",
    "https://italopedia.com/privacy/",
    "https://italopedia.com/privacy-policy/",
    "https://italopedia.com/cookie-policy/",
    "https://italopedia.com/terms/",
    "https://italopedia.com/disclaimer/",
    "https://italopedia.com/affiliate-disclosure/",
]

CANONICAL_RE = re.compile(r'(<link rel="canonical"[^>]*>)')
NOINDEX_TAG = '<meta name="robots" content="noindex, nofollow"/>'

# ── Step 1: inject noindex ────────────────────────────────────────────────────
print("=== Step 1: Adding noindex ===")
for rel_path in NEEDS_NOINDEX:
    fpath = os.path.join(ROOT, rel_path)
    if not os.path.exists(fpath):
        print(f"  MISSING  {rel_path}")
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    if "noindex" in content:
        print(f"  SKIP (already noindex)  {rel_path}")
        continue
    if not CANONICAL_RE.search(content):
        print(f"  ERROR (no canonical)  {rel_path}")
        continue
    new_content = CANONICAL_RE.sub(r'\1\n' + NOINDEX_TAG, content, count=1)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  noindex added  {rel_path}")

# ── Step 2: clean sitemap ─────────────────────────────────────────────────────
print("\n=== Step 2: Cleaning sitemap.xml ===")
sitemap_path = os.path.join(ROOT, "sitemap.xml")
with open(sitemap_path, "r", encoding="utf-8") as f:
    sitemap = f.read()

# Each <url> block spans multiple lines; remove entire block for target URLs
url_block_re = re.compile(r'\s*<url>.*?</url>', re.DOTALL)

before_count = sitemap.count("<url>")
removed = []

def should_remove(block):
    for url in SITEMAP_REMOVE:
        if f"<loc>{url}</loc>" in block:
            return True
    return False

new_sitemap = url_block_re.sub(
    lambda m: "" if should_remove(m.group(0)) else m.group(0),
    sitemap
)

after_count = new_sitemap.count("<url>")
removed_count = before_count - after_count

with open(sitemap_path, "w", encoding="utf-8") as f:
    f.write(new_sitemap)

print(f"  Sitemap: {before_count} URLs → {after_count} URLs ({removed_count} removed)")
for url in SITEMAP_REMOVE:
    found = f"<loc>{url}</loc>" in sitemap
    still = f"<loc>{url}</loc>" in new_sitemap
    status = "removed ✓" if (found and not still) else ("not found" if not found else "ERROR still present ✗")
    print(f"  {status}  {url}")
