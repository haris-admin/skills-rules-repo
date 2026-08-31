# W28 Weekly Review — Key Diagnostic Findings

## New Patterns Discovered (July 17, 2026)

### 1. Daily Learning False Negative
- **Cron:** `0fb6bf47f704` (Moonshots Daily Learning, 6:15 AM)
- **Finding:** Cron produces 60-68KB of real LLM output daily → but saves ONLY to `cron/output/0fb6bf47f704/`, NOT to `research_outputs/daily-learning-*.md`
- **Impact:** Friday review reported "0/7" for weeks — 100% false negative
- **Detection command:**
  ```
  ls ~/.hermes/research_outputs/daily-learning-2026-07-1*.md  # Expected: 7 files (actual: 0)
  ls ~/.hermes/cron/output/0fb6bf47f704/2026-07-1*.md        # Actual: 7 files (all 60-68KB)
  ```
- **Fix:** Update cron prompt to include save-to-research_outputs instruction (15 min)
- **Status:** Carried to W29 Dream #5

### 2. Synthesis File Identical-Size Pattern
- **Finding:** Jul 12-14 synthesis JSONs were all 23,740 bytes; Jul 15-16 were all 23,782 bytes
- **Verification:** `diff -q` confirmed files are DIFFERENT (same JSON structure, different content)
- **Lesson:** Identical byte sizes ≠ duplicate output. Always run `diff -q` before flagging.
- **Detection command:**
  ```
  diff -q synthesis_2026-07-12.json synthesis_2026-07-13.json
  ```

### 3. AMLHive Sentry Alert Trend Analysis
- **Method:** Count 🔴 emojis per 11PM monitor file to track severity trend
- **W28 trend:** Jul 11:6 → Jul 12:1 → Jul 13:0 → Jul 14:7 (deploy) → Jul 15:0 → Jul 16:1 → Jul 17:1
- **Patterns identified:**
  - W27's 6 P1 Redis/startup alerts → RESOLVED (zero by Jul 12)
  - Jul 14 deploy-day spike (19-min uptimes, ProgrammingError) → self-resolved
  - PII decryption errors persistent (Jul 14, 16, 17) → 3/7 days, P2 severity
- **Detection command:**
  ```
  for f in ~/.hermes/reviews/fleet/amlhive-monitor_2026-07-1[1-7]_2300.md; do
    echo -n "$(basename $f): "; grep -c "🔴" "$f" 2>/dev/null || echo "0"
  done
  ```

### 4. Cron Output Misrouting (Generalized)
- Daily learning was the first discovered case; pattern may exist for other crons
- Cross-reference checklist when any pipeline cron shows "0 files":
  1. Check `cron/output/<job_id>/` for files matching the date range
  2. If files exist there but not in `research_outputs/`, flag as MISROUTED (not FAILED)
  3. Report: "N/N in cron/output/ (misrouted — not in research_outputs/)"
- Key crons with expected paths:
  - `0fb6bf47f704` → `research_outputs/daily-learning-*.md`
  - `d4d77c41f6c0` → `research_outputs/podcast_insights.md`
  - `2d33c8f9a89c` → `research_outputs/skill-proposals_*.md`

### 5. Competitor Intel Quality Categorization
- **187B** = empty (placeholder JSON)
- **500-1,500B** = near-empty
- **1,500-3,000B** = partial
- **>3,000B** = meaningful
- Report "% meaningful" as pipeline health metric
- W28: 4/7 (57%) meaningful — up from 3/7 (43%) in W27

### 6. Session Search for User Interactions
- Use `role_filter: "user"` to filter cron system messages
- Zero results across entire week = MEDIUM severity (no feedback loop)
- W27+W28: 2 consecutive weeks with zero user interactions
