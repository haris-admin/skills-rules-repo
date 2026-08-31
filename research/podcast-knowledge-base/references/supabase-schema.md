# Podcast KB — Supabase Schema

Full DDL deployed to Supabase project `vyqagemgwxfscppkfswq` (ap-southeast-2) on June 4, 2026.

## Extension

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

pgvector 0.8.0 installed. Uses IVFFlat index (list=100) for embedding search.

## Tables

### podcast_kb.podcasts
```sql
CREATE TABLE podcast_kb.podcasts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    channel_id VARCHAR(100),
    youtube_handle VARCHAR(100),
    tier INTEGER DEFAULT 3 CHECK (tier BETWEEN 1 AND 4),
    category VARCHAR(100),
    description TEXT,
    relevance_au NUMERIC(3,2) DEFAULT 0.0 CHECK (relevance_au BETWEEN 0 AND 1),
    spotify_url VARCHAR(500),
    website_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### podcast_kb.episodes
```sql
CREATE TABLE podcast_kb.episodes (
    id SERIAL PRIMARY KEY,
    podcast_id INTEGER REFERENCES podcast_kb.podcasts(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    published_date DATE NOT NULL,
    youtube_id VARCHAR(20) UNIQUE,
    transcript_text TEXT,
    duration_min INTEGER,
    au_relevance_score NUMERIC(3,2) DEFAULT 0.0 CHECK (au_relevance_score BETWEEN 0 AND 1),
    tags TEXT[] DEFAULT '{}',
    frameworks TEXT[] DEFAULT '{}',
    key_quotes TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(podcast_id, title, published_date)
);

CREATE INDEX idx_episodes_published_date ON podcast_kb.episodes(published_date DESC);
CREATE INDEX idx_episodes_podcast_id ON podcast_kb.episodes(podcast_id);
```

### podcast_kb.chunks (vector-ready)
```sql
CREATE TABLE podcast_kb.chunks (
    id SERIAL PRIMARY KEY,
    episode_id INTEGER REFERENCES podcast_kb.episodes(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    content_tsvector TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    embedding VECTOR(1536),
    au_keywords TEXT[] DEFAULT '{}',
    speaker VARCHAR(200),
    start_time INTEGER,
    end_time INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chunks_embedding ON podcast_kb.chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_chunks_fts ON podcast_kb.chunks USING GIN (content_tsvector);
```

### podcast_kb.cross_references
```sql
CREATE TABLE podcast_kb.cross_references (
    id SERIAL PRIMARY KEY,
    source_chunk_id INTEGER REFERENCES podcast_kb.chunks(id) ON DELETE CASCADE,
    target_chunk_id INTEGER REFERENCES podcast_kb.chunks(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100),
    similarity_score NUMERIC(5,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### podcast_kb.au_keywords
```sql
CREATE TABLE podcast_kb.au_keywords (
    keyword VARCHAR(100) PRIMARY KEY,
    category VARCHAR(50),
    weight NUMERIC(3,2) DEFAULT 0.5
);
```

### podcast_kb.ingest_log
```sql
CREATE TABLE podcast_kb.ingest_log (
    id SERIAL PRIMARY KEY,
    podcast_id INTEGER REFERENCES podcast_kb.podcasts(id),
    action VARCHAR(50),
    episodes_processed INTEGER DEFAULT 0,
    chunks_created INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'success',
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Functions

### hybrid_search()
```sql
CREATE OR REPLACE FUNCTION podcast_kb.hybrid_search(
    query_text TEXT,
    query_embedding VECTOR(1536),
    match_threshold NUMERIC DEFAULT 0.5,
    match_count INT DEFAULT 10,
    au_filter BOOLEAN DEFAULT FALSE
)
RETURNS TABLE(
    chunk_id INT,
    episode_id INT,
    podcast_name VARCHAR(255),
    episode_title VARCHAR(500),
    content TEXT,
    speaker VARCHAR(200),
    start_time INT,
    similarity NUMERIC,
    au_relevance NUMERIC
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id, c.episode_id, p.name, e.title,
        c.content, c.speaker, c.start_time,
        1 - (c.embedding <=> query_embedding) AS similarity,
        e.au_relevance_score
    FROM podcast_kb.chunks c
    JOIN podcast_kb.episodes e ON c.episode_id = e.id
    JOIN podcast_kb.podcasts p ON e.podcast_id = p.id
    WHERE 1 - (c.embedding <=> query_embedding) > match_threshold
        AND (NOT au_filter OR e.au_relevance_score > 0.3)
    ORDER BY similarity DESC
    LIMIT match_count;
END;
$$;
```

## Current State (June 8, 2026 — POST-FIX)

| Table | Rows |
|-------|------|
| podcasts | 22 registered |
| episodes | 198 (all with transcripts) |
| chunks | 501 (~2.5/episode, all with 1536-dim embeddings via OpenRouter) |
| au_keywords | 30 seeded |
| hybrid_search | Working — returns relevant chunks by vector similarity |

**Pipeline status:** All 3 crons operational — ingestion (`fabab82f804a`), chunking (`79c8ad5b9465`), insights (`67319a9b2606`). Backlog cleared.

**Fix date:** June 8, 2026. Root cause: chunking/embedding pipeline was never built. Ingestion stored transcripts but no code generated embeddings. Built `podcast_chunker.py` + wiring cron.
