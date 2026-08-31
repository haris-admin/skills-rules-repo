# Supabase + pgvector — Podcast Knowledge Architecture

## Decision (June 4, 2026)

**Supabase + pgvector** chosen over: ChromaDB (scale ceiling), MongoDB Atlas ($57/mo for vector search), Local PostgreSQL (no remote access).

Reason: Haris already uses Supabase for portfolio projects. pgvector is a free extension. Hybrid search (keyword + vector) is the killer feature for finding AU-relevant podcast segments across shows.

## Schema

```sql
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Podcasts registry
CREATE TABLE podcasts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    channel_id TEXT,
    youtube_handle TEXT,
    tier INTEGER CHECK (tier BETWEEN 1 AND 4),
    category TEXT,
    relevance_au BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Episodes with transcripts
CREATE TABLE episodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    podcast_id UUID REFERENCES podcasts(id),
    title TEXT NOT NULL,
    published_date DATE,
    youtube_id TEXT UNIQUE,
    transcript_text TEXT,
    duration_min INTEGER,
    au_relevance_score FLOAT DEFAULT 0 CHECK (au_relevance_score BETWEEN 0 AND 1),
    tags TEXT[],
    frameworks TEXT[],
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Vector chunks for semantic search
CREATE TABLE chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    episode_id UUID REFERENCES episodes(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    au_keywords TEXT[],
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Cross-podcast connections
CREATE TABLE cross_references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_episode_id UUID REFERENCES episodes(id),
    target_episode_id UUID REFERENCES episodes(id),
    relationship_type TEXT,
    similarity_score FLOAT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX idx_episodes_podcast ON episodes(podcast_id);
CREATE INDEX idx_episodes_date ON episodes(published_date);
CREATE INDEX idx_episodes_au_relevance ON episodes(au_relevance_score);
CREATE INDEX idx_chunks_episode ON chunks(episode_id);
CREATE INDEX idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_chunks_content_fts ON chunks USING gin (to_tsvector('english', content));
```

## Podcast Tier Prioritization

| Tier | Podcasts | Focus |
|------|----------|-------|
| 🔴 Tier 1 | All-In, a16z, My First Million, Acquired | VC debates, tech trends, business ideas, company strategy |
| 🟡 Tier 2 | Masters of Scale, Prof G Pod, Knowledge Project | Growth, strategy, mental models |
| 🟢 Tier 3 | Diary of a CEO, Foundr, Logan Bartlett, How I Built This | Leadership, founder stories |
| 🔵 Special | **Lenny's Podcast** (insider access) | Product, growth, AI — Haris has elevated subscriber access |
| ⚪ Archive | Moonshots Clips (already in ChromaDB), The Pitch, Investors Podcast directory | Reference/curation |

## AU Relevance Scoring

Each episode gets scored 0-1 on Australian relevance:
- **1.0** — Directly about Australian regulation, market, or startups
- **0.7** — Indirectly applicable (global trend with clear AU implications)
- **0.3** — General business/tech with distant AU relevance
- **0.0** — No Australian connection

Scoring keywords: AUSTRAC, ASIC, CGT, PSP, AML, Australian, Sydney, Melbourne, APRA, RBA, Australian fintech, Australian startup, Australian regulation, Tranche 2, payments licensing, digital assets Australia.

## Hybrid Search Function

```sql
CREATE OR REPLACE FUNCTION search_podcasts(
    query_text TEXT,
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10,
    au_only BOOLEAN DEFAULT false
) RETURNS TABLE(
    episode_id UUID,
    podcast_name TEXT,
    title TEXT,
    content TEXT,
    similarity FLOAT,
    au_score FLOAT
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        p.name,
        e.title,
        c.content,
        1 - (c.embedding <=> query_embedding) AS similarity,
        e.au_relevance_score
    FROM chunks c
    JOIN episodes e ON c.episode_id = e.id
    JOIN podcasts p ON e.podcast_id = p.id
    WHERE 1 - (c.embedding <=> query_embedding) > match_threshold
      AND (NOT au_only OR e.au_relevance_score > 0.3)
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

## Twice-Weekly Monitoring Cron

A cron job runs every Wednesday and Sunday, scanning all registered podcast channels for new episodes in the last 3 days, downloading transcripts, and inserting into the database.

**Cron schedule:** `0 20 * * 3,0` (6:00 AM AEST Wed + Sun)

## Credentials

Supabase project: `vyqagemgwxfscppkfswq` (ap-southeast-2 = Sydney)
URLs stored in `/mnt/c/Users/habib/.hermes/.env`:
- `SUPABASE_OPERATOR_DATABASE_URL` — transaction mode pooler (port 5432)
- `SUPABASE_OPERATOR_SPOOLER_DATABASE_URL` — session mode pooler (port 6543)  
- `DIRECT_URL` — AWS pooler (ap-southeast-2)

**Note:** Passwords in `.env` are redacted placeholders (`***`) as of June 4, 2026. Real credentials needed before ingestion can begin.

## Ingestion Pipeline Script (Design)

```
fetch RSS → extract video IDs → filter by date (Jan 2026+) → 
download transcripts → chunk text (500-word segments) → 
generate embeddings (OpenAI text-embedding-3-small, 1536d) → 
score AU relevance → INSERT into episodes + chunks → 
run cross-reference search against existing episodes
```

## Edge Cases
- **Duplicate episodes:** Check `youtube_id` UNIQUE constraint before inserting
- **Transcript unavailable:** Skip episode, log to errors table
- **Embedding API rate limits:** Batch in groups of 20 with 1s delay
- **WSL IPv6 issues:** Use AWS pooler URL (IPv4) for psql connections
