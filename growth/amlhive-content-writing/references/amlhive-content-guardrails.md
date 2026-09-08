# AMLHive content guardrails — repo source map, sourced facts, verification

## Repo source-of-truth map (amlhive1, /home/habib/code/amlhive1)

| File | What it holds |
|---|---|
| `AGENTS.md` → "Public Marketing And Implementation-Service Guardrails" | 14-day trial, tagline, C146 services copy rules |
| `docs/branding.md` | Brand identity, positioning, "We are / We are not" claim boundaries |
| `docs/outreach/brand_voice.md` | Personality, messaging pillars, words we use/avoid, AUSTRAC accuracy rules, LinkedIn rules |
| `docs/pluto_agent_instructions.md` | Canonical operating contract (controlled AMLHive facts) — the repo file is source of truth; the `pluto-amlhive-operating-contract` skill is a synced mirror, do not edit the skill directly |
| `frontend/app/Compliance/*/content.ts` | Live published guide FAQ content — sourced regulatory facts safe to reuse (each carries a LAST_UPDATED date, e.g. `austrac-tranche-2-guide/content.ts` = 2026-08-01) |
| `openspec/changes/146-productised-implementation-services/design.md` | C146 canonical public/website copy (implementation services wording) |

## Sourced facts reused (verified against live repo content, Aug 2026)

- Tranche 2: reforms in force 31 March 2026; hard compliance deadline 1 July 2026 (passed).
- Scale: ~35,000 new reporting entities overall; ~15,000 real estate agencies; 18,000 legal practices.
- AUSTRAC Program Starter Kits: a global first; aimed at small businesses with 15 or fewer personnel.
- SMR: obligation under **s.41** — both limbs (designated service to a customer AND a suspicion on reasonable grounds). Due within 24 hours of a terrorism-financing suspicion, within 3 business days for other suspicions; clock runs from suspicion-formed; lodged via AUSTRAC Online; business-day counts vary with state public holidays.
- CDD records: generally kept at least 7 years from end of business relationship or completion of an occasional transaction.
- Source of funds ≠ source of wealth: SoF = origin of the particular funds in a transaction; SoW = origin of the person's entire wealth.
- PEP: foreign PEP = enhanced CDD **mandatory**; domestic / international-organisation PEP = **risk-based**; never an automatic refusal.
- Sanctions match = prohibition on dealing + obligation to freeze + mandatory report to the Australian Sanctions Office and the AFP (DFAT real-estate guidance note, published 23 March 2026).
- Enrolment: AUSTRAC transition enrolment date 29 July 2026 for businesses starting designated services 1 July 2026; general rule is within 28 days of starting a designated service.
- Tipping off: **s.123** of the AML/CTF Act — reformed offence in force from **31 March 2025**; test is whether a disclosure "would or could reasonably be expected to prejudice an investigation" of a Commonwealth/State/Territory offence.
- AML/CTF Act cited by compilation number (as of Sept 2026: C2026C00274, current as at 1 July 2026). See `references/austrac-source-verification.md` for the full playbook.
- Status quo intel: most newly captured practices run AML/CTF on Word templates and spreadsheets.
- Profession response: compliance guides published by Dentons, Gilbert + Tobin, Norton Rose Fulbright, and Crowe.

**All regulatory facts must be re-verified against AUSTRAC / current repo content before publication.** Dates and deadlines go stale; repo `content.ts` files carry LAST_UPDATED markers.

## Verification sweep (run after drafting)

```bash
# From the draft file:
grep -in "two-week\|two week\|30-day\|30 day" FILE                     # expect nothing
grep -in "seamless\|robust\|end-to-end\|leverage\|AI-powered\|statutory officer\|outsourced\|certifier\|legal adviser" FILE  # expect nothing
grep -c "—" FILE                                                      # expect 0 (no em dashes)
awk 'BEGIN{fm=0} /^---$/{fm++; next} fm>=2{print}' FILE | wc -w        # body word count, excluding YAML frontmatter
```

## Draft conventions (TASK-040 example, 2026-08-08)

- YAML frontmatter: `title`, `description` (120–160 chars), `date`, `slug`, `author: AMLHive`.
- Tagline usage: "AMLHive is **Your Virtual Compliance Officer**: ..." followed by the responsibility-boundary sentence ("The reporting entity remains responsible for its decisions and lodgements...").
- Closing disclaimer as italic line: general information only, not legal advice; check AUSTRAC's current guidance and consult a professional adviser.
- Article targets: 1200–1500 words; answer-first (H1 + direct-answer lede); question-phrased H2s; obligation lists; practical steps; consequences; one CTA.
- Drafts land in `docs/content-drafts/TASK-<NNN>-<slug>.md` (create the directory if missing).
