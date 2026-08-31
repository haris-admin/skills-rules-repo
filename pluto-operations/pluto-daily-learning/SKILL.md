---
name: pluto-daily-learning
description: "Daily learning cron. Query Supabase, dedup, teach, quiz."
---

# Pluto Daily Learning — Moonshots Podcast Pipeline

## Overview

**Cron:** `0fb6bf47f704` | **Time:** 6:15 AM AEST daily | **Deliver:** origin (Telegram)

Every morning, Pluto queries the Supabase podcast knowledge base for a random episode with frameworks, teaches Haris one concept (250-350 words), quizzes him with one thought-provoking question, and saves the full learning to `research_outputs/daily-learning-YYYY-MM-DD.md`.

## Pipeline

### 1. Query Supabase — Two-Path Strategy

The "alternate podcasts" instruction requires variety, but only Moonshots episodes have pre-extracted frameworks. Use **Path A first**, falling back to **Path B** when Moonshots has been used 2+ days in a row or needs variety.

**Supabase connection:** Host `aws-1-ap-southeast-2.pooler.supabase.com`, port 6543, database `postgres`, schema `podcast_kb`. PGPASSWORD is embedded. Use `-t -A -F '|||'` for clean delimited output in automated scripts (no table borders, nulls as empty strings, `|||` as column separator).

#### Path A — Moonshots with pre-extracted frameworks (preferred when available)

```bash
python3 << 'PYEOF'
import subprocess, os
env = os.environ.copy()
env['PGPASSWORD'] = '4SIsDTYfvHjAqC7Ygp8B89q7Q743eOC!'
env['PGSSLMODE'] = 'require'
r = subprocess.run(['psql', '-h', 'aws-1-ap-southeast-2.pooler.supabase.com', '-p', '6543',
    '-U', 'postgres.vyqagemgwxfscppkfswq', '-d', 'postgres',
    '-t', '-A', '-F', '|||',
    '-c', """SELECT p.name, e.title, e.published_date::text, e.transcript_text, e.frameworks, e.key_quotes, e.au_relevance_score FROM podcast_kb.episodes e JOIN podcast_kb.podcasts p ON e.podcast_id = p.id WHERE e.transcript_text IS NOT NULL AND e.frameworks IS NOT NULL AND array_length(e.frameworks, 1) > 0 ORDER BY RANDOM() LIMIT 1;"""],
    capture_output=True, text=True, timeout=15, env=env)
print(r.stdout)
PYEOF
```

#### Path B — Non-Moonshots with long transcript (fallback for variety)

When Moonshots has been used recently and variety is needed, query ANY podcast with a long enough transcript to extract a framework from:

```bash
python3 << 'PYEOF'
import subprocess, os
env = os.environ.copy()
env['PGPASSWORD'] = '4SIsDTYfvHjAqC7Ygp8B89q7Q743eOC!'
env['PGSSLMODE'] = 'require'
# Step 1: Check what podcasts were in the last 3 days
import glob
recent_podcasts = set()
for f in sorted(glob.glob('/home/habib/.hermes/research_outputs/daily-learning-*.md'))[-4:]:
    for line in open(f):
        if '🎙️ From:' in line:
            recent_podcasts.add(line.split('🎙️ From:')[1].split('—')[0].strip())
            break
# Step 2: Build exclusion list
exclude = list(recent_podcasts) if recent_podcasts else ['NONE']
exclude_str = "', '".join(exclude)
# Step 3: Query excluding recently-used podcasts, requiring long transcript
r = subprocess.run(['psql', '-h', 'aws-1-ap-southeast-2.pooler.supabase.com', '-p', '6543',
    '-U', 'postgres.vyqagemgwxfscppkfswq', '-d', 'postgres',
    '-t', '-A', '-F', '|||',
    '-c', f"""SELECT p.name, e.title, e.published_date::text, e.transcript_text, e.au_relevance_score FROM podcast_kb.episodes e JOIN podcast_kb.podcasts p ON e.podcast_id = p.id WHERE e.transcript_text IS NOT NULL AND length(e.transcript_text) > 2000 AND p.name NOT IN ('{exclude_str}') ORDER BY RANDOM() LIMIT 1;"""],
    capture_output=True, text=True, timeout=20, env=env)
print(r.stdout)
PYEOF
```

When using Path B, you must extract the framework yourself from the transcript. Read the full transcript, identify the core concept/framework, and synthesize it — the `frameworks` column will be NULL.

### 2. Deduplicate Against Recent Days — MANDATORY (don't skip)

