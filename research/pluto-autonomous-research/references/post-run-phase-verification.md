# Phase Verification — Post-Run Guardrail (Full Detail)

Full detail behind the "Phase Verification" summary in `SKILL.md`. After
the inline pipeline completes (~5:25 AM AEST), verify all phases actually
produced output. **Do not trust `last_status: ok` alone** — phases can
silently produce zero output while reporting success.

## Contents

- [Verification checklist](#verification-checklist-run-one-liner)
- [Common silent-failure patterns](#common-silent-failure-patterns)
- [Remediation for missing phases](#remediation-for-missing-phases)
- [Mempalace feeder verification](#mempalace-feeder-verification)

## Verification checklist (run one-liner)

```bash
echo "== Pipeline Phase Verification =="
echo "1. Research JSON: $(ls -la ~/.hermes/research_outputs/research_$(date +%Y-%m-%d).json 2>/dev/null | awk '{print $5\" bytes\"}')"
echo "2. Morning Briefing: $(ls -la ~/.hermes/research_outputs/morning-briefing-$(date +%Y-%m-%d).md 2>/dev/null | awk '{print $5\" bytes\"}')"
echo "3. Mempalace Feed: run --status check"
echo "4. LinkedIn Ideas: $(ls -la ~/.hermes/research_outputs/linkedin-ideas_$(date +%Y-%m-%d).md 2>/dev/null | awk '{print $5\" bytes\"}')"
echo "5. Email Delivery: check Python smtplib return value"
```

## Common silent-failure patterns

- Research JSON exists but has 0 findings → RSS queries returned empty
- Morning briefing exists but is stale (from previous day's data) → Phase 2 synthesis loaded wrong file
- Mempalace feeder not invoked → the inline step skipped Phase 3 (common — see June 5, 2026: feeder not run despite all other phases ✅). Fix: run feeder manually, add it to the inline cron script.
- Voice overview MP3 not generated → voice cron ran but found no research JSON to read

## Remediation for missing phases

- **Missing research JSON** → Run Phase 1 inline (Google News RSS + Python synthesis)
- **Missing mempalace feed** → Run Phase 3 manually with `pluto_mempalace_feeder.py`
- **Missing email** → Run Phase 9 manually with Python smtplib (the himalaya auth.cmd fallback)
- **Missing LinkedIn ideas** → Run Phase 8 manually with `linkedin_ideas_generator.py`

If 2+ phases are missing simultaneously, regenerate the full briefing: re-run the research pipeline from Phase 1.

## Mempalace feeder verification

(must be run separately — the `--status` flag shows chamber state, not last-feed state):
```bash
# Check if today's topic was stored
/home/habib/.hermes/venv/bin/python3 /home/habib/.hermes/scripts/pluto_mempalace_feeder.py --status 2>&1 | grep -A3 "$(date +%Y-%m-%d)"
# Reliable check: look for today's date in chamber finding timestamps
/home/habib/.hermes/venv/bin/python3 -c "
import json, datetime
d = json.loads(open('/home/habib/.hermes/research_outputs/research_$(date +%Y-%m-%d).json').read())
print(f'Findings in JSON: {len(d.get(\"findings\",[]))} stored for {d.get(\"topic\",\"unknown\")}')
"
```
This second check validates that the JSON file itself is non-empty and correctly structured — a prerequisite for the feeder to work.

**Pluto is the sole operator of the full morning briefing pipeline as of June 4, 2026.** This includes research, synthesis, LinkedIn/blog ideation, voice overview, email delivery to hhsiddiqui@gmail.com + admin@harishabib.au, and Telegram delivery. **No Gumby forwarding — Pluto delivers directly to Haris.** Gumby is fully retired from briefing duties. All 9 cron jobs plus inline briefing/email phases are Pluto's responsibility.
