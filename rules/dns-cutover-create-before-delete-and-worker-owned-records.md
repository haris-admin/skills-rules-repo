# DNS cutover: create before delete, handle empty bodies, detach Worker-owned records (all agents, all repos)

Applies to any scripted change of live DNS or Cloudflare settings.

## Why this exists

**1 Nov 2026, handledispute.com.au:** a cutover script detached a Worker custom domain, crashed on the empty response body, and left the
apex and api with no records. The site returned 530 until repaired. A second Worker custom domain then held `www` as a read-only record.

## Rules

1. Create the new records first, delete the old ones last, so a mid-run failure never leaves a name with no answer.
2. API clients treat an empty 2xx body as success and a non-JSON body as a failed result, never as a crash. Test both.
3. A record with `meta.read_only` or `origin_worker_id` belongs to a Worker custom domain. List the Worker domains in the dry run
   and detach them only under a decision the owner has recorded.
4. Take a backup before every apply and keep `--rollback`. A re-run must be idempotent and show only the remaining steps.
5. Verify from outside after every apply with `curl --resolve <host>:443:<cloudflare IP>`. The local resolver caches negative answers.
6. Email, SPF, DMARC, DKIM and verification records are never touched. Guard the zone name in code, not by convention.
