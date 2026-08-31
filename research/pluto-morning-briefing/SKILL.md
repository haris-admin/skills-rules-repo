---
name: pluto-morning-briefing
description: Pluto's morning briefing compilation and delivery — the output-side of the research pipeline. Use when compiling the daily brief, writing LinkedIn/blog ideas from research signals, or delivering briefings via email/Telegram. The briefing format, portfolio cross-referencing, and email delivery patterns live here.
allowed-tools: [read_file, write_file, terminal, execute_code, skill_manage]
---

# Pluto Morning Briefing — Compilation & Delivery

## When to Use
- Compiling the daily morning briefing from research JSON
- Writing LinkedIn post ideas mapped to portfolio projects
- Generating blog post ideas with content gap analysis
- Delivering briefings via email (himalaya) and Telegram
- Delivering daily learning sessions from MemPalace knowledge bases (Moonshots, podcasts)
- Any session where Pluto delivers research output directly to Haris (no Gumby intermediary)

## Operational Context

**As of June 4, 2026, Pluto delivers the full morning briefing directly.** No Gumby handoff. No `gumby-brief-input.md` intermediary. The pipeline is: Research → Synthesis → Briefing → LinkedIn/Blog Ideas → Voice → Email × 2 → Telegram.
The `pluto-autonomous-research` skill covers the research pipeline (Phases 0-4). This skill covers the output side (Phases 5-10): briefing format, content ideation, email delivery, and daily learning sessions.

**Related skills created June 6, 2026 (Saturday auto-improvement cycle):**
- `pluto-gmail-signal-ingestion` — Gmail pipeline details (formerly inline in pluto-autonomous-research Phase 0b)
- `pluto-linkedin-content-engine` — LinkedIn/blog ideation pipeline details
- `pluto-honcho-signal-bridge` — Honcho bridge operations and debugging
- `pluto-pipeline-orchestration` — Full 20-stage cron pipeline map with known issues

**Deduplicated skills (covered by existing umbrellas):**
- `pluto-intelligence-pipeline` → covered by `pluto-autonomous-research` (Phase 0-11) + `pluto-pipeline-orchestration`
- `pluto-cross-chamber-synthesis` → covered by `pluto-mempalace-bridge` (Synthesizer section)
- `pluto-gumby-feedback-loop` → covered by `pluto-mempalace-bridge` (Feedback Processor section)
- `pluto-weekly-research-digest` → covered by `pluto-autonomous-research` (Phase 7)
The `pluto-autonomous-research` skill covers the research pipeline (Phases 0-4). This skill covers the output side (Phases 5-10): briefing format, content ideation, email delivery, and daily learning sessions.

## Daily Learning Sessions

For knowledge bases stored in MemPalace chambers (e.g., Moonshots podcast transcripts, business podcast directories), Pluto can deliver daily learning sessions that teach a concept and quiz Haris. The format and cron setup are documented in `references/daily-learning-format.md`.

The Moonshots Daily Learning cron (`0fb6bf47f704`, 6:15 AM AEST) uses this format, alternating between `critical-infra` and `startup-vc` chambers.

## Briefing Report Format

Write to `~/.hermes/research_outputs/morning-briefing-YYYY-MM-DD.md`. The format has been battle-tested on June 4, 2026 with 300+ headlines across 5 topics.

### Section 1: Header
```markdown
# 🌑 Pluto Morning Briefing — Day, Date Month Year
**Generated:** 5:05 AM AEST | **Topics:** comma-separated
**Signal Balance:** Topic ratio | Topic ratio ⚠️ | Topic ratio
```

### Section 2: 🚨 TOP SIGNALS
Each finding gets its own subsection:
```markdown
### 🔴/🟡/🟢 📜/🔒/📈/💰 [Signal Title]

[Content — 2-3 paragraphs summarizing the finding with key facts]

**Sources:** Publication, Publication, Publication
**Confidence:** HIGH/MEDIUM/LOW (reason) | **Type:** regulatory|threat|market|trend|opportunity

> **For Haris:** [Actionable insight tying the signal to a specific portfolio project + recommended action]
```

