# JS Bundle Pricing Extraction — Product Research Technique

## When to Use

Investigating a product or startup's pricing when:
- The landing page only shows a "Reserve for $X" deposit, not the full price
- The pricing page is a client-rendered SPA (React, Vue, etc.)
- The page HTML contains only marketing copy, no pricing data
- You want to verify pricing claims before writing a competitive analysis

## How It Works

Modern SPAs bundle their entire application configuration (including pricing constants) into a single minified JS file. This file is loaded by the browser but is also `curl`-accessible — it contains the raw configuration objects in plain text alongside the minified framework code.

## Extraction Steps

### Step 1: Find the JS Bundle URL

```bash
curl -sL "https://example.com" | grep -oP 'src="[^"]*\.js"' | head -5
```

The main bundle is typically `/assets/index-XXXXXXXX.js`. Look for files with `-B7U9ndqc.js` style hashed names, not `vendor.js` or `runtime.js`.

### Step 2: Download the Bundle

```bash
curl -sL -o /tmp/bundle.js "https://example.com/assets/index-B7U9ndqc.js"
```

### Step 3: Search for Pricing Patterns

The most reliable signal is finding the `Af=` (pricing config) or similar object. Common patterns:

```bash
# Find pricing configuration object
grep -oP 'Af\s*=\s*\{.*?\};' /tmp/bundle.js

# Find currency + number patterns
grep -oP '.{0,20}(full|reservation|price|deposit).{0,40}' /tmp/bundle.js | sort -u

# Find dollar amounts
strings /tmp/bundle.js | grep -P '\$\d+' | sort -u

# Find currency config
grep -oP 'currency["\']?\s*[:=]\s*["\']([A-Z]{3}|.)["\']' /tmp/bundle.js
```

### Step 4: Extract Structured Data

Modern SPAs define pricing as a dictionary/map, typically keyed by payment provider:

```javascript
// Stripe pricing (USD)
Af={
  [Lt.stripe]: {currency: "$", currencyCode: "USD", full: 399, reservation: 19},
  [Lt.wechat]: {currency: "¥", currencyCode: "CNY", reservation: 129}
};
```

Fields to look for:
- `full` — Full retail price (this is what the user cares about)
- `reservation` / `deposit` — Pre-order deposit (shown on the landing page)
- `currency` / `currencyCode` — Currency symbol and ISO code
- Provider keys (`stripe`, `wechat`, `paypal`) — Different pricing for different markets

### Step 5: Cross-Reference with Page HTML

Search the JS bundle for order/payment flow text to understand pricing structure:

```bash
grep -oP '.{0,50}(remaining|balance|shipping|refund|total).{0,50}' /tmp/bundle.js | sort -u
```

This reveals important details like:
- "You'll pay the remaining balance before your unit ships" — confirms deposit ≠ full price
- "If your unit isn't ready for shipping by end of August, your reservation will be automatically refunded" — refund policy
- "Charging accessories are included" — what's in the box

## Known Example

**Monako.ai** (June 12, 2026):

Landing page showed only "RESERVE FOR 19$" — no full price. JS bundle revealed:

```javascript
Af={
  [Lt.stripe]: {currency: "$", currencyCode: "USD", full: 399, reservation: 19},
  [Lt.wechat]: {currency: "¥", currencyCode: "CNY", reservation: 129}
};
```

**Full price: $399 USD** ($19 deposit + $380 balance before shipping).
Shipping target: July-August 2026. Auto-refund if not shipped by end of August.

## Limitations

- **Not all bundles use `Af=`** — the variable name varies per project. Common names: `pricing`, `PRICES`, `config`, `settings`, `Af` (React naming convention artifact).
- **Minification can obscure variable names** — search for number patterns (`399`, `19`, `0.99`) near currency strings instead.
- **Some SPAs load pricing via API** (not bundled) — if the JS bundle has no pricing config, check for API endpoint patterns like `/api/pricing`, `/api/products`.
- **React production bundles are ~235KB+** — use `strings` or targeted `grep`, not `cat`, to avoid flooding your context window.
