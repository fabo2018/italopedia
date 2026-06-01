#!/usr/bin/env python3
"""
Aggiunge FAQPage JSON-LD ai top 20 articoli di Italopedia.
Uso: python3 add_faq_schema.py           → dry-run (mostra file che verranno modificati)
     python3 add_faq_schema.py --apply   → applica le modifiche
Idempotente: non aggiunge il blocco se è già presente.
"""

import sys
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
DRY_RUN = "--apply" not in sys.argv

# ---------------------------------------------------------------------------
# FAQ data: top 20 articles by traffic/intent potential
# Each key is the file path relative to ROOT (without leading /)
# Each value is a list of {"q": "...", "a": "..."} dicts (4–6 per article)
# ---------------------------------------------------------------------------

FAQ_DATA = {

    # ── VISAS ────────────────────────────────────────────────────────────────

    "visas/elective-residence-visa/index.html": [
        {
            "q": "What is the Italy Elective Residence Visa?",
            "a": "The Elective Residence Visa (visto per residenza elettiva) is Italy's long-stay visa for Americans who want to live in Italy without working. It requires proof of passive income—at least €31,000/year for a single applicant—from pensions, investments, rental income, or other non-employment sources. It is Italy's most popular retirement visa."
        },
        {
            "q": "How much income do I need for the Italy Elective Residence Visa?",
            "a": "Consulates typically require at least €31,000 per year in passive income for a single applicant (roughly €38,000 if bringing a spouse, plus €5,000 per additional dependent). Some consulates set the bar higher—€40,000–€50,000. Income must be passive: Social Security, pensions, dividends, or rental income. Earned income from work does not qualify."
        },
        {
            "q": "Can I work on the Italy Elective Residence Visa?",
            "a": "No. The Elective Residence Visa explicitly prohibits employment or any income-generating activity in Italy, including remote work for non-Italian employers. If you plan to work remotely while living in Italy, you need Italy's Digital Nomad Visa instead."
        },
        {
            "q": "How long does the Elective Residence Visa application take?",
            "a": "Processing takes 90–120 days at most US consulates, but appointment wait times alone can be 2–6 months depending on jurisdiction. Apply at least 6 months before your intended move date. The visa is issued for one year and must be converted to a permesso di soggiorno within 8 days of arrival."
        },
        {
            "q": "What documents do I need for the Italy Elective Residence Visa?",
            "a": "Key documents include: valid passport (6+ months beyond the visa period), completed application form, recent photos, proof of passive income (tax returns, pension letters, bank statements), proof of Italian accommodation (lease or property deed), and health insurance covering at least €30,000. Exact requirements vary by consulate—always confirm with your local Italian consulate in the US."
        },
        {
            "q": "What happens after I arrive in Italy on the Elective Residence Visa?",
            "a": "Within 8 days of arriving you must declare your presence at the local Questura and apply for a permesso di soggiorno through a post office (Poste Italiane) kit. Within 20 days you should register at the Anagrafe (civil registry) if you intend to establish legal residency. The permesso is renewable annually."
        },
    ],

    "visas/digital-nomad-visa/index.html": [
        {
            "q": "What is Italy's Digital Nomad Visa?",
            "a": "Italy's Digital Nomad Visa (Visto per Nomadi Digitali), introduced in 2024, allows non-EU citizens to live and work remotely from Italy for up to one year. It requires proof of remote employment or self-employment, a minimum income of €28,000/year, health insurance, and accommodation in Italy."
        },
        {
            "q": "How much do I need to earn for Italy's Digital Nomad Visa?",
            "a": "The minimum income requirement is €28,000/year (about €2,333/month). This must come from remote work—employment with a non-Italian company, freelancing, or running an online business. Income must be demonstrable for at least 6 months before applying."
        },
        {
            "q": "How does Italy's Digital Nomad Visa differ from the Elective Residence Visa?",
            "a": "The Digital Nomad Visa allows active remote work; the Elective Residence Visa prohibits it. The Digital Nomad Visa requires earned income; the Elective Residence Visa requires passive income such as pensions or investments. Both are issued for one year. Remote workers choose the Digital Nomad Visa; retirees and passive-income earners choose Elective Residence."
        },
        {
            "q": "Can I freelance as a US citizen on the Italy Digital Nomad Visa?",
            "a": "Yes. Self-employed freelancers qualify as long as their clients are outside Italy and they earn at least €28,000/year. You will need to show contracts, invoices, and 6+ months of income history. If you intend to work with Italian clients once in Italy, you will need to open a Partita IVA (Italian VAT number)."
        },
        {
            "q": "Can I extend Italy's Digital Nomad Visa?",
            "a": "The initial visa is for one year. You can apply for a digital-nomad permesso di soggiorno valid up to 2 years. After that, you would need to switch categories—typically Elective Residence if you have passive income, or a Partita IVA work permit if you generate Italian business income."
        },
    ],

    "visas/italy-visa-income-requirements-2025-all-types/index.html": [
        {
            "q": "How much income do I need to retire to Italy?",
            "a": "For the Elective Residence Visa, Italian consulates typically require at least €31,000/year in passive income (pensions, investments, rental income) for a single applicant. Some consulates set higher thresholds of €40,000–€50,000. Income must be passive—not from employment. US Social Security, 401k/IRA distributions, and dividends all count."
        },
        {
            "q": "What is the minimum income for Italy's Digital Nomad Visa?",
            "a": "Italy's Digital Nomad Visa requires a minimum of €28,000/year (approximately €2,333/month) from remote work. This must be active income from employment or self-employment with non-Italian clients and must be demonstrable for at least the past 6 months."
        },
        {
            "q": "Can I combine multiple income sources to meet Italy's visa requirements?",
            "a": "Yes. For the Elective Residence Visa, you can combine Social Security, pension payments, IRA or 401k distributions, dividend income, and rental income to meet the €31,000 minimum. The key requirement is that all sources are passive—not earned through active work."
        },
        {
            "q": "Does Italy check your bank account when applying for a visa?",
            "a": "Yes. Italian consulates require bank statements (typically the last 3–6 months) to verify income and savings. They look for stable, recurring deposits consistent with your stated income source. Large one-time deposits made shortly before applying may be questioned or discounted."
        },
        {
            "q": "What is the minimum income for Italy's family reunification visa?",
            "a": "For family reunification (ricongiungimento familiare), the sponsor in Italy must earn at least the annual social allowance (approximately €6,000/year) plus 50% more per dependent. For a spouse, this works out to roughly €9,000–€12,000/year. Adequate housing is also required."
        },
    ],

    "visas/health-insurance-italian-visa/index.html": [
        {
            "q": "What health insurance is required for an Italian visa?",
            "a": "All Italian long-stay D visas require health insurance covering at least €30,000 in medical expenses, valid throughout the Schengen area, for the entire visa duration. The policy must include emergency treatment, hospitalisation, and medical repatriation. Standard US health insurance usually does not meet these criteria."
        },
        {
            "q": "Can I use US health insurance for an Italian visa application?",
            "a": "Most US health insurance policies do not qualify because they do not cover repatriation or do not explicitly guarantee €30,000 in European medical coverage. Cigna Global, Allianz Care, GeoBlue, and Axa Connect are expat policies commonly accepted by Italian consulates. Expect to pay €150–€400/month for qualifying coverage."
        },
        {
            "q": "How long do I need private health insurance before enrolling in Italy's SSN?",
            "a": "You will need private health insurance from arrival until SSN enrollment, which typically takes 2–6 months—the time needed to obtain your permesso di soggiorno and register at the local ASL. Elective Residence Visa holders can enroll in the SSN voluntarily by paying an annual contribution of approximately €400–€1,500, replacing private insurance."
        },
        {
            "q": "What happens if I need medical care in Italy before my SSN is active?",
            "a": "You can use private clinics and pay out of pocket, then claim on your private health insurance. Emergency care is free at all Italian public hospitals regardless of insurance status. Emergency room visits (Pronto Soccorso) are free for genuine emergencies; non-urgent visits may carry a small co-pay of €20–€50."
        },
        {
            "q": "Does enrolling in Italy's SSN replace the need for private health insurance?",
            "a": "Once enrolled in the SSN, most expats find public coverage sufficient for routine care and emergencies. Many keep a supplemental private policy for faster specialist access, English-speaking doctors, and private dental. A supplemental plan typically costs €50–€150/month."
        },
    ],

    "visas/italy-investor-visa-golden-visa-americans/index.html": [
        {
            "q": "What is Italy's Investor Visa (Golden Visa)?",
            "a": "Italy's Investor Visa (Visto per Investitori) is a 2-year long-stay visa for non-EU nationals who make a qualifying investment in Italy. Options include: €250,000 in an innovative startup; €500,000 in an existing Italian company; €1 million in a charitable donation of general Italian interest; or €2 million in Italian government bonds."
        },
        {
            "q": "How much do I need to invest for Italy's Golden Visa?",
            "a": "Minimum investments are: €250,000 in an innovative startup (the most popular option); €500,000 in an established Italian company; €1,000,000 charitable donation; €2,000,000 in Italian government bonds (Titoli di Stato). The startup option at €250,000 offers the lowest entry threshold."
        },
        {
            "q": "How long does Italy's Investor Visa last?",
            "a": "The initial visa is valid for 2 years and renewable for up to 3 additional years (5 years total). After 5 years of legal residence, you can apply for permanent residency (permesso CE per soggiornanti di lungo periodo). After 10 years, you can apply for Italian citizenship by naturalisation."
        },
        {
            "q": "Can family members join under Italy's Investor Visa?",
            "a": "Yes. The investor can bring a spouse and minor children under a family reunification permesso di soggiorno without the normal income requirements that apply to other visa types. Family members enjoy the same rights of residence as the primary investor."
        },
        {
            "q": "Does Italy's Investor Visa include a tax benefit?",
            "a": "The Investor Visa does not automatically include a tax benefit, but investors who establish Italian tax residency may qualify for the €100,000 flat tax regime if they have not been Italian tax residents in 9 of the last 10 years. The combination of Investor Visa and flat tax is very attractive for high-net-worth individuals relocating to Italy."
        },
    ],

    # ── CITIZENSHIP ──────────────────────────────────────────────────────────

    "citizenship/jure-sanguinis/index.html": [
        {
            "q": "What is jure sanguinis Italian citizenship?",
            "a": "Jure sanguinis (by right of blood) is Italy's principle of citizenship by descent. If you have an Italian ancestor who was an Italian citizen at the time of your connecting relative's birth, Italy recognises you as a citizen—regardless of how many generations back that ancestor lived—as long as the citizenship line was never broken by naturalisation before the next birth in the chain."
        },
        {
            "q": "How many generations back can I claim Italian citizenship by descent?",
            "a": "There is theoretically no generational limit. If your great-great-great-grandparent was born in Italy and never naturalised in another country before the next qualifying ancestor was born, you may qualify. In practice most successful claimants trace the line back 2–4 generations. The key is an unbroken chain of Italian citizenship transmission."
        },
        {
            "q": "What breaks the jure sanguinis chain?",
            "a": "The chain breaks if an Italian ancestor naturalised as a citizen of another country before the birth of the next qualifying ancestor in the line. For example, if your great-grandfather naturalised as a US citizen in 1920, but your grandfather was born in 1925, the chain broke at your grandfather's birth—he was not born to an Italian citizen."
        },
        {
            "q": "What is the 1948 case for Italian citizenship?",
            "a": "The '1948 case' applies when Italian citizenship would pass through a female line before January 1, 1948—the date Italy's constitution granted women equal rights. Under ordinary consulate rules, women could not transmit citizenship before that date. The 1948 case allows applicants to pursue recognition through Italian courts, which have ruled the exclusion unconstitutional, restoring claims that consulates would otherwise reject."
        },
        {
            "q": "How long does the jure sanguinis application process take?",
            "a": "The consulate route takes 1–5+ years depending on the consulate's backlog—Chicago and New York have notoriously long waits, sometimes 5–8 years. The Italian court route typically takes 12–24 months but requires hiring an Italian lawyer and at least one trip to Italy. The 2024 reform tightened document requirements but did not fundamentally change timelines."
        },
        {
            "q": "Do I need to speak Italian to get Italian citizenship by descent?",
            "a": "No. Jure sanguinis is the recognition of pre-existing citizenship, not the acquisition of a new nationality, so there is no Italian language test. However, if you apply for Italian citizenship through naturalization after 10 years of legal residency, a B1 language certificate is required."
        },
    ],

    "citizenship/citizenship-court-vs-consulate-route/index.html": [
        {
            "q": "What is the difference between the court route and the consulate route for Italian citizenship?",
            "a": "The consulate route processes jure sanguinis claims through the Italian consulate in your US jurisdiction. It requires no travel to Italy but is slow—1–5+ years. The court route involves filing directly with an Italian civil court. It is faster (12–18 months), handles 1948 cases that consulates refuse, and bypasses consulate backlogs—but it requires an Italian lawyer and typically at least one trip to Italy."
        },
        {
            "q": "Which is faster: the Italian citizenship court route or consulate route?",
            "a": "The court route is generally faster—12–18 months versus 2–5+ years at most US consulates. Chicago consulate appointments are booked out past 2030. However, the court route costs more: €3,000–€6,000 in legal fees versus €300–€1,000 total for the consulate route."
        },
        {
            "q": "Can I use the Italian court route if my consulate already rejected my claim?",
            "a": "Yes. If your claim passes through a female line before 1948 (the 1948 case), Italian consulates will reject it—but Italian courts recognise the claim as constitutional. Even if the consulate rejected your application on other grounds, you may refile through the court system, where judges can independently assess the evidence."
        },
        {
            "q": "Do I need to live in Italy to use the citizenship court route?",
            "a": "Not necessarily. While you typically need to attend at least one hearing, many law firms can represent you via power of attorney and handle the preliminary steps without your presence. Hearings are usually scheduled 6–18 months after filing, giving you time to plan a trip. Some applicants combine the hearing with a longer stay to explore the country."
        },
        {
            "q": "What does the Italian citizenship court route cost?",
            "a": "Total costs range from €4,000–€9,000: €3,000–€6,000 in Italian lawyer fees, €300–€800 in court and filing fees, and €500–€2,000 for document preparation (apostilles, certified translations). The consulate route costs €300–€1,500 total but takes 3–5× longer."
        },
    ],

    # ── RESIDENCY ────────────────────────────────────────────────────────────

    "residency/permesso-di-soggiorno/index.html": [
        {
            "q": "What is the permesso di soggiorno?",
            "a": "The permesso di soggiorno (residence permit) is the document that authorises non-EU citizens to legally reside in Italy beyond 90 days. It must be applied for within 8 days of arriving in Italy and is tied to your visa type—elective residence, digital nomad, family reunification, employment, etc. It is issued by the Questura (police headquarters) after a process that begins at Poste Italiane."
        },
        {
            "q": "How do I apply for a permesso di soggiorno in Italy?",
            "a": "Pick up a yellow kit (kit postale) at Poste Italiane, complete the application form, attach required documents (passport copy, visa, photos, marca da bollo revenue stamp), and submit it at a post office that handles permesso applications. You receive a receipt (ricevuta) immediately and an appointment date at the Questura. The physical permesso card arrives 3–6 months after the Questura appointment."
        },
        {
            "q": "How long does it take to get a permesso di soggiorno?",
            "a": "From post office submission to physical card: 3–6 months typically, up to 9 months in cities with heavy backlogs like Rome and Milan. The receipt from the post office serves as legal proof of residence in the meantime and is accepted by banks, schools, the Anagrafe, and the ASL for SSN enrollment."
        },
        {
            "q": "How much does a permesso di soggiorno cost?",
            "a": "Total cost is approximately €200–€400: the postal kit fee (about €30), a marca da bollo revenue stamp (€16), and the government contribution fee (€80–€200 depending on the permesso duration and type). The Elective Residence permesso typically costs €200–€250 per year."
        },
        {
            "q": "What documents do I need to apply for a permesso di soggiorno?",
            "a": "Core documents: valid passport with your entry visa, 4 passport-size photos, marca da bollo (€16 revenue stamp), proof of accommodation (lease, property deed, or host letter), proof of income or financial means, and private health insurance documentation. Exact requirements depend on your visa type and local Questura."
        },
    ],

    "residency/how-to-get-codice-fiscale-italy-americans/index.html": [
        {
            "q": "What is the codice fiscale in Italy?",
            "a": "The codice fiscale is Italy's 16-character alphanumeric tax identification code. It is required for almost every bureaucratic transaction: opening a bank account, renting an apartment, getting a SIM card, enrolling in the SSN, filing taxes, buying property, and more. Think of it as Italy's equivalent of a US Social Security Number."
        },
        {
            "q": "How do I get a codice fiscale as an American?",
            "a": "Three options: (1) Contact your nearest Italian consulate in the US—free, takes 2–4 weeks. (2) Visit the Agenzia delle Entrate (tax office) in Italy with your passport—issued same day or within a few days. (3) Apply online via the Agenzia delle Entrate website if you already have an Italian address. There is no fee for any method."
        },
        {
            "q": "Can I get a codice fiscale before moving to Italy?",
            "a": "Yes. Contact your local Italian consulate (in New York, Chicago, Los Angeles, etc.) and request a codice fiscale before you move. You will need your passport and a completed request form. Getting it in advance speeds up critical tasks like opening a bank account remotely or signing a lease before arrival."
        },
        {
            "q": "How long does it take to get a codice fiscale?",
            "a": "At the Agenzia delle Entrate in Italy: same day or within 1–3 days. At an Italian consulate in the US: 2–6 weeks depending on the consulate and current workload. Online (if already in Italy with an address): 1–5 business days. There is no charge."
        },
        {
            "q": "Is the codice fiscale the same as a Partita IVA?",
            "a": "No. The codice fiscale is a personal identification code for all Italian residents and taxpayers. The Partita IVA is a business VAT registration number for self-employed individuals and companies. As a resident employee or retiree you only need a codice fiscale. If you work as a freelancer or run a business in Italy, you need both."
        },
    ],

    "residency/spid-italy-foreigners-americans-guide/index.html": [
        {
            "q": "What is SPID and why do Americans in Italy need it?",
            "a": "SPID (Sistema Pubblico di Identità Digitale) is Italy's national digital identity system. It lets you access all Italian government portals online—INPS (social security), Agenzia delle Entrate (tax office), permesso di soggiorno status, health services, school registration, and more. Without SPID, most Italian public-sector services are inaccessible online."
        },
        {
            "q": "Can Americans get SPID without being Italian residents?",
            "a": "You need a codice fiscale to register for SPID—which Americans can obtain from their Italian consulate before moving. However, most SPID identity providers also ask for a recent Italian document (permesso di soggiorno or residency certificate) during identity verification. In practice, most foreigners obtain SPID after getting their permesso."
        },
        {
            "q": "Which identity provider is easiest for foreigners to get SPID?",
            "a": "Poste Italiane (PosteID) is the most accessible for foreigners: you verify your identity in person at any post office using your passport and permesso di soggiorno. Namirial's video-identification (riconoscimento video) is popular for those who prefer to avoid an in-person visit. Sielte and Infocert also accept foreign documents."
        },
        {
            "q": "Is SPID required to apply for a permesso di soggiorno?",
            "a": "The permesso application itself is submitted via the post office kit and does not require SPID. However, SPID is needed to check your permesso status online, schedule Questura appointments on some regional portals, and access INPS or Agenzia delle Entrate services. Getting SPID as early as possible significantly simplifies Italian bureaucracy."
        },
        {
            "q": "How long does it take to get SPID in Italy?",
            "a": "In-person registration at Poste Italiane: same day, about 30 minutes. Online or video identification via Namirial or Infocert: 1–3 business days for verification. You receive your SPID credentials (username and one-time password generator) within 24 hours of completed verification."
        },
    ],

    # ── TAXES ────────────────────────────────────────────────────────────────

    "taxes/flat-tax-regime/index.html": [
        {
            "q": "What is Italy's €100,000 flat tax regime for new residents?",
            "a": "Italy's lump-sum tax regime (Article 24-bis TUIR) allows individuals who establish Italian tax residency to pay a single annual flat tax of €100,000 on all foreign-source income, regardless of the actual amount. It lasts for up to 15 years and replaces standard IRPEF on foreign income. Income generated in Italy is still taxed at ordinary Italian rates."
        },
        {
            "q": "Who qualifies for Italy's €100,000 flat tax?",
            "a": "You qualify if you were not an Italian tax resident in at least 9 of the 10 years before the year you apply. There is no income cap or minimum—whether you earn €200,000 or €5 million abroad, the flat tax is €100,000. Each family member can opt in for an additional €25,000/year."
        },
        {
            "q": "Does Italy's flat tax cover income earned inside Italy?",
            "a": "No. The €100,000 flat tax covers only foreign-source income. Any income generated in Italy—employment income, Italian business income, Italian rental income, Italian capital gains—remains taxable at standard IRPEF rates. US Social Security is generally treated as foreign-source income under the US-Italy tax treaty."
        },
        {
            "q": "Can I claim US-Italy tax treaty benefits while on the Italian flat tax?",
            "a": "Italy's tax authorities have clarified that flat-tax residents generally cannot claim treaty benefits on the foreign-source income covered by the flat tax, since they already pay a substitute tax on that income. Social Security and pension income may still fall under treaty protections. Consult a commercialista experienced with US-Italy dual taxation before relying on treaty provisions."
        },
        {
            "q": "How do I apply for Italy's €100,000 flat tax?",
            "a": "Elect the regime in your first Italian tax return (Modello Redditi PF) after establishing Italian residency. Check the flat-tax election box and provide supporting information. You must have registered at the Anagrafe (establishing residenza) in Italy. The election must be renewed or maintained each year by filing."
        },
    ],

    "taxes/us-italy-tax-treaty-double-taxation/index.html": [
        {
            "q": "Does Italy have a tax treaty with the United States?",
            "a": "Yes. The US-Italy Income Tax Treaty (in force since 1985, with protocols) prevents double taxation by allocating taxing rights between the two countries. It covers employment income, pensions, business profits, dividends, interest, royalties, and capital gains. Italy and the US also have a FATCA agreement requiring Italian banks to report US account holders."
        },
        {
            "q": "Do Americans living in Italy have to pay taxes in both countries?",
            "a": "The US taxes its citizens on worldwide income regardless of where they live. Italy taxes residents on worldwide income. The US-Italy treaty and the US Foreign Tax Credit (Form 1116) generally prevent double taxation—Italian taxes paid offset US tax liability on the same income. Some income types, like US Social Security, are taxed only in one country."
        },
        {
            "q": "Is US Social Security taxable in Italy?",
            "a": "Under Article 20 of the US-Italy tax treaty, US Social Security benefits paid to US citizens are taxable only in the United States—Italy has no right to tax them. This is one of the most significant treaty provisions for American retirees in Italy, making Social Security income very efficient."
        },
        {
            "q": "How does the US Foreign Tax Credit work for Americans in Italy?",
            "a": "The Foreign Tax Credit (Form 1116) lets you subtract Italian taxes paid from your US tax bill, dollar for dollar, up to the US tax owed on that income. If your Italian effective tax rate is higher than your US rate on the same income, you typically owe nothing extra to the IRS. It does not eliminate the US filing obligation, just the double tax."
        },
        {
            "q": "What is the Foreign Earned Income Exclusion and can Americans in Italy use it?",
            "a": "The Foreign Earned Income Exclusion (Form 2555) excludes up to $126,500 (2024) of foreign earned income from US tax. Americans in Italy can use it, but it does not apply to passive income (dividends, pensions, Social Security). Because Italy's tax rates are high, many expats in Italy find the Foreign Tax Credit more effective than the FEIE."
        },
    ],

    "taxes/irpef-tax-brackets-italy-2025-americans/index.html": [
        {
            "q": "What are Italy's income tax (IRPEF) rates for 2025?",
            "a": "Italy's 2025 IRPEF brackets are: 23% on income up to €28,000; 35% on income from €28,001 to €50,000; 43% on income above €50,000. Regional and municipal surtaxes add 1–3% depending on your region. Deductions and tax credits reduce the effective rate well below the top marginal rate for most residents."
        },
        {
            "q": "Do Americans living in Italy pay Italian income tax?",
            "a": "Yes, if you are an Italian tax resident—meaning you spent 183+ days in Italy in a calendar year, or Italy is your primary domicile or place of habitual abode. Italian tax residents pay IRPEF on worldwide income. US taxes paid can be credited against Italian taxes under the US-Italy tax treaty and Italy's own unilateral foreign tax credit rules."
        },
        {
            "q": "What tax deductions are available to American expats in Italy?",
            "a": "Common Italian tax deductions include: a 19% tax credit on medical expenses above €129, a 19% credit on mortgage interest, a 50–65% credit on home renovation costs, deductions for dependent family members, and voluntary pension (previdenza complementare) contributions. Italian tax law is complex and a commercialista familiar with US-Italy dual-taxation is strongly recommended."
        },
        {
            "q": "What is the regional income tax surtax (addizionale regionale) in Italy?",
            "a": "Italian regions impose a surtax on IRPEF income ranging from 1.23% (minimum by law, applied in Trento and Bolzano) to 3.33% in regions with high healthcare spending. Most regions charge 1.23–2.03%. The regional surtax is calculated on the same taxable base as IRPEF and paid together with it."
        },
        {
            "q": "When must Americans in Italy file an Italian tax return?",
            "a": "Italy's tax year runs January 1–December 31. Self-employed individuals and those with foreign income file Modello Redditi PF by November 30 of the following year. Employees whose income is fully withheld at source by an Italian employer may not need to file. If in doubt—especially with US income streams—consult a commercialista."
        },
    ],

    "taxes/fbar-fatca-americans-italy-guide/index.html": [
        {
            "q": "What is FBAR and do Americans in Italy need to file it?",
            "a": "FBAR (FinCEN Form 114) is the Foreign Bank Account Report required of any US citizen or resident holding foreign financial accounts with an aggregate value exceeding $10,000 at any point during the calendar year. Americans living in Italy with Italian bank accounts, brokerage accounts, or pension accounts almost certainly need to file FBAR annually—by April 15, extendable to October 15."
        },
        {
            "q": "What is FATCA and how does it affect Americans in Italy?",
            "a": "FATCA (Foreign Account Tax Compliance Act) requires US citizens to report foreign financial assets over certain thresholds on Form 8938 with their annual tax return: $200,000 for single filers living abroad at year-end (or $300,000 at any point in the year). Italy has a FATCA inter-governmental agreement (IGA) with the US, meaning Italian banks automatically report US account holders to the IRS."
        },
        {
            "q": "What is the penalty for not filing FBAR?",
            "a": "Non-willful FBAR violations can result in penalties of up to $10,000 per violation per year. Willful violations: up to the greater of $100,000 or 50% of account value per violation, plus potential criminal prosecution. The IRS offers voluntary disclosure programmes (such as the Streamlined Foreign Offshore Procedure) for Americans who are behind on filings."
        },
        {
            "q": "Do Italian bank accounts count for FBAR reporting?",
            "a": "Yes. Any Italian conto corrente (checking account), investment or brokerage account, or Italian pension account must be reported on FBAR if the aggregate of all foreign accounts exceeds $10,000 at any point in the year. This includes accounts held jointly with an Italian spouse."
        },
        {
            "q": "Can an Italian commercialista help with FBAR and FATCA?",
            "a": "A standard Italian commercialista handles Italian taxes only and is not qualified to prepare US tax forms. For FBAR and FATCA, you need a US-licensed CPA or tax attorney specialising in expat taxation. Several firms in Milan and Rome—and many US-based practices—specialise in US-Italy dual-taxation, including FBAR, FATCA, Form 8938, and Foreign Tax Credit planning."
        },
    ],

    # ── HEALTHCARE ───────────────────────────────────────────────────────────

    "healthcare/enroll-italian-ssn/index.html": [
        {
            "q": "Who can enroll in Italy's National Health Service (SSN)?",
            "a": "Legal residents of Italy can enroll in the SSN (Servizio Sanitario Nazionale). This includes holders of a valid permesso di soggiorno—elective residence, digital nomad, family reunification, work permit, long-term or permanent residency. Tourists and individuals on stays of fewer than 90 days cannot enroll."
        },
        {
            "q": "How do I enroll in Italy's SSN as an American?",
            "a": "Bring your permesso di soggiorno (or the post office receipt if your card hasn't arrived yet), codice fiscale, and passport to the local ASL (Azienda Sanitaria Locale). Request iscrizione al SSN. You will choose a family doctor (medico di base) from the ASL's list. The Tessera Sanitaria health card arrives by mail within 2–4 weeks."
        },
        {
            "q": "Is Italy's SSN free for Americans on an Elective Residence Visa?",
            "a": "For most employed workers and their dependents, SSN coverage is free. Elective Residence Visa holders enroll voluntarily and pay an annual contribution of approximately €400–€1,500 depending on income. This is far less than US private insurance premiums and covers essentially all primary and specialist care."
        },
        {
            "q": "What does Italy's SSN cover for expats?",
            "a": "The SSN covers: GP visits (free), specialist visits with a small co-pay called a ticket (typically €10–€60), emergency room care (free or low co-pay), hospitalisation and surgery (free), and most prescription drugs (free or low co-pay). Dental care is mostly private for adults, though children and certain chronic conditions receive partial public coverage."
        },
        {
            "q": "How quickly can I use Italy's SSN after enrolling?",
            "a": "There is no waiting period. From the day you register at the ASL and are assigned a medico di base, you can use SSN services. The ASL typically issues a temporary certificate on the spot, which is valid for the same purposes as the Tessera Sanitaria card while the card is being printed and mailed."
        },
    ],

    "healthcare/tessera-sanitaria-italy-health-card-americans/index.html": [
        {
            "q": "What is the Tessera Sanitaria?",
            "a": "The Tessera Sanitaria is Italy's national health card, combining an identification card with a European Health Insurance Card (EHIC). It is issued to everyone enrolled in Italy's SSN and is required to access your family doctor (medico di base), request prescriptions, and book specialist visits through the public health system."
        },
        {
            "q": "How do I get a Tessera Sanitaria as an American?",
            "a": "Once you enroll in the SSN at your local ASL office, the Tessera Sanitaria is automatically issued. Bring your permesso di soggiorno (or receipt), codice fiscale, and passport. The card is mailed to your Italian address within 2–4 weeks. The ASL gives you a temporary certificate immediately after enrollment."
        },
        {
            "q": "What is the European Health Insurance Card (EHIC) on the Tessera Sanitaria?",
            "a": "The reverse of the Italian Tessera Sanitaria contains the EHIC, which entitles you to state-provided healthcare in any EU or EEA country at local rates. As a US citizen enrolled in Italy's SSN, your Italian EHIC is a major benefit—it means free or low-cost emergency and necessary healthcare throughout the EU."
        },
        {
            "q": "Do I need the Tessera Sanitaria for emergencies in Italy?",
            "a": "No. Italian emergency rooms (Pronto Soccorso) treat all patients regardless of whether they have a Tessera Sanitaria or health insurance. The card is needed for scheduled appointments, prescriptions, and non-emergency specialist or GP visits through the SSN. Genuine emergencies are covered for everyone."
        },
        {
            "q": "How long is the Tessera Sanitaria valid?",
            "a": "For Italian citizens, it is valid 6 years. For non-EU residents, it is valid for the duration of your permesso di soggiorno. When you renew your permesso, your health card coverage is automatically extended. If you move or change status, update your information at the ASL."
        },
    ],

    # ── COST OF LIVING ───────────────────────────────────────────────────────

    "cost-of-living/cost-of-living-italy-vs-usa/index.html": [
        {
            "q": "Is Italy cheaper than the USA to live in?",
            "a": "Yes. Italy is generally 30–50% cheaper than major US cities for most everyday expenses. Groceries cost 35–45% less, dining out 50–60% less, and public healthcare is essentially free for legal residents (vs. $400–$800/month in US premiums). Housing is comparable to mid-tier US cities—cheaper than NYC or San Francisco, similar to Denver or Austin."
        },
        {
            "q": "How much does it cost to live in Italy per month as an American?",
            "a": "A comfortable lifestyle in a medium-sized Italian city costs €1,800–€2,800/month for a single person, including rent. In smaller southern cities like Lecce or Catanzaro, €1,200–€1,600/month is realistic. In Milan, budget €2,800–€4,000/month. These figures assume SSN enrollment for healthcare."
        },
        {
            "q": "What are the biggest cost differences between Italy and the USA?",
            "a": "Healthcare is the starkest difference—SSN coverage costs €400–€1,500/year for Elective Residence Visa holders versus $400–$800/month in US premiums. Food costs 35–40% less. Eating out is dramatically cheaper: a sit-down lunch costs €10–€15 versus $20–$30 in the US. Public transit eliminates the need for a car in most Italian cities."
        },
        {
            "q": "Is US Social Security enough to live on in Italy?",
            "a": "The average US Social Security benefit (approximately $1,800/month in 2025) is enough to live comfortably in southern Italy or smaller northern cities. Combined with low healthcare costs and affordable food, many American retirees find that Italian living expenses run 40–50% below their US baseline."
        },
        {
            "q": "What hidden costs should Americans budget for when moving to Italy?",
            "a": "Key hidden costs include: visa and permesso di soggiorno fees (€200–€400/year), marca da bollo revenue stamps (€16 each, required frequently for bureaucratic documents), Italian income taxes on Italian-source income, and apostille and translation fees ($200–$600+) for documents. Private health insurance before SSN enrollment costs €150–€400/month."
        },
    ],

    "cost-of-living/retire-italy-2000-month-budget/index.html": [
        {
            "q": "Can you really retire in Italy on $2,000 a month?",
            "a": "Yes, in southern Italy and smaller cities—it is entirely feasible. Cities like Lecce, Catanzaro, Palermo, Matera, and inland Umbria or Le Marche offer comfortable lifestyles at €1,200–€1,600/month. This covers a decent 1-bedroom apartment (€400–€600), food (€300–€400), transport, utilities, and healthcare through Italy's SSN."
        },
        {
            "q": "Which Italian cities are most affordable for American retirees?",
            "a": "The most affordable regions are Calabria, Sicily, Puglia, Basilicata, and inland Umbria and Le Marche. Lecce and Catanzaro are routinely among Italy's cheapest livable cities. Even regional capitals like Bari, Palermo, and Reggio Calabria are significantly cheaper than Rome or Milan."
        },
        {
            "q": "What does average rent cost for American retirees in Italy?",
            "a": "Rent varies widely. In Lecce or Catanzaro: €350–€550/month for a 1-bedroom. In Rome: €1,100–€1,700/month. In Milan: €1,400–€2,200/month. Long-term leases (4+4 years) are typically 15–25% cheaper than short-term furnished expat-targeted apartments."
        },
        {
            "q": "Is US Social Security taxed in Italy?",
            "a": "Under the US-Italy tax treaty, US Social Security benefits paid to US citizens are taxable only in the US—Italy cannot tax them. This makes Social Security income very efficient for American retirees in Italy. Other US pension income (private pensions, IRA withdrawals) is generally taxable in Italy at standard IRPEF rates."
        },
        {
            "q": "What visa allows Americans to retire to Italy on a fixed income?",
            "a": "The Elective Residence Visa is the standard path, requiring at least €31,000/year in passive income. If you qualify for Italy's €100,000 flat tax regime—which requires no Italian tax residency in 9 of the last 10 years—you can pay a fixed annual sum on all foreign income regardless of amount. The combination of Elective Residence Visa and flat tax is highly attractive for American retirees with substantial incomes."
        },
    ],

    "cost-of-living/cost-of-living-milan/index.html": [
        {
            "q": "What is the cost of living in Milan for Americans in 2025?",
            "a": "Milan is Italy's most expensive city but still 30–40% cheaper than New York or San Francisco. Typical monthly costs: 1-bedroom in the city centre €1,400–€2,200, groceries €250–€400, a mid-range dinner €15–€25 per person, monthly ATM transit pass €39, and utilities €120–€180. Total comfortable lifestyle: €3,000–€4,500/month."
        },
        {
            "q": "Is Milan affordable for American expats?",
            "a": "Milan is the priciest Italian city but far cheaper than comparable European financial capitals (London, Paris, Zurich) or US tech hubs. If you earn a US salary or have US retirement income, Milan is very affordable. The city also has excellent English-language infrastructure, international schools, and a strong expat community."
        },
        {
            "q": "How much does rent cost in Milan in 2025?",
            "a": "2025 Milan rents: 1-bedroom city centre (Brera, Navigli, Porta Venezia) €1,400–€2,200/month; 1-bedroom outside centre €900–€1,400/month; 2-bedroom city centre €2,000–€3,200/month. Shared apartments (coliving or flatshare) start at €600–€900 per room including utilities."
        },
        {
            "q": "What are the most affordable neighborhoods in Milan?",
            "a": "More affordable Milan neighborhoods include Nolo (North of Loreto), Quarto Oggiaro, Corvetto, Bovisa, and Sesto San Giovanni (just outside the city limits, Metro Line 1). These areas are well-served by metro but have rents 30–40% below central Milan. Trendy but cheaper: Isola and parts of Porta Garibaldi."
        },
        {
            "q": "How does the cost of living in Milan compare to Rome?",
            "a": "Milan and Rome are similar overall, with Milan slightly more expensive for rent (+10–15%) and dining. Rome may have higher transport costs due to less efficient public transit. Both cities cost 2–3× more than equivalent housing in southern Italian cities like Lecce, Catanzaro, or Palermo."
        },
    ],

    # ── PROPERTY ─────────────────────────────────────────────────────────────

    "property/how-to-buy-property-italy-american-guide/index.html": [
        {
            "q": "Can Americans buy property in Italy?",
            "a": "Yes. Americans can buy property in Italy on the same terms as Italian citizens, with one caveat: the US-Italy treaty of friendship (1948) grants reciprocal rights, so Americans can own Italian property without needing to be residents. No special permits are required, though you will need a codice fiscale and Italian bank account to complete the purchase."
        },
        {
            "q": "What are the steps to buying property in Italy as an American?",
            "a": "The key steps are: (1) obtain a codice fiscale; (2) find a property and negotiate a price; (3) sign a preliminary contract (compromesso) with a deposit of 10–30%; (4) conduct due diligence via a geometra or lawyer; (5) sign the final deed (rogito) before an Italian notary; (6) register the deed with the land registry (Catasto). The entire process takes 2–6 months."
        },
        {
            "q": "What taxes do Americans pay when buying property in Italy?",
            "a": "For a primary residence (prima casa): 2% registro tax on the cadastral value (not the sale price) plus €200 in fixed taxes. For a non-primary or investment property: 9% registro tax plus fixed taxes. New builds (from developers) pay 4–10% VAT instead. Total purchase taxes typically add 3–10% to the property price depending on category."
        },
        {
            "q": "Do I need an Italian lawyer to buy property in Italy?",
            "a": "An Italian notary is legally required and acts as a neutral public official—not your advocate. While not legally mandatory, hiring an independent Italian property lawyer (avvocato) is strongly recommended to review the compromesso, conduct title searches, verify planning permissions (concessioni edilizie), and protect your interests before signing. Budget €1,500–€3,000 for legal representation."
        },
        {
            "q": "Can I get a mortgage in Italy as an American non-resident?",
            "a": "Italian banks do offer mortgages to non-resident foreigners, but with stricter conditions: typically a maximum of 60% LTV (vs. 80% for residents), higher interest rates, and more documentation. Banks require proof of income, Italian codice fiscale, property valuation, and in many cases an Italian guarantor. Specialist brokers who work with expats can help navigate the process."
        },
    ],
}


