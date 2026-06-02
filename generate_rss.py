#!/usr/bin/env python3
"""
Generates /feed.xml — RSS 2.0 feed with the 20 most recent articles.
Run this script every time new articles are published.
"""
import os, re
from datetime import datetime, timezone
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.abspath(__file__))

articles = []

for dirpath, _, filenames in os.walk(ROOT):
    for fname in filenames:
        if fname != "index.html":
            continue
        fpath = os.path.join(dirpath, fname)
        with open(fpath, encoding="utf-8") as f:
            content = f.read()

        if '"datePublished"' not in content:
            continue

        title  = re.search(r'<title>([^<]+)</title>', content)
        desc   = re.search(r'"description":"([^"]{20,400})"', content)
        date   = re.search(r'"datePublished":"([^"]+)"', content)
        canon  = re.search(r'<link rel="canonical" href="([^"]+)"', content)

        if not (title and date and canon):
            continue

        title_text = title.group(1).replace(" — Italopedia", "").strip()
        desc_text  = desc.group(1) if desc else ""
        date_str   = date.group(1)          # e.g. 2026-05-08
        url        = canon.group(1)

        try:
            pub_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue

        articles.append({
            "title":    title_text,
            "desc":     desc_text,
            "date":     pub_date,
            "date_str": date_str,
            "url":      url,
        })

# Sort newest first, keep top 20
articles.sort(key=lambda x: x["date"], reverse=True)
articles = articles[:20]

now_rfc822 = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

def to_rfc822(dt):
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")

items = ""
for a in articles:
    items += f"""
  <item>
    <title>{escape(a['title'])}</title>
    <link>{escape(a['url'])}</link>
    <guid isPermaLink="true">{escape(a['url'])}</guid>
    <pubDate>{to_rfc822(a['date'])}</pubDate>
    <description>{escape(a['desc'])}</description>
  </item>"""

feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Italopedia — Move to Italy Guide for Americans</title>
    <link>https://italopedia.com/</link>
    <description>The complete English-language reference for Americans moving to and living in Italy. Guides on visas, residency, taxes, healthcare, property, citizenship, regions, and cost of living.</description>
    <language>en-us</language>
    <lastBuildDate>{now_rfc822}</lastBuildDate>
    <atom:link href="https://italopedia.com/feed.xml" rel="self" type="application/rss+xml"/>
    <image>
      <url>https://italopedia.com/assets/images/og-default.jpg</url>
      <title>Italopedia</title>
      <link>https://italopedia.com/</link>
    </image>{items}
  </channel>
</rss>"""

out_path = os.path.join(ROOT, "feed.xml")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(feed)

print(f"Generated feed.xml with {len(articles)} items")
for a in articles:
    print(f"  {a['date_str']}  {a['url']}")
