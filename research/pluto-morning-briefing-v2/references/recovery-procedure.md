# Morning Briefing Recovery Procedure

When the scheduled pipeline fails to produce the morning briefing, follow these steps.

## Step 1: Diagnose

```bash
ls -la ~/.hermes/research_outputs/morning-briefing-$(date +%Y-%m-%d).md
```

If missing, check which upstream outputs exist:

```bash
ls -la ~/.hermes/research_outputs/research_$(date +%Y-%m-%d).json
ls -la ~/.hermes/research_outputs/synthesis_$(date +%Y-%m-%d).json
ls -la ~/.hermes/research_outputs/actions_$(date +%Y-%m-%d).json
ls -la ~/.hermes/research_outputs/competitor_intel_$(date +%Y-%m-%d).json
```

## Step 2: Check cron status

```bash
# In Pluto session: cronjob action=list
```

Look for failed crons. Common failures:
- `b0de180cec84` (Morning Research): broken pipe, RSS curl failures
- `c23dc3f73e2d` (Git Repo Sync): auth/permission issues

## Step 3: Dry-run the improver

```bash
cd ~/.hermes
python3 scripts/briefing_improver.py --dry-run
```

This shows what the briefing WOULD look like with available inputs. If it's too sparse, consider:

### Minimal input scenario (only competitor + synthesis)
If `research_YYYY-MM-DD.json` is missing but synthesis + competitor exist:
- The improver reads cross-domain patterns from synthesis
- Competitor watch section appears if relevant
- Checklist will have cross-domain items (abstract but useful)
- The briefing will note lighter-than-usual signals

### Zero input scenario (nothing exists)
- Run synthesis manually: `python3 scripts/cross_chamber_synthesis.py`
- Run competitor intel manually: `python3 scripts/competitor_intel.py`
- Then dry-run the improver again

## Step 4: Generate and deliver

```bash
cd ~/.hermes
python3 scripts/briefing_improver.py
```

The script now prints the full briefing to stdout (for Telegram delivery) AND saves the markdown file.

## Step 5: Deliver

Copy the printed briefing and send to Haris via Telegram DM. Include a note if the briefing is lighter than usual due to upstream failures.

## Step 6: Root cause fix

After recovery, fix the root cause so tomorrow's pipeline doesn't fail the same way. Common fixes:
- Broken pipe in RSS pipeline → add retry logic or error handling
- File naming mismatch → update glob patterns in briefing_improver.py
- Cron not running → check schedule, enable if paused

## Recovery Record (June 9, 2026)

**Failure:** Morning Research cron (`b0de180cec84`) errored with `RuntimeError: Broken pipe`. No `research_2026-06-09.json` generated.

**Available inputs:** synthesis_2026-06-09.json (371 docs), actions_2026-06-09.json (20 items), competitor_intel_2026-06-09.json (4 signals), podcast_insights.json.

**Action:** Dry-ran the improver (found 0 signals — bug in signal extraction). Fixed 3 bugs in briefing_improver.py (synthesis glob, multi-source extraction, competitor display). Regenerated and delivered.

**Outcome:** Clean briefing delivered. Briefing improver cron created (`7cc81d64613a`, 5:20 AM) to prevent future gaps.
