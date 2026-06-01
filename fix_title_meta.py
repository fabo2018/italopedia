#!/usr/bin/env python3
"""
Fix automatico title tag e meta description su tutti i file HTML di Italopedia.
Uso: python3 fix_title_meta.py           → dry-run (mostra cambiamenti)
     python3 fix_title_meta.py --apply   → applica le modifiche
"""

import sys
import re
import csv
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).parent
DRY_RUN = "--apply" not in sys.argv
MAX_TITLE = 65
MAX_DESC = 162  # trim point; with "..." = 165

BRAND = " — Italopedia"

TITLE_OVERRIDES = {
    "/":
        "Italopedia — Move to Italy: The Complete Guide for Americans",
    "/healthcare/enroll-italian-ssn/":
        "How to Enroll in Italy's SSN (2025) — Italopedia",
    "/citizenship/citizenship-court-vs-consulate-route/":
        "Italian Citizenship: Court vs Consulate Route (2025) — Italopedia",
    "/visas/italy-investor-visa-golden-visa-americans/":
        "Italy Investor Visa (Golden Visa) (2025) — Italopedia",
    "/taxes/flat-tax-regime/":
        "Italy's €100,000 Flat Tax Regime for New Residents — Italopedia",
    "/cost-of-living/":
        "Cost of Living in Italy for Americans (2025) — Italopedia",
    "/cost-of-living/grocery-costs-italy-by-city/":
        "Grocery Costs in Italy by City (2025) — Italopedia",
    "/cost-of-living/healthcare-costs-italy-vs-usa/":
        "Healthcare Costs in Italy vs USA (2025) — Italopedia",
    "/cost-of-living/cost-of-living-milan/":
        "Cost of Living in Milan for Americans (2025) — Italopedia",
    "/visas/elective-residence-visa/":
        "Elective Residence Visa Italy (2025) — Italopedia",
    "/shop/":
        "Italopedia Shop — Premium Italy Guides for Americans — Italopedia",
    "/healthcare/tessera-sanitaria-italy-health-card-americans/":
        "Tessera Sanitaria: Italy's Health Card (2025) — Italopedia",
    "/cost-of-living/cost-of-living-italy-vs-usa/":
        "Cost of Living: Italy vs USA (2025) — Italopedia",
}


class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.desc = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            d = dict(attrs)
            if d.get("name", "").lower() == "description":
                self.desc = d.get("content", "")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def extract_meta(html):
    p = MetaParser()
    try:
        p.feed(html)
    except Exception:
        pass
    return p.title.strip(), p.desc.strip()


def get_url(path):
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if parts[-1] == "index.html":
        return "/" + "/".join(parts[:-1]) + "/" if len(parts) > 1 else "/"
    return "/" + "/".join(parts)


def shorten_title(title, url):
    if url in TITLE_OVERRIDES:
        return TITLE_OVERRIDES[url]
    if len(title) <= MAX_TITLE:
        return title
    if not title.endswith(BRAND):
        return title

    core = title[:-len(BRAND)]
    ym = re.search(r' \(20\d{2}\)$', core)
    year = ""
    if ym:
        year = ym.group(0)
        core = core[:ym.start()]

    def build(c):
        return c + year + BRAND

    def fits(c):
        return c and len(c) >= 15 and len(build(c)) <= MAX_TITLE

    if ':' in core:
        main, sub = core.split(':', 1)
        main, sub = main.strip(), sub.strip()

        # A: remove "for Americans" from subtitle only
        sub_a = re.sub(r'\s+for Americans?(?:\s+(?:Expats?|Living in Italy|Expat))?', '', sub).strip()
        sub_a = re.sub(r'\s+as an Americans?(?:\s+Expat)?', '', sub_a).strip()
        if sub_a != sub:
            ca = main + ': ' + sub_a if sub_a else main
            if fits(ca):
                return build(ca)

        # B: drop entire subtitle (keep "for Americans" in main if present)
        if fits(main):
            return build(main)

        # C: also strip "for Americans" from main
        main_c = re.sub(r'\s+for Americans?(?:\s+(?:Expats?|Living in Italy|Expat))?', '', main).strip()
        main_c = re.sub(r'\s+as an Americans?(?:\s+Expat)?', '', main_c).strip()
        if fits(main_c):
            return build(main_c)

    # No colon — try removing secondary dash segment
    c_dash = re.sub(r' — .+$', '', core).strip()
    if fits(c_dash):
        return build(c_dash)

    # Remove "for Americans" from full core
    c_no_amer = re.sub(r'\s+for Americans?(?:\s+(?:Expats?|Living in Italy|Expat))?', '', core).strip()
    c_no_amer = re.sub(r'\s+as an Americans?(?:\s+Expat)?', '', c_no_amer).strip()
    if fits(c_no_amer):
        return build(c_no_amer)

    # Hard truncate
    max_core = MAX_TITLE - len(year) - len(BRAND)
    truncated = core[:max_core].rsplit(' ', 1)[0].rstrip(':,— ').strip()
    return build(truncated) if truncated else title


