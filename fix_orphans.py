#!/usr/bin/env python3
"""
fix_orphans.py
Risolve i 19 articoli orfani rimasti (0 link in entrata).
Strategia: aggiunge un 4° card related-section negli articoli che
dovrebbero naturalmente linkare a ciascun orfano.
"""

import re, os

BASE = '/Users/fabrizio/italopedia/'

# Mappa: articolo_da_modificare → lista di (href_del_orfano, categoria, titolo)
# Ogni entry aggiunge un 4° card alla related-grid dell'articolo target.
ORPHAN_FIXES = {
    # orfano: citizenship/b1-italian-language-requirement/
    'citizenship/italian-citizenship-10-years-residency-naturalization/': [
        ('../../citizenship/b1-italian-language-requirement/', 'Citizenship',
         'B1 Italian Language Requirement for Citizenship: Tests and Exemptions'),
    ],
    # orfano: citizenship/italian-citizenship-by-marriage/ già linkato da molti
    # — quella è effettivamente già coperta da altri

    # orfano: cost-of-living/italy-vs-spain-vs-portugal-cost/
    'cost-of-living/cost-of-living-italy-vs-usa/': [
        ('../../cost-of-living/italy-vs-spain-vs-portugal-cost/', 'Cost of Living',
         'Italy vs Spain vs Portugal: Cost of Living Comparison for Americans'),
    ],

    # orfano: healthcare/dental-care-italy-americans/
    'healthcare/best-health-insurance-americans-italy/': [
        ('../../healthcare/dental-care-italy-americans/', 'Healthcare',
         'Dental Care in Italy for Americans: Mostly Private, Mostly Cheaper'),
    ],

    # orfano: healthcare/english-speaking-doctors-italy/
    'healthcare/enroll-italian-ssn/': [
        ('../../healthcare/english-speaking-doctors-italy/', 'Healthcare',
         'Finding English-Speaking Doctors in Italy: Complete Guide for Americans'),
    ],

    # orfano: property/renovating-italian-stone-house/
    'property/1-euro-house-italy/': [
        ('../../property/renovating-italian-stone-house/', 'Property',
         'Renovating an Italian Stone House: Real Costs, Permits, and Pitfalls'),
    ],

    # orfano: regions/living-florence-american-expat/
    'regions/living-in-tuscany-american-expat/': [
        ('../../regions/living-florence-american-expat/', 'Regions',
         'Living in Florence as an American Expat: Complete Guide (2025)'),
    ],

    # orfano: regions/sicily-american-expats-guide/
    'regions/best-coastal-towns-italy-year-round/': [
        ('../../regions/sicily-american-expats-guide/', 'Regions',
         'Sicily for American Expats: The Complete Living Guide (2025)'),
    ],

    # orfano: residency/declaring-presence-8-day-rule-italy-americans/
    'residency/permesso-di-soggiorno/': [
        ('../../residency/declaring-presence-8-day-rule-italy-americans/', 'Residency',
         "Italy's 8-Day Rule: How to Declare Your Presence as an American"),
    ],

    # orfano: residency/getting-sim-card-italy-americans-guide/
    'residency/how-to-get-codice-fiscale-italy-americans/': [
        ('../../residency/getting-sim-card-italy-americans-guide/', 'Residency',
         'Getting a SIM Card in Italy: Complete Guide for Americans'),
    ],

    # orfani: residency/italian-civil-union-unione-civile/ + residency/registering-foreign-marriage-italy/
    'citizenship/italian-citizenship-by-marriage/': [
        ('../../residency/italian-civil-union-unione-civile/', 'Residency',
         'Italian Civil Union (Unione Civile): Rights, Process, and What It Means'),
        ('../../residency/registering-foreign-marriage-italy/', 'Residency',
         'Registering a Foreign Marriage in Italy: Complete Guide for Americans'),
    ],

    # orfano: residency/italian-drivers-license-americans/
    'residency/how-to-register-anagrafe-italy-americans/': [
        ('../../residency/italian-drivers-license-americans/', 'Residency',
         "Italian Driver's License for Americans: Converting Your U.S. License"),
    ],

    # orfano: residency/marca-da-bollo-italy/
    'residency/spid-italy-foreigners-americans-guide/': [
        ('../../residency/marca-da-bollo-italy/', 'Residency',
         'Marca da Bollo: The €16 Italian Government Stamp, Fully Explained'),
    ],

    # orfano: residency/pec-email-italy/
    'residency/open-italian-bank-account/': [
        ('../../residency/pec-email-italy/', 'Residency',
         'PEC Email in Italy: Why Every Resident Needs One and How to Get It'),
    ],

    # orfano: taxes/us-italy-social-security-totalization-agreement/
    'taxes/us-italy-tax-treaty-double-taxation/': [
        ('../../taxes/us-italy-social-security-totalization-agreement/', 'Taxes',
         'US-Italy Social Security Totalization Agreement: What Americans Need to Know'),
    ],

    # orfano: visas/etias-americans-italy-schengen-guide/
    'visas/90-180-schengen-rule-calculator/': [
        ('../../visas/etias-americans-italy-schengen-guide/', 'Visas',
         'ETIAS for Americans Visiting Italy: What You Need to Know (2025)'),
    ],

    # orfano: visas/italy-spouse-visa-americans/
    'visas/elective-residence-visa/': [
        ('../../visas/italy-spouse-visa-americans/', 'Visas',
         'Italy Spouse Visa for Americans: Move to Italy with Your Italian Partner'),
    ],

    # orfano: visas/italy-student-visa/
    'visas/how-to-apply-italy-visa-usa/': [
        ('../../visas/italy-student-visa/', 'Visas',
         'Italy Student Visa for Americans: How to Study in Italy Long-Term'),
    ],

    # orfano: visas/italy-visa-rejection-how-to-appeal/
    'visas/italy-visa-income-requirements-2025-all-types/': [
        ('../../visas/italy-visa-rejection-how-to-appeal/', 'Visas',
         'Italy Visa Rejection: Common Reasons and How to Appeal'),
    ],
}