**Severity marking rules:**
- 🔴 CRITICAL — direct portfolio impact, time-sensitive (legislative window, security breach)
- 🟡 HIGH — relevant but not immediate
- 🟢 MONITOR — background intelligence, tailwind confirmation

**Type emojis:** 📜 regulatory, 🔒 security/threat, 📈 market, 🤖 tech/trend, 💰 funding, 📋 licensing

**Confidence tiering:**
- HIGH = 5+ credible publications, or primary sources (ASIC, Treasury, law firms)
- MEDIUM = 2-3 credible publications
- LOW = single source or second-hand aggregation

### Section 3: 📊 SIGNAL BALANCE AUDIT
Table format:
```
| Topic | Pro | Con | Ratio | Status |
|-------|-----|-----|-------|--------|
```
Flag any ratio > 5:1 with ⚠️ and note counter-sweep recommendation.

### Section 4: 🔗 PORTFOLIO IMPACT MAP (INTERNAL ONLY)
Cross-reference table mapping signals → internal signal domains (not product names). This is for Pluto's routing — never shared externally:
```
| Signal | ESOP/CGT | Payments | Digital Assets | AI Gov | Cloud |
|--------|----------|----------|---------------|--------|-------|
```
Use: 🔴 LAUNCH NOW, 🟡 Content/Monitor, 🟢 Tailwind, — (no impact)

**This table must use signal domains, never product names.** AML Hive is NEVER included — it has its own separate stream.

### Section 5: ✍️ LINKEDIN POST IDEAS
3-4 post drafts, each with:
- **Hook:** 1-2 sentence grabber with specific data point or news hook
- **Angle:** 2-3 sentences connecting the news to Haris's thought leadership expertise
- **CTA:** 1 sentence engagement prompt
- **Content Pillar:** Map to one of: AI Agents & Governance, Australian Fintech Regulation, Cloud & Resilience, Startup & ESOP

**ZERO commercial product names in any LinkedIn post.** Reference expertise domains, not specific products. AML Hive is NEVER a valid LinkedIn reference.

## Podcast Content Pipeline (NEW June 2026)

The morning briefing now pulls content ideas from the Supabase podcast knowledge base. This avoids YouTube rate limits by using multiple acquisition strategies.

### Content Sources (Priority Order)

1. **YouTube descriptions** (yt-dlp --print description) — NOT rate-limited. Contains timestamps, topics, show notes. The primary source for episode content when transcripts are blocked.
2. **Full transcripts** (youtube-transcript-api) — rich but IP-rate-limited. Use with 90s delays between requests. Run overnight.
3. **Manual synthesis** (Moonshots knowledge base JSON) — hand-curated episode summaries with frameworks and quiz questions.

### Creator Channels to Monitor

| Creator | Platform | Channel/Handle | Content Type |
|---------|----------|---------------|-------------|
| Moonshots | YouTube | @moonshotsclips | AI, geopolitics, future of work |
| Lenny's Podcast | YouTube | @lennyspodcast | Product, growth, AI |
| Silicon Valley Girl | YouTube | @siliconvalleygirl | AI founders, tools, startups |
| Allie K. Miller | LinkedIn | linkedin.com/in/alliekmiller | AI business, Claude Code tips |
| Allie K. Miller | Substack | alliekmiller.substack.com | Newsletter |
| Allie K. Miller | Inc.com | inc.com/author/allie-miller | AI productivity column |

### Transcript Acquisition Strategy

When YouTube blocks transcript API (HTTP 429):
1. **DO NOT retry aggressively** — backoff makes it worse
2. **Use yt-dlp --print description** for immediate content (not blocked)
3. **Set 90s delays** and run overnight for full transcript repair
4. **Website scraping** only works for non-JS-rendered sites (most podcast sites ARE JS-rendered — skip this)

### Attribution Rules (MANDATORY for all podcast-sourced content)
- Always credit: Podcast Name, Episode Title, Host(s), Date
- For direct quotes: quotation marks + speaker attribution
- For frameworks/ideas: "As discussed on [Podcast] ([Episode], [Date])"
- Never present podcast-sourced insights as original research

