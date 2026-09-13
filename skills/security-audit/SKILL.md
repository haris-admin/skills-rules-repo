---
name: security-audit
description: >-
  Perform a structured, tool-assisted security audit of a codebase — secret/credential
  exposure, injection and auth flaws, dependency CVEs, and infra/config misconfigurations.
  Produces a severity-ranked, file:line-anchored findings report, each finding verified
  (not just pattern-matched) before it's reported. Use when asked to audit security, scan
  for secrets, review code for vulnerabilities, or before a release/PR that touches auth,
  payments, external input handling, or infra config.
---

# Security Audit & Vulnerability Assessment

## Scope & rules of engagement

- **Read and report — do not exploit.** Confirm a vulnerability is real (trace the data
  flow, don't just pattern-match), but never actually run an injection payload against a
  live system, exfiltrate real data, or demonstrate a working exploit. Describe the class
  of problem and the concrete fix.
- **Static analysis of the working tree** — don't scan against production, don't hit
  external endpoints, don't use found credentials to authenticate anywhere.
- A finding you can't trace to an actual reachable code path is a **candidate**, not a
  finding — see "Verify before reporting" below. Don't pad the report with theoretical
  OWASP-category boilerplate that doesn't correspond to real code in this repo.
- If the codebase has its own security/compliance skill (data residency, sector-specific
  rules), run that too — this skill covers generic AppSec, not regulatory obligations.

## Severity rubric

Use this consistently — "Critical/High/Medium/Low" without a definition is meaningless to
a team triaging a report.

| Severity | Definition | Example |
|---|---|---|
| **Critical** | Unauthenticated remote code execution, full auth bypass, or direct access to another user's/tenant's data or funds, exploitable today with no special access. | SQL injection in a public login endpoint; missing ownership check on `/api/payouts/{id}` that lets any authenticated user view/cancel anyone's payout. |
| **High** | Requires some precondition (authenticated-but-unprivileged user, specific input, race window) but still reaches sensitive data/actions. | IDOR requiring a guessable ID; stored XSS in an admin-only field; a hardcoded credential for a real (non-test) system. |
| **Medium** | Weakens defense-in-depth or leaks info that aids further attack, without being directly exploitable alone. | Verbose stack traces on 500s; missing rate limiting on login; permissive CORS (`*`) on a read-only public endpoint; outdated dependency with a CVE that needs a specific unreachable code path. |
| **Low** | Best-practice / hardening gap with limited real-world impact. | Missing `Strict-Transport-Security` header; a `.env.example` with a placeholder value that looks secret-shaped; verbose but non-sensitive logging. |

## Workflow

### 1. Recon — know what you're actually auditing

- Identify the stack (language, framework, ORM, auth mechanism) and the trust boundaries:
  what's public internet-facing vs internal-only vs same-process.
  For a Python/FastAPI service, check `app/main.py` or `app/asgi.py` for mounted routers,
  middleware, and CORS config first — that's the actual attack surface, not every file.
- List external entry points: HTTP routes, webhook receivers, CLI scripts run with
  external input, file upload handlers, message-queue consumers.

### 2. Secret & credential scanning

Prefer a real tool over ad-hoc grep — it has calibrated patterns and an entropy check:

```bash
# gitleaks — scans working tree + full git history for committed secrets
gitleaks detect --source . --report-format json --report-path gitleaks-report.json --no-git=false

# trufflehog — verifies many secret types live (flags which ones still work) — useful signal,
# but never rely on "verified" against a real system as part of this audit; treat it as a
# stronger prioritization signal, not permission to authenticate anywhere.
trufflehog filesystem . --json > trufflehog-report.json
```

**False positives to filter before reporting, not after:**
- `.env.example` / `.env_example` files with placeholder values (`your-api-key-here`).
- Seed/fixture scripts with intentionally fake test credentials (e.g. `scripts/seed_dev_data.py`,
  `scripts/pos_partner_fixtures.py`-style files) — these are fixtures, not leaks, as long as
  they don't correspond to a real reachable system.
- A password appearing only in a comment documenting a **dev/staging-only** DB tunnel that's
  already firewalled to a specific EC2 SSM session — still worth a Low/Medium ("don't commit
  this even for dev"), not a Critical.
- Test files under `tests/` using hardcoded dummy JWTs/API keys.

Anything left after that filter — hardcoded prod credentials, private keys, unencrypted
`.pem`/`.pfx` files, real third-party API keys — is Critical or High depending on blast radius.

Also check: `git log --all -p | grep -iE 'password|secret|api_key'` for secrets that were
committed and later removed (still in history), and confirm `.gitignore` actually covers
`.env`, `*.pem`, `*.key`, credential JSON files.

### 3. Dependency / SCA scanning

Run whichever applies to the manifests present:

```bash
# Python
pip-audit -r requirements.txt          # or: poetry export -f requirements.txt | pip-audit -r -
safety check -r requirements.txt       # alternative/complementary

# Node
npm audit --omit=dev
# or: pnpm audit / yarn npm audit

# Language-agnostic, catches transitive deps across ecosystems in one pass
osv-scanner --recursive .
```

Only flag results with a real advisory (CVE/GHSA) at Medium+ severity per the upstream
advisory's own severity, adjusted for reachability — a Critical CVE in an unused
transitive dependency of a dev-only tool is not a Critical finding here.

### 4. Static analysis (SAST)

```bash
# semgrep — broad, fast, good default rulesets
semgrep --config p/owasp-top-ten --config p/security-audit .

# Python-specific
bandit -r . -x tests/,.venv/

# JS/TS-specific (if no semgrep available)
npx eslint . --no-eslintrc -c <a security-focused eslint config, e.g. eslint-plugin-security>
```

Treat every hit as a lead to manually verify (see below), not a finding by itself — SAST
tools have a high false-positive rate on parameterized-but-dynamically-built queries,
already-sanitized templates, etc.

### 5. Manual review — the checks tools don't reliably catch

**Auth & access control (usually the highest-value manual pass):**
- Every endpoint that takes a resource ID — does it verify the *authenticated* user owns/may
  access that specific resource, or only that they're logged in at all (IDOR)?
- Admin-only endpoints — checked by role/permission on every request, not just hidden from a
  nav menu.
- JWT/session handling — expiry enforced, signature algorithm pinned (reject `alg: none`),
  refresh-token rotation/reuse detection if applicable.

**Injection:**
- Every raw SQL string built with f-strings/`.format()`/`%` instead of parameterized
  queries or the ORM's query builder (`session.execute(text(f"..."))` is a red flag even if
  no injection is currently reachable from it).
- Every `subprocess`/`os.system`/shell-out call — is any part of the command built from
  external input? Is `shell=True` used with untrusted input?
- Every raw HTML render (`dangerouslySetInnerHTML`, Jinja `| safe`, string-built HTML) —
  is the content user-controlled?

**Config / infra:**
- CORS: is `allow_origins` a wildcard (`*`) combined with `allow_credentials=True`? (That
  combination is itself the vulnerability regardless of what origins are listed.)
- Cookies: `HttpOnly`, `Secure`, `SameSite` set on session/auth cookies.
- Error handling: do 500s leak stack traces / SQL / internal hostnames to the client in
  production mode?
- Secrets in environment vs. secrets manager — are production credentials in plain env vars
  readable by any process on the box, vs. pulled from AWS Secrets Manager / SSM Parameter
  Store at runtime?
- Rate limiting on auth endpoints (login, password reset, OTP) — brute-force feasible?

### 6. Verify before reporting

For each candidate finding, before it goes in the report:
1. **Trace the actual data flow** from the external entry point to the sink (SQL execution,
   shell exec, HTML render, resource access) in this codebase's real code — not "this
   pattern looks risky in general."
2. **State the concrete failure scenario**: what input, from whom, produces what wrong
   outcome. If you can't state this concretely, it's not ready to report as CONFIRMED —
   either mark it PLAUSIBLE and say what would need to be true, or drop it.
3. Check whether an existing control elsewhere (middleware, decorator, ORM behavior)
   already mitigates it — don't report something the framework already prevents.

### 7. Report findings

Rank most-severe first. Each finding needs:
- **File + line** (exact, not "somewhere in the auth module").
- **Summary** — one sentence, the defect itself.
- **Failure scenario** — concrete inputs/state → wrong output, in the format
  "X can do Y because Z."
- **Severity** — per the rubric above, with the reasoning (not just the label).
- **Remediation** — the actual code/config change, not "sanitize input better."
- **Verdict** — CONFIRMED (you traced it end-to-end in this code) or PLAUSIBLE (strong
  signal, but you couldn't fully verify reachability — say what's missing).

If running inside a harness that exposes a structured findings tool (e.g. Claude Code's
`ReportFindings`), use it instead of free-form prose so the host can render it consistently.
Otherwise use a table: Severity | File:Line | Vulnerability | Failure scenario | Remediation.

An audit that reports zero findings is a valid, complete result if that's what verification
actually showed — don't manufacture Low-severity padding to make the report look thorough.

## References

- [OWASP Top 10 Quick Reference](./references/owasp-top-10.md)
- [Secret-scanning false-positive patterns](./references/secret-false-positives.md)
- [FastAPI / Python-specific checklist](./references/fastapi-python-checklist.md)
