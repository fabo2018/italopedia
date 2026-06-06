#!/usr/bin/env python3
"""
fix_internal_links_v2.py
Operazione in due fasi:
  Phase 1: 50 articoli senza related-section → aggiunge related-section + nuovo footer
  Phase 2: 9 articoli con old footer ma related-section già presente → solo footer upgrade
Totale: 59 file modificati.
"""

import re, os, sys

BASE = '/Users/fabrizio/italopedia/'

# ── NEW FOOTER (standard, depth-2, tutte le pagine articolo usano ../../) ───
NEW_FOOTER = '<footer class="footer"><div class="footer-inner">\n    <div class="footer-top">\n      <div class="footer-brand-col">\n        <a href="../../" class="footer-logo">Italo<span>pedia</span></a>\n        <p class="footer-brand-desc">The complete English-language reference for Americans moving to and living in Italy. Written from a small town in Piedmont, verified against official Italian sources.</p>\n        <span class="footer-stamp">📍 Piedmont, Italy</span>\n      </div>\n      <div><div class="footer-col-title">Categories</div><ul class="footer-links"><li><a href="../../visas/">Visas<span class="footer-count">15</span></a></li><li><a href="../../residency/">Residency<span class="footer-count">17</span></a></li><li><a href="../../taxes/">Taxes<span class="footer-count">17</span></a></li><li><a href="../../healthcare/">Healthcare<span class="footer-count">12</span></a></li><li><a href="../../property/">Property<span class="footer-count">13</span></a></li><li><a href="../../citizenship/">Citizenship<span class="footer-count">11</span></a></li><li><a href="../../regions/">Regions<span class="footer-count">15</span></a></li><li><a href="../../cost-of-living/">Cost of Living<span class="footer-count">12</span></a></li></ul></div>\n      <div><div class="footer-col-title">Resources</div><ul class="footer-links"><li><a href="../../newsletter/">Newsletter</a></li><li><a href="../../shop/">Shop guides</a></li><li><a href="../../consult/">Book a 1:1 consult</a></li><li><a href="../../resources/">Free resources</a></li><li><a href="../../checklist/">Free checklist</a></li><li><a href="../../about/">About Fabrizio</a></li><li><a href="../../contact/">Contact</a></li></ul></div>\n      <div><div class="footer-col-title">Popular guides</div><ul class="footer-links"><li><a href="../../visas/elective-residence-visa/"><span class="footer-guide-cat">Visas</span>Elective Residence Visa</a></li><li><a href="../../taxes/flat-tax-regime/"><span class="footer-guide-cat">Taxes</span>Italy Flat Tax Regime</a></li><li><a href="../../citizenship/jure-sanguinis/"><span class="footer-guide-cat">Citizenship</span>Citizenship by Descent</a></li><li><a href="../../residency/permesso-di-soggiorno/"><span class="footer-guide-cat">Residency</span>Permesso di Soggiorno</a></li><li><a href="../../visas/digital-nomad-visa/"><span class="footer-guide-cat">Visas</span>Digital Nomad Visa</a></li><li><a href="../../healthcare/best-health-insurance-americans-italy/"><span class="footer-guide-cat">Healthcare</span>Health Insurance</a></li><li><a href="../../property/1-euro-house-italy/"><span class="footer-guide-cat">Property</span>1-Euro House Programs</a></li></ul></div>\n    </div>\n        <div class="footer-newsletter" style="border-top:1px solid var(--color-border,#2a2520);padding:1.5rem 0 1rem;margin-top:.5rem">\n      <p style="font-size:.85rem;color:rgba(250,247,240,.55);margin:0 0 .75rem;font-family:var(--font-heading,\'Syne\'),sans-serif;letter-spacing:.04em;text-transform:uppercase">Free weekly guide — join 4,200+ readers</p>\n      <form class="kit-form" onsubmit="kitSubscribe(this,event)" novalidate>\n      <div class="kit-row">\n        <input class="kit-input" type="email" name="email_address" placeholder="your@email.com" required aria-label="Email address">\n        <button class="kit-btn" type="submit">Subscribe →</button>\n      </div>\n      <span class="kit-msg" aria-live="polite"></span>\n    </form>\n    </div>\n    <div class="footer-bottom">\n      <div class="footer-copy">© <span data-year>2026</span> Italopedia · All rights reserved · Made with espresso in Piedmont</div>\n      <div class="footer-legal">\n      <a href="../../privacy/">Privacy Policy</a>\n      <a href="../../terms/">Terms</a>\n      <a href="../../cookies/">Cookie Policy</a>\n      <a href="../../affiliate-disclosure/">Affiliate Disclosure</a>\n      <a href="../../disclaimer/">Disclaimer</a>\n      <button class="cc-footer-btn" onclick="italopediaConsent.openModal()">Cookie Settings</button>\n    </div>\n    </div>\n  </div></footer>'

