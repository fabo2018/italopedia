#!/usr/bin/env python3
"""
Italopedia — Internal linking + shop product CTAs.

What this script does:
  OLD articles (div.related-section, 3 links):
    - Adds 2 more related articles → 5 total
    - Adds a shop product CTA before </article>
  NEW articles (aside.article-related, 4 links):
    - Adds a shop product CTA before the existing article-cta div
  ORPHAN (jure-sanguinis, 0 links):
    - Creates full related section + shop CTA

Usage:
  python3 fix_internal_links.py           # dry-run
  python3 fix_internal_links.py --apply   # apply changes
"""

import sys
import re
import csv
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).parent
DRY_RUN = "--apply" not in sys.argv
ARTICLE_SECTIONS = {"visas","residency","taxes","regions","property","healthcare","cost-of-living","citizenship"}

# ── Shop products ───────────────────────────────────────────────────────────
STRIPE = {
    "visa-bundle":      "9B600icgQgqn5FU9f2bsc05",
    "jure-sanguinis":   "dRm28q1Cc6PN8S6bnabsc03",
    "tax-guide":        "cNi7sKft24HF9Wa9f2bsc04",
    "buying-property":  "00waEWa8Ib632tIdvibsc02",
    "first-90-days":    "00w7sKbcM2zx0lAfDqbsc06",
    "where-to-live":    "fZucN4a8Ia1Z5FU8aYbsc01",
    "all-access-bundle":"8x23cubcM1vtd8m8aYbsc00",
}

SECTION_PRODUCT = {
    "visas":         ("Complete Italy Visa Bundle",           "49",  "visa-bundle"),
    "residency":     ("First 90 Days in Italy Pack",          "24",  "first-90-days"),
    "taxes":         ("US-Italy Tax Survival Guide",          "29",  "tax-guide"),
    "property":      ("Buying Property in Italy",             "35",  "buying-property"),
    "healthcare":    ("First 90 Days in Italy Pack",          "24",  "first-90-days"),
    "citizenship":   ("Jure Sanguinis Master Pack",           "39",  "jure-sanguinis"),
    "regions":       ("Where to Live in Italy: 20 Cities",    "19",  "where-to-live"),
    "cost-of-living":("All-Access Bundle",                    "129", "all-access-bundle"),
}

SECTION_DISPLAY = {
    "visas": "Visas", "residency": "Residency", "taxes": "Taxes",
    "property": "Property", "healthcare": "Healthcare", "citizenship": "Citizenship",
    "regions": "Regions", "cost-of-living": "Cost of Living",
}

# ── Related article priority lists ──────────────────────────────────────────
# Each list is ordered by importance; the script picks the first ones not
# already linked from each article.

