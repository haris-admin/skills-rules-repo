---
name: monitoring-alert-verification
description: Use when verifying monitor alerts or writing checks.
---

# Monitor & Alert Verification

Rules for any script that decides PASS/ALERT on behalf of a system: cron monitors, sync
checkers, uptime probes, test runners, pipeline health checks. Applies both when authoring
the checker and when triaging what it reports.

## The two failure modes — both are bugs

1. **Fake PASS** — rendering ✅ when the work never completed. Root cause is nearly always
treating an ACKNOWLEDGEMENT as a RESULT: an enqueue, a 202/200, a queued job id, a
fingerprint that was read rather than earned.
2. **Fake FAIL** — rendering ❌ when the work actually succeeded. Root cause is nearly always
   asserting on the IMMEDIATE response for work that finishes ASYNCHRONOUSLY. The alert
   fires, the job completes minutes later, later runs inherit a "failure streak", and the next
   session debugs a healthy system.
3. **Silent failure** — the checker never reports at all, so nothing is rendered and nobody
   looks. A script-only cron (`no_agent: true`) that exits non-zero with EMPTY stdout delivers
   *nothing*: the error lives only in the job's own output directory, and under an "empty
   output = send nothing" watchdog convention a broken run is indistinguishable from a quiet
   one. Two fixes, use at least one: make the failure path itself print a one-line
   `FAIL: <reason>` on stdout, and/or set the job's failure-notice target so engine-level
   failure notices land where a human reads them. In Hermes that target is the per-job
   `failure_deliver` field (`cronjob(action='update', job_id=…, failure_deliver='telegram:…')`,
   empty string clears it) — and its DEFAULT is to follow `deliver`, so every job whose output is
   saved locally instead of sent can fail in complete silence. Audit for them:
   `python3 -c "import json;[print(j['id'],j.get('name')) for j in json.load(open('/home/habib/.hermes/cron/jobs.json'))['jobs'] if str(j.get('deliver'))=='local' and not j.get('failure_deliver')]"`.
   A monitor you only notice when it is happy
   is not a monitor.

4. **Undelivered assurance** — the run reports `ok`, you tell the human it was sent, and nothing
   reached them. Every "nothing to report" convention (`[SILENT]`, empty stdout, suppressed
   delivery) is *by design* silent, so an agent handed a "report the baseline" prompt can finish
   successfully and deliver nothing. Run status proves the job completed, not that a message
   exists: read the job's own output file (`~/.hermes/cron/output/<job_id>/<timestamp>.md`) and
   check the response section before claiming delivery — never write "this is being delivered now"
   about a run you have not read.

All four are fixed the same way: **rank the evidence.** Immediate response < durable state —
and a run that produced no output has produced no evidence.

## Rules

- **Read the SOURCE OF TRUTH — never a mirror of it.** A checker wired to a dashboard, cache or
  replica has a *second* thing that can fail, and its failure mode is not an error but a
  clean-looking **ZERO**: the mirror answers empty, the checker totals 0, and it renders "nothing to
  see" as a PASS. Observed: a cost monitor scraped a local dashboard plugin that merely mirrored the
  register; the plugin moved ports and the monitor reported `Assets: 0 · A$0.00/month` for four
  consecutive days — the **opposite of the truth**, and far more dangerous than a crash, because a
  crash gets fixed and a plausible zero does not. Wire the checker to the system of record (the API or
  DB that OWNS the data) and keep it independent of anything local whose port, process or lifecycle
  can drift. If a mirror must be used, **assert its liveness first** — a mirror that cannot prove it is
  serving must render UNKNOWN with the reason, never 0.
- **A locally computed cost is an ESTIMATE, never a measurement.** Tokens x published price is right for
  planning per-item spend (it told us a repair would cost cents), but it silently omits everything else
  billing on the same credential and says nothing about the provider's real tally. Before quoting spend
  to the user, read the provider's own usage: OpenRouter's `GET https://openrouter.ai/api/v1/auth/key`
  returns `usage_daily` / `usage_weekly` / `usage_monthly` / `usage` (lifetime) and `/api/v1/credits`
  returns credits purchased vs consumed — that is the figure the user can check themselves, and this user
  checks at source. Report the estimate AND the billed figure, and name which is which.
- **An acknowledgement is never a result.** If an API returns `enqueued` / `queued` /
  `accepted` / a job id, that proves the request was accepted — nothing more. Never ✅ on it.
