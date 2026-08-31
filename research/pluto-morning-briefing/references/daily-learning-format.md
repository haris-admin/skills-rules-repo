# Daily Learning Session Format

## Cron
- **Job:** `0fb6bf47f704` (Moonshots Daily Learning)
- **Time:** 6:15 AM AEST daily
- **Source:** Supabase `podcast_kb` schema — random episode from any podcast

## Format
```
🎓 Daily Learning — [Date]
🎙️ From: [Podcast Name] — [Episode Title] ([Published Date])
🧠 The Idea: [Framework name + 250-350 word explanation]
💡 Why It Matters: [Relevance to Haris as Australian tech founder]
🔗 Portfolio Angle: [Connection to ExitLens, PayLicence, TokenPilot, FinAI File, CloudProof, AML Hive]
❓ Your Challenge: [One thought-provoking conceptual question — NOT trivia]
```

## Quiz Rules
- Ask ONE question, conceptual not factual
- Don't ask "what are the six dimensions?" — ask "what does the six-dimensional framework mean for how we should regulate AI?"
- Reveal answer with additional context when Haris responds
- Make it feel like morning coffee conversation, not a test

## Content Selection
- Alternates between podcasts — don't repeat same show two days in a row
- Prefer episodes with high AU relevance (>0.5) when available
- Prefer episodes with frameworks[] populated
- Fall back to any episode with transcript if no framework-tagged episodes available

### ⚠️ Frameworks bottleneck (June 26, 2026)
**Only Moonshots Podcast has populated `frameworks` arrays.** All 14 other podcasts (Lenny's Podcast, Acquired, a16z, All-In, HBR IdeaCast, etc.) have `frameworks = {}` — empty text arrays. The query `WHERE array_length(e.frameworks, 1) > 0` returns ONLY Moonshots episodes, which breaks the "alternate podcasts" rule.

**Two-stage query pattern (use this in the cron prompt):**

```bash
# Stage 1: Try a non-last-used podcast with frameworks
# (skip if last used was a non-Moonshots, since only Moonshots has frameworks)
PGPASSWORD='...' psql -h aws-1-ap-southeast-2.pooler.supabase.com -p 6543 \
  -U postgres.vyqagemgwxfscppkfswq -d postgres -t -A -F $'\t' \
  -c "SELECT p.name, e.title, e.published_date, e.frameworks, e.key_quotes, e.au_relevance_score,
      substring(e.transcript_text, 1, 6000) as txt
      FROM podcast_kb.episodes e JOIN podcast_kb.podcasts p ON e.podcast_id = p.id
      WHERE e.transcript_text IS NOT NULL
        AND e.transcript_text NOT LIKE '%YouTube is blocking%'
        AND e.transcript_text NOT LIKE '%Could not retrieve%'
        AND e.au_relevance_score > 0.5
      ORDER BY RANDOM() LIMIT 1;"

# Stage 2: If Stage 1 returns a frameworks-populated episode, use it directly.
# If it returns a non-frameworks episode, extract the key idea from the transcript
# by reading it in 6000-char chunks with additional psql queries.
```

**psql transcript retrieval (avoid column truncation):**
Always use `-t -A` flags for transcript queries — default psql column-width formatting silently truncates long text fields. Example:
```bash
PGPASSWORD='...' psql -h ... -t -A -F $'\t' -c "SELECT substring(e.transcript_text, 6000, 6000) ..."
```
