#!/usr/bin/env python3
"""Replace all author boxes site-wide with article-specific Torino bios."""

import re, os

BASE = os.path.dirname(os.path.abspath(__file__))

BIOS = {
    # citizenship
    "citizenship/apostille-document-translation-italy": "Getting my own documents apostilled from New York took longer than I expected — factor in at least 6 weeks if you're going through a U.S. state office. The translation part is faster, but make sure your translator is officially recognized in Italy.",
    "citizenship/citizenship-court-vs-consulate-route": "I've watched friends go both routes. The court option is faster right now, but only if your lawyer files in a jurisdiction that isn't backlogged — ask before you commit.",
    "citizenship/italian-citizenship-10-years-residency-naturalization": "Ten years feels like a long time, but if you're already planning to stay, it goes quickly. Start gathering paperwork in year eight — the comune is never in a rush.",
    "citizenship/italian-citizenship-1948-case": "The 1948 case is a narrow window but a real one. I've seen it work for people who thought they had no path to citizenship at all. Worth checking your family tree carefully.",
    "citizenship/italian-citizenship-by-marriage": "Two years of Italian residency sounds manageable, but the language requirement trips people up. Start lessons early — the B1 test is taken seriously.",
    "citizenship/jure-sanguinis": "Jure sanguinis was the first thing I researched before moving to Torino. The paperwork chain is tedious, but finding a good genealogist early saves months of back-and-forth with Italian municipalities.",
    # cost-of-living
    "cost-of-living/cost-of-living-italy-vs-usa": "Groceries are cheaper here, utilities less so — especially in winter in northern Italy. My first heating bill in Torino genuinely caught me off guard.",
    "cost-of-living/cost-of-living-milan": "Milan is Italy's most expensive city by a wide margin. If budget matters, a 30-minute train from smaller cities cuts rent nearly in half.",
    "cost-of-living/cost-of-living-turin-american-expats-2025": "I live in Torino, so these numbers come from my actual monthly bills. It's meaningfully more affordable than Milan and underrated as a long-term base for Americans.",
    "cost-of-living/grocery-costs-italy-by-city": "The mercato is almost always cheaper than the supermarket for produce. In Torino, Porta Palazzo market is where I do most of my weekly shop.",
    "cost-of-living/healthcare-costs-italy-vs-usa": "My first specialist visit through the SSN cost €30. The wait was six weeks — for anything semi-urgent I use a private clinic at €80–120, which is still far cheaper than the U.S.",
    "cost-of-living/italy-rent-prices-city-comparison": "These are real market numbers, not listing prices. In Torino what you see advertised and what you actually pay are usually within 5% — less negotiation drama than Rome or Milan.",
    "cost-of-living/living-italy-2500-month": "€2,500 a month works well in smaller northern cities. In Torino I'd call it comfortable — not lavish, but you eat well, travel on weekends, and don't feel squeezed.",
    "cost-of-living/retire-italy-2000-month-budget": "€2,000 a month for a couple is tight but doable outside the major cities. The hidden savings are healthcare and eating out — both far cheaper than the U.S. equivalent.",
    # healthcare
    "healthcare/best-health-insurance-americans-italy": "I went through three different plans in my first two years here. The one thing I'd tell everyone: check whether your actual specialists are in the network before you sign anything.",
    "healthcare/best-private-health-insurance-italy-americans-2025": "Private insurance fills the gaps the SSN doesn't cover well — dental, specialist wait times, anything semi-urgent. Don't skip it in your first year before SSN enrollment kicks in.",
    "healthcare/cigna-vs-axa-vs-allianz-italy": "I spent weeks comparing these three before my move. Cigna has the widest English-speaking network in Italy; AXA was noticeably cheaper when I went to renew.",
    "healthcare/english-speaking-doctors-italy": "Finding an English-speaking GP in Torino took me three tries. The expat Facebook groups usually have the most current recommendations — official lists go stale fast.",
    "healthcare/enroll-italian-ssn": "Enrolling in the SSN at the ASL in Torino took about 45 minutes and one return visit. Bring the permesso, codice fiscale, and proof of address — they will ask for all three.",
    "healthcare/tessera-sanitaria-italy-health-card-americans": "The tessera arrived by mail about three weeks after I enrolled at the ASL in Torino. In the meantime the printed receipt from enrollment works for any appointment.",
    # property
    "property/1-euro-house-italy": "I looked into the €1 programs before settling in Torino. Most properties need €50,000 or more in renovation — budget that in before you get excited about the sticker price.",
    "property/best-cities-invest-property-italy": "From what I've watched over six years, smaller northern cities like Torino are the better bet right now — lower entry price, strong rental demand from students and workers.",
    "property/how-to-buy-property-italy-american-guide": "The thing that surprised me most was how central the notaio is to everything. In the U.S. a lawyer handles this role — in Italy it's the notaio, and their fee is non-negotiable.",
    "property/italian-notary-process": "The compromesso is binding in a way many Americans underestimate. If you back out after signing, you lose the deposit. Read it carefully before you put pen to paper.",
    "property/mortgages-non-residents-italy": "Getting a mortgage as a non-resident is possible but slow. Italian banks want two to three years of local income history if they can get it — a guarantor speeds things up considerably.",
    "property/renting-apartment-italy-expat-guide": "Most landlords in Torino want a 4+4 contract for expats. Transitorio contracts are rare unless you can prove a short-term reason in writing.",
    # residency
    "residency/declaring-presence-8-day-rule-italy-americans": "I got caught out on this my first trip before residency — the hotel handled it, but if you're staying with friends they often forget. A quick dichiarazione at the questura fixes it fast.",
    "residency/getting-sim-card-italy-americans-guide": "TIM has the widest coverage in the mountain areas around Torino, but Iliad is what I use day-to-day — cheapest plan, very reliable in the city.",
    "residency/how-to-get-codice-fiscale-italy-americans": "My codice fiscale was ready the same day I applied at the Agenzia delle Entrate in Torino. Bring your passport — nothing else is strictly required, but they sometimes ask for a copy.",
    "residency/how-to-register-anagrafe-italy-americans": "The first appointment at the anagrafe in Torino is always the hardest to get — book it the same week you arrive. The actual process once you're there takes about 20 minutes.",
    "residency/italian-drivers-license-americans": "Americans have a one-year window to drive on a U.S. license after establishing residency. After that you need an Italian one — don't wait until month eleven to start the process.",
    "residency/open-italian-bank-account": "Fineco was the easiest account for me to open in Torino without a long Italian credit history. Bring the codice fiscale, permesso, and patience for the compliance questions.",
    "residency/permesso-di-soggiorno-renewal-americans-guide": "Book the Kit Postale appointment at the post office at least two months before your permesso expires. The slots in Torino fill up faster than you'd think.",
    "residency/permesso-di-soggiorno": "The Kit Postale at the post office was much calmer than going directly to the questura. The questura in Torino has improved since 2022, but the post office is still my recommendation.",
    "residency/permesso-lungo-periodo-permanent-residency-italy": "After five years you start to feel like the paperwork finally makes sense. The lungo periodo application at the questura in Torino took about three months to process.",
    "residency/register-foreign-car-italy": "I went through this with a car brought from the U.S. The collaudo appointment and the VIN reclassification were the two steps that took the longest — plan for two to three months total.",
    "residency/spid-italy-foreigners-americans-guide": "Getting SPID at a Poste Italiane office in Torino took under 30 minutes with an appointment. Once you have it, you realize how many Italian services actually work well digitally.",
    "residency/tessera-sanitaria-expats": "The card itself arrives by mail, but the process starts at the ASL in your municipality. In Torino the ASL Città di Torino has an English-speaking window at the central office.",
    # taxes
    "taxes/fbar-fatca-americans-italy-guide": "FBAR is the one filing most Americans forget about in their first year abroad. It's free to file and the penalty for missing it is severe — it sits at the top of my annual checklist.",
    "taxes/flat-tax-regime": "The flat tax is a real deal if your income is high enough. I know people who restructured their finances specifically to qualify — run the numbers with a commercialista who handles U.S.-Italy cases.",
    "taxes/irpef-tax-brackets-italy-2025-americans": "IRPEF rates look high on paper but deductions bring the effective rate down significantly. A good commercialista in Torino will find deductions most Americans wouldn't think to claim.",
    "taxes/partita-iva-italy-foreigners": "I opened my Partita IVA under the forfettario regime and it's been straightforward. The key is choosing the right ATECO code from the start — changing it later is a real headache.",
    "taxes/southern-italy-7-percent-flat-tax-foreign-pensioners": "The 7% regime is one of Italy's most underreported tax deals for retirees. The south isn't for everyone, but the numbers are hard to argue with if you're flexible on location.",
    "taxes/us-italy-social-security-totalization-agreement": "If you've worked in both countries, the totalization agreement can make a real difference in what you ultimately collect. Pull your SSA records and have a specialist review them.",
    "taxes/us-italy-tax-treaty-double-taxation": "The treaty is helpful but doesn't eliminate all the friction. I still file in both countries every year — the treaty just determines who taxes what. A dual-qualified CPA is worth every euro.",
    # visas
    "visas/apostille-document-translation-italian-visa": "Apostilles from certain U.S. states take weeks. I recommend starting this step the moment you decide to apply — everything else can wait, the apostille cannot.",
    "visas/digital-nomad-visa": "Italy's nomad visa is newer than the others and consulates are still working out the kinks. Apply with more income documentation than you think you need — they're cautious with new visa types.",
    "visas/elective-residence-visa": "The elective residence visa was my path to Torino. The income threshold sounds daunting but passive income counts — rental income from the U.S. worked for my application.",
    "visas/etias-americans-italy-schengen-guide": "ETIAS isn't live yet but it's worth understanding before it rolls out. Americans planning short trips should apply as soon as the system opens — the launch window will be busy.",
    "visas/fbi-background-check-italian-visa-americans": "The FBI check for my ERV application took eight weeks by mail. Using an FBI-approved channeler gets it in three days — worth the extra cost when you have a consulate deadline.",
    "visas/italy-investor-visa-golden-visa-americans": "The investor visa thresholds haven't changed much since launch. The €500k business route is the most popular with Americans, but the due diligence on the target company is serious work.",
    "visas/italy-spouse-visa-americans": "Processing times at some consulates have improved, but budget four to six months from application to arrival. Having all documents certified and apostilled before submitting cuts the back-and-forth significantly.",
    "visas/italy-student-visa": "Italian consulates process student visas faster than residency visas — typically six to eight weeks. The tricky part is the university enrollment letter, which some schools issue very late.",
    "visas/italy-visa-income-requirements-2025-all-types": "The income thresholds are tied to the ISTAT poverty line and adjust each year. Always confirm the current figure with your consulate — the number in your head from last year may already be wrong.",
    # regions
    "regions/living-rome-american-expat": "Rome is a different Italy from what I know in Torino — bigger, louder, more bureaucratic. That said, the expat community there is huge and the support network is genuinely impressive.",
}