- **Never ❌ on an acknowledgement either.** An async run you could not observe is
  *unverified*, not failed. Confirming it is the checker's job, not the reader's puzzle.
- **Verify by polling durable state until it ADVANCES**, then stop. Choose a signal that can
  only change once the work really landed — a persisted fingerprint, a state row's
  timestamp, a row count — never a flag the caller itself sets.
- **Confirm the verification signal is deployed before wiring a checker to it.** A route or
  column that exists only on a branch is absent in production: a read-only status `GET` against
  an image that predates it returns **405** because a path-param `POST /prefix/{id}` route matches
  the path with the wrong method — that reads like an auth/route bug but means "not shipped yet".
  Probe the signal and treat 404/405 as *not deployed*; interrogate the durable store directly
  until it ships, and only then switch the checker over.
- **Bound the wait to the measured job duration.** Size the window from observed completion
  times (a 4–8 min job wants ~12 min of slack in 90s probes) and confirm the scheduler's own
  timeout exceeds the worst case *before* shipping. An unbounded loop inside a cron is an
  outage waiting to happen.
- **A stuck run still ends as ALERT** once the window is exhausted. Verification removes
  false alarms; it must never remove honesty.
- **Compare timestamps before believing an alert.** If the durable `last_success` is LATER
  than the alert time, that run was a false negative — fix the checker, not the backend.
- **A failure streak proves the checker is unhappy, not that the work failed.** Repetition
  is not corroboration; N identical false negatives look exactly like a real outage.
- **Read live serving stores read-only** (`sqlite3.connect("file:...?mode=ro", uri=True)` or
  equivalent). A write connection can contend with a production lock. Reading state and
  counts is enough to establish truth.
