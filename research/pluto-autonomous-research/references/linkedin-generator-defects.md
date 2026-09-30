# LinkedIn generator defect log (linkedin_ideas_generator.py)

Full history of defects found and fixed in the LinkedIn/blog ideas generator (Phase 8).
Each entry is a rule, not a changelog entry: the defect, the fix, and the assertion that
proves the fix. Load this when modifying `linkedin_ideas_generator.py` or when a curated
set looks mechanical — the SKILL.md holds the condensed rules.

## Rules 1–7, 13–20 (moved out of SKILL.md 2026-09-20 to keep SKILL.md under the 100K limit)

**Generator hardening (Sep 10, 2026 — three defects fixed):**
1. **Hardcoded blog ideas went stale.** The generator emitted the same 3 blog titles daily regardless of signals, and kept proposing "The Agent Security Supply Chain" for a week AFTER it published on harishabib.au. Blog ideas now come from `BLOG_CANDIDATES`, are gated on the day's signal/research corpus, and are skipped when the key exists in `KNOWN_BLOGS`. **Refresh `KNOWN_BLOGS` whenever a post publishes** — the inventory is the gap detector; curl `https://harishabib.au/blog` and grep the `<h1-h3>` titles. A stale inventory silently re-proposes published posts.
2. **Zero signals → template output.** `himalaya` returns nothing in the sandbox, so `get_briefings_from_gmail()` yielded 0 and the generator fell back to "Here's what the data says about..." hooks. New `get_signals_from_files()` reads the newest `gmail-briefing-*.md` / `claude-research-*.md` / `content-ideas-*.md` from `~/.hermes/mempalace-inputs/` as the fallback (42 signals on the first run). Note gmail-briefing files use generic `## Finding` headers — the generic-header filter drops them, so claude-research/content-ideas carry the signal.
3. **Hooks led with nothing.** Hooks now lead with the finding's strongest stat (`extract_headline_stat`), dollar figures are suppressed for non-market findings (an acquisition price is not a breach hook), and research-driven ideas are ordered ahead of theme templates.
4. **Pillar mis-mapping (Sep 11, 2026).** `research_ideas` assigned pillar as fintech-if-regulator-words-else-"AI Agents & Governance", so every Cloud & Infrastructure finding (DTA cloud policy, Broadcom repatriation, sovereign cloud spend, hyperscaler capex) was labelled agent governance — wrong pillar, wrong CTA framing. Fix: resolve pillar by domain, with a cloud branch (`sovereign`/`cloud`/`repatriation`/`finops`/`hyperscaler`/`infrastructure`/`aws`/`azure`) → "Cloud & Resilience Engineering" and a startup branch → "Startup & ESOP". When the day's research topic and the idea pillars disagree, suspect this mapping first.
5. **BLOG_CANDIDATES must cover every tracked research topic.** On the Cloud & Infrastructure day the generator emitted zero cloud blog ideas — it fell through to AML/agent-security candidates — because no cloud candidate existed. Any tracked topic (see the Tracked Topics list) with no matching candidate silently degrades that day's blog ideas. `keywords` gate candidates against the day's research + signal corpus; a candidate with no keyword hits is dropped entirely, so keyword lists must include the vocabulary the RSS synthesis actually uses. **Startup & VC was the last gap (closed Sep 14 2026)** — a startup/VC day produced agent-identity and egress-control blog ideas with `signal matches: 0`. Three candidates were added (CGT exposure draft, VC barbell/missing middle, public co-investment accountability) and scored 8–11 matches on the first run. When you add candidates, mirror the vocabulary the research JSON actually uses ("exposure draft", "deal count", "sub-$5m", "co-investment", "spinout"), not press-release vocabulary.