# ── MAPPA SEMANTICA: slug → 3 articoli correlati (href, categoria, titolo) ───
# Regole seguite:
# 1. Ogni articolo linka a 3 articoli tematicamente rilevanti
# 2. Si privilegiano articoli orfani (0 incoming) come destinazioni dove pertinente
# 3. Nessun articolo linka a se stesso
# 4. I percorsi usano ../../ (depth-2 standard)

RELATED_MAP = {

    # ── CITIZENSHIP ──────────────────────────────────────────────────────────
    'citizenship/2024-italian-citizenship-reform/': [
        ('../../citizenship/jure-sanguinis/', 'Citizenship',
         'Italian Citizenship by Descent: Complete 2025 Guide'),
        ('../../citizenship/jure-sanguinis-document-checklist/', 'Citizenship',
         'Jure Sanguinis Document Checklist: Every Document You Need in 2025'),
        ('../../citizenship/citizenship-court-vs-consulate-route/', 'Citizenship',
         'Court Route vs Consulate Route: Which Is Right for You?'),
    ],
    'citizenship/aire-registration-italians-abroad/': [
        ('../../citizenship/jure-sanguinis/', 'Citizenship',
         'Italian Citizenship by Descent: Complete 2025 Guide'),
        ('../../residency/how-to-register-anagrafe-italy-americans/', 'Residency',
         'How to Register at the Anagrafe in Italy'),
        ('../../citizenship/italian-citizenship-by-marriage/', 'Citizenship',
         'Italian Citizenship by Marriage: Complete Guide for Americans'),
    ],
    'citizenship/b1-italian-language-requirement/': [
        ('../../citizenship/italian-citizenship-10-years-residency-naturalization/', 'Citizenship',
         'Italian Citizenship by 10 Years Residency: The Naturalization Route'),
        ('../../citizenship/italian-citizenship-by-marriage/', 'Citizenship',
         'Italian Citizenship by Marriage: Complete Guide for Americans'),
        ('../../citizenship/jure-sanguinis/', 'Citizenship',
         'Italian Citizenship by Descent: Complete 2025 Guide'),
    ],
    'citizenship/italian-passport-application/': [
        ('../../citizenship/jure-sanguinis/', 'Citizenship',
         'Italian Citizenship by Descent: Complete 2025 Guide'),
        ('../../citizenship/2024-italian-citizenship-reform/', 'Citizenship',
         '2024 Italian Citizenship Reform: What Actually Changed'),
        ('../../citizenship/citizenship-court-vs-consulate-route/', 'Citizenship',
         'Court Route vs Consulate Route: Which Is Right for You?'),
    ],
    'citizenship/jure-sanguinis-document-checklist/': [
        ('../../citizenship/jure-sanguinis/', 'Citizenship',
         'Italian Citizenship by Descent: Complete 2025 Guide'),
        ('../../citizenship/2024-italian-citizenship-reform/', 'Citizenship',
         '2024 Italian Citizenship Reform: What Actually Changed'),
        ('../../citizenship/apostille-document-translation-italy/', 'Citizenship',
         'Apostille & Document Translation for Italy: Complete American Guide'),
    ],

    # ── COST OF LIVING ────────────────────────────────────────────────────────
    'cost-of-living/cost-of-living-bologna/': [
        ('../../cost-of-living/cost-of-living-italy-vs-usa/', 'Cost of Living',
         'Cost of Living: Italy vs USA — What Americans Actually Save'),
        ('../../regions/florence-vs-rome-vs-bologna/', 'Regions',
         'Florence vs Rome vs Bologna: Which Italian City Is Best for Expats?'),
        ('../../cost-of-living/italy-rent-prices-city-comparison/', 'Cost of Living',
         'Italy Rent Prices by City: Complete 2025 Comparison for Americans'),
    ],
    'cost-of-living/cost-of-living-lecce/': [
        ('../../cost-of-living/cost-of-living-italy-vs-usa/', 'Cost of Living',
         'Cost of Living: Italy vs USA — What Americans Actually Save'),
        ('../../regions/living-puglia-american-expat/', 'Regions',
         'Living in Puglia as an American Expat: The Full Honest Guide'),
        ('../../cost-of-living/italy-rent-prices-city-comparison/', 'Cost of Living',
         'Italy Rent Prices by City: Complete 2025 Comparison for Americans'),
    ],
    'cost-of-living/hidden-costs-living-italy/': [
        ('../../cost-of-living/cost-of-living-italy-vs-usa/', 'Cost of Living',
         'Cost of Living: Italy vs USA — What Americans Actually Save'),
        ('../../taxes/us-italy-tax-treaty-double-taxation/', 'Taxes',
         'US-Italy Tax Treaty: How Double Taxation Works for Americans'),
        ('../../visas/elective-residence-visa/', 'Visas',
         'Elective Residence Visa Italy: The Complete 2025 Guide'),
    ],
    'cost-of-living/italy-vs-spain-vs-portugal-cost/': [
        ('../../cost-of-living/cost-of-living-italy-vs-usa/', 'Cost of Living',
         'Cost of Living: Italy vs USA — What Americans Actually Save'),
        ('../../cost-of-living/living-italy-2500-month/', 'Cost of Living',
         'Living in Italy on $2,500/Month: Is It Really Possible in 2025?'),
        ('../../cost-of-living/retire-italy-2000-month-budget/', 'Cost of Living',
         'Retiring in Italy on $2,000/Month: Complete Budget Guide'),
    ],

    # ── HEALTHCARE ────────────────────────────────────────────────────────────
    'healthcare/chronic-conditions-italy-expats/': [
        ('../../healthcare/enroll-italian-ssn/', 'Healthcare',
         "How to Enroll in Italy's National Health Service (SSN)"),
        ('../../healthcare/tessera-sanitaria-italy-health-card-americans/', 'Healthcare',
         "Tessera Sanitaria: How to Get Italy's Health Card as an American"),
        ('../../healthcare/specialist-visits-italy-referral/', 'Healthcare',
         'Specialist Visits in Italy: How the Referral System Works'),
    ],
    'healthcare/dental-care-italy-americans/': [
        ('../../healthcare/best-health-insurance-americans-italy/', 'Healthcare',
         'Best Health Insurance for Americans in Italy: 2025 Guide'),
        ('../../healthcare/enroll-italian-ssn/', 'Healthcare',
         "How to Enroll in Italy's National Health Service (SSN)"),
        ('../../cost-of-living/healthcare-costs-italy-vs-usa/', 'Cost of Living',
         'Healthcare Costs in Italy vs USA: What Americans Actually Pay'),
    ],
    'healthcare/emergency-room-italy-pronto-soccorso/': [
        ('../../healthcare/enroll-italian-ssn/', 'Healthcare',
         "How to Enroll in Italy's National Health Service (SSN)"),
        ('../../healthcare/tessera-sanitaria-italy-health-card-americans/', 'Healthcare',
         "Tessera Sanitaria: How to Get Italy's Health Card as an American"),
        ('../../healthcare/mental-health-care-italy/', 'Healthcare',
         'Mental Health Care in Italy: Public and Private Options for Americans'),
    ],
    'healthcare/mental-health-care-italy/': [
        ('../../healthcare/best-health-insurance-americans-italy/', 'Healthcare',
         'Best Health Insurance for Americans in Italy: 2025 Guide'),
        ('../../healthcare/best-private-health-insurance-italy-americans-2025/', 'Healthcare',
         'Best Private Health Insurance for Americans in Italy: 2025 Comparison'),
        ('../../healthcare/top-private-hospitals-italy/', 'Healthcare',
         'Top Private Hospitals in Italy: Where Americans Go'),
    ],
    'healthcare/specialist-visits-italy-referral/': [
        ('../../healthcare/enroll-italian-ssn/', 'Healthcare',
         "How to Enroll in Italy's National Health Service (SSN)"),
        ('../../healthcare/tessera-sanitaria-italy-health-card-americans/', 'Healthcare',
         "Tessera Sanitaria: How to Get Italy's Health Card as an American"),
        ('../../healthcare/chronic-conditions-italy-expats/', 'Healthcare',
         'Chronic Conditions in Italy: Diabetes, Hypertension for American Expats'),
    ],
    'healthcare/top-private-hospitals-italy/': [
        ('../../healthcare/best-private-health-insurance-italy-americans-2025/', 'Healthcare',
         'Best Private Health Insurance for Americans in Italy: 2025 Comparison'),
        ('../../healthcare/cigna-vs-axa-vs-allianz-italy/', 'Healthcare',
         'Cigna vs AXA vs Allianz: Best International Health Insurance for Italy'),
        ('../../healthcare/emergency-room-italy-pronto-soccorso/', 'Healthcare',
         'Emergency Room in Italy (Pronto Soccorso): What Americans Need to Know'),
    ],

    # ── PROPERTY ──────────────────────────────────────────────────────────────
    'property/buying-property-puglia/': [
        ('../../property/how-to-buy-property-italy-american-guide/', 'Property',
         'How to Buy Property in Italy as an American: Complete 2025 Guide'),
        ('../../regions/living-puglia-american-expat/', 'Regions',
         'Living in Puglia as an American Expat: The Full Honest Guide'),
        ('../../property/italian-notary-process/', 'Property',
         'The Italian Notary Process: How Property Buying Works in Italy'),
    ],
    'property/compromesso-preliminary-contract-italy/': [
        ('../../property/how-to-buy-property-italy-american-guide/', 'Property',
         'How to Buy Property in Italy as an American: Complete 2025 Guide'),
        ('../../property/italian-notary-process/', 'Property',
         'The Italian Notary Process: How Property Buying Works in Italy'),
        ('../../property/property-purchase-taxes-italy/', 'Property',
         'Property Purchase Taxes in Italy: Exact Calculation'),
    ],
    'property/italian-lease-types-explained/': [
        ('../../property/renting-apartment-italy-expat-guide/', 'Property',
         "Renting an Apartment in Italy: The American Expat's Complete Guide"),
        ('../../property/renting-out-property-italy-cedolare-secca/', 'Property',
         'Renting Out Property in Italy: Cedolare Secca vs Ordinary Regime'),
        ('../../residency/how-to-register-anagrafe-italy-americans/', 'Residency',
         'How to Register at the Anagrafe in Italy'),
    ],
    'property/property-purchase-taxes-italy/': [
        ('../../property/how-to-buy-property-italy-american-guide/', 'Property',
         'How to Buy Property in Italy as an American: Complete 2025 Guide'),
        ('../../property/compromesso-preliminary-contract-italy/', 'Property',
         "The Compromesso: Italy's Preliminary Sale Contract Explained"),
        ('../../property/italian-notary-process/', 'Property',
         'The Italian Notary Process: How Property Buying Works in Italy'),
    ],
    'property/renovating-italian-stone-house/': [
        ('../../property/how-to-buy-property-italy-american-guide/', 'Property',
         'How to Buy Property in Italy as an American: Complete 2025 Guide'),
        ('../../property/1-euro-house-italy/', 'Property',
         "Italy's €1 House Programs: What's Real and How to Actually Do It"),
        ('../../property/best-cities-invest-property-italy/', 'Property',
         "Best Cities to Invest in Italian Property: An American's Guide"),
    ],
    'property/renting-out-property-italy-cedolare-secca/': [
        ('../../property/italian-lease-types-explained/', 'Property',
         'Italian Lease Types Explained: 4+4, 3+2, Transitorio, Cedolare Secca'),
        ('../../property/short-term-rentals-italy-rules/', 'Property',
         'Short-Term Rentals in Italy: Rules, Taxes, and Airbnb Reality'),
        ('../../taxes/imu-property-tax-italy/', 'Taxes',
         'IMU Property Tax in Italy: When You Owe It and How to Calculate'),
    ],
    'property/short-term-rentals-italy-rules/': [
        ('../../property/renting-out-property-italy-cedolare-secca/', 'Property',
         'Renting Out Property in Italy: Cedolare Secca vs Ordinary Regime'),
        ('../../property/italian-lease-types-explained/', 'Property',
         'Italian Lease Types Explained: 4+4, 3+2, Transitorio, Cedolare Secca'),
        ('../../taxes/imu-property-tax-italy/', 'Taxes',
         'IMU Property Tax in Italy: When You Owe It and How to Calculate'),
    ],

    # ── REGIONS ───────────────────────────────────────────────────────────────
    'regions/best-cities-remote-workers-italy/': [
        ('../../visas/digital-nomad-visa/', 'Visas',
         'Italy Digital Nomad Visa: Requirements & Application (2025)'),
        ('../../regions/best-cities-american-expats-italy/', 'Regions',
         'Best Cities for American Expats in Italy: The Honest 2025 Guide'),
        ('../../cost-of-living/cost-of-living-italy-vs-usa/', 'Cost of Living',
         'Cost of Living: Italy vs USA — What Americans Actually Save'),
    ],
    'regions/best-coastal-towns-italy-year-round/': [
        ('../../regions/best-cities-american-expats-italy/', 'Regions',
         'Best Cities for American Expats in Italy: The Honest 2025 Guide'),
        ('../../regions/living-sardinia-american-expat/', 'Regions',
         'Living in Sardinia as an American Expat: Beyond the Tourist Beaches'),
        ('../../regions/best-small-towns-italy-retirees/', 'Regions',
         'Best Small Towns in Italy for American Retirees: 2025 Guide'),
    ],
    'regions/best-italian-cities-families/': [
        ('../../regions/best-cities-american-expats-italy/', 'Regions',
         'Best Cities for American Expats in Italy: The Honest 2025 Guide'),
        ('../../regions/living-veneto-venice-verona/', 'Regions',
         'Living in Veneto: Venice, Verona, and Padua for American Expats'),
        ('../../cost-of-living/cost-of-living-italy-vs-usa/', 'Cost of Living',
         'Cost of Living: Italy vs USA — What Americans Actually Save'),
    ],
    'regions/living-puglia-american-expat/': [
        ('../../property/buying-property-puglia/', 'Property',
         'Buying Property in Puglia: Trulli, Masserie, and the Coastal Market'),
        ('../../regions/best-cities-american-expats-italy/', 'Regions',
         'Best Cities for American Expats in Italy: The Honest 2025 Guide'),
        ('../../cost-of-living/cost-of-living-lecce/', 'Cost of Living',
         'Cost of Living in Lecce 2025: Southern Italy on a Budget'),
    ],
    'regions/living-sardinia-american-expat/': [
        ('../../regions/best-cities-american-expats-italy/', 'Regions',
         'Best Cities for American Expats in Italy: The Honest 2025 Guide'),
        ('../../regions/best-coastal-towns-italy-year-round/', 'Regions',
         'Best Italian Coastal Towns for Year-Round Living'),
        ('../../cost-of-living/cost-of-living-italy-vs-usa/', 'Cost of Living',
         'Cost of Living: Italy vs USA — What Americans Actually Save'),
    ],
    'regions/living-veneto-venice-verona/': [
        ('../../regions/best-cities-american-expats-italy/', 'Regions',
         'Best Cities for American Expats in Italy: The Honest 2025 Guide'),
        ('../../regions/best-italian-cities-families/', 'Regions',
         'Best Italian Cities for Families with Children in 2025'),
        ('../../cost-of-living/cost-of-living-italy-vs-usa/', 'Cost of Living',
         'Cost of Living: Italy vs USA — What Americans Actually Save'),
    ],
    'regions/test-living-italy-before-moving/': [
        ('../../visas/elective-residence-visa/', 'Visas',
         'Elective Residence Visa Italy: The Complete 2025 Guide'),
        ('../../regions/best-cities-american-expats-italy/', 'Regions',
         'Best Cities for American Expats in Italy: The Honest 2025 Guide'),
        ('../../cost-of-living/cost-of-living-italy-vs-usa/', 'Cost of Living',
         'Cost of Living: Italy vs USA — What Americans Actually Save'),
    ],

    # ── RESIDENCY ─────────────────────────────────────────────────────────────
    'residency/changing-visa-type-italy/': [
        ('../../residency/permesso-di-soggiorno/', 'Residency',
         'Permesso di Soggiorno: Complete Step-by-Step Guide for Americans'),
        ('../../visas/elective-residence-visa/', 'Visas',
         'Elective Residence Visa Italy: The Complete 2025 Guide'),
        ('../../residency/permesso-di-soggiorno-renewal-americans-guide/', 'Residency',
         'Permesso di Soggiorno Renewal: Timing, Documents, Strategy'),
    ],
    'residency/italian-civil-union-unione-civile/': [
        ('../../residency/permesso-di-soggiorno/', 'Residency',
         'Permesso di Soggiorno: Complete Step-by-Step Guide for Americans'),
        ('../../residency/how-to-register-anagrafe-italy-americans/', 'Residency',
         'How to Register at the Anagrafe in Italy'),
        ('../../citizenship/italian-citizenship-by-marriage/', 'Citizenship',
         'Italian Citizenship by Marriage: Complete Guide for Americans'),
    ],
    'residency/marca-da-bollo-italy/': [
        ('../../residency/permesso-di-soggiorno/', 'Residency',
         'Permesso di Soggiorno: Complete Step-by-Step Guide for Americans'),
        ('../../residency/how-to-get-codice-fiscale-italy-americans/', 'Residency',
         'How to Get a Codice Fiscale in Italy: Complete 2025 Guide'),
        ('../../residency/spid-italy-foreigners-americans-guide/', 'Residency',
         "SPID for Foreigners in Italy: How Americans Get Italy's Digital Identity"),
    ],
    'residency/pec-email-italy/': [
        ('../../residency/spid-italy-foreigners-americans-guide/', 'Residency',
         "SPID for Foreigners in Italy: How Americans Get Italy's Digital Identity"),
        ('../../residency/permesso-di-soggiorno/', 'Residency',
         'Permesso di Soggiorno: Complete Step-by-Step Guide for Americans'),
        ('../../residency/how-to-get-codice-fiscale-italy-americans/', 'Residency',
         'How to Get a Codice Fiscale in Italy: Complete 2025 Guide'),
    ],
    'residency/registering-foreign-marriage-italy/': [
        ('../../residency/how-to-register-anagrafe-italy-americans/', 'Residency',
         'How to Register at the Anagrafe in Italy'),
        ('../../citizenship/italian-citizenship-by-marriage/', 'Citizenship',
         'Italian Citizenship by Marriage: Complete Guide for Americans'),
        ('../../residency/permesso-di-soggiorno/', 'Residency',
         'Permesso di Soggiorno: Complete Step-by-Step Guide for Americans'),
    ],

    # ── TAXES ─────────────────────────────────────────────────────────────────
    'taxes/401k-ira-withdrawals-italy-resident/': [
        ('../../taxes/us-italy-tax-treaty-double-taxation/', 'Taxes',
         'US-Italy Tax Treaty: How Double Taxation Works for Americans'),
        ('../../taxes/roth-ira-italy-tax-implications/', 'Taxes',
         "Roth IRA in Italy: Tax-Free Doesn't Mean Tax-Free"),
        ('../../taxes/fbar-fatca-americans-italy-guide/', 'Taxes',
         'FBAR and FATCA for Americans Living in Italy: What You Must File'),
    ],
    'taxes/capital-gains-tax-italy/': [
        ('../../taxes/us-italy-tax-treaty-double-taxation/', 'Taxes',
         'US-Italy Tax Treaty: How Double Taxation Works for Americans'),
        ('../../taxes/cryptocurrency-tax-italy-2025/', 'Taxes',
         'Cryptocurrency Tax in Italy 2025: Complete Rules for American Residents'),
        ('../../taxes/fbar-fatca-americans-italy-guide/', 'Taxes',
         'FBAR and FATCA for Americans Living in Italy: What You Must File'),
    ],
    'taxes/cryptocurrency-tax-italy-2025/': [
        ('../../taxes/capital-gains-tax-italy/', 'Taxes',
         'Capital Gains Tax in Italy 2025: Investments, Property, and Crypto'),
        ('../../taxes/us-italy-tax-treaty-double-taxation/', 'Taxes',
         'US-Italy Tax Treaty: How Double Taxation Works for Americans'),
        ('../../taxes/fbar-fatca-americans-italy-guide/', 'Taxes',
         'FBAR and FATCA for Americans Living in Italy: What You Must File'),
    ],
    'taxes/find-commercialista-us-tax-italy/': [
        ('../../taxes/us-italy-tax-treaty-double-taxation/', 'Taxes',
         'US-Italy Tax Treaty: How Double Taxation Works for Americans'),
        ('../../taxes/flat-tax-regime/', 'Taxes',
         "Italy's Flat Tax Regime: €100,000 Annual Cap for New Residents"),
        ('../../taxes/fbar-fatca-americans-italy-guide/', 'Taxes',
         'FBAR and FATCA for Americans Living in Italy: What You Must File'),
    ],
    'taxes/foreign-tax-credit-vs-feie-italy/': [
        ('../../taxes/us-italy-tax-treaty-double-taxation/', 'Taxes',
         'US-Italy Tax Treaty: How Double Taxation Works for Americans'),
        ('../../taxes/tax-residency-italy-when-liable/', 'Taxes',
         'Tax Residency in Italy: When Americans Become Liable'),
        ('../../taxes/fbar-fatca-americans-italy-guide/', 'Taxes',
         'FBAR and FATCA for Americans Living in Italy: What You Must File'),
    ],
    'taxes/imu-property-tax-italy/': [
        ('../../property/property-purchase-taxes-italy/', 'Property',
         'Property Purchase Taxes in Italy: Exact Calculation'),
        ('../../property/how-to-buy-property-italy-american-guide/', 'Property',
         'How to Buy Property in Italy as an American: Complete 2025 Guide'),
        ('../../taxes/italian-tax-year-calendar/', 'Taxes',
         'Italian Tax Year Calendar 2025: Every Deadline Americans Care About'),
    ],
    'taxes/inheritance-gift-tax-italy/': [
        ('../../taxes/us-italy-tax-treaty-double-taxation/', 'Taxes',
         'US-Italy Tax Treaty: How Double Taxation Works for Americans'),
        ('../../taxes/fbar-fatca-americans-italy-guide/', 'Taxes',
         'FBAR and FATCA for Americans Living in Italy: What You Must File'),
        ('../../property/how-to-buy-property-italy-american-guide/', 'Property',
         'How to Buy Property in Italy as an American: Complete 2025 Guide'),
    ],
    'taxes/italian-tax-year-calendar/': [
        ('../../taxes/us-italy-tax-treaty-double-taxation/', 'Taxes',
         'US-Italy Tax Treaty: How Double Taxation Works for Americans'),
        ('../../taxes/imu-property-tax-italy/', 'Taxes',
         'IMU Property Tax in Italy: When You Owe It and How to Calculate'),
        ('../../taxes/fbar-fatca-americans-italy-guide/', 'Taxes',
         'FBAR and FATCA for Americans Living in Italy: What You Must File'),
    ],
    'taxes/roth-ira-italy-tax-implications/': [
        ('../../taxes/401k-ira-withdrawals-italy-resident/', 'Taxes',
         '401(k) and IRA Withdrawals as an Italian Resident: The Tax Reality'),
        ('../../taxes/us-italy-tax-treaty-double-taxation/', 'Taxes',
         'US-Italy Tax Treaty: How Double Taxation Works for Americans'),
        ('../../taxes/foreign-tax-credit-vs-feie-italy/', 'Taxes',
         'Foreign Tax Credit vs FEIE for Americans in Italy: Which to Use'),
    ],
    'taxes/tax-residency-italy-when-liable/': [
        ('../../taxes/us-italy-tax-treaty-double-taxation/', 'Taxes',
         'US-Italy Tax Treaty: How Double Taxation Works for Americans'),
        ('../../taxes/flat-tax-regime/', 'Taxes',
         "Italy's Flat Tax Regime: €100,000 Annual Cap for New Residents"),
        ('../../taxes/fbar-fatca-americans-italy-guide/', 'Taxes',
         'FBAR and FATCA for Americans Living in Italy: What You Must File'),
    ],

    # ── VISAS ─────────────────────────────────────────────────────────────────
    'visas/90-180-schengen-rule-calculator/': [
        ('../../visas/elective-residence-visa/', 'Visas',
         'Elective Residence Visa Italy: The Complete 2025 Guide'),
        ('../../visas/how-to-apply-italy-visa-usa/', 'Visas',
         'How to Apply for an Italy Visa from the USA: Complete 2025 Guide'),
        ('../../visas/italy-visa-income-requirements-2025-all-types/', 'Visas',
         'Italy Visa Income Requirements 2025: All Visa Types for Americans'),
    ],
    'visas/dual-us-italian-citizens-visa/': [
        ('../../citizenship/jure-sanguinis/', 'Citizenship',
         'Italian Citizenship by Descent: Complete 2025 Guide'),
        ('../../citizenship/italian-passport-application/', 'Citizenship',
         'Italian Passport Application: Everything You Need After Getting Citizenship'),
        ('../../taxes/tax-residency-italy-when-liable/', 'Taxes',
         'Tax Residency in Italy: When Americans Become Liable'),
    ],
    'visas/health-insurance-italian-visa/': [
        ('../../visas/elective-residence-visa/', 'Visas',
         'Elective Residence Visa Italy: The Complete 2025 Guide'),
        ('../../visas/how-to-apply-italy-visa-usa/', 'Visas',
         'How to Apply for an Italy Visa from the USA: Complete 2025 Guide'),
        ('../../healthcare/best-health-insurance-americans-italy/', 'Healthcare',
         'Best Health Insurance for Americans in Italy: 2025 Guide'),
    ],
    'visas/how-to-apply-italy-visa-usa/': [
        ('../../visas/elective-residence-visa/', 'Visas',
         'Elective Residence Visa Italy: The Complete 2025 Guide'),
        ('../../visas/italy-visa-income-requirements-2025-all-types/', 'Visas',
         'Italy Visa Income Requirements 2025: All Visa Types for Americans'),
        ('../../visas/health-insurance-italian-visa/', 'Visas',
         'Health Insurance for Italian Visa: What Consulates Actually Accept'),
    ],
    'visas/italy-visa-rejection-how-to-appeal/': [
        ('../../visas/elective-residence-visa/', 'Visas',
         'Elective Residence Visa Italy: The Complete 2025 Guide'),
        ('../../visas/how-to-apply-italy-visa-usa/', 'Visas',
         'How to Apply for an Italy Visa from the USA: Complete 2025 Guide'),
        ('../../visas/italy-visa-income-requirements-2025-all-types/', 'Visas',
         'Italy Visa Income Requirements 2025: All Visa Types for Americans'),
    ],
    'visas/self-employment-visa-italy/': [
        ('../../visas/elective-residence-visa/', 'Visas',
         'Elective Residence Visa Italy: The Complete 2025 Guide'),
        ('../../taxes/partita-iva-italy-foreigners/', 'Taxes',
         'Partita IVA Italy for Americans: How to Get a VAT Number as a Foreigner'),
        ('../../visas/how-to-apply-italy-visa-usa/', 'Visas',
         'How to Apply for an Italy Visa from the USA: Complete 2025 Guide'),
    ],
}