- **Name the cause you actually proved.** A hardcoded alert string ("worker not
  initialised", "credentials missing") goes stale the moment that cause is fixed, and then
  misdirects every future reader. Alert text should describe the observed condition
  ("enqueued but not confirmed within N minutes"), not a remembered diagnosis.
- **A hit count is not a failure count.** Before reporting that an error class is occurring, open
  the matched lines: a grep for a vendor name or an error string ("rate limit", "quota", "429",
  "credit") also matches docstrings, spec prose, and test fixtures that *describe* that error path,
  so a perfectly healthy system can yield hundreds of hits — and reporting them as real failures
  invents an incident. Enumerate real usage by CALL SITE instead
  (`api.<vendor>.com/v1/<endpoint>`) and state a count only from lines you have read.
- **A generic word inside a longer identifier is not a failure signal.** A substring test for
  `"failed"` / `"error"` / `"denied"` also fires on strings that merely CONTAIN it: a worker
  startup banner that enumerates its registered functions (`Starting worker for N functions: …,
  retry_failed_notifications, …`) matched on `failed` and was reported as a production incident on
  every healthy run, for weeks, because the alert text looked plausible. Anchor the match so it
  cannot land inside an identifier (`re.search(r"\bfailed\b", low)`) **and** skip lifecycle lines
  (startup / shutdown / registration / function-list banners) before classifying — those enumerate
  names, they do not report outcomes. Alert on the precise failure signature only; keep every other
  token in the display-only set.
- **Missing data is UNKNOWN, never healthy.** A metric the checker could not obtain must render as
  unknown with the reason attached, never as a green tick beside it — `CPU: N/A` under a ✅ tells the
  reader the machine is fine when nothing was measured at all. The same trap inverted: an alarm whose
  metric has stopped being published (`no datapoints were received for N periods`) is measuring
  nothing, so establish whether the metric is still emitted before calling it an outage *or* an
  all-clear. If it is not emitted, the finding is a monitoring gap with a named owner — not a P1
  incident and not a pass.
- **An empty successful read is a THIRD state — never fold it into the error branch.** A probe that
  reports "transport error" because its output string was empty cannot tell *the read failed* from
  *the thing read is empty*, and it cries wolf on healthy hosts: a check written as
  `if not out or out.startswith("SSM_"): render "SSM error"` labelled every green machine broken,
  because a present-but-0-byte log returns `""`. Classify all three explicitly and render each in its
  own words — read failed (the tool's own error sentinel), resource absent (a `test -f` fallback
  emitting a NAMED sentinel the caller then tests for), present-but-empty (clean). "No output" is a
  state to be named, not a synonym for failure.
- **A pipeline's exit status is its LAST command's — `||` after a pipe never fires on a missing input.**
  `cat missing.log | tail -50 || echo NO_LOG` always takes the success branch, since `tail` exits 0 on
  an empty stream; the fallback sentinel is unreachable and the failure surfaces only as emptiness,
  which the classifier then misreads as an infrastructure error. Guard the input explicitly instead:
  `for f in A B; do [ -f "$f" ] && { tail -50 "$f"; exit 0; }; done; echo NO_LOG`.
- **A value probe must be proven to return the REAL value, not its placeholder.** Extractors rot
  silently because their failure mode is indistinguishable from success: a regex written for
  `VERSION = "1.2.3"` stops matching the moment the source declares `VERSION: str = "1.2.3"`, so the
  probe keeps emitting its placeholder (`v?`) while the value sits right there. Allow the optional
  intervening tokens (`VERSION(?:\s*:\s*\w+)?\s*=`) and assert the probe returns a real value against
  the live source before trusting it — a probe with a fallback default must be tested until it does
  NOT fall back.
- **Compare values SEMANTICALLY, never lexically.** A version, duration or size compared as a
  string silently inverts the truth the moment the format changes shape: `"0.50.101" <
  "0.5.168"` lexicographically, although `(0,50,101) > (0,5,168)` numerically — and because it
  fails toward "no drift" it reads as a clean PASS rather than an error. Parse to the comparable
  type (`tuple(int(x) for x in v.lstrip("v").split(".")[:3])`), fail closed on malformed input,
  and when a product or repo changes its numbering scheme, audit EVERY consumer of that string
  before the first release under the new scheme.
- **A zero result must assert its own liveness.** Record INPUT counters separately from
  findings — `items_seen` / `items_in_window` / `hits` — and treat `hits == 0` as an empty
  state only when the input actually carried fresh material. `items_seen > 0` with
  `items_in_window == 0` means the FETCH is broken, not that the world is quiet: a pipeline
  read hundreds of headlines, dropped every one on a recency filter (all of them years old),
  and reported a clean zero for days. Labelling a zero "empty" does not make it one — an
  unverified zero is a dead instrument reporting silence.
- **A stage must never log `success` on zero output — measure the PRODUCER's freshness, not its exit
  code.** The same zero-liveness rule applies one link upstream, where it is more dangerous because
  every downstream reader keeps working perfectly on a corpus that no longer grows: an ingest stage
  wrote `status = 'success'` with `chunks_created = 0` on every run for months, so 98% of the stored
  episodes became unreachable by the pipeline that selects on chunk count — while each run's status,
  exit code and duration all looked healthy. Two habits catch it:
  (1) assert the stage's OWN output count and exit non-zero on zero (`created == 0` is a failure of
  the producer, not an empty day); (2) **probe producer freshness** — `max(created_at)` of the
  artifact it writes versus `max(created_at)`/newest timestamp of its INPUT. An output watermark that
  stopped advancing while the input keeps moving is a dead producer, and it is the cheapest detector
  that exists (one query, no log-diving).
- **An "already processed" marker must compare CONTENT, not merely exist.** A consumer that skips a file
  because `<name>.done` exists silently drops every LATER addition to that file: when a producer rewrites
  a stable filename with more items (a per-day digest that grows as the day's runs append — measured 804 →
  1,167 items inside a single day), the consumer reads it once on first sighting and never again, so the
  downstream store stops growing while the queue reports clean and every checker stays green. Record the
  content hash in the marker **and compare it** — storing the hash without comparing it is this same bug
  wearing a safety belt. The signature to recognise is a total frozen at a plausible number while the
  producer's own output keeps growing.
- **When a consumer selects on a threshold, check the corpus against that threshold before blaming
  the consumer.** A reader filtering `>= N` rows per item will look "picky" or "repeating itself"
  when in fact almost nothing in the store satisfies `N` — presence of the data is not availability
  to the selector. Compare the threshold against the real distribution (how many items clear it, and
  how stale those are) and report the reachable fraction; tuning the consumer's prompt or lowering
  the bar treats the symptom and hides the broken producer behind it.
- **Classify a "gap" count BEFORE reporting it — an unclassified gap overstates the damage and gets the
  audit discounted.** "N items are missing/unreachable" is a measurement of absence, not of breakage: the
  items are almost always a mix of genuinely defective, legitimately small, and never-measured, and
  folding them into one headline is false in both directions. A coverage audit shouted that **62.5% of a
  corpus was unreachable** when the real defects were a minority — most of the rest were items whose size
  was CORRECT for their source (a 45-second clip legitimately holds ~800 chars of speech), and a third
  bucket could not be measured at all. Derive the expected size from an INDEPENDENT measurement of the
  SOURCE (here: the source's own duration metadata x the corpus's calibrated rate, ~1,100 chars per
  minute of speech), never from the artefact being judged, then report the buckets separately — complete /
  legitimately-small / defective / unjudged — with unjudged counted as neither. The same discipline
  catches the opposite error: a "verified complete" total that only means "we never checked it".
