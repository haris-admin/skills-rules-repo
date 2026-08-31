# Google Antigravity 2.0 — Emerging Tech Investigation (June 9, 2026)

## Investigation Context

Haris asked: "Find the best use cases of the Antigravity 2.0 and the Claude Code." This is a case study in how to research a newly-launched tech product when articles are JS-rendered and official packages aren't on public registries.

## Methodology

### 1. Google News RSS Discovery (Phase 1 pattern)

Used 3-angle Google News RSS queries to discover articles:

```bash
curl -sL "https://news.google.com/rss/search?q=Google+Antigravity+2.0&hl=en-US&gl=US&ceid=US:en"
```

This returned 10+ article headlines covering the product launch at Google I/O 2026, including comparative reviews, installation guides, and security warnings. Key sources: TechCrunch, 9to5Google, XDA, How-To Geek, Augment Code, MarkTechPost.

### 2. What Worked

- **Google News RSS headlines + descriptions** — richest source. 390 headlines across 5 queries, 196 unique sources. Enough signal for confident synthesis.
- **npm ecosystem search** — `npm search antigravity` returned 15+ wrapper packages. The ecosystem tells you what's real: `opencode-agy-bridge`, `openclaw-antigravity`, `agy-superpowers`, `eagle-mem` (shared memory across Claude Code + Antigravity).
- **Landing page discovery** — found `https://antigravity.google.com` (HTTP 200) via URL pattern guessing.
- **npm registry search** — `npm view @google/antigravity` returned 404, confirming it's NOT publicly distributed via npm.
- **Claude Code verification** — `claude --version` returned 2.1.150, confirmed installed at `/home/habib/.local/bin/claude`.

### 3. What Didn't Work

- **Subagent delegation for web research** — 2/2 delegate_task calls with `toolsets: ["web","search"]` returned empty tool_trace despite explicit instructions.
- **Direct article fetching via curl** — All major article URLs (blog.google, techcrunch.com, 9to5google.com, xda-developers.com, howtogeek.com, marktechpost.com) returned 404 or empty content. All JS-rendered.
- **Terminal `curl | python3` pipes** — Shell escaping inside `terminal()` consistently breaks with multi-line Python. Always write to temp file first.
- **Google page fetching** — antigravity.google.com returns gzipped content. `--compressed` flag works but the page timed out in terminal (JS-heavy).

### 4. Investigation Pattern That Works

For researching new tech products (the "Antigravity pattern"):

1. **Fire 3-5 Google News RSS queries** with different angles (product name, "vs competitor", "how to install", "review")
2. **Extract headlines + sources** to build a landscape map
3. **Search npm/pip registries** to find real ecosystem packages — they tell you the CLI name (`agy`), auth methods, known bugs
4. **Guess landing page URLs** — try `productname.google.com`, `productname.com`
5. **Check local installation** — `which`, `npm ls -g`, `pip list | grep`
6. **Synthesize from headlines** — don't wait for article content. Headline confidence-tiering works.

## Product Profile (as of June 9, 2026)

| Attribute | Detail |
|-----------|--------|
| **Name** | Google Antigravity 2.0 |
| **Category** | Agentic development platform |
| **Launch** | Google I/O 2026 (May 20) |
| **Predecessor** | Gemini CLI (rebranded) |
| **CLI name** | `agy` |
| **Components** | Desktop app, CLI, SDK, Managed Execution, AI Studio (Android) |
| **Model** | Gemini 3.5 Flash |
| **Competitors** | Claude Code, OpenAI Codex, Cursor |
| **Pricing** | Free tier + $100/month AI Ultra |
| **npm package** | NOT published (`@google/antigravity` = 404) |
| **Landing page** | https://antigravity.google.com |
| **Security** | Fake downloads circulating — Malwarebytes warning |

## Ecosystem (15+ npm packages by June 9)

| Package | Purpose |
|---------|---------|
| `opencode-antigravity-auth` | OAuth for Opencode → Gemini 3 Pro / Claude 4.6 via Google creds |
| `unofficial-antigravity-sdk` | TypeScript SDK port |
| `opencode-agy-bridge` | Route LLM prompts to agy CLI |
| `openclaw-antigravity` | OpenClaw provider plugin |
| `agy-superpowers` | Skills library, scaffold `.agent/` |
| `eagle-mem` | Shared memory across Claude Code, Codex, Antigravity, Grok |
| `antigravity-awesome-skills` | 1,525+ agentic skills |
| `oh-my-oma` | Multi-agent workflow orchestration |
| `antigravity-projects-fix` | Fix for duplicate projects bug |
| `pi-antigravity-rotator` | Multi-account rotation proxy |

## Claude Code Status (WSL)

```
Version: 2.1.150
Path:    /home/habib/.local/bin/claude
Config:  ~/.claude.json + ~/.claude/ 
Status:  Installed, needs re-authentication (last used May 25)
```

## Recommendation to Haris

| Task | Tool | Why |
|------|------|-----|
| Existing codebase work | Claude Code | Precise, terminal-first, mature |
| Greenfield prototypes | Antigravity | "Describe and build" paradigm |
| Multi-agent orchestration | Antigravity SDK | Agent chaining for gstack |
| Enterprise compliance | Antigravity | Google enterprise support |
| Daily coding | Claude Code | Battle-tested, known workflow |
| Weekend experiments | Antigravity | Free tier, Desktop GUI |

## For Next Time

When this topic resurfaces:
- Check if `@google/antigravity` is on npm yet
- The Desktop app may need Windows-side installation (download from antigravity.google.com)
- Re-authenticate Claude Code with `claude login`
- Test both against `ideas-exitlens` repo for a real comparison
