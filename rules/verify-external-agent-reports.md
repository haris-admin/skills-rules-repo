# Verifying live-state and absence claims (all agents)

Applies whenever any report — from another agent/tool, or self-generated — makes a "live state,"
"critical/urgent," or "X is missing/absent from prod" claim, before that claim is accepted,
refuted, or acted on (e.g. filing a `prod_issues/` doc, proposing a hotfix).

## Why this exists

**17 Jul 2026:** A Cursor-generated assessment report claimed prod was stuck on a stale image with
a DB migration head mismatch. A live snapshot check (`curl .../version`, `alembic current`) showed
everything matching — first-pass conclusion was "this claim is fabricated." **That conclusion was
wrong.** `prod_issues/issue-151` (not checked before drawing that conclusion) showed the identical
symptom happened for real the day before, was fixed *forward* rather than at the root cause, and
was `REOPENED`. The live snapshot only looked clean because no EC2 instance had been replaced
since the last manual fix — the underlying trigger (missing `ecr:DescribeImages` IAM grant causing
a silent fallback to a frozen ECR `:latest` tag) was still present and would recur on the next
instance replacement.

**Same day, self-inflicted instance of the identical pattern:** an independent investigation in
that session flagged 4 `STRIPE_*_PRICE_ID` secrets as "missing from prod" based on checking AWS
Secrets Manager alone, and drafted a `prod_issues/` doc plus a Tier-1 hotfix plan on that basis. It
was wrong: this backend's config is assembled from **two merged stores** (Secrets Manager + an SSM
`plain_env` JSON parameter), and the 4 keys were in the second store the whole time, correctly
loaded into the running container. Caught only because the user pushed back ("SSM Parameter Store
has these values. Why are they missing?") instead of accepting the finding.

**The lesson generalizes beyond "external reports":** a self-generated finding is not exempt from
the same scrutiny an external tool's report gets. Some claims describe *conditions* ("will fail on
X trigger"), not permanent states — a clean point-in-time check doesn't disprove those; only
history and root-cause status do. And "absent" claims specifically need every plausible store
checked, not just the first one queried.

**8 Aug 2026, the canonical "external agent report" case this rule's title describes:** Pluto
pasted a summarized report claiming YourApp's ASIC reference-data sync had **not** ingested since
24 Jul, with a root-cause theory (the change-detection fingerprint never changes month-to-month)
and a proposed fix (`force=true` to bypass it). Both the absence claim and the root cause were
**false** — a code read showed the fingerprint includes the request URL, which does change monthly,
so it couldn't be stuck the way described. Pulling the *actual* `audit_entries` rows (not a
paraphrase) showed three real `SYNCED` ingests had happened since 24 Jul (27 Jul, 1 Aug, 3 Aug),
with row counts genuinely increasing each time — the report's own "first run: 3,308,701 rows on 24
Jul" didn't even match the real first logged row (3,978,184, already `NO_CHANGE`). The same
transcript also claimed an audit-actor rename ("Hivey → Nectar") was "✅ complete"; nothing in the
repo's git history matched that change anywhere. Had the proposed `force=true` been run on the
strength of the summary alone, it would have re-downloaded ~400MB for no reason and obscured the
real picture. **A structured, confident-sounding report from another agent is still a claim, not
evidence — verify against raw source data (here: real `audit_entries` rows + a live HEAD check of
the actual upstream file) before accepting or acting on it, even when it cites specific dates and
row counts that make it sound authoritative.**

**22 Aug 2026, a new source and a new claim type — same rule:** a separate multi-agent business-
opportunity tool the user runs (personas "Sol"/"Lumen", not part of this Claude Code session and
not reachable from it — checked via `ListAgents`, confirmed no such agent, no `hermes` binary, no
`profiles/sol/` path anywhere on the machine) fed in two reports proposing product work. Mixed
accuracy, same as every prior case here: the report's headline claim (an AGDIS regulatory deadline)
was independently corroborated via WebSearch and matched a source already in this repo; but its
specific supporting citation — *"you already have draft content in `docs/content-drafts/TASK-041-
...md`"* — was **fabricated**: neither that file nor the `docs/content-drafts/` directory has ever
existed in this repo, at any point in git history. A second claim (an existing "needs human review"
gate in a specific schema) was also inaccurate as stated, though it was describing something real
under a different name (`05m-ai-extraction-review-staging`) once traced. **A confident external
report citing a specific repo file path is not evidence the file exists — `ls`/`git log --all --
<path>` it before treating the citation as grounding**, the same discipline this rule already
requires for a live-state or absence claim. Partial accuracy is the realistic expectation for this
class of report, not a reason to either fully trust or fully dismiss one — verify each citable
claim independently before drafting anything on top of it.

## Rules

1. **A passing live snapshot only rules out "currently manifesting," not "real and recurring."**
   Before calling a claim fabricated, grep `prod_issues/` (and related OpenSpec changes) for a
   matching incident.
2. **An "X is absent/missing" claim needs every plausible config store checked**, not just the
   first one queried — this app has at least two (Secrets Manager + SSM `plain_env`); check both
   before concluding a variable is truly absent.
3. **Mark each claim in a three-way state, not binary:** CONFIRMED / REFUTED / CONDITIONAL-TRUE
   (real but not currently manifesting — will recur on a known trigger). A binary CONFIRMED/REFUTED
   forces conditional-but-real bugs into "fabricated."
4. **This applies equally to self-generated findings.** An agent's own investigation drafting a
   `prod_issues/` doc or a hotfix plan on an "absent" or "broken" finding gets the same rigor as
   grading someone else's report — check history, check every store, before writing the incident
   doc or touching production.
5. **Before filing a `prod_issues/` doc or proposing a hotfix on an "absent" finding, ask:** have I
   checked every place this could be configured, and does `prod_issues/` already have a matching
   incident that tells me whether this is new or a known recurrence?
6. **A specific repo file path cited by an external report is a claim, not a citation, until
   checked.** `ls`/`git log --all --oneline -- <path>` it before drafting anything on the assumption
   it exists — this applies whether the report is about live infra state or a business/product
   opportunity; the claim type differs, the verification discipline doesn't.

## Related

- `prod_issues/issue-151` — the REOPENED image/migration-skew recurrence that looked refuted by a
  clean snapshot
- `prod_issues/issue-157` — a claim ("SG open to 0.0.0.0/0") that was real but already fixed by
  check time — the other failure direction (true claim, stale by check time)
- `docs/pluto_asic_ref_db_sync_instructions.md` — 8 Aug 2026 Pluto false "hasn't ingested since Jul
  24" report; the fix that followed (tracking `sync_at` correctly) is documented there
- `docs/agent_rules/prod-issue-numbering.md` — where to log a finding once verified
