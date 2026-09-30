# verify_amlhive_draft.py — the gate contract

`scripts/verify_amlhive_draft.py <path>` prints one PASS/FAIL per check, then `ALL PASS` (exit 0) or `ISSUES` (exit 1). Run it after EVERY trim batch, not once at the end.

## Why a FAIL is not automatically a defect
The checker is a blunt regex layer. Several checks match a *substring* anywhere in the body, so a compliant sentence can trip the check that exists to ban the non-compliant version of it. Read each FAIL against the actual sentence before editing, and when the sentence is already compliant, **reword it so the guard can see that** — do not weaken the claim.

## Presence checks (the draft must CONTAIN these)
| Check | Literal requirement |
| --- | --- |
| `14-day free trial only` | the string `14-day free trial` |
| `C146 contact-for-pricing` | `contact for pricing` (compared lowercased) |
| `tagline present` | `Your Virtual Compliance Officer` |
| `general-info disclaimer` | `general information only` — **case-sensitive**, keep it mid-sentence lowercase |

A draft that is pure education and sells nothing still fails all four; the close is one sentence combining tagline, trial, the C146 services and the pricing pointer.

## Prohibition checks (the draft must NOT contain these)
| Check | Pattern / trigger |
| --- | --- |
| `no two-week/30-day` | `two-week\|two week\|30-day\|30 day`, case-insensitive — also catches legitimate real-world durations |
| `not AUSTRAC-approved` | `AUSTRAC-approved\|approved by AUSTRAC`, case-insensitive — **also matches the compliant negation** |
| `no statutory-officer/legal-adviser/certifier` | claim-shape patterns |
| `no delivery-date promise` | SLA / date commitments |
| `no auto-lodgement claim` | implies AMLHive files SMRs/TTRs |
| `no banned words` | seamless, robust, leverage, synergies, AI-powered, enterprise-grade |
| `SMR not SAR` / `TTR not CTR` | Australian terminology |
| `no other-venture brands` | reverse firewall — Haris's other ventures must not appear |
| `no Haris personal reference` | AMLHive copy never references him personally |

## Word count
Two figures are printed: **body words (incl //VERIFY)** — the number the 1100–1400 gate uses — and **publishable prose** (the same count minus the inline annotations). The gap tells you how much of your budget is verification notes.

Counted: everything before the first `<!--`, including inline `//VERIFY:` notes, the sources line and the disclaimer.
NOT counted: the trailing `<!-- … -->` block. Put the long verification notes and the resolve-before-publish list in there; move them out of the body before cutting real prose.

## Fixing the two trap FAILs
- `not AUSTRAC-approved` FAIL on a disclaimer → write "AMLHive is not approved or endorsed by AUSTRAC" (or "…is not a statutory body") instead of "not an AUSTRAC-approved body".
- `no two-week/30-day` FAIL on a non-trial duration → write "14 days"; never reword the trial offer to dodge it.
