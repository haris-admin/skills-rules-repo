# Monthly strategy report: After-Action format + renderer lessons

## After-Action heading (user-requested format, Aug 2026)

For the "Next 7 days" section of the AMLHive monthly strategy report, Haris
wants the production after-action email style, NOT a plain "Next 7 days"
heading. Canonical format (verbatim example from user):

```
## AMLHive Production After-Action — v0.5.69 (backfilled 1 Aug 2026)
- **Day 1:**
  - Confirm the measurement owner and source-of-truth systems.
  - ...
```

Implementation in `pluto_monthly_strategy_job.py` `markdown_report()`:

- Heading reads `## AMLHive Production After-Action — v{aa_version} (backfilled {aa_backfill})`
  where `aa_version` defaults `"0.5.69"` and `aa_backfill` defaults `"1 Aug 2026"`
  (read from `result.get("after_action_version")` / `result.get("after_action_backfill")`
  so the job can pass real values later).
- Each `next_7_days` item is a dict `{day: "Day 1", actions: [...]}`. Normalise the
  day label: `raw = item.get("day_range") or item.get("day")`; if it does not start
  with "day", prefix it (`f"Day {raw}"`). Do NOT double-prefix when the model already
  returned "Day 1" — that produced "Day Day 1".
- Actions render as indented sub-bullets (`  - {action}`).

## Renderer pitfalls (markdown_report / _flat_lines)

- **`_flat_lines` append-vs-extend bug:** when a mapped key holds a `list`, use
  `out.extend(_flat_lines(val, key_map))`, NOT `out.append(...)`. The append version
  emits the whole Python list as one element, rendering raw `['a', 'b']` in the
  markdown/email (this was the "email is still raw" bug for the Next-7-days section).
- **Measurement section:** `measurement_plan` is a dict of `{tracking_events: [...],
  funnel_definition: {...}, reporting_cadence: str, required_dimensions: [...],
  quality_controls: [...]}`. Do NOT wrap it in a list and run it through `_flat_lines`
  (pipe-joined wall of text). Render each key as its own bullet with a bolded,
  title-cased label: `- **Minimum Events:** ...`.
- **Growth experiments:** `growth_plan` is a dict `{strategy, paid_media_budget,
  lead_generation_funnel, experiments}`. Render strategy/budget/funnel explicitly,
  then flatten only `experiments` — don't dump the whole dict through the generic
  flattener.
- Schema-tolerant rendering is intentional: Luna returns richer nested JSON than the
  old executor expected. Don't force the model back to a strict flat schema; make the
  renderer tolerant instead.

## Re-render without re-running the model

To refresh the `.md` after a renderer fix (no re-model call, no duplicate email):

```python
import sys; sys.path.insert(0, r"C:\Users\habib\.hermes\scripts")
import pluto_monthly_strategy_job as job
import json
result = json.load(open(r"C:\...\<run_id>.json"))
md = job.markdown_report(result)
open(r"C:\...\<run_id>.md", "w", encoding="utf-8").write(md)
# optionally: job.send_result_email(result, Path(md_path), job.executor_config())
```

Use `/mnt/c/...` paths when running from WSL python; `C:\...` only under Windows `py.exe`.