SECTION_PRIORITY = {
    "visas": [
        "elective-residence-visa",
        "digital-nomad-visa",
        "italy-visa-income-requirements-2025-all-types",
        "italy-spouse-visa-americans",
        "italy-investor-visa-golden-visa-americans",
        "fbi-background-check-italian-visa-americans",
        "apostille-document-translation-italian-visa",
        "italy-student-visa",
        "etias-americans-italy-schengen-guide",
        "self-employment-visa-italy",
        "health-insurance-italian-visa",
        "90-180-schengen-rule-calculator",
        "how-to-apply-italy-visa-usa",
        "dual-us-italian-citizens-visa",
        "italy-visa-rejection-how-to-appeal",
    ],
    "residency": [
        "permesso-di-soggiorno",
        "how-to-get-codice-fiscale-italy-americans",
        "how-to-register-anagrafe-italy-americans",
        "spid-italy-foreigners-americans-guide",
        "permesso-di-soggiorno-renewal-americans-guide",
        "permesso-lungo-periodo-permanent-residency-italy",
        "tessera-sanitaria-expats",
        "open-italian-bank-account",
        "italian-drivers-license-americans",
        "getting-sim-card-italy-americans-guide",
        "declaring-presence-8-day-rule-italy-americans",
        "register-foreign-car-italy",
        "pec-email-italy",
        "marca-da-bollo-italy",
        "changing-visa-type-italy",
        "registering-foreign-marriage-italy",
        "italian-civil-union-unione-civile",
    ],
    "taxes": [
        "flat-tax-regime",
        "irpef-tax-brackets-italy-2025-americans",
        "us-italy-tax-treaty-double-taxation",
        "fbar-fatca-americans-italy-guide",
        "southern-italy-7-percent-flat-tax-foreign-pensioners",
        "us-italy-social-security-totalization-agreement",
        "partita-iva-italy-foreigners",
        "tax-residency-italy-when-liable",
        "capital-gains-tax-italy",
        "imu-property-tax-italy",
        "inheritance-gift-tax-italy",
        "foreign-tax-credit-vs-feie-italy",
        "cryptocurrency-tax-italy-2025",
        "401k-ira-withdrawals-italy-resident",
        "roth-ira-italy-tax-implications",
        "italian-tax-year-calendar",
        "find-commercialista-us-tax-italy",
    ],
    "property": [
        "how-to-buy-property-italy-american-guide",
        "1-euro-house-italy",
        "mortgages-non-residents-italy",
        "italian-notary-process",
        "renting-apartment-italy-expat-guide",
        "best-cities-invest-property-italy",
        "compromesso-preliminary-contract-italy",
        "property-purchase-taxes-italy",
        "renting-out-property-italy-cedolare-secca",
        "renovating-italian-stone-house",
        "buying-property-puglia",
        "italian-lease-types-explained",
        "short-term-rentals-italy-rules",
    ],
    "healthcare": [
        "enroll-italian-ssn",
        "best-health-insurance-americans-italy",
        "tessera-sanitaria-italy-health-card-americans",
        "best-private-health-insurance-italy-americans-2025",
        "cigna-vs-axa-vs-allianz-italy",
        "english-speaking-doctors-italy",
        "specialist-visits-italy-referral",
        "emergency-room-italy-pronto-soccorso",
        "dental-care-italy-americans",
        "mental-health-care-italy",
        "chronic-conditions-italy-expats",
        "top-private-hospitals-italy",
    ],
    "citizenship": [
        "jure-sanguinis",
        "italian-citizenship-by-marriage",
        "citizenship-court-vs-consulate-route",
        "italian-citizenship-10-years-residency-naturalization",
        "italian-citizenship-1948-case",
        "apostille-document-translation-italy",
        "jure-sanguinis-document-checklist",
        "b1-italian-language-requirement",
        "aire-registration-italians-abroad",
        "italian-passport-application",
        "2024-italian-citizenship-reform",
    ],
    "regions": [
        "best-cities-american-expats-italy",
        "florence-vs-rome-vs-bologna",
        "best-small-towns-italy-retirees",
        "living-rome-american-expat",
        "living-florence-american-expat",
        "living-in-tuscany-american-expat",
        "sicily-american-expats-guide",
        "quietest-regions-italy",
        "best-cities-remote-workers-italy",
        "best-italian-cities-families",
        "living-veneto-venice-verona",
        "living-puglia-american-expat",
        "living-sardinia-american-expat",
        "best-coastal-towns-italy-year-round",
        "test-living-italy-before-moving",
    ],
    "cost-of-living": [
        "cost-of-living-italy-vs-usa",
        "living-italy-2500-month",
        "retire-italy-2000-month-budget",
        "cost-of-living-milan",
        "cost-of-living-turin-american-expats-2025",
        "healthcare-costs-italy-vs-usa",
        "italy-rent-prices-city-comparison",
        "grocery-costs-italy-by-city",
        "hidden-costs-living-italy",
        "cost-of-living-bologna",
        "cost-of-living-lecce",
        "italy-vs-spain-vs-portugal-cost",
    ],
}

