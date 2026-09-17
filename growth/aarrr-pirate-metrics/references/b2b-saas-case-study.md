# B2B SaaS AARRR Pirate Metrics Case Study

Practical application of the AARRR Pirate Metrics framework for vertical B2B SaaS products (such as compliance platforms like AMLHive and workflow systems like Simplifii-OS).

---

## 1. Funnel Architecture for B2B Compliance SaaS (AML Hive)

```
[Acquisition]  SEO / ASIC Lookup Tool Traffic (5,000 visitors/mo)
     │ 6.0% signup conversion
     ▼
[Activation]   Free Trial / Run First Company Due Diligence Search (300 entities)
     │ 70.0% run search within 24h
     ▼
[Retention]    Weekly AUSTRAC watchlist alerts & ongoing search usage (210 active entities)
     │ 45.0% convert to paid plan
     ▼
[Revenue]      Paid Subscription ($149/mo Starter, $499/mo Pro) (95 paying entities = $18,900 MRR)
     │ 20.0% refer peer firm
     ▼
[Referral]     Accountant / Legal Peer Referral (19 referral signups/mo)
```

---

## 2. Stage-by-Stage Diagnostics & Optimization Levers

### Stage 1: Acquisition Optimization
- **Symptom**: High bounce rate (>70%) on marketing landing pages.
- **Root Cause**: Generic messaging that doesn't target the user's specific industry sector.
- **Fix**: Deploy industry-specific landing pages (e.g. `amlhive.com.au/real-estate/`, `amlhive.com.au/solicitors/`) highlighting AUSTRAC compliance deadlines for that specific cohort.

### Stage 2: Activation Optimization
- **Symptom**: Users sign up but drop off before executing their first PEP or company search.
- **Root Cause**: Friction in initial verification (demanding credit card upfront or requiring full company registration details before demo search).
- **Fix**: Offer 3 instant, un-gated mock verification searches on company names directly in onboarding. Deliver the "Aha!" moment in < 60 seconds.

### Stage 3: Retention Optimization
- **Symptom**: Entities run searches once during initial client intake and never log in again.
- **Root Cause**: Lack of ongoing triggers.
- **Fix**: Introduce automated Ongoing Customer Due Diligence (OCDD) and batch ASIC status change alerts sent directly to email/Slack.

### Stage 4: Revenue Optimization
- **Symptom**: Low upgrade rate from trial to paid tier.
- **Root Cause**: Pricing cliff (jump from free to expensive tier too steep).
- **Fix**: Introduce flexible search credit bundles alongside unlimited subscription plans to capture low-volume reporting entities.

### Stage 5: Referral Optimization
- **Symptom**: Zero organic word-of-mouth growth.
- **Root Cause**: Compliance is perceived as sensitive/private; firms don't spontaneously share tools.
- **Fix**: Provide "AUSTRAC Compliance Audit Ready" export packs co-branded with AMLHive, creating visible credibility when shared with auditors and regulators.