**⚠️ DO NOT write the daily learning file until you've completed this step.** `ORDER BY RANDOM()` regularly returns already-used episodes — Aug 2026 alone had two confirmed back-to-back repeats (Cathie Wood Aug 6→7, Privacy in the Age of AGI Aug 4→8).

Always check the last 4 days of learning files for the episode TITLE (not just the podcast name) before committing:

```bash
# Step 1: Check recent episode TITLES (not just podcast names — same podcast is fine, repeat title is NOT)
for f in $(ls -t ~/.hermes/research_outputs/daily-learning-*.md | head -4); do
    echo "=== $(basename $f) ==="
    grep -m1 "🎙️ From:" "$f"
done
```

If the random result's TITLE matches any of the last 4 days, re-query with that specific title excluded:

```bash
python3 -c "
import subprocess, os
env = os.environ.copy()
env['PGPASSWORD'] = '4SIsDTYfvHjAqC7Ygp8B89q7Q743eOC!'
env['PGSSLMODE'] = 'require'
r = subprocess.run(['psql', '-h', 'aws-1-ap-southeast-2.pooler.supabase.com', '-p', '6543', '-U', 'postgres.vyqagemgwxfscppkfswq', '-d', 'postgres', '-c', \"SELECT e.id, p.name, e.title, e.published_date, e.frameworks FROM podcast_kb.episodes e JOIN podcast_kb.podcasts p ON e.podcast_id = p.id WHERE e.transcript_text IS NOT NULL AND e.frameworks IS NOT NULL AND array_length(e.frameworks, 1) > 0 ORDER BY e.published_date DESC;\"], capture_output=True, text=True, timeout=15, env=env)
print(r.stdout)
"
```

Then re-query with explicit title exclusion(s). This is the pattern used successfully Aug 9, 2026:

```bash
PGPASSWORD='4SIsDTYfvHjAqC7Ygp8B89q7Q743eOC!' PGSSLMODE='require' \
psql -h aws-1-ap-southeast-2.pooler.supabase.com -p 6543 \
  -U 'postgres.vyqagemgwxfscppkfswq' -d postgres -A -F '|||' -t \
  -c "SELECT p.name, e.title, e.published_date::text, substring(e.transcript_text, 1, 5000), e.frameworks, e.key_quotes, e.au_relevance_score FROM podcast_kb.episodes e JOIN podcast_kb.podcasts p ON e.podcast_id = p.id WHERE e.transcript_text IS NOT NULL AND e.frameworks IS NOT NULL AND array_length(e.frameworks, 1) > 0 AND e.title NOT IN ('Privacy in the Age of AGI — The End of Personal Data') ORDER BY RANDOM() LIMIT 1;"
```

Add all duplicate titles found in the last 4 days to the `NOT IN` list.

### 3. Teach the Concept (250-350 words)

Structure:
- **The Idea:** Framework name + 3-5 paragraph deep explanation with specific examples. Not just a definition — explain the mechanism, cite research/data points, show why it matters.
- **Why It Matters:** Connect to Haris as an Australian fintech/regtech founder. Ground it in his context — AML/KYC, payments, AI governance, data sovereignty, startup building.
- **Portfolio Angle:** Map the concept to specific projects (ExitLens AU, PayLicence AU, TokenPilot AU, FinAI File AU, CloudProof AU, AML Hive). Use a table or bullet list with impact levels (🔴 HIGH / 🟡 MEDIUM / 🟢 LOW).
- **Key Takeaways:** 3-4 bullet points summarizing the actionable insights.

### 4. Quiz Haris

One thought-provoking question. Make it **conceptual**, not trivia. The question should force Haris to apply the framework to his own context. Example formats that work:
- "If [framework insight], does [existing assumption] still hold?"
- "Given [specific data point from the episode], what would you change about [portfolio project]?"
- "Is [trend] an opportunity or a threat for [Haris's business] — and why?"

### 5. Save to Both Locations

```bash
# The write_file call saves to:
~/.hermes/research_outputs/daily-learning-YYYY-MM-DD.md
```

The cron's `deliver: origin` setting handles Telegram delivery automatically — the agent's final response text goes to Haris. The file save is for archival and dedup tracking.

## Output Format

```
🎓 Daily Learning — Weekday, DD Month YYYY

🎙️ From: [Podcast Name] — "[Episode Title]" ([Date])

AU Relevance Score: X.XX
Framework: [Framework name]

🧠 The Idea: [Framework name + 3-5 paragraph deep explanation]

💡 Why It Matters: [Relevance to Haris/Australia, 1-2 paragraphs]

🔗 Portfolio Angle: [Table or bullets mapping to specific projects]

❓ Your Challenge: [One conceptual question]

📚 Key Takeaways: [3-4 bullet points]
```

