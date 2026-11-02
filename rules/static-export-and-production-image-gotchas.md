# Static export, production image and small-instance gotchas (all agents, all repos)

Applies to Next.js static export hosting, Python Docker images and NAT or small EC2 instances.

## Why this exists

**1 Nov 2026, handledispute (prod-issues 041, 042, 043, 045, 046).**

## Rules

1. Next.js `output: "export"`: metadata routes need `export const dynamic = "force-static"`; pages cannot read server `searchParams`
   (read the query in a client component). Headers belong in the host config (`public/_headers` or nginx), not `next.config`.
2. nginx on an export: a path with a trailing slash can match a payload directory with no index and return 403. Redirect trailing slashes to the slash-less page.
3. Python images: build the venv at its final path (builder `WORKDIR` equals runtime), set `PYTHONPATH` to the app root so the Alembic launcher imports the app,
   and create writable data, log and upload dirs for the non-root user. Run `alembic --version` inside the built image before deploying.
4. Build `linux/amd64` on an arm64 Mac. Pin base image tags.
5. A NAT instance below t3.micro runs out of memory during `dnf`. Add swap and `user_data_replace_on_change`, and make dependents wait for the network.
6. Production never serves `/docs`, `/redoc` or the OpenAPI schema. Pin it with a test.
7. A usage-limited secrets script must be behavioural-tested with a stub `aws` and must never print values.
8. **No literal `localhost` API origin in a static export.** On 2 Nov 2026 a grep found 18 `http://localhost:8008` fetches with no env fallback (merchant portal sign-in, Operations desk, communication controls, unsubscribe), which on the live site target the visitor's own machine. Route every call through one shared `getApiBaseUrl()`, add a unit guard that fails on a literal outside that helper, and grep the built `out/` for `localhost` before each release.
9. **Media on nginx:** serve `.vtt` as `text/vtt` (the alpine mime table lacks it), keep `video/mp4`, and check `Range` returns 206. Verify playback in real Chrome, not bundled Chromium (no H.264).
10. **A new release id for every change.** A deploy that compares the running image tag skips the recreate when only config changed in the image. Dev-only folders (for example a capture project that imports test helpers) must not ship in a release tree: they can break `next build` type-checking on an older base.
