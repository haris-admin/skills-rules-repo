# Hermes profile variables

Set in the Hermes profile by the owner on 16 Nov 2026 (the earlier names, which began with the earlier product name, were renamed in OpenSpec 54 and are not read). The instructions file `hermes-agent-instructions.md` deliberately does not name them: it uses `HANDLEDISPUTE_AGENT_KEY` and the fixed base URL.

| Variable | Value | Notes |
|---|---|---|
| `PLUTO_HERMES_HANDLEDISPUTE_BASE_URL` | `https://api.handledispute.com.au` | Full URL with `https://`, no trailing slash, no path. Production requires HTTPS. |
| `PLUTO_HERMES_HANDLEDISPUTE_AGENT_API_KEY` | the agent key | Secret. Same value as `HANDLEDISPUTE_AGENT_KEY`. Never write it in a file, note or log. |
| `PLUTO_HERMES_HANDLEDISPUTE_INTERVAL` | poll seconds (60) | Positive whole number. |
| `PLUTO_HERMES_HANDLEDISPUTE_ALLOW_INSECURE_LOCAL` | `false` | For a local test against `http://localhost` only. Must be `false` or unset in production. |

Search providers in the Hermes worker's own store: Exa, Tavily, Brave, Serper and Firecrawl. Perplexity is no longer used (owner, 16 Nov 2026: no key).
