#!/usr/bin/env python3
"""Generate Batch 4A articles from markdown files."""

import os, re, markdown as md_lib

CONTENT_DIR = os.path.expanduser("~/Desktop/ITALOPEDIA DEFINITIVO/03-content")
OUT_DIR = os.path.expanduser("~/italopedia")

NAV_LINKS = {
    "visas":        "Visas",
    "residency":    "Residency",
    "taxes":        "Taxes",
    "healthcare":   "Healthcare",
    "property":     "Property",
    "citizenship":  "Citizenship",
    "regions":      "Regions",
    "cost-of-living": "Cost of Living",
}

FOOTER_HTML = """\
<footer class="footer"><div class="footer-inner">
    <div class="footer-top">
      <div class="footer-brand-col">
        <a href="../../" class="footer-logo">Italo<span>pedia</span></a>
        <p class="footer-brand-desc">The complete English-language reference for Americans moving to and living in Italy. Written from a small town in Piedmont, verified against official Italian sources.</p>
        <span class="footer-stamp">📍 Piedmont, Italy</span>
      </div>
      <div><div class="footer-col-title">Categories</div><ul class="footer-links">
        <li><a href="../../visas/">Visas</a></li><li><a href="../../residency/">Residency</a></li>
        <li><a href="../../taxes/">Taxes</a></li><li><a href="../../healthcare/">Healthcare</a></li>
        <li><a href="../../property/">Property</a></li><li><a href="../../citizenship/">Citizenship</a></li>
        <li><a href="../../regions/">Regions</a></li><li><a href="../../cost-of-living/">Cost of Living</a></li>
      </ul></div>
      <div><div class="footer-col-title">Resources</div><ul class="footer-links">
        <li><a href="../../resources/">Free resources</a></li><li><a href="../../shop/">Shop guides</a></li>
        <li><a href="../../consult/">Book a 1:1 consult</a></li><li><a href="../../newsletter/">Newsletter</a></li>
        <li><a href="../../checklist/">Free checklist</a></li><li><a href="../../about/">About</a></li>
      </ul></div>
      <div><div class="footer-col-title">Popular guides</div><ul class="footer-links">
        <li><a href="../../visas/elective-residence-visa/">Elective Residence Visa</a></li>
        <li><a href="../../taxes/flat-tax-regime/">Italian Flat Tax</a></li>
        <li><a href="../../citizenship/jure-sanguinis/">Citizenship by Descent</a></li>
        <li><a href="../../residency/permesso-di-soggiorno/">Permesso di Soggiorno</a></li>
        <li><a href="../../cost-of-living/">Cost of Living</a></li>
      </ul></div>
    </div>
    <div class="footer-bottom">
      <div class="footer-copy">© <span data-year>2026</span> Italopedia · All rights reserved · Made with espresso in Piedmont</div>
      <div class="footer-legal">
        <a href="../../privacy/">Privacy</a><a href="../../terms/">Terms</a>
        <a href="../../cookies/">Cookies</a><a href="../../affiliate-disclosure/">Affiliate Disclosure</a>
        <a href="../../disclaimer/">Disclaimer</a>
      </div>
    </div>
  </div></footer>"""

SEARCH_HTML = """\
<div class="search-overlay" id="searchOverlay"><div class="search-box">
  <div class="search-input-wrap"><span class="search-input-icon">⌕</span>
    <input class="search-input" type="text" id="searchInput" placeholder="Search guides…" autocomplete="off"/>
    <button class="search-close" onclick="closeSearch()">✕</button></div>
  <div class="search-results" id="searchResults"></div>
  <div class="search-hint">⌘ K to open · ESC to close · ↵ to visit</div>
</div></div>
<script>window.SITE_PREFIX="../../";</script>
<script src="../../assets/js/search-index.js"></script>
<script src="../../assets/js/main.js"></script>"""


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text


