# Secret-scanning false positives — patterns worth knowing before you report

A naive `grep -ri password` or default secret-scanner run over a real project repo throws a
lot of noise. These are the recurring shapes of "looks like a leak, isn't one" — and the
ones that look benign but actually deserve a Low/Medium anyway.

## Usually not a finding

- **`.env.example` / `.env_example`** — placeholder values (`your-api-key-here`,
  `changeme`, `xxx`). Confirm it's actually a placeholder (open it) before dismissing —
  don't assume every `.env*` file is safe just because of the name.
- **Seed / fixture scripts** — a script whose entire purpose is inserting synthetic test
  data (drivers, cards, transactions, payments) with hardcoded fake IDs and dummy
  card/account numbers is not a credential leak. Confirm the values are synthetic (an
  Oxygen sandbox card ID, a `CLV-REF-SHIFT-TEST-01`-shaped test reference) and don't
  correspond to a real production account.
- **Test files** — hardcoded dummy JWTs, API keys, or bearer tokens used purely to drive
  unit/integration tests against a mocked or local service.
- **Documentation / runbook examples** — a skill or README showing the *shape* of a
  command with an obviously fake value (`<password>`, `***`) filled in.

## Usually still worth flagging, at a calibrated severity — not zero

- **A real password committed in a comment**, even for a dev/staging-only resource that's
  already firewalled behind a bastion/tunnel (e.g. a commented-out `DATABASE_URL` line in a
  checked-in `.env` pointing at a dev DB reachable only via an internal port-forward). The
  network boundary reduces blast radius, but the credential is still committed to git
  history for anyone with repo access, and deleting the comment later doesn't remove it from
  history. This is a real Low/Medium: "don't commit real credentials even for non-prod
  resources — use a secrets manager or an untracked local file, and rotate this one," not a
  Critical (it isn't a live public credential), and not nothing.
- **A production credential**, however "just for dev convenience" the excuse — always
  Critical/High regardless of where it's committed.
- **A working webhook signing secret, third-party API key, or SSH private key** anywhere in
  the tree, including old commits still in `git log -p` even if removed from HEAD.

## A note on agentic/sandboxed audit environments

If this audit is run from inside an agent harness with its own permission layer, some
generic commands (talking to a live remote credential store, or reading from a designated
production host) may require explicit human approval independent of the target codebase's
own security posture. Treat a harness-level approval prompt as a normal part of the
process, not a finding about the code under audit — and don't try to script around it;
surface it to the user and let them approve or decline.

## Verification step before reporting any secret hit

1. Is the value real (matches a live account/service you can positively identify), or
   synthetic/placeholder?
2. Is it still live — i.e. still committed at `HEAD`, not just in old history that's been
   rotated since? (Still report history-only leaks — rotation should be confirmed, not
   assumed — but say so explicitly: "present in history at `<sha>`, appears rotated/removed
   at HEAD.")
3. What's the actual blast radius if someone with repo read access used it right now?

That last answer sets the severity — don't default to Critical for every regex hit.