# Cross-section "next step" links (section → [section/slug, ...])
CROSS_SECTION = {
    "visas":         ["residency/permesso-di-soggiorno",
                      "residency/how-to-get-codice-fiscale-italy-americans",
                      "taxes/flat-tax-regime"],
    "residency":     ["visas/elective-residence-visa",
                      "taxes/irpef-tax-brackets-italy-2025-americans",
                      "healthcare/enroll-italian-ssn"],
    "taxes":         ["residency/permesso-di-soggiorno",
                      "visas/elective-residence-visa",
                      "residency/spid-italy-foreigners-americans-guide"],
    "property":      ["cost-of-living/cost-of-living-italy-vs-usa",
                      "residency/permesso-di-soggiorno",
                      "taxes/imu-property-tax-italy"],
    "healthcare":    ["residency/tessera-sanitaria-expats",
                      "visas/health-insurance-italian-visa",
                      "residency/permesso-di-soggiorno"],
    "citizenship":   ["residency/permesso-di-soggiorno",
                      "visas/elective-residence-visa",
                      "taxes/flat-tax-regime"],
    "regions":       ["cost-of-living/cost-of-living-italy-vs-usa",
                      "property/how-to-buy-property-italy-american-guide",
                      "residency/permesso-di-soggiorno"],
    "cost-of-living":["regions/best-cities-american-expats-italy",
                      "property/how-to-buy-property-italy-american-guide",
                      "visas/elective-residence-visa"],
}


# ── Build article catalog ───────────────────────────────────────────────────

def card_title_from_html(html: str) -> str:
    """Short display title: <title> minus '— Italopedia' and year."""
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.DOTALL)
    if m:
        t = m.group(1).strip()
        t = t.replace(" — Italopedia", "").replace(" (2025)", "").replace(" (2024)", "").strip()
        return t
    return ""

def build_catalog() -> dict:
    """Returns {section/slug: {section, slug, title, file, html}}"""
    cat = {}
    for path in ROOT.glob("**/*.html"):
        rel = str(path.relative_to(ROOT))
        parts = rel.split("/")
        top = parts[0]
        if top not in ARTICLE_SECTIONS or len(parts) != 3:
            continue
        html = path.read_text(encoding="utf-8", errors="replace")
        key = f"{top}/{parts[1]}"
        cat[key] = {
            "section": top,
            "slug":    parts[1],
            "title":   card_title_from_html(html),
            "file":    path,
            "html":    html,
        }
    return cat


# ── Related link helpers ────────────────────────────────────────────────────

def get_related_title(related_title: str) -> str:
    return related_title.replace(" — Italopedia","").replace(" (2025)","").strip()

def existing_slugs_in_related(html: str, section: str) -> set:
    """Extract slugs already in the related section block."""
    # Find related-section or article-related
    pattern = re.search(
        r'(?:class="related-section"|class="article-related").*?(?:</div></div>|</aside>)',
        html, re.DOTALL
    )
    if not pattern:
        return set()
    block = pattern.group(0)
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', block)
    slugs = set()
    for h in hrefs:
        # Extract slug from relative URL like ../slug/ or ../../section/slug/
        parts = [p for p in h.strip("/").split("/") if p and p != ".."]
        if parts:
            slugs.add(parts[-1])
    return slugs

def relative_url(from_section: str, to_key: str) -> str:
    """Build relative URL from a depth-2 article to another article key."""
    to_section, to_slug = to_key.split("/", 1)
    if to_section == from_section:
        return f"../{to_slug}/"
    return f"../../{to_section}/{to_slug}/"