# ---------------------------------------------------------------------------
# Helper: build FAQPage JSON-LD string
# ---------------------------------------------------------------------------

def build_faq_jsonld(faqs: list) -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq["q"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq["a"]
                }
            }
            for faq in faqs
        ]
    }
    return '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(',', ':')) + '</script>'


# ---------------------------------------------------------------------------
# Helper: inject JSON-LD before </head>
# ---------------------------------------------------------------------------

def inject_schema(html: str, jsonld: str) -> tuple[str, bool]:
    """Returns (new_html, changed). Does nothing if FAQPage already present."""
    if '"@type":"FAQPage"' in html or '"@type": "FAQPage"' in html:
        return html, False
    idx = html.lower().rfind('</head>')
    if idx < 0:
        return html, False
    return html[:idx] + jsonld + '\n' + html[idx:], True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    changed = 0
    skipped_existing = 0
    missing_files = []

    for rel_path, faqs in FAQ_DATA.items():
        path = ROOT / rel_path
        if not path.exists():
            missing_files.append(rel_path)
            continue

        html = path.read_text(encoding="utf-8", errors="replace")
        jsonld = build_faq_jsonld(faqs)
        new_html, did_change = inject_schema(html, jsonld)

        if not did_change:
            skipped_existing += 1
            continue

        changed += 1
        mode = "DRY-RUN" if DRY_RUN else "  UPDATED"
        print(f"{mode}  {rel_path}  ({len(faqs)} Q&As)")

        if not DRY_RUN:
            path.write_text(new_html, encoding="utf-8")

    print()
    mode_label = "DRY-RUN" if DRY_RUN else "APPLIED"
    print(f"[{mode_label}] {changed} files {'would be' if DRY_RUN else 'were'} modified")
    if skipped_existing:
        print(f"  {skipped_existing} files skipped (FAQPage already present)")
    if missing_files:
        print(f"  {len(missing_files)} files not found on disk:")
        for f in missing_files:
            print(f"    missing: {f}")


if __name__ == "__main__":
    main()
