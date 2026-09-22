# DevOps & Deployment Safety Guidelines

Guidelines for infrastructure management, deployment automation, Docker containerization, and release safety.

## Operational Standards

1. **Deployment Safety & Zero Downtime**:
   - Always run linting, static checks, and unit tests before initiating deployment pipelines.
   - Implement rolling updates or blue-green deployments to prevent service disruption.
   - Ensure database migrations are backwards-compatible (expand before contract).

2. **Docker & Container Hygiene**:
   - Use multi-stage Dockerfiles to minimize final production image sizes.
   - Never run container processes as `root`; create a dedicated unprivileged user (`USER appuser`).
   - Pin base images and package dependencies to prevent unexpected breaking changes during builds.
   - **`docker-compose.yml`'s `environment:`/`env_file:` only apply at container RUNTIME — they do
     NOT populate a Dockerfile's build-stage `ARG` declarations.** For any Dockerfile that declares
     `ARG` for framework env vars baked into the build (`REACT_APP_*`, `VITE_*`, `NEXT_PUBLIC_*`),
     the compose service needs an explicit `build.args:` list, or `docker compose up --build` ships
     a bundle with every such var undefined. The failure looks like a broken `.env` file, not a
     compose bug — the app throws "missing required env var" at runtime, and the actual root cause
     (no build-stage passthrough) is easy to miss because the container otherwise starts fine.
     Confirmed live 23 Sep 2026 (Simplifii-OS-Main): `docker-compose.yml` had zero `build.args`
     despite the Dockerfile declaring ~30 `ARG`s, so every local `docker compose up --build` shipped
     a bundle with `REACT_APP_SUPABASE_URL` undefined. Fix: list every such `ARG` under
     `build.args:` (bare-key syntax sources the value from Compose's own auto-loaded `.env`);
     re-check this whenever either the Dockerfile's `ARG` list or `docker-compose.yml` changes,
     since the two can drift independently with no error until someone actually rebuilds.

3. **Nginx & Reverse Proxy Configuration**:
   - Test configurations with `nginx -t` before reloading (`nginx -s reload` or `systemctl reload nginx`).
   - Always enforce HTTPS/TLS with strong cipher suites and HSTS headers.
   - Set appropriate rate limiting and timeout configurations (`proxy_connect_timeout`, `proxy_read_timeout`).

4. **Monitoring & Health Checks**:
   - Expose lightweight `/healthz` or `/livez` endpoints for orchestrator probes.
   - Configure alert thresholds on CPU, memory, error rate spikes (5xx), and API response latency.
