# Italopedia.com

**Move to Italy. Do it right.**  
The complete English-language reference for Americans moving to and living in Italy.

A static multi-page editorial site — 260+ guides across 8 topic categories, written from Piedmont and verified against official Italian sources.

---

## 🇮🇹 What's inside

```
italopedia/
├── index.html                  Homepage
├── 404.html                    Not found page
├── robots.txt                  Search-engine directives
├── sitemap.xml                 XML sitemap
├── _headers                    Cloudflare Pages: cache + security headers
├── _redirects                  Cloudflare Pages: legacy URL redirects
├── favicon.svg                 Site icon
│
├── assets/
│   ├── css/main.css           Single shared stylesheet (design system)
│   └── js/
│       ├── main.js            Shared interactions: nav, faq, search, toc
│       └── search-index.js    Client-side search index
│
├── visas/                      Hub: 30 visa guides
│   ├── index.html
│   ├── elective-residence-visa/index.html
│   └── digital-nomad-visa/index.html
├── residency/                  Hub: 28 residency guides
│   ├── index.html
│   └── permesso-di-soggiorno/index.html
├── taxes/                      Hub: 28 tax guides
│   ├── index.html
│   └── flat-tax-regime/index.html
├── healthcare/                 Hub: 25 healthcare guides
│   └── index.html
├── property/                   Hub: 32 property guides
│   └── index.html
├── citizenship/                Hub: 28 citizenship guides
│   ├── index.html
│   └── jure-sanguinis/index.html
├── regions/                    Hub: 42 regional guides
│   └── index.html
├── cost-of-living/             Hub: 30 cost-of-living guides
│   └── index.html
│
├── about/                      About Sara & editorial standards
├── consult/                    Book a 1:1 video consultation
├── shop/                       Premium PDF guides
├── resources/                  Free links, calculators, templates
├── newsletter/                 Subscribe to the weekly newsletter
├── checklist/                  Free 47-point checklist
│
└── (legal)
    ├── privacy/
    ├── terms/
    ├── cookies/
    ├── disclaimer/
    └── affiliate-disclosure/
```

---

## 🚀 Deploying

This is a **fully static site**. Nothing to build, nothing to install. Drop the folder into any static host.

### Option A — Cloudflare Pages (recommended)

1. Push this folder to a GitHub repository.
2. Go to **Cloudflare → Workers & Pages → Create application → Pages → Connect to Git**.
3. Select your repo. Use these build settings:
   - **Build command:** *(leave empty)*
   - **Build output directory:** `/`
4. Click **Save and Deploy**. Done.

`_headers` and `_redirects` are honored automatically by Cloudflare Pages.

To attach `italopedia.com`:
- In Cloudflare Pages → **Custom domains** → add `italopedia.com` + `www.italopedia.com`.
- Cloudflare auto-issues SSL.

### Option B — GitHub Pages

1. Push this folder to a GitHub repository (`main` branch).
2. **Settings → Pages → Build and deployment → Source: Deploy from a branch**.
3. Select `main` / `/` (root). Save.
4. Site goes live at `https://<username>.github.io/<repo>/`.

⚠️ GitHub Pages does not read `_headers` or `_redirects`. They are Cloudflare-specific. The site still works; you just don't get the security headers or redirects.

### Option C — Any other static host

Netlify, Vercel, Render, S3+CloudFront, even plain Nginx. Just serve the folder. Nothing else.

---

## 🛠 Editing content

Every page is **plain HTML** with `<link rel="stylesheet" href="../assets/css/main.css">`. No frameworks, no build step, no JavaScript bundlers, no React. Open the file in your editor, change the words, save, refresh.

### To add a new article

1. Create a new folder: `visas/your-new-article-slug/`
2. Copy any existing article (e.g. `visas/digital-nomad-visa/index.html`) as a template
3. Edit the content — title, body, breadcrumb, related links
4. Add the article to its hub's article list (`visas/index.html`)
5. Add it to `assets/js/search-index.js` so search finds it
6. Add the URL to `sitemap.xml`

### To add a new hub category

1. Create a new folder: `your-category/`
2. Copy an existing hub (e.g. `regions/index.html`) as a template
3. Add the category to the top nav in **every** page (`<nav class="topnav">`)
4. Add to the footer too
5. Add to homepage `.hubs-grid` and the stats bar
6. Add to `sitemap.xml`

---

## 🎨 Design system

The visual language is fully defined in `assets/css/main.css` — single source of truth. Tokens at the top:

```css
:root {
  --paper:#faf7f0;      /* background */
  --ink:#1a1610;        /* primary text */
  --red:#b83020;        /* italian flag red (primary accent) */
  --green:#1e6b3a;      /* italian flag green */
  --serif:'Cormorant Garamond';
  --sans:'Syne';
  --mono:'DM Mono';
}
```

To re-skin the site, change those values.

---

## 📜 License

© Sara Bianchi · All rights reserved. Editorial content is copyrighted. The design is custom and not licensed for reuse.

---

## ✉️ Contact

- editor@italopedia.com — editorial
- privacy@italopedia.com — data/GDPR
- press@italopedia.com — media

Made with espresso in Piedmont 🇮🇹