- **Coverage that is invisible to its readers is treated as absent.** Once a checker has both a
  script and a spec/doc, the doc becomes the thing people read — so a check implemented and wired in
  code but missing from the doc gets reported as a monitoring GAP by the next reviewer, and you
  re-litigate a control that already works. Every check belongs in both places (signature it matches,
  window it scans, where its alerts go), and adding a check is a two-file change. The mirror matters
  just as much when triaging: before accepting "X is not monitored", grep the checker for X's failure
  signature **and** for the check's call site — reading the doc is not reading the monitor, and the
  most consequential finding in a review is exactly where this mistake hides.

- **A scheduled gate must select only work it has not already judged — consult the VERDICT store in the
  selection query.** A gate that picks its items by recency ("the newest N with usable input") and never
  asks its own ledger re-processes the SAME items on every tick: identical verdicts, identical failures,
  and a per-run bill that repeats forever while producing nothing new. It is invisible because every run
  looks busy and the verdicts look plausible. Worse, a verdict that means "needs a human" can never
  settle — the producer fails the same way each night, so the row stays pending and the cost recurs for a
  verdict that will not change. Exclude every item already carrying ANY terminal verdict (including the
  review-needed one), and require an explicit ledger edit to re-run one deliberately. **If a recurring
  job's selection does not consult its own verdict store, it is re-buying the same answer forever.**
- **A review FINDING is not a job FAILURE — do not wire a non-zero exit code to it.** Making a gate exit
  non-zero because items need review turns a permanent, legitimate condition into a permanently RED job:
  it fires every day forever, trains everyone to ignore it, and makes any chain-level assertor report the
  whole pipeline broken on a healthy run. The gate DID its job — it ran, produced verdicts, recorded
  them. Reserve the non-zero exit for a real failure of the job itself (crash, unhandled error) and carry
  the review queue in the output and the durable store instead. **Decide "did the job fail" separately
  from "did the job find something" before choosing an exit code** — conflating them is how a checker
  becomes noise, and noise is how the next real alert gets missed.
- **A batch job must be able to stop ITSELF before an outer timeout kills it.** A run SIGKILLed by a
  wrapper timeout reports a hard failure and **hides the work that already landed** — items processed,
  rows written, verdicts stored are all invisible behind one `exit 124`, so the same "broken" job gets
  re-diagnosed from scratch while its real output sits in the store. Give the job its own
  `--deadline SECONDS` that finishes the item in flight, prints how far it got, and exits 0; set the
  wrapper timeout comfortably ABOVE it. Pair it with per-item locking so the next tick resumes. **A job
  that cannot end cleanly cannot report honestly.**

## Alert-once discipline (standing conditions, baselines, watermarks)

A checker that compares against a stored baseline must persist that baseline on **every** run —
including the run that alerts. Persist it only on the success path and the monitor is born broken:
the first alert never advances the watermark, so the same historical failures re-fire on every tick,
the recipient learns to ignore it, and the alert is worth less than no alert at all. If you find
yourself writing `if healthy: save_baseline()`, that is the bug.

- **Separate NEW from STANDING, then alert on change only.** A fresh failure (a count regressing, a
  new failing record past the watermark) is news; a condition already reported is known — carry it in
  the baseline and stay quiet until it changes. Write the baseline unconditionally, after building
  the alert text, so one run both reports and advances the watermark.
- **A standing condition alerts ONCE, not daily.** An absent directory, an unconfigured connector, a
  permanently broken lane gets reported the first time it is seen and suppressed thereafter. A
  monitor that repeats the same sentence every day carries no information — it trains the reader to
  skip it.
- **Assert on counts that can only move when work really landed** (doc counts, row totals, a
  persisted fingerprint) and alert on REGRESSION, not on the absolute value. That is what turns a
  health check into a detector rather than a status echo.
- **Silent when healthy is the correct watchdog default** — and it is only safe because the failure
  path speaks (see failure mode 3). Empty stdout delivers nothing; a quiet monitor and a dead one
  look identical, so prove the failure path prints before trusting the quiet.
