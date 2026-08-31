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

3. **Nginx & Reverse Proxy Configuration**:
   - Test configurations with `nginx -t` before reloading (`nginx -s reload` or `systemctl reload nginx`).
   - Always enforce HTTPS/TLS with strong cipher suites and HSTS headers.
   - Set appropriate rate limiting and timeout configurations (`proxy_connect_timeout`, `proxy_read_timeout`).

4. **Monitoring & Health Checks**:
   - Expose lightweight `/healthz` or `/livez` endpoints for orchestrator probes.
   - Configure alert thresholds on CPU, memory, error rate spikes (5xx), and API response latency.