### Section 6: 📝 BLOG POST IDEAS (harishabib.au)
2-3 blog ideas, each with:
- **Pillar:** Content pillar
- **Gap filled:** What gap in existing posts does this fill?
- **Companion:** Which existing post does this pair with?
- **Angle:** 1-2 sentence description

**Existing blog posts to cross-reference:**
1. The Docker Moment for AI Agents
2. The Human-AI Partnership: A Framework for Safe Adoption
3. Resilience Engineering in the Cloud
4. The 2026 Budget Changed the ESOP Question

### Section 7: ⏱️ TIMELINE & ACTIONS
Priority table:
```
| Priority | Action | Deadline | Owner |
```

## Email Delivery (Phase 9 Equivalent)

Send to BOTH recipients every time:
- `hhsiddiqui@gmail.com`
- `admin@harishabib.au`

### Method: File-Based Pipe (CRITICAL — heredocs time out)

Do NOT use heredocs in terminal() — they consistently time out with BLOCKED status. Instead:

```bash
# Step 1: Write email to temp file
write_file("/tmp/email-body.txt", content)

# Step 2: Pipe file to himalaya
terminal("cat /tmp/email-body.txt | himalaya template send")
```

**Email format (plain text):**
```
From: Pluto Research <macarthurgarments@gmail.com>
To: recipient@domain.com
Subject: Pluto Morning Briefing — FULL REPORT — Day Date Month Year

[Content with severity markers: [RED], [YELLOW], [GREEN]
Include: top signals with >> action items, LinkedIn ideas, blog ideas, critical actions]
```

**DO NOT use execute_code read_file/write_file for email rewriting** — the hermes_tools read_file prepends line numbers (`1|From:...`) which corrupts the MML format, causing himalaya to return "cannot parse MML message: empty body." Always use the native write_file tool directly.

