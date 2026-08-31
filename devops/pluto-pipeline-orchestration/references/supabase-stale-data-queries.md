# Supabase Stale Data Cleanup Queries

Used by the Saturday DREAM MODE Phase 1 (pgvector cleanup) and the Friday weekly review (podcast ingestion audit).

## Connection

```bash
PGPASSWORD='4SIsDTYfvHjAqC7Ygp8B89q7Q743eOC!' PGSSLMODE=require \
  psql -h aws-1-ap-southeast-2.pooler.supabase.com -p 6543 \
  -U postgres.vyqagemgwxfscppkfswq -d postgres
```

**Password note:** Contains `!` — always use single quotes or Python subprocess with env dict, never double-quote or interpolate in bash.

## Stale Data Detection Queries

### 1. YouTube IP-blocked garbage (safe to delete)
```sql
SELECT COUNT(*) FROM podcast_kb.episodes 
WHERE transcript_text LIKE '%YouTube is blocking%';
```

### 2. Short transcripts (failed downloads — safe to delete)
```sql
SELECT COUNT(*) FROM podcast_kb.episodes 
WHERE LENGTH(COALESCE(transcript_text, '')) < 100;
```

### 3. Stale episodes with no AU relevance score (review before acting)
```sql
SELECT COUNT(*) FROM podcast_kb.episodes 
WHERE published_date < NOW() - INTERVAL '90 days'
  AND (au_relevance_score IS NULL OR au_relevance_score = 0);
```

### 4. Duplicate episodes (same youtube_id + podcast_id)
```sql
SELECT youtube_id, podcast_id, COUNT(*) as dup_count
FROM podcast_kb.episodes
GROUP BY youtube_id, podcast_id
HAVING COUNT(*) > 1;
```

### 5. Orphaned chunks (no matching episode)
```sql
SELECT COUNT(*) FROM podcast_kb.chunks c
LEFT JOIN podcast_kb.episodes e ON c.episode_id = e.id
WHERE e.id IS NULL;
```

### 6. Total episode count
```sql
SELECT COUNT(*) FROM podcast_kb.episodes;
```

## Combined Health Check (single query)

```sql
SELECT 
  'youtube_blocked' as category, COUNT(*) as count
FROM podcast_kb.episodes WHERE transcript_text LIKE '%YouTube is blocking%'
UNION ALL
SELECT 'short_transcript', COUNT(*)
FROM podcast_kb.episodes WHERE LENGTH(COALESCE(transcript_text, '')) < 100
UNION ALL
SELECT 'stale_no_score', COUNT(*)
FROM podcast_kb.episodes WHERE published_date < NOW() - INTERVAL '90 days' AND (au_relevance_score IS NULL OR au_relevance_score = 0)
UNION ALL
SELECT 'total_episodes', COUNT(*) FROM podcast_kb.episodes
ORDER BY category;
```

## Cleanup (safe to delete)

Only delete items that can be re-ingested:
```sql
-- Remove IP-blocked garbage (can re-download with fresh IP/cookies)
DELETE FROM podcast_kb.episodes WHERE transcript_text LIKE '%YouTube is blocking%';

-- Remove failed downloads (transcript < 100 chars is an error message, not content)
DELETE FROM podcast_kb.episodes WHERE LENGTH(COALESCE(transcript_text, '')) < 100;
```

**Do NOT automatically delete:** duplicate episodes (need manual review — one may have better transcript), stale no-score episodes (may have valid transcripts just pre-dating the scorer).

## Weekly Ingestion Audit

```sql
SELECT COUNT(*), date(published_date) 
FROM podcast_kb.episodes 
WHERE date(published_date) >= 'DATE_START' AND date(published_date) <= 'DATE_END' 
GROUP BY date(published_date) ORDER BY date(published_date);
```

## Column Name Pitfalls

**The `podcast_kb.episodes` table uses `published_date` — NOT `published_at`, NOT `created_at`.** This has burned multiple DREAM MODE cycles. The PostgreSQL error is:
```
ERROR: column "published_at" does not exist
HINT: Perhaps you meant to reference the column "episodes.published_date".
```

**Correct columns for common queries:**
- Episode date: `published_date` (NOT `published_at`, NOT `created_at`)
- Episode ID: `id` (PK)
- Podcast FK: `podcast_id`
- Transcript: `transcript_text`
- AU score: `au_relevance_score` (float, 0-1, NULL = unscored)

Always verify column names with `\d podcast_kb.episodes` before running queries if you get a "column does not exist" error.

## History

- **Jul 18, 2026:** All checks passed — 481 episodes, 0 stale records. 46 episodes >90 days without AU scores (carried from W26). Fixed `created_at` → `published_date` in all queries (3 instances were wrong since original creation).
- **Jun 27, 2026:** All checks passed — 0 stale records across all categories, 302 total episodes. Second consecutive clean week.
- **Jun 20, 2026:** All checks passed — 0 stale records, 275 episodes, 501 chunks.
- **Jun 13, 2026:** All checks passed — 0 stale records, 214 episodes.
