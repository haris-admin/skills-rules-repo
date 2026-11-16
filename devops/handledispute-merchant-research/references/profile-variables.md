# Hermes profile variables

Hermes profile configuration. On 16 Nov 2026, the owner chose `HANDLEDISPUTE_AGENT_KEY` as the shared name for the Hermes credential and its AWS Secrets Manager field. The owner will update the Hermes agent to read that name; this document does not establish that the running agent has been changed.

| Variable | Value | Notes |
|---|---|---|
| `PLUTO_HERMES_HANDLEDISPUTE_BASE_URL` | `https://api.handledispute.com.au` | Full URL with `https://`, no trailing slash, no path. Production requires HTTPS. |
| `HANDLEDISPUTE_AGENT_KEY` | the agent key | Secret. Use the value of `HANDLEDISPUTE_AGENT_KEY` in AWS Secrets Manager `handledispute/secrets/prod`. Keep it in the worker's private `.env` or secret store, never in an instruction, note, source file or log. |
| `PLUTO_HERMES_HANDLEDISPUTE_INTERVAL` | poll seconds (60) | Positive whole number. |
| `PLUTO_HERMES_HANDLEDISPUTE_ALLOW_INSECURE_LOCAL` | `false` | For a local test against `http://localhost` only. Must be `false` or unset in production. |

Search providers in the Hermes worker's own store: Exa, Tavily, Brave, Serper and Firecrawl. Perplexity is no longer used (owner, 16 Nov 2026: no key).
