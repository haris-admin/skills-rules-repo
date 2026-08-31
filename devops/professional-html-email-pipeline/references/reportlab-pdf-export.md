# Reportlab PDF export from result JSON

Professional branded PDF generation from a structured result JSON (e.g. monthly strategy review). Generator: `~/.hermes/scripts/pluto_monthly_strategy_pdf.py`.

## Usage

```bash
python3 ~/.hermes/scripts/pluto_monthly_strategy_pdf.py <result.json> <out.pdf>
```

Output: 4-page A4 PDF with dark navy header band, teal accents, footer page numbers, opportunity portfolio table (color-coded decisions), and clean bullets.

## Pitfalls (all hit Aug 2026 — verify against these when editing the generator)

1. **`str(HexColor)` returns `Color(...)` not a hex string.** `color.hexval()[:6]` truncates (`0x2dd4bf` → `0x2dd4` = broken). Use:
   ```python
   hex_str = "#%02x%02x%02x" % (int(color.red*255), int(color.green*255), int(color.blue*255))
   ```
   A bad value crashes reportlab at build with `Invalid color value 'Color('`.

2. **`md_inline()` escapes pre-built `<b>` tags.** If you pass `f"• <b>{name}</b>"` through `esc()` first, the tags render literally. Restore them after escaping:
   ```python
   t = t.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
   ```

3. **Dict/JSON bleed in reports.** Luna returns `growth_plan` / `measurement_plan` as nested dicts, not flat string lists. Three renderer strategies:
   - `render_growth_plan(items)` — bold channel headings + arrow actions + budget/success lines
   - measurement dict → one bullet per key with `k.replace("_"," ").title()` label
   - portfolio ideas → table with Decision/Opportunity columns
   Without these, sections render as raw `{"positioning": ...}` JSON — the #1 "unprofessional" complaint.

4. **"Day Day 1" duplication.** `next_7_days` items already carry `day: "Day 1"`. Normalize:
   ```python
   day = str(item.get("day_range") or item.get("day") or "").strip()
   if not day.lower().startswith("day"):
       day = f"Day {day}"
   ```

5. **Footer/page numbers** via `doc.build(story, onFirstPage=footer, onLaterPages=footer)` with a canvas callback — `canvas.drawString(22*mm, 11*mm, ...)`.

6. **Status colors:** pursue=teal, watch=gold/amber, reject=red (`#d64545`). Reject-as-green is a semantic error users notice immediately.

7. **Verify visually:** render pages with pypdfium2 and check with vision — text truncation mid-line at page bottom is the classic failure (padding/margins too tight for long content).

## Verification

```bash
python3 -c "
from pypdf import PdfReader
r = PdfReader('out.pdf')
print('Pages:', len(r.pages))
print(r.pages[0].extract_text()[:300])
"
```

Per skill `pdf` verification: extract text, render to PNG via pypdfium2, inspect with vision_analyze.
