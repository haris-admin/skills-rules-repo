# Fleet value audit — are the checkers themselves still earning their place?

The SKILL.md rules tell you how to verify *one* checker's verdict. This file is for the periodic
question that arrives above them: *"audit all the recurring jobs — are they still giving us the right
value, and why does the same wrong item keep arriving?"*

**Read-only.** An audit proposes; it never enables, disables, edits or reschedules. Every state
change is a separate, human-approved action — say so in the report.

## 1. Enumerate from the registry, never from the docs

Schedule listings and prose counts drift silently. The registry is the fleet:

```bash
python3 - <<'PY'
import json, os
d = json.load(open(os.path.expanduser("~/.hermes/cron/jobs.json")))
jobs = d.get("jobs", d) if isinstance(d, dict) else d
print(f"total: {len(jobs)}  enabled: {sum(1 for j in jobs if j.get('enabled'))}")
for j in sorted(jobs, key=lambda x: str((x.get("schedule") or {}).get("expr", ""))):
    s = j.get("schedule") or {}
    print(f"  {str(j.get('id',''))[:12]:<12} | {str(j.get('name',''))[:50]:<50} | "
          f"{str(s.get('expr') or s.get('display') or '')[:20]:<20} | "
          f"enabled={j.get('enabled')} no_agent={j.get('no_agent')}")
PY
```

Report the real count against whatever the docs claim — if the fleet is in the dozens, say the
number up front so the human can scope the audit.

## 2. Read what each job EXECUTES, not what it is called

Take `script` / `prompt` / `deliver` from the registry and open the target. **Names drift from
behaviour**: a job called "…Monitor" may be a prompt with no script; a name may carry a platform and
time that no longer exist. Audit the artifact.

## 3. Freshness per job, not status per job

For each *enabled* job, ask whether its output is newer than its own cadence:

- **silent** — enabled, scheduled, no output within a multiple of its period;
- **never ran** — `last_run_at` null while enabled (scheduler-level, not a script bug);
- **erroring** — non-`ok` status, always cross-checked against the output file, never the status alone.

## 4. Overlap and coverage-gap map

Group jobs by **target system + cadence family**:

- sibling jobs at fixed slots on one system may be the intended design or redundancy left by a
  migration — decide which is authoritative and say what the other adds;
- **a disabled job is not coverage.** When one of a pair is disabled, whatever only IT covered is now
  unmonitored — list those gaps explicitly instead of counting the disabled job as present;
- two jobs differing only by delivery target are a MERGE candidate, not two findings.

## 5. Standard compliance

- A job that commits or pushes to a **protected/shared branch** — agent check-ins belong on the agent
  branch, and a job doing otherwise breaches the branch standard silently.
- A job writing outside its own lane (another product's repo, another agent's skill tree).
- A job whose configured output path no longer exists: it "succeeds" while writing nothing.

## 6. Verdict per job, then a summary

Exactly one of **KEEP / FIX / MERGE / DISABLE** per job, each with a one-line reason. Signals: nobody
reads the output (DISABLE), two jobs publish the same number (MERGE), the thing it watches no longer
exists (DISABLE), it errors on the same input every run (FIX).

Lead the report with counts per verdict and the **top 5 fixes ranked by value** so the human can act
without reading every row.

## 7. "The same item keeps arriving" — classify before fixing

Identical repetition is one of two things, and the fix is completely different:

1. **Correct repetition** — the condition is genuinely still true; the checker is working. The defect
   is in *presentation*: every repeated item needs a freshness timestamp and first-seen age so
   "unchanged" is distinguishable from "the job stopped running", and an item already acknowledged or
   resolved must stop re-raising at incident severity.
2. **A classifier defect** — the same false verdict from healthy input, every run. Find it by reading
   the **matched line and the classifier**, never the report: a pattern that matches inside a longer
   identifier, or a lifecycle banner that merely lists component names, fires forever on a healthy
   system while looking plausible. Apply the SKILL.md rules (precise signature only, word-boundary
   anchoring, lifecycle-line exclusion, both-direction proof) rather than tuning thresholds.

Check the reverse too: an alarm whose metric stopped being published emits the same "no datapoints"
line forever. That is a **monitoring gap** with a named owner — never an incident and never an
all-clear — and it gets its own section.

## 8. If the audit also drafts the recurring status message

Hold it to four contracts:

- four visibly distinct states — **real incident / degraded / monitoring gap / informational** — and
  never render a metric it could not read as healthy (`CPU: N/A` beside a ✅ is a lie of omission);
- **freshness timestamps** on any "up to date" claim, so a stalled job cannot read as a quiet one;
- **one stated evidence requirement per severity**, so a future substring match cannot raise a P1;
- **no unbounded repetition** — state how an acknowledged item is shown, and make it disappear when it
  actually clears.

## 9. When the human authorises ACTING on the verdicts

The audit stays read-only (§ header). This section is the separate, explicitly-authorised follow-up —
the human says "fix these" and the state changes start. Four rules, all about making that reversible.

- **Fix the repetition instead of removing the slot.** When sibling jobs publish the same finding four
  times a day, the tempting "merge" is deleting three slots — but that is a **coverage reduction**, and
  reducing monitoring cadence needs its own explicit dated human decision, not a tidy-up. Implement
  **delta reporting** in the judge instead: an item already reported in an earlier slot of the same day
  moves to a standing section carrying its first-seen age, while anything genuinely new still alerts
  immediately. Prove BOTH halves — a repeat gets demoted *and* a fresh failure still raises — because a
  change that only silences is a disarmed monitor. State in the report that no slot stopped running.
- **Disable, never delete.** Set `enabled: false` and keep the job in the registry, so every change is
  a one-field revert and its schedule, prompt and history survive for the next reader. Record the reason
  in the job's own description field, not only in your report.
- **Back up the registry with a timestamp BEFORE the first edit, and hand back the restore command.**
  `cp jobs.json ~/.hermes/backups/jobs_$(date +%Y%m%d_%H%M%S).json` and print the exact one-liner that
  puts it back. A cron registry has no git history of its own, so this copy is the only undo.
- **Prove the snapshot really holds the PRE-EDIT state before you trust it as the undo.** Parse the
  backup and assert the jobs you are about to disable are still `enabled: true` in it — a snapshot taken
  after a partial edit restores the damage instead of repairing it, and the restore command looks
  identical either way.
- **Prove ONLY the intended jobs changed, by diffing the live registry against that snapshot.** Assert
  the job count is unchanged (nothing was deleted) and that the set of flipped `enabled` values is
  exactly the ids you authorised, then list any change you did not ask for as a defect. A delegate
  working through a batch of verdicts can flip neighbours, and a state-diff is the only evidence that
  separates "the two you asked for" from "the two you asked for plus three".

- **One writer on the registry, and report before/after per job.** Queue the change behind any run that
  also edits that file (an audit pass rewriting prompts, for instance) — concurrent writers corrupt it.
  Then report each job's id, name, previous state, new state, and what you deliberately left for the
  human (test-runner consolidations, anything destructive, anything whose removal would lose coverage).
