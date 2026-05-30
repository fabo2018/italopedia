#!/usr/bin/env python3
"""
Remove all dead placeholder links (href="#") from hub pages
that are NOT in the approved 50-article list.
- Approved placeholders: keep as href="#"
- Non-approved placeholders: remove entire <a class="article-row"> block
- Real article links: never touched
- Empty hub-sections (no article-rows left): removed entirely
"""

import re, os

BASE = os.path.dirname(os.path.abspath(__file__))

APPROVED = {
    # VISAS (6)
    "Self-Employment Visa Italy: Freelancers & Business Owners",
    "Italy Visa Rejection: Common Reasons and How to Appeal",
    "Health Insurance for Italian Visa: What Consulates Accept",
    "90/180 Schengen Rule Explained: The Calculator Every American Needs",
    "How to Apply for an Italy Visa from the USA: Consulate Guide",
    "Dual US-Italian Citizens: Do You Need a Visa?",
    # RESIDENCY (5)
    "PEC Email: Why Every Italian Resident Needs One",
    "Italian Government Stamps (Marca da Bollo): The €16 Mystery",
    "Changing Visa Type Inside Italy: When You Can, When You Cannot",
    "Registering a Marriage Performed Abroad in Italy",
    "Italian Civil Union (Unione Civile): Rights and Process",
    # TAXES (10)
    "Tax Residency in Italy: When You Become Liable",
    "IMU Property Tax: When You Owe and How Much",
    "Capital Gains Tax in Italy: Investments, Property, Crypto",
    "Inheritance and Gift Tax in Italy: A Surprise for Americans",
    "Foreign Tax Credit vs Foreign Earned Income Exclusion",
    "Italian Tax Year Calendar: Every Deadline You Care About",
    "How to Find a Commercialista (Italian CPA) Who Knows US Tax",
    "Cryptocurrency Tax in Italy: 2025 Rules",
    "401(k) and IRA Withdrawals as an Italian Resident",
    "Roth IRA in Italy: Tax-Free Doesn't Mean Tax-Free",
    # HEALTHCARE (6)
    "Specialist Visits: How the Italian Referral System Works",
    "Emergency Room (Pronto Soccorso) in Italy: What to Expect",
    "Dental Care in Italy: Mostly Private, Mostly Cheaper",
    "Mental Health Care in Italy: Public and Private Options",
    "Chronic Conditions: Diabetes, Hypertension, Cardiac in Italy",
    "Top Private Hospitals in Italy: Where Americans Go",
    # PROPERTY (7)
    "Compromesso: The Italian Preliminary Sale Contract",
    "Property Purchase Taxes in Italy: Exact Calculation",
    "Renting Out Property in Italy: Cedolare Secca vs Ordinario",
    "Renovating an Italian Stone House: Costs, Permits, Contractors",
    "Buying in Puglia: The Trulli, the Masserie, the Coast",
    "Italian Lease Types Explained: 4+4, 3+2, Transitorio",
    "Short-Term Rentals in Italy: Rules, Taxes, Platforms",
    # CITIZENSHIP (5)
    "Jure Sanguinis Document Checklist: Birth, Marriage, Death Certificates",
    "B1 Italian Language Requirement: CILS, CELI, PLIDA Tests",
    "AIRE Registration: The Italian Registry of Citizens Abroad",
    "Italian Passport Application: After You're a Citizen",
    "2024 Italian Citizenship Reform: What Actually Changed",
    # REGIONS (7)
    "Best Italian Cities for Remote Workers and Digital Nomads",
    "Best Italian Cities for Families with Children",
    "Living in Veneto: Venice, Verona, Padua",
    "Living in Puglia: The Heel and the Trulli",
    "Living in Sardinia: The Quietest Italian Region",
    "Best Italian Coastal Towns for Year-Round Living",
    "How to Test-Live in Italy Before Committing",
    # COST OF LIVING (4)
    "Cost of Living in Bologna 2025: The Best-Value Big City",
    "Cost of Living in Lecce 2025: Southern Italy on a Budget",
    "Hidden Costs of Living in Italy Americans Forget",
    "Italy vs Spain vs Portugal: Cost Comparison for Expats",
}

HUB_PAGES = [
    'visas/index.html',
    'residency/index.html',
    'taxes/index.html',
    'healthcare/index.html',
    'property/index.html',
    'citizenship/index.html',
    'regions/index.html',
    'cost-of-living/index.html',
]

# Match a complete <a class="article-row" href="#"> ... </a> block
PLACEHOLDER_RE = re.compile(
    r'[ \t]*<a class="article-row" href="#">.*?</a>[ \t]*\n?',
    re.DOTALL
)

TITLE_RE = re.compile(r'<div class="article-row-title">(.*?)</div>', re.DOTALL)


def remove_empty_hub_sections(html):
    """
    Remove <div class="hub-section">...</div> blocks that contain
    no <a class="article-row"> elements. Uses depth counting to
    correctly find section boundaries without regex cross-section issues.
    """
    lines = html.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if '<div class="hub-section">' in line:
            # Collect the entire hub-section block via div depth counting
            section_lines = [line]
            # Count open divs: opening line has one <div class="hub-section">
            depth = line.count('<div') - line.count('</div>')
            i += 1
            while i < len(lines) and depth > 0:
                l = lines[i]
                section_lines.append(l)
                depth += l.count('<div') - l.count('</div>')
                i += 1
            # Check if any article-row survives in this section
            section_html = '\n'.join(section_lines)
            if 'class="article-row"' in section_html:
                result.extend(section_lines)
            # else: section is empty — skip it
        else:
            result.append(line)
            i += 1
    return '\n'.join(result)


grand_removed = 0

for rel in HUB_PAGES:
    fpath = os.path.join(BASE, rel)
    with open(fpath, encoding='utf-8') as f:
        content = f.read()
    orig = content
    removed_titles = []
    kept_titles = []

    def handle_match(m):
        block = m.group(0)
        tm = TITLE_RE.search(block)
        title = tm.group(1).strip() if tm else ''
        if title and title not in APPROVED:
            removed_titles.append(title)
            return ''
        kept_titles.append(title)
        return block

    # Step 1: remove non-approved href="#" blocks
    content = PLACEHOLDER_RE.sub(handle_match, content)

    # Step 2: remove hub-sections that became empty
    content = remove_empty_hub_sections(content)

    if content != orig:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ {rel}")
        print(f"   Rimossi: {len(removed_titles)}  |  Approvati mantenuti: {len(kept_titles)}")
        for t in removed_titles:
            print(f"   ✗ {t}")

    grand_removed += len(removed_titles)

print(f"\n{'='*60}")
print(f"TOTALE rimossi: {grand_removed}")
