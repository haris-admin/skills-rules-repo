# Prod issue numbering (all agents)

Applies when creating or renaming files under `prod_issues/`, `backend/prod_issues/`, or `frontend/prod_issues/`.

## Global sequence

Issue IDs are **one shared sequence** across all three folders. The next ID is **one higher than the highest `issue-NNN` filename in any folder** (currently **103** after 102).

```bash
ls backend/prod_issues/issue-*.md frontend/prod_issues/issue-*.md prod_issues/issue-*.md 2>/dev/null \
  | sed 's/.*issue-//' | sed 's/-.*//' | sort -n | tail -3
```

## When to use the same ID in multiple folders

| Situation | Action |
|-----------|--------|
| One prod defect spans **frontend and backend** | **Same ID**, one file per layer — e.g. issue **050** in both `frontend/prod_issues/` and `backend/prod_issues/`. |
| Fix lives in **one layer only** | **One ID**, one file in that layer. Header must say `**Layer:** Frontend only` or `**Layer:** Backend only`. |
| **Never** | Reuse an ID for a different bug because the number is “free” in one folder (052/053 are pool timeout and agent onboarding — not SEO). |

## Search before you number

Before logging a new issue, search the register for the same symptom (the URL, the error text, the
file). Simplifii-OS logged the bare-domain TLS failure as ISSUE-044 on 26 Sep 2026 while ISSUE-006
already held it; the duplicate was merged by pointing 006 at 044. Likewise, a register row marked
"Done" is a claim: re-read the cited file and lines before relying on it (a "Done" feature row
pointed at markdown-rendering code, and the feature was only partly built).

## After creating a file

1. Add a row to `prod_issues/README.md` § Index.
2. Cross-link related issues in the same doc (`issue-088` ↔ `issue-089`).
3. Reference the ID in tests, skills, or rules when the issue is a regression guard.

## Examples

- **088** — frontend-only SEO canonical bug → `frontend/prod_issues/issue-088-….md` only.
- **068** — backend-only audit PDF → `backend/prod_issues/issue-068-….md` only.
- **050** — auth session bug → matching files in `frontend/prod_issues/` and `backend/prod_issues/`.
