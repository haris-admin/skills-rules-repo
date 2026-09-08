# AUSTRAC / legislation source-verification playbook

The concrete "how" behind "re-verify regulatory facts before publication." Applies to any AMLHive
public compliance copy — blog articles, guides, landing pages, newsletter, social. Distilled from
the 2026-09 hardening of the vendor-payment-fraud / overseas-deposits blog pair, where a
first-pass draft deferred the citation check and shipped the pre-2025 tipping-off test plus two
near-duplicate articles.

---

## 1. The fetch reality

- **`legislation.gov.au` is fetchable.** It is the primary source for anything statutory. It
  exposes a compilation number and a "current as at" date — cite both, not "compiled version".
  - `https://www.legislation.gov.au/C2006A00169/latest/text` → AML/CTF Act 2006, current
    compilation (as of Sept 2026: **C2026C00274, current as at 1 July 2026**).
- **The AUSTRAC website times out on automated fetches more often than not.** Don't burn retries.
  Fall back to: (1) a web search with an AUSTRAC-specific query — the result snippets carry
  AUSTRAC's own wording; (2) one reputable secondary summary (a top-tier law firm — MinterEllison,
  Lexology, HWL Ebsworth, Norton Rose, Dentons) to confirm dates and the direction of a reform;
  (3) mark the AUSTRAC page's own "last updated" line **`confirm on publication day`** in the
  claim register and re-check it at publish.
- **`austlii.edu.au` returns 403 to automated fetches.** Use `legislation.gov.au` instead.
- `dfat.gov.au` guidance notes are reachable via search. The real-estate sanctions note was
  **published 23 March 2026**.

A claim whose *substance* is confirmed by legislation.gov.au + AUSTRAC-surfaced wording + a
reputable summary is verified even if the AUSTRAC page's own timestamp is still pending — the
pending item is the page date, not the fact.

## 2. Statutory anchors — exact wording

| Topic | Cite | Exact wording / facts |
|---|---|---|
| SMR obligation | AML/CTF Act **s.41** | Trigger is **both limbs**: the entity "commences to provide, or proposes to provide, or has provided a designated service" **AND** "holds a suspicion on reasonable grounds". Fraud against the agency's *own* office funds (invoice redirection, business email compromise) has no designated-service-to-a-customer nexus — it is a fraud-response matter (bank, ReportCyber, police), **not** an SMR. |
| SMR timing | s.41(2) | **3 business days** from when the suspicion is formed; **24 hours** where it relates to terrorism financing. Clock runs from suspicion-formed, not transaction date. State public holidays shift the business-day count — say so. Lodged by the reporting entity via AUSTRAC Online; never auto-submitted. |
| Tipping off | AML/CTF Act **s.123** | The reformed offence is **in force from 31 March 2025** (most other 2024-Amendment reforms commenced 31 March 2026). Test: a disclosure that **"would or could reasonably be expected to prejudice an investigation"** of a Commonwealth, State or Territory offence. Use that phrase verbatim; name the commencement date. Do not describe it only as "a criminal offence, treat seriously". |
| Threshold transaction reports | AML/CTF Act **s.43** | TTR for physical currency ≥ AUD 10,000. Never "CTR". |
| Real estate = designated service | AUSTRAC "Real estate designated services" + Act compilation | Tranche 2 entities comply from **1 July 2026**. |
| Foreign PEP | AUSTRAC EDD guidance | Enhanced CDD is **mandatory** for a foreign PEP — senior-management approval, source-of-funds + source-of-wealth, enhanced monitoring, as a matter of course. |
| Domestic / international-organisation PEP | AUSTRAC PEP guidance | **Risk-based** — apply EDD where the entity assesses risk as high, and record why. Never merge with foreign PEP into "the risk-based process". A PEP match is never an automatic refusal. |
| Source of funds vs source of wealth | AUSTRAC "Source of funds and source of wealth" | SoF = origin of the **particular funds** in a transaction. SoW = origin of the person's **entire wealth** — how much they'd be expected to have and how they acquired it. A large or higher-risk deposit can need both; keep them labelled separately in the file. |
| Sanctions | DFAT real-estate guidance note | Not risk-based. Prohibition on **dealing** with an asset owned/controlled by a designated person, obligation to **freeze**, and **mandatory report to the Australian Sanctions Office and the AFP**. In practice the agency does not provide the designated service. |
| Record keeping | AUSTRAC "Record keeping overview" | CDD records kept **at least 7 years** from end of the business relationship / date of the last occasional transaction. |
| AML/CTF program structure | repo issue-023 | Do **not** reference "Part A / Part B" — that structure was abolished. |

## 3. Citation conventions

- Cite the Act by **compilation number** (`C2026C00274, current as at 1 July 2026`).
- The article's central framing/thesis ("this got stricter", "this is now required", "this is
  not an SMR") is itself a claim — verify it against a primary or reputable secondary source
  specifically, not by assuming it from the supporting details.
- Analytical / line-drawing claims (e.g. "ordinary office-account invoice fraud is not an SMR
  trigger") need legal sign-off (Shoaib / legal) even when the reasoning is sound — they are not
  AUSTRAC statements in those words.
- Never paper over an unverified specific (a number, a threshold, an exact test) with vaguer
  prose. Either state the correctly-sourced fact, omit the detail and link the primary source, or
  hold the piece.

## 4. No near-duplicate articles

Two pieces on adjacent topics (both about SMR timing, both about source of funds) must not share
verbatim sections — the tipping-off block, the SMR-timing block, and the "Where AMLHive fits /
Your Virtual Compliance Officer" close are the usual offenders. Check the **article body only**
(exclude the Sources list and the standard disclaimer):

```bash
node -e '
const fs=require("fs");
const body=s=>s.split(/\n##\s+Sources/)[0]
  .split("\n").filter(l=>!l.includes("general information only")).join("\n");
const clean=s=>body(s).replace(/https?:\/\/[^\s"\x27<>]+/g," ").toLowerCase().match(/[a-z0-9]+/g)||[];
const runs=(w,n)=>{const set=new Set();for(let i=0;i<=w.length-n;i++)set.add(w.slice(i,i+n).join(" "));return set;};
const a=clean(fs.readFileSync(process.argv[1],"utf8"));
const b=clean(fs.readFileSync(process.argv[2],"utf8"));
const rb=runs(b,14);
console.log([...runs(a,14)].filter(r=>rb.has(r)));
' DRAFT_A.md DRAFT_B.md
```

Empty array = pass. `Your Virtual Compliance Officer` must stay immediately qualified per
`brand_voice.md` — vary the sentence around it, don't drop it.
