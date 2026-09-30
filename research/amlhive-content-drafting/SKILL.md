---
name: amlhive-content-drafting
description: Use when drafting AMLHive blog posts or compliance guides.
---

# AMLHive Content Drafting

## Trigger
Use when asked to write, draft, refresh, or review AMLHive (amlhive.com.au) blog posts, compliance guides, marketing copy, or content drafts (e.g. tasks named `TASK-0xx-…` landing in `docs/content-drafts/`). Also load when a task mentions Tranche 2, AUSTRAC CDD, eKYC, or any AMLHive public-facing claim.

## Step 0 — check the live inventory before proposing a topic
Never shortlist, propose or draft an article from memory, from an ideas file, or from a cron brief —
pull the **live** article set first:

```bash
curl -s https://amlhive.com.au/sitemap.xml | grep -o '<loc>[^<]*' | grep compliance-blog
```

Then fetch each URL's own `<title>` and the sitemap `<lastmod>` for the real headline and freshness.
The posts sit under `/Compliance/compliance-blog/…` — a path filter for `/blog`, `/insights` or
`/resources` matches nothing and makes a full blog look empty.

- **A sibling lane can publish a topic between sessions, so a day-old inventory is not current.**
  A near-identical piece (same subject, same hook) may already be live; publishing the draft anyway
  splits one query across two URLs. If the topic is taken, re-scope the draft to the part the live
  article does not cover and say so explicitly instead of presenting it as new.
- **Read the inventory as a coverage map, not a list.** Group the live set by theme and separate
  event-led pieces ("<deadline> has passed", "the regulator is knocking") from standing
  **definitional** pieces ("what is X"). Event-led content wins timeliness; definitional pages are
  what search and AI answers cite. A theme with event coverage but no definitional page — or a
  deadline the regulator has moved with no page explaining it — is the gap worth writing.
- **Age flags a page for review, it does not reserve a slot.** An entry whose date is weeks old is a
  refresh candidate (or a staleness risk when it carries a superseded date), not automatically the
  next publication.

## Canonical sources — read BEFORE drafting
AMLHive content governance lives in the repo, not the Hermes skill library. Read in order:
1. `AGENTS.md` → section **"Public Marketing And Implementation-Service Guardrails"** — the 14-day trial rule, tagline boundaries, and C146 services rules.
2. `docs/outreach/brand_voice.md` — locked taglines, messaging pillars, words use/avoid, AUSTRAC-accuracy rules (wins on drift).
3. `.agents/skills/amlhive-blogpost/SKILL.md` — the full blog workflow (topic → claim register → bundle → validation → CMS handoff).
4. `.agents/skills/amlhive-content-research/SKILL.md` + `references/validation-gates.md` + `references/amlhive-voice.md`.
5. `pluto-content-firewall` skill — applies to Haris's PERSONAL channels only. AMLHive copy is Stream 2: AMLHive itself may be named freely, but never reference Haris personally and never mention his other ventures inside AMLHive copy.

## Mandatory public-copy guardrails (non-negotiable)
- Trial offer: **"14-day free trial"** ONLY. Never "two-week", "30-day", or any variant.
- Tagline **"Your Virtual Compliance Officer"** may be used verbatim. Never imply AMLHive is a statutory officer, legal adviser, compliance certifier, or outsourced managed-compliance provider. State that the customer retains AML/CTF decisions and legal responsibility.
- C146 implementation services (Go-Live & Adoption, Secure Data Migration & Configuration, Integration Discovery and Delivery, Enterprise Rollout): **"Contact for pricing"**, remote delivery OK where suitable, NO delivery dates / SLAs / open-ended commitments.
- **One CTA max** + a general-information (not legal advice) disclaimer at the end.
- No AUSTRAC-approval claims; no automatic report-lodgement claims (SMRs/TTRs are lodged by the reporting entity via AUSTRAC Online).
- Language: Australian spelling; **SMR** not SAR, **TTR** not CTR; "Tranche 2" not "the changes"; business-day deadlines need the state-public-holiday caveat.
- Regulatory precision (full table + fetch playbook: `../../growth/amlhive-content-writing/references/austrac-source-verification.md`): **foreign** PEP = enhanced CDD **mandatory**, **domestic / international-organisation** PEP = **risk-based**, never an automatic block; sanctions match = prohibition + freeze + report to the Australian Sanctions Office and AFP; tipping-off (**s.123**, reformed offence in force **31 March 2025**) = disclosure that "would or could reasonably be expected to prejudice an investigation"; SMR obligation (**s.41**) needs a designated-service-to-a-customer nexus, so fraud on the agency's own office funds is not an SMR; source of funds ≠ source of wealth.
- Banned words: seamless, robust, leverage, synergies, AI-powered, enterprise-grade (SMB context).