- **On a sub-hourly cadence, a standing condition needs TRANSITION gating, not just a persisted
  baseline.** A watermark is not enough when the checker runs every minute: every tick that prints its
  failure block sends a message, so one backend outage becomes hundreds of chat messages and buries
  everything else in the channel (observed: ~416 delivered in seven hours, one per tick). Track the
  last REPORTED state plus its reason and emit only on change — one line on the first failure, silence
  while the identical condition persists, one line on recovery — and put the running counts in a slower
  scheduled digest instead. Prove the quiet path by watching a known-bad window stay silent; a checker
  you have only ever seen shout is not a checker.
- **A watermark that lags BY DESIGN is not a dead producer.** Some stores return the last REAL write time
  on their no-op path, so a healthy skip leaves the timestamp unchanged for days at a time (monthly
  reference data, weekly publications). Before calling a lagging watermark an outage, find out from the
  writer whether the no-op path is specified to return the stored timestamp, and corroborate with
  something only a real write moves (row count, fingerprint, offset). Escalate when those disagree —
  never on the date alone.
- **When asked for "a P1 if it breaks tomorrow", the deliverable is an ARMED CHECK, not an assurance.**
  Create a one-shot job scheduled before the next window: it returns exactly `[SILENT]` when healthy and
  otherwise emits the full incident (failure signature, streak length, the evidence, top causes with the
  first diagnostic step), delivered to the chat that asked. Answer the same-day verdict as well — a
  promise in prose cannot be verified, a job can.
- **"Nothing to do" is not one state — resolve it against the system of record before reporting it.**
  A checker that finds no work cannot distinguish an empty queue from work that never entered the queue
  (a producer that enqueues only when a prerequisite field is set, a paused or refusing worker, a
  target that is unreachable). Answering "no work, so nothing happened" from the checker's own output
  is how a silently un-enqueued backlog gets declared healthy. Read the queue table, then the
  producer's enqueue CONDITION — and when a case exists with no work item, name the missing
  prerequisite rather than calling the consumer broken. Recipe: `references/queue-backlog-verification.md`.

**Repairing the data is half the fix; the missing MONITOR is the other half.** When a store or write
path is found broken with nothing alerting — a connector that failed 100% of its writes for weeks
while every scheduled job reported `ok`, a collection that stopped decoding — treat "build the check"
as part of the SAME task, not a follow-up. A repaired silent failure with no detector is simply
scheduled to happen again. Pair the repair with a check that would have caught it, and prove the
check fires by feeding it a known-bad input.

## Assert the CHAIN, not the legs

A pipeline built as independent time-sequenced jobs cannot report whether the CHAIN worked. Each leg
reporting only to itself means a dead leg is indistinguishable from an idle one — both are simply quiet
— so failures rot unseen (observed: five legs red, one for eleven days, with nothing surfacing it, while
several of the survivors had stopped producing anything at all).

- **Two conditions per leg, and freshness alone is not evidence:** it RAN inside its cadence (`last_run_at`
  within the expected interval) **and** its EFFECT exists (the artefact it writes is present and newer
  than the input it reads; the store it feeds has advanced). A stage can run on schedule every day and
  produce nothing — that is the producer-freshness trap one link up, seen from the pipeline's side.
- **Build ONE assertion job that runs after the last leg** and reports the whole chain in a single block,
  silent when healthy (watchdog default). It should also RUN the child checkers (contract/health/reconcile)
  and check the terminal store for a regression, so one message carries the entire verdict.
- **Fold the standalone child checkers INTO the assertor rather than leaving both scheduled.** One
  consolidated status beats N independent ones that each land somewhere different; the child jobs stay
  available for manual re-run. When you fold a job in, say so in its paused reason — an unexplained
  paused job reads as a coverage gap to the next reviewer.
- **Never quiet a failing leg by adding it to an accepted baseline.** Fix the leg or record an explicit,
  NAMED exception with a reason; an accepted failure with no reason is a monitor that has been trained
  to lie.
- **Prove the assertor fails on the real break.** Its first run should be against a chain with a known-bad
  leg and it must name THAT leg; a chain assertion you have only ever seen pass is not a check.

## Recurring-item monitors (dedupe state, watchlists, vulnerability/competitor feeds)

When a checker remembers what it has already reported, two decisions decide whether it stays
trusted: what counts as NEW, and what counts as STILL TRUE.