def parse_frontmatter(content):
    meta = {}
    body = content
    if content.startswith('---'):
        end = content.find('\n---', 3)
        if end != -1:
            fm = content[3:end].strip()
            body = content[end+4:].strip()
            for line in fm.split('\n'):
                if ':' in line:
                    k, v = line.split(':', 1)
                    meta[k.strip()] = v.strip().strip('"')
    return meta, body


def md_to_html(body):
    """Convert markdown body to HTML with heading IDs and data-table classes."""
    extensions = ['tables', 'fenced_code', 'nl2br']
    try:
        html = md_lib.markdown(body, extensions=extensions)
    except Exception:
        html = md_lib.markdown(body, extensions=['tables'])

    # Add IDs to headings
    def add_id(m):
        level = len(m.group(1))
        text = m.group(2)
        clean = re.sub(r'<[^>]+>', '', text)
        sid = slugify(clean)
        return f'<h{level} id="{sid}">{text}</h{level}>'
    html = re.sub(r'<(h[23])>(.*?)</\1>', add_id, html, flags=re.DOTALL)

    # Add data-table class to tables
    html = html.replace('<table>', '<table class="data-table">')

    # Remove top-level h1 if present (it's used in header already)
    html = re.sub(r'<h1[^>]*>.*?</h1>\s*', '', html, count=1, flags=re.DOTALL)

    # Convert blockquotes to callout boxes
    def bq_to_callout(m):
        inner = m.group(1).strip()
        inner = re.sub(r'^<p>', '', inner)
        inner = re.sub(r'</p>$', '', inner)
        return f'<div class="callout callout-tip"><div class="callout-label">Note</div><p>{inner}</p></div>'
    html = re.sub(r'<blockquote>\s*<p>(.*?)</p>\s*</blockquote>', bq_to_callout, html, flags=re.DOTALL)

    # Wrap intro (first paragraph) with quick answer if it has key intro text
    return html


def estimate_read_time(body):
    words = len(body.split())
    minutes = max(7, round(words / 200))
    return minutes


def build_nav(category):
    parts = []
    for key, label in NAV_LINKS.items():
        active = ' active' if key == category else ''
        parts.append(f'<a href="../../{key}/" class="nav-link{active}">{label}</a>')
    return '\n      '.join(parts)


def category_label(category):
    return NAV_LINKS.get(category, category.title())


def build_article(title, description, category, slug, body_html, read_time, related_cards):
    cat_label = category_label(category)
    nav = build_nav(category)
    canonical = f"https://italopedia.com/{category}/{slug}/"
    ld = (
        f'{{"@context":"https://schema.org","@type":"Article",'
        f'"headline":"{title}",'
        f'"description":"{description}",'
        f'"datePublished":"2026-05-29","dateModified":"2026-05-29",'
        f'"author":{{"@type":"Person","name":"Fabrizio Boggio"}},'
        f'"publisher":{{"@type":"Organization","name":"Italopedia"}},'
        f'"mainEntityOfPage":"{canonical}"}}'
    )
    related_html = '\n        '.join(related_cards)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{title} — Italopedia</title>
<meta name="description" content="{description}"/>
<meta name="theme-color" content="#1a1610"/>
<link rel="canonical" href="{canonical}"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="{title} — Italopedia"/>
<meta property="og:description" content="{description}"/>
<meta property="og:url" content="{canonical}"/>
<meta property="og:site_name" content="Italopedia"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&family=Syne:wght@400;500;600;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="../../assets/css/main.css"/>
<script type="application/ld+json">{ld}</script>
<link rel="icon" type="image/svg+xml" href="../../favicon.svg"/>
</head>
<body><nav class="topnav"><div class="nav-inner">
    <a href="../../" class="nav-logo">Italo<span>pedia</span><span class="tld">.com</span></a>
    <div class="nav-links">
      {nav}
    </div>
    <div class="nav-right">
      <button class="nav-icon-btn" data-search-trigger title="Search (⌘K)">⌕</button>
      <a href="../../newsletter/" class="nav-cta">Free Guide ↓</a>
      <button class="mobile-toggle">☰</button>
    </div>
  </div></nav>
