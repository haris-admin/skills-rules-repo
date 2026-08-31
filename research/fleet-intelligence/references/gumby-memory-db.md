# Querying Gumby's OpenClaw Memory DB

The database at `/home/habib/.openclaw/memory/main.sqlite` (from WSL) or `C:\Users\habib\.openclaw\memory\main.sqlite` (from Windows/PowerShell) is a vec0-backed SQLite store.

## Schema

```
files        — path, source, hash, mtime, size (87 rows, one per indexed file)
chunks       — id, path, source, start_line, end_line, hash, model, text, embedding (736 rows)
meta         — key, value (1 row: memory_index_meta_v1 config JSON)
chunks_fts   — FTS5 virtual table for full-text search
chunks_vec   — vec0 virtual table for vector similarity (embedding FLOAT[1536])
```

## Critical Queries (via Python sqlite3)

### Recent memory files
```sql
SELECT path, source, mtime, size 
FROM files 
WHERE source = 'memory' 
ORDER BY mtime DESC 
LIMIT 30
```

### Full file content (reassembling from chunks)
```sql
SELECT text FROM chunks 
WHERE path = ? AND source = 'memory'
ORDER BY start_line
```
Join results with newlines to reconstruct the file.

### Search for topic references
```sql
SELECT path, substr(text, 1, 500) 
FROM chunks 
WHERE text LIKE '%search_term%'
LIMIT 5
```

### Memory store config
```sql
SELECT key, value FROM meta
```
Returns model (text-embedding-3-small), provider (openai), sources list, and scope hash.

## Edge Cases

- **sqlite3 CLI absent:** Use `execute_code` with Python's `sqlite3` — it's built into the stdlib, no install needed.
- **Vector queries:** The `chunks_vec` table uses sqlite-vec extension. Vector similarity queries may fail if the extension isn't loaded. For intelligence gathering, FTS5 text search (`chunks_fts`) and direct chunk lookups are sufficient.
- **Encoding:** The DB stores text as-is. No special encoding handling needed.
- **Date range:** The DB indexed memory files from Feb 19 to April 9, 2026. Content after April 9 may not be indexed yet. Fall back to reading files directly from `/mnt/c/Users/habib/.openclaw/memory/` for more recent dates.
