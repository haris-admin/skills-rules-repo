---
name: docx
description: Read, parse, and work with DOCX/Word documents — extract content, convert to Markdown, and integrate into project workflows.
---

# DOCX Skill

## When to use
Invoke when the user provides a `.docx` file, asks to extract content from a Word document, or needs to convert between DOCX and Markdown.

## Workflow

1. **Inspect the file.** DOCX files are ZIP archives containing XML. Use Bash to extract and read:
   ```bash
   unzip -o "$FILE" word/document.xml -d /tmp/docx_extract
   ```
   Then read `/tmp/docx_extract/word/document.xml` to get raw content.

2. **Parse structure.** Identify:
   - Headings (`w:pStyle` with `Heading1`, `Heading2`, etc.) — map to `#`, `##`.
   - Body paragraphs — map to plain text.
   - Bold/italic runs — map to `**bold**` / `*italic*`.
   - Lists (numbered and bulleted) — map to Markdown lists.
   - Tables — map to Markdown tables.
   - Images — note their presence but do not extract binary data unless requested.

3. **Clean output.** Remove Word-specific metadata, track changes markup, and comment annotations. Preserve semantic structure.

4. **Deliver.** Output clean Markdown. If the user wants it saved, write to `docs/` per project file organisation rules.

## Reverse (Markdown to DOCX)
If the user needs DOCX output, use `pandoc` if available:
```bash
pandoc input.md -o output.docx
```
Check for pandoc first: `which pandoc`. If unavailable, inform the user and suggest installation.

## Constraints
- Never modify the original DOCX file unless explicitly asked.
- Clean up temp files after extraction.
- Respect selective harvesting: surface clean content, not raw XML.
