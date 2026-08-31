# Agentic AI Educational Content Sourcing

Proven June 4, 2026 — 30+ results across 6 queries, curated to 8 high-quality resources.

## When to Use
- Finding tutorials, guides, and best practices for agentic AI tools (Hermes, OpenClaw, Claude Code, Codex)
- Sourcing educational content from content creators (Allie Miller, Silicon Valley Girl, etc.)
- Periodic refresh of the agentic AI knowledge base

## Google News RSS Query Pattern

Use AU locale for Australian-relevant results, US locale for broader tool coverage:

```bash
# Agentic AI tools and best practices (US locale for broader coverage)
curl -sL --max-time 10 -A "Mozilla/5.0" -o /tmp/edu_QUERY.xml \
  "https://news.google.com/rss/search?q=QUERY&hl=en-US&gl=US&ceid=US:en&tbs=qdr:m"

grep -oP '<title>(?!.*Google News)(.*?)</title>' /tmp/edu_QUERY.xml | head -8 | sed 's/<title>//;s/<\/title>//'
```

## Proven Query Catalog

| Query | Results | Best For |
|-------|---------|----------|
| `Hermes+agent+Nous+Research+tutorial+2026` | 5 hits | Hermes-specific guides |
| `OpenClaw+agent+workflow+guide+2026` | 5 hits | OpenClaw patterns |
| `Claude+Code+advanced+patterns+multi-agent` | 5 hits | Claude Code orchestration |
| `agentic+AI+development+best+practices+2026` | 5 hits | General best practices |
| `AI+coding+agent+orchestration+tutorial` | 5 hits | Multi-agent coordination |
| `autonomous+AI+agent+architecture+patterns` | 5 hits | Architecture patterns |

## Content Creator Discovery

For finding specific creators (Allie Miller, Silicon Valley Girl):

```bash
# Search for creator content
curl -sL --max-time 10 -A "Mozilla/5.0" -o /tmp/creator.xml \
  "https://news.google.com/rss/search?q=CREATOR+NAME+AI+agent+content+2026&hl=en-US&gl=US&ceid=US:en&tbs=qdr:m"
```

## Curated Creators (as of June 2026)

| Creator | Platform | Audience | Best Content |
|---------|----------|----------|-------------|
| Allie K. Miller | LinkedIn, Substack, Inc.com | 1.9M followers | AI business, Claude Code workflows |
| Silicon Valley Girl | YouTube (@siliconvalleygirl) | Video | AI founder interviews, Codex/Gemini tutorials |
| Moonshots Podcast | YouTube (@moonshotsclips) | Podcast | AI future, geopolitics, consciousness |

## Output Format

Save curated results as JSON to `~/.hermes/research_outputs/agentic-ai-education-YYYY-MM-DD.json` with the standard `findings` schema. Feed to MemPalace under chamber `agentic-security` or `pluto_research`:

```bash
/home/habib/.hermes/venv/bin/python3 scripts/pluto_mempalace_feeder.py \
  --input ~/.hermes/research_outputs/agentic-ai-education-YYYY-MM-DD.json \
  --topic "Agentic AI Educational Resources" \
  --tags "agentic-AI,Hermes,OpenClaw,ClaudeCode,Codex" \
  --source "pluto_research"
```

## Pitfalls
- Google News RSS is minified XML (single line). Use `grep -oP` not `read_file`.
- Filter out "Google News" internal entries from the title results.
- The `tbs=qdr:m` parameter limits to last month — remove for broader date range.
- Creator searches may return podcast transcripts (e.g., The Singju Post) — these are valuable for extracting quotes and frameworks.
