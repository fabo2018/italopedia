#!/usr/bin/env python3
"""Add affiliate links to the FIRST unlinked body mention of each insurance provider.

Skips occurrences inside: <meta, <title, <script, <style, <noscript, <head
"""

import os, re

ROOT = os.path.dirname(os.path.abspath(__file__))

PROVIDERS = {
    "Cigna Global":      "https://www.cigna.com/international",
    "AXA International": "https://www.axaglobalhealthcare.com",
    "Allianz Care":      "https://www.allianzcare.com",
    "GeoBlue":           "https://www.geo-blue.com",
    "SafetyWing":        "https://www.safetywing.com",
}

# Tags whose content must never receive links
NO_LINK_TAGS = re.compile(
    r"<(meta|title|script|style|noscript|head)[\s>]", re.IGNORECASE
)

def is_in_bad_zone(content, pos):
    """Return True if pos is inside a meta/title/script/style/head block."""
    before = content[:pos]
    # Find the last opening "bad" tag before this position
    for m in re.finditer(NO_LINK_TAGS, before):
        tag = m.group(1).lower()
        close = f"</{tag}>"
        # Check if it was already closed before pos
        close_pos = before.find(close, m.end())
        if close_pos == -1:
            # No closing tag found before pos → still open → we're inside it
            # Special case: <meta> and some others are self-closing (no </meta>)
            # For meta we can just check if the > that ends the tag is before pos
            tag_end = before.find(">", m.end())
            if tag in ("meta", "link", "br", "hr", "input"):
                # self-closing: we're NOT inside the tag body, just in its attribute
                # If our pos is between the < and > of the meta tag, we're inside it
                if tag_end != -1 and tag_end >= pos:
                    return True
            else:
                # block tag not yet closed → we're inside it
                return True
    return False

def is_inside_anchor(content, pos):
    """Return True if pos is inside an <a ...> ... </a> block."""
    before = content[:pos]
    last_open  = before.rfind("<a")
    last_close = before.rfind("</a>")
    return last_open != -1 and last_open > last_close

def link_tag(name, url):
    return f'<a href="{url}" target="_blank" rel="sponsored nofollow">{name}</a>'

def process_file(fpath):
    rel = os.path.relpath(fpath, ROOT)
    with open(fpath, encoding="utf-8") as f:
        content = f.read()

    original = content
    changes = []

    for name, url in PROVIDERS.items():
        search_from = 0
        while True:
            pos = content.find(name, search_from)
            if pos == -1:
                break
            if is_inside_anchor(content, pos):
                break  # already linked — first occurrence is done
            if is_in_bad_zone(content, pos):
                search_from = pos + len(name)
                continue  # skip this occurrence, try next
            # Good position — link it
            replacement = link_tag(name, url)
            content = content[:pos] + replacement + content[pos + len(name):]
            changes.append(name)
            break

    if content != original:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  FIXED  {rel}  →  {', '.join(changes)}")
    else:
        print(f"  SKIP   {rel}")

def main():
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in sorted(dirs) if not d.startswith(".")]
        for fn in sorted(files):
            if fn.endswith((".html", ".md", ".mdx")):
                process_file(os.path.join(root, fn))
    print("\nDone.")

if __name__ == "__main__":
    main()