## Medium-confidence intel convention
Claims from secondary/market reporting (market size, provider user counts, accreditation numbers) get an inline `//VERIFY: source (date) — what to confirm before publish` marker on the same line, PLUS a consolidated list in an HTML comment (`<!-- … -->`) at the bottom. Never invent facts beyond what the task provides; flag rather than fabricate.

- **Two credible sources disagreeing on the same figure means DROP the figure.** Do not pick the likelier one, do not average it, do not present it as a range: omit the number, keep the qualitative point, and log a `//VERIFY` asking for the primary source (the regulator's own penalties/fees page). A wrong compliance number costs credibility with exactly the audience being sold to.
- **Date-anchored obligations must be re-verified at drafting time, never inherited.** Reporting periods and deadlines change shape (a compliance-report period can move from calendar years to financial years), and secondary summaries, stale chamber notes and the repo's own calendar keep carrying the superseded date. Verify on the regulator's own page; when the copy corrects a widely-repeated wrong date, say so explicitly — that correction is the most shareable paragraph in the piece.

## Trending-topic content (regulator-driven hooks)
For "review the latest AML/CTF developments and give me a script or blog post for today and this week":
1. Sweep the last ~4 weeks from the regulator's OWN news, enforcement-actions and penalty pages FIRST, then the sector trade press and law-firm briefings. Trade press carries the operational detail (notice length, response window, who was targeted) that the regulator's own release omits.
2. **Hunt the collision, not the headline.** The strongest hook is two independently-verified events landing in the same window aimed at the same audience (an enforcement wave and a warning about the very same letters arriving). Write the hook as that collision.
3. Lead with the most actionable, self-interested angle available — "how to tell the real notice from the fake one" beats "the regulator is getting tougher" for a compliance audience currently being targeted.
4. Deliver a PAIR off one verified fact base: a short-form script for today (hook 0:00–0:07, three or four beats, one CTA, on-screen text per beat) and a blog for the week carrying the methodology and the `//VERIFY` list the script has no room for.
5. Keep the one-CTA rule inside the pair: the script's CTA and the blog's CTA are the same ask, not two.

## Length and word-count method
- Blog drafts target **1100–1400 words**. Count the visible body (everything before the first `<!--`), stripping markdown symbols. Inline `//VERIFY:` annotations count toward the total — so land around ~1300 to leave headroom (publishable prose without markers comes out shorter).
- If over target, trim in this order: short-answer intro → numbered CDD/checklist items → landscape bullets → CTA paragraph. Re-run the verifier after each batch.

## Verification — run before declaring done
Run `scripts/verify_amlhive_draft.py <path>` (asserts word count + all guardrails; exit 0/1). The complete check-by-check contract — every literal phrase it *requires*, and the regexes that fire on compliant prose — is in `references/verify-gate-contract.md`.

- **It is a BLOG gate, not a general copy gate.** Run it on a short-form video/LinkedIn script and it reports `FAIL word count in range` plus every blog-only presence check, however good the script is. Verify scripts against the guardrail list by hand and state which checks you applied — never pad a script to satisfy a blog gate.
- **Three of the checks are presence checks, not prohibitions:** the body must CONTAIN `14-day free trial`, `contact for pricing`, and `Your Virtual Compliance Officer`. There is no "educational post, so nothing to sell" exemption — the close carries tagline + trial + C146 services + pricing pointer in one sentence.
- **`general information only` is matched as a case-sensitive substring.** Keep it mid-sentence in lowercase ("This is general information only and does not constitute legal advice."); a capitalised or italicised lead-in FAILs it.
- **Trap — the AUSTRAC guard matches its own disclaimer.** `AUSTRAC-approved|approved by AUSTRAC` flags the compliant sentence "not an AUSTRAC-approved or statutory body". Write "…is not approved or endorsed by AUSTRAC": identical meaning, guard passes.
- **Trap — the trial-wording ban fires on unrelated durations.** `two-week|two week|30-day|30 day` (case-insensitive) also catches a genuine regulatory "two-week response window". Express real-world durations as "14 days".
- Do NOT trust a bare boolean: regexes span sentences — a multi-line `file.*SMR.*for you` pattern once flagged the compliant sentence "eKYC does not file reports for you" as a violation. Read any FAIL against the actual sentence before acting.
- **Trim order, with the counter's blind spot first:** long inline `//VERIFY:` notes are counted, but the trailing `<!-- … -->` block is NOT — move verification detail into that block before cutting prose. Then: short-answer intro → numbered checklist items → landscape bullets → CTA. The sources line and disclaimer sit inside the counted body and are a legitimate last lever.

## Pitfalls
- **Verify the live bundle path on `origin/dev` before dispatching a draft — the convention moves.** As of 21 Sep 2026 (human instruction) new CMS-ready bundles go to `assets/YYYY-MM-DD-<slug>/` (article's own meta.json date), NOT `assets/blog-migration/<slug>/`; read `.agents/skills/amlhive-blogpost/SKILL.md` on `origin/dev` rather than trusting a cron brief or an older agent branch, and re-dedupe the chosen topics against dev's shipped articles (a topic can be published while an ideas file still lists it). Writing to a superseded path manufactures the mess the drift-reconciliation exists to clean up.
- **A pre-flight merge conflict BLOCKS the run — do not skip the merge to get the content out.** When `git merge origin/dev` conflicts inside a long-lived agent branch, abort, report BLOCKED, and stop: an unresolved conflict in an application file means the branch is behind the repo's current conventions, so any content written on the un-merged tip inherits them. `git merge --abort` restores a clean tree; verify with `git status --porcelain` plus `git rev-list --left-right --count origin/<branch>...HEAD` before reporting.
- **A repeat block is a lane fault, not a tool fault — separate them and make the escalation actionable.** When the same pre-flight block recurs, the run must still produce new information, or the escalation is worthless. Three probes cost nothing and change the outcome: (1) prove the writer is healthy (`codex login status`, `codex --version`) so the report does not blame Codex for a branch problem; (2) health-check the ALTERNATIVE lanes (`git rev-list --left-right --count origin/dev...HEAD` in each worktree) and report which one is actually mergeable — a lane that reads `0 behind` needs no merge at all, which turns a pending decision into a one-line retarget; (3) re-measure the drift number every run and chart it, because a growing-behind count is the argument for retiring the lane. Keep the A/B/C decision the human's to make; supply the evidence that makes it cheap to answer.
- The patch tool's fuzzy matching can merge two lines when you delete a blank line (saw "suggests:1." instead of "suggests:\n\n1."). Re-read the diff after trims.
- Sweep AMLHive drafts for Haris's other venture names (finai, paylicence, exitlens, tokenpilot, cloudproof, tapease, agentgate, cloudwise, verifylink) and "haris" — they must not appear; the reverse firewall holds even though AMLHive itself is the promoted brand.
- The full repo blog workflow wants OpenSpec plan gates + claim registers for CMS-ready bundles. A plain draft in `docs/content-drafts/` is a lower bar — match the task scope, don't invent a human decision, and never claim publication/deployment.
- **When the ask is NOT a repo task** ("review what's trending and give me a script or post for today and this week"), file the finished pieces in the Alexandria vault at `vault/refined/amlhive-content/`, one file per piece named `<medium>-<yyyy-mm-dd>-<slug>.md` with the `//VERIFY` list at the foot, and land them with a scoped `git add -- vault/refined/amlhive-content` + the mandatory secret scan (see `alexandria-vault-sync`). `docs/content-drafts/` is for work already inside the repo's blog workflow.

## Support files
- `scripts/verify_amlhive_draft.py` — word-count + full guardrail compliance checker.