- **Freshness decides "is this news"; truth decides "is this still on fire".** An item older than
  the lookback window is not news — but if it describes a condition that is still true on the
  watched system, it must be re-reported EVERY run until resolved, or the window silently hides a
  live problem the moment the item ages out. Keep the fetched horizon wider than the reporting
  window (pull a year of advisories, report the last week, but always re-surface anything that
  still matches the machine) and make the suppression rule explicit in code, not in your head.
- **Prove the negative instead of tolerating noise.** If the checker has enough data to show an
  item does NOT apply (installed version outside the advisory's range, target not in the changed
  set), downgrade it and say so — "not affected" — rather than leaving a scary line in the list.
  A list padded with things that do not apply is a list nobody reads, and reading it is the only
  control that exists.
- **A keyword hit is not entity identity.** A search or feed match proves the WORD appeared, not
  that it is the same product — a keyword sweep for an OS name returns every third-party app that
  runs on it. Tag those hits as unverified in the output and cap their severity below the rows you
  can attribute from a first-party source, so a coincidence can never outrank a confirmed item.
- **Separate signal from housekeeping in the headline counts.** Version-update notes, changelog
  feeds and vendor status incidents are not findings; count and section them separately, or the
  "N new items" number becomes meaningless and the reader stops believing the one line that matters.
- **A channel release post is housekeeping too.** "ChromeOS LTS", "Android", "early stable" and similar
  channel promotions in a release feed are notes about builds nobody here runs; promoting them into the
  findings bucket is the same error as counting changelogs.
- **Only a RANGE CHECK can prove applicability, so a headline's severity must never lead.** An advisory
  with a vulnerable range compared against a detected installed version yields a provable "affects this
  machine". A news/RSS item carries neither range nor version, so its CRITICAL/HIGH label is the
  headline's opinion — never raise one to P1 without a primary advisory behind it, and always rank the
  range-checked bucket above the feed bucket. Broad `<vendor> vulnerability` queries make this concrete:
  they return other vendors' products under our vendor's name often enough that the top of the digest is
  regularly unrelated software.
- **When asked "why haven't we acted on these?", answer with the CLASS, not the count.** Walk the items
  and say which are range-verified, which are version drift, and which are keyword matches — then state
  plainly that triage-driven-by-headline spends attention on products we do not run while genuine
  version drift sits unread in the informational section. That answer is the deliverable; a restated
  list is not.

## Diff-gated monitors (wake only on change)

A monitor that hashes its source's output each tick and only wakes the reasoning agent when that
output changes. Cheap and quiet by design — so the gate itself has two failure modes: it fires every
tick, or it stops firing and nobody notices.

- **Emit byte-stable output.** No timestamps, no "now", no run counters, no iteration over an
  unordered set — and **no trailing newline**. `print("\n".join(lines))` emits one; if the engine
  stores a stripped baseline the bytes then differ on *every* tick and the monitor fires forever.
  Use `sys.stdout.write("\n".join(lines))`.
- **Prove suppression before trusting it**, in this order: run the source twice and `cmp -s` the two
  outputs; compare the engine's stored baseline hash against a fresh run's hash; then trigger one
  real tick and require the engine to report that the change-gate suppressed the agent run. A
  monitor you have never watched stay quiet is a monitor you have not tested.
- **The first tick is the baseline and it still runs the agent** — which may then answer `[SILENT]`
  and deliver nothing (failure mode 4). If a baseline message is wanted, ask for it explicitly in
  that run's prompt and verify it landed.
- **A fetch or parse failure must produce a DIFFERENT output**, not identical quietness — emit a
  distinct line (`RESULT: FETCH_FAILED`) so the change itself wakes the agent, and tell the waking
  prompt that an unverifiable watch is the finding. A monitor that goes silent when its source
  breaks is worse than no monitor.
- Page-specific capture traps, baseline storage and the waking prompt's language rules:
  `references/page-change-monitors.md`.

## Triage order for a reported failure

1. Read the checker's own output — what did it actually assert, and on which response?
2. **Check whether the ground moved under it.** Compare the last GREEN run's timestamp with
   the host's launch time and the deploy history. A checker that was green and is now failing
   on infrastructure it merely runs ON is usually a replacement, not a regression: a
   hand-installed dependency, a pinned instance id and a warm cache all disappear with the
   instance, and the failure then looks like a code or credential bug. Only a checker whose
   own host is unchanged is a code problem.
