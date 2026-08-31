# Agent tooling secrets protection — ignore files per tool (all agents, all repos)

Applies whenever setting up or materially touching agent-tooling configuration in **any**
repository, not just this one. `.gitignore` controls what gets committed; it does not stop an
agentic tool with broad file-access settings from *reading* a secret into its context even if that
secret would never be committed. These are a separate, defense-in-depth control.

## Why this exists

**3 Jul 2026:** while setting up Antigravity-specific rules/skills for this repo's AWS/Cognito
migration work, it became clear `.gitignore` alone doesn't stop an agent from reading a `.env` or
credential file into context. The user's instruction: "make sure that none of them are actually
exposing the passwords. Put this in every repo that we create going forward."

**Verify each tool's actual mechanism first — do not assume a `.<tool>ignore` file exists or is
enforced just because the pattern worked for another tool.** Confirmed as of 3 Jul 2026 research:

| Tool | Real mechanism | Confidence |
|---|---|---|
| Cursor | `.cursorignore` (repo root, gitignore syntax) | High — long-established |
| Gemini Antigravity | `.antigravityignore` | Medium — newer product, converging but not 100%-official-doc-confirmed |
| Gemini CLI | `.geminiignore` (+ global `~/.gemini/.geminiignore`) | High — confirmed official docs. **Caveat: filters auto-discovery only — explicit `@file` reference still loads it.** Also has a separate built-in refusal on sensitive filenames + env-var redaction (TOKEN/SECRET/PASSWORD/KEY/AUTH/CREDENTIAL/PRIVATE/CERT) independent of this file. |
| Windsurf (Codeium) | `.codeiumignore` (+ global `~/.codeium/`) — **not** `.windsurfignore` | High — confirmed official docs. **Caveat: `!negation` patterns don't reliably override `.gitignore`.** |
| Claude Code | **No `.claudeignore`.** That filename does not exist/is not honored — multiple 2026 reports of Claude Code reading "denied" files anyway when people assumed it existed. The real, working mechanism is `permissions.deny` rules in `.claude/settings.json` (repo-level, checked in — not `settings.local.json`), e.g. `"deny": ["Read(./.env)", "Read(./**/*.tfvars)", ...]`. | High for `permissions.deny` being real; the `.claudeignore` myth is the actual trap to avoid. |
| OpenAI Codex | No confirmed shipped `.codexignore` as of this writing — multiple open/contested GitHub issues, unclear ship status. Creating the file costs nothing and may already work in some builds, but **do not rely on it.** The real backstop is an explicit "never read/print secret files" instruction in `AGENTS.md`, which Codex does confirmedly read (order: `AGENTS.override.md` → `AGENTS.md` → `TEAM_GUIDE.md` → `.agents.md`). | Low for the ignore file; High for the AGENTS.md instruction being the actual control. |
| Devin (Cognition) | **No repo-local ignore-file mechanism at all.** Secrets live in Devin's own org-level Secrets Dashboard, injected into Devin's environment, never read from repo files; `.env` should simply be `.gitignore`d as normal. There is nothing to create in the repo for this. | High (confirmed via docs.devin.ai) — but the finding itself is "no file exists," not a pattern to copy. |

## Rules

1. **Treat this as a default step of onboarding any repo to agent tooling**, the same way
   `.gitignore` is a default step of `git init` — do it proactively, don't wait to be asked
   per-repo.
2. **Minimum pattern set** for tools with a real ignore-file mechanism (adapt to the repo's actual
   stack): `.env`/`.env.*` (keep `.env.example`), cloud credential files (`.aws/`,
   `**/credentials`, `*.pem`, `id_rsa`/`id_ed25519`), IaC state/vars (`*.tfvars` minus `.example`,
   `*.tfstate*`, `.terraform/`), and any `*_secret*`/`*_credentials*` JSON or dump files.
3. **For tools without a real ignore-file mechanism (Codex, Devin), don't fake one.** Use the
   documented real control instead — an explicit instruction in `AGENTS.md` for Codex, keeping
   secrets out of the repo entirely for Devin.
4. **When adding a new ignore file, do a quick grep sweep** (secret-shaped patterns: AWS access
   keys, PEM headers, `password=`/`password:` with a literal value, `user:pass@host` connection
   strings, long bearer tokens) over whatever files were just written/edited in that session, to
   catch anything that leaked into a doc or spec before the ignore file existed to prevent it.
5. **Re-verify a tool's mechanism before copying this table into a new repo or a long time later** —
   these products change fast; a "Medium" or "Low" confidence entry above especially may have
   shipped or changed since 3 Jul 2026.

## Related

- `.claude/settings.json` `permissions.deny` — this repo's working example of the Claude Code
  mechanism
