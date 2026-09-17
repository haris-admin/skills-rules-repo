# Runway, Burn Rate, and Cashflow Modeling Guide

A quantitative methodology for tracking startup cash depletion, projecting runway, and determining Default Alive vs Default Dead status.

---

## 1. Burn Rate Definitions

### Gross Monthly Burn
Total cash outflow spent in a single calendar month:
$$\text{Gross Burn} = \text{Headcount \& Contractors} + \text{Cloud \& SaaS Tools} + \text{Marketing Spend} + \text{Admin / Legal / Tax}$$

### Net Monthly Burn
True monthly cash depletion after accounting for customer collections:
$$\text{Net Burn} = \text{Gross Burn} - \text{Cash Collected (Revenue Inflows)}$$

*Note: Use actual bank cash receipts rather than GAAP accrual revenue when calculating net burn.*

---

## 2. Runway & Zero Cash Date (ZCD)

### Static Runway (Months)
$$\text{Runway (Months)} = \frac{\text{Current Available Cash Balance}}{\text{Average Net Monthly Burn}}$$

### Zero Cash Date (ZCD)
$$\text{ZCD} = \text{Current Date} + \text{Runway in Days}$$

### Runway Health Classification

| Runway Range | Health State | Operational Action Required |
|:---|:---|:---|
| **$> 18$ months** | **Comfortable Growth** | Invest in product roadmap and scalable acquisition channels. |
| **$12 – 18$ months** | **Normal Operating Range** | Monitor unit economics; maintain hiring discipline. |
| **$6 – 12$ months** | **Fundraising / Action Window** | Kick off fundraising, accelerate revenue initiatives, or curb non-essential burn. |
| **$< 6$ months** | **Red Alert Zone** | Immediate burn compression; cut contractor spend; pivot to cash-generative pilots. |

---

## 3. Paul Graham's "Default Alive" vs "Default Dead"

A startup is **Default Alive** if, assuming current revenue growth rate and expenses hold, it reaches profitability before running out of money without needing external funding.

### The Algorithm:
1. Let $C_0$ be current cash, $R_0$ current monthly revenue, $E_0$ current monthly expenses.
2. Let $g$ be monthly revenue growth rate ($R_t = R_0 \times (1 + g)^t$).
3. At month $t$, $\text{Net Cashflow}_t = R_t - E_t$.
4. **Default Alive**: If cumulative cash $C_t = C_0 + \sum_{i=1}^t (R_i - E_i) > 0$ for all $t$ until $R_t \ge E_t$.
5. **Default Dead**: If $C_t \le 0$ at any point before reaching break-even.

---

## 4. Working Capital & Cash Conversion Cycle

- **Annual Upfront Discounting**: Collecting 12 months upfront at a 15–20% discount significantly increases immediate cash balance and extends runway.
- **Payment Gateway Lag**: Factor in Stripe/merchant payout rolling reserves and payout delays (typically T+2 to T+7 business days).
- **Accounts Receivable Collections**: For enterprise invoices, assume net 30 or net 60 day payment terms, not immediate cash receipt.