# ── ARTICOLI con OLD FOOTER ma related-section già presente (solo footer fix) ──
FOOTER_ONLY = [
    'property/renting-apartment-italy-expat-guide/',
    'regions/living-rome-american-expat/',
    'residency/declaring-presence-8-day-rule-italy-americans/',
    'residency/getting-sim-card-italy-americans-guide/',
    'residency/italian-drivers-license-americans/',
    'taxes/irpef-tax-brackets-italy-2025-americans/',
    'taxes/us-italy-social-security-totalization-agreement/',
    'visas/etias-americans-italy-schengen-guide/',
    'visas/fbi-background-check-italian-visa-americans/',
    'visas/self-employment-visa-italy/',   # duplicato già in RELATED_MAP — handle in logic
]


def build_related_section(slug):
    """Costruisce il blocco HTML related-section per un dato slug."""
    cards = RELATED_MAP[slug]
    lines = [
        '\n<div class="related-section">',
        '  <div class="related-title">Continue reading</div>',
        '  <div class="related-grid">',
    ]
    for href, cat, title in cards:
        lines.append(f'    <a href="{href}" class="related-card">')
        lines.append(f'      <div class="related-cat">{cat}</div>')
        lines.append(f'      <div class="related-card-title">{title}</div>')
        lines.append(f'    </a>')
    lines.append('  </div>')
    lines.append('</div>\n')
    return '\n'.join(lines)


