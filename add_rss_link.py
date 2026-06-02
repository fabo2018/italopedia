#!/usr/bin/env python3
"""
Adds <link rel="alternate" type="application/rss+xml"> to the <head>
of every indexable page that doesn't already have it.
Skips noindex pages.
"""
import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
RSS_TAG = '<link rel="alternate" type="application/rss+xml" title="Italopedia RSS Feed" href="https://italopedia.com/feed.xml"/>'
CANONICAL_RE = re.compile(r'(<link rel="canonical"[^>]*>)')

updated, skipped = [], []

for dirpath, _, filenames in os.walk(ROOT):
    for fname in filenames:
        if fname != "index.html":
            continue
        fpath = os.path.join(dirpath, fname)
        with open(fpath, encoding="utf-8") as f:
            content = f.read()

        if "noindex" in content:
            continue
        if "application/rss+xml" in content:
            skipped.append(fpath)
            continue
        if not CANONICAL_RE.search(content):
            continue

        new_content = CANONICAL_RE.sub(r'\1\n' + RSS_TAG, content, count=1)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)
        updated.append(os.path.relpath(fpath, ROOT))

print(f"RSS link added to {len(updated)} pages")
print(f"Already present:  {len(skipped)}")