def trim_desc(desc):
    if len(desc) <= MAX_DESC:
        return desc
    chunk = desc[:MAX_DESC]
    # Try sentence boundary
    for pat in [r'\. ', r'\? ', r'! ']:
        last = None
        for m in re.finditer(re.escape(pat[0]) + r' ', chunk):
            last = m
        if last and last.start() > MAX_DESC * 0.65:
            return desc[:last.start() + 1]
    # Word boundary + ellipsis
    sp = chunk.rfind(' ')
    return (chunk[:sp] if sp > 0 else chunk) + "..."


def replace_title_in_html(html, old_title, new_title):
    pat = re.compile(r'(<title[^>]*>)(.*?)(</title>)', re.IGNORECASE | re.DOTALL)
    m = pat.search(html)
    if m and m.group(2).strip() == old_title:
        return html[:m.start()] + m.group(1) + new_title + m.group(3) + html[m.end():], True
    return html, False


def replace_desc_in_html(html, new_desc):
    name_m = re.search(r"""name=['"]description['"]""", html, re.IGNORECASE)
    if not name_m:
        return html, False
    tag_start = html.rfind('<meta', 0, name_m.start())
    if tag_start < 0:
        return html, False
    tag_end_rel = html.find('/>', tag_start)
    if tag_end_rel < 0:
        tag_end_rel = html.find('>', tag_start)
        if tag_end_rel < 0:
            return html, False
        tag_end = tag_end_rel + 1
    else:
        tag_end = tag_end_rel + 2
    safe_desc = new_desc.replace('"', '&quot;')
    new_tag = f'<meta name="description" content="{safe_desc}"/>'
    return html[:tag_start] + new_tag + html[tag_end:], True


def main():
    files = sorted(ROOT.glob("**/*.html"))
    log = []
    changed = 0

    for path in files:
        html = path.read_text(encoding="utf-8", errors="replace")
        url = get_url(path)
        old_title, old_desc = extract_meta(html)

        new_title = shorten_title(old_title, url)
        new_desc = trim_desc(old_desc) if old_desc else old_desc

        title_changed = new_title != old_title
        desc_changed = new_desc != old_desc

        if not title_changed and not desc_changed:
            continue

        log.append({
            "url":           url,
            "title_old":     old_title,
            "title_new":     new_title if title_changed else "",
            "title_len_old": len(old_title),
            "title_len_new": len(new_title) if title_changed else "",
            "desc_old":      old_desc[:80] + "..." if len(old_desc) > 80 else old_desc,
            "desc_new":      new_desc[:80] + "..." if new_desc and len(new_desc) > 80 else (new_desc or ""),
            "desc_len_old":  len(old_desc),
            "desc_len_new":  len(new_desc) if desc_changed else "",
        })

        if not DRY_RUN:
            new_html = html
            if title_changed:
                new_html, ok = replace_title_in_html(new_html, old_title, new_title)
                if not ok:
                    print(f"  WARNING: title replacement failed for {url}")
                    title_changed = False
            if desc_changed:
                new_html, ok = replace_desc_in_html(new_html, new_desc)
                if not ok:
                    print(f"  WARNING: desc replacement failed for {url}")
                    desc_changed = False
            if title_changed or desc_changed:
                path.write_text(new_html, encoding="utf-8")
                changed += 1

    out_csv = ROOT / "fix_title_meta_log.csv"
    if log:
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=log[0].keys())
            writer.writeheader()
            writer.writerows(log)

    mode = "DRY-RUN" if DRY_RUN else "APPLIED"
    print(f"[{mode}] {len(log)} file con cambiamenti rilevati")
    if not DRY_RUN:
        print(f"  {changed} file modificati su disco")
    print(f"  Log: {out_csv}")
    print()

    print(f"{'URL':<55} {'OLD':>4} {'NEW':>4}  TITLE")
    print("-" * 90)
    for r in log:
        if r["title_new"]:
            print(f"  {r['url']:<53} {r['title_len_old']:>3}→{r['title_len_new']:>3}  {r['title_new']}")
        if r["desc_new"]:
            print(f"  {'  DESC':53} {r['desc_len_old']:>3}→{r['desc_len_new']:>3}  {r['desc_new'][:60]}")


if __name__ == "__main__":
    main()
