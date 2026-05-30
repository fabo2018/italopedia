#!/usr/bin/env python3
"""
TASK 1: Wire Add-to-Cart buttons in /shop/ to /checkout/ intermediate page.
TASK 2: Add "Shop" link to navbar in every HTML page.
"""

import os, re, glob

BASE = os.path.dirname(os.path.abspath(__file__))

# ══════════════════════════════════════════════════════════════════
# TASK 1 — Shop page: wire buttons
# ══════════════════════════════════════════════════════════════════

SHOP_PATH = os.path.join(BASE, 'shop', 'index.html')

# Products in the order they appear in shop/index.html
# (card 1→6 top-to-bottom, then the All-Access bundle at bottom)
SHOP_PRODUCTS = [
    # (slug, price, stripe_url)
    ('visa-bundle',      '49',  'https://buy.stripe.com/9B600icgQgqn5FU9f2bsc05'),
    ('jure-sanguinis',   '39',  'https://buy.stripe.com/dRm28q1Cc6PN8S6bnabsc03'),
    ('tax-guide',        '29',  'https://buy.stripe.com/cNi7sKft24HF9Wa9f2bsc04'),
    ('buying-property',  '35',  'https://buy.stripe.com/00waEWa8Ib632tIdvibsc02'),
    ('first-90-days',    '24',  'https://buy.stripe.com/00w7sKbcM2zx0lAfDqbsc06'),
    ('where-to-live',    '19',  'https://buy.stripe.com/fZucN4a8Ia1Z5FU8aYbsc01'),
]

BUNDLE = ('all-access-bundle', '129', 'https://buy.stripe.com/8x23cubcM1vtd8m8aYbsc00')

OLD_CART_BTN   = '<button class="shop-btn">Add to cart →</button>'
OLD_BUNDLE_BTN = '<button class="btn-primary" style="background:var(--red)">Get the bundle →</button>'

with open(SHOP_PATH, encoding='utf-8') as f:
    shop = f.read()

orig = shop

# Replace the 6 "Add to cart" buttons in order
for slug, price, stripe in SHOP_PRODUCTS:
    url = f'../checkout/?product={slug}&amp;price={price}&amp;link={stripe}'
    new_btn = f'<a href="{url}" class="shop-btn">Add to cart →</a>'
    shop = shop.replace(OLD_CART_BTN, new_btn, 1)

# Replace the All-Access bundle button
slug, price, stripe = BUNDLE
url = f'../checkout/?product={slug}&amp;price={price}&amp;link={stripe}'
shop = shop.replace(
    OLD_BUNDLE_BTN,
    f'<a href="{url}" class="btn-primary" style="background:var(--red)">Get the bundle →</a>'
)

if shop != orig:
    with open(SHOP_PATH, 'w', encoding='utf-8') as f:
        f.write(shop)
    print('✅ TASK 1: shop/index.html — 7 buttons wired to checkout')
else:
    print('⚠️  TASK 1: no changes made to shop/index.html')

# ══════════════════════════════════════════════════════════════════
# TASK 2 — Navbar: add Shop after Cost of Living
# ══════════════════════════════════════════════════════════════════

def get_prefix(fpath):
    """Return relative prefix (../../) based on file depth from BASE."""
    rel = os.path.relpath(fpath, BASE)
    depth = len(rel.split(os.sep)) - 1  # -1 for the filename itself
    return '../' * depth

all_html = sorted(glob.glob(os.path.join(BASE, '**', '*.html'), recursive=True))
all_html = [f for f in all_html if '/assets/' not in f.replace('\\', '/')]

nav_updated = 0

for fpath in all_html:
    with open(fpath, encoding='utf-8') as f:
        content = f.read()

    # Skip if Shop already in navbar (guard against double-run)
    if 'class="nav-link">Shop</a>' in content:
        continue

    prefix = get_prefix(fpath)
    old_nav = 'class="nav-link">Cost of Living</a>'
    new_nav = f'class="nav-link">Cost of Living</a><a href="{prefix}shop/" class="nav-link">Shop</a>'

    if old_nav not in content:
        continue

    content = content.replace(old_nav, new_nav, 1)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    nav_updated += 1

print(f'✅ TASK 2: Shop added to navbar in {nav_updated} pages')
