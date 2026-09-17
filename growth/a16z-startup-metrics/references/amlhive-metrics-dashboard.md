# AMLHive Operational Metrics Dashboard & a16z Mapping

This document maps the a16z startup metrics directly to **AML Hive (amlhive.com.au)**, an Australian regulatory technology SaaS serving AUSTRAC-regulated reporting entities (solicitors, accountants, real estate agents, remittances, crypto, and financial institutions).

---

## 1. AMLHive Metric Definitions & Benchmarks

| a16z Metric | AMLHive Domain Equivalent | Calculation Method / Source | Target Benchmark |
|:---|:---|:---|:---|
| **ARR** | Contracted Annual Compliance Subscriptions | Normalized annual subscription run rate (excluding one-off ASIC top-ups) | Growth > 15% MoM |
| **MRR** | Monthly Active Recurring Subscriptions | Active Stripe subscriptions (Starter, Professional, Enterprise) | Monitored 1st of month |
| **Search Gross Margin** | Net margin after ASIC / PEP search COGS | $\frac{\text{Search Revenue} - \text{ASIC & PEP API Fees}}{\text{Search Revenue}} \times 100\%$ | **$\ge 75\%$** |
| **Blended CAC** | Cost to acquire a reporting entity | (Google/LinkedIn Ads + SEO/Outreach costs) / New Entities | **$\le \$250$** (SMB tiers) |
| **CAC Payback** | Months to recoup compliance entity acquisition | $\frac{\text{CAC}}{\text{Monthly Subscription} \times \text{Gross Margin}}$ | **$\le 4-6$ months** |
| **LTV / CAC** | Lifetime regulatory value vs acquisition | $\frac{\text{ARPU} \times \text{Gross Margin}}{\text{Monthly Churn}} / \text{CAC}$ | **$\ge 4.0\times$** |
| **Logo Churn** | Entity drop-off rate | Entities cancelling subscription / Active Entities | **$\le 1.5\%$ monthly** |
| **Net Retention (NRR)** | Expansion via Tranche 2 & added seats | Retention + upgrade to full independent reviews / extra search packs | **$\ge 115\%$** |
| **Regulatory Surge** | AUSTRAC Compliance Report Season | Annual spike in onboarding prior to 31 March regulatory deadlines | Seasonal capacity buffer |

---

## 2. COGS Breakdown for AMLHive Search Engine

To maintain healthy SaaS gross margins ($\ge 75\%$), AMLHive tracks direct search execution COGS:
1. **ASIC Registry Query API Fees**: Direct cost per business lookup or company register extract.
2. **PEP & Sanctions Data Provider Fees**: Tiered query pricing for international sanctions list checks.
3. **SMS Verification (Brevo / Twilio)**: Identity validation message costs for client 2FA.
4. **Cloud Database Query Overhead**: AWS RDS Aurora & OpenSearch infrastructure costs dedicated to live verification queries.

*Rule: Never count general engineering R&D or founder salaries in COGS; count only incremental delivery costs.*

---

## 3. Weekly & Monthly Fleet Reporting Integration

In the AMLHive fleet (via Hermes/Pluto weekly reviews and the monthly strategy review):
- **Weekly Pulse (Monday briefing)**: Tracks active reporting entities, weekly search query volume, and new paid subscriptions.
- **Monthly Board Pack**:
  - ARR / MRR bridge (Starting, New, Expansion, Contraction, Churned).
  - Search unit economics (cost per scan vs revenue per scan).
  - LTV/CAC and Payback trajectory.
  - Cash runway and net burn against AWS / SaaS hosting expenses.
