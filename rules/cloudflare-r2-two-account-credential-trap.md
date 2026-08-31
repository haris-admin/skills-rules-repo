# Cloudflare R2 two-account credential trap (all agents)

Applies whenever debugging staleness, `AccessDenied`, or write failures against
`content.yourapp.com.au` or any R2-backed blog/content storage path.

## Why this exists

YourApp uses **two separate Cloudflare accounts** for R2, each holding a bucket literally named
`yourapp-blog-content`:

- `R2_ACCOUNT_ID` (`0f9ad05aed2ef935f572d55cf6e4b8b8`) — the *primary blog bucket* account,
  reached with `R2_ACCESS_KEY_ID`/`R2_SECRET_ACCESS_KEY`. This is where
  `backend/scripts/sync_blog_content.py` and the primary `BlogService` writes go.
- `CLOUDFLARE_ACCOUNT_ID` (`3183e033d01cca3f99bfd9d8e2670f9a`) — the *zone-owning* account (owns
  the `yourapp.com.au` DNS zone and the `content.yourapp.com.au` custom domain), reached with
  `R2_PRIMARY_ACCESS_KEY_ID_HHSIDDIQUI`/`R2_PRIMARY_SECRET_ACCESS_KEY_HHSIDDIQUI`. This is the
  *only* account/credential pair that can write something `content.yourapp.com.au` will ever
  serve.

An R2 client's endpoint URL must be built from the account ID matching the credential pair in use
(`https://{account_id}.r2.cloudflarestorage.com`). Testing the `_HHSIDDIQUI` credentials against
`R2_ACCOUNT_ID`'s endpoint (or vice versa) produces a misleading `AccessDenied` that looks like a
bad/revoked key, when the credentials are actually fine and just pointed at the wrong account.
Writing to the wrong account looks **exactly like a Cloudflare cache bug** from the outside: the
write appears to succeed (visible via that account's own `pub-<hash>.r2.dev` URL), but the custom
domain never shows it, and a cache purge changes nothing — because no cache was ever involved.

## Rules

1. **Before assuming `content.yourapp.com.au` staleness is a cache issue, check
   `cf-cache-status`** on the response and try a `purge_cache` call first. If the response doesn't
   change after a purge, stop looking at caching — the write almost certainly landed in the wrong
   R2 account.
2. **`cf-cache-status: DYNAMIC` on every request combined with a no-op purge is the tell** that
   this is an account/binding problem, not a cache problem.
3. **Always pair the account ID with its matching credential pair explicitly** — never assume
   "the R2 credentials" means one specific account without checking which `R2_*`/`CLOUDFLARE_*`
   env var pair the code path in question actually reads.
4. **An `AccessDenied` on an R2 call is not proof the key is bad or revoked** — check the account
   ID in the endpoint URL against the account ID the credential pair belongs to before concluding
   the key itself needs rotating.

## Related

- `openspec/changes/133-content-mirror-full-site-parity/` — root-cause and remediation writeup
  (12 Jul 2026)
- [aws-profile-and-secret-recovery.md](aws-profile-and-secret-recovery.md) — the equivalent
  wrong-account trap on the AWS side
