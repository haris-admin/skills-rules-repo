---
name: pdf
description: Read, parse, and extract content from PDF files for use in the project workflow.
---

# PDF Skill

## When to use
Invoke when the user provides a PDF file or asks to extract content from a PDF document (lecture slides, readings, journal articles, assignment briefs).

## Workflow

1. **Read the PDF.** Use the `Read` tool with the file path and optional `pages` parameter for large documents (>10 pages). Always start with the first 5 pages to gauge structure.
2. **Identify structure.** Determine whether the PDF is:
   - **Structured text** (headings, paragraphs, tables) — extract as clean Markdown.
   - **Slide deck** — extract slide titles and bullet points, one heading per slide.
   - **Journal article** — extract Abstract, Methods, Results, Discussion sections.
   - **Scanned / image-heavy** — flag to the user that OCR is not available; suggest alternatives.
3. **Clean output.** Strip headers/footers, page numbers, and watermarks from extracted text. Preserve tables as Markdown tables. Preserve LaTeX equations where detected.
4. **Selective harvesting.** Per the Sovereign Constitution, surface clean Markdown to the student — never raw data. Prioritise high-mark-density content (definitions, key findings, rubric criteria).
5. **Deliver.** Output the extracted content in Markdown. If the user wants it saved, write to `docs/` following project file organisation rules.

## Constraints
- Max 20 pages per Read call; batch large PDFs.
- Never guess content that cannot be read — flag unreadable sections.
- Respect the Burrito First rule: extract the meat, not the garnish.