NEW_BOX_TEMPLATE = (
    '<div class="author-box">\n'
    '      <div class="author-avatar-lg">FB</div>\n'
    '      <div><div class="author-name">Fabrizio Boggio · Editor-in-Chief, Italopedia</div>\n'
    '        <div class="author-title">Italian-American writer based in Torino · 6+ years living in Italy</div>\n'
    '        <p class="author-bio">{bio}</p>\n'
    '      </div>\n'
    '    </div>'
)

# Pattern for OLD box (img-based)
OLD_BOX_RE = re.compile(
    r'<div class="author-box">\s*'
    r'<img[^>]+class="author-avatar"[^>]*/>\s*'
    r'<div class="author-info">\s*'
    r'<span class="author-name">[^<]*</span>\s*'
    r'<span class="author-bio">[^<]*</span>\s*'
    r'</div>\s*'
    r'</div>',
    re.DOTALL
)

# Pattern for NEW box — any variant with author-avatar-lg + FB
NEW_BOX_RE = re.compile(
    r'<div class="author-box">\s*'
    r'<div class="author-avatar-lg">FB</div>\s*'
    r'.*?'
    r'</div>\s*'
    r'</div>',
    re.DOTALL
)

updated = []
skipped = []

for key, bio in BIOS.items():
    path = os.path.join(BASE, key, "index.html")
    if not os.path.exists(path):
        skipped.append(f"MISSING: {key}")
        continue

    with open(path, encoding="utf-8") as f:
        content = f.read()

    new_box = NEW_BOX_TEMPLATE.format(bio=bio)

    if OLD_BOX_RE.search(content):
        new_content = OLD_BOX_RE.sub(new_box, content)
        tag = "old→new"
    elif NEW_BOX_RE.search(content):
        new_content = NEW_BOX_RE.sub(new_box, content)
        tag = "updated"
    else:
        skipped.append(f"NO MATCH: {key}")
        continue

    if new_content != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        updated.append(f"{tag}: {key}")
    else:
        skipped.append(f"UNCHANGED: {key}")

print(f"\n✅ Updated {len(updated)} files:")
for u in updated:
    print(f"  {u}")
if skipped:
    print(f"\n⚠️  Skipped {len(skipped)}:")
    for s in skipped:
        print(f"  {s}")