13. **Quota-padding with zero-hit candidates is worse than returning two ideas (Sep 14 2026).** The blog-idea block padded to three picks with any unfresh candidate regardless of pillar, which is how an unrelated-pillar idea reaches the page. Pad only with candidates whose pillar is already in play that day (`day_pillars(topic, findings)` — topic-derived pillar plus every pillar implied by the findings' `portfolio_hit`), and accept two relevant ideas. Never fill the third slot with a different domain.

14. **Hook stat clauses need a standalone-clause gate (Sep 14 2026).** `extract_headline_stat` returns the clause around a number, and `hook = f"{stat}: {short}"` prefixed fragments pulled from mid-sentence: "offsets rise by up to ~ 50%: Treasury drops exposure draft…", "less than two years after taking $32m … to 'continue to base: Harrison.ai…", "collecting data in 2020 and a 44% drop…". Gate the prefix: the clause must (a) contain a digit, (b) start with an uppercase letter or a digit/currency symbol — a lowercase start means the sentence was cut in half, (c) have balanced quotation marks, (d) carry a number the short title does not already state, and (e) not share >40% of its non-stopword tokens with the title. Title-only is the better hook when the gate rejects the stat; all six hooks were complete clauses after the fix.

15. **`_short_title` must balance parentheses too, not just clause boundaries (Sep 14 2026).** Slicing at a 100-char limit and stripping trailing function words left hooks ending "…Firmus ($14bn" and a one-word colon tail "…deep tech: Firmus". Route every trimmed fragment through a `_balance_fragment()` helper: drop an unterminated trailing parenthetical, drop a leading dangling ")", and cut a ≤2-word tail hanging off a colon.

16. **Pillar mapping must consult `portfolio_hit` first AND scope the ecosystem exception (Sep 14 2026).** Two failure modes on one day: the CGT exposure draft (ExitLens AU → Startup & ESOP) was pillared fintech because "cgt" was a fintech keyword, and the NSW $150m university co-investment fund (AML Hive) was pillared fintech and given an AML CTA because `portfolio_hit` was treated as the whole answer. Resolution order that works: (1) AI- and cloud-specific products (FinAI File AU, CloudProof AU) and ExitLens AU win outright, (2) a public-ecosystem/innovation-policy finding (`co-investment|spinout|commercialis*|innovation fund|innovation blueprint|universit(y|ies)`) with no regulator vocabulary is Startup & ESOP regardless of a compliance-product `portfolio_hit`, (3) regulator terms, (4) cloud terms, (5) startup/VC terms, (6) remaining `portfolio_hit`. Also use word-boundary regexes for regulator keywords — substring matching made "asic" hit "basic".

17. **A re-run of the generator must not destroy the hand-written curation (Sep 14 2026).** Phase 8 appends a `# ✅ Curated by Pluto` section to the day's file, and `main()` rewrote the whole file — so any same-day re-run (verification, a fixed defect, a manual kick) silently discarded the curated set. Before writing, read the existing file and re-append everything from the curated marker to EOF. Any cron whose output is human-edited after generation needs this guard.
18. **The blog-rotation window must be SHORTER than the research topic cycle (Sep 16 2026).** `recently_proposed_blog_titles(days=5)` suppressed every candidate proposed within 5 days, but the tracked-topic cycle is also 5 days (`date % 5`) — so a Cloud day's cloud candidates were always suppressed on its own next appearance and the engine silently answered with AI-governance ideas, every cycle. Rotation defers an unwritten idea for a few days; it must never retire one. Keep the window at 4 days, and retire a candidate by adding its KEY to `KNOWN_BLOGS`. **A candidate whose gap was published under a DIFFERENT title must also be retired** (the sovereign/DTA candidate became "Australia's Cloud-First Policy Is an Architecture Decision…"; the VC-barbell candidate became "Record Venture Dollars, Record Concentration") — otherwise the generator re-proposes a filled gap forever. The only reliable refresh is diffing the live index against `KNOWN_BLOGS`: `curl -sL https://harishabib.au/blog | grep -oP '<h[123][^>]*>.*?</h[123]>'` (4 posts were missing on Sep 16, 36 live vs 32 known). **HTML-unescape the scraped titles before diffing** — the index serves apostrophes as `&#39;`, which produced six phantom 'missing' posts on Sep 19 2026 (real answer: 36 live, 0 missing). Run `html.unescape()` on both sides and normalise to alphanumerics before concluding the inventory is stale.
19. **Order blog picks by the day's topic pillar, not alphabetically (Sep 16 2026).** With equal keyword-match counts the tiebreak was the candidate key, so a Cloud day's cloud candidate landed third behind two agent-governance candidates that merely keyword-matched the day's corpus. Sort by `(-hits, 0 if pillar == topic_pillar else 1, key)`; and when the day's dominant signal has no candidate at all, add one (data-centre energy/grid had none, and both of the day's top-impact findings sat there).
20. **The angle field is prose and must be cut at a boundary, and a stat-prefixed hook must not double-splice (Sep 18 2026).** Two defects shipped together on an Agentic AI & Security day: (a) `"angle": (f.get("for_haris") or content)[:420]` ended every angle mid-word ("…deputy director Franc", "only 11% of those applica", "training utilit", "The Cloud") — route angles through a `_trim_angle()` helper that takes the last sentence end inside the limit, else a clause boundary, else a word boundary plus an ellipsis; (b) `_hook_stat_ok()` allowed a stat prefix on a title that already contained a colon, producing "Cohesity reports only 2% …: Australia has no AI early-warning system: signals chief warns…" — reject the stat whenever the short title itself contains ": " (the title already supplies the topic:detail structure, so the hook becomes "A: B: C"). **Verification for any hook/angle change: assert every angle ends in terminal punctuation and no hook contains more than one colon** — both are one-liners over the written file and caught both defects. **A clause-boundary angle cut must be CLOSED with a full stop, not left hanging on its separator (Sep 19 2026):** `_trim_angle` cut at the last `", "` / `"; "` inside the window and returned the separator, so three of six angles ended "…at the 2007 introduction);", "…a failed promise of 15,000 jobs,", "…became unicorns this year;". Prefer a sentence end anywhere above ~35% of the limit, then clause boundaries closed with `"."`, and accept the `…` fallback as an explicit truncation marker. Two further `_hook_stat_ok` gates from the same run: reject a stat clause containing a spaced dash (`\s[-–—]\s`) — those are parenthetical splices lifted mid-sentence ("17% write-down - at the August re-mark: …") — and reject a stat clause opening with a bare four-digit year ("2016 - is in market for $400m for Fund IV: …"). Assert both over the written file: `angles = [l[11:] for l in txt.split('\n') if l.startswith('**Angle:** ')]; assert all(a.rstrip().endswith(('.','!','?','…')) for a in angles); assert all(h.count(':') <= 1 for h in hooks)`.

6. **Truncated hooks.** Titling a hook by slicing the title at 100 chars yields fragments ("…sovereign-first procurement rewrites"). Prefer a complete clause at an em-dash/en-dash/semicolon boundary; only slice at a word boundary when no clause fits.
7. **Bare-number hooks (Sep 12, 2026).** Leading a hook with the raw first stat emits meaningless fragments, worse when the stat came from a parenthetical unit definition: "30%: a 7-month obligation/remedy gap" (source text: "$50m per contravention (or 3x benefit / 30% adjusted turnover)") and "10%: ASIC digital-asset licensing cliff". `extract_headline_stat` must return the *clause* around the number, cut at the nearest clause boundary on BOTH sides (`. ` `; ` `, ` ` (` `: ` ` — `), with leading stopwords and unterminated parentheticals stripped, and must SKIP numbers inside parentheses. Result: "penalties up to 10% of annual turnover".
8. **Pillar from `portfolio_hit`, not from regulator keywords (Sep 12, 2026).** The pillar resolver tested `austrac|asic|apra|psp|cgt|afsl` first, so "AUSTRAC names AI a cross-cutting money-laundering accelerant" (portfolio_hit = FinAI File AU) was pillared *Australian Fintech Regulation* — the AI-governance pillar got zero ideas on a fintech-topic day. `portfolio_hit` already encodes the true domain: FinAI File AU → AI Agents & Governance, CloudProof AU → Cloud & Resilience Engineering; check those BEFORE the regulator-keyword branch.
9. **Pillar diversity before truncation (Sep 12, 2026).** One research topic per day means every finding shares a pillar, so a naive top-N slice returns an all-one-pillar set and cross-pillar signals never surface. Order research ideas one-per-pillar first, then fill the remainder, and keep the cap at 6 (was 4, which silently dropped the AI-governance and enforcement-wave findings entirely).
10. **Clause boundaries must not be taken from inside parentheses (Sep 13, 2026).** `_hook_clause` picked `max()` of all candidate boundaries, and a `", "` sitting inside a parenthetical wins that contest — producing hooks that open with a dangling fragment ("264 in Australia) found 84% of Australian enterprises…"). Filter boundary positions through `_inside_parens()` and keep the opening `"("` itself as a valid boundary so the parenthetical stays intact; also strip a leading `")"` when the segment has more closes than opens. Related, same function: a hard 110-char slice ends hooks mid-phrase ("…governance gap that no", "…OWASP's agentic") — cut at a real clause boundary when one exists in the first 110 chars, and otherwise drop trailing function words (`TRAILING_WORDS`) before returning. Title shortening has the same failure mode: use a `_short_title()` helper, not `title[:100].rsplit(' ', 1)`.
11. **Currency-unit patterns must be case-insensitive and token-bounded (Sep 13, 2026).** `r'\$\d+…\s?(?:bn|b|m|k)?'` matched only the digits of `$100M`, so the tail rebuilt it as `$100 M Series B`. Add `(?![A-Za-z])` and `re.IGNORECASE` so the suffix joins the number.
12. **Blog ideas repeat verbatim on consecutive days unless rotated (Sep 13, 2026).** Candidate scoring only consulted `KNOWN_BLOGS` (published posts), so the same two AML/fintech candidates were proposed on Sep 12 and Sep 13. Keep a `recently_proposed_blog_titles(days=5)` blob of prior `linkedin-ideas_*.md` files and skip any candidate whose title appears there; when the day's topic has no matching candidate the engine silently falls through to another pillar's candidates, so add candidates per tracked topic (five agentic-security candidates were needed for an Agentic AI day).

21. **A trimmed hook must not ship an unterminated quote (Sep 20 2026).** `_balance_fragment()` balanced parentheses and colon-tails but not quotation marks, so `_short_title`'s 100-char slice dropped the closing quote and shipped `…OpenAI failed to report a 'serious incident`. CLOSE the phrase (append the missing quote) rather than cutting it — cutting leaves `…failed to report a`. Do not count possessives as quotes: only an apostrophe at a word start (`(?:^|\s)'` followed by a letter) opens a phrase. Assert per hook, per quote character: `pos=[m.end()-1 for m in re.finditer(r"(?:^|\s)"+re.escape(q)+r"(?=[A-Za-z0-9])",h)]; assert not (pos and q not in h[pos[-1]+1:])`.

22. **A stat clause must not end on a dangling auxiliary or an unqualified number (Sep 20 2026).** `_hook_clause` stopped wherever the source's next boundary fell, producing `87% of organisations encourage AI agent use but only 47% have` — a fragment that reads as a broken feed. Route EVERY clause through a `_strip_dangling_tail()` helper before returning: pop trailing auxiliaries/conjunctions/prepositions (a `DANGLE_TAIL` superset of `TRAILING_WORDS` — have/has/do/will/only/just/while/…), then strip a trailing quantified number with no subject (`…but only 47%`) and re-pop what that exposes; if nothing meaningful survives, return `""` and let the caller fall back to the title — a clean title beats a fragment. Title side, same family: a word-boundary slice in `_short_title` still ended on a subordinate clause opener (`…and a 'kill switch' while Washington`), so cut a trailing `while|as|and|but|because|if|since|when|after|before|that|which|who` plus 1–3 words — but ONLY in the word-boundary fallback path. In the clause-boundary path `…then shelved after media pushback` is a good hook and a blanket rule would damage it.

23. **The blog pillar gate must cover MATCHED candidates, not just the padding slot (Sep 20 2026).** Padding was gated on `day_pillars()`, the scored path was not — so one cross-domain keyword lifts an off-day candidate into the top three: on an AI Regulation day the FIIG penalty (Cloud & Resilience) matched on `asic` and took a slot ahead of the day's own AI-governance candidates. Filter `scored` by `day_pillars(topic, findings)` before sorting, keep the padding gate as-is, and when the day's dominant gap has NO candidate, add one (`agent-incident-register` — EU Article 50 / incident reporting — had none; it scored 6 keyword matches on its first run and led the set). Every recurring gap needs at least one candidate.

24. **One CTA per PILLAR means one CTA per DAY on a single-topic run — and a topic whose candidate list is thin degrades its own blog block (Sep 22 2026).** Two defects shipped together on a FinTech Regulation day. (a) `CTA_BY_PILLAR[pillar]` was the whole CTA strategy, and every research finding on a single-topic day resolves to the same pillar — so all six posts closed with the identical line ("If you're the reporting entity, the clock is already running…"). Add a `CTA_BY_PORTFOLIO` map (the portfolio is what the post actually sells), a public-facing `CTA_ALTERNATES` list, and a day-level `_pick_cta(pillar, portfolio, seen)` that resolves portfolio → pillar → alternate → generic while accumulating a `seen` list, so no CTA repeats verbatim. Two findings can share a portfolio (PayLicence AU appeared twice), which is exactly what the alternates tier is for. Do NOT let the third tier name an internal product ("Building this into AML Hive — what would it look like in your stack?" reads as internal shorthand on a public post). Also normalise `portfolio_hit` in the list shape, not just the string shape, before the lookup — the briefing improver's podcast path emits list-of-dicts. (b) `BLOG_CANDIDATES` held only three `Australian Fintech Regulation` entries, and on the day whose OWN topic pillar was fintech, the rotation gate and keyword gate suppressed two of them — leaving one blog idea and forcing hand-written padding. FinTech Regulation is a 5-day-cycle topic that recurs roughly weekly, so it needs at least five candidates covering DISTINCT published gaps. Added `spf-multiparty-liability` (Scams Prevention Framework / multi-party liability — Tapease) and `digital-asset-licence-cliff` (ASIC transitional-relief expiry — TokenPilot AU); the block went 1 → 3 ideas at 8 / 6 / 4 keyword hits. Check the candidate count for the day's OWN pillar whenever the blog block comes back short — the padding gate cannot rescue a topic with no candidates.

25. **Near-duplicate CTAs survive exact-string dedupe (Sep 23 2026).** `_pick_cta` rejected a candidate only when `candidate not in seen`, so two *different* table entries that say the same thing both shipped: `CTA_BY_PILLAR['Australian Fintech Regulation']` ("If you're the reporting entity, the clock is already running — where does your evidence trail live today?") and `CTA_BY_PORTFOLIO['AML Hive']` ("If you run a reporting entity: when did you last test your evidence trail…?") closed posts 3 and 4 with the same sentence on an Agentic AI day where one finding pillared fintech (via its AML Hive `portfolio_hit` fallback) and another carried AML Hive outright. Add `_cta_fingerprint()` (lowercased words >3 chars minus `_CTA_STOPWORDS`) and `_cta_too_similar(candidate, seen, threshold=0.4)` comparing overlap over `min(len)` — order-insensitive, so reworded variants are caught — then fall through to the next tier. Reworded the AML Hive portfolio CTA to name the product outcome instead ("When AUSTRAC asks, the question is what your file shows and when it was created"). Verified: 6/6 CTAs distinct, 0 verbatim duplicates, max pairwise similarity 0.40 → 0.17. Note the pattern behind it — a pillar CTA and a portfolio CTA written for the *same* domain will collide unless one of them is product-specific; the portfolio line is the one that should name the product.

26. **A hook stat must belong to the SAME SUBJECT as the finding, and a slice must not strand scaffolding or land mid-list (Sep 24 2026).** Two defects shipped together on a Startup & VC day. (a) `extract_headline_stat` quoted a number that was only the TAIL of a range: `~86–91%` matched `91%`, and the clause built around it — "September RBA hike is ~86- 91% priced by the ASX rate tracker and rateprobability" — became the hook for an **R&D tax-offset** finding, because it came from an unrelated macro sentence inside the same content blob. `_hook_stat_ok` waved it through (standalone clause, few title words, no dash splice, no bare-year lead). Skip any numeric match whose preceding character is a digit or `-–—/` and let the search fall through to the next match; on this finding the fallback ("CBA's 2-year fixed rate is already 6.82%") is itself rejected by the odd-apostrophe check, so the hook correctly degrades to the title. (b) The 100-char word-boundary slice in `_short_title` left a dangling scaffolding tail ("…data-centre clusters are already", "…built-in AI agent in five") or cut inside a coordination ("…R&D tax offset has founders" where the title reads on "…and scientists warning of offshore drift"). Pop trailing tokens while the last one is scaffolding (auxiliary / adverb / number / function word) and at least 4 words survive, and separately cut a `has|have|had|includes|include|involves|with` + ≤3-word tail when the ORIGINAL title continues with `and `/`or `. Do NOT cut a tail that carries its own content nouns — the naive version of this rule ("cut before the auxiliary") shipped three regressions in the same harness run ("…signals chief warns AI agents", "…investors are told a run", "…A$2M pre-seed"), which is why the scaffolding-pop form is the one to keep. Verify with a before/after harness that imports the old copy of the script and diffs every hook across the last ~9 days of `research_*.json`: expect only the intended changes and **zero** regressions (Sep 24 2026: 52 findings / 9 files → 3 hook changes, all improvements):

```python
def load(p, n):
    s = importlib.util.spec_from_file_location(n, p); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m
before, after = load('/tmp/lig_before.py', 'b'), load('~/.hermes/scripts/linkedin_ideas_generator.py', 'a')
def render(m, t, c):
    stat = m.extract_headline_stat(c); short = m._short_title(t)
    return f"{stat}: {short}" if m._hook_stat_ok(stat, short) else short
# diff render() per finding across research_2026-09-*.json; inspect EVERY diff before shipping
```

## Rule 29 (Sep 27 2026) — five defects on one FinTech day, all in the hook/grounding gates

A six-post FinTech day shipped two broken hooks and three blog candidates that had all been
delivered 5–7 days earlier, one of them ungrounded. Every defect below was found by probe
before delivery, and the fixes were verified with two harnesses (hook before/after over the
last 9 `research_*.json`; blog candidate replay over the last 9 days).

**29a. `_hook_clause` can still emit an unclosed parenthetical.** Hook shipped:
`Dabble was hit with more than $1m in penalties for self-exclusion deficiencies (16 September: …`
— the `(` arrived inside the appended tail, so the "drop an unterminated parenthetical tail"
step (which ran before the tail was joined) never saw it. Gate in `_hook_stat_ok`:
`if stat.count("(") != stat.count(")"): return False`.

**29b. A stat clause opening on a third-party subject is not this finding's stat.** Hook
shipped: `Transport has assessed that its 5% maximum non-cash taxi fare surcharge is
unaffected and continues: Card surcharge ban starts 1 October…` — the 5% is South
Australia's cap (a cited source document), not the finding's subject (the RBA ban). Rule 26(a)
caught this class by hand; this gate catches it mechanically: if the clause opens on a
proper-noun token the (short) title never names **and** a copula/reporting verb appears in
positions 1–2 of the clause, reject — the sentence belongs to another actor. `_REPORT_VERBS`
holds the verb set; the auxiliary requirement is what keeps `Australian startups raised
A$3.5bn…` (no auxiliary) hookable while killing `Transport has assessed…` and `Dabble was hit…`.

**29c. A stat sharing ZERO content words with the title is about something else.**
`if sw and not (sw & tw): return False` — the one-line generalisation of Rule 26(a), where a
macro rate-hike clause (`September RBA hike is ~86-91% priced…`) hooked an R&D tax finding.
Both 29b and 29c reject into the safe fallback (title-only hook), so a false positive costs a
weaker hook, never a broken one.

**29d. The 4-day blog rotation is shorter than the 5-day topic cycle, so a same-topic day
always resurfaces the identical slate.** Today's three delivered ideas had all shipped on
20/22 Sep. Widening the window to suppress is NOT the fix (Rule 18 starved the day's own
pillar that way), so a repeat now LOSES instead of disappearing: `recently_proposed_blog_
titles(days=10)` feeds a `_repeat(title)` flag, and the sort key becomes
`(repeat, -hits, pillar_penalty, key)` — freshness first, grounding second. A repeat still
reaches the slate when nothing fresh and grounded exists for the day's pillar (today's third
idea did exactly that, and curation held it).

**29e. Keyword matching was plain substring AND half the candidates carried only context
vocabulary.** `rce` matched inside "source"/"force", `log` inside "technology", `aisi`
inside "raising" (verified: 2 substring hits, 0 word-boundary hits). Fix: `_kw_present()`
uses word boundaries (with plural tolerance — `guardrail` must match "guardrails") for
single-token keywords and substring only for phrases. Then require at least one
SUBJECT-bound hit via `_subject_kw_hits()`, which drops `GENERIC_BLOG_KEYWORDS`
(`governance`, `control`, `regulator`, `transparency`, `log`, `identity`, `credential`,
`accountability`): the padding slot's `nhi-agent-identity` idea shipped on a FinTech day whose
corpus contained "non-human identity", "nhi", "nist", "agent identity" ZERO times, firing on
the single word "identity" from the Quest ID-compromise item. Likewise `tranche2-property`
fired on `austrac`/`tranche 2`/`real estate`/`aml` with "western union" absent (now
subject-bound), and `spf-multiparty-liability` fired on `accc` (now subject-bound).
**Keep the generic list SHORT.** A wider list (payments, licensing, rba, cloud, record,
consultation, carve-out, nsw, concentration, acquisition) was tested against the 9-day replay
and cut back: those words are the SUBJECT vocabulary of specific candidates
(`psp-regulated-software` is about payments licensing; `aml-data-residency-cloud` is about
cloud records), so a global blocklist removed legitimate candidates from their own day — the
"one bad slate traded for another" failure Rule 27 warns about. Only add a word that is
context for EVERY candidate.

**Verification (both harnesses, run every time these gates change):**

```python
# hook harness — expect only intended removals, 0 regressions
h_before, h_after = render(before, t, c), render(after, t, c)   # over every research_*.json
# blog replay — no candidate that shipped historically may become unfireable on its own day
old = [k for k in kws if k in corpus]; new = _subject_kw_hits(kws, corpus)
```

The replay reports a candidate as a REGRESSION whenever `old and not new`; classify each hit
by hand before "fixing" it, because two of the three hits on this run were CORRECT drops
(`cross-org-agent-accountability` fired only on the `aisi`→"raising" phantom plus the generic
word `accountability`; `nhi-agent-identity`'s subject terms were absent). Expect
`psp-regulated-software` to be the canary whenever the generic list grows — if it stops firing
on a payments-licensing day, the list has eaten a real subject word.

---

## Rule 30 (Sep 27 2026) — a best-effort signal source must degrade, not kill the run

`himalaya()` ran `subprocess.run(..., timeout=30)` with no exception handling. `envelope list`
hung, and the `TimeoutExpired` propagated out of `main()`: **no output file was written at all**
— `get_signals_from_files()` never got its turn, so a transient himalaya stall silently
produces nothing rather than the file-based slate the fallback exists to provide. Wrap the
helper and return `""`; both callers already read empty output as "use the fallback".

```python
try:
    result = subprocess.run(["himalaya"] + list(args), capture_output=True, text=True, timeout=30)
    return result.stdout
except Exception as exc:   # any failure means "no signals here"
    print(f"  ⚠️  himalaya {args[0] if args else ''} unavailable: {type(exc).__name__}")
    return ""
```

The general rule: **any external command inside a generator is best-effort — an exception in it
must fall through to the offline source, because a generator that dies before writing is
indistinguishable from a cron that never ran.** Confirm a re-run after such a fix produces the
file (`Output:` line + mtime).

---

## Rule 31 (Sep 27 2026) — run the recipes against the DELIVERED block, not the whole file

A curated section supersedes the auto-generated posts, but both blocks stay in the same
file, so a whole-file CTA scan compares 6 auto closes against 5 curated ones and reports a
false near-duplicate: the curated post 4 close ("If you are mid-licence-application or working
through the card-scheme and PSP changes this creates…") scored **0.70** against the auto post 4
close it replaced — the same sentence, once. Scope every recipe to the block that will ship:

```python
curated = txt.split('# ✅ Curated by Pluto', 1)[1]
ctas = re.findall(r'\*\*CTA:\*\* (.+)', curated)
fps = [frozenset(w for w in re.findall(r"[a-z']+", c.lower())
                 if len(w) > 3 and w not in _CTA_STOPWORDS) for c in ctas]
assert len(ctas) == len(set(ctas))
assert max((len(fps[i] & fps[j]) / min(len(fps[i]), len(fps[j]))
            for i in range(len(fps)) for j in range(i+1, len(fps))), default=0) < 0.4
```

This run: auto block 6/6 distinct, curated block 5/5 distinct, max curated pairwise 0.10.
The false flag was still worth chasing — reading it is what surfaced that the curated CTA had
been copied from the engine's line instead of written fresh, so the delivered post answered its
predecessor rather than the reader. **A false-positive recipe hit on a human-edited block is a
prompt to rewrite the line, not to widen the threshold.**

---

## Verification recipes (run over the written file, not the in-memory objects)

```python
hooks  = [l[len('**Hook:** _'):].rstrip('_') for l in txt.split('\n') if l.startswith('**Hook:** _')]
angles = [l[len('**Angle:** '):] for l in txt.split('\n') if l.startswith('**Angle:** ')]
assert all(a.rstrip().endswith(('.', '!', '?', '…')) for a in angles)   # no hanging separators
assert all(h.count(':') <= 1 for h in hooks)                            # no "A: B: C" double-splice
# no dangling quote / no dangling function word
for h in hooks:
    for q in ("'", '"'):
        pos = [m.end()-1 for m in re.finditer(r"(?:^|\s)"+re.escape(q)+r"(?=[A-Za-z0-9])", h)]
        assert not (pos and q not in h[pos[-1]+1:]), h
    assert h.split()[-1].lower().strip('.,;:()%$') not in DANGLE_TAIL, h

# CTAs: no verbatim repeat AND no near-duplicate close (rule 25)
ctas = re.findall(r'\*\*CTA:\*\* (.+)', txt)
assert len(ctas) == len(set(ctas)), 'verbatim CTA repeat'
fps = [frozenset(w for w in re.findall(r"[a-z']+", c.lower())
                if len(w) > 3 and w not in _CTA_STOPWORDS) for c in ctas]
worst = max((len(fps[i] & fps[j]) / min(len(fps[i]), len(fps[j]))
             for i in range(len(fps)) for j in range(i+1, len(fps))), default=0)
assert worst < 0.4, f'near-duplicate CTA pair (similarity {worst:.2f})'

# rule 29a: no unbalanced bracket in a stat-prefixed hook
assert all(h.count('(') == h.count(')') for h in hooks), [h for h in hooks if h.count('(') != h.count(')')]
# rule 28a/29e: every delivered blog idea is grounded (matches >= 1)
for m in re.finditer(r'\*\*Gap filled:\*\* .*?\(signal matches: (\d+)\)', txt):
    assert int(m.group(1)) >= 1, m.group(0)
```

## Rule 27 (Sep 25 2026): a blog candidate's keywords must be SUBJECT-BOUND, never regulator vocabulary

`BLOG_CANDIDATES` matched on substrings of a signal corpus that spans several days
(`get_signals_from_files()` reads every recent `mempalace-inputs/` file), so any keyword
that appears on *every* regulatory day will fire regardless of the subject. The
`fiig-penalty` candidate carried `["fiig", "penalty", "asic", "afsl", "cyber", "enforcement"]`
and reached the **delivered** slate on an AI-Regulation day with 3 hits — while `fiig` and
`penalty` occurred **zero** times anywhere in the corpus. Its A$2.5m framing was unverifiable
to any source we could reach.

- **Authoring rule:** a candidate's keyword list must contain only terms that identify its
  own subject (`fiig`, `fiig securities`). Words such as `asic`, `afsl`, `cyber`,
  `enforcement`, `penalty`, `regulator`, `compliance` describe *any* day's context and are
  banned from keyword lists.
- **Verification before delivering any blog idea:** count occurrences of the candidate's own
  subject term in the corpus; if it is 0, the candidate is ungrounded — drop it.
  `grep -ci '<subject>'` across `mempalace-inputs/*<date>*.md` + `research_<date>.json`.
- **Do not fix this with a global anchor gate** (`if keywords[0] in corpus`). Tested and
  reverted the same run: it excluded the day's two best-fit candidates
  (`agent-incident-register` — its anchor phrase `incident report` never appears, the corpus
  says "AI incidents" / "incident-reporting"; `autonomy-tiers` — anchor `autonomy` absent)
  while still admitting others, so it traded one bad slate for another. Fix the mis-specified
  candidate, not the matcher.
- **Empirical probe** — run this before trusting the blog block on a new topic:

```python
import importlib.util, sys
spec = importlib.util.spec_from_file_location('lig', '~/.hermes/scripts/linkedin_ideas_generator.py'.replace('~','/home/habib'))
lig = importlib.util.module_from_spec(spec); sys.modules['lig'] = lig; spec.loader.exec_module(lig)
research = lig.load_research(); corpus = " ".join(lig.get_signals_from_files()).lower()
corpus += " " + " ".join(f.get("title","")+f.get("content","") for f in research["findings"]).lower()
for key,title,pillar,gap,kws in lig.BLOG_CANDIDATES:
    hits = [k for k in kws if k in corpus]
    if hits: print(f"{key:32s} hits={len(hits)} {hits}")
```

A candidate ranking first on words that are not in its own title is a false positive.

---

## Rule 28 (Sep 26 2026) — three defects, all in the delivery path

**28a. Blog padding must be GROUNDED, not just same-pillar.** Rule 13 gated the padding
slot on `day_pillars()`, and Rule 27 made the FIIG candidate's keyword list
subject-bound (`["fiig", "fiig securities", …]`). The FIIG idea still reached the
delivered slate: on a Cloud & Infrastructure day *every* Cloud candidate satisfies
`pillar in wanted`, so the padding loop (which had no hit requirement) filled the third
slot with a zero-hit candidate. Verified by probe: FIIG scored **0 hits** (`grep -i fiig`
across `research_2026-09-26.json` + the signal corpus returned nothing) while
`datacentre-energy-grid` (5) and `cloud-waste-finops` (1) were the only grounded Cloud
candidates that day — so the correct slate is **two** ideas, and the engine's own comment
("two well-matched ideas beat three") already said so.

Fix — a padding candidate needs at least one term of its own in the corpus:

```python
for key, title, pillar, gap, keywords in BLOG_CANDIDATES:
    if key in chosen or not _fresh(key, title) or pillar not in wanted:
        continue
    if not any(kw in corpus for kw in keywords):
        continue
```

Assertion: every delivered blog idea reports `signal matches >= 1`; the slate may be two
long. Do NOT reintroduce a global anchor gate (`keywords[0] in corpus`) to solve this —
Rule 27 tested and reverted that, because it excludes good candidates whose anchor phrase
is worded differently in the corpus.

**28b. The terminal CTA branch ignored `seen` and reprinted one line.** `_pick_cta`'s
final fallback was hardcoded: it appended `"What would this look like in your stack?"` to
`seen` and returned it *unconditionally*, so when the portfolio CTA, pillar CTA and all
three `CTA_ALTERNATES` were spent (six same-pillar posts on a single-topic day), posts 5
and 6 closed with the identical sentence. Fix: add `CTA_FALLBACKS` (four closes with no
shared content words) and pick the least-used one, tie-broken by index:

```python
counts = {c: seen.count(c) for c in CTA_FALLBACKS}
pick = min(CTA_FALLBACKS, key=lambda c: (counts[c], CTA_FALLBACKS.index(c)))
seen.append(pick); return pick
```

Assertion (run every time): parse `**CTA:**` lines from the output md, then check
(a) no exact duplicates and (b) no pair whose `_cta_fingerprint` overlap is `>= 0.4`.
This run: 6/6 distinct, 0 pairs flagged.

**28c. `_balance_fragment` strips terminal full stops — re-terminate after balancing.**
Wiring `_balance_fragment` into `_trim_angle` (to drop the unclosed `(` on the Oracle
angle) silently removed the full stop from the sentence-end cut, shipping four angle
fragments with no terminal punctuation (`…across the markets the RBA covers`,
`…approaching US$6.2tn`) — a Rule 20 regression. Fix: a `_ensure_terminal()` wrapper
applied on every `_trim_angle` return path:

```python
def _ensure_terminal(s):
    s = (s or "").rstrip()
    return s if s.endswith((".", "!", "?", "…")) else s + "."
```

Assertion: every `**Angle:**` line ends in `.!?…` and has `count("(") == count(")")`.
The general lesson — **any helper that strips trailing punctuation must be paired with a
re-termination step at the boundary where punctuation is a contract** — applies to
`_short_title`/hook paths too, not just angles.

---

## Rule 32 (Sep 28 2026) — a hook must not end on a verb whose object the slice cut away

Delivered hook: `MCP exposure ranks LAST among CISO priorities while >6% of enterprise
chatbot conversations carry` — the word-boundary slice in `_short_title` stopped on a verb,
so the object of that verb (`sensitive data`) was never reached. The existing gates missed
it because `carry` is not in `TRAILING_WORDS`/`_WEAK`/`DANGLE_TAIL` and the subordinate-tail
regex (`while|as|and|…` + 1–3 words) refused a 6-token tail.

A slice ending on a present-tense/base verb is *provably* unfinished, which makes this the
one safe place to cut an arbitrarily long subordinate clause. Fix — a bounded `_DANGLE_VERBS`
set (carry/hold/contain/include/involve/require/need/drive/take/hit/give/make/show/report/
produce/use/run/allow/remain/become/leave/spend/affect/raise/reach/face/expect/want/see/
keep/add/offer/cover/deliver, with `-s` forms), applied after the scaffolding pop:

```python
def _ends_on_verb(text):
    words = text.split()
    return bool(words) and words[-1].strip(" ,;:.%$()\"'").lower() in _DANGLE_VERBS

if _ends_on_verb(sliced):
    m = re.search(r"\s(?:while|whereas|because|since|as)\s+\S.*$", sliced, re.IGNORECASE)
    cand = (sliced[:m.start()].rstrip(" ,;:-—–") if m and m.start() >= 30
            else sliced.rsplit(" ", 1)[0].rstrip(" ,;:-—–"))
    if len(cand) >= 30:
        sliced = cand
```

**The gate is the verb, not the clause length.** A blanket "cut any subordinate clause"
rule damages good hooks (`…then shelved after media pushback`, Sep 22 2026); requiring the
slice to END on a verb means the clause was already broken, so cutting back to the main
clause only ever repairs it. Result: `MCP exposure ranks LAST among CISO priorities`.

## Rule 33 (Sep 28 2026) — the scaffolding pop must not leave a bare quantity

The same day's NIST hook shipped `UPDATE to the 12 Sep standards-race feed: the NIST agent
deadline is now three months` — `out` is in `TRAILING_WORDS`, so the first pop loop removed
it and left a quantity with nothing completing it. There were TWO pop loops (the
`TRAILING_WORDS` loop and the later `_WEAK` loop); guarding only one leaves the defect live.
Both now break when the remainder would end on a measurement phrase:

```python
_MEASURE = re.compile(
    r"\b(?:\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten|several|few)\s+"
    r"(?:hour|day|week|month|year|quarter|decade)s?$", re.IGNORECASE)

while words and words[-1].lower() in TRAILING_WORDS:      # and again in the _WEAK loop
    if _MEASURE.search(" ".join(words[:-1])):
        break
    words.pop()
```

Result: `…the NIST agent deadline is now three months out`.

**Verification (run both fixes together):** the before/after hook harness over the last 9
`research_*.json` renders **52 hooks, 2 changed, 0 regressions** — the only two diffs are the
two defects above. Assert it, don't eyeball one day's file: a day-scoped check cannot see
that the fix re-cut hooks the previous rules had already repaired.

## Rule 34 (Sep 28 2026) — the keyword gate protects SELECTION, not the CLAIM

`agent-rollback-evidence` reached the delivered blog slate titled **"84% of Australian Firms
Have Rolled Back an AI Agent. Can You Evidence Yours?"** while `84%` and `rollback` occurred
**zero** times in the day's corpus. It cleared `_subject_kw_hits()` on `auditability` and
`pii` — context vocabulary that appears on almost any compliance day — so the candidate was
ungrounded twice over: the pool of words and the number in its own title.

- **A candidate TITLE is an assertion, not framing.** Every statistic in a candidate title
  must be countable in the corpus that fired it. Rules 27/28a police the keyword list; they
  say nothing about a fabricated number inside the title, which is what a reader actually
  sees. Verify with a direct count (`grep -ci '<the figure>'` across the day's
  `mempalace-inputs/` + `research_<date>.json`) before delivering.
- **Fix the candidate, not the matcher.** Reworded to "When the Agent Gets Rolled Back: The
  Evidence Trail a Regulated Firm Still Owes", keywords cut to `rollback`, `rolled back`,
  `agent rollback`, `trust pulse`, `sinch`. It now scores 0 hits and correctly does not
  appear until a day's corpus actually discusses agent rollback — which is the honest
  outcome, not a loss.
- Watch the input-file glob when counting: `mempalace-inputs/*2026-09-28*.md` misses
  `gmail-briefing-<id>-20260928_<time>.md`. Use `*20260928*` as well, or a "0 occurrences"
  verdict is really "I looked in the wrong file".

## Rules 35–37 (Sep 29 2026) — three hook defects on one Startup & VC day

Three of six hooks shipped broken or awkward on the Startup & VC run. All three live in the
hook path (`extract_headline_stat` → `_hook_stat_ok` → `_short_title`) and each reproduces
from that day's own `research_2026-09-29.json`.

### Rule 35 — parenthetical figures defeated the stat-duplication check

**Defect:** the hook read `Amber Electric closed a $78.5 million (EUR 49m / US$56.22m)
Series E: Amber Electric closes $78.5m Series E led by Morgan Stanley's 1GT` — the same
sentence twice.

- **Cause:** two gates failed on the same clause. The duplicate check `all(n in short for n
  in nums)` took `nums` from the raw stat, and the parenthetical currency conversions
  (`49`, `56.22`) appear nowhere in the title, so the check never fired. The content-word
  ratio gate then landed on **exactly 0.40** (10 stat words, 4 shared: amber/electric/
  series/E) — and the gate is `> 0.4`, so it passed by one word.
- **Fix:** strip parentheticals before harvesting figures — `re.findall(r"\d[\d.,]*",
  re.sub(r"\([^)]*\)", " ", stat))`. This is Rule 26's "skip numbers inside parentheses"
  extended from *extraction* to the *duplicate check*.
- **Assertion:** the hook collapses to the title-only form `Amber Electric closes $78.5m
  Series E led by Morgan Stanley's 1GT`. Prefer this over moving the 0.4 threshold: the
  ratio is a proxy for "same sentence", a shared headline figure is the actual test, and
  loosening the ratio would suppress good stat prefixes elsewhere.

### Rule 36 — slice ended on a dangling auxiliary after a coordination

**Defect:** `UPDATE to the 8 September feed: Harrison.ai says contracted ARR quadrupled to
$40m and R&D stays`.

- **Cause:** two compounding gaps, and the second is the general lesson. (a) `stays` was not
  in `_DANGLE_VERBS`, so Rule 32's verb-drop never fired. (b) The dangling-subordinate-tail
  regex used `(?:\w+['’]?\w*\s*){1,3}$`, and `\w+` **cannot match a token containing `&`** —
  so ` and R&D stays` was invisible to it. Any punctuation-bearing token (R&D, US$56,
  state-level, 2026-27) is un-matchable by a `\w` group; check the tail pattern, not just the
  verb list, when a dangling slice survives.
- **Fix:** add `stay`/`stays` to `_DANGLE_VERBS`, and widen the tail pattern to
  `(?:\S+\s*){1,3}$`. The widening is narrow by construction — every token the old pattern
  matched, the new one matches identically — so previously-repaired hooks are unchanged.
- **Assertion:** the hook becomes `…contracted ARR quadrupled to $40m`.

### Rule 37 — slice split a multi-word proper noun

**Defect:** `NSW innovation funding retreat hardens: tech minister hand-wrote '$0' over a
recommended $40k Spark` — the entity is **Spark Festival**.

- **Cause:** the word-boundary slice at the 100-char limit landed between the two words of
  the name, and nothing in `_short_title` knows a capitalised token may continue into the
  next one.
- **Fix:** in the word-slice branch, before the trailing-word pops run, if the last retained
  token is capitalised AND the next token of the original head is capitalised, append that
  token. A one-or-two token overshoot is cheaper than a half-named entity.
- **Assertion:** the hook ends `…over a recommended $40k Spark Festival`.

**Harness and assertion for all three.** Copy the generator to `/tmp` before editing, import
both copies by path (`importlib.util.spec_from_file_location`), recompute every finding's hook
in both, diff. Result on this run: **48 findings over 8 research days → 3 hooks changed, 3
improvements, 0 regressions.** Two harness cautions: it scans only `research_*.json` (so it
cannot see blog-candidate changes), and its "unbalanced quote" flag fires on possessives
(`Stanley's`) — count quoting pairs, not raw apostrophes, before calling something a
regression.

## Rules 38–39 (Sep 30 2026) — a tag shipped as a hook, and a repeat took the leftover slot

**Rule 38 — the pipeline's own repeat tag became the hook.** `_short_title` normalises with
`raw.split(" - ")[0]`, which exists to drop a publisher suffix ("Headline - Publisher"). The
research phase tags repeat findings with its own bookkeeping prefix, so four of six posts on
the 30 Sep AI-Regulation day shipped with a hook of literally `UPDATE` (x3) or `FOLLOW-ON` —
a label, not a claim, and useless as the first line of a post.

Fix: strip a leading `UPDATE|UPDATED|FOLLOW-ON|FOLLOW ON|FOLLOWUP|FOLLOW-UP|FORMALISATION|
FORMALIZATION|NEW` tag before the dash split, keeping the full tagged title for display.

Two constraints, both found by the before/after harness:

1. **A separator must actually follow the tag.** The first attempt made the separator
   optional (`\s*(?:[-–—:]\s*)?`), which rewrote `UPDATE to the 12 Sep standards-race feed:
   …` into a hook opening `to the 12 Sep standards-race feed:` and `UPDATE to the 8 September
   feed: …` into `to the 8 September feed:` — the tag sentence IS the title there, so
   stripping it strands a preposition. Require the separator: `\b\s*[-–—:]\s*`.
2. **Never trade a tag-only hook for an empty one** — if stripping leaves nothing, keep the
   original.

Harness: `_short_title` old vs new over the last 9 `research_YYYY-MM-DD.json` files, flagging
any result that is under 8 chars, is a bare tag, or opens on `to|of|for|and|the`.
Result: **5 hook changes, 0 regressions** (4 on 30 Sep = the tag defects; 1 on 29 Sep turning
`UPDATE: startup CGT carve-out consultation closed…` into the headline itself).

**Rule 39 — a within-10-day repeat must not take the leftover slot.** Rule 29d marks a
candidate proposed in the last 10 days as a repeat and sorts it last, but "last" still wins
when only two fresh candidates match: on 30 Sep the third blog slot went to
`aml-data-residency-cloud`, already delivered on 24 Sep. Haris reads the slate, not the sort
order. Fix: when >=2 fresh grounded candidates exist, emit those and stop (`_fresh_hits[:3]`);
repeats still pad only when fewer than two fresh candidates exist, and the padding loop now
skips repeats as well.

Also added this run: candidate `insurer-as-regulator` ("Your Insurer Is Now Your AI Regulator:
The Private Route to Obligation", pillar `AI Agents & Governance`, subject-bound keywords
`insurer|insurance|underwriting`). It fills a gap no existing candidate covers — the private
enforcement channel: obligations arriving via underwriting, procurement conditions and private
standards bodies while statute stalls — and it fired on the day's own signal that enterprise
obligations land there first. CTA invariants re-asserted: 0 exact duplicates, worst content-word
fingerprint overlap 0.17.

## Rule 40 (Oct 1 2026) — a hook ended on a bare initialism, and the blog slate recycled wholesale

One Cloud & Infrastructure day produced one hook defect and a blog block that was entirely
recycled from the topic's previous cycle. Both were caught by probe before delivery.

### 40a. A slice ending on an all-caps acronym ships half a compound noun

**Defect:** `Investment-flight warning crystallises: peak body says Australia risks losing
A$30bn of AI` — the 100-char word-boundary slice in `_short_title` stopped between `AI` and
`investment`. Every existing gate missed it: `AI` is not in `TRAILING_WORDS`/`_WEAK`/
`DANGLE_TAIL`, it is not a dangling verb (Rule 32), and Rule 36's proper-noun guard asks for
BOTH tokens to be capitalised (`investment` is lowercase).

**Fix:** when the last retained token is an all-caps acronym of <=4 letters, pull the next
token in. Applied in the word-slice branch, after the Rule 36 capitalised-pair check:

```python
if words and _rest and 1 < len(words[-1]) <= 4 \
        and words[-1].isupper() and words[-1].isalpha():
    words = words + [_rest[0]]
```

Narrow by construction — one extra token at most — and the later scaffolding/`_WEAK` pops leave
it alone (`investment` is neither). Assertion: hooks no longer end on a bare acronym.

**Harness:** before/after `render()` over the last 8 `research_*.json` files — **48 findings,
1 changed, 0 regressions**.

### 40b. The day's OWN pillar had no un-repeated candidate, so the block came back identical

On 1 Oct (Cloud & Infrastructure, the topic's 5-day cycle returning) the delivered blog slate was
`datacentre-energy-grid` and `cloud-waste-finops` — both **verbatim repeats of 26 Sep** — plus
`aml-data-residency-cloud`, already delivered 24 Sep. Rule 39 could not help: with `_fresh_hits`
empty there was nothing fresh to promote, and Rules 13/28a then required the padding slot to be
same-pillar AND grounded.

**The fix is the candidate list, never the matcher** (Rules 18/23): three grounded Cloud
candidates were added, each subject-bound to the day's own evidence and verified to fire on it
while NOT firing on other days' subjects (blog-candidate replay across 8 research days):

| key | subject hits on 1 Oct | other days |
|-----|----------------------|------------|
| `datacentre-permitting-risk` | 6 (`project mars`, `goodman`, `lane cove`, `withdrawn`, `fast-track`, `senate inquiry`) | 1 hit on 25/26/27 Sep |
| `datacentre-efficiency-disclosure` | 6 (`pue`, `wue`, `usage effectiveness`, `rating scheme`, `waste heat`, `delegated regulation`) | none |
| `compute-securitisation-lockin` | 5 (`firmus`, `bookbuild`, `prospectus`, `data#3`, `vendor lock-in`) | 24 & 29 Sep (the float's own coverage — legitimate) |

Slate went from 3 recycled to 3 fresh grounded ideas. **Diagnostic to run the moment a topic
comes round and the slate looks familiar:** count the candidates for that day's OWN pillar
(`_subject_kw_hits` probe below) before touching the rotation window or the padding gate.

### 40c. Two candidate defects fixed the same way — by fixing the CANDIDATE

- **`cloud-waste-finops` shipped an ungrounded figure in its TITLE.** Delivered as "The 29% You
  Are Paying For Nothing" while `29%` AND `finops` occurred **zero** times in the corpus
  (`grep -ci` across `mempalace-inputs/*20261001*` + `research_2026-10-01.json`). Rule 34 in
  action: a title is an assertion. Reworded to "FinOps as a Compliance Deliverable: Proving
  Cloud Cost Control, Not Just Reporting It" and its keyword list trimmed to subject terms
  (`capex` was doing the firing, and `capex` is context on any cloud day) — it now correctly
  scores 0 and does not ship until a corpus actually discusses FinOps.
- **`aml-data-residency-cloud` fired on context vocabulary.** Its list was
  `[data residency, record, cloud, tranche 2, amlhive, austrac, vendor]`; `record`/`cloud`/
  `vendor` match ANY cloud day, which is how a 24 Sep repeat re-took a slot on a Cloud day. Now
  `[data residency, record-keeping, records retention, offshore vendor, aml record]` → 0 hits,
  correctly excluded. Note this is the mirror image of Rule 29e's warning: **tighten a specific
  candidate's list when its words are context for that candidate; never widen the global
  `GENERIC_BLOG_KEYWORDS` blocklist** (it eats real subject words such as `payments`/`records`).

**Invariants re-asserted this run:** auto block 6/6 CTAs distinct (worst fingerprint 0.33),
curated block 5/5 distinct (worst 0.18), 0 dangling quotes/brackets, every angle terminal,
every delivered blog idea >= 1 subject hit, and the curated section byte-identical across a
generator re-run (Rule 17).

**Provenance note for the same run:** no `gmail-briefing-*.md` existed for the day (newest was
the previous day's), the `inbox_*.json` dumps were podcast-filter streams rather than a
Perplexity topic, and the newest Claude Daily Research file was 3 days old — so the slate was
research-driven and that degradation was stated in the output file rather than glossed over.

## Rules 8–12 (moved out of SKILL.md 2026-09-29) — generator hardening, remaining items

8. Pillar from `portfolio_hit`, not from regulator keywords.
9. Order research ideas one-per-pillar before truncating (cap 6).
10. Never take a clause boundary from inside a parenthetical.
11. Currency-unit regexes must be case-insensitive and token-bounded (`$100M` ≠ `$100 M`).
12. Blog rotation suppresses recent titles; `KNOWN_BLOGS` retires them.

Items 1–7 and 13–20 are the numbered entries under the heading above; 21–23 and 27–40 follow in
this file. SKILL.md now carries only a pointer to this log — the condensed list had been
duplicated here and SKILL.md had drifted to 100,689 bytes, over its 100K limit (trimmed back to
~99.3K on 2026-10-01 by folding Rules 24–30 and 32–40 into pointers, since the detail lives here).

