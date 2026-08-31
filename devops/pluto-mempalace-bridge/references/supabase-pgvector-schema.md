# Supabase pgvector Schema — Podcast Knowledge Base

Designed June 4, 2026 to replace ChromaDB for large-scale podcast ingestion (500+ episodes, 30+ podcasts).

## Why Supabase over ChromaDB

| Factor | ChromaDB | Supabase+pgvector |
|--------|----------|-------------------|
| Scale ceiling | ~10K docs (SQLite) | Millions of vectors |
| Hybrid search | Vector only | Full-text + vector combined |
| AU context filtering | Metadata tags only | SQL WHERE on tags, dates, scores |
| Cross-podcast queries | Manual | SQL JOINs |
| Remote access | No | REST API (PostgREST) |
| Row-level security | No | Yes |
| Haris already uses it | — | Portfolio projects |

## Connection Setup

Create a Supabase project (or reuse existing), enable pgvector:
```sql
create extension if not exists vector;
```

Connection string stored in `/mnt/c/Users/habib/.hermes/.env`:
```
SUPABASE_PODCAST_KB_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres
```

## Full Schema

```sql
-- ============================================
-- TABLE 1: Podcast Sources
-- ============================================
CREATE TABLE podcasts (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    channel_id TEXT,
    tier INT DEFAULT 3 CHECK (tier BETWEEN 1 AND 4),
    category TEXT,
    youtube_handle TEXT,
    rss_feed_url TEXT,
    relevance_au BOOLEAN DEFAULT false,
    active BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================
-- TABLE 2: Episodes
-- ============================================
CREATE TABLE episodes (
    id SERIAL PRIMARY KEY,
    podcast_id INT REFERENCES podcasts(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    published_date DATE,
    youtube_id TEXT UNIQUE,
    transcript_text TEXT,
    duration_min INT,
    au_relevance_score FLOAT DEFAULT 0 CHECK (au_relevance_score BETWEEN 0 AND 1),
    tags TEXT[],
    extracted_frameworks TEXT[],
    core_idea TEXT,
    quiz_question TEXT,
    quiz_answer TEXT,
    processed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================
-- TABLE 3: Transcript Chunks (vectorized)
-- ============================================
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    episode_id INT REFERENCES episodes(id) ON DELETE CASCADE,
    chunk_index INT,
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    au_keywords TEXT[],
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================
-- TABLE 4: Cross-References (connection discovery)
-- ============================================
CREATE TABLE cross_references (
    id SERIAL PRIMARY KEY,
    source_episode_id INT REFERENCES episodes(id) ON DELETE CASCADE,
    target_episode_id INT REFERENCES episodes(id) ON DELETE CASCADE,
    relationship_type TEXT,
    similarity_score FLOAT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX idx_chunks_embedding ON chunks
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX idx_chunks_au_keywords ON chunks USING gin (au_keywords);
CREATE INDEX idx_episodes_tags ON episodes USING gin (tags);
CREATE INDEX idx_episodes_podcast_date ON episodes(podcast_id, published_date DESC);
CREATE INDEX idx_episodes_au_score ON episodes(au_relevance_score)
    WHERE au_relevance_score > 0.7;

-- ============================================
-- HYBRID SEARCH FUNCTION
-- ============================================
CREATE OR REPLACE FUNCTION search_podcast_kb(
    query_text TEXT DEFAULT NULL,
    query_embedding VECTOR(1536) DEFAULT NULL,
    au_only BOOLEAN DEFAULT false,
    podcast_filter INT DEFAULT NULL,
    match_limit INT DEFAULT 10
) RETURNS TABLE(
    chunk_id INT,
    episode_id INT,
    episode_title TEXT,
    podcast_name TEXT,
    content TEXT,
    similarity FLOAT,
    published_date DATE
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id, e.id, e.title, p.name, c.content,
        CASE
            WHEN query_embedding IS NOT NULL
            THEN (1 - (c.embedding <=> query_embedding))
            ELSE 0.0
        END AS similarity,
        e.published_date
    FROM chunks c
    JOIN episodes e ON c.episode_id = e.id
    JOIN podcasts p ON e.podcast_id = p.id
    WHERE
        (query_embedding IS NULL OR c.embedding IS NOT NULL)
        AND (NOT au_only OR e.au_relevance_score > 0.7)
        AND (podcast_filter IS NULL OR e.podcast_id = podcast_filter)
        AND (query_text IS NULL OR
             to_tsvector('english', c.content) @@ plainto_tsquery('english', query_text)
             OR to_tsvector('english', e.title) @@ plainto_tsquery('english', query_text))
    ORDER BY
        CASE WHEN query_embedding IS NOT NULL
             THEN c.embedding <=> query_embedding
             ELSE e.published_date END
    LIMIT match_limit;
END;
$$;

-- ============================================
-- VIEW: AU-Relevant Episodes
-- ============================================
CREATE OR REPLACE VIEW au_relevant_episodes AS
SELECT e.id, e.title, p.name AS podcast_name, e.published_date,
       e.au_relevance_score, e.core_idea, e.extracted_frameworks
FROM episodes e
JOIN podcasts p ON e.podcast_id = p.id
WHERE e.au_relevance_score > 0.5
ORDER BY e.au_relevance_score DESC, e.published_date DESC;

-- ============================================
-- VIEW: Cross-Podcast Framework Discovery
-- ============================================
CREATE OR REPLACE VIEW cross_podcast_frameworks AS
SELECT
    unnest(e.extracted_frameworks) AS framework,
    COUNT(DISTINCT e.podcast_id) AS podcast_count,
    array_agg(DISTINCT p.name) AS podcasts,
    COUNT(*) AS episode_count
FROM episodes e
JOIN podcasts p ON e.podcast_id = p.id
WHERE e.extracted_frameworks IS NOT NULL
GROUP BY framework
HAVING COUNT(DISTINCT e.podcast_id) > 1
ORDER BY podcast_count DESC, episode_count DESC;
```

## Seeding — Tier 1 Podcasts

```sql
INSERT INTO podcasts (name, channel_id, tier, category, youtube_handle, relevance_au)
VALUES
    ('All-In', 'UChJM-mF-4w_61Z6eCyl0eKQ', 1, 'VC/Tech/Markets', '@allinpodcast', true),
    ('a16z', 'UC9cn0TuPq4dnbTY-CBsm8XA', 1, 'Tech/VC', '@a16z', true),
    ('My First Million', 'UCyaN6mg5u8Cjy2ZI4ikWaug', 1, 'Business Ideas', '@MyFirstMillionPod', true),
    ('Acquired', 'UCyFqFYfTW2VoIQKylJ04Rtw', 1, 'Company Histories', '@AcquiredFM', false),
    ('Moonshots', 'UCCpNQKYvrnWQNjZprabMJlw', 1, 'AI/Future', '@moonshotsclips', true);
```

## Prerequisites to Activate

1. **Supabase project created** — Haris provides connection string
2. **pgvector extension enabled** — `create extension if not exists vector;`
3. **OpenAI API key** for generating 1536d embeddings (or use local model)
4. **Connection string in `.env`** — `SUPABASE_PODCAST_KB_URL`
