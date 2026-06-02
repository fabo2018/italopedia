#!/usr/bin/env python3
"""
Adds Person @id to all Article schema author fields across all 112 articles.
The Person entity lives at https://italopedia.com/#fabrizio (defined in /about/).
"""
import os, re

PERSON_ID = "https://italopedia.com/#fabrizio"
PERSON_NAME = "Fabrizio Boggio"

# Pattern: "author":{"@type":"Person","name":"Fabrizio Boggio","jobTitle":"..."}
# Replace with: "author":{"@type":"Person","@id":"...","name":"Fabrizio Boggio","jobTitle":"..."}
OLD_AUTHOR = re.compile(
    r'"author"\s*:\s*\{([^}]*"@type"\s*:\s*"Person"[^}]*)\}'
)

def make_new_author(m):
    inner = m.group(1)
    if f'"@id"' in inner:
        return m.group(0)  # already has @id, skip
    # inject @id right after @type
    inner = re.sub(
        r'("@type"\s*:\s*"Person")',
        rf'\1,"@id":"{PERSON_ID}"',
        inner
    )
    return f'"author":{{{inner}}}'

root = os.path.dirname(os.path.abspath(__file__))
updated = []
skipped = []

for dirpath, _, filenames in os.walk(root):
    for fname in filenames:
        if fname != "index.html":
            continue
        fpath = os.path.join(dirpath, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        if '"datePublished"' not in content:
            continue  # not an article page
        if OLD_AUTHOR.search(content) and f'"@id":"{PERSON_ID}"' not in content:
            new_content = OLD_AUTHOR.sub(make_new_author, content)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            updated.append(os.path.relpath(fpath, root))
        elif f'"@id":"{PERSON_ID}"' in content:
            skipped.append(os.path.relpath(fpath, root))

print(f"Updated: {len(updated)} files")
print(f"Already had @id: {len(skipped)} files")
if updated:
    for p in sorted(updated)[:10]:
        print(f"  ✓ {p}")
    if len(updated) > 10:
        print(f"  ... and {len(updated)-10} more")
