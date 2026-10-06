# Scratch Copies Of An App Never Include Env Files

A throwaway copy of an app that is built or served locally (a production-build proof, a real-server test, a clean-worktree build) must never carry `.env*` files, and must never run publish, webhook or notify hooks against real keys. Applies to every agent and subagent that builds or serves a scratch copy.

**Scope:** any agent making a scratch, temporary or isolated copy of an application to build or run it (worked example: an AMLHive Next.js proof run, 6 Oct 2026).

---

## Why this exists

An earlier scratch run copied `.env.local` into its throwaway directory. The first call to the app's on-demand revalidate hook then sent a real IndexNow submission for two production URLs, because the copy held real keys. A scratch copy that carries real keys is not a sandbox: a "local" test made an outbound call to a third party with production credentials.

## Core Directives

1. **Build from a commit, not a working tree.** `git archive <sha> | tar -x -C <empty scratch dir>`. An archive holds tracked files only, so ignored env files cannot ride along.
2. **Delete every `.env*` and assert it.** After export, and again after any copy or install, `find <dir> -name '.env*' -not -path '*/node_modules/*' | wc -l` must print `0`. Non-zero is a stop.
3. **Run servers under `env -i` with an explicit allowlist** (for example `PATH`, `NODE_ENV`, `PORT`, `HOSTNAME`, and stub URLs). Never inherit the shell environment, which may hold real tokens.
4. **Bind to loopback only** (`127.0.0.1`). A scratch server is never reachable from the network.
5. **Never run a publish, webhook, notify or revalidate hook against real keys.** Read the route's source before the first call to find outbound calls (search-engine pings, IndexNow, email, chat, payments). Point them at stubs, or leave the keys unset so they fail closed.
6. **Stub the backend.** A real-server proof talks to a local stub, never to production or to a dev backend with real data.
7. **Say it in every builder prompt:** "do not copy any `.env*` file".
8. **Install fresh in the scratch copy** (for example `npm ci --legacy-peer-deps`). A stale local `node_modules` can fail the build with a misleading error such as `Cannot find module @vercel/turbopack/postcss`.

---

## Patterns to Follow

```bash
SCRATCH=<empty dir>
git archive <sha> | tar -x -C "$SCRATCH"
find "$SCRATCH" -name '.env*' -not -path '*/node_modules/*' | wc -l    # must print 0
env -i PATH="$PATH" NODE_ENV=production PORT=3999 HOSTNAME=127.0.0.1 node server.js
```

---

## Patterns to Avoid

```bash
cp -R app /tmp/app-copy && cd /tmp/app-copy && npm start     # copies .env.local, inherits the shell env
curl -X POST localhost:3000/api/revalidate                    # first call can reach real third parties
```

---

## Verification & Guardrails

- The `find ... | wc -l` assertion is part of the scratch-run script and exits non-zero on a count above 0.
- Related: `rules/release-image-from-clean-export.md`, `rules/agent-tooling-secrets-protection.md`, `rules/no-secret-masking.md`, `rules/subagent-dispatch-authorization-boundary.md`.
