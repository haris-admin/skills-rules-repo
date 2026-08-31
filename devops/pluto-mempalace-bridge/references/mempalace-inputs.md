# Mempalace Inputs — Complete Operational Reference

**Status:** Operational (wired May 24, 2026)
**Watcher script:** `~/.hermes/scripts/mempalace_watcher.py`
**Cron job:** `5678a363ce3b` (every 5 minutes)

## Architecture

```
User/System drops .md
        ↓
mempalace-inputs/YYYY-MM-DD-topic.md
        ↓ (≤5 min, cron 5678a363ce3b)
mempalace_watcher.py parses markdown
        ├─ # Topic → research topic
        ├─ Tags: → comma-separated tags
        ├─ ## Finding [VERIFIED/UNVERIFIED] → finding title + verified flag
        ├─ Content paragraphs → finding body
        ├─ Source: URL → verified source link
        ├─ Type: → regulatory|technical|market|opportunity|threat|trend
        └─ Confidence: → high|medium|low
        ↓
Structured JSON → pluto_mempalace_feeder.py
        ↓
ChromaDB pluto_research collection
        ↓
Marked as processed in mempalace-inputs/.processed/
```

## Watcher CLI

```bash
# Process all pending files (one-shot)
python3 ~/.hermes/scripts/mempalace_watcher.py

# Watch continuously
python3 ~/.hermes/scripts/mempalace_watcher.py --watch

# Process specific file
python3 ~/.hermes/scripts/mempalace_watcher.py --file 2026-05-24-topic.md

# Dry run (parse but don't feed)
python3 ~/.hermes/scripts/mempalace_watcher.py --dry-run

# Show inbox status
python3 ~/.hermes/scripts/mempalace_watcher.py --status
```

## Input Format Specification

Files must use this exact format for the watcher to parse correctly:

```markdown
# Topic Name (required — first # heading)
Tags: tag1, tag2, tag3 (optional — comma-separated)

## Finding Title [VERIFIED] or [UNVERIFIED] (required — ## heading)
Content paragraph(s) — can span multiple lines.
Non-metadata lines are treated as content body.
Source: https://real-url.com (optional)
Type: regulatory|technical|market|opportunity|threat|trend (optional, defaults to "trend")
Confidence: high|medium|low (optional, defaults to "medium")
```

### Rules
- Multiple `## Finding` sections → multiple ChromaDB documents
- `[VERIFIED]` / `[UNVERIFIED]` tags in heading → `verified: true/false` in parsed data
- `Source:` line → `url` field
- `Type:` line → `type` field (lowercased)
- `Confidence:` line → `confidence` field (lowercased)
- Everything between `## Finding` and next `## Finding` (or EOF) belongs to that finding

## Processed Files

Processed files are tracked in `mempalace-inputs/.processed/` — one `.done` file per processed `.md`:

```json
{
  "processed_at": "2026-05-24T01:25:00+10:00",
  "file_hash": "md5hash",
  "findings_count": 4
}
```

The watcher checks for `.done` markers before processing — prevents duplicate feeds.

## First Run Results (May 24, 2026)

| Topic | File | Findings | Status |
|-------|------|----------|--------|
| A2A Protocol & Agent Standards | `2026-05-24-a2a-protocol-standards.md` | 4 | processed |
| EU AI Act Article 11 | `2026-05-24-eu-ai-act-article-11.md` | 5 | processed |
| SKILL.md Ecosystem | `2026-05-24-skills-ecosystem.md` | 4 | processed |
| Zero Language Progress | `2026-05-24-zero-language.md` | 3 | processed |

**Result:** ChromaDB 17 → 33 documents (16 new findings across 4 new topics).

## Integration Points

### With RegRadar Enterprise Tier
Customer submits custom research topic → `.md` lands in `mempalace-inputs/` → auto-processed → appears in their search portal. Zero human in the loop.

### With Weekend Research Missions
Batch research topics → write all `.md` files → watcher auto-processes within 5 minutes. The `--dry-run` flag validates format before live feed.

### With Gumby (OpenClaw)
Gumby can write `.md` files to `mempalace-inputs/` from Windows via PowerShell:
```powershell
Copy-Item "C:\Users\habib\research-topic.md" "\\wsl$\Ubuntu\home\habib\.hermes\mempalace-inputs\"
```

## Pitfalls
- **No dedup across topics:** Same event covered in multiple topics creates separate ChromaDB docs. Manual review recommended for cross-topic dedup.
- **Markdown format is strict:** `Source:` must be on its own line, `Type:` must match one of the recognized values, or it gets treated as content body.
- **Empty findings = skip:** Files with zero parsable `## Finding` sections are skipped (marked as "skipped" in results).
- **ONNX model download:** First feed after ChromaDB restart may trigger ~80MB model download — 30-60s delay.
