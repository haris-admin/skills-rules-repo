# Alibaba Cloud International — Account Types & Verification for Australian Entities

Research conducted 2026-08-09 (all URLs live-verified; docs restructured — old `/help/en/account/real-name-verification*` and `/help/en/account/user-guide/*` URLs return HTTP 200 but are 404 shells; check HTML for `notfound:"true"`).

## Canonical doc URLs (current)

| Topic | URL |
|---|---|
| What is an Alibaba Cloud account (individual vs enterprise definitions) | https://www.alibabacloud.com/help/en/account/what-is-an-alibaba-cloud-account |
| Identity verification overview (comparison table, limits) | https://www.alibabacloud.com/help/en/account/account-verification-overview |
| Individual verification guide | https://www.alibabacloud.com/help/en/account/verify-your-identity-individual-account/ |
| Enterprise verification guide | https://www.alibabacloud.com/help/en/account/verify-your-identity-enterprise-account/ |
| Basic account info / card binding / BRN-TIN | https://www.alibabacloud.com/help/en/account/manage-basic-account-information |
| Payment methods (contracting party tables) | https://www.alibabacloud.com/help/en/user-center/instruction-of-payment-management/ |
| Model Studio overview (regions, free quota, billing) | https://www.alibabacloud.com/help/en/model-studio/what-is-model-studio |
| Model Studio free quota for new users | https://www.alibabacloud.com/help/en/model-studio/new-free-quota |
| Free tier (70M tokens; T&C with eligibility rules) | https://www.alibabacloud.com/free |
| Startup program (AI Catalyst) | https://www.alibabacloud.com/en/startup/ai |
| Startup program T&C | https://www.alibabacloud.com/startup/terms-and-conditions |
| Registration form (account type selector) | https://account.alibabacloud.com/register/intl_register.htm |
| Identity verification console | https://account-intl.console.aliyun.com/#/intlAuth |

## 1. Can a sole trader / Proprietary ABN sign up?
- **Yes as an INDIVIDUAL account.** Registration asks to pick "Enterprise Account" or "Individual Account"; both proceed with email+password only (no ABN/ACN collected at signup — verified live on the form).
- Individual = "solo developers, students, startup teams, personal projects"; Enterprise = "any company or organization" (what-is-an-account doc).
- **Enterprise verification with a sole-trader ABN is LIKELY but UNVERIFIED in official docs.** Enterprise requires "a valid business certificate issued by local government" matching the account's Country/Region. For new companies Alibaba accepts government-registry screenshots (ACRA/BizFile cited as example; AU equivalent would be ASIC/ABR). Pty Ltd is the safer enterprise submission.
- **Identity verification is OPTIONAL on the international site** — required only for: Chinese-mainland deployments/acceleration, online contracts, credit limits, ACPN membership, binding a phone with a different country code. Model Studio (Singapore) works without it.

## 2. Individual vs Enterprise verification (Australia)
| Aspect | Individual | Enterprise |
|---|---|---|
| Documents | **Passport OR Driver's Licence ONLY** (no national ID cards, no residence permits, no alternatives) | Business registration document (front+back photos), company name, registration number, state/province, city, address |
| ID must be issued by | the account's registered Country/Region (AU account → AU passport/licence; a Chinese passport cannot verify an AU account) | same country as account's Country/Region |
| Review | ~3 business days, manual, result by email | ~3 business days, manual, result by email |
| Lock-in | Type locked to Individual; cannot change | Type locked to Enterprise; individual accounts can upgrade to enterprise but never revert |
| Extra rights | mainland-China purchases only | + online contracts, credit limits, ACPN, cross-country phone binding, Resource Management |

- Individual upload specs: JPG/JPEG/PNG/PDF, ≤5 MB, doc ≥40% of image, all corners visible, no screenshots/photocopies; name + ID number must match EXACTLY (punctuation included) or rejected.
- Enterprise phone rule: phone country code must match account country DURING verification; bind a foreign phone only after approval.
- Common enterprise rejection fixes: exact legal-name/address/number match; bank statement ≥1 month with ≥5 transactions; or official government-registry screenshot.

