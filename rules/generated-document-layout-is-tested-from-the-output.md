# A generated document's layout is tested from its own output (receipts, reports, PDFs; all agents)

When code draws a document itself (a hand-built PDF, a thermal receipt, a rendered report), test sizes, positions, wrapping and overflow by reading them out of the generated output, and measure text with real font metrics.

## Why this exists
**11 Nov 2026, Tap-Ease receipt PDF (C65D):** Haris reported that labels and values were different sizes, the Transaction ID wrapped, From and To ran off the page and the header was crowded. The PDF is built by hand (`receipt_pdf.py`), so a layout bug is invisible to ordinary tests. Reading each text item (font, size, colour, x, y) from the content stream made every complaint a failing test. A character-count wrap rule then wrapped a normal 46-character place and could overflow an all-capitals one; exact Helvetica-Bold widths fixed both.

## Rules
1. Write tests that parse the output: one label size and one value size, one colour per role, values on the same baseline or below the label as specified, nothing left of the left margin or right of the right margin, the footer within a set distance of the bottom.
2. Wrap with real font metrics (the font's width table), never a characters-per-line guess. Test an all-capitals string and a long unbroken word.
3. Keep the old content check: every string that used to be on the document is still there.
4. Render the real thing to an image and look at it before saying it is done; use the owner's own sample file for the first look.
5. A passing run on sample data is not evidence for real data: also render a few real records through the running service, read-only.
