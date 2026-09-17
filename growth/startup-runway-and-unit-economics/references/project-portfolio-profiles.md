# Portfolio Project Economic Profiles

Specific unit economic structures, expense baselines, and revenue levers for portfolio ventures.

---

## 1. AML Hive (B2B Regulatory SaaS)

- **Revenue Model**: Tiered recurring subscriptions ($149/mo Starter, $499/mo Pro, $1,500/mo Enterprise) + pre-purchased search credit top-ups.
- **Direct Unit Costs (COGS)**:
  - ASIC lookup API queries ($1.20 – $2.50 per query depending on register).
  - PEP & Sanctions watchlist lookups ($0.30 – $0.80 per check).
  - Brevo / SMS identity tokens ($0.05 per SMS).
  - Stripe transaction fee: 1.75% + A$0.30.
- **Gross Margin Target**: $\ge 75\%$.
- **Burn Levers**:
  - AWS Aurora Postgres & OpenSearch cluster right-sizing.
  - S&M efficiency via organic search authority rather than high-CPC paid ads.

---

## 2. Tapease (Merchant Payments & POS)

- **Revenue Model**: Merchant discount rate (MDR) fee spread (e.g. 1.2% – 1.8% per card transaction) + terminal lease / software subscription ($29–$59/mo per terminal).
- **Direct Unit Costs (COGS)**:
  - Interchange scheme fees (Visa/Mastercard interchange rates).
  - Acquiring bank processor fees.
  - POS hardware amortization & shipping.
- **Gross Margin Target**: $40\% – 60\%$ (fintech payment margins are structurally lower than pure SaaS).
- **Cashflow Profile**: Highly sensitive to gross merchant volume (GMV) and transaction settlement velocity (daily batch sweeps).

---

## 3. Simplifii-OS (Autonomous AI Developer & Agent Platform)

- **Revenue Model**: Developer seat subscription ($20 – $80/user/mo) + metered AI execution compute.
- **Direct Unit Costs (COGS)**:
  - LLM inference API tokens (Claude, OpenAI, DeepSeek, Gemini).
  - Cloud serverless runtime compute (Workers, Lambda, ECS).
  - Vector database storage & vector search read units.
- **Gross Margin Target**: $\ge 70\%$.
- **Key Risk**: Token consumption spikes without hard quota ceilings per user.