3. Read the DURABLE state and compare its timestamps against the alert's run time.
4. Only then inspect the target system's logs and health.

- **Attribute a failure to the right CALL SITE by reading LINE ORDER, not by what the message says.** A
  job that makes several distinct calls (a producer call, then a verifier call on a DIFFERENT provider, a
  retry chain) logs an error that does not name which call produced it — "the job is broken" is not a
  diagnosis, and fixing the wrong call wastes a full run and leaves the real failure untouched. Use the
  per-call marker each site already prints (key source, endpoint, pass name): the marker line immediately
  PRECEDING the error names the culprit, and the absence of one before a retry tells you the same call
  was retried rather than a different one being tried. Verified the hard way: two consecutive fixes were
  aimed at the producer while every error line sat directly under the verifier's own marker.

- **Many jobs failing with the identical error inside one window is ONE event, not N bugs.** Cluster
  the failures by error string and timestamp before debugging any single one, and where they share a
  model provider, probe that provider directly — with BOTH a small and a large payload, since
  long-context runs fail in ways a tiny probe never reproduces. Then fix the absent resilience rather
  than the past blip: automatic failover only happens if a fallback provider/model is actually
  configured, so an unfailover'd fleet converts one transient upstream outage into a whole morning of
  dead jobs. Verified 2026-09-15: 8 agent-driven crons (5:02–6:45 window) all died with `RuntimeError:
  [Errno 32] Broken pipe` after 3/3 attempts against the primary DIRECT provider — one event, eight
  red jobs. Note the transport-failure path only falls back at `retry_count >= 2`
  (`agent/turn_recovery.py`), and only if the chain is non-empty. Use the canonical key
  `fallback_providers` (legacy `fallback_model` is merged second and is usually absent); the
  finding is `hermes fallback list` resolving to **zero hops**, not a "Config key not set" on the
  legacy name. Prove every hop responds with a live call before trusting it.
- **Verify the RESOLVED chain, never the config text — a chain can resolve to zero hops.** The same
  rule as any other value probe: a failover setting that *reads* as configured can be silently inert.
  Entries that are not dicts (a JSON string, or bare provider names) are dropped by the loader, so
  `fallback_providers: '["openrouter","deepseek"]'` contributes nothing while looking like
  protection. Load the config and print what the runtime will actually try — an empty list means one
  provider outage takes the whole fleet at once. Chain shapes, the multi-hop form and a live
  two-stage probe (plain completion **plus** a structured tool call — an agent fallback that cannot
  emit tool calls is not resilience) live in `llm-cost-routing` → "Hermes failover chain".

Never start at the last step. "The cron says the service is broken" is a claim, not evidence —
and neither is "this worked last week", when the machine underneath it was rebuilt on Tuesday.

## Independent-model checkers (verifying model-produced records)

When the thing being checked was itself produced by a model — extractions, summaries, categorised
records — the checker must be a different instrument, not a second opinion from the same instrument.

