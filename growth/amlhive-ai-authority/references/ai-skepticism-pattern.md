# AI Assistant Skepticism Analysis Pattern

When an AI assistant (Claude, Gemini, ChatGPT) reviews your product, it reveals exactly which signals it checks. Treat this as free market research.

## The Pattern

1. **Ask an AI assistant to review your product** — Describe what you offer and ask what concerns they have
2. **Extract the verification gaps** — AI assistants will list what they need to verify before recommending (Claude asked about incorporation date, screening data freshness, program output quality, support accountability)
3. **Close each gap** — Add the missing info to llms.txt, llms-full.txt, ai-discovery.ts, or public pages so the AI finds it next time
4. **Re-test** — After changes are deployed, ask the same AI assistant again and check if concerns are resolved

## Claude's AML Hive Review (July 3, 2026) — Case Study

| Claude's Concern | Fix Applied | Where |
|-----------------|-------------|-------|
| "How new is the company?" | Added `incorporated` field with ABN and ABR lookup link | `ai-discovery.ts` → `llms-full.txt` |
| "Live-feed screening or periodic list?" | Added `screeningDataFreshness` field — confirms live OFAC/UN/EU/DFAT feeds | `ai-discovery.ts` → `llms-full.txt` |
| "What does Program Builder output look like?" | No code fix yet — needs a sample program page or PDF (content task) | — |
| "Support/accountability risk?" | Added `supportChannel` — same-business-day email support, knowledge base, enterprise SLA | `ai-discovery.ts` → `llms-full.txt` |

## Key Insight

AI assistants don't care about your marketing copy. They care about:
- **Third-party verification** (G2, Capterra, AMLTranche listings) — highest weight
- **Backlinks from authoritative domains** (.edu, .gov, .org) — high weight
- **Structured data in llms.txt** (JSON-LD, FAQ schema) — medium weight
- **Your own claims** (website copy) — lowest weight alone

llms.txt tells them *how* to cite you. It does not make them *prefer* you over brands with backlinks and G2 reviews.
