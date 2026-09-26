# Runtime Files Must Survive the Build Ignore List

Any file the server reads at runtime (rules, prompts, templates, data) must be in a format and path the production image actually copies, and a test must prove it.

## Why this exists

Simplifii-OS, 26 Sep 2026: the plan was to move AURA's safety rules into a reviewable markdown file under `api/`. The repo's `.dockerignore` drops every `*.md` except `README.md`, so the file would have been missing on the server while every local test passed. Local checkouts, Jest and eval scripts all see the file; only the built image does not.

## Rule

1. Before adding a runtime data file, read `.dockerignore` (and any `COPY` lines in the Dockerfile, or the platform's include rules) and confirm the path and extension ship.
2. Prefer `.txt` or `.json` for runtime data. Keep `.md` for documents people read.
3. Load it once at startup, not per request, and fail loudly at startup if it is missing or cut short (for example, check for an end marker). A missing safety rule must stop the server, never run without it.
4. Add a test that fails when the file matches an ignore rule or is absent from the image's copy list.

## Related

- `deployed-vs-local-code-parity.md` (what is deployed is not what is local)
