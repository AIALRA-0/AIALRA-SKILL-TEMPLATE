# Retail offer evidence schema

Read this file before recording offers. Keep unknown values as `null`; never convert an unknown cost to zero.

## Required fields

| Field | Meaning |
|---|---|
| `platform` | Retailer or marketplace name |
| `title` | Listing title as observed |
| `product_key` | GTIN/UPC/EAN/ASIN/SKU, or normalized brand + model + generation + core variant |
| `variant` | Capacity, color, size, region, network, bundle, or other selected option |
| `condition` | New, refurbished, open-box, used, parts, or another explicit condition |
| `quantity` | Comparable unit or bundle count |
| `price` | Selected-variant item price before other cost components |
| `currency` | ISO 4217 code such as `USD` or `CNY` |
| `shipping` | Known shipping amount, `0` only when explicitly free, otherwise `null` |
| `tax` | Known tax amount or `null` |
| `fees` | Known marketplace, import, recycling, or service fees, otherwise `null` |
| `verified_discount` | Discount visibly applied to this offer; unverified coupons remain `null` |
| `known_total` | Decimal sum of known charges minus verified discount |
| `seller` | Legal or displayed seller identity |
| `fulfillment` | Party responsible for shipping or pickup |
| `stock` | In stock, limited, preorder, backorder, out of stock, or unknown |
| `price_scope` | Public, member, newcomer, subscription, group-buy, auction, or personalized |
| `source_type` | Official API, direct product page, third-party discovery, or search discovery |
| `url` | Direct product URL without added affiliate parameters |
| `retrieved_at` | ISO 8601 timestamp including timezone |

Use decimal strings for money in structured data, for example `"199.99"`, to avoid binary floating-point errors.

## Comparability key

Only rank offers together when all of these match:

```text
product_key + variant + condition + quantity + currency + cost_basis
```

`cost_basis` is one of:

- `item-only`: item price is known but one or more mandatory costs are unknown;
- `pre-tax-delivered`: item, verified discount, shipping, and mandatory fees are known;
- `all-known-total`: every currently determinable mandatory cost is included.

Do not rank an `item-only` offer ahead of an `all-known-total` offer solely because its displayed number is lower. Present separate groups or obtain the missing costs.

## Eligibility for the winner

An offer may be recommended as the lowest verified option only when it has:

- exact product and variant match;
- acceptable condition and quantity;
- direct product-page or official-API evidence;
- current stock or an explicitly acceptable preorder state;
- direct URL and timestamp;
- a cost basis comparable with every other ranked row.

Search snippets, category cards, expired pages, indirect affiliate pages, unavailable inventory, and low-confidence matches may be shown as leads but cannot win.

## Default report table

```markdown
| Store | Exact item / variant | Condition | Seller / fulfillment | Item | Shipping | Tax / fees | Verified discount | Known total | Stock / price scope | Retrieved | Link |
|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|
```

After the table, state:

1. the lowest verified option and the exact comparison basis;
2. account, membership, pickup, delivery, warranty, and return conditions;
3. every requested source that was inaccessible, unmatched, out of stock, or unchecked;
4. all unknown mandatory costs that could change the ranking.
