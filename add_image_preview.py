#!/usr/bin/env python3
"""
Inserts <meta name="robots" content="index, follow, max-image-preview:large"/>
after the canonical tag on every indexable page.

Rules:
- SKIP pages that already have name="robots" (noindex pages — never touch them)
- SKIP pages that already contain max-image-preview (idempotent)
- INSERT only after <link rel="canonical" .../>
- Fail loudly if canonical tag is not found in a page
"""
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
ROBOTS_TAG = '<meta name="robots" content="index, follow, max-image-preview:large"/>'

CANONICAL_RE = re.compile(r'(<link rel="canonical"[^>]*>)')

updated = []
skipped_noindex = []
skipped_already = []
errors = []

for dirpath, _, filenames in os.walk(ROOT):
    for fname in filenames:
        if fname != "index.html":
            continue
        fpath = os.path.join(dirpath, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        # Skip pages with any existing robots meta (noindex etc.)
        if 'name="robots"' in content:
            skipped_noindex.append(os.path.relpath(fpath, ROOT))
            continue

        # Skip if already has max-image-preview (idempotent)
        if "max-image-preview" in content:
            skipped_already.append(os.path.relpath(fpath, ROOT))
            continue

        # Must have a canonical tag — fail loudly otherwise
        if not CANONICAL_RE.search(content):
            errors.append(os.path.relpath(fpath, ROOT))
            continue

        # Insert robots tag on new line immediately after canonical
        new_content = CANONICAL_RE.sub(
            r'\1\n' + ROBOTS_TAG,
            content,
            count=1
        )

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)
        updated.append(os.path.relpath(fpath, ROOT))

print(f"Updated:          {len(updated)} pages")
print(f"Skipped (noindex): {len(skipped_noindex)} pages — {skipped_noindex}")
print(f"Skipped (already): {len(skipped_already)} pages")
if errors:
    print(f"\nERRORS — no canonical tag found in:")
    for e in errors:
        print(f"  ✗ {e}")