**For the second recipient:** modify only the To: line. The rest of the content is identical. Write a fresh file (don't use execute_code for string replacement on the first file — line numbers corrupt it).

### Proven delivery sequence (June 4, 2026):
1. Write full email to `/tmp/email-full-report.txt` with `To: hhsiddiqui@gmail.com`
2. `cat /tmp/email-full-report.txt | himalaya template send` → success
3. Write second file `/tmp/email-admin-full.txt` with `To: admin@harishabib.au`
4. `cat /tmp/email-admin-full.txt | himalaya template send` → success

## Content Ideation Rules

### LinkedIn Post Quality Gates
- Hook must include a specific data point or event (not generic)
- Angle must connect to Haris's specific expertise/portfolio
- CTA must be engagement-driving (question, DM invite, link)
- Every post maps to exactly one content pillar
- Never fabricate statistics — use numbers from the research findings

### Blog Gap Analysis
- Check against existing harishabib.au posts (27 live as of June 2026)
- Identify which content pillars are underrepresented
- Each idea fills a specific gap in the existing catalog
- Recommend a companion post (existing post to pair with for internal linking)
- **AML Hive is NEVER a valid blog topic for harishabib.au** — separate entity

### Kanban Tracking (NEW June 9, 2026)
Every content-related action must create a corresponding Kanban task for full visibility:
- Blog posts → Kanban card with pillar, portfolio tie, deadline
- LinkedIn ideas → Kanban card when selected for execution
- Content pipeline changes → Kanban card for tracking
- All future tasks visible in backlog with priority and time estimates

## Saturday "About Haris" Weekly Briefing (NEW June 9, 2026)

**Cron:** `9a13f666d918`, schedule `0 7 * * 6` AEST (7 AM Saturday)
**Skills:** `fleet-intelligence`, `honcho-setup`
**Deliver:** `origin` (direct to Telegram)
**Output:** `~/.hermes/research_outputs/about-haris-YYYY-MM-DD.md`

A lightweight ~20-line Saturday briefing with ONE focus: what Pluto learned about Haris that week. Format:

```
# 🌑 Pluto Saturday Briefing — About Haris — Day, Date Month Year

## What I Learned About Haris This Week
[5-10 bullet points — NEW observations only, never recycled]

## Signal Check
[Pattern: more hands-off vs more hands-on, trust level, recurring asks]

## Action for Next Week
[One thing Pluto should do differently based on these learnings]
```

Rules:
- Only NEW observations from the current week. No recycling old facts.
- Source from Honcho context, session transcripts, corrections received.
- If genuinely nothing new was learned, say so honestly.
- Never fabricate observations to fill the 5-10 line quota.

TTS voice (OpenAI Nova) is generated inline during the 6:00 AM morning briefing (`c527fed4a1da`). For immediate delivery during manual briefing compilation:

```bash
cd ~/.hermes && /home/habib/.hermes/venv/bin/python3 scripts/voice_overview.py YYYY-MM-DD
```

Output goes to `~/.hermes/voice_outputs/pluto_briefing_YYYY-MM-DD.mp3`. Deliver via Telegram with `MEDIA:/path/to/file.mp3` in the response.

## Pitfalls
- **Heredoc pipes in terminal() time out for himalaya.** Always use file-based pipe pattern.
- **execute_code read_file corrupts MML format** — prepends line numbers like `1|From:...` which breaks himalaya parsing.
- **Don't forget the second email.** admin@harishabib.au must receive every briefing alongside hhsiddiqui@gmail.com.
- **Blog gap analysis must reference the 4 existing posts.** Don't propose ideas that duplicate what's already published.
- **LinkedIn posts must remain pure thought leadership.** Never reference Haris's own product names. Reference expertise domains (AI governance, fintech regulation, cloud resilience, startup/ESOP) — not products. Third-party product mentions are fine.
- **Signal balance audit is mandatory.** Never deliver a briefing without the audit table.
- **Time-aware delivery.** Server is UTC. The briefing is compiled at ~5:20 AM AEST. Don't use "good morning" in cron-triggered deliveries unless you verify Sydney time.
- **YouTube transcript blocks produce error text, not real content.** When querying podcast_kb for content ideas, always filter: `AND e.transcript_text NOT LIKE '%YouTube is blocking%' AND e.transcript_text NOT LIKE '%Could not retrieve%'`. Otherwise you'll pull error messages posing as transcripts (51 of 66 episodes affected as of June 4).
- **Podcast attribution is mandatory.** Never present podcast-sourced frameworks or quotes as original. Format: "As heard on [Podcast Name] ([Episode Title], [Date])". See Section 5a.
- **🔴 AML Hive firewall:** AML Hive must NEVER appear in morning briefings, LinkedIn ideas, or blog post suggestions for Haris Habib. These are separate entities. AML Hive content lives on amlhive.com.au only.
- **🔴 Zero Haris products (harishabib.au + LinkedIn):** harishabib.au and Haris Habib LinkedIn must never mention Haris's own startup products. Third-party commercial products (Snyk, Sysdig, Microsoft, AWS) are fully allowed. Blog post ideas and LinkedIn drafts must reference expertise domains — never Haris's product names. The only exception: free utility tools that provide standalone value without promoting any personal paid product.
- **Kanban tracking:** Every content action needs a Kanban card. Haris wants full visibility of all agent activities via the board.
- **Two-stream content separation:** Always present content recommendations as two distinct streams: (1) Haris Habib (harishabib.au + LinkedIn) — opinion only, no products. (2) AML Hive (amlhive.com.au) — compliance/regtech, completely separate.
- **Daily Learning frameworks bottleneck:** Only Moonshots Podcast has populated `frameworks[]` arrays. All 14 other podcasts have empty `{}` arrays. The `array_length(e.frameworks, 1) > 0` filter effectively returns ONLY Moonshots episodes, breaking the "alternate podcasts" rule. Use the two-stage query in `references/daily-learning-format.md` instead — prefer frameworks when available, but fall back to any transcript-populated episode from another podcast when frameworks are empty.
- **psql column truncation:** Default psql output silently truncates long text fields (transcript_text). Always use `-t -A` (tuples-only, unaligned mode) when querying transcripts. Example: `psql -t -A -F $'\t' -c "SELECT substring(e.transcript_text, 1, 6000) ..."`

## Reference Files
- `references/podcast-kb-infrastructure.md` — Full Supabase podcast_kb schema, yt-dlp patterns, channel handles, bug history, cron jobs
- `references/daily-learning-format.md` — Daily learning session format and cron setup
