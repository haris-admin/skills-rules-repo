# Andreessen Horowitz (a16z) 16 Startup Metrics Guide

The canonical 16 startup metrics defined by Andreessen Horowitz (Jeff Jordan, Anu Hariharan, Frank Chen, Preethi Kasireddy) for evaluating growth, efficiency, and venture viability.

---

## 1. Business & Financial Metrics

1. **Bookings vs. Revenue**:
   - **Bookings**: Contract value committed by a customer to spend with the company (e.g., a signed 12-month $12,000 contract).
   - **Revenue**: GAAP recognized value delivered over time as the service is rendered ($1,000/month).
   - *Danger*: Never conflate bookings with revenue.

2. **Recurring Revenue (ARR & MRR)**:
   - **ARR**: Annual Recurring Revenue (excludes one-off fees, setup charges, or non-recurring professional services).
   - **MRR**: Monthly Recurring Revenue ($ARR / 12$).
   - *Formula*: $MRR = \text{Beginning MRR} + \text{New MRR} + \text{Expansion MRR} - \text{Contraction MRR} - \text{Churn MRR}$.

3. **Gross Profit & Gross Margin**:
   - **Gross Profit**: Revenue minus Cost of Goods Sold (COGS: hosting, API query fees, third-party data licenses, customer support directly delivering service).
   - **Gross Margin**: $\frac{\text{Gross Profit}}{\text{Revenue}} \times 100\%$. (Top-tier SaaS benchmarks: >75-80%).

4. **Total Contract Value (TCV) & Annual Contract Value (ACV)**:
   - **TCV**: Total value across multi-year commitments including service fees.
   - **ACV**: Value of the contract annualized over a 12-month period.

5. **Customer Lifetime Value (LTV)**:
   - Present value of net profit generated from a customer over their entire relationship.
   - *Formula*: $LTV = \frac{\text{ARPU} \times \text{Gross Margin \%}}{\text{Churn Rate}}$.

---

## 2. Economics & Unit Efficiency Metrics

6. **Customer Acquisition Cost (CAC)**:
   - All sales and marketing expenses (ad spend, commissions, salaries) incurred to acquire customers in a given period divided by the number of new customers acquired.
   - *Blended CAC*: Total S&M spend / Total new customers (including organic).
   - *Paid CAC*: Direct paid ad spend / Customers acquired directly via paid channels.

7. **LTV / CAC Ratio**:
   - Benchmark for unit economic viability.
   - **Target**: $\ge 3.0\times$. If $< 1.0\times$, the business destroys capital per customer. If $> 5.0\times$, the company may be under-investing in acquisition.

8. **CAC Payback Period**:
   - Number of months required for a customer to generate enough gross profit to pay back their acquisition cost.
   - *Formula*: $\text{Months} = \frac{\text{CAC}}{\text{ARPU} \times \text{Gross Margin \%}}$.
   - **Target**: $< 12$ months for SMB/mid-market, $< 18$ months for enterprise.

9. **Burn Rate & Runway**:
   - **Gross Burn**: Total monthly cash outflows.
   - **Net Burn**: Gross Burn minus monthly cash inflows (true cash depletion).
   - **Runway**: $\frac{\text{Cash Balance}}{\text{Net Monthly Burn}}$ (in months).

---

## 3. Product, Retention & Engagement Metrics

10. **Churn Rates**:
    - **Logo / Customer Churn**: $\frac{\text{Customers lost in period}}{\text{Customers at start of period}}$.
    - **Gross Revenue Churn**: Percentage of recurring dollars lost from cancellations.
    - **Net Revenue Churn (Negative Churn)**: Churn offset by expansion/upsell.

11. **Net Retention Rate (NRR)**:
    - Percentage of recurring revenue retained from existing customers over a period, including expansion.
    - *Formula*: $\frac{\text{Starting MRR} + \text{Expansion} - \text{Contraction} - \text{Churn}}{\text{Starting MRR}} \times 100\%$.
    - **Target**: $> 110\%$ for SMB, $> 130\%$ for enterprise SaaS.

12. **Cohort Analysis**:
    - Tracking retention curves by month/quarter of acquisition over time. Flattening retention curves signify true product-market fit.

13. **Active Users (DAU / MAU) & Engagement Ratio**:
    - Stickiness ratio: $\frac{DAU}{MAU}$. Top daily utilities achieve $> 40-50\%$; compliance/workflow software typically ranges $15-30\%$.

14. **Compound Monthly Growth Rate (CMGR)**:
    - Geometric mean growth rate over $n$ months: $\left(\frac{\text{Latest Month}}{\text{Base Month}}\right)^{\frac{1}{n}} - 1$.