def pick_related(section: str, current_slugs: set, catalog: dict, need: int) -> list:
    """Return list of (key, title) pairs to add, avoiding current_slugs."""
    candidates = []

    # Same-section priority articles
    for slug in SECTION_PRIORITY.get(section, []):
        key = f"{section}/{slug}"
        if slug not in current_slugs and key in catalog:
            candidates.append(key)

    # Cross-section articles
    for cross_key in CROSS_SECTION.get(section, []):
        slug = cross_key.split("/")[-1]
        full_key = cross_key.replace("/", "/", 1)  # already 'section/slug'
        if slug not in current_slugs and full_key in catalog:
            candidates.append(full_key)

    # De-dup preserving order
    seen = set()
    unique = []
    for k in candidates:
        if k not in seen:
            seen.add(k)
            unique.append(k)

    result = []
    for key in unique:
        if len(result) >= need:
            break
        result.append((key, catalog[key]["title"]))
    return result

def shop_cta_html(section: str, prefix: str = "../../") -> str:
    """Build the shop product CTA HTML block."""
    name, price, product_id = SECTION_PRODUCT[section]
    stripe_hash = STRIPE[product_id]
    url = (f"{prefix}checkout/?product={product_id}"
           f"&amp;price={price}"
           f"&amp;link=https://buy.stripe.com/{stripe_hash}")
    return (
        f'\n<div class="shop-cta">'
        f'<div class="shop-cta-inner">'
        f'<strong>{name}</strong> — '
        f'<a href="{url}" class="shop-cta-link">'
        f'Get the guide for ${price} →</a>'
        f'</div></div>'
    )


# ── Old-article patcher ─────────────────────────────────────────────────────

def patch_old_article(html: str, section: str, slug: str, catalog: dict) -> tuple[str, str]:
    """
    Expands related-section from 3 to 5 links and adds shop CTA.
    Returns (new_html, change_description).
    """
    changes = []

    # ── 1. Expand related section ──
    rs_match = re.search(
        r'(<div class="related-section">.*?<div class="related-grid">)(.*?)(</div></div>)',
        html, re.DOTALL
    )
    if rs_match:
        existing_block = rs_match.group(2)
        # Count existing cards
        existing_links = re.findall(r'<a href=["\']([^"\']+)["\']', existing_block)
        existing_slugs = {h.strip("/").split("/")[-1] for h in existing_links}
        # Also add current article itself to avoid self-links
        existing_slugs.add(slug)

        n_existing = len(existing_links)
        need = max(0, 5 - n_existing)

        if need > 0:
            new_cards = pick_related(section, existing_slugs, catalog, need)
            extra_html = ""
            for key, title in new_cards:
                url = relative_url(section, key)
                target_section = key.split("/")[0]
                cat_label = SECTION_DISPLAY.get(target_section, target_section.title())
                card_title = get_related_title(title)
                extra_html += (
                    f'<a href="{url}" class="related-card">'
                    f'<div class="related-cat">{cat_label}</div>'
                    f'<div class="related-card-title">{card_title}</div></a>'
                )
            new_block = rs_match.group(1) + existing_block + extra_html + rs_match.group(3)
            html = html[:rs_match.start()] + new_block + html[rs_match.end():]
            changes.append(f"+{len(new_cards)} related links")

    # ── 2. Add shop CTA before </article> ──
    # Only if no checkout link already in the body (article-body area)
    body_match = re.search(r'class="article-body">(.*?)</article>', html, re.DOTALL)
    body_area = body_match.group(1) if body_match else ""
    if "checkout" not in body_area:
        cta = shop_cta_html(section)
        html = html.replace("</article>", cta + "\n  </article>", 1)
        name, price, _ = SECTION_PRODUCT[section]
        changes.append(f"shop CTA: {name} ${price}")

    return html, " | ".join(changes)


# ── New-article patcher ─────────────────────────────────────────────────────

