# Brainy Strategic Review Pattern

**Last used:** June 2, 2026 | **Purpose:** Fleet strategic code review via subagent delegation

## What It Is

Brainy is a subagent role that performs strategic code review of any fleet project. It produces a structured assessment with star ratings, specific file-path-cited issues, and a prioritized improvement roadmap. Use it after major builds or before Haris reviews a project.

## When to Use

- After completing a build phase on any `ideas-*` project
- Before Haris reviews a project — pre-empt issues he'd find
- When Haris says "engage Brainy" or "get Brainy to review"
- As the final step of the Ideas→Development pipeline

## How to Invoke

Use `delegate_task` with a goal that explicitly names "Brainy" and sets expectations:

```python
delegate_task(
    goal="You are Brainy, the fleet's strategic analysis agent. Conduct a thorough review of [PROJECT] and provide your assessment.",
    context="""## What to Review
The full codebase at /mnt/c/Code/gitlab/[repo]/

Read these key files:
- README.md, PRD.md, ASSESSMENT.md — product context
- docs/OPEN_SPEC.md, docs/ARCHITECTURE.md — design docs
- src/backend/ — all Python files
- src/app/ — all frontend pages
- src/lib/ — shared modules
- tests/ — all test files
- Configuration files (pytest.ini, package.json, etc.)

## Deliverable
Produce a structured review with:

1. **Star Rating** (1-10) with brief justification
2. **What's Working Well** (3-5 strengths)
3. **What Needs Improvement** (3-5 specific issues with file paths and concrete fixes)
4. **To Make It 10 Stars** — the specific changes needed, prioritized (table: #, Change, Effort, Impact)
5. **Architecture Score** (1-10) — separation of concerns, modularity, data flow
6. **Test Coverage Score** (1-10) — unit/integration ratio, edge cases, real vs mock
7. **Production Readiness** (1-10) — would you deploy this to paying customers today?
8. **Overall Verdict** — one paragraph summary

Be specific. Cite file paths. Give concrete suggestions, not vague criticism. This is for Haris — be direct and useful.""",
    toolsets=["file", "terminal"]
)
```

## Output Format

Brainy's review should follow this structure:

```
## 1. Star Rating: X/10
[Justification in 1-2 sentences]

## 2. What's Working Well
- **Strength name:** Detail with specifics

## 3. What Needs Improvement
| # | Issue | Severity | Location |
|---|-------|----------|----------|

## 4. To Make It 10 Stars
| # | Change | Effort | Impact |
|---|--------|--------|--------|

## 5. Architecture Score: X/10
## 6. Test Coverage: X/10
## 7. Production Readiness: X/10
## 8. Verdict
```

## Proven Results (PayLicence AU, June 2 2026)

Brainy reviewed 48 tests, 10 source files, architecture docs, and produced:
- **Star rating:** 6/10 with specific justification
- **5 issues identified** with file paths and concrete fixes
- **10-item prioritized roadmap** (P0→P3) with effort and impact estimates
- **Key finding:** Critical end-to-end flow was broken (report page disconnected from API) — something unit tests passed but integration revealed
- **Token cost:** ~450K input, ~6K output (DeepSeek v4 Pro)

## Pitfalls

- Brainy reads files, not executes them — it can't run `pytest` or `npm run build` itself. Tell it to use the `terminal` tool to verify claims
- Brainy needs explicit file paths in the context — it has no prior knowledge of the project structure
- Don't use Brainy for line-by-line code review (use `github-code-review` skill for PRs). Brainy is for strategic assessment
- Brainy's review is a self-report — cross-check its file-path claims against the actual repo before acting on them