def has_new_footer(html):
    m = re.search(r'<footer[^>]*>.*?</footer>', html, re.DOTALL)
    return m and 'footer-guide-cat' in m.group(0)


def replace_footer(html):
    """Sostituisce qualsiasi <footer ...>...</footer> con il nuovo footer standard."""
    return re.sub(
        r'<footer[^>]*>.*?</footer>',
        NEW_FOOTER,
        html,
        flags=re.DOTALL
    )


def insert_related_section(html, slug):
    """Inserisce il related-section immediatamente prima del tag <footer."""
    related_html = build_related_section(slug)
    # Inserisci prima di <footer
    idx = html.find('<footer')
    if idx == -1:
        print(f"  WARN: no <footer found in {slug}")
        return html
    return html[:idx] + related_html + html[idx:]


def process_file(slug, add_related):
    filepath = BASE + slug + 'index.html'
    if not os.path.exists(filepath):
        print(f"  SKIP (file not found): {filepath}")
        return False

    html = open(filepath, encoding='utf-8').read()

    if has_new_footer(html) and not add_related:
        print(f"  SKIP (already new footer + no related needed): {slug}")
        return False

    # Verifica che non abbia già una related-section se stiamo aggiungendola
    if add_related and 'related-section' in html:
        print(f"  SKIP (related-section already present): {slug}")
        # Fa solo footer fix se serve
        if not has_new_footer(html):
            html_new = replace_footer(html)
            open(filepath, 'w', encoding='utf-8').write(html_new)
            print(f"  → footer only fixed: {slug}")
            return True
        return False

    changed = html

    if add_related:
        changed = insert_related_section(changed, slug)

    if not has_new_footer(changed):
        changed = replace_footer(changed)

    if changed == html:
        print(f"  NO CHANGE: {slug}")
        return False

    open(filepath, 'w', encoding='utf-8').write(changed)
    return True


