# Build release images from a clean export of a named commit

Building and publishing a Docker image (or any deploy artefact) for a release or a workshop. Applies to every agent and person who runs a build in a shared working tree.

**Scope:** release engineering where more than one agent edits the same checkout (Simplifii-OS, 5 Oct 2026).

---

## Why this exists

During the 8 Oct release the working tree held another agent's uncommitted `0.70.33` work, including a changed `Dockerfile`, while the release candidate was `b5d5d09d`. `docker build .` copies the tree, not the commit, so building in place would have shipped unreviewed code under the release's name and sha. The image was built from `git archive b5d5d09d` into a scratch folder instead.

## Core Directives

1. **Name the commit, then export it.** `git archive <full-sha> | tar -x -C <new empty scratch dir>`, and build there. Never build a release from a checkout with uncommitted changes.
2. **Tag by full sha, plus a readable suffix.** Use `<repo>:<full-sha>` and a human tag (`0.70.29`, `0.70.29-obs`). Do not move `latest` or a moving branch tag in the same step. A rebuild with different inputs gets a new suffix (`-obs2`), never an overwritten tag.
3. **Bake the sha in twice.** Pass the build-time sha (`REACT_APP_BUILD_SHA`) and a runtime one (`APP_BUILD_SHA`) so `/api/health` can report the commit whatever the hosting platform does.
4. **Boot it locally before pushing.** Run the container, hit `/api/health`, check the sha, and check the baked-in values (see `build-time-browser-keys-prove-on-live-bundle.md`). Then push.
5. **Read env files by key, never `source` them.** `.env.local` often has unquoted values (`NIXPACKS_START_CMD=node server.js`); sourcing it runs `server.js` as a command and aborts the build script. Extract the named keys with `grep`, `cut` and `sed`, export them, and pass `--build-arg NAME` with no value so nothing is printed.
6. **An out-of-memory build is not a code failure.** `react-scripts build` with a 4 GiB heap can exceed a 7.7 GiB Docker VM that is shared with other containers. Retry once; if it fails again, tell the owner to free memory or raise the limit. Do not stop their running containers.
7. **Pick the platform deliberately.** Build `--platform linux/amd64` for Railway even on an Apple Silicon Mac.
8. **Deploying is the owner's step.** Pushing an image tag is allowed when asked; pointing the hosting service at it, and deploying, is done by the person with the platform access. Verify afterwards from outside: health sha, bundle filename, smoke test.

---

## Patterns to Follow

```bash
mkdir /scratch/export-<sha8> && git archive <full-sha> | tar -x -C /scratch/export-<sha8>
cd /scratch/export-<sha8>
getv() { grep -E "^$1=" /path/.env.local | tail -1 | cut -d= -f2- | sed -e 's/^"//' -e 's/"$//'; }
export REACT_APP_SUPABASE_URL="$(getv REACT_APP_SUPABASE_URL)"
docker build --platform linux/amd64 --build-arg REACT_APP_SUPABASE_URL --build-arg REACT_APP_BUILD_SHA -t repo/app:<full-sha> -t repo/app:<version> .
```

## Patterns to Avoid

- `docker build .` in a dirty shared checkout.
- `set -a; . ./.env.local; set +a` in a build script.
- Overwriting `latest` or a tag that staging or production currently runs.
- Declaring "deployed" from a push log; check the live health sha.