def build_card(href, cat, title):
    """Costruisce l'HTML di un singolo related-card."""
    return (
        f'    <a href="{href}" class="related-card">\n'
        f'      <div class="related-cat">{cat}</div>\n'
        f'      <div class="related-card-title">{title}</div>\n'
        f'    </a>'
    )


def add_cards_to_related_grid(html, cards):
    """
    Trova il <div class="related-grid"> nell'HTML e aggiunge i card
    dati prima del suo </div> di chiusura.
    Gestisce entrambe le varianti di indentazione presenti nel sito.
    """
    # Trova l'inizio del related-grid
    grid_start = html.find('<div class="related-grid">')
    if grid_start == -1:
        return html, False

    # Conta i div per trovare il </div> di chiusura del related-grid
    pos = grid_start
    depth = 0
    close_pos = -1
    while pos < len(html):
        next_open = html.find('<div', pos)
        next_close = html.find('</div>', pos)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            if depth == 0:
                close_pos = next_close
                break
            pos = next_close + 6

    if close_pos == -1:
        return html, False

    # Costruisce il blocco da inserire prima del </div> di chiusura
    new_cards = '\n'.join(build_card(h, c, t) for h, c, t in cards)
    # Inserisce prima del </div> di chiusura del grid
    return html[:close_pos] + new_cards + '\n' + html[close_pos:], True


def process_file(slug, cards_to_add):
    filepath = BASE + slug + 'index.html'
    if not os.path.exists(filepath):
        print(f"  SKIP (not found): {slug}")
        return False

    html = open(filepath, encoding='utf-8').read()

    # Verifica che non abbia già questi link (evita duplicati)
    hrefs = [c[0] for c in cards_to_add]
    already = [h for h in hrefs if h in html]
    if already:
        print(f"  SKIP (link già presente {already}): {slug}")
        return False

    new_html, ok = add_cards_to_related_grid(html, cards_to_add)
    if not ok:
        print(f"  WARN (related-grid non trovato): {slug}")
        return False

    if new_html == html:
        print(f"  NO CHANGE: {slug}")
        return False

    open(filepath, 'w', encoding='utf-8').write(new_html)
    return True


if __name__ == '__main__':
    print('=' * 65)
    print('ORPHAN FIX: aggiunta 4° card a related-grid di 18 articoli')
    print('=' * 65)

    fixed = 0
    for target_slug, cards in sorted(ORPHAN_FIXES.items()):
        result = process_file(target_slug, cards)
        if result:
            for href, cat, title in cards:
                orphan = href.replace('../../', '').rstrip('/')
                print(f"  ✓ {target_slug}")
                print(f"      → link aggiunto verso: {orphan}/")
            fixed += 1

    print(f'\nFixed: {fixed} articoli modificati')
