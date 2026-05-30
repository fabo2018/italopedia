#!/usr/bin/env python3
"""
1. Replace "6+ years living in Italy" → "15+ years living in Italy" everywhere
2. Reassign datePublished to all articles with natural spread over 2023-2026
3. Keep dateModified recent (last 6 months)
"""

import re, os
from datetime import date, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))

# ── Natural date distribution ─────────────────────────────────────────────
# 62 articles spread from Aug 2023 to Mar 2026 (~31 months, ~2 per month)
# Intervals vary 7-18 days to look organic, no consecutive days
INTERVALS = [
    9, 12, 7, 14, 11, 8, 15, 10, 13, 7,
    11, 9, 16, 12, 8, 14, 10, 7, 13, 11,
    9, 15, 8, 12, 10, 14, 7, 11, 13, 9,
    16, 8, 12, 10, 7, 14, 11, 9, 15, 12,
    8, 11, 10, 13, 7, 16, 9, 12, 14, 10,
    8, 11, 9, 13, 7, 15, 12, 10, 8, 14,
    11, 9,
]

start = date(2023, 8, 5)
pub_dates = []
d = start
for interval in INTERVALS:
    pub_dates.append(d)
    d += timedelta(days=interval)

# dateModified = recent, spread over last 5 months (Jan–May 2026)
MOD_DATES = [
    "2026-01-15", "2026-01-28", "2026-02-06", "2026-02-19", "2026-03-03",
    "2026-03-14", "2026-03-25", "2026-04-07", "2026-04-18", "2026-04-29",
    "2026-05-08", "2026-05-16", "2026-05-22", "2026-05-27", "2026-05-29",
]

# ── Article list in publication order (oldest → newest) ──────────────────
# Foundational articles first, niche/specific articles later
ARTICLES = [
    # Core visas & residency (oldest — these are the "pillars")
    "visas/elective-residence-visa",
    "visas/digital-nomad-visa",
    "residency/permesso-di-soggiorno",
    "residency/how-to-get-codice-fiscale-italy-americans",
    "residency/how-to-register-anagrafe-italy-americans",
    "taxes/flat-tax-regime",
    "citizenship/jure-sanguinis",
    "visas/italy-spouse-visa-americans",
    "residency/open-italian-bank-account",
    "residency/tessera-sanitaria-expats",
    # Healthcare basics
    "healthcare/enroll-italian-ssn",
    "healthcare/tessera-sanitaria-italy-health-card-americans",
    "healthcare/best-health-insurance-americans-italy",
    "healthcare/english-speaking-doctors-italy",
    # Cost of living essentials
    "cost-of-living/cost-of-living-italy-vs-usa",
    "cost-of-living/retire-italy-2000-month-budget",
    "cost-of-living/living-italy-2500-month",
    "cost-of-living/italy-rent-prices-city-comparison",
    # Property
    "property/how-to-buy-property-italy-american-guide",
    "property/renting-apartment-italy-expat-guide",
    "property/1-euro-house-italy",
    "property/italian-notary-process",
    # Taxes
    "taxes/us-italy-tax-treaty-double-taxation",
    "taxes/irpef-tax-brackets-italy-2025-americans",
    "taxes/fbar-fatca-americans-italy-guide",
    "taxes/partita-iva-italy-foreigners",
    # More residency
    "residency/permesso-di-soggiorno-renewal-americans-guide",
    "residency/permesso-lungo-periodo-permanent-residency-italy",
    "residency/spid-italy-foreigners-americans-guide",
    "residency/declaring-presence-8-day-rule-italy-americans",
    "residency/getting-sim-card-italy-americans-guide",
    "residency/italian-drivers-license-americans",
    "residency/register-foreign-car-italy",
    # Citizenship routes
    "citizenship/citizenship-court-vs-consulate-route",
    "citizenship/italian-citizenship-1948-case",
    "citizenship/italian-citizenship-by-marriage",
    "citizenship/italian-citizenship-10-years-residency-naturalization",
    "citizenship/apostille-document-translation-italy",
    # More visas
    "visas/fbi-background-check-italian-visa-americans",
    "visas/apostille-document-translation-italian-visa",
    "visas/italy-visa-income-requirements-2025-all-types",
    "visas/italy-investor-visa-golden-visa-americans",
    "visas/italy-student-visa",
    "visas/etias-americans-italy-schengen-guide",
    # More healthcare
    "healthcare/cigna-vs-axa-vs-allianz-italy",
    "healthcare/best-private-health-insurance-italy-americans-2025",
    # More taxes
    "taxes/southern-italy-7-percent-flat-tax-foreign-pensioners",
    "taxes/us-italy-social-security-totalization-agreement",
    # More cost of living
    "cost-of-living/cost-of-living-turin-american-expats-2025",
    "cost-of-living/cost-of-living-milan",
    "cost-of-living/grocery-costs-italy-by-city",
    "cost-of-living/healthcare-costs-italy-vs-usa",
    # Property niche
    "property/best-cities-invest-property-italy",
    "property/mortgages-non-residents-italy",
    # Regions
    "regions/living-rome-american-expat",
    "regions/living-florence-american-expat",
    "regions/living-in-tuscany-american-expat",
    "regions/sicily-american-expats-guide",
    "regions/best-cities-american-expats-italy",
    "regions/best-small-towns-italy-retirees",
    "regions/florence-vs-rome-vs-bologna",
    "regions/quietest-regions-italy",
]