## 3. Free tier / 70M tokens — enterprise verification needed?
- **The "70+ Million Tokens Free" (Model Studio, Qwen text gen) headline does NOT require enterprise verification.** It's the standard free tier.
- **BUT the Enterprise Free Tier is a separate, better track:** "Users who pass our Company Real Name Registration verification process are eligible for Enterprise Free Tier. Those who have already joined our Individual Free Tier are not eligible for the Enterprise Free Tier." (T&C on /free). Signup steps page: "Register as enterprise account and complete Company Real Name Registration Verification for Enterprise Exclusive offers."
- Free tier rules: one-time free tier per product; **only ONE account per user/organization eligible**; multi-account harvesting = disqualification + instance stop; must add credit/debit card even for free tier (**PayPal not supported for Free Tier**).
- Model Studio free quota mechanics (new-free-quota doc): auto-granted on activation, **Singapore region only** (International scope models), valid 30–90 days (90 days for activations since Sep 8, 2026), per-model (e.g. 1M tokens qwen-max) and shared by account + RAM users. No identity verification needed to activate. After exhaustion: incomplete-profile users get `AllocationQuota.FreeTierOnly` and must "complete account information" (profile + payment method) to go pay-as-you-go; "Free Quota Only" switch prevents surprise charges. Regions: Singapore, Virginia, Beijing, HK, Tokyo, Frankfurt. Base URL for AU: `ap-southeast-1` (Singapore).

## 4. Startup program (AWS Activate equivalent)
- **"Alibaba Cloud AI Catalyst Program"** — apply at https://www.alibabacloud.com/en/startup/ai via survey (https://survey.alibabacloud.com/uone/sg/survey/Ki6nZZ5hr), review ~4–5 business days, notified by email.
- Benefits: up to **2B free Model Studio tokens**, up to **$120k cloud credits**, POC coupons, 1:1 AI expert office hours, 12 months Alibaba Cloud Academy.
- Eligibility: **Company, unlisted, founded ≤10 years, accessible website, solid proposal** on Alibaba AI tools; reseller/distributor accounts excluded; approval at Alibaba's full discretion. **Sole-trader ABN likely does NOT qualify — company required.**
- Credits exclude: domain purchase, CDN, Academy, Marketplace, prepaid products/services.
- ⚠️ **Publicity clause (T&C §2):** grants Alibaba license to list applicant's name/website/contact info in a Program directory and marketing materials. Relevant when an entity must stay low-profile.
- T&C campaign period: Apr 1, 2025 – Mar 31, 2026 (program page still live Aug 2026 — verify extension).

## 5. Same person holding individual + enterprise accounts
- **Allowed.** Docs: one phone number can register up to **6 accounts**, "individually verified or enterprise-verified separately"; each account binds ONE identity only.
- Caveats: free-tier benefits apply to only one account per user/organization; **one bank card can be linked to only one account**; verification is permanent per account.

## 6. Australia-specific gotchas
- **Contracting party:** Australia → **Alibaba Cloud (Singapore) Private Limited** (payment doc's registration-address table), billing currency **USD**.
- **Payment methods (Singapore contracting party):** Visa, Mastercard, Amex, UnionPay, JCB, Discover, Diners Club; PayPal, Apple Pay, Google Pay, Alipay CN. Bank transfer only for enterprise accounts approved for credit control. PayPal NOT usable for free tier.
- Card binding: **1.00 USD pre-authorization** (statement line `ALIBABACLOUD.COM`), 3DS required in some countries, **no prepaid/virtual/gift cards**, each card linked to exactly one account; issuer may charge FX fee on USD.
- Pay-as-you-go billing triggers at ~1,000 USD usage (card) or 8–1,000 USD (wallet).
- Verification email can land in spam/junk — docs explicitly warn; ~3 business days manual review.
- Account type locked after verification (individual can upgrade to enterprise, never back); organization name locked after verification (support ticket + re-verification to change).
- Skip the "Purchase cloud resources in Chinese mainland" option unless needed — it triggers a separate compliance review.
- BRN/TIN for AU: fill on Basic Information page; universal personal tax number `EI00000000010` is a fallback when TIN validation fails.

## Technique: navigating the Alibaba docs site
- Server-rendered pages (curl-able, real content): verify-your-identity-* , account-verification-overview, manage-basic-account-information, instruction-of-payment-management, model-studio/* docs, what-is-an-account.
- JS-shell pages (~3KB, need browser): many /help/en/* pages that 404'd post-restructure.
- Marketing pages (/free, /en/startup/ai, product pages): JS apps — extract via browser_console `document.body.innerText`.
- To discover current doc URLs: fetch a live page and grep `href="/help/en/...` links (e.g. the account docs index at https://www.alibabacloud.com/help/en/account/ lists the whole tree).
- Strip-tags parse script pattern: remove `<script>/<style>`, strip tags, unescape entities, collapse whitespace.
