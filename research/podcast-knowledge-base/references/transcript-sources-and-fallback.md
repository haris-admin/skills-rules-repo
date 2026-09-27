# Transcript sources when the archive/KB is stale

Ingestion lags or breaks silently, so a show's newest episode in `podcast_kb` can be weeks old while the
show publishes daily. **Never conclude "that episode doesn't exist" from the KB alone.**

## 1. Check freshness first (cheap, one query)

```sql
SELECT p.name, max(e.published_date) AS newest, count(*) AS eps
FROM podcast_kb.episodes e JOIN podcast_kb.podcasts p ON e.podcast_id = p.id
WHERE p.name ILIKE '%<show>%' GROUP BY p.name;
```

A `newest` well behind wall-clock is an INGESTION problem to report separately — it is not evidence about
the episode the user heard. Run the query through `podcast_kb_query.py <file.sql>` (the pooler helper), not
ad-hoc psql.

## 2. Go to the source

| Source | URL shape | What it gives you |
|---|---|---|
| **podscripts.co** | `podscripts.co/podcasts/<show-slug>/<episode-slug>` | Full transcript with speaker turns. Find the slug by web search: `"<show>" <episode title> transcript podscripts`. |
| **finance.biggo.com** | `finance.biggo.com/podcast/<hex-id>` | Structured summary + **verbatim quotes carrying timestamps** (`(00:22:51)`) + a business-highlights list. Best when you need a *citable* line, not a transcript wall. |
| **Apple Podcasts / Podbean** | episode page | Show notes, canonical episode number and publish date, guest bylines, and sometimes the full description with the episode's own framing question. |

Extract with `web_extract` (char_limit ~30000–40000). Long episode pages save the full text to a cache
file — grep that cache for the keyword you actually need instead of dumping the whole thing back.

## 3. Attribute precisely, or not at all

- **Confirm the speaker from the transcript** before attributing a quote. Multi-host shows attribute to
  the wrong person constantly (bylines mix hosts and guests).
- **When a user paraphrases ("X said Y"), check the on-record wording before repeating it.** A paraphrase
  can invert or soften the real claim, which is typically more specific and more useful. Quote the verbatim
  line and its timestamp instead of the paraphrase.
- **Separate the episode from its companion Q&A.** Panel shows often publish a news episode AND a
  listener-AMA episode in the same week; a claim heard in the AMA is not in the news episode's transcript.
  Search both before saying you cannot find something.
- Label confidence: a summary page is a secondary source. If the answer turns on an exact number or a
  decisive quote, pull it from the transcript itself.
