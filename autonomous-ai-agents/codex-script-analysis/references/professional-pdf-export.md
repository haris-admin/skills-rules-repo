# Professional PDF Export from Structured JSON (reportlab)

Reusable pattern for turning a script's structured output (LLM decision JSON, report data)
into a polished, branded PDF. Built Aug 2026 for the monthly strategy review
(`pluto_monthly_strategy_pdf.py`), which renders the `pluto-monthly-strategy` job's result JSON
into a 4-page A4 report with header band, page-number footers, a status table, and clean bullets.

Used by: `pluto_monthly_strategy_pdf.py` (generator at `~/.hermes/scripts/`).
The `pdf` skill covers generic PDF ops; THIS reference covers the branded reportlab layout +
the schema-tolerance gotchas that cost real debugging rounds.

## Architecture

```
result JSON (from job/model)
  │
  └── pluto_monthly_strategy_pdf.py (reportlab Platypus)
        ├── SimpleDocTemplate(A4, margins 22/18mm)
        ├── Header band: dark Table with teal accent LINEBELOW
        ├── Sections: executive summary → plan → growth → measurement → portfolio table → next 7 days
        └── footer(canvas, doc) callback: left doc title, right "Page N"
```

Key elements (each verified with vision on rendered pages):
- `SimpleDocTemplate(..., onFirstPage=footer, onLaterPages=footer)` for page numbers.
- Header band = `Table` with `BACKGROUND DARK`, `LINEBELOW TEAL` — compact paddings (8) so it
  doesn't become a tall black void.
- Opportunity portfolio = two-column `Table` with `ROWBACKGROUNDS [WHITE, LIGHT]` zebra stripes,
  status tags colored PURSUE=teal / WATCH=amber / REJECT=red.
- Colors: `DARK #0f1a2e`, `NAVY #1a2a4a`, `TEAL #2dd4bf`, `SLATE #4a5568`, `LIGHT #f2f5fa`.

## Pitfalls (each one cost a debug round)

1. **LLM JSON is schema-drift, not schema** — Luna-class models return dicts where the renderer
   expected lists of dicts, and nested dicts (`priority_channels: [{channel, actions[], budget}]`)
   where a flat list was assumed. Do NOT write renderers that assume `item.get('action')` works on
   every element. Write **per-structure renderers**: detect the dict shape
   (`positioning`/`priority_channels` → growth plan; `tracking_events`/`funnel_definition` →
   measurement) and emit one readable bullet per key. A generic fallback that joins `key: value`
   with ` | ` produces an unprofessional "wall of text" — the #1 complaint from visual review.
2. **reportlab colors: `str(HexColor)` returns `Color(...)` and `hexval()` returns `0x...`** —
   neither is a valid HTML color for `<font color='...'>`. Convert explicitly:
   `hex_str = "#%02x%02x%02x" % (int(c.red*255), int(c.green*255), int(c.blue*255))`.
   Using `str(color)[:6]` or `hexval()[:6]` silently breaks the color (invalid → exception, or
   truncated → wrong shade).
3. **Don't double-escape pre-built tags** — if you build `f"<b>{label}:</b> {text}"` and then run
   the text through an `esc()`/`md_inline()` that escapes `<`, the bold tags render literally
   (`• <b>Owned search</b>`). Either escape only the user content, or restore
   `&lt;b&gt;` → `<b>` after escaping.
4. **Day-range dedup** — model output may give `day_range: "Day 1"` OR `day: "Day 1"` OR
   `day: 1`. `f"Day {day}"` on an already-prefixed value yields "Day Day 1". Normalize:
   `if not str(raw).lower().startswith("day"): day = f"Day {raw}"`.
5. **Text truncation at page bottom** — if a long JSON blob is one Paragraph, it silently clips
   mid-word. Split into short Paragraphs and keep a healthy bottom margin (18mm+) so flowables
   break cleanly.
6. **Verification loop is mandatory** — reportlab output must be visually inspected, not just
   `PdfReader` text-checked. Render pages and inspect with vision:
   ```python
   import pypdfium2 as pdfium
   pdf = pdfium.PdfDocument(out_pdf)
   pdf[i].render(scale=2.0).to_pil().save(f"/tmp/pg{i+1}.png")
   ```
   (`pdftoppm` may not be installed; pypdfium2 is reliable.) First pass always finds layout sins:
   header void, raw JSON leaks, green-for-REJECT, pipe-walls. Fix → re-render → re-inspect.
7. **Fonts** — Helvetica family only (built-in). No Unicode sub/superscripts (render as boxes);
   the "→" arrow works in Helvetica.

## Status-color semantics

PURSUE = teal (positive action), WATCH = amber/gold (hold), REJECT = red (stop). Green for REJECT
confuses the reader — visual review flags it immediately. Keep red for rejection.
