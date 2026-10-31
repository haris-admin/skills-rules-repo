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
