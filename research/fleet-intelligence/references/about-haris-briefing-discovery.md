# About Haris — Interactive Session Discovery

## Problem

When compiling the Saturday "About Haris" briefing, `session_search()` browse mode returns ONLY recent cron sessions. Default queries like "Haris OR habibi OR habib interaction" match cron job prompts (which contain "Haris's portfolio", "Haris's interests"), not actual user interactions. Finding genuine interactive sessions requires targeted discovery.

## Discovery Pattern (proven June 13, 2026; refined same day)

### Step 0: Check the Friday Weekly Review FIRST
Before searching sessions, read the most recent weekly review:
```
~/.hermes/reviews/weekly/weekly-review-YYYY-MM-DD.md
```
The "📊 By the Numbers" table tracks `User interactions (non-cron)` explicitly. The "Honest Assessment" section states whether Haris engaged at all. This is the single most authoritative source — if it says "0 interactions," session_search will confirm it, not contradict it. A finding of "zero interactions" from both sources is trustworthy and saves deep session_search digging.

### Step 1: Search with role_filter="user" only
```python
session_search(limit=5, role_filter="user", sort="newest")
```
The `user` role filter removes all cron-injected system prompts and leaves only sessions where a human wrote a message. Interactive sessions show source=`telegram` or `cli`; cron sessions show source=`cron` even with user messages (because cron prompts are injected as user messages).

### Step 2: Check source field on matches
Look for sessions where `source` is NOT "cron":
- `"telegram"` — Haris messaged via Telegram bot
- `"cli"` — Haris used CLI or Kanban task command

### Step 3: Search for specific interaction patterns
If Step 1 returns only cron sessions, try:
```
session_search(query="deploy blog commit OR push OR GitLab", role_filter="user,assistant", sort="newest")
session_search(query="separate entity OR completely independent OR different entities", sort="newest")
```

### Step 4: Scroll into found sessions
Once an interactive session is found, use `session_search(session_id=..., around_message_id=...)` to scroll through the full conversation. The `bookend_start` and `bookend_end` show first and last messages — key for understanding the session's purpose and outcome.

### Step 5: Extract learnings from user messages
Focus on messages where `role="user"` — these are Haris's direct words. Look for:
- Directives ("deploy it", "add this", "remove that")
- Corrections ("don't mention AML Hive")
- Frustrations ("why are my memories almost full")
- Preferences ("I want..." / "Make sure...")
- New information shared (projects, tools, constraints)

## Typical Yield

From the June 13, 2026 run:
- 2 interactive sessions found (June 8 Telegram, June 9 CLI)
- 8 new observations about Haris extracted
- ~40 messages scrolled per session for full context
- Most valuable signal: Haris's user messages (role="user"), not assistant responses

## Pitfalls

- **Cron prompts masquerade as user messages:** Cron job prompts are injected as `role="user"` with `source="cron"`. Always check the `source` field, not just the role.
- **Broad queries match cron injection text:** Cron prompts reference "Haris's portfolio", "Haris's interests", etc. — these match FTS5 queries for "Haris" even though no human is present. Use narrow, interaction-specific terms.
- **Honcho may not have peer cards:** Self-hosted Honcho < 3.x returns "No profile facts available yet" for all peers. This is not an error — rely on session_search instead.
- **session_search alone is not authoritative for "zero interactions":** A search returning no results could mean no interactions OR a search gap. Always cross-reference with the Friday weekly review (Step 0) — its `User interactions (non-cron)` metric is the ground truth. When the review says 0 and session_search also returns 0, the finding is reliable. When they disagree, trust the review and widen the search.