<div class="article-breadcrumb-wrap"><div class="article-breadcrumb-inner">
  <div class="breadcrumb dark">
    <a href="../../">Home</a><span class="sep">›</span>
    <a href="../../{category}/">{cat_label}</a><span class="sep">›</span>
    <span class="current">{title}</span>
  </div>
</div></div>

<div class="article-layout">
  <article class="article-main">
    <header class="article-header">
      <a class="article-cat-pill" href="../../{category}/">{cat_label}</a>
      <h1 class="article-h1">{title}</h1>
      <p class="article-dek">{description}</p>
      <div class="article-meta-bar">
        <div class="article-author-mini"><div class="av">FB</div><span>By Fabrizio Boggio</span></div>
        <span>Updated May 2026</span>
        <span>{read_time} min read</span>
        <span class="verified-badge">VERIFIED</span>
        <div class="article-share">
          <a class="share-btn" href="#" title="Email">✉</a>
          <a class="share-btn" href="#" title="Twitter">𝕏</a>
          <a class="share-btn" href="#" title="Link">⌘</a>
        </div>
      </div>
    </header>

    <div class="article-hero-img">
      <div class="ph-pattern"></div>
      <div class="ph-label">{cat_label} guide · placeholder</div>
      <span class="img-credit">Photo placeholder — drop your own</span>
    </div>

    <div class="article-body">
{body_html}
    </div>

    <div class="author-box">
      <div class="author-avatar-lg">FB</div>
      <div>
        <div class="author-name">Fabrizio Boggio · Italopedia</div>
        <div class="author-title">Living in Piedmont since 2019 · Verified against official Italian sources</div>
        <p class="author-bio">I write Italopedia from a small town in Piedmont. Every guide is researched against official Italian government sources and verified against my own lived experience in Italy.</p>
      </div>
    </div>

    <div class="related-section">
      <div class="related-title">Continue reading</div>
      <div class="related-grid">
        {related_html}
      </div>
    </div>
  </article>

  <aside class="article-sidebar">
    <div class="sidebar-box">
      <div class="sidebar-box-title">In this article</div>
      <ul class="toc-list" id="toc"></ul>
    </div>

    <div class="consult-box">
      <div class="consult-box-icon">1:1</div>
      <div class="consult-box-title">Need personal help?</div>
      <div class="consult-box-desc">A 45-min video call to review your specific situation. Walk away with a clear written plan.</div>
      <a href="../../consult/" class="consult-box-btn">Book consult · $97 →</a>
    </div>

    <div class="checklist-dl-box">
      <div class="checklist-dl-icon">↓</div>
      <div class="checklist-dl-title">Free 47-Point Italy Checklist</div>
      <div class="checklist-dl-desc">Our complete pre-move checklist. PDF, 22 pages.</div>
      <a href="../../newsletter/" class="checklist-dl-btn">Get the checklist</a>
    </div>
  </aside>
