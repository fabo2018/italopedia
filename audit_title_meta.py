#!/usr/bin/env python3
"""
Audit title tag e meta description su tutti i file HTML di Italopedia.
Output: audit_title_meta.csv con tutti i problemi trovati + priorità fix.
"""

import os
import re
import csv
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).parent

# Sezioni che contengono articoli reali (escludi pagine di servizio)
ARTICLE_SECTIONS = {
    "visas", "residency", "taxes", "regions", "property",
    "healthcare", "cost-of-living", "citizenship"
}

# Pagine di servizio: non controllare keyword Italy/anno
SERVICE_PAGES = {
    "404.html", "checkout/index.html", "cookie-policy/index.html",
    "cookies/index.html", "contact/index.html", "privacy-policy/index.html",
    "privacy/index.html", "terms/index.html", "affiliate-disclosure/index.html",
    "disclaimer/index.html", "thank-you/index.html", "resources/index.html",
    "checklist/index.html", "newsletter/index.html",
}

TITLE_MIN = 30
TITLE_MAX = 65
DESC_MIN  = 100
DESC_MAX  = 165

CURRENT_YEAR = "2025"
BRAND_SUFFIX = "— Italopedia"

class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.desc  = ""
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

def extract_meta(html: str) -> tuple[str, str]:
    parser = MetaParser()
    parser.feed(html)
    return parser.title.strip(), parser.desc.strip()

def is_service(rel_path: str) -> bool:
    return rel_path in SERVICE_PAGES or rel_path.startswith(("about/", "consult/"))

def check_title(title: str, url: str, rel_path: str) -> list[str]:
    issues = []
    if not title:
        return ["MISSING title"]
    ln = len(title)
    if ln < TITLE_MIN:
        issues.append(f"TOO SHORT ({ln} chars, min {TITLE_MIN})")
    if ln > TITLE_MAX:
        issues.append(f"TOO LONG ({ln} chars, max {TITLE_MAX})")

    service = is_service(rel_path)
    if not service:
        # "italy" OR "italian" (catches both Italy and Italian)
        if "ital" not in title.lower():
            issues.append("NO Italy/Italian keyword")
        # Year check for article pages only (not hub index pages)
        top_dir = rel_path.split("/")[0]
        is_hub = (rel_path == top_dir + "/index.html") and top_dir in ARTICLE_SECTIONS
        is_root = rel_path == "index.html"
        if not is_hub and not is_root:
            if CURRENT_YEAR not in title and "2024" not in title:
                issues.append(f"No year ({CURRENT_YEAR}) in title")

    if BRAND_SUFFIX not in title:
        issues.append(f"Missing brand suffix '{BRAND_SUFFIX}'")
    return issues

def check_desc(desc: str, rel_path: str) -> list[str]:
    issues = []
    if not desc:
        # Service pages senza description: solo MEDIUM
        if is_service(rel_path):
            return ["MISSING description (service page)"]
        return ["MISSING description"]
    ln = len(desc)
    if ln < DESC_MIN:
        issues.append(f"TOO SHORT ({ln} chars, min {DESC_MIN})")
    if ln > DESC_MAX:
        issues.append(f"TOO LONG ({ln} chars, max {DESC_MAX})")
    if not is_service(rel_path) and "ital" not in desc.lower():
        issues.append("NO Italy/Italian in description")
    return issues

def priority(title_issues: list[str], desc_issues: list[str]) -> str:
    all_issues = title_issues + desc_issues
    if not all_issues:
        return "OK"
    critical = ["MISSING", "TOO SHORT", "NO 'Italy'"]
    for kw in critical:
        if any(kw in i for i in all_issues):
            return "HIGH"
    return "MEDIUM"

def get_url(path: Path) -> str:
    rel = path.relative_to(ROOT)
    parts = rel.parts
    if parts[-1] == "index.html":
        url = "/" + "/".join(parts[:-1]) + "/"
    else:
        url = "/" + "/".join(parts)
    return url

def is_article(path: Path) -> bool:
    """True se il file è un articolo o hub page, False se è pagina di servizio."""
    rel = str(path.relative_to(ROOT))
    top_dir = rel.split("/")[0]
    return top_dir in ARTICLE_SECTIONS or rel in ("index.html",)

def main():
    html_files = sorted(ROOT.glob("**/*.html"))

    rows = []
    for path in html_files:
        html = path.read_text(encoding="utf-8", errors="replace")
        title, desc = extract_meta(html)
        url = get_url(path)
        rel = str(path.relative_to(ROOT))

        t_issues = check_title(title, url, rel)
        d_issues = check_desc(desc, rel)
        pri = priority(t_issues, d_issues)

        # Declassa service pages a MEDIUM al massimo
        if is_service(rel) and pri == "HIGH":
            pri = "MEDIUM"

        rows.append({
            "priority":     pri,
            "url":          url,
            "file":         rel,
            "title":        title,
            "title_len":    len(title),
            "title_issues": " | ".join(t_issues) if t_issues else "",
            "desc":         desc,
            "desc_len":     len(desc),
            "desc_issues":  " | ".join(d_issues) if d_issues else "",
        })

    # Ordina: HIGH prima, poi MEDIUM, poi OK — e per URL
    order = {"HIGH": 0, "MEDIUM": 1, "OK": 2}
    rows.sort(key=lambda r: (order[r["priority"]], r["url"]))

    out = ROOT / "audit_title_meta.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    # Stampa summary
    total  = len(rows)
    high   = sum(1 for r in rows if r["priority"] == "HIGH")
    medium = sum(1 for r in rows if r["priority"] == "MEDIUM")
    ok     = sum(1 for r in rows if r["priority"] == "OK")

    print(f"Audit completato: {total} file HTML analizzati")
    print(f"  HIGH   (fix urgente): {high}")
    print(f"  MEDIUM (migliorabile): {medium}")
    print(f"  OK     (nessun problema): {ok}")
    print(f"\nReport salvato in: {out}")

    # Dettaglio problemi più comuni
    all_t = [r["title_issues"] for r in rows if r["title_issues"]]
    all_d = [r["desc_issues"]  for r in rows if r["desc_issues"]]

    print("\n--- Problemi titoli più frequenti ---")
    from collections import Counter
    t_counter = Counter()
    d_counter = Counter()
    for r in rows:
        for issue in r["title_issues"].split(" | "):
            if issue: t_counter[issue] += 1
        for issue in r["desc_issues"].split(" | "):
            if issue: d_counter[issue] += 1

    for issue, count in t_counter.most_common(10):
        print(f"  {count:3d}x  {issue}")

    print("\n--- Problemi meta description più frequenti ---")
    for issue, count in d_counter.most_common(10):
        print(f"  {count:3d}x  {issue}")

if __name__ == "__main__":
    main()