## Content Principles

- **Conversational tone.** Assume Haris is reading at 6:15 AM with coffee. Not dry, not academic. But not sloppy either — the depth should be genuine.
- **Specific data, not generalities.** Cite the numbers, studies, or examples from the episode. "Researchers demonstrated X with Y% accuracy" beats "AI is changing privacy."
- **Australian context.** Whenever possible, tie back to Australian regulation (AUSTRAC, ASIC, APRA, OAIC, Privacy Act reforms) or Australian market dynamics.
- **Portfolio-first.** The "Why It Matters" section should always connect to at least one of Haris's projects. If the connection is weak, pick a different episode.

## Pitfalls

- **Only Moonshots Podcast has frameworks in Supabase (as of Aug 2026).** The query `WHERE e.frameworks IS NOT NULL AND array_length(e.frameworks, 1) > 0` returns only 15 Moonshots episodes. Other podcasts (The Prof G Pod, My First Million, All-In, Lenny's, AI Engineer, The Pitch, etc.) have transcripts but no frameworks populated — their `frameworks` column is NULL or empty arrays. **Workaround:** Use Path B (above) — query non-Moonshots episodes with `length(e.transcript_text) > 2000`, read the transcript, and extract the framework yourself. This requires more synthesis work but enables podcast variety. Example: Aug 5 session used My First Million ("What happened when I accidentally sat next to...") with a 52K-char transcript and extracted "Achieving Greatness vs. Being Great" as the framework.

- **`psql` output is tabular by default — use tuple-only + delimiter for scripts.** Without `-t -A -F '|||'`, psql returns column headers, spacing, and pipe-separated borders. In automated Python scripts parsing the result, use: `psql -t -A -F '|||' -c "..."`. The output is one line per row, columns separated by `|||`, no headers. Split with `row.strip().split('|||')`.

- **Transcripts can be truncated in psql output.** Psql may clip long text fields. For episodes with >8000-char transcripts, cast `e.published_date::text` to avoid date wrapping issues, and use `length(e.transcript_text) > N` in the WHERE clause to ensure you're getting a useful amount of content. The Aug 5 session successfully used `length(e.transcript_text) > 2000` which returned a 52K-char transcript from My First Million.

- **RANDOM() doesn't deduplicate — and this fires in production.** The `ORDER BY RANDOM()` query can (and will) return episodes already used in the last 1-3 days. There's no exclusion list in the SQL. Always check `~/.hermes/research_outputs/daily-learning-*.md` for recently-used episodes before committing. The Path B query above now includes automated exclusion of podcasts used in the last 3 days. Path A (Moonshots) still needs a manual check. If the random result is a repeat, manually select a different episode by id.

  **⚠️ This has bitten us twice (Aug 2026):** Cathie Wood episode was delivered Aug 6 AND Aug 7 back-to-back. "Privacy in the Age of AGI" was delivered Aug 4 AND Aug 8. Both happened because the agent didn't run the dedup check. The fix is NOT a smarter query — it's a mandatory step in the agent's workflow. **Before writing ANY daily learning file, grep the last 3 filenames for the episode title.** If found, re-query with `AND e.title NOT IN ('already-used-title-1', 'already-used-title-2')` appended to the WHERE clause. See the dedup section above for the exact re-query pattern.

- **The transcript_text field is often truncated in Supabase storage.** Supabase stores only the first ~8000 characters of transcripts. When explaining a framework, don't rely on the transcript for granular detail — use the `frameworks` array (which contains the distilled concept names) and the `key_quotes` array for quotes. The transcript provides context but not completeness.

- **key_quotes is frequently empty.** Most episodes have `key_quotes: {}` (empty JSON object). The podcast insight extractor (cron `67319a9b2606`) populates frameworks but key_quotes extraction is less reliable. Don't depend on quotes being available.

- **The saved file must be the COMPLETE learning, not a summary.** The cron prompt explicitly requires: "The file saved to research_outputs/ MUST contain: the COMPLETE, FULL learning synthesis including: the concept name, a 3-5 paragraph deep explanation of the framework/idea with specific examples, quiz questions, and key takeaways — do NOT summarize or condense." Use write_file, not a terminal echo.

- **pgvector schema is separate from this workflow.** The daily learning cron queries Supabase's `podcast_kb` schema (relational tables with psql), NOT the pgvector embeddings. The pgvector schema is used by the podcast insight extractor and morning briefing pipeline, but the daily learning reads directly from the episodes table.
