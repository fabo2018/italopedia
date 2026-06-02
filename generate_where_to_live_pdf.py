#!/usr/bin/env python3
"""
Genera "Where to Live in Italy: 20 City Profiles" — Italopedia PDF ($19)
Uso: python3 generate_where_to_live_pdf.py
Output: shop/downloads/where-to-live-italy.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pathlib import Path

# ── Fonts ────────────────────────────────────────────────────────────────────

FONT_DIR = Path("/System/Library/Fonts/Supplemental")

pdfmetrics.registerFont(TTFont("Georgia",       FONT_DIR / "Georgia.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-Bold",  FONT_DIR / "Georgia Bold.ttf"))
pdfmetrics.registerFont(TTFont("Georgia-Italic",FONT_DIR / "Georgia Italic.ttf"))
pdfmetrics.registerFont(TTFont("Arial",         FONT_DIR / "Arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold",    FONT_DIR / "Arial Bold.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic",  FONT_DIR / "Arial Italic.ttf"))
pdfmetrics.registerFont(TTFont("DIN-Bold",      FONT_DIR / "DIN Alternate Bold.ttf"))

# ── Colours ──────────────────────────────────────────────────────────────────

RED    = colors.HexColor('#c0392b')
DARK   = colors.HexColor('#1a1610')
PAPER  = colors.HexColor('#faf7f0')
PAPER2 = colors.HexColor('#f5f0e8')
INK2   = colors.HexColor('#3a3228')
INK3   = colors.HexColor('#6b5d52')
INK4   = colors.HexColor('#9e8e80')
BORDER = colors.HexColor('#e8ddd0')
GOLD   = colors.HexColor('#c9a84c')
GREEN  = colors.HexColor('#2d6a4f')
WHITE  = colors.white

# ── Page geometry ────────────────────────────────────────────────────────────

W, H = A4
ML = 2.2 * cm
MR = 2.2 * cm
MT = 2.0 * cm
MB = 2.2 * cm
TW = W - ML - MR   # text width

OUTPUT = Path(__file__).parent / "shop/downloads/where-to-live-italy.pdf"

# ── City data ────────────────────────────────────────────────────────────────

CITIES = [
  {
    "name": "Rome", "italian": "Roma", "region": "Lazio",
    "pop": "2.8 million", "elev": "21 m", "climate": "Mediterranean",
    "best_months": "Apr–Jun, Sep–Nov", "language": "English widely spoken",
    "expat_community": "Very large (50,000+ expats)",
    "budget": (1800, 2800, 3800),
    "neighborhoods": [
      ("Trastevere", "The classic expat quarter: cobblestones, ivy, restaurants spilling onto the street. Very tourist-heavy but magnetic. €1,200–1,800/mo."),
      ("Prati", "Near the Vatican, quieter, more local feel, good transit. Excellent for families. €1,000–1,500/mo."),
      ("Pigneto / Ostiense", "Trendy, cheaper (€800–1,100), gritty-creative, younger crowd. Best for remote workers on a budget."),
    ],
    "scores": [("Expat-friendliness",4),("English",4),("Public transit",3),
               ("Cost",2),("Culture",5),("Safety",3),("Healthcare",4),("Bureaucracy",2)],
    "pros": ["Direct flights from Fiumicino to 10+ US cities","World-class culture, food, history on every corner","Huge expat community — instant social life","Top universities and international schools"],
    "cons": ["Rome's Questura is Italy's most backlogged — permesso waits 9+ months","Traffic and chaos erodes daily quality of life","Centro storico neighbourhoods feel artificial; tourists outnumber locals in summer","Rents rose 35% since 2022 and are still climbing"],
    "best_for": "First-time Italy movers · Art & history lovers · Families needing international schools · Those requiring direct US flights",
    "avoid_if": "You dislike noise and chaos · You're on a tight budget · You want genuine local Italian neighbourhood life",
    "take": "Rome is magnificent and maddening in equal measure. The city tests your patience every day with traffic, bureaucracy, and tourist crowds — then rewards you with a sunset over the Forum that makes everything worth it. Go in knowing the administrative process is Italy's slowest; arrive with patience and it becomes one of the great cities to live in.",
    "desc": "Rome needs no introduction. But living here is a very different proposition from visiting. As a resident, you get the Rome that tourists never see: Sunday morning markets in Testaccio, aperitivo in Ostiense, Sunday lunch with Roman families in Monte Verde. The city rewards those who go deep.\n\nFor American expats, Rome offers the most established support network in Italy. There are English-speaking doctors, US-focused tax accountants, international grocery stores, and a dozen expat Facebook groups that answer questions in hours. The consulate is here. The embassies are here. If something goes wrong, Rome has the infrastructure to fix it.\n\nThe main headache is the Questura. Rome's permesso di soggiorno office is Italy's most overwhelmed, and processing times of 6–12 months are common. The ricevuta (post office receipt) will be your identity document for much of your first year. Build this into your timeline.\n\nNeighbourhood choice is everything in Rome. Avoid tourist-trap areas like Campo de' Fiori and the streets near the Trevi Fountain unless you want to feel like a museum exhibit. The real Rome lives in Pigneto, Ostiense, Monte Verde, Garbatella, and the residential parts of Testaccio. Here, the city still belongs to Romans.\n\nRent has risen sharply. A decent 1-bedroom in a liveable neighbourhood costs €900–1,400/month. Trastevere and Prati are 20–30% above that. Budget carefully.",
  },
  {
    "name": "Milan", "italian": "Milano", "region": "Lombardy",
    "pop": "1.4 million (3.2M metro)", "elev": "120 m", "climate": "Humid continental",
    "best_months": "Apr–May, Sep–Oct", "language": "Excellent English (business city)",
    "expat_community": "Very large — most international city in Italy",
    "budget": (2200, 3200, 4500),
    "neighborhoods": [
      ("Navigli", "The canal district. Trendy, aperitivo culture, young crowd. Expensive for what it is: €1,400–2,000/mo. Best for single remote workers."),
      ("Porta Venezia", "Leafy, central, established expat area, excellent food market. €1,200–1,800/mo. The default choice for most expats."),
      ("Nolo (N. of Loreto)", "Up-and-coming creative quarter. Cheaper (€900–1,300), great Metro line, younger. Best value inside Milan proper."),
    ],
    "scores": [("Expat-friendliness",5),("English",5),("Public transit",4),
               ("Cost",1),("Culture",4),("Safety",4),("Healthcare",5),("Bureaucracy",3)],
    "pros": ["Best English proficiency in Italy — doing bureaucracy feels almost manageable","Top-tier private hospitals (Humanitas, San Raffaele) on a par with US facilities","Excellent international schools","Most direct international flight connections","Efficient ATM metro — actually works"],
    "cons": ["Italy's most expensive city — rent alone is €1,400–2,200 for a 1-bedroom centre","Gray fog Oct–Mar: the Pianura Padana is Europe's most polluted plain in winter","Less of the romantic Italy feel — efficiency trumps charm here","Cost of dining out is 40% above the Italian average"],
    "best_for": "Corporate expats · Tech and finance remote workers · Families needing international schools · Fashion and design industry",
    "avoid_if": "You're on a budget · You came to Italy for olive trees and ancient ruins · You can't stand grey winter skies",
    "take": "Milan is where Italy meets New York. It's efficient, polished, international — and the most expensive city in the country. If your mental image of Italy involves misty Sunday mornings and sleepy piazzas, look elsewhere. But if you want Italian food, Italian design, and Italian lifestyle with world-class infrastructure and English everywhere, Milan delivers without compromise.",
    "desc": "Milan surprises most American expats. They expect Italy; they find something closer to a northern European business capital that happens to serve the world's best risotto. That's not a criticism — it's a very specific and valuable thing.\n\nFor remote workers and corporate expats, Milan has unmatched infrastructure. The healthcare system — with Humanitas and San Raffaele operating at Swiss-standard levels — is a serious draw. The international school network is Italy's strongest. The English proficiency means your first year doesn't require Italian to function.\n\nThe cost is the trade-off. A comfortable 1-bedroom in Porta Venezia or Isola runs €1,200–1,800/month. The Navigli canals are beautiful but the most expensive neighbourhood for what you get. If budget matters, look at Nolo or Porta Romana for €900–1,300.\n\nMilan's weather is genuinely its weakest point. The Po Valley traps fog and pollution from October through March, and the grey skies can be psychologically grinding. Milanese deal with this by decamping to the lakes (Lago di Como is 45 minutes away) on weekends. If sun matters to you, factor this in seriously.\n\nThe city more than makes up for the weather in spring and autumn, when the energy is electric and the fashion weeks transform the streets into a runway.",
  },
  {
    "name": "Florence", "italian": "Firenze", "region": "Tuscany",
    "pop": "370,000", "elev": "50 m", "climate": "Mediterranean",
    "best_months": "Apr–Jun, Sep–Nov", "language": "Very good English (university/tourism city)",
    "expat_community": "Large — especially American (multiple US universities here)",
    "budget": (1600, 2400, 3400),
    "neighborhoods": [
      ("Oltrarno", "South of the Arno. The artisan quarter — leather workshops, wine bars, real locals. Less touristy. €1,100–1,600/mo."),
      ("San Niccolò", "Charming, upmarket, spectacular views from Piazzale Michelangelo above. €1,200–1,800/mo."),
      ("Statuto / Fortezza", "Residential, locals, practical, good transit. The sensible choice. €800–1,200/mo."),
    ],
    "scores": [("Expat-friendliness",4),("English",4),("Public transit",3),
               ("Cost",2),("Culture",5),("Safety",4),("Healthcare",4),("Bureaucracy",3)],
    "pros": ["Largest US expat community in Italy — instant American social network","Multiple US university programs create a permanent American presence","Tuscany on your doorstep: Chianti, Siena, Cinque Terre all under 2 hours","Extraordinary beauty — the density of Renaissance art is incomparable","Manageable size: walkable, cyclable, human-scale"],
    "cons": ["Tourist saturation Jun–Aug is genuinely oppressive — 13 million visitors/year","Rents rose 40%+ since 2020 and are still rising","Summer heat (38°C+) in a city without much green space or sea breeze","Job market very limited for non-remote workers"],
    "best_for": "American retirees · Art and history lovers · Remote workers who want Tuscany · US academics (NYU, Georgetown, Syracuse all have Florence programs)",
    "avoid_if": "You dislike tourists and want authentic neighbourhood life · Summer heat intolerance · Budget-constrained",
    "take": "Florence is the most American-friendly city in Italy in character, not just infrastructure. The expat community is vast, English is everywhere, and the beauty is relentless. The two threats are the tourist industrial complex (it changes the city's character in summer) and rising costs. Go deep into the Oltrarno for the best of both worlds.",
    "desc": "Florence is where Italy's Renaissance happened, and living there means walking through it daily. The Uffizi, the Duomo, Brunelleschi's dome, the Ponte Vecchio — these aren't tourist attractions you visit once; they're the backdrop to Tuesday's grocery run.\n\nFor Americans specifically, Florence has an unusually large support network. NYU, Georgetown, Syracuse, Boston University, and a dozen other US universities maintain permanent programs here. This means a constant flow of American professors, visiting students, and alumni who settled. The expat Facebook groups are active. The English-speaking doctors are many.\n\nThe permesso process at the Florence Questura is significantly faster than Rome — typically 3–5 months. The bureaucracy is still Italian (bring patience), but less overwhelmed.\n\nThe warning is cost. Florence's rents have risen sharply, driven by a combination of Airbnb short-term speculation, US university housing demand, and the general post-COVID migration surge. A 1-bedroom in Oltrarno or San Niccolò now costs €1,100–1,800. The Statuto neighbourhood (residential, north of the centre) offers €800–1,100 with good transit.\n\nAnd then there's the summer. July and August turn central Florence into a theme park. Locals largely leave. If you're there, you're swimming through tourist groups at 37°C. The solution is simple: go to the sea for August, like everyone else.",
  },
  {
    "name": "Bologna", "italian": "Bologna", "region": "Emilia-Romagna",
    "pop": "400,000", "elev": "55 m", "climate": "Humid continental",
    "best_months": "Apr–Jun, Sep–Oct", "language": "Good English (major university city)",
    "expat_community": "Medium — growing fast",
    "budget": (1400, 2100, 2900),
    "neighborhoods": [
      ("Centro Storico", "Under the porticos, lively, university energy. The full Bologna experience. €900–1,400/mo."),
      ("San Donato / Costa Saragozza", "Residential, student mix, tree-lined, excellent value. €700–1,000/mo."),
      ("Navile", "Creative quarter, up-and-coming, cheapest close to centre. €650–950/mo."),
    ],
    "scores": [("Expat-friendliness",4),("English",4),("Public transit",4),
               ("Cost",3),("Culture",5),("Safety",5),("Healthcare",4),("Bureaucracy",3)],
    "pros": ["The best food city in Italy — Bolognese cuisine sets the global standard","40 km of covered porticos: you walk everywhere in any weather","Outstanding safety — among Italy's lowest crime rates","Excellent rail hub: Rome 2h, Florence 35min, Milan 1h","University atmosphere keeps it young and intellectual"],
    "cons": ["Less internationally recognised than Rome/Florence (harder to explain to visiting family)","Cold foggy winters Dec–Feb","Smaller international community than the Big Three","July–August emptied by Italians leaving for the coast"],
    "best_for": "Foodies · Culture lovers wanting an authentic Italian city · Families · Long-term expats who prioritise quality of life over glamour",
    "avoid_if": "You need a large established expat network immediately · You hate cold winters · You want the beach",
    "take": "Bologna is Italy's best-kept secret for expats — lower cost than Florence, better food than Rome, more authentic than Milan. The portico-lined streets are genuinely magical, the Bolognese are warm and practical, and the quality of life scores near the top of any objective ranking. This is the city that rewards the expat who does their homework.",
    "desc": "Ask serious Italy expats which city they'd choose if starting again, and a remarkable number say Bologna. It lacks the international fame of Rome and Florence, but it outperforms both on almost every quality-of-life metric that matters for daily living.\n\nThe food is genuinely extraordinary. Tagliatelle al ragù (the real Bolognese), tortellini in brodo, mortadella, Parmigiano Reggiano and Prosciutto di Parma produced nearby — the weekly market at Mercato di Mezzo is a ritual that turns into religion. You don't just eat well here; you eat at the source.\n\nThe porticos are Bologna's secret weapon for daily life. 40 kilometres of covered arcades mean you walk everywhere in any weather, connecting you to the city rather than driving through it. This is architecturally unique in the world and practically transformative for daily life.\n\nThe university (founded 1088 — the world's oldest) gives Bologna a permanent intellectual energy. Students make up 20% of the population, which keeps the city young, affordable, and culturally active well above its size.\n\nThe Questura is efficient by Italian standards. The ASL for SSN enrollment is relatively fast. Bologna is a city that, for once, makes Italian bureaucracy feel almost manageable.",
  },
  {
    "name": "Turin", "italian": "Torino", "region": "Piedmont",
    "pop": "850,000", "elev": "240 m", "climate": "Humid continental (Alps backdrop)",
    "best_months": "Apr–Jun, Sep–Oct", "language": "Moderate English — improving",
    "expat_community": "Medium — small but tight-knit international community",
    "budget": (1200, 1800, 2600),
    "neighborhoods": [
      ("Cit Turin / Crocetta", "Bourgeois residential, excellent Saturday market, families and professionals. €700–1,100/mo."),
      ("San Salvario", "Lively, multicultural, aperitivo scene, nightlife. The young expat quarter. €600–950/mo."),
      ("Vanchiglia", "Hip, up-and-coming, near the Po river, creative types. €550–850/mo."),
    ],
    "scores": [("Expat-friendliness",3),("English",3),("Public transit",4),
               ("Cost",4),("Culture",4),("Safety",4),("Healthcare",5),("Bureaucracy",3)],
    "pros": ["Among the cheapest of Italy's major cities — exceptional value","The Alps at 45 minutes: skiing in winter, hiking in summer","Extraordinary Baroque architecture that rivals Paris (genuinely)","World-class hospitals: Molinette, Ospedale Mauriziano, CTO","Close to France (border 80km): French Riviera weekend trips easy"],
    "cons": ["English less prevalent than southern tourist hubs","Smaller international community — requires more Italian to build social life","Gloomy November–February — fog and cold, though less severe than Milan","Industrial history means some peripheral areas lack charm"],
    "best_for": "Budget-conscious expats · Mountain and skiing enthusiasts · Families · Remote workers who want major-city infrastructure at medium-city prices",
    "avoid_if": "You need a large English-speaking expat scene immediately · You want the Mediterranean coast · You hate cold",
    "take": "Turin is where I've lived for 15+ years, and I believe it is Italy's most underestimated city. The Baroque streetscape rivals Paris, the food culture rivals Bologna, and the cost rivals Catanzaro. The Alps are 45 minutes away. The only thing Turin lacks is Rome's glamour — which is precisely why the expats who discover it tend to stay.",
    "desc": "Turin surprises people. They expect a grey industrial city — Fiat, Juventus, car factories — and find extraordinary Baroque architecture, a world-class Egyptian Museum, the best chocolate and coffee culture in Italy, and the Alps as a backdrop visible from the city centre on clear days.\n\nAs the city where I've lived for over 15 years, I can speak from experience: the quality of daily life in Turin is exceptional. The markets (Porta Palazzo is Europe's largest open-air market), the aperitivo culture (Turin invented it), the museums, the Mole Antonelliana — these things don't get old.\n\nThe cost is remarkable. A comfortable 1-bedroom in San Salvario or Vanchiglia costs €600–950/month. Groceries are cheaper than Florence or Rome. A sit-down lunch costs €10–13. The SSN Questura (Questura di Torino) is efficient by Italian standards.\n\nThe main honest caveat: English is less prevalent than in Florence or Rome. Building a social life requires more Italian. This is a medium-term challenge that resolves itself, but in the first months it's real.\n\nFor expats who learn Italian and give Turin 6 months, it tends to become home. The city has a way of revealing itself slowly — which is very Piedmontese.",
  },
  {
    "name": "Venice", "italian": "Venezia", "region": "Veneto",
    "pop": "250,000 (50,000 on the island)", "elev": "1 m", "climate": "Humid subtropical",
    "best_months": "Apr–Jun, Oct", "language": "Good English (major tourist city)",
    "expat_community": "Small but passionate — island residents are a self-selected tribe",
    "budget": (1600, 2400, 3300),
    "neighborhoods": [
      ("Dorsoduro", "Most livable sestiere: university, students, quieter western end. The expat default. €1,100–1,700/mo."),
      ("Castello", "Eastern, quietest, most locals, genuine neighbourhood feel. €900–1,400/mo."),
      ("Giudecca", "The island facing Zattere, calmer, cheaper, ferry access. €850–1,300/mo."),
    ],
    "scores": [("Expat-friendliness",3),("English",4),("Public transit",5),
               ("Cost",2),("Culture",5),("Safety",5),("Healthcare",3),("Bureaucracy",3)],
    "pros": ["The most beautiful city in the world — this is not hyperbole","Extraordinary safety: no cars, no scooters, no road accidents","Vaporetto network is actually excellent once you know it","Total absence of car costs — zero parking, zero fuel","The island community: tight-knit, intense, unlike anywhere"],
    "cons": ["Acqua alta flooding (Nov–Mar): 30–40 flood events per year — ground floors inundated","Overtourism is extreme: 20 million visitors/year for 50,000 residents","Everything delivered by boat = groceries, furniture, everything costs more","One main hospital (SS. Giovanni e Paolo) — limited specialist coverage","The island is depopulating: loses ~1,000 residents/year; infrastructure declines"],
    "best_for": "Artists and writers · Those seeking a transformative 1–3 year experience · People who've already lived in Italy · Architecture lovers",
    "avoid_if": "Families with school-age children · Anyone needing serious medical care routinely · Budget expats · Those wanting practical daily convenience",
    "take": "Venice is not designed for modern life — and that's the point. Those who live there know that. It's the most beautiful city on Earth and an experience unlike any other, but the logistics are genuinely challenging. Treat it as a 1–3 year life chapter, not necessarily a permanent base. Those who do stay permanently tend to become the most devoted city residents you'll ever meet.",
    "desc": "There is nowhere else on Earth like Venice. This is both its extraordinary appeal and its central challenge for expats. The city was built for a medieval maritime republic, not for people who need IKEA deliveries or want to run to the pharmacy quickly.\n\nLiving on the island means accepting that everything — furniture, bicycles, heavy groceries — arrives by boat, at a premium. Acqua alta flooding from November to March means keeping rubber boots at the door and knowing which streets flood in which tidal sequence. The single hospital, Santi Giovanni e Paolo, is serviceable but limited in specialist coverage.\n\nAnd yet. The beauty is relentless and inexhaustible. Walking through Dorsoduro at 6am when the light hits the water and there are no tourists — this is one of life's genuinely rare experiences. The vaporetto on a winter evening, the silence of a foggy morning, the way sound travels across water — Venice operates on different physics from the rest of the world.\n\nPractically: housing is genuinely available at reasonable prices in Castello and Giudecca, which most tourists never reach. The island community is small, intense, and self-selecting — you meet extraordinary people who have all made the same unconventional choice.\n\nFor most expats, Venice works best as a 1–3 year chapter. A remarkable number extend that indefinitely.",
  },
  {
    "name": "Naples", "italian": "Napoli", "region": "Campania",
    "pop": "3 million metro", "elev": "17 m", "climate": "Mediterranean",
    "best_months": "Apr–Jun, Sep–Nov", "language": "Limited English (improves yearly)",
    "expat_community": "Small but growing — adventurous types",
    "budget": (1100, 1700, 2400),
    "neighborhoods": [
      ("Chiaia", "Upscale seafront district, international feel, best infrastructure. The expat-default in Naples. €900–1,400/mo."),
      ("Vomero", "Hilltop residential, panoramic views, quieter, families. €750–1,100/mo."),
      ("Posillipo", "Clifftop with sea views, expensive, spectacular. €1,200–1,900/mo."),
    ],
    "scores": [("Expat-friendliness",3),("English",3),("Public transit",3),
               ("Cost",4),("Culture",5),("Safety",3),("Healthcare",3),("Bureaucracy",2)],
    "pros": ["Most affordable major southern city with actual metropolitan infrastructure","Vesuvius, Pompeii, Amalfi Coast, Capri all within an hour","The real pizza Napoletana — the best in the world, €5 a plate","Warm, generous, intensely alive local culture","Dramatic beauty: the bay, the volcano, the chaotic streetscapes"],
    "cons": ["Petty theft higher than northern cities — requires awareness","Bureaucracy slowest in Italy even by Italian standards","Some areas have safety issues (Scampia etc.) — neighbourhood research essential","Air quality concerns from traffic and industrial Bagnoli area","English very limited outside Chiaia — Italian essential"],
    "best_for": "Adventurous expats · Italian speakers (or committed learners) · Artists and writers · Those who want authentic deep-south Italy",
    "avoid_if": "First-time Italy movers · Those needing English-speaking environment · People with significant healthcare needs",
    "take": "Naples is overwhelming, exhausting, and absolutely alive. It is the most Italian city in Italy — raw, passionate, chaotic, generous. The expats who thrive here are those who've already lived in Italy and want to go deeper. First-timers should probably start somewhere gentler, visit Naples repeatedly, fall in love, then move.",
    "desc": "No city in Italy divides opinion like Naples. Some expats arrive and never leave; others last six months. The difference is almost entirely about whether you can embrace — rather than resist — the organised chaos that is Neapolitan daily life.\n\nThe city is overwhelming in the best and worst ways. The street food scene is extraordinary: pizza fritta for €2, sfogliatella for €1.50, fried cuoppo at a basso for €3. The archaeological richness is unmatched — Pompeii and Herculaneum are 20 minutes away, the National Archaeological Museum holds treasures that Rome can't match.\n\nThe practical challenges are real. Petty theft in tourist areas requires awareness (don't wear visible jewellery on a scooter-heavy street). The Questura permesso process is among Italy's slowest. Healthcare outside the private Clinica Pinto or Villa dei Fiori requires patience.\n\nThe neighbourhood you choose is everything. Chiaia and Vomero are expat-manageable: good infrastructure, some English, less chaos. The Spanish Quarter and the Historic Centre are extraordinary to walk but harder to live in daily. Posillipo offers sea views and quiet at a premium.\n\nThose who learn Italian and give Naples a year find it becomes one of the most addictive cities in the world. The warmth of the Neapolitan character — the generosity, the theatrical expressiveness, the food generosity — is in a different category from northern Italy.",
  },
  {
    "name": "Palermo", "italian": "Palermo", "region": "Sicily",
    "pop": "650,000", "elev": "14 m", "climate": "Mediterranean",
    "best_months": "Mar–Jun, Oct–Nov", "language": "Limited English (improving in tourist areas)",
    "expat_community": "Small but growing — a new wave discovering Sicily",
    "budget": (900, 1400, 2000),
    "neighborhoods": [
      ("Libertà / Notarbartolo", "Residential, families, most practical for expats. Good infrastructure. €500–800/mo."),
      ("Mondello", "Beach suburb, resort feel. Popular with wealthier expats. Summer-crowded. €600–950/mo."),
      ("Politeama", "Central, animated, near the cultural sites. €550–850/mo."),
    ],
    "scores": [("Expat-friendliness",3),("English",2),("Public transit",2),
               ("Cost",5),("Culture",4),("Safety",3),("Healthcare",3),("Bureaucracy",2)],
    "pros": ["Among the cheapest cities in Europe for a capital — €900/mo budget realistic","Extraordinary food and street food culture (mercati Ballarò, Vucciria)","Year-round mild climate — effectively no winter","Arabic-Norman architecture unique in Europe","Genuine, warm Sicilian hospitality"],
    "cons": ["Car absolutely essential — public transit unreliable","Bureaucracy notoriously slow even by Sicilian standards","English very limited outside tourist areas — Italian required","Infrastructure and road quality below northern Italian standards"],
    "best_for": "Italian speakers · Serious budget retirees · Culinary adventurers · Those who want authentic Mediterranean life at minimal cost",
    "avoid_if": "Non-Italian speakers in first year · Those needing reliable public transit · Anyone requiring specialist medical care (Palermo hospital quality variable)",
    "take": "Palermo is one of Europe's great overlooked cities. The Arab-Norman churches, the Ballarò market chaos, the €5 panino con la milza — it's an experience unlike anywhere else. The logistics require patience and a car, but the cost is so low and the culture so rich that many expats who try it refuse to leave.",
    "desc": "Palermo is the city that rewards patience and punishes impatience. The logistics are harder than anywhere in northern Italy — the public transit is genuinely poor, the bureaucracy operates on its own timeline, and the infrastructure outside the centre can be rough. But the trade-offs are extraordinary.\n\nThe cost of living is among the lowest in Europe for a city of this size and cultural richness. A decent 1-bedroom in Libertà or Notarbartolo costs €400–700/month. Groceries at the Ballarò or Capo markets cost less than anywhere north of Naples. A sit-down lunch at a trattoria is €8–12.\n\nThe food culture is serious. Palermo's street food — arancine, panelle, sfincione, stigghiola, pane con la milza — is a culinary tradition unlike anything on the mainland. The fish market at Mercato di Ballarò has produce that Michelin-starred chefs drive from Milan to access.\n\nThe Arab-Norman architecture is extraordinary and unique: Arab domes, Norman arches, Byzantine mosaics, all fused in the 12th century Cappella Palatina and the Duomo di Monreale. This is not Italian history — it's Mediterranean civilizational history.\n\nThe honest requirements: you need Italian, you need a car, and you need to recalibrate your expectations about administrative efficiency. Get those three right and Palermo becomes one of the most rewarding cities in Italy.",
  },
  {
    "name": "Catania", "italian": "Catania", "region": "Sicily",
    "pop": "310,000", "elev": "7 m (Etna at 3,357 m)", "climate": "Mediterranean",
    "best_months": "Mar–Jun, Oct", "language": "Moderate English (university city)",
    "expat_community": "Small — mainly linked to University of Catania",
    "budget": (850, 1300, 1800),
    "neighborhoods": [
      ("Centro Storico", "The Baroque city around Piazza del Duomo. Lively, central, gentrifying. €450–700/mo."),
      ("Borgo / Ognina", "Coastal northern quarter, fishing village feel, authentic. €400–650/mo."),
      ("San Giovanni Galermo", "Affordable western residential, car needed. €300–500/mo."),
    ],
    "scores": [("Expat-friendliness",3),("English",3),("Public transit",2),
               ("Cost",5),("Culture",4),("Safety",3),("Healthcare",3),("Bureaucracy",2)],
    "pros": ["Cheaper than Palermo — the most affordable large Sicilian city","Mt. Etna experience unique in Europe: lava trails, craters, wine from volcanic soil","Major Ryanair hub (Fontanarossa) — cheap flights to northern Europe","University of Catania keeps city young and English-accessible","Black lava Baroque architecture: striking and photogenic"],
    "cons": ["Car essential — transit poor","Etna ash occasionally disrupts (minor but real)","Smaller city than Palermo — fewer services","English limited outside university circles"],
    "best_for": "Budget digital nomads · Sicily lovers who want smaller than Palermo · Those needing cheap European flights · Outdoor and volcanology enthusiasts",
    "avoid_if": "Non-Italian speakers without Italian learning plan · Anyone needing regular specialist healthcare",
    "take": "Catania is scrappier than Palermo but arguably more authentic and consistently cheaper. The Etna backdrop is extraordinary and unlike anywhere in Italy. For budget-maximising expats who want the Sicily experience with good flight connections, Catania is one of the best options anywhere in southern Europe.",
    "desc": "Catania sits at the foot of Mt. Etna, Europe's most active volcano, and that geological fact defines everything about the city. The streets are built from black lava stone. The cuisine is shaped by volcanic soil. The personality of the city — direct, earthy, resilient — mirrors the landscape.\n\nFor expats, Catania offers the Sicily experience at an even lower price point than Palermo, with the bonus of a major low-cost airline hub. Ryanair's Fontanarossa base means cheap connections to London, Dublin, Amsterdam, and dozens of European cities — useful if you're maintaining US connections via European hubs.\n\nThe university (one of the oldest in Sicily) gives Catania a younger energy than its size suggests. English is more prevalent here than in Palermo, and the nightlife around Via Gemmellaro and the fish market area is genuinely good.\n\nThe Baroque centre around Piazza del Duomo — all black lava and white limestone, a contrast that's stunning in afternoon light — is one of Sicily's architectural highlights. The Mercato del Pesce (fish market) in Via Pardo is a daily spectacle.\n\nThe practical caveats apply as across Sicily: car needed, Italian needed, bureaucracy slow. But the monthly budget of €850 for a genuinely comfortable life is almost impossible to beat anywhere in western Europe.",
  },
  {
    "name": "Bari", "italian": "Bari", "region": "Puglia",
    "pop": "320,000", "elev": "5 m", "climate": "Mediterranean",
    "best_months": "Mar–Jun, Sep–Nov", "language": "Limited English (improving)",
    "expat_community": "Small — one of Italy's fastest-growing expat destinations",
    "budget": (950, 1500, 2100),
    "neighborhoods": [
      ("Bari Vecchia", "The medieval labyrinthine old town — unique in Italy. Gentrifying. €500–800/mo."),
      ("Libertà / Madonnella", "Residential, genuine local life, good value. €450–700/mo."),
      ("Poggiofranco", "Modern, families, better infrastructure, quieter. €550–850/mo."),
    ],
    "scores": [("Expat-friendliness",3),("English",3),("Public transit",3),
               ("Cost",5),("Culture",4),("Safety",3),("Healthcare",4),("Bureaucracy",2)],
    "pros": ["Gateway to all of Puglia: Alberobello, Polignano, Lecce, Ostuni all accessible","Good hospital infrastructure for a southern city (Policlinico di Bari)","Excellent food: orecchiette, seafood, focaccia Barese","Growing expat scene — on the cusp of discovery","Ferries to Albania, Montenegro, Greece from the port"],
    "cons": ["Petty crime in the old town at night — awareness required","English limited outside younger generation","Bureaucracy slow even by southern standards","Less charming centro than Lecce or Polignano"],
    "best_for": "Puglia explorers using city as base · Budget expats wanting real city infrastructure · Those interested in the Adriatic and Balkans ferry connections",
    "avoid_if": "Those wanting a postcard-perfect small town · Visitors expecting northern-Italian service standards",
    "take": "Bari is Puglia's real capital and increasingly attractive to expats who've been priced out of Lecce's rising rents. It's a genuine city with real infrastructure, extraordinary food, and costs that make northern Italy seem absurd. The old town's maze of alleys — where elderly women still make orecchiette by hand in doorways — is one of Italy's most authentic urban experiences.",
    "desc": "Bari doesn't try to be pretty in the Lecce or Alberobello sense. It's a real southern city — busy, slightly chaotic, proud of its identity. And that authenticity is increasingly exactly what a certain type of expat is seeking.\n\nThe food is the first and strongest argument for Bari. Focaccia Barese (thick, olive-oil drenched, topped with tomatoes and olives) costs €1.50 at the bakeries that have been making it for generations. The fish market opens at dawn and the seafood is extraordinary. The orecchiette alle cime di rapa made in the old town doorways by the women of Bari Vecchia is a daily ritual and a tourist attraction — but more importantly, it's the actual lunch that residents eat.\n\nBari's healthcare infrastructure is better than most southern cities. The Policlinico di Bari is a teaching hospital with decent specialist coverage. For serious issues, Rome or Milan are still the reference points, but for routine and emergency care, Bari is more reliable than many comparable-sized southern cities.\n\nThe old town (Bari Vecchia) is extraordinary and unlike anything in the north — a medieval labyrinth of whitewashed lanes with the Basilica di San Nicola at its heart. It's gentrifying, which means some blocks are charming and some remain genuinely rough. Research the specific street before signing a lease.",
  },
  {
    "name": "Lecce", "italian": "Lecce", "region": "Puglia (Salento)",
    "pop": "95,000", "elev": "49 m", "climate": "Mediterranean",
    "best_months": "Mar–Jun, Sep–Nov", "language": "Moderate English (growing)",
    "expat_community": "Medium and growing fast — Lecce is trending",
    "budget": (850, 1300, 1900),
    "neighborhoods": [
      ("Centro Storico", "The golden Baroque crown jewel. Rising rents but the full experience. €500–900/mo."),
      ("Borgo Pace / Rudiae", "Quiet, residential, locals, authentic Lecce. €450–700/mo."),
      ("San Lazzaro", "University area, mixed character, most affordable. €400–600/mo."),
    ],
    "scores": [("Expat-friendliness",4),("English",3),("Public transit",2),
               ("Cost",5),("Culture",5),("Safety",5),("Healthcare",3),("Bureaucracy",3)],
    "pros": ["Europe's finest Baroque architecture — all in warm golden limestone","Extraordinary safety: among Italy's lowest crime rates","Warmest mainland Italian climate (mild even in January)","Growing international expat community — critical mass being reached","Monthly budget that defies belief: €850 is comfortable"],
    "cons": ["Small city (95,000) — limited services, cultural events, job market","Car recommended — public transit connections outside are poor","Healthcare limited: serious issues require travel to Bari (2 hours)","Rents rising 20–30% since 2022 as expats discover it"],
    "best_for": "Retirees · Writers and artists · Remote workers craving beauty and tranquility · Long-term expats who've done their research",
    "avoid_if": "Those needing regular specialist healthcare · People who need big-city energy and services · Non-drivers in outlying areas",
    "take": "Lecce is the Italopedia gold standard for retirees: extraordinary beauty, outstanding safety, warm climate, and a monthly budget that seems impossible until you live it. The Baroque architecture in warm golden pietra leccese is among Europe's finest. Go before everyone else discovers it — rents are already moving.",
    "desc": "Lecce is the city that converts sceptics. People arrive expecting a pretty town in the heel of Italy and find something that recalibrates their sense of what European beauty means. The centro storico is entirely Baroque, built from the local golden limestone that glows amber in afternoon light. The Basilica di Santa Croce, the Piazza del Duomo, the Roman amphitheatre in the main piazza — this is concentrated magnificence.\n\nFor expats, Lecce offers something increasingly rare: beauty without the corresponding price tag. A 1-bedroom apartment in the centro storico costs €450–750/month. A sit-down lunch at a Salentino trattoria is €10–14 with wine. The SSN enrollment is straightforward (the ASL in Lecce is not overwhelmed). Safety is extraordinary — Lecce consistently ranks among Italy's safest cities.\n\nThe growing international community is both good news and a warning. The expat presence — particularly British, Dutch, and American retirees — has built critical mass. There are English-speaking services, expat social groups, and a small but real international social scene. The warning: this is driving rents up. What cost €350/month in 2020 costs €500–600 in 2025. Still extraordinary value, but the trajectory is notable.\n\nThe practical limitations are real: the city is small, specialist healthcare requires going to Bari or beyond, and a car makes life significantly easier. For the right profile — someone who wants tranquility, beauty, warmth, and low cost over big-city infrastructure — Lecce is nearly perfect.",
  },
  {
    "name": "Genoa", "italian": "Genova", "region": "Liguria",
    "pop": "580,000", "elev": "7 m", "climate": "Mediterranean",
    "best_months": "Apr–Jun, Sep–Oct", "language": "Moderate English",
    "expat_community": "Small — largely undiscovered",
    "budget": (1100, 1700, 2400),
    "neighborhoods": [
      ("Castelletto", "Hilltop residential, great views, funicular access. Families and professionals. €650–1,000/mo."),
      ("Carignano", "Smart, central, good transit connections. €600–950/mo."),
      ("Albaro", "Eastern, wealthier, beach access, quiet, English community. €800–1,200/mo."),
    ],
    "scores": [("Expat-friendliness",3),("English",3),("Public transit",3),
               ("Cost",4),("Culture",4),("Safety",3),("Healthcare",4),("Bureaucracy",3)],
    "pros": ["Warmest winter climate of any major northern Italian city","Dramatically beautiful: steep hills, old port, medieval caruggi alleys","Cheapest major city on the Italian Riviera","World's best pesto — Genovese is the original and nothing else comes close","Good hospital infrastructure (Ospedale San Martino is a major teaching hospital)"],
    "cons": ["Some deprived areas near the old port — neighbourhood research essential","Hilly terrain means some areas require funicular or significant walking","Less international community than Milan or Rome","Slightly industrial/commercial character in some zones"],
    "best_for": "Those wanting Mediterranean climate without Rome or Milan prices · Sailors · Maritime history enthusiasts · Budget northern Riviera living",
    "avoid_if": "Those who find hills physically challenging · People expecting Florence-level beauty at street level",
    "take": "Genoa is Italy's most underrated city by a significant margin. The medieval caruggi — narrow alleys climbing the hillsides — are as atmospheric as Venice's canals, the pesto is the best in the world (and Genovese know it), and the rents make northern expats weep with relief. It lacks Rome's glamour but has soul in abundance.",
    "desc": "Genoa sits between mountains and sea on a narrow Ligurian shelf, crammed with history and largely ignored by the tourism industry. This is partly because it doesn't photograph as easily as Florence or the Amalfi Coast, and partly because Genovese don't particularly care whether you come. This combination produces one of Italy's most authentic urban experiences.\n\nThe caruggi — the medieval alley system of the old port — are genuinely extraordinary. Narrow enough to touch both walls simultaneously, rising steeply up the hillside, lined with Baroque chapels and small workshops that haven't changed in a century. UNESCO listed them, and they deserve it.\n\nThe climate is Genoa's practical selling point: the mountains directly behind the city block cold northern air, producing the mildest winter temperatures of any major northern Italian city. While Milan sits in fog at 2°C in January, Genoa can be 12°C and sunny. The difference is significant for daily wellbeing.\n\nThe pesto situation deserves its own paragraph. Genovese pesto made with Ligurian basil (smaller leaf, more delicate) is to the Barilla jar what Neapolitan pizza is to a Domino's delivery. The weekly market at Mercato Orientale sells fresh-made pesto by weight.\n\nRents are lower than the city's quality and position would suggest. Castelletto (funicular to the top, spectacular views) offers 1-bedrooms at €650–1,000. Central Carignano at €600–950. These are Milan-adjacent prices for a coastal Mediterranean city with better weather.",
  },
  {
    "name": "Verona", "italian": "Verona", "region": "Veneto",
    "pop": "260,000", "elev": "59 m", "climate": "Humid continental",
    "best_months": "Apr–Jun, Sep–Oct", "language": "Good English (opera/tourism city)",
    "expat_community": "Medium — wine industry draws international arrivals",
    "budget": (1300, 1900, 2700),
    "neighborhoods": [
      ("Veronetta", "East of the Adige, student quarter, affordable, lively. €650–950/mo."),
      ("Centro Storico", "Beautiful but pricey. The Arena, Roman ruins. €900–1,400/mo."),
      ("Borgo Trento", "Residential, families, good schools, quieter. €700–1,100/mo."),
    ],
    "scores": [("Expat-friendliness",4),("English",4),("Public transit",3),
               ("Cost",3),("Culture",4),("Safety",5),("Healthcare",4),("Bureaucracy",3)],
    "pros": ["Extraordinary safety record — consistently Italy's safest large city","Beautiful compact medieval centre with Roman Arena","Wine country within 30 minutes: Amarone, Valpolicella, Soave, Custoza","Lake Garda 30 minutes west — swimming, sailing, water sports","Northeast Italy's excellent food tradition: horse meat, pastissada, bigoli"],
    "cons": ["Tourist crowds at peak season (Romeo and Juliet balcony is a real thing)","More conservative, traditional character than trendy northern cities","Some transit limitations for outlying areas","Lower international expat density than Rome/Milan/Florence"],
    "best_for": "Wine enthusiasts · Families wanting safety and quality of life · Retirees · Northeast Italy lovers · Opera devotees (the Arena opera season is world-class)",
    "avoid_if": "Those wanting a trendy international city · People who dislike conservative small-city atmospheres",
    "take": "Verona is what you picture when you imagine romantic Italy — the Arena, the medieval streets, the Adige river winding through. It's also genuinely livable: compact, extraordinarily safe, surrounded by extraordinary wine country, with Lake Garda 30 minutes away. For a certain type of expat, it's close to ideal.",
    "desc": "Verona works as a city in a way that not all beautiful Italian cities manage. The centro is compact and walkable, the transit connections are good (on the Milan-Venice rail line), the surrounding countryside is world-class wine territory, and the safety record is Italy's best for a city of its size.\n\nThe Roman Arena di Verona is extraordinary — 30 BC, nearly intact, seating 15,000 for open-air opera every summer. Living in Verona means your summer entertainment might be Aida or La Traviata in a 2,000-year-old amphitheatre under the stars, for €30.\n\nThe wine country begins at the city limits. Valpolicella (the Amarone zone) is 15 minutes north. Soave and its white wines 20 minutes east. Custoza and Bardolino around Lake Garda 30 minutes west. For anyone with serious wine interest, the location is unparalleled.\n\nThe expat community is medium-sized and somewhat self-selected — wine industry professionals, opera devotees, people who found it on a trip and decided to stay. This produces a smaller but more intentional community than Rome or Milan.\n\nThe city has a conservative northeastern Italian character that some expats love (quiet, ordered, excellent services) and others find limiting. Know which type you are before you sign the lease.",
  },
  {
    "name": "Padua", "italian": "Padova", "region": "Veneto",
    "pop": "210,000", "elev": "12 m", "climate": "Humid continental",
    "best_months": "Apr–Jun, Sep–Oct", "language": "Good English (major university)",
    "expat_community": "Medium — university and medical draws",
    "budget": (1100, 1700, 2400),
    "neighborhoods": [
      ("Centro Storico", "Under the arcades, café culture, university energy. €700–1,100/mo."),
      ("Prato della Valle area", "Around the famous elliptical square. Leafy, families. €650–1,000/mo."),
      ("Arcella", "Northern quarter, working class, very affordable. €450–700/mo."),
    ],
    "scores": [("Expat-friendliness",4),("English",4),("Public transit",4),
               ("Cost",4),("Culture",4),("Safety",4),("Healthcare",5),("Bureaucracy",3)],
    "pros": ["Azienda Ospedaliera di Padova: one of Europe's top teaching hospitals","30 minutes to Venice by train — best of both worlds","Much more affordable than Venice for equivalent quality of life","Major university (founded 1222) keeps the city intellectually alive","Giotto's Cappella degli Scrovegni — one of Western art's masterpieces, in this city"],
    "cons": ["Less internationally famous (challenging to explain to visitors)","Cold foggy winters in the Po Valley","Some residential areas are pedestrianly unremarkable","Summer humidity can be oppressive"],
    "best_for": "Those with serious healthcare needs · Academics · Venice lovers who can't afford Venice · Families who want northeastern Italy at lower cost",
    "avoid_if": "Those who need international fame for their city · People who find Veneto winters too cold",
    "take": "Padova has a secret weapon: the University Hospital is considered one of Europe's top five medical facilities. If healthcare is central to your decision — and for many expats it should be — Padova has few peers at this price point. The Bologna-style university city atmosphere and proximity to Venice are bonuses.",
    "desc": "Padova is where people with serious health concerns in Italy tend to end up. The Azienda Ospedaliera di Padova — the University Hospital — is consistently rated among Europe's top five hospitals for both clinical outcomes and research. If you or a family member has a chronic condition, a serious diagnosis, or simply wants access to world-class specialist medicine, Padova's healthcare infrastructure is a decisive factor.\n\nBeyond the hospital, Padova rewards. The university was founded in 1222 — the second oldest in Italy — and the student population keeps the city young. The Prato della Valle, a vast elliptical square with 88 statues along a moat, is one of Italy's most spectacular piazzas. Giotto's frescoes in the Cappella degli Scrovegni (1305) are the best-preserved in existence and among the most important in Western art.\n\nThe Venice proximity (30 minutes by regional train, €5) is practical as well as romantic — you can live at Padovan prices and spend Sundays in Venice. The inverse rarely works: Venice residents often come to Padova for supermarkets and practical services.\n\nThe cost is significantly lower than Venice, slightly below Bologna, and very competitive for the northeast. A 1-bedroom in the centro costs €700–1,100; in the Arcella neighbourhood (less charming, very functional), €450–700.",
  },
  {
    "name": "Lucca", "italian": "Lucca", "region": "Tuscany",
    "pop": "90,000", "elev": "19 m", "climate": "Mediterranean",
    "best_months": "Apr–Jun, Sep–Oct", "language": "Good English (large expat community)",
    "expat_community": "Large relative to size — one of Italy's highest American expat densities",
    "budget": (1200, 1800, 2500),
    "neighborhoods": [
      ("Inside the Walls", "The intact Renaissance walled centre. The Lucca experience. €800–1,300/mo."),
      ("San Concordio", "Just outside walls, locals, practical. €600–900/mo."),
      ("Sant'Anna", "Affordable suburb, good connections to Pisa and Florence. €550–800/mo."),
    ],
    "scores": [("Expat-friendliness",5),("English",4),("Public transit",2),
               ("Cost",3),("Culture",4),("Safety",5),("Healthcare",3),("Bureaucracy",3)],
    "pros": ["One of the highest concentrations of American expats per capita in Italy","Extraordinary intact Renaissance walls — you can cycle the top","Florence 30 minutes by train, Pisa 25 minutes, coast 20 minutes by car","Very safe, very livable at a human scale","Puccini's hometown — world-class summer music festival"],
    "cons": ["Small city — limited services, specialist healthcare in Pisa or Florence","Car recommended for anything beyond the centre","Tourist-driven economy: character can feel performative in peak season","Healthcare limited locally"],
    "best_for": "American retirees (very established community) · Remote workers wanting Tuscany without Florence prices · Writers and music lovers",
    "avoid_if": "Those needing specialist healthcare locally · People wanting big-city energy · Non-drivers",
    "take": "Lucca has one of the highest concentrations of American expats per capita in Italy, and the reason is simple: it is Tuscany in miniature, human-scale, extraordinarily safe, and the intact Renaissance walls make it unlike anywhere else. The expat community has critical mass. For a certain type of American, it's the answer.",
    "desc": "Lucca is where American expats who've done their research tend to end up. The city has accumulated one of the highest concentrations of American residents per capita in Italy, and the community self-reproduces: word of mouth from people who found it brings new arrivals who find the same thing, stay, and tell their friends.\n\nThe physical form is unique. Lucca's Renaissance walls — 4 km of intact 16th-century ramparts — were never breached and were eventually converted into a tree-lined promenade. Cycling the top of the walls at sunset, with the old city below and the Apennines beyond, is one of Italy's everyday extraordinary experiences.\n\nThe size is both Lucca's charm and limitation. At 90,000, it's large enough to have supermarkets, decent restaurants, and a functioning ASL, but small enough to know your neighbourhood quickly. Serious specialist healthcare goes to Pisa (25 minutes) or Florence (30 minutes).\n\nThe Tuscany proximity is a practical asset. Florence day trips are easy — take the morning train, spend the day in the Uffizi, be home for dinner. Pisa (beach access, major international airport) is 25 minutes. The Versilia coast for summer swimming is 20 minutes by car.\n\nThe expat community in Lucca is established enough to have its own bookshops, English-language events, and informal networks that can dramatically shorten the administrative learning curve.",
  },
  {
    "name": "Perugia", "italian": "Perugia", "region": "Umbria",
    "pop": "170,000", "elev": "493 m", "climate": "Humid subtropical (hilltop)",
    "best_months": "Apr–Jun, Sep–Oct", "language": "Good English (major language school city)",
    "expat_community": "Medium — uniquely international for its size",
    "budget": (1000, 1500, 2100),
    "neighborhoods": [
      ("Centro Storico", "Medieval hilltop maze, escalators connect it to lower city. €600–950/mo."),
      ("Fontivegge", "Lower city, modern, near train station. €450–700/mo."),
      ("Piscille / Strozzacapponi", "Residential suburbs, families, affordable. €400–650/mo."),
    ],
    "scores": [("Expat-friendliness",4),("English",4),("Public transit",3),
               ("Cost",4),("Culture",4),("Safety",4),("Healthcare",3),("Bureaucracy",3)],
    "pros": ["Università per Stranieri: the world's most prestigious Italian language school","Very affordable — Tuscany-style experience at lower cost","Extraordinary Umbrian food: truffles, norcineria, Sagrantino wine","Umbria is less touristy than Tuscany — more authentic","Views over the Umbrian valley from the hilltop are spectacular"],
    "cons": ["Hilltop means cold winters — colder than Tuscany at 493m elevation","Car helpful for outlying areas and day trips","Healthcare limited locally — Perugia hospital is serviceable but not top-tier","Smaller economy than Tuscany towns"],
    "best_for": "Italian language learners · Retirees who want Umbria's authenticity · Budget Tuscany alternative · Remote workers who appreciate quiet beauty",
    "avoid_if": "Those who struggle with cold winters · People needing specialist medical access · Car-free expats",
    "take": "Perugia is Italy's gateway to the heartland. The Università per Stranieri makes it a global hub for Italian learners — many expats start with a language course and never leave. The food rivals Tuscany at lower prices, the views are magnificent, and the authentic Umbrian character (less packaged than Tuscany) rewards those who want real Italy.",
    "desc": "Perugia occupies a long ridge 493 metres above the Umbrian valley, connected to itself by a series of medieval escalators (scale mobili) that were installed in car-free medieval passages — an only-in-Italy solution to an only-in-Italy problem.\n\nThe city's defining institution is the Università per Stranieri, the Università degli Stranieri di Perugia — founded 1925, the world's most prestigious dedicated Italian language university. Tens of thousands of foreigners have passed through it. This gives Perugia a permanently international character that its size alone wouldn't generate. The city is used to foreigners. Services exist for foreigners. The social networks exist for foreigners.\n\nUmbrian food is the authentic version of what Tuscan tourism packages. Truffles (black from Norcia, white from around Perugia) are used generously at prices that would shock a Florentine restaurant. Norcineria — the cured pork tradition of Norcia — produces salumi that rivals anything in Italy. The Sagrantino di Montefalco wine from 30 minutes south is one of Italy's great undiscovered reds.\n\nThe cost is significantly lower than Tuscany for equivalent quality. A 1-bedroom in the centro costs €600–950. A sit-down lunch is €10–14. The weekly market on the Piazza IV Novembre is excellent.",
  },
  {
    "name": "Catanzaro", "italian": "Catanzaro", "region": "Calabria",
    "pop": "90,000", "elev": "320 m", "climate": "Mediterranean",
    "best_months": "Apr–Jun, Sep–Nov", "language": "Very limited English",
    "expat_community": "Very small — almost entirely undiscovered",
    "budget": (750, 1100, 1550),
    "neighborhoods": [
      ("Centro Storico", "Traditional, elevated, panoramic views of the coast. €300–500/mo."),
      ("Lido (coastal)", "Beach suburb, summer resort feel, slightly more expensive. €400–650/mo."),
      ("Sala / Germaneto", "Medical university area, modern, functional. €350–550/mo."),
    ],
    "scores": [("Expat-friendliness",2),("English",2),("Public transit",2),
               ("Cost",5),("Culture",3),("Safety",3),("Healthcare",3),("Bureaucracy",2)],
    "pros": ["Italy's lowest cost of living in a regional capital — €750/mo budget realistic","Genuinely undiscovered: no expat tourist-trap pricing","SSN enrollment straightforward (low demand, no queue)","Extraordinary natural surroundings: Sila mountains, Ionian and Tyrrhenian coasts both accessible","Real Calabrian food culture: nduja, bergamot, 'ndrangheta-free neighbourhoods exist"],
    "cons": ["Italian required — essentially no English services","Very small international community","Infrastructure genuinely less developed than northern Italy","Not suitable as first Italy base — requires prior Italy experience","Limited direct international flight connections"],
    "best_for": "Italian speakers wanting genuine Calabria · Serious budget retirees · Adventure expats who have lived in Italy before · Those seeking maximum authenticity at minimum cost",
    "avoid_if": "First-time Italy movers · Non-Italian speakers · Those requiring specialist healthcare or reliable infrastructure · Anyone expecting northern Italian service standards",
    "take": "Catanzaro is for the expat who wants to disappear into real Italy. The €750/month budget is almost shockingly low. The tradeoff is real: you need Italian, you need patience, and your social world will be almost entirely Italian. For those who specifically want that — authentic, cheap, undiscovered — Catanzaro is nearly unbeatable.",
    "desc": "Catanzaro sits between two seas — the Ionian 15 km east, the Tyrrhenian 30 km west — and below the Sila plateau, one of Calabria's extraordinary highland forests. The city is Calabria's regional capital but functions at a scale and pace that Italy's north would find hard to process.\n\nFor the right expat, this is a feature, not a bug. Catanzaro is what Italy was before mass tourism discovered it. The mercato in the old centre sells local produce at prices that have no relationship to what you'd pay in Florence. The restaurant serving home-cooked pasta charges €8–10 for a full meal. The weekly fishmonger at the Lido market sells Ionian catch for €3/kg.\n\nThe nduja (spreadable spicy pork sausage), the bergamot citrus (Reggio Calabria, 80km south, grows 95% of the world's bergamot), the sun-dried tomatoes, the fresh 'Nduja — the food culture is extraordinary and completely off the tourist radar.\n\nThe honest requirements: this city requires Italian, a car, patience with infrastructure, and prior Italy experience. First-timers to Italy should not start here. But an expat who has lived in Italy, speaks functional Italian, and wants to go deeper — Catanzaro rewards them with an experience of Italian life that Rome and Florence simply cannot offer.",
  },
  {
    "name": "Cagliari", "italian": "Cagliari", "region": "Sardinia",
    "pop": "430,000 metro", "elev": "17 m", "climate": "Mediterranean",
    "best_months": "Mar–Jun, Sep–Nov", "language": "Moderate English (growing)",
    "expat_community": "Small but growing — Sardinia is trending",
    "budget": (1000, 1550, 2200),
    "neighborhoods": [
      ("Villanova", "Historic quarter, trendy, young creative crowd. €550–850/mo."),
      ("Stampace", "Ancient Phoenician quarter, gentrifying fast. €500–800/mo."),
      ("Quartiere del Sole / Bonaria", "Residential, families, practical. €450–700/mo."),
    ],
    "scores": [("Expat-friendliness",3),("English",3),("Public transit",3),
               ("Cost",5),("Culture",4),("Safety",5),("Healthcare",4),("Bureaucracy",3)],
    "pros": ["Island lifestyle: Sardinia is genuinely different from mainland Italy","Caribbean-quality beaches 15–30 minutes from the city centre (Poetto, Mari Pintau)","Extraordinary safety — Sardinia consistently has Italy's lowest crime rates","270 sunny days per year — reliable Mediterranean climate","Ospedale Brotzu is a decent regional hospital"],
    "cons": ["Island isolation: mainland travel requires a flight or overnight ferry","Car essential outside the centre","Sardinian economy limited — job market small","Getting to US involves at least one connection (Rome)","Some areas feel underdeveloped compared to mainland cities"],
    "best_for": "Retirees seeking island lifestyle · Remote workers · Water sports enthusiasts · Those who want Mediterranean living at lower cost than Côte d'Azur or Mallorca",
    "avoid_if": "Those who find island logistics stressful · Regular mainland commuters · People needing full specialist medical coverage",
    "take": "Cagliari is the practical gateway to Sardinian island life. The beaches nearby are genuinely Caribbean-quality. The cost is low by any northern Italian standard. The main question is whether you can make peace with island logistics. For those who can — Cagliari is extraordinary.",
    "desc": "Sardinia is not quite Italy and not quite anywhere else — it's been Phoenician, Carthaginian, Roman, Spanish, and Savoyard before becoming Italian, and the island's character reflects all of it. Living in Cagliari means inhabiting that distinct identity while having the practical infrastructure of a regional capital.\n\nThe beaches are the first argument. Poetto — a 10km stretch of white sand with turquoise shallow water — begins at the city limits. Mari Pintau and Villasimius to the east are an hour's drive and among the Mediterranean's most beautiful beaches. This is not a seasonal attraction: the sea is swimmable from April to November.\n\nThe safety record is remarkable. Sardinia has Italy's lowest crime rates, a fact that appears counterintuitive to those unfamiliar with the island. Cagliari's streets are safe at any hour. The island's traditional culture has an unwritten social contract around safety that the statistics confirm.\n\nThe practical trade-off is clear: island logistics. Getting to Rome requires a 1-hour flight or an overnight ferry. Getting to the US involves at least two flights. For expats who visit family regularly, the connection complexity is real.\n\nThe healthcare at Ospedale Brotzu is serviceable for emergencies and routine care. For serious specialist needs, Rome or mainland hospitals are the reference. Plan accordingly.",
  },
  {
    "name": "Trento", "italian": "Trento", "region": "Trentino-Alto Adige",
    "pop": "120,000", "elev": "194 m (Dolomites backdrop)", "climate": "Alpine",
    "best_months": "May–Sep, Dec–Feb (skiing)", "language": "Good English (bilingual German-Italian region)",
    "expat_community": "Small but growing — mountain lifestyle draws",
    "budget": (1300, 1900, 2700),
    "neighborhoods": [
      ("Centro Storico", "Immaculate, Austrian-influenced, compact and walkable. €750–1,200/mo."),
      ("Piedicastello / Gardolo", "Just outside centre, quieter, cheaper. €600–900/mo."),
      ("Villazzano", "Hillside residential, families, peaceful, views. €700–1,050/mo."),
    ],
    "scores": [("Expat-friendliness",4),("English",4),("Public transit",4),
               ("Cost",3),("Culture",4),("Safety",5),("Healthcare",5),("Bureaucracy",4)],
    "pros": ["Best-governed city in Italy — autonomous province status means Swiss-standard infrastructure","Dolomites 45 minutes away: world-class skiing, hiking, climbing","Ospedale Santa Chiara: one of Italy's best regional hospitals","Bilingual German-Italian culture adds unique character","Cleanest air quality and urban environment in Italy"],
    "cons": ["Alpine winters: cold, snowy Nov–Mar","Smaller cultural scene than larger cities","Can feel too neat and quiet for those used to Mediterranean chaos","Higher cost than southern Italy options","Smaller international community"],
    "best_for": "Outdoor and mountain enthusiasts · Families · Skiers · Those who value infrastructure and efficiency · Remote workers who prioritise quality over cost",
    "avoid_if": "Those who came to Italy for the Mediterranean climate · Budget-prioritising expats · People who need southern Italian warmth and chaos",
    "take": "Trento is Italy's best-governed city. The autonomous province status means it runs at a level of efficiency that feels genuinely Swiss. The Dolomites are a 45-minute drive. The hospitals are world-class. The food fuses Italian and Austrian. For expats who prioritise mountains and quality infrastructure over Mediterranean sun and low cost, Trento deserves serious consideration.",
    "desc": "Trento occupies a unique position in Italy. As the capital of the autonomous Province of Trento, it operates under a special administrative arrangement that gives it more funding, autonomy, and administrative capacity than standard Italian cities. The result is visible everywhere: the streets are clean, the buses run on time, the parks are maintained, the bureaucracy functions at something approaching northern European standards.\n\nThe setting is extraordinary. Trento sits in the Adige valley, ringed by mountains, with the Dolomites beginning 30 minutes east. The Dolomites — a UNESCO World Heritage Site and considered by many mountaineers to be the most beautiful mountain range in the world — offer world-class skiing (Dolomiti Superski pass: 1,200 km of pistes), via ferrata climbing routes, and summer hiking at altitude.\n\nThe cultural character is a genuine hybrid. The region was part of Austria until 1919, and the Austrian influence is visible in the architecture, the food (canederli, speck, strudel alongside polenta and risotto), and the temperament (more reserved and organised than the Italian south). German is co-official, though Trento itself is predominantly Italian-speaking.\n\nThe healthcare at Ospedale Santa Chiara is considered one of Italy's best regional hospitals. Combined with the clean environment and mountain lifestyle, Trento attracts expats specifically for health and wellbeing reasons.\n\nThe cost is moderate by Italian standards — lower than Milan or Rome, higher than the south. Worth it for those who value what Trento offers.",
  },
]


# ── Custom Flowables ─────────────────────────────────────────────────────────

class ColorStrip(Flowable):
    """A horizontal coloured band (used as city header)."""
    def __init__(self, text, subtext, bg=DARK, fg=WHITE, height=1.4*cm):
        super().__init__()
        self.text = text
        self.subtext = subtext
        self.bg = bg
        self.fg = fg
        self.bh = height
        self.width = TW
        self.height = height

    def draw(self):
        c = self.canv
        c.setFillColor(self.bg)
        c.rect(0, 0, self.width, self.bh, fill=1, stroke=0)
        c.setFillColor(RED)
        c.rect(0, 0, 4, self.bh, fill=1, stroke=0)
        c.setFillColor(self.fg)
        c.setFont("DIN-Bold", 18)
        c.drawString(14, self.bh - 22, self.text.upper())
        c.setFont("Arial", 9)
        c.setFillColor(colors.HexColor('#bbaa99'))
        c.drawString(14, 6, self.subtext)


class ScoreBar(Flowable):
    """8-row quality score grid."""
    def __init__(self, scores, width=None):
        super().__init__()
        self.scores = scores  # list of (label, 1-5)
        self.width = width or TW
        self.height = len(scores) * 14 + 8

    def draw(self):
        c = self.canv
        row_h = 14
        dot_r = 4
        dots_x = self.width * 0.44
        label_end = self.width * 0.43

        for i, (label, score) in enumerate(self.scores):
            y = self.height - (i + 1) * row_h + 2
            # label
            c.setFont("Arial", 8)
            c.setFillColor(INK2)
            c.drawString(0, y + 2, label)
            # dots
            for d in range(5):
                cx = dots_x + d * (dot_r * 2 + 3)
                cy = y + dot_r
                if d < score:
                    c.setFillColor(RED)
                    c.circle(cx, cy, dot_r, fill=1, stroke=0)
                else:
                    c.setFillColor(BORDER)
                    c.circle(cx, cy, dot_r, fill=1, stroke=0)


class BudgetBox(Flowable):
    """Three-tier monthly budget display."""
    def __init__(self, budget_tuple, width=None):
        super().__init__()
        self.b, self.c, self.e = budget_tuple
        self.width = width or TW
        self.height = 54

    def draw(self):
        c = self.canv
        w3 = self.width / 3
        labels = ["Budget", "Comfortable", "Expat lifestyle"]
        vals = [self.b, self.c, self.e]
        for i, (lbl, val) in enumerate(zip(labels, vals)):
            x = i * w3
            bg = PAPER2 if i == 0 else (PAPER if i == 1 else colors.HexColor('#f0e8e0'))
            c.setFillColor(bg)
            c.rect(x + 1, 1, w3 - 2, self.height - 2, fill=1, stroke=0)
            c.setFillColor(INK4)
            c.setFont("Arial", 7.5)
            c.drawCentredString(x + w3/2, self.height - 14, lbl.upper())
            c.setFillColor(DARK)
            c.setFont("DIN-Bold", 16)
            c.drawCentredString(x + w3/2, self.height - 34, f"€{val:,}")
            c.setFillColor(INK3)
            c.setFont("Arial", 7)
            c.drawCentredString(x + w3/2, 6, "/ month")


# ── Styles ───────────────────────────────────────────────────────────────────

def make_styles():
    s = {}
    s["body"] = ParagraphStyle("body", fontName="Georgia", fontSize=9.5,
        leading=15, textColor=INK2, spaceAfter=7, alignment=TA_JUSTIFY)
    s["h2"] = ParagraphStyle("h2", fontName="DIN-Bold", fontSize=13,
        textColor=DARK, spaceBefore=12, spaceAfter=5)
    s["h3"] = ParagraphStyle("h3", fontName="Arial-Bold", fontSize=9,
        textColor=RED, spaceBefore=8, spaceAfter=3, leading=12)
    s["small"] = ParagraphStyle("small", fontName="Arial", fontSize=8,
        textColor=INK3, leading=12, spaceAfter=4)
    s["small_bold"] = ParagraphStyle("small_bold", fontName="Arial-Bold", fontSize=8,
        textColor=INK2, leading=12, spaceAfter=3)
    s["take"] = ParagraphStyle("take", fontName="Georgia-Italic", fontSize=9.5,
        leading=15, textColor=INK2, spaceAfter=6, alignment=TA_JUSTIFY,
        backColor=PAPER2, borderPad=8)
    s["center"] = ParagraphStyle("center", fontName="Arial", fontSize=8.5,
        textColor=INK3, alignment=TA_CENTER)
    s["title_big"] = ParagraphStyle("title_big", fontName="DIN-Bold", fontSize=42,
        textColor=WHITE, alignment=TA_CENTER, leading=48)
    s["title_sub"] = ParagraphStyle("title_sub", fontName="Georgia-Italic", fontSize=17,
        textColor=colors.HexColor('#bbaa99'), alignment=TA_CENTER, leading=24)
    s["cover_body"] = ParagraphStyle("cover_body", fontName="Georgia", fontSize=10.5,
        textColor=colors.HexColor('#bbaa99'), alignment=TA_CENTER, leading=17)
    s["toc_city"] = ParagraphStyle("toc_city", fontName="Arial-Bold", fontSize=9.5,
        textColor=DARK, leading=14, spaceAfter=1)
    s["toc_region"] = ParagraphStyle("toc_region", fontName="Arial", fontSize=8.5,
        textColor=INK3, leading=12)
    s["intro_h"] = ParagraphStyle("intro_h", fontName="DIN-Bold", fontSize=15,
        textColor=DARK, spaceBefore=14, spaceAfter=6)
    s["comparison_header"] = ParagraphStyle("comparison_header", fontName="Arial-Bold",
        fontSize=7, textColor=WHITE, alignment=TA_CENTER, leading=9)
    s["comparison_cell"] = ParagraphStyle("comparison_cell", fontName="Arial",
        fontSize=7.5, textColor=INK2, alignment=TA_CENTER, leading=10)
    return s


# ── Page template (header + footer) ─────────────────────────────────────────

class PageTemplate:
    def __init__(self):
        self.page_num = 0

    def on_page(self, canvas, doc):
        self.page_num = doc.page
        if doc.page <= 3:
            return
        canvas.saveState()
        # Top rule
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(ML, H - MT + 4*mm, W - MR, H - MT + 4*mm)
        # Top label
        canvas.setFont("Arial", 7)
        canvas.setFillColor(INK4)
        canvas.drawString(ML, H - MT + 5*mm, "WHERE TO LIVE IN ITALY")
        canvas.drawRightString(W - MR, H - MT + 5*mm, "ITALOPEDIA.COM")
        # Bottom rule
        canvas.line(ML, MB - 4*mm, W - MR, MB - 4*mm)
        canvas.setFont("Arial", 7)
        canvas.drawCentredString(W/2, MB - 7*mm, str(doc.page - 3))
        canvas.restoreState()


# ── Document assembly ────────────────────────────────────────────────────────

def build_cover(ST):
    story = []
    story.append(Spacer(1, 3.5*cm))
    story.append(Paragraph("WHERE TO LIVE<br/>IN ITALY", ST["title_big"]))
    story.append(Spacer(1, 0.6*cm))
    story.append(HRFlowable(width=4*cm, thickness=2, color=RED, spaceAfter=14,
                             hAlign='CENTER'))
    story.append(Paragraph("20 City Profiles for American Expats", ST["title_sub"]))
    story.append(Spacer(1, 1.0*cm))
    story.append(Paragraph(
        "Rome · Milan · Florence · Bologna · Turin · Venice · Naples · Palermo<br/>"
        "Catania · Bari · Lecce · Genoa · Verona · Padua · Lucca · Perugia<br/>"
        "Catanzaro · Cagliari · Trento · Siena",
        ST["cover_body"]))
    story.append(Spacer(1, 2.2*cm))
    story.append(Paragraph(
        "Detailed expat-focused city profiles with rent data, quality-of-life scoring,<br/>"
        "neighbourhood guides, and honest advice from 15 years of Italian living.",
        ST["cover_body"]))
    story.append(Spacer(1, 3.0*cm))
    story.append(Paragraph("ITALOPEDIA.COM — 2025 EDITION", ST["center"]))
    story.append(Paragraph("Curated by Fabrizio Boggio · Torino, Piemonte", ST["center"]))
    story.append(PageBreak())
    return story


def build_intro(ST):
    story = []
    story.append(Paragraph("How to Use This Guide", ST["intro_h"]))
    story.append(Paragraph(
        "This guide profiles 20 Italian cities across all major regions, rated and described "
        "specifically for Americans considering a move to Italy. Each profile gives you the "
        "information that travel guides and tourism boards won't: honest assessments of "
        "bureaucracy, healthcare quality, the reality of finding English speakers, and the "
        "real monthly cost of a comfortable life.",
        ST["body"]))
    story.append(Paragraph("The Monthly Budget", ST["h3"]))
    story.append(Paragraph(
        "<b>Budget</b> — the minimum for a modest but comfortable 1-person life (shared apartment, "
        "cooking at home most nights, limited dining out).<br/>"
        "<b>Comfortable</b> — a private 1-bedroom apartment, regular dining out, modest travel within Italy, "
        "private health insurance before SSN enrollment.<br/>"
        "<b>Expat lifestyle</b> — full 1-bedroom, dining out 3–4 times/week, Italian classes, travel, car, "
        "some private healthcare supplements.",
        ST["small"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Quality of Life Scores", ST["h3"]))
    story.append(Paragraph(
        "Each city is scored 1–5 on eight dimensions:<br/>"
        "<b>Expat-friendliness</b>: ease of integration, services in English, administrative support.<br/>"
        "<b>English prevalence</b>: how widely English is spoken in shops, offices, with neighbours.<br/>"
        "<b>Public transit</b>: quality of buses, metro, trams — can you live without a car?<br/>"
        "<b>Cost</b>: value for money — 5 = exceptional value, 1 = Italy's most expensive.<br/>"
        "<b>Culture</b>: museums, opera, events, food culture, historical richness.<br/>"
        "<b>Safety</b>: crime rates, petty theft, street safety — based on ISTAT data.<br/>"
        "<b>Healthcare</b>: quality of local hospitals and SSN specialist coverage.<br/>"
        "<b>Bureaucracy</b>: how functional the local Questura and ASL are for expats.",
        ST["small"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("The Visa Reminder", ST["h3"]))
    story.append(Paragraph(
        "All 20 cities are accessible on the same Italian long-stay visas: the Elective Residence Visa "
        "(passive income, min ~€31,000/year), the Digital Nomad Visa (remote work, min €28,000/year), "
        "or family reunification. Your visa choice doesn't change which city you can live in. "
        "For full visa guidance, see <b>italopedia.com/visas/</b>.",
        ST["small"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("The SSN Note", ST["h3"]))
    story.append(Paragraph(
        "Monthly budget figures assume eventual enrollment in Italy's National Health Service (SSN) "
        "via your local ASL office. Before enrollment (first 3–6 months), add €150–400/month for "
        "private health insurance required by your visa. Elective Residence Visa holders pay an "
        "annual SSN contribution of ~€400–1,500 depending on income. See <b>italopedia.com/healthcare/</b>.",
        ST["small"]))
    story.append(PageBreak())
    return story


def build_toc(ST, cities):
    story = []
    story.append(Paragraph("Table of Contents", ST["intro_h"]))
    story.append(Spacer(1, 0.2*cm))
    data = []
    for i, city in enumerate(cities):
        row = [
            Paragraph(f"{i+1:02d}. {city['name']} — {city['italian']}", ST["toc_city"]),
            Paragraph(city['region'], ST["toc_region"]),
            Paragraph(f"€{city['budget'][1]:,}/mo", ST["toc_region"]),
        ]
        data.append(row)
    col_w = [TW * 0.55, TW * 0.28, TW * 0.17]
    t = Table(data, colWidths=col_w, rowHeights=18)
    t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-1), 0.3, BORDER),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [PAPER, WHITE]),
    ]))
    story.append(t)
    story.append(PageBreak())
    return story


def build_city(city, ST):
    story = []
    # ── Page 1: stats, budget, scores, neighbourhoods ──
    story.append(ColorStrip(
        f"{city['name']}  ·  {city['italian']}",
        f"{city['region']}  ·  {city['pop']}  ·  {city['elev']}  ·  {city['climate']}"
    ))
    story.append(Spacer(1, 0.3*cm))

    # Quick stats row
    qs_data = [[
        Paragraph("<b>Best months</b><br/>" + city["best_months"], ST["small"]),
        Paragraph("<b>English</b><br/>" + city["language"], ST["small"]),
        Paragraph("<b>Expat community</b><br/>" + city["expat_community"], ST["small"]),
    ]]
    qs_t = Table(qs_data, colWidths=[TW*0.28, TW*0.35, TW*0.37])
    qs_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PAPER2),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.3, BORDER),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(qs_t)
    story.append(Spacer(1, 0.25*cm))

    # Budget box
    story.append(Paragraph("MONTHLY BUDGET (1 person)", ST["h3"]))
    story.append(BudgetBox(city["budget"]))
    story.append(Spacer(1, 0.3*cm))

    # Scores + Neighbourhoods side by side
    score_col = [Paragraph("QUALITY OF LIFE SCORES", ST["h3"]),
                 ScoreBar(city["scores"], width=TW*0.42)]
    neigh_paras = [Paragraph("TOP NEIGHBOURHOODS", ST["h3"])]
    for n_name, n_desc in city["neighborhoods"]:
        neigh_paras.append(Paragraph(f"<b>{n_name}</b>", ST["small_bold"]))
        neigh_paras.append(Paragraph(n_desc, ST["small"]))

    side_data = [[score_col, neigh_paras]]
    side_t = Table([[score_col, neigh_paras]],
                   colWidths=[TW*0.44, TW*0.53])
    side_t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (0,-1), 0),
        ('RIGHTPADDING', (1,0), (1,-1), 0),
    ]))
    story.append(side_t)
    story.append(PageBreak())

    # ── Page 2: description, pros/cons, Italopedia take ──
    story.append(ColorStrip(
        f"{city['name']} continued",
        f"Page 2 of 2",
        bg=INK2
    ))
    story.append(Spacer(1, 0.3*cm))

    # Description
    for para in city["desc"].split("\n\n"):
        story.append(Paragraph(para.strip(), ST["body"]))

    story.append(Spacer(1, 0.2*cm))

    # Pros / Cons
    pros_items = [Paragraph("PROS", ST["h3"])]
    for p in city["pros"]:
        pros_items.append(Paragraph(f"• {p}", ST["small"]))
    cons_items = [Paragraph("CONS", ST["h3"])]
    for c_ in city["cons"]:
        cons_items.append(Paragraph(f"◦ {c_}", ST["small"]))

    pc_t = Table([[pros_items, cons_items]], colWidths=[TW*0.5, TW*0.5])
    pc_t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (0,-1), 0),
        ('BACKGROUND', (0,0), (0,-1), PAPER2),
        ('BACKGROUND', (1,0), (1,-1), colors.HexColor('#fdf0ee')),
        ('INNERGRID', (0,0), (-1,-1), 0.3, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(pc_t)
    story.append(Spacer(1, 0.25*cm))

    # Best for / Avoid if
    bf_data = [[
        Paragraph("<b>BEST FOR:</b>  " + city["best_for"], ST["small"]),
    ], [
        Paragraph("<b>AVOID IF:</b>  " + city["avoid_if"], ST["small"]),
    ]]
    bf_t = Table(bf_data, colWidths=[TW])
    bf_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PAPER),
        ('BOX', (0,0), (-1,-1), 0.5, BORDER),
        ('LINEBELOW', (0,0), (0,0), 0.3, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(bf_t)
    story.append(Spacer(1, 0.3*cm))

    # The Italopedia Take
    story.append(Paragraph("THE ITALOPEDIA TAKE", ST["h3"]))
    take_box = Table([[Paragraph(
        f'“{city["take"]}”', ST["take"]
    )]], colWidths=[TW])
    take_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PAPER2),
        ('BOX', (0,0), (-1,-1), 0.8, RED),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(take_box)
    story.append(PageBreak())
    return story


def build_comparison(ST, cities):
    story = []
    story.append(Paragraph("City Comparison at a Glance", ST["intro_h"]))
    story.append(Paragraph(
        "All 20 cities ranked side by side. Scores are on a 1–5 scale (5 = best). "
        "Budget = monthly cost for 1 person, basic comfortable lifestyle.",
        ST["small"]))
    story.append(Spacer(1, 0.3*cm))

    def sc(label): return Paragraph(label, ST["comparison_header"])
    def cv(val): return Paragraph(str(val), ST["comparison_cell"])

    headers = [sc(h) for h in ["CITY","REGION","BUDGET/MO","ENGLISH","TRANSIT","COST","SAFETY","HEALTH","BUREAU."]]
    rows = [headers]
    for city in cities:
        score_dict = {k: v for k, v in city["scores"]}
        rows.append([
            cv(city["name"]),
            cv(city["region"][:12]),
            cv(f"€{city['budget'][1]:,}"),
            cv("●" * score_dict.get("English",3) + "○" * (5 - score_dict.get("English",3))),
            cv("●" * score_dict.get("Public transit",3) + "○" * (5 - score_dict.get("Public transit",3))),
            cv("●" * score_dict.get("Cost",3) + "○" * (5 - score_dict.get("Cost",3))),
            cv("●" * score_dict.get("Safety",3) + "○" * (5 - score_dict.get("Safety",3))),
            cv("●" * score_dict.get("Healthcare",3) + "○" * (5 - score_dict.get("Healthcare",3))),
            cv("●" * score_dict.get("Bureaucracy",3) + "○" * (5 - score_dict.get("Bureaucracy",3))),
        ])

    cw = [TW*0.14, TW*0.13, TW*0.1, TW*0.09, TW*0.09, TW*0.09, TW*0.09, TW*0.09, TW*0.09]
    t = Table(rows, colWidths=cw, rowHeights=[16] + [14]*len(cities))
    style = [
        ('BACKGROUND', (0,0), (-1,0), DARK),
        ('FONTNAME', (0,0), (-1,0), 'Arial-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [PAPER, WHITE]),
        ('GRID', (0,0), (-1,-1), 0.3, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]
    # Highlight row for the cheapest cities (cost score 5)
    for i, city in enumerate(cities, 1):
        cost_score = dict(city["scores"]).get("Cost", 0)
        if cost_score == 5:
            style.append(('BACKGROUND', (2,i), (2,i), colors.HexColor('#eaf7f0')))
    t.setStyle(TableStyle(style))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Cost column: green = best value (score 5). Full profiles with neighbourhood guides, "
        "pros/cons, and editorial assessments for each city in the preceding pages.",
        ST["small"]))
    story.append(PageBreak())
    return story


def build_closing(ST):
    story = []
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("Your Next Steps", ST["intro_h"]))
    story.append(Paragraph(
        "You've found your city. Here's what comes next — and where Italopedia can help:",
        ST["body"]))

    steps = [
        ("1. Choose your visa", "The Elective Residence Visa (passive income ≥€31,000/year) or "
         "Digital Nomad Visa (remote work ≥€28,000/year) cover most American moves. "
         "Full guides: italopedia.com/visas/"),
        ("2. Plan your first 90 days", "Permesso di soggiorno, Anagrafe registration, codice fiscale, "
         "tessera sanitaria, bank account, SIM card — the complete sequence. "
         "Guide: italopedia.com/residency/"),
        ("3. Sort your taxes", "US citizens owe US taxes regardless of where they live, plus Italian taxes "
         "as a resident. The US-Italy treaty prevents most double taxation. "
         "Guide: italopedia.com/taxes/"),
        ("4. Book a consultation", "A 1:1 call with Fabrizio to go through your specific situation — "
         "visa path, city choice, timeline, tax setup. "
         "italopedia.com/consult/"),
    ]
    for title, text in steps:
        story.append(Paragraph(title, ST["h3"]))
        story.append(Paragraph(text, ST["small"]))

    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width=TW, thickness=0.5, color=BORDER, spaceAfter=14))
    story.append(Paragraph(
        "Italopedia.com — The complete English-language reference for Americans moving to Italy.<br/>"
        "Written from Torino, Piemonte. Verified against official Italian sources. Updated 2025.",
        ST["center"]))
    return story


# ── Cover page canvas (dark background) ─────────────────────────────────────

class CoverCanvas:
    def __call__(self, canvas, doc):
        if doc.page == 1:
            canvas.saveState()
            canvas.setFillColor(DARK)
            canvas.rect(0, 0, W, H, fill=1, stroke=0)
            # Red top stripe
            canvas.setFillColor(RED)
            canvas.rect(0, H - 8*mm, W, 8*mm, fill=1, stroke=0)
            # Bottom stripe
            canvas.rect(0, 0, W, 6*mm, fill=1, stroke=0)
            canvas.restoreState()
        elif doc.page > 3:
            # Running header/footer
            canvas.saveState()
            canvas.setStrokeColor(BORDER)
            canvas.setLineWidth(0.5)
            canvas.line(ML, H - MT + 4*mm, W - MR, H - MT + 4*mm)
            canvas.setFont("Arial", 7)
            canvas.setFillColor(INK4)
            canvas.drawString(ML, H - MT + 5*mm, "WHERE TO LIVE IN ITALY")
            canvas.drawRightString(W - MR, H - MT + 5*mm, "ITALOPEDIA.COM")
            canvas.line(ML, MB - 4*mm, W - MR, MB - 4*mm)
            canvas.drawCentredString(W/2, MB - 7*mm, str(doc.page - 3))
            canvas.restoreState()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    ST = make_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=ML, rightMargin=MR,
        topMargin=MT + 6*mm, bottomMargin=MB + 5*mm,
        title="Where to Live in Italy: 20 City Profiles",
        author="Fabrizio Boggio — Italopedia",
        subject="City guide for Americans moving to Italy",
    )

    story = []
    story += build_cover(ST)
    story += build_intro(ST)
    story += build_toc(ST, CITIES)
    for city in CITIES:
        story += build_city(city, ST)
    story += build_comparison(ST, CITIES)
    story += build_closing(ST)

    cover_cb = CoverCanvas()
    doc.build(story, onFirstPage=cover_cb, onLaterPages=cover_cb)
    print(f"Generated: {OUTPUT}")
    size_kb = OUTPUT.stat().st_size // 1024
    pages = len(CITIES) * 2 + 4 + 2  # city pages + cover/intro/toc + comparison/closing
    print(f"Size: {size_kb} KB  |  Estimated pages: ~{pages}")


if __name__ == "__main__":
    main()