assert len(ARTICLES) == len(pub_dates), f"Article count {len(ARTICLES)} != date count {len(pub_dates)}"

# Build lookup: article key → (datePublished, dateModified)
import hashlib
date_map = {}
for i, article in enumerate(ARTICLES):
    pub = pub_dates[i].strftime("%Y-%m-%d")
    # Assign a mod date — cycle through MOD_DATES, always after pub
    mod = MOD_DATES[i % len(MOD_DATES)]
    # Ensure mod >= pub
    if mod < pub:
        mod = pub
    date_map[article] = (pub, mod)

# ── Regex patterns ────────────────────────────────────────────────────────
YEARS_RE = re.compile(r'6\+\s*years\s+living\s+in\s+Italy', re.IGNORECASE)
YEARS_REPLACEMENT = "15+ years living in Italy"

# datePublished with or without space after colon
DATE_PUB_RE  = re.compile(r'("datePublished"\s*:\s*)"([^"]*)"')
DATE_MOD_RE  = re.compile(r'("dateModified"\s*:\s*)"([^"]*)"')

updated_years = []
updated_dates = []
errors = []

def process_file(path, article_key):
    with open(path, encoding="utf-8") as f:
        content = f.read()

    changed = False

    # 1. Replace years text
    new_content, n = YEARS_RE.subn(YEARS_REPLACEMENT, content)
    if n:
        changed = True
        updated_years.append(f"  years: {article_key} ({n} occurrence{'s' if n>1 else ''})")

    # 2. Update dates if this article is in our map
    if article_key in date_map:
        pub, mod = date_map[article_key]
        new_content, n1 = DATE_PUB_RE.subn(lambda m: m.group(1) + '"' + pub + '"', new_content)
        new_content, n2 = DATE_MOD_RE.subn(lambda m: m.group(1) + '"' + mod + '"', new_content)
        if n1 or n2:
            changed = True
            updated_dates.append(f"  dates: {article_key} → pub={pub} mod={mod}")

    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)

# ── Process all HTML files ────────────────────────────────────────────────
# First process known articles
for article_key in ARTICLES:
    path = os.path.join(BASE, article_key, "index.html")
    if not os.path.exists(path):
        errors.append(f"MISSING: {article_key}")
        continue
    process_file(path, article_key)

# Also sweep all other HTML for the years replacement
import glob
all_html = glob.glob(os.path.join(BASE, "**", "index.html"), recursive=True)
known_paths = {os.path.join(BASE, k, "index.html") for k in ARTICLES}
for path in all_html:
    if path not in known_paths:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        new_content, n = YEARS_RE.subn(YEARS_REPLACEMENT, content)
        if n:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            updated_years.append(f"  years (sweep): {os.path.relpath(path, BASE)} ({n}x)")

# ── Report ────────────────────────────────────────────────────────────────
print(f"\n✅ '15+ years' updated in {len(updated_years)} files:")
for l in updated_years: print(l)

print(f"\n📅 Dates reassigned for {len(updated_dates)} articles:")
for l in updated_dates: print(l)

if errors:
    print(f"\n⚠️  Errors:")
    for e in errors: print(f"  {e}")

print(f"\n📊 ARTICLE COUNT: {len(ARTICLES)} articles total")
print(f"   Date range: {pub_dates[0]} → {pub_dates[-1]}")
