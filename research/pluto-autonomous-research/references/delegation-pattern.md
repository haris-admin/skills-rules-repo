# Proven Subagent Delegation Pattern for Research

## Template Structure

Each subagent needs:
- **goal**: Specific research angle (one geographic region or one topic dimension)
- **context**: Rich background — who Haris is (Australian fintech founder, AMLHive), what the research is for, what date it is
- **toolsets**: `["web", "search"]` — these are what actually work

## Example: Multi-Angle Parallel Research

```python
delegate_task(tasks=[
    {
        "goal": "Research EU AI Act enforcement status as of [DATE]. Search for: enforcement deadline, provisions active, enterprise readiness, Codes of Practice. Return 4-6 key facts with source URLs.",
        "context": "It is [DATE]. Haris runs AMLHive, an Australian fintech. He needs to understand EU AI Act impacts on his business. Be specific — give actual dates, numbers, and URLs.",
        "toolsets": ["web", "search"]
    },
    {
        "goal": "Research Australian AI regulation developments in 2026. Search for: mandatory guardrails consultation, budget allocation, bill status, EU alignment. Return 4-6 key facts with source URLs.",
        "context": "It is [DATE]. Haris runs AMLHive (Australian fintech). The government allocated $39.9M for AI regulation. Need concrete status updates.",
        "toolsets": ["web", "search"]
    },
    {
        "goal": "Research global AI governance developments in 2026. Search for: US executive orders/legislation, UK AI Bill, China AI law, Seoul AI Summit, international cooperation. Return 4-6 key facts with source URLs.",
        "context": "It is [DATE]. Need a global regulatory landscape overview for Haris (AMLHive founder). Focus on concrete 2026 developments.",
        "toolsets": ["web", "search"]
    }
])
```

## What Worked
- **3 parallel subagents** covering different angles — maximum concurrency for this setup
- **Rich context** including who Haris is and what AMLHive does — subagents have NO memory of your session
- **Explicit instruction to return facts with URLs** — prevents vague summaries
- **Specific search queries listed in the goal** — gives subagents a concrete starting point
- **"Return ONLY valid JSON" constraint in goal field** — the single most effective pattern discovered. Format: *"Your ONLY job is to return valid JSON. No markdown, no commentary, no code blocks. Output exactly: { structured schema }"*. Include the full expected JSON schema in the goal. Success rate went from ~30% structured output to ~90%.

## What Didn't Work
- `terminal("web_search 'query'")` — web_search is not a shell command
- `execute_code` calling `terminal("web_search ...")` — same issue
- DuckDuckGo HTML scraping via curl — returned empty results
- Subagents with too-broad goals — they got lost and returned empty summaries
- Omitting the `toolsets` parameter — subagents default-inherit but may lack web access
- **Vague output instructions** — "summarize findings" or "report back" produces unusable narrative text. Always demand structured JSON with explicit field names.
- **GitHub API-only research** — subagents that use only `curl` to GitHub API often return 404s or incomplete data. Always pair with web search for broader source discovery.

## Subagent Reliability Notes

**⚠️ May 25, 2026: 100% failure rate.** 6/6 subagents across two rounds returned empty `tool_trace` despite explicit instructions to use web tools. Subagents described search actions in their summaries (e.g., "<search query=...>", "[Calling mcp__tavily__tavily_search]") but never actually executed them. When this happens, do NOT retry subagent delegation — pivot immediately to the RSS feed pipeline (see `references/australian-news-feeds.md`).

**Historical baseline (prior to May 25):** About 1/3 of research subagents returned empty or trivially short results. The global-governance angle tended to be the most reliable (richer search results for that domain). Given the current 100% failure rate, the RSS pipeline is now the recommended primary approach for topics covered by Australian/international news feeds.

### When to use delegation vs RSS

| Topic coverage | Use |
|---------------|-----|
| Australian startup/fintech/policy news | RSS feeds (StartupDaily, InnovationAus, SmartCompany, AustralianFintech) |
| Global fintech news | RSS (Finextra) |
| Specialized research (scientific papers, niche regulatory filings) | delegate_task (if operational) |
| Topics with no RSS feed coverage | delegate_task first, abort if empty tool_trace |
