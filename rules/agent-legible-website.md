# Agent-legible website (markdown twins, llms files, content negotiation)

Every public website should give AI agents a clean, machine-readable version of what humans see: the same facts, never more, never staler, and read-only until a deliberate change allows agent actions.

## Why this exists

From an AMLHive build on 26 Sep 2026 (markdown twins of every public page plus an Atom feed). The review and first build hit five traps: a route handler in a private folder that never routed while its unit tests passed, prices hidden in client state that no agent could see, a negotiated response without `Vary: Accept`, an agent-facing cache that outlived an unpublished post, and a converter that stripped consent text along with the form controls.

## Surfaces

| Surface | Purpose |
|---|---|
| `/llms.txt`, `/llms-full.txt` | Curated map and full context for AI assistants. Link each page's `.md` version (llmstxt.org convention). |
| Markdown twin | `text/markdown` version of a page at `<path>.md` and via `Accept: text/markdown` on the canonical URL. Home page twin at `/index.md`. |
| Feed (Atom/RSS) | Tells agents when new content exists. The only place XML is the right format for agent content. |
| JSON-LD | Hard facts (organisation, offers, prices, FAQ). Must match visible content. |
| `/.well-known/*` | Agent card, MCP manifest, API catalog. Describe only what really exists. |

## Rules

1. **Prove routes in the real build.** A unit test that imports a route handler's `GET` does not prove the route exists. Check the built route manifest or request the path from a running production build. In the Next.js App Router, an `_`-prefixed folder is private and never routable.
2. **Parity with humans.** Every fact visible to a human, including content revealed only by client-side state (price toggles, tabs, countdowns), must be in the twin or the llms files. Keep a registry of client-only components and a test that fails when a new one is unlisted.
3. **Never show agents what humans cannot see.** Clear agent-surface caches on the same event that changes the human page (CMS publish/unpublish hook). Never cache a non-200 response, a redirect, or a maintenance page.
4. **Negotiate correctly.** Send `Vary: Accept` on every response of a negotiable URL, HTML and markdown alike. Parse q-values: `text/html, text/markdown;q=0.5` gets HTML. Prefer the `.md` URL for shared caches, since many CDNs ignore `Vary` unless configured.
5. **Convert content, not controls.** Select the main content region, remove inputs, buttons, scripts, styles and decorative icons, and keep consent text, legal wording, step numbers, FAQ answers and tables. Use a real HTML parser; regex parsing breaks on nested elements.
6. **Carry boundary text.** Legal and regulatory disclaimers usually live in the footer, outside the main region. Add them to every twin's header.
7. **Twins are alternates, not pages.** Exclude them from the sitemap and send `X-Robots-Tag: noindex` plus `Link: <canonical>; rel="canonical"`.
8. **Outage is not absence.** A backend error returns 503 with `Retry-After`, never a 404 or an empty 200. Check whether your data source returns an empty list on failure.
9. **Self-fetching your own pages:** use `127.0.0.1` rather than `localhost`, do not follow redirects, set a timeout, and de-duplicate concurrent cache misses.
10. **Read-only by default.** Agent-discovery documents advertise no action URLs until a deliberate change adds them. In regulated products, an agent may create an account but a person accepts the terms and starts the trial or payment.

## Related

`rules/public-discoverability-crawler-access.md`, `rules/new-public-page-registration-checklist.md`, `rules/public-claim-audit.md`.