- **A self-check is not a check.** Use a different model FAMILY for the verifier, and prefer a CHEAP
  independent model over the strongest model in the producer's own family: same-family agreement is a
  foregone conclusion, so it is not evidence. Verify the family split at the routing layer (a configured
  fallback that silently resolves to the producer's family undoes the independence).
- **Ask the verifier TWO questions: are these claims supported, and WHAT MATERIAL POINT IS MISSING.** The
  second question is the one that earns the cost. A pass where every extracted quote verified (14/14)
  still surfaced three material points the producer had missed — found only because the checker was asked
  to look for ABSENCE, not to confirm presence.
- **Gate in code whatever code can decide.** Verbatim-quote containment is a token-window membership test
  (fold typography to ASCII, compare a contiguous ~12-token window): exact string equality false-rejects
  genuinely verbatim quotes because models normalise curly quotes and dashes, while a paraphrase still
  fails the window test, so nothing is lost. A gate that rejects good records gets switched off — that is
  how a control dies.
- **Keep THREE states per record, with provenance: verified/locked, needs-human, errored.** Record which
  model verified, how many rounds, and what stayed unresolved; lock only on a clean pass, and never let
  "could not finish" default to done. A verifier that cannot fail is not a control.
- **Budget for reasoning tokens before calling an empty response a failure.** A reasoning model given too
  small an output budget returns EMPTY content with `finish_reason=length`, which reads as "the model said
  nothing". Retry on empty content with a larger budget (8k -> 16k -> 32k) before concluding anything, and
  never persist the first empty answer as a verdict.
- **Ask the round-2 fix for the DELTA only.** Re-requesting the full merged list after a partially failed
  round returns truncated JSON; requesting only the missing items keeps the output short, lands cleanly,
  and merges in code.

## Test a checker without touching production

Exercise the verification function against scripted responses instead of hitting the live
system — extract the real function from the script with `ast` so the test cannot drift:

```python
import ast, pathlib
src = pathlib.Path(script).read_text()
fn = next(ast.get_source_segment(src, n) for n in ast.parse(src).body
          if isinstance(n, ast.FunctionDef) and n.name == "_verify_enqueued")
calls = {"n": 0}
def _post_sync(url, token, timeout, force=False):
    i = min(calls["n"], len(responses) - 1); calls["n"] += 1
    return 200, responses[i]
ns = {"time": type("T", (), {"sleep": staticmethod(lambda s: None)})(),
      "print": lambda *a, **k: None,
      "LONG_TIMEOUT_DS": {"long-dataset"}, "_post_sync": _post_sync}
exec(fn, ns)
```

Assert all four cases, every time:

1. verifies on the real advance signal (e.g. acknowledgement → acknowledgement → advanced),
2. stays BOUNDED when the job never completes (no infinite loop),
3. accepts a genuinely synchronous success,
4. **never passes on a bare acknowledgement** — the invariant that stops fake PASS.

**For a pattern-set monitor, prove the new signature in BOTH directions using the monitor's own
classifier.** Import the module and call its real formatter/classifier rather than re-implementing
the match in the test — a re-implementation proves your copy works, not the shipped code:

- a synthetic line carrying the real failure string → exactly one alert, at the expected severity;
- **a negative control**: a success-shaped line carrying the same job/component name → ZERO alerts;
- **a lifecycle negative control**: a startup/shutdown banner that lists the component's identifiers →
  ZERO alerts (this is the case a naive substring match gets wrong, so it must be in the proof set);
- **both together**: the banner *plus* a genuine failure line → still exactly ONE alert.

Drive the **window/selection function itself**, not only its formatter, by replacing its IO wrapper
inside the imported module (`m.aws_cli = lambda *a, **k: {"events": [{"message": line}, …]}`) and
calling the real entry point — that exercises window arithmetic, classification and alert construction
in one shot, and it is the only way to catch a false FAIL that the classifier's own unit test would
pass. Probe the fix, then read the final message the checker *would* have sent, and quote it.

Put only the precise failure string in the alerting set and leave the bare component/job name in the
display-only set — alerting on the job name alone fires on every healthy run of that job, which is
how a new signature gets muted within a week. When the same failure class already has a dedicated
window-scoped check, add the signature to the generic scan as well so it is caught outside that
window; keep the two paths' coverage written down side by side.

## Related

- `amlhive-prod-monitor` (user-owned) — AMLHive prod monitor; holds its own alert severity
  model and EC2 auto-discovery notes.
- `website-uptime-monitor` — HTTP/SSL probing; same discipline applies to "is it up" checks
  (a single 5xx during a deploy is not an outage).
- `references/refdb-readonly-probe.md` — read-only serving-store probe recipe: the concrete
  "establish truth" step for a reference-data sync.
- `references/queue-backlog-verification.md` — the same "establish truth" step for a BACKGROUND WORKER
  with no read API: proving whether work was enqueued, claimed and completed, the enqueue-condition
  and schema-drift checks, and the psycopg2 probe traps.
- `references/fleet-value-audit.md` — the periodic audit ABOVE the individual checker: enumerate the
  job registry, per-job freshness, the overlap/coverage-gap map (a disabled job is not coverage),
  keep/fix/merge/disable verdicts, the "same wrong item every run" classifier-vs-truth diagnostic, and
  the contract for the recurring status message itself.
- `references/feed-backed-monitors.md` — when the checker's input is a search/news feed:
  pushing recency into the query, the `items_seen`/`items_in_window`/`hits` liveness contract,
  precision gating on entity names, and rotating a large watchlist.
- `references/page-change-monitors.md` — when the input is a page that changes in place: proving a
  capture is substantive, diff-gated byte stability, baseline discipline, and the waking prompt.
- `credential-exposure-remediation` — the follow-up when an audit surfaces a hardcoded secret in a
  checker or its cron prompt: containment vs rotation, the no-VCS backup, the literal sweep, and the
  rotation handover.
- `pluto-pipeline-orchestration` — where the fleet's various checkers sit in the schedule.