</div>
{FOOTER_HTML}
{SEARCH_HTML}
</body></html>"""


ARTICLES = [
    {
        "file": "best-health-insurance-americans-italy.md",
        "category": "healthcare",
        "slug": "best-health-insurance-americans-italy",
        "related": [
            '<a href="../../healthcare/cigna-vs-axa-vs-allianz-italy/" class="related-card"><div class="related-cat">Healthcare</div><div class="related-card-title">Cigna vs AXA vs Allianz: Full Comparison</div></a>',
            '<a href="../../healthcare/enroll-italian-ssn/" class="related-card"><div class="related-cat">Healthcare</div><div class="related-card-title">How to Enroll in Italy\'s SSN</div></a>',
            '<a href="../../healthcare/tessera-sanitaria-italy-health-card-americans/" class="related-card"><div class="related-cat">Healthcare</div><div class="related-card-title">Tessera Sanitaria: Italy\'s Health Card</div></a>',
        ],
    },
    {
        "file": "cigna-vs-axa-vs-allianz-italy.md",
        "category": "healthcare",
        "slug": "cigna-vs-axa-vs-allianz-italy",
        "related": [
            '<a href="../../healthcare/best-health-insurance-americans-italy/" class="related-card"><div class="related-cat">Healthcare</div><div class="related-card-title">Best Health Insurance for Americans in Italy</div></a>',
            '<a href="../../healthcare/enroll-italian-ssn/" class="related-card"><div class="related-cat">Healthcare</div><div class="related-card-title">How to Enroll in Italy\'s SSN</div></a>',
            '<a href="../../visas/elective-residence-visa/" class="related-card"><div class="related-cat">Visas</div><div class="related-card-title">Elective Residence Visa: Complete Guide</div></a>',
        ],
    },
    {
        "file": "enroll-italian-ssn.md",
        "category": "healthcare",
        "slug": "enroll-italian-ssn",
        "related": [
            '<a href="../../healthcare/tessera-sanitaria-italy-health-card-americans/" class="related-card"><div class="related-cat">Healthcare</div><div class="related-card-title">Tessera Sanitaria: Italy\'s Health Card</div></a>',
            '<a href="../../healthcare/best-health-insurance-americans-italy/" class="related-card"><div class="related-cat">Healthcare</div><div class="related-card-title">Best Health Insurance for Americans in Italy</div></a>',
            '<a href="../../residency/how-to-register-anagrafe-italy-americans/" class="related-card"><div class="related-cat">Residency</div><div class="related-card-title">How to Register at the Anagrafe</div></a>',
        ],
    },
    {
        "file": "italian-citizenship-by-marriage.md",
        "category": "citizenship",
        "slug": "italian-citizenship-by-marriage",
        "related": [
            '<a href="../../citizenship/jure-sanguinis/" class="related-card"><div class="related-cat">Citizenship</div><div class="related-card-title">Italian Citizenship by Descent (Jure Sanguinis)</div></a>',
            '<a href="../../citizenship/italian-citizenship-10-years-residency-naturalization/" class="related-card"><div class="related-cat">Citizenship</div><div class="related-card-title">Citizenship by Naturalization: 10-Year Guide</div></a>',
            '<a href="../../residency/permesso-di-soggiorno/" class="related-card"><div class="related-cat">Residency</div><div class="related-card-title">Permesso di Soggiorno: Complete Guide</div></a>',
        ],
    },
    {
        "file": "1-euro-house-italy.md",
        "category": "property",
        "slug": "1-euro-house-italy",
        "related": [
            '<a href="../../property/how-to-buy-property-italy-american-guide/" class="related-card"><div class="related-cat">Property</div><div class="related-card-title">How to Buy Property in Italy as an American</div></a>',
            '<a href="../../property/italian-notary-process/" class="related-card"><div class="related-cat">Property</div><div class="related-card-title">The Italian Notary Process Explained</div></a>',
            '<a href="../../regions/living-in-tuscany-american-expat/" class="related-card"><div class="related-cat">Regions</div><div class="related-card-title">Living in Tuscany as an American Expat</div></a>',
        ],
    },
    {
        "file": "italian-notary-process.md",
        "category": "property",
        "slug": "italian-notary-process",
        "related": [
            '<a href="../../property/how-to-buy-property-italy-american-guide/" class="related-card"><div class="related-cat">Property</div><div class="related-card-title">How to Buy Property in Italy as an American</div></a>',
            '<a href="../../property/mortgages-non-residents-italy/" class="related-card"><div class="related-cat">Property</div><div class="related-card-title">Italian Mortgages for Non-Residents</div></a>',
            '<a href="../../property/1-euro-house-italy/" class="related-card"><div class="related-cat">Property</div><div class="related-card-title">Italy\'s €1 House Programs: The Full Picture</div></a>',
        ],
    },
    {
        "file": "cost-of-living-italy-vs-usa.md",
        "category": "cost-of-living",
        "slug": "cost-of-living-italy-vs-usa",
        "related": [
            '<a href="../../cost-of-living/living-italy-2500-month/" class="related-card"><div class="related-cat">Cost of Living</div><div class="related-card-title">Living in Italy on $2,500/Month</div></a>',
            '<a href="../../cost-of-living/cost-of-living-turin-american-expats-2025/" class="related-card"><div class="related-cat">Cost of Living</div><div class="related-card-title">Cost of Living in Turin (2025)</div></a>',
            '<a href="../../taxes/flat-tax-regime/" class="related-card"><div class="related-cat">Taxes</div><div class="related-card-title">Italy\'s €100k Flat Tax for New Residents</div></a>',
        ],
    },
    {
        "file": "living-italy-2500-month.md",
        "category": "cost-of-living",
        "slug": "living-italy-2500-month",
        "related": [
            '<a href="../../cost-of-living/cost-of-living-italy-vs-usa/" class="related-card"><div class="related-cat">Cost of Living</div><div class="related-card-title">Italy vs USA: Real Cost Comparison</div></a>',
            '<a href="../../cost-of-living/cost-of-living-milan/" class="related-card"><div class="related-cat">Cost of Living</div><div class="related-card-title">Cost of Living in Milan (2025)</div></a>',
            '<a href="../../visas/elective-residence-visa/" class="related-card"><div class="related-cat">Visas</div><div class="related-card-title">Elective Residence Visa: Complete Guide</div></a>',
        ],
    },
    {
        "file": "mortgages-non-residents-italy.md",
        "category": "property",
        "slug": "mortgages-non-residents-italy",
        "related": [
            '<a href="../../property/how-to-buy-property-italy-american-guide/" class="related-card"><div class="related-cat">Property</div><div class="related-card-title">How to Buy Property in Italy as an American</div></a>',
            '<a href="../../property/italian-notary-process/" class="related-card"><div class="related-cat">Property</div><div class="related-card-title">The Italian Notary Process Explained</div></a>',
            '<a href="../../taxes/flat-tax-regime/" class="related-card"><div class="related-cat">Taxes</div><div class="related-card-title">Italy\'s €100k Flat Tax for New Residents</div></a>',
        ],
    },
    {
        "file": "best-cities-american-expats-italy.md",
        "category": "regions",
        "slug": "best-cities-american-expats-italy",
        "related": [
            '<a href="../../regions/living-in-tuscany-american-expat/" class="related-card"><div class="related-cat">Regions</div><div class="related-card-title">Living in Tuscany as an American Expat</div></a>',
            '<a href="../../cost-of-living/living-italy-2500-month/" class="related-card"><div class="related-cat">Cost of Living</div><div class="related-card-title">Living in Italy on $2,500/Month</div></a>',
            '<a href="../../visas/elective-residence-visa/" class="related-card"><div class="related-cat">Visas</div><div class="related-card-title">Elective Residence Visa: Complete Guide</div></a>',
        ],
    },
]


def main():
    for art in ARTICLES:
        md_path = os.path.join(CONTENT_DIR, art["file"])
        with open(md_path, encoding="utf-8") as f:
            raw = f.read()

        meta, body = parse_frontmatter(raw)
        title = meta.get("title", art["file"])
        description = meta.get("description", "")
        body_html = md_to_html(body)
        read_time = estimate_read_time(body)

        html = build_article(
            title=title,
            description=description,
            category=art["category"],
            slug=art["slug"],
            body_html=body_html,
            read_time=read_time,
            related_cards=art["related"],
        )

        out_dir = os.path.join(OUT_DIR, art["category"], art["slug"])
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "index.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✓  {art['category']}/{art['slug']}/index.html  ({read_time} min, {len(html)//1024}KB)")


if __name__ == "__main__":
    main()
