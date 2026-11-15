# Before saying a push deploys nothing, list the check runs of the pushed commit (all agents, all repos)

Applies whenever you tell the owner what pushing to the main branch will or will not do.

## Why this exists
**15 Nov 2026 (ChargeRail):** the owner was told twice that pushing `main` runs CI only and deploys nothing. It was not true: a Cloudflare Workers Builds integration, connected to the repository in the Cloudflare dashboard and invisible in `.github/workflows`, built and published a second public copy of the site (`workers.dev`) on every push. It showed up only as an extra red check on Dependabot pull requests. The same Cloudflare account also held Workers of two other products.

## Rules
1. Read the workflows AND the external integrations. After the first push, run `gh api repos/<owner>/<repo>/commits/<sha>/check-runs --jq '.check_runs[]|"\(.app.slug) \(.name)"'`; any app other than GitHub Actions is a deploy path until proven otherwise (Cloudflare Workers and Pages, Vercel, Netlify, Railway).
2. State the finding to the owner as a correction, with the evidence, before relying on the earlier claim again.
3. Removing an integration is the owner's decision. With the owner's go-ahead and a token they point to, do it by exact name with a dry run first, refuse if a custom domain or route is bound, and never touch a neighbour's resources in a shared account. Prove it afterwards: push again and confirm the check no longer appears.
4. Add a repository test that fails if the integration's config file comes back.