def patch_new_article(html: str, section: str, catalog: dict) -> tuple[str, str]:
    """
    Adds shop product CTA before article-cta div (new article format).
    Returns (new_html, change_description).
    """
    # Don't add if already has a checkout link in the article area
    # (exclude nav and footer which always have shop/)
    main_idx = html.find('class="article-body"')
    if main_idx < 0:
        main_idx = html.find('<main')
    body_area = html[main_idx:] if main_idx >= 0 else html

    # Strip nav/footer from check
    footer_idx = body_area.find('<footer')
    if footer_idx >= 0:
        body_area = body_area[:footer_idx]

    if "checkout" in body_area:
        return html, "already has shop link"

    cta = shop_cta_html(section)
    # Insert before <div class="article-cta"> or before </main>
    if '<div class="article-cta">' in html:
        html = html.replace('<div class="article-cta">', cta + '\n<div class="article-cta">', 1)
    elif '</main>' in html:
        html = html.replace('</main>', cta + '\n</main>', 1)
    else:
        return html, "no insertion point found"

    name, price, _ = SECTION_PRODUCT[section]
    return html, f"shop CTA: {name} ${price}"


# ── Orphan patcher (jure-sanguinis) ─────────────────────────────────────────

def patch_orphan(html: str, section: str, slug: str, catalog: dict) -> tuple[str, str]:
    """Add full related section + shop CTA to an article that has neither."""
    related_keys = pick_related(section, {slug}, catalog, 5)
    cards_html = ""
    for key, title in related_keys:
        url = relative_url(section, key)
        target_section = key.split("/")[0]
        cat_label = SECTION_DISPLAY.get(target_section, target_section.title())
        card_title = get_related_title(title)
        cards_html += (
            f'<a href="{url}" class="related-card">'
            f'<div class="related-cat">{cat_label}</div>'
            f'<div class="related-card-title">{card_title}</div></a>'
        )

    related_block = (
        '\n    <div class="related-section">'
        '<div class="related-title">Continue reading</div>\n'
        '      <div class="related-grid">\n'
        + cards_html +
        '\n      </div></div>'
    )
    cta = shop_cta_html(section)
    insert = related_block + cta + "\n  </article>"
    html = html.replace("</article>", insert, 1)
    return html, f"new related section ({len(related_keys)} links) + shop CTA"


# ── Article type detector ────────────────────────────────────────────────────

def article_type(html: str) -> str:
    """Return 'old', 'new', 'orphan', or 'skip'."""
    if 'class="related-section"' in html:
        return "old"
    if 'class="article-related"' in html:
        return "new"
    if "<article" in html or 'class="article-body"' in html:
        return "orphan"
    return "skip"


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    catalog = build_catalog()
    print(f"Catalog: {len(catalog)} articles")

    log = []
    changed = 0

    for key, art in sorted(catalog.items()):
        html   = art["html"]
        section = art["section"]
        slug    = art["slug"]
        atype   = article_type(html)

        if atype == "skip":
            continue

        if atype == "old":
            new_html, desc = patch_old_article(html, section, slug, catalog)
        elif atype == "new":
            new_html, desc = patch_new_article(html, section, catalog)
        elif atype == "orphan":
            new_html, desc = patch_orphan(html, section, slug, catalog)
        else:
            continue

        if new_html == html:
            continue

        log.append({"url": f"/{key}/", "type": atype, "changes": desc})

        if not DRY_RUN:
            art["file"].write_text(new_html, encoding="utf-8")
            changed += 1

    # Output
    mode = "DRY-RUN" if DRY_RUN else "APPLIED"
    print(f"[{mode}] {len(log)} articles modified")
    if not DRY_RUN:
        print(f"  {changed} files written")

    old_cnt = sum(1 for r in log if r["type"] == "old")
    new_cnt = sum(1 for r in log if r["type"] == "new")
    orp_cnt = sum(1 for r in log if r["type"] == "orphan")
    print(f"  old-style: {old_cnt}  new-style: {new_cnt}  orphan: {orp_cnt}")
    print()

    for r in log:
        print(f"  [{r['type']:6}] {r['url']:<55} {r['changes']}")

    if log:
        out = ROOT / "fix_internal_links_log.csv"
        with open(out, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=log[0].keys())
            writer.writeheader()
            writer.writerows(log)
        print(f"\nLog: {out}")


if __name__ == "__main__":
    main()
