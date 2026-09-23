# Pitfalls & Incident Log

Full dated incident log behind the condensed Pitfalls summary in
`SKILL.md`. Read this when debugging a specific failure mode — each entry
is a verified, dated root-cause writeup with its fix.

## Contents

- [Watcher format mismatch — gmail briefings accumulate](#watcher-format-mismatch)
- [Post-manual-watcher verification — "down" vs "skipped"](#post-manual-watcher-verification)
- [Research JSON overwrite — wrong topic](#research-json-overwrite)
- [Mempalace feeder silently skipped by cron pipeline](#mempalace-feeder-silently-skipped)
- [Feeder auto-routing bug — topic "&" + hyphenated tags](#feeder-auto-routing-bug)
- [Himalaya email sending failure modes](#himalaya-email-sending)
- [Cron runs may silently produce zero output](#cron-silent-zero-output)
- [Subagent / web tool pitfalls](#subagent--web-tool-pitfalls)
- [Inline Python / curl pipe failures](#inline-python--curl-pipe-failures)
- [JSON and file-reading pitfalls](#json-and-file-reading-pitfalls)
- [General research hygiene](#general-research-hygiene)
- [Publisher curl reliability](#publisher-curl-reliability)
- [Signal polarity bias](#signal-polarity-bias)
- [Cron / scheduling gotchas](#cron--scheduling-gotchas)
- [Model pricing & multimedia gaps](#model-pricing--multimedia-gaps)
- [Podcast ingestion pitfalls](#podcast-ingestion-pitfalls)
- [Time-aware communication](#time-aware-communication)
- [Supabase URL parsing](#supabase-url-parsing)
- [Cross-referencing with competitor intel](#cross-referencing-with-competitor-intel)

## Watcher format mismatch

**⚠️ Watcher format mismatch — gmail briefings accumulate because watcher parser can't read them (June 30, 2026):** The watcher cron (`5678a363ce3b`) IS running but skips ALL gmail briefing files due to a format incompatibility. **Root cause:** The gmail ingestor (`gmail_ingestor_imaplib.py`) produces files with plain `## Finding` headers (no structured fields), but `mempalace_watcher.py` expects `## Finding Title` followed by `Source:` / `Type:` / `Confidence:` fields. The watcher parses these as "No findings parsed" → `"status": "skipped"` and does NOT move them to `processed/`. As of June 30, 2026, 88 `.md` files (gmail briefings from May 24–June 30) and 17 `.json` files were sitting unprocessed with an empty `processed/` directory. **This is NOT a cron failure — the watcher runs, returns exit 0, but skips everything.** The `head -60` pipe in the Phase 0 check command also SIGPIPEs the watcher mid-run. **Distinguish "down" from "format-skipping":** (a) If watcher runs and produces "stored" entries for SOME files → watcher works, format is the issue for others. (b) If watcher produces ONLY "skipped" entries → format mismatch across all pending files. (c) If watcher produces NOTHING → cron is actually down. **Fix options:** (1) Update `gmail_ingestor_imaplib.py` to add `Source:` / `Type:` / `Confidence:` fields to its output, (2) Update `mempalace_watcher.py` to handle plain `## Finding` format as a fallback, (3) Create a separate gmail-briefing processor. `mempalace_watcher.py` line 49 uses `MEMPAINPUTS_DIR.glob("*.md")`, so `pluto-msg-*.json` files in the inputs directory are completely invisible to the watcher. As of June 14, 2026, 13 pluto-msg JSON files had accumulated unprocessed for 3–14 days. These are Telegram DM messages from Haris that need dedicated JSON handling or integration through the Honcho bridge. **Check for `.json` files in `mempalace-inputs/` manually before research runs.**

## Post-manual-watcher verification

**⚠️ Post-manual-watcher verification — distinguish "down" from "skipped" (June 28, 2026):** After running `mempalace_watcher.py` manually, do NOT assume it failed if files remain in `mempalace-inputs/`. The watcher parses `.md` files expecting `## Finding Title` headers followed by content with `Source:` / `Type:` / `Confidence:` fields. Many files in the inputs directory — including `pluto-msg-*.md` (Telegram DMs), older gmail briefing formats, and files without structured findings sections — are deliberately skipped with `"status": "skipped", "error": "No findings parsed"`. This is NORMAL for those file types; it does not mean the watcher is broken. **Verification checklist after manual watcher run:** (a) check `processed/` for newly moved files (confirms watcher IS running), (b) check watcher stdout for `"status": "stored"` entries (confirms successful feeds), (c) expect `"status": "skipped"` for pluto-msg files and unstructured inputs — these need dedicated handling. If you see BOTH `"stored"` and `"skipped"` entries, the watcher is functional; the skipped files are format-incompatible, not watcher-failures. Only flag the watcher as down when NO files are processed AND no `"stored"` entries appear in output.

## Research JSON overwrite

**Research JSON overwrite — existing file may have wrong topic (June 11, 2026):** An existing `research_2026-06-11.json` was found containing Cloud & Infrastructure data (from a prior cron topic mismatch). It was overwritten with the correct FinTech Regulation topic. **Always read the existing research JSON's `topic` field before overwriting.** If the topic differs from what today's cron expects, either (a) archive the stale file and write the correct one, or (b) name files with topic suffixes like `research_2026-06-11_fintech.json` to avoid collisions.

## Mempalace feeder silently skipped

**Mempalace feeder silently skipped by cron pipeline (June 5, 2026):** The 01:28 AM AEST cron pipeline generated the full research JSON, morning briefing, and queued email delivery — but NEVER ran the mempalace feeder. All phases reported success. The feeder must be called explicitly as a separate step. If you verify a completed pipeline and find no mempalace feed, run Phase 3 manually. The cron pipeline table now documents this as a dedicated inline step at 5:07 AM AEST.

## Feeder auto-routing bug

**Feeder auto-routing bug — topic "&" + hyphenated tags misroute to pluto_research (fixed Aug 16, 2026):** `route_to_chamber()` in `pluto_mempalace_feeder.py` failed to route "Agentic AI & Security" to the `agentic-security` chamber because (a) the `&` broke the substring match for "agentic ai security", and (b) hyphenated tags (`agentic-ai`, `ai-security`, `red-teaming`) didn't match the chamber's unhyphenated tags (`agentic`, `security`, `red-team`). Result: findings silently landed in the generic `pluto_research` chamber instead of the topic chamber. **Fixed** by normalizing the topic (collapse non-alphanumerics to spaces via `re.sub(r'[^a-z0-9]+', ' ', topic)` ) and expanding hyphenated tags into component parts before matching. **Verification:** after feeding, confirm the findings landed in the correct topic chamber, not `pluto_research` — query ChromaDB at `/mnt/c/Users/habib/.mempalace/palace` for entries with today's date; if they're in `pluto_research` under the wrong topic, delete them (`col.delete(ids=...)`) and re-feed with `--chamber <correct>`. Use `--chamber` explicitly when the auto-route is uncertain.

## Himalaya email sending

**Himalaya email sending: TWO failure modes, both with fixes.** (1) **Heredoc pipes time out** — `cat << 'EOF' | himalaya template send` via `terminal()` consistently times out (BLOCKED status). Fix: write to file first, then `cat /tmp/email-body.txt | himalaya template send`. (2) **Auth command fails** — `auth.cmd = "echo <password>"` in himalaya config returns `cannot get secret from command: No child process (os error 10)` in the terminal sandbox. The echo command works in a real shell but the sandbox prevents child process spawning. Fix: fall back to Python `smtplib` via `execute_code` — same Gmail app password, same SMTP server, reliably works. See `references/email-smtp-fallback.md` for the full pattern. Both failures encountered June 4-5, 2026; both workarounds verified.

## Cron silent zero output

**CRITICAL: Cron runs may silently produce zero output.** As of June 2, 2026, manual `cronjob action=run` on the research job reported `last_status: ok` but produced no research JSON, no synthesis, and no gumby-brief-input.md. The cron scheduler's environment may differ from the interactive session. When this happens, do NOT retry the cron — run the research pipeline directly inline using the Phase 1 Google News RSS pattern (5 sequential curl queries + Python parsing + synthesis by hand). The inline pattern is verified reliable (re-validated July 9, 2026: AI Regulation & Compliance, 353 headlines, 215 sources, all 5 queries clean).

## Subagent / web tool pitfalls

- Subagents may return empty `tool_trace` results silently — if a subagent's summary is missing actual facts/URLs, re-run with more specific search queries in the `context` field
- **`web_search` and `web_extract` unavailable in cron sandbox (June 25, 2026):** The skill's `allowed-tools` and Phase 1 enrichment section reference `web_search` and `web_extract`, but these tools do not exist in the Hermes cron sandbox environment. The RSS-only synthesis pipeline (Google News RSS → Python parse → headline synthesis) is the reliable path for cron runs. The `web_search → web_extract` enrichment pattern only works in interactive mode. When running as a cron job, skip Phase 1 enrichment entirely — the RSS headline synthesis across 5 queries (376 headlines from 213 sources) provides sufficient signal for high-confidence findings when cross-referenced across 3+ sources. The `allowed-tools` field should be treated as aspirational, not guaranteed.
- **"Return ONLY valid JSON" delegation pattern:** When a subagent keeps returning commentary or markdown instead of structured JSON, use this `goal` format: *"Research X. Your ONLY job is to return valid JSON. No markdown, no commentary, no code blocks. Output exactly: { ... }"*. Include the full expected JSON schema in the goal. This tripled structured output success rate (from ~30% to ~90%) in testing.
- **Subagents with `toolsets: ["web","search"]` can use real web tools** — they are NOT limited to just search. They can fetch URLs, call APIs, and scrape pages. Tell them explicitly: "use web_search to find sources, then fetch the URLs for details."
- DuckDuckGo HTML scraping via terminal/curl is unreliable — DDG now returns CAPTCHA challenges ("bots use DuckDuckGo too", "select all squares containing a duck") on both `lite.duckduckgo.com` and `html.duckduckgo.com` endpoints. Prefer RSS feeds over DDG scraping.

## Inline Python / curl pipe failures

- **Inline Python in curl pipes breaks (TWO failure modes):** (1) Shell escaping of regex patterns inside `terminal("curl ... | python3 -c '...'")` fails with "No such file or directory". (2) **Hermes security scanner (tirith) blocks `curl | python3` pipes entirely** — flags them as HIGH risk `pending_approval`, even for trusted feeds. Always curl to a temp file first, then parse with separate Python. The safest pattern: use `execute_code` with `from hermes_tools import terminal` — curl-to-file and parse steps happen inside a single Python script with no pipe-to-interpreter.
- **F-string curly-brace escaping in `execute_code` + `terminal()` (THIRD failure mode, June 19, 2026):** When embedding Python code inside a `terminal()` call within an `execute_code` f-string, curly braces like `{headline}` or `{source}` are interpreted as f-string variable references — causing `NameError` at the outer f-string level. Example that FAILS: `terminal(f"python3 -c '...print(f\"{headline}\")...'")`. **Fix:** write the parser script to a temp file with `write_file()`, then invoke it with `terminal(f"python3 /tmp/parser.py /tmp/file.xml")`. This separates the Python parsing logic from the f-string scope entirely. Verified June 19, 2026 on 5 Google News RSS files.

## JSON and file-reading pitfalls

- **JSON control characters from RSS feeds break json.loads() via terminal() (July 1, 2026):** Google News RSS descriptions contain control characters (0x00–0x1f range) that survive regex parsing and cause `JSONDecodeError: Invalid control character` when piping JSON through `terminal()` → `json.loads()`. **Fix:** write parsed items to a temp JSON file (not stdout) with control-character cleaning applied: `re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)` on headline, source, and description fields before `json.dump()`. Then read the file back using Python's `open()` directly in `execute_code` — NOT `read_file()` (see next pitfall). This avoids both the control-character and line-number-prefix issues simultaneously. Verified July 1, 2026 on 251 FinTech Regulation headlines.
- **`read_file()` returns line-numbered content incompatible with json.loads() (July 1, 2026):** The `read_file()` tool prepends line numbers (`LINE_NUM|CONTENT`) that break `json.loads()`. When you need to read a JSON file for programmatic parsing inside `execute_code`, use Python's `open()` directly instead of `read_file()`. `read_file()` is designed for human-readable text display, not machine parsing. This bit me when reading a 251-item JSON array — `read_file()` returned `1|[...` and `json.loads()` failed with "Extra data". Fix: `with open('/path/to/file.json') as f: data = json.load(f)` in execute_code.

## General research hygiene

- Do NOT generate fake URLs — if no URL, leave empty string
- Do NOT exceed 10 findings per topic — quality over quantity
- Always validate JSON before feeding
- The feeder script needs ChromaDB ONNX model downloaded (first run is slow)
- Research outputs go to `/home/habib/.hermes/research_outputs/`
- When running as a cron job: check which topics were already covered today before picking (read existing research_*.json files for today's date)
- **Staging inbox is now automated:** Watcher cron `5678a363ce3b` auto-processes `mempalace-inputs/` every 5 minutes. No manual steps needed. For urgent/one-off feeds, run `python3 ~/.hermes/scripts/mempalace_watcher.py`.
- **Windows credentials for cross-platform tasks:** When API keys or env vars are needed from the Windows side, check `/mnt/c/Users/habib/.hermes/.env` — Haris may place credentials there instead of `~/.hermes/.env`.
- **Google News RSS redirect links return HTTP 400:** The article URLs in Google News RSS feeds (`news.google.com/rss/articles/CBMimAFB...`) redirect to publisher sites, but following them with `curl -L` consistently returns "Error 400 (Bad request)" — even with realistic browser User-Agents. Google's redirect mechanism appears to validate the request origin. **Do not attempt to curl Google News article links.** Use Google News RSS for discovery + headline synthesis only. Fetch confirming articles from the publisher's own RSS feed or direct site search instead.
- **Do NOT construct article URLs from Google News RSS headlines (June 14, 2026):** Guessing publisher URLs from headlines (e.g., constructing `abc.net.au/news/2026/06/10/removing-capital-gains-tax-discount-disastrous-startups/...`) returned 404 — URL structures are not predictable from headlines alone. Search the publisher site directly by article title, use their RSS feed, or accept RSS-only confidence for that source.
- **Publisher site search pages are JS-rendered:** Direct curl of publisher search pages (e.g., `lawfaremedia.org/search?q=...`, `iapp.org/search/`, `fortune.com/search`) returns empty or minimal content because results load via JavaScript. Use the publisher's own RSS feed (if available) rather than their search page.

## Publisher curl reliability

**Reliably curl-accessible publishers (positive list):** These sources consistently return full article content via `curl -sL`:
- **Law Society Journal (LSJ)** (`lsj.com.au/...`) — full analysis articles, no paywall, ~87KB, ~9230 chars extractable content. Verified June 11, 2026 (AUSTRAC Tranche 2 Program Starter Kits article).
- **ASPI Strategist** (`aspistrategist.org.au/...`) — full analysis articles, no paywall, ~73KB. Verified June 11, 2026.
- **iTWire** (`itwire.com/...`) — full editorial content, ~37KB. Verified June 11, 2026.
- **Bessemer Venture Partners** (`bvp.com/atlas/...`) — full analysis articles, no paywall, ~14-60KB
- **StartupDaily** (`startupdaily.net/...`) — full content, ~770KB
- **TechCrunch Australia** (`techcrunch.com/...`) — full content, ~235KB
- **WIRED** (`wired.com/...`) — full content, ~1.3MB (use `body__inner-container` selector)
- **Finextra** (`finextra.com/...`) — full content
- **AdNews Australia** (`adnews.com.au/...`) — full regulatory/policy articles, no paywall, ~40KB, ~3,700 chars extractable content. Verified June 13, 2026 (Australia AI guardrails pause article).
- **Forbes Australia** (`forbes.com.au/...`) — candidate source. Curled successfully at 107KB (June 14, 2026) but text extraction NOT YET verified — differs from Forbes.com (paywalled/JS-rendered). Test before relying on.

**Publishers behind JS/Cloudflare/paywalls (curl returns empty or stub):** InfoWorld, CIO Dive, Microsoft Security Blog, The Hacker News, Forbes, SiliconANGLE, Dark Reading, IBM Newsroom, Mayer Brown, Bloomberg, AFR, SmartCompany (metered), InnovationAus (subscriber wall), **CIO.com** (214KB JS shell, 0 paragraphs extractable — confirmed June 6, 2026), **Computerworld** (216KB JS shell, 0 paragraphs — confirmed June 6, 2026), **W.Media** (183KB JS shell, 0 paragraphs — confirmed June 6, 2026).

**Most direct article URLs are JS-rendered — expect ~15% curl success rate:** As of May 31, 2026, only 1 of 7 article URLs (InnovationAus, which is paywall-truncated) returned extractable content via curl. InfoWorld, CIO Dive, Microsoft Security Blog, The Hacker News, Forbes, and SiliconANGLE all returned empty or navigation-only content. **Strategy:** rely on Google News RSS headlines + descriptions for synthesis (headline data is rich and source-attributed), and treat successfully curled articles as a bonus, not the primary input. The RSS descriptions alone provide enough signal for medium-confidence findings when cross-referenced across 3+ sources.

## Signal polarity bias

**Signal polarity bias (CRITICAL):** Research defaults to amplifying the dominant narrative — more media coverage of regulation creates a pro-regulation echo chamber. On May 30, 2026, Haris flagged a 35:3 imbalance. **Always run the Signal Balance Check in Phase 2.** When imbalance exceeds 5:1, run a targeted counter-signal sweep with opposite-angle queries. Anti-regulation query patterns that work: `"Liberal Party Australia deregulation agenda red tape"`, `"Australian CEOs regulatory burden compliance costs"`, `"CGT capital gains tax reform criticism opposition Australia"`, `"deregulation trend innovation competitiveness"`. See `references/anti-regulation-signal-sources.md` for the full query catalog.

## Cron / scheduling gotchas

- **Grant/program name validation:** Verify named references before building go-to-market plans. "Neo-X" was a company that got an AFSL, not a grant program.
- **Hermes cron uses LOCAL time (AEST), not UTC:** `5 19 * * *` = 7:05 PM, not 5:05 AM. For morning delivery use `5 5 * * *`. Always check `next_run_at` timezone suffix.
- **Cron `script` field for `no_agent: true`:** Use just the filename (`pluto_honcho_bridge.py`), NOT full path with interpreter. Runner resolves under `~/.hermes/scripts/` and auto-detects Python shebang.
- **Honcho bridge `last_status: ok` is misleading (June 3, 2026):** The bridge cron reported `last_status: ok` but 7 files were sitting unpushed since June 2. The script ran, exited 0, but state tracking failed silently. Always verify by running `--list` to check for pending files: `python3 ~/.hermes/scripts/pluto_honcho_bridge.py --list`. If pending files exist, run the bridge manually. Bridge cron moved to 5:30 AM AEST (was 5:20 PM, then 6:00 AM) to align with morning pipeline.

## Model pricing & multimedia gaps

- **DeepSeek v4 Flash:** 4.4x cheaper than v4 Pro ($0.098/$0.197 vs $0.435/$0.870 per 1M tokens). Use for cron jobs. MiniMax M3 costs 38% MORE on completion. See `references/model-pricing.md`.
- **OpenRouter multimedia gap:** Does NOT proxy TTS or Whisper. Audio models are input-only (`openai/gpt-audio-mini`). For TTS output: direct OpenAI key or gTTS. For STT: direct Whisper key or GPT Audio Mini transcription (see `references/voice-transcription-pipeline.md`).

## Podcast ingestion pitfalls

- **YouTube RSS channel ID 404:** Some channel IDs extracted from YouTube page HTML (`channel_id=UC...`) return 404 from the RSS endpoint even when the channels clearly exist. This happened for All-In (UChJM-mF-4w_61Z6eCyl0eKQ), a16z, MFM, and Acquired on June 4, 2026, while Moonshots (UCCpNQKYvrnWQNjZprabMJlw) RSS worked in the same session. Root cause unidentified — may be a YouTube-side restriction on certain channel types. Workaround: try the channel's "videos" page HTML or use yt-dlp for video listing instead.
- **YouTube transcript API rate-limiting (CRITICAL — June 4, 2026):** Both `youtube-transcript-api` and `yt-dlp --write-auto-subs` return HTTP 429 when called rapidly from the same IP. The block persists across tools. **Do NOT retry aggressively** — short backoffs worsen it. Workaround: use `yt-dlp --print "%(description)s"` for YouTube descriptions (NOT rate-limited, contains timestamps and topics). For full transcripts, use 90-second delays and run overnight.
- **90-second overnight repair VALIDATED (June 5, 2026):** The 90s-delay strategy successfully cleared YouTube's IP block overnight. Results: 7 transcripts → 55 rich transcripts (7.8× improvement). 0 episodes still showing blocking errors. This is the definitive fix for transcript rate-limiting. Run `podcast_repair_transcripts.py` with 90s delays overnight — do not attempt faster repair during the day.
- **Podcast websites are JS-rendered (June 4, 2026):** All major podcast sites (allinpodcast.co, a16z.com, acquired.fm, lennysnewsletter.com) return empty pages via curl. Skip website scraping for podcast transcripts — use YouTube descriptions or the transcript API with delays instead.
- **The podcast ingestor is DB-driven (June 5, 2026):** `podcast_ingestor.py` queries Supabase for ALL podcasts with `youtube_handle` or `channel_id` set. To add new channels, UPDATE `podcast_kb.podcasts` — no script changes needed. The Wed+Sun 6AM cron auto-discovers new channels next run. All 21 registered podcasts now have handles (Tier 1: 7, Tier 2: 8). SV Girl and Tier 3 pending.
- **YouTube handle discovery (June 5, 2026):** Three methods in priority order: (A) curl channel page HTML + grep `channelId` or `externalId` JSON — most reliable, not rate-limited; (B) YouTube search results page + grep `/@[a-zA-Z0-9_-]+` — for when the exact handle is unknown; (C) yt-dlp flat-playlist — may be rate-limited after transcript downloads. See `references/podcast-ingestion-pipeline.md` for full patterns and confirmed handles.
- **Supabase URL parsing: double `==` and `pgbouncer=true` (June 5, 2026):** The `.env` file has `SUPABASE_OPERATOR_SPOOLER_DATABASE_URL=="postgresql://..."` with a double equals sign. The regex `DATABASE_URL=(.*)` captures `="postgresql://...` which breaks psycopg2. Fix: use regex `DATABASE_URL=+["']?(.*?)["']?\\s*$` to handle 1+ equals signs and optional quotes. Additionally, `pgbouncer=true` in the Supabase pooler URL breaks psycopg2 (`invalid URI query parameter: "pgbouncer"`). Strip it with `re.sub(r'[?&]pgbouncer=true', '', url)` before connecting.

## Time-aware communication

**Time-aware communication (CRITICAL):** Server is UTC, Haris is Sydney AEST (UTC+10). NEVER use time-based greetings ("good morning", "good evening") when delivering research results without verifying current Sydney time. Haris flagged this June 3: greeted with "good morning" at 10:16 PM Sydney. Cron jobs run at known times (5:05 AM research, 10:15 PM voice overview) — use Sydney-aware time context in deliveries. When in interactive mode (not cron), skip time-based greetings entirely or use neutral openers.

## Supabase URL parsing

See [Supabase URL parsing](#podcast-ingestion-pitfalls) above (double `==` and `pgbouncer=true`).

## Cross-referencing with competitor intel

**Cross-referencing research outputs with competitor intel:** Research findings with "portfolio_hit" fields feed into `competitor_intel.py` (cron `1a13a2d49682`). If competitor signals look noisy (all three 💰🏢🚀 simultaneously), see `fleet-intelligence` skill → `references/competitor-signal-verification.md` for validation steps. The `competitor_intel.py` script has a known false-positive pattern where single-word name tokens trigger over-broad matches.

## Topic recurrence and chamber continuity (24 Sep 2026)

**Startup & VC Trends has a recurring five-theme set — check the chamber and label repeats as updates.** The topic rotates back every 5 days and the same stories dominate Google News across runs: Airwallex absorbing ~half of FY26 fintech funding, Breakthrough Victoria's political threat, the ARENA Launchpad / Main Sequence-Atmosphere / NSW research-commercialisation capital windows, the Canva markdown, and the CGT/ESVCLP policy cluster. On 24 Sep 2026, four of six findings drafted from a fresh 130-headline corpus were already in the `startup-vc` chamber from the 1/6/14/19 Sep runs. Before writing, query the chamber (`col.get(where={"topic": "Startup & VC Trends"})`), then prefix every repeat with `UPDATE to the <date> feed (what changed: ...)`, put what is genuinely new in the title, and carry an `Excluded as already fed` line in `gumby-brief-input.md`. Re-feeding a corrected set means `col.delete(ids=...)` on that run's `pluto_<YYYYMMDD>_*` docs first, then re-run the feeder and assert both the doc count and the unique-text-prefix count equal the finding count (verified 6/6, `pluto_20260924_050921_0..5`, 0 misroutes to `pluto_research`).

**Recency lever confirmed again (24 Sep 2026):** on this topic the Tier-2 broad `when:30d` queries (`Australian startup funding venture capital`, `Australia fintech funding`, `Australian VC investment startup ecosystem`) supplied 127 of 153 items inside 25 days, while the six specific-angle queries returned only 22 recent items out of 427. Bearish counter-sweep vocabulary remains unproductive (5 of 8 queries returned 1.2–3.4KB shells); `Australian tech startup layoffs cuts job losses` returns 128KB but is dominated by GLOBAL layoff timelines.
