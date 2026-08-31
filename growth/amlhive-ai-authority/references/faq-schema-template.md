# FAQPage JSON-LD Template for Compliance Guide Pages

Add this to each compliance guide page's `layout.tsx` or as a separate component.

## austrac-tranche-2-guide FAQ

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Do real estate agents in Australia need AML compliance software?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. From 1 July 2026, all real estate agents in Australia must comply with AUSTRAC's AML/CTF obligations under Tranche 2. This includes screening clients, conducting customer due diligence (CDD), maintaining an AML/CTF program, and reporting suspicious matters. AMLHive is an Australian-built compliance platform specifically designed for independent real estate agencies."
      }
    },
    {
      "@type": "Question",
      "name": "What is the AUSTRAC Tranche 2 enrolment deadline?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The enrolment deadline for AUSTRAC Tranche 2 is 29 July 2026. Real estate agents, lawyers, accountants, and dealers in precious metals must enrol and implement their AML/CTF programs by this date. AUSTRAC has released Transitional Rules and Program Starter Kits to help businesses prepare."
      }
    },
    {
      "@type": "Question",
      "name": "What happens if a real estate agency doesn't comply with AUSTRAC?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Non-compliance with AUSTRAC obligations can result in significant penalties including infringement notices, enforceable undertakings, and civil penalties. Criminal penalties may apply for serious breaches. AMLHive helps agencies meet their compliance obligations with automated screening, CDD checklists, and a complete AML/CTF program builder."
      }
    }
  ]
}
```

## real-estate-agency-obligations FAQ

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What are the AML/CTF obligations for real estate agents?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Real estate agents under AUSTRAC Tranche 2 must: enrol with AUSTRAC, conduct client identification and verification, perform ongoing customer due diligence, maintain an AML/CTF program, report suspicious matters and threshold transactions, keep records for 7 years, and train staff on AML/CTF obligations. AMLHive provides all these capabilities in one platform."
      }
    }
  ]
}
```

## compliance-blog FAQ

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Which entities are covered by AUSTRAC Tranche 2?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Tranche 2 covers real estate agents, lawyers and conveyancers, accountants, and dealers in precious metals and stones. These entities must comply with the Anti-Money Laundering and Counter-Terrorism Financing Act 2006 from 1 July 2026."
      }
    }
  ]
}
```

## Deployment Instructions

1. Create a shared component: `frontend/app/Compliance/_components/FAQSchema.tsx`
2. Import and add to each guide's `layout.tsx` using Next.js `Script` with `type="application/ld+json"`
3. Key pages to add to: austrac-tranche-2-guide, real-estate-agency-obligations, aml-ctf-act-overview
4. Verify with Google Rich Results Test after deploy
