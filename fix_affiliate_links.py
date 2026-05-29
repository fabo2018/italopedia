#!/usr/bin/env python3
"""Add affiliate links to first brand mentions in article body text."""

import os

BASE = "/Users/fabrizio/italopedia/"

CIGNA     = '<a href="https://www.cigna.com/international" target="_blank" rel="sponsored nofollow">Cigna Global</a>'
AXA       = '<a href="https://www.axaglobalhealthcare.com" target="_blank" rel="sponsored nofollow">AXA International</a>'
ALLIANZ   = '<a href="https://www.allianzcare.com" target="_blank" rel="sponsored nofollow">Allianz Care</a>'
GEOBLUE   = '<a href="https://www.geo-blue.com" target="_blank" rel="sponsored nofollow">GeoBlue</a>'
SAFETYWING = '<a href="https://www.safetywing.com" target="_blank" rel="sponsored nofollow">SafetyWing</a>'


def edit(path, replacements):
    full = BASE + path
    with open(full, "r", encoding="utf-8") as f:
        content = f.read()
    original = content
    for old, new in replacements:
        if old not in content:
            print(f"  WARNING: pattern not found in {path}:\n    {old!r}")
            continue
        content = content.replace(old, new, 1)
    if content != original:
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  OK  {path} ({len(replacements)} replacement(s))")
    else:
        print(f"  SKIP {path} (no changes)")


# ── 1. best-health-insurance-americans-italy ──────────────────────────────────
# First body mention for each brand is in the h2 section headings.
edit("healthcare/best-health-insurance-americans-italy/index.html", [
    ("1. Cigna Global</h2>",                    f"1. {CIGNA}</h2>"),
    ("2. AXA International (AXA Global",        f"2. {AXA} (AXA Global"),
    ("3. Allianz Care (formerly Allianz",       f"3. {ALLIANZ} (formerly Allianz"),
    ("4. GeoBlue (Xplorer)</h2>",               f"4. {GEOBLUE} (Xplorer)</h2>"),
    ("5. SafetyWing (Nomad Insurance)</h2>",    f"5. {SAFETYWING} (Nomad Insurance)</h2>"),
])

# ── 2. cigna-vs-axa-vs-allianz-italy ─────────────────────────────────────────
# First body mentions: dek (all 3 brands) + GeoBlue in bullet list.
edit("healthcare/cigna-vs-axa-vs-allianz-italy/index.html", [
    (
        "Cigna Global, AXA International, and Allianz Care for Americans living in Italy",
        f"{CIGNA}, {AXA}, and {ALLIANZ} for Americans living in Italy",
    ),
    (
        "GeoBlue (not in the top 3, but worth noting)",
        f"{GEOBLUE} (not in the top 3, but worth noting)",
    ),
])

# ── 3. best-private-health-insurance-italy-americans-2025 ─────────────────────
# First body mentions in the Quick Answer callout (before h3 headings).
edit("healthcare/best-private-health-insurance-italy-americans-2025/index.html", [
    (
        "Cigna Global (best all-around), AXA International (best for retirees), Allianz Care (best network in Italy)",
        f"{CIGNA} (best all-around), {AXA} (best for retirees), {ALLIANZ} (best network in Italy)",
    ),
])

# ── 4. affiliate-disclosure ───────────────────────────────────────────────────
# Brand names listed in the disclosure without links.
edit("affiliate-disclosure/index.html", [
    ("<strong>Cigna Global Health Insurance</strong>", f"<strong>{CIGNA} Health Insurance</strong>"),
    ("<strong>AXA International</strong>",             f"<strong>{AXA}</strong>"),
    ("<strong>Allianz Care</strong>",                  f"<strong>{ALLIANZ}</strong>"),
])

print("\nDone.")
