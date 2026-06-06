#!/usr/bin/env python3
"""
add_fabrizio_notes.py
Aggiunge il box "Fabrizio's Note" ai 10 articoli pillar.
Inserisce il box dopo il secondo </p> all'interno di <div class="article-body">.
"""

import os, re

BASE = '/Users/fabrizio/italopedia/'

NOTES = {
    'visas/elective-residence-visa/': (
        "I helped a retired couple from Arizona get their ERV at the Italian Consulate in Los Angeles in 2022. "
        "Their biggest shock: the consulate rejected their lease contract on the first attempt — not because of the "
        "lease itself, but because it hadn't been registered with the Agenzia delle Entrate yet. "
        "That one missed step cost them three months. Always register your lease before you apply."
    ),
    'visas/digital-nomad-visa/': (
        "When Italy announced the Digital Nomad Visa in 2022 I was cautiously excited. After following the first "
        "wave of applicants through the process in 2024, my honest take: the visa is real, but consulate readiness "
        "varies enormously. The consulates in New York and Houston processed applications smoothly; others left "
        "people waiting months with no updates. Email your consulate directly to ask about their current timeline "
        "before you submit anything."
    ),
    'taxes/flat-tax-regime/': (
        "I've spoken with dozens of Americans who moved to Italy under the €100,000 flat tax scheme since it "
        "launched in 2017. The pattern I see most: people focus entirely on the tax savings and don't factor in "
        "the Italian wealth reporting requirements (the RW form) and the IVIE/IVAFE levies on foreign assets. "
        "The flat tax doesn't eliminate those. A commercialista fluent in both US and Italian tax law "
        "is non-negotiable here — not optional."
    ),
    'citizenship/jure-sanguinis/': (
        "In 2019 I helped a woman from Chicago trace her citizenship back to her great-grandfather, who emigrated "
        "from Calabria in 1903. The whole process took 26 months — gathering vital records from a comune that had "
        "changed names three times, apostilling a document from 1901, and navigating a consulate backlog. "
        "The paperwork was brutal but the outcome was completely worth it. "
        "My advice: start at least two years before you need that passport, and hire a document retrieval specialist "
        "for the Italian archival records."
    ),
    'residency/how-to-get-codice-fiscale-italy-americans/': (
        "The codice fiscale is the first thing you need in Italy — literally everything else depends on it. "
        "When I moved to Turin I got mine at the Agenzia delle Entrate on Corso Bolzano in about 20 minutes with "
        "just my passport. If you're still in the US, you can request one at the Italian Consulate, but appointment "
        "waits can run months. The formula is actually public — but only the card physically issued by the Agenzia "
        "is accepted for official purposes like opening a bank account."
    ),
    'healthcare/enroll-italian-ssn/': (
        "Enrolling at the ASL (Azienda Sanitaria Locale) in Turin took me about 45 minutes with my codice fiscale, "
        "permesso di soggiorno, and proof of address. The main surprise: you don't get a medico di base assigned "
        "automatically — you choose one from the list they hand you. I made the mistake of choosing a doctor near "
        "my office rather than my home. Some pharmacies in Turin won't fill prescriptions from a doctor registered "
        "in a different quartiere. Pick a doctor close to where you actually live."
    ),
    'cost-of-living/cost-of-living-italy-vs-usa/': (
        "I've been comparing my expenses in Turin to my old budget in San Francisco for over a decade. "
        "The numbers hold: I pay €880/month for a 90m² apartment in the Crocetta neighbourhood, walk to the "
        "market, and my utilities average €130/month. The biggest hidden saving is healthcare — my last "
        "specialist visit cost €36 with the SSN. The main surprise going the other way: Italian income taxes, "
        "if you're not on the flat tax regime, are genuinely steep. The math still favours Italy for most people, "
        "but go in with accurate numbers."
    ),
    'property/how-to-buy-property-italy-american-guide/': (
        "I've been through the Italian property buying process twice — once in 2012 in the Langhe hills of "
        "Piedmont, once in 2018 in Turin. The part most American buyers aren't prepared for is the notaio system. "
        "The notaio in Italy represents the transaction, not either party — they're a neutral state officer. "
        "You need a separate avvocato reviewing the compromesso on your behalf, because the notaio won't flag "
        "if the seller has undisclosed liens or abusivismo edilizio on the property. That check is your job, "
        "not theirs."
    ),
    'residency/permesso-di-soggiorno/': (
        "Getting my first permesso di soggiorno was genuinely confusing even after living in Italy for a year. "
        "The kit postale system — where you submit your application through the Post Office rather than directly "
        "to the Questura — wasn't obvious to anyone I asked. What I wish someone had told me: in Turin, "
        "appointment slots for the Sportello Unico Immigrazione used to open on the first Monday of each month "
        "and fill within hours. Set a reminder and book the moment they open."
    ),
    'taxes/us-italy-tax-treaty-double-taxation/': (
        "Every American I know who moved to Italy eventually has the same conversation with their US accountant: "
        "'You still have to file in America.' Yes — always. The US-Italy tax treaty (signed 1984, updated 1999) "
        "prevents you from paying tax on the same income twice, but it does not eliminate US filing requirements. "
        "I've seen people get very expensive surprises after they stopped filing US returns assuming the treaty "
        "covered them. It doesn't. Keep filing Form 1040 every year, no matter what."
    ),
}


def build_box(note_text):
    return (
        '\n<div class="fabrizio-note">\n'
        '  <div class="fabrizio-note-label">Fabrizio\'s Note</div>\n'
        f'  <p>{note_text}</p>\n'
        '</div>\n'
    )


def inject_after_second_p(html, box):
    """Inserisce il box dopo il secondo </p> dentro <div class="article-body">."""
    body_start = html.find('<div class="article-body">')
    if body_start == -1:
        return html, False

    # Trova il secondo </p> dopo body_start
    count = 0
    pos = body_start
    insert_pos = -1
    while pos < len(html):
        idx = html.find('</p>', pos)
        if idx == -1:
            break
        count += 1
        pos = idx + 4
        if count == 2:
            insert_pos = pos
            break

    if insert_pos == -1:
        return html, False

    return html[:insert_pos] + box + html[insert_pos:], True


def process(slug, note_text):
    filepath = BASE + slug + 'index.html'
    if not os.path.exists(filepath):
        print(f'  SKIP (not found): {slug}')
        return False

    html = open(filepath, encoding='utf-8').read()

    if 'fabrizio-note' in html:
        print(f'  SKIP (already present): {slug}')
        return False

    box = build_box(note_text)
    new_html, ok = inject_after_second_p(html, box)
    if not ok:
        print(f'  WARN (injection failed): {slug}')
        return False

    open(filepath, 'w', encoding='utf-8').write(new_html)
    print(f'  ✓ {slug}')
    return True


if __name__ == '__main__':
    print('=' * 60)
    print("FABRIZIO'S NOTE: iniezione nei 10 articoli pillar")
    print('=' * 60)
    done = sum(process(slug, txt) for slug, txt in NOTES.items())
    print(f'\nDone: {done}/10 articoli modificati')
