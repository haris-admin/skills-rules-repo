---
name: railway-docker-image-release
description: Build, publish and prove a Docker-image release of a React single-page app plus Express API on Railway, with Supabase and observability keys. Use when asked to build or push an image for staging or a demo, when a Railway service pulls a Docker Hub image, when browser keys (Sentry, PostHog, Supabase anon) must change, or when proving which commit and which database a live host is running.
---

# Railway Docker image release (React + Express + Supabase)

A repeatable runbook from the Simplifii-OS 8 Oct 2026 workshop release. It ties together four rules in this repo:
`release-image-from-clean-export`, `build-time-browser-keys-prove-on-live-bundle`, `deploy-state-needs-independent-reads` and `supabase-migrations-compare-by-name-never-db-push`.

## When to use

- A Railway service's Source is a Docker image, not a GitHub repo.
- A build must carry a specific commit, database and set of public browser keys.
- You need to prove, from outside, what a live host is running.

## Authority

You may build and push an image tag when the owner asks. Pointing Railway at the tag, redeploying, changing Railway or Supabase settings, rotating keys and any production release are the owner's steps. Never print or store a key, host or project id.

## Steps

1. **Pick the commit.** Write down the full sha. Check it is on the remote and CI is green on it (read the run on a repo where runners execute). Confirm the working tree is not the source: other agents may have uncommitted work.
2. **Export it.** `git archive <full-sha> | tar -x -C <new scratch dir>`. Build only from there.
3. **Collect build inputs by key.** From the env file, extract only the named keys (never `source` it): the database URL and anon key for the target project, the demo flags, `REACT_APP_POSTHOG_KEY` and `REACT_APP_POSTHOG_HOST`, `REACT_APP_SENTRY_DSN`. Add `REACT_APP_BUILD_SHA` and `APP_BUILD_SHA` set to the full sha. Pass them as `--build-arg NAME` with no value.
4. **Build.** `docker build --platform linux/amd64 ... -t <repo>:<full-sha> -t <repo>:<version>[-suffix] .` If it fails with a process killed or resource exhausted message, it is memory: retry once, then ask the owner to free memory or raise the Docker limit. Do not stop their containers.
5. **Boot and inspect locally.** `docker run -d -p 3993:3001 <repo>:<tag>`; `curl localhost:3993/api/health` must return `ok` and the full sha. Fetch the served JavaScript and compare browser keys to the env file in code, printing only `True` or `False`. Confirm the target database is present and the production one is absent.
6. **Push the tag, read it back.** `docker push`, then `docker buildx imagetools inspect <repo>:<tag>` for the digest. Keep earlier tags for rollback. Do not move `latest`.
7. **Hand over the exact tag.** Tell the owner the full image reference to put in Railway (Settings, Source) and to deploy. An "Invalid Docker image" message is usually a typo, a stray prefix such as `docker pull`, or a transient registry check; verify the tag pulls anonymously (registry token + `HEAD /v2/<repo>/manifests/<tag>` returns 200) before debugging further.
8. **Prove the deploy with independent reads.** Live `/api/health` sha equals the intended sha; the served bundle filename changed; the browser keys in the live bundle match the env file; smoke test passes against the host (the smoke test's base URL must come from `PLAYWRIGHT_BASE_URL`, not a hard-coded retired host); a signed-in seat or test account works. Record each with the time and the host, in the shared notes, keeping older text marked superseded.
9. **Server-only changes need only a redeploy.** `SENTRY_DSN`, `CRISIS_ALERT_EMAIL`, service-role keys and similar runtime variables take effect on redeploy; browser `REACT_APP_*` values need a new image.

## Database and migrations

Use `supabase-migrations-compare-by-name-never-db-push`. Audit with read-only management-API queries; apply nothing to production without the owner's release word.

## Verification checklist

- [ ] Built from a clean export of a named full sha
- [ ] Health sha, bundle keys and database project verified locally before the push
- [ ] Digest read back from the registry
- [ ] Owner deployed; live health sha, bundle hash and smoke test verified from outside
- [ ] Shared notes updated with dated independent reads
