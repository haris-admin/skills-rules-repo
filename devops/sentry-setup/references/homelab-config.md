# Haris HomeLab Sentry Configuration (Updated Jul 2026)

## Organization
- **Slug**: `amlhive-pty-ltd`
- **API URL**: `https://sentry.io/api/0/organizations/amlhive-pty-ltd/`

## Projects

| Project | Slug | Sentry Project ID | DSN |
|---------|------|-------------------|-----|
| Python FastAPI | `python-fastapi` | `4511291847213056` | `https://b3c61ef2f55...@o4511291833516032.ingest.us.sentry.io/4511291847213056` |
| JavaScript Next.js | `javascript-nextjs` | `4511291872706560` | `https://004932f784dba8b737e7fbcbde51c56c@o4511291833516032.ingest.us.sentry.io/4511291872706560` |

## Environment Variables (Windows `.hermes/.env`)

```
SENTRY_DSN=https://b3c61ef2f...@o4511291833516032.ingest.us.sentry.io/4511291847213056
SENTRY_AUTH_TOKEN=sntryu_78a5... (71 chars, sntryu_ prefix)
```

## Current Next.js Integration

- **Project**: `cloudproof-au` (Next.js 16.2.7)
- **Config files**: `sentry.client.config.ts` + `sentry.server.config.ts` + `sentry.edge.config.ts`
- **Build wrapper**: `next.config.ts` with `withSentryConfig`
- **Test page**: `src/app/test/page.tsx` — has manual send button UI
- **Static export**: `output: \"export\"` — client-side Sentry works, source maps not uploaded
- **Sentry DSN set via**: `NEXT_PUBLIC_SENTRY_DSN` container env var
- **Reason for 0 events**: Static export has no server runtime — only client-side JS errors from real users trigger events. Server-side errors (Next.js proxy failures, nginx issues) appear in CloudWatch `/amlhive/frontend` and `/amlhive/frontend-system`, NOT in Sentry.

## Permission Notes

The `SENTRY_AUTH_TOKEN` has only `project:read` scope.

**What works with `project:read`:**
- ✅ `GET /api/0/projects/{org}/{project}/` — project info
- ✅ `GET /api/0/projects/{org}/{project}/stats/?stat=received&resolution=1d` — event counts
- ✅ **`GET /api/0/projects/{org}/{project}/events/?full=true&limit=20`** — actual event details (title, level, message, groupID, dateCreated). This is the workaround for the missing `event:read` scope.

**What returns HTTP 403:**
- ❌ `GET /api/0/projects/{org}/{project}/issues/?statsPeriod=24h&limit=5` — needs `event:read`
- ❌ `GET /api/0/organizations/{org}/issues/?project={id}` — needs `event:read`

**Key insight (found 07 Jul 2026):** The `/events/` endpoint works with `project:read` scope and returns event-level details that can be grouped by `groupID` to reconstruct unique issues. This is the correct endpoint for automated monitoring with the current token. The `/issues/` endpoint requires `event:read` which the current token lacks.

## DSNs Used By Deployed Apps

| App | DSN | Project ID |
|-----|-----|------------|
| Backend (FastAPI on EC2) | `https://b3c61ef2f55...@o4511291833516032.ingest.us.sentry.io/4511291847213056` | `4511291847213056` |
| Frontend (Next.js on EC2) | `https://004932f784dba8b737e7fbcbde51c56c@o4511291833516032.ingest.us.sentry.io/4511291872706560` | `4511291872706560` |