# ── MAIN ─────────────────────────────────────────────────────────────────────

print("=" * 70)
print("PHASE 1: 50 articoli senza related-section (related + footer fix)")
print("=" * 70)

phase1_ok = 0
for slug in RELATED_MAP:
    result = process_file(slug, add_related=True)
    if result:
        print(f"  ✓ {slug}")
        phase1_ok += 1

print(f"\nPhase 1 completata: {phase1_ok} file modificati\n")

print("=" * 70)
print("PHASE 2: articoli con old footer ma related-section già presente")
print("=" * 70)

# Articoli con old footer e related-section — costruiamo lista dinamicamente
# (esclude quelli già trattati in phase 1)
import subprocess
result = subprocess.run(
    ['find', BASE, '-name', 'index.html'],
    capture_output=True, text=True
)
all_files = [f for f in result.stdout.strip().split('\n')
             if f and '/italopedia/' in f]

phase2_ok = 0
for filepath in sorted(all_files):
    slug = filepath.replace(BASE, '').replace('index.html', '')
    # Salta articoli già trattati in phase 1
    if slug in RELATED_MAP:
        continue
    # Solo articoli (depth >= 2, in una delle 8 categorie)
    cats = ['visas/', 'residency/', 'taxes/', 'healthcare/', 'property/',
            'citizenship/', 'regions/', 'cost-of-living/']
    if not any(slug.startswith(c) for c in cats):
        continue
    html = open(filepath, encoding='utf-8').read()
    if has_new_footer(html):
        continue  # Già ok
    # Ha old footer — aggiorna solo il footer
    html_new = replace_footer(html)
    if html_new != html:
        open(filepath, 'w', encoding='utf-8').write(html_new)
        print(f"  ✓ footer fixed: {slug}")
        phase2_ok += 1

print(f"\nPhase 2 completata: {phase2_ok} file modificati\n")

print("=" * 70)
print(f"TOTALE file modificati: {phase1_ok + phase2_ok}")
print("=" * 70)
