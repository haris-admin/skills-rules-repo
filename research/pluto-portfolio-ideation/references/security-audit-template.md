# Pre-Build Security Audit Template

**Version:** 1.0 | **Date:** 2026-05-29 | **Created by:** Pluto

## Purpose

Before writing ANY code for a new project, run a security audit against this template. Document all vulnerabilities, assign severity, and provide exact remediations. The audit must be complete BEFORE Phase 1 implementation begins.

## Audit Frameworks (must apply all)

1. **OWASP Top 10 (2021)** — web application security risks
2. **ASD Essential Eight** — Maturity Level 2 minimum (Australian government standard)
3. **Australian Privacy Act 1988** — APP 1 (notice), APP 11 (security), Notifiable Data Breach scheme
4. **APRA CPS 234** — if project touches APRA-regulated entities (fintech, banking, insurance)

## Vulnerability Register Format

| ID | Severity | OWASP | Finding | Remediation |
|----|----------|-------|---------|-------------|
| VULN-001 | HIGH | A01 | PII unencrypted at rest | AES-256-GCM, 90-day retention |
| VULN-002 | HIGH | A03 | CSV formula injection | Strip =+-@ prefixes from output |
| VULN-003 | HIGH | A01+A04 | No auth layer | API key (P1) → Supabase Auth (P2) |

## High-Risk Areas to Always Audit

### 1. Data Classification & PII Handling
- What PII is stored? (email, financial data, IP)
- Is it encrypted at rest? What cipher?
- What's the retention policy?
- Is there a privacy notice (APP 1)?

### 2. Authentication & Authorization
- Is there any auth layer? If not, how is data scoped?
- API keys or JWT? Session management?
- Rate limiting on sensitive endpoints?
- MFA for admin access?

### 3. Input Validation & Injection
- SQL injection vectors? (use parameterized queries)
- CSV/Excel formula injection? (strip =+-@ from all exports)
- PDF injection? (sanitize user data before template rendering)
- XSS vectors? (CSP headers, output encoding)

### 4. Infrastructure Security
- Hardcoded credentials in git? (use .env, gitignored)
- Database port exposed? (listen on localhost only)
- CORS configured? (explicit allowlist, never *)
- Docker security? (non-root user, read-only rootfs)

### 5. Supply Chain Security
- Dependency audit? (pip-audit / npm audit in CI)
- Lock files committed?
- Dependabot/Renovate enabled?
- Every new dependency reviewed before adding?

### 6. Audit Logging
- What events are logged? (calculations, access, exports)
- Log format? (structured JSON)
- PII in logs? (hash it, don't log plaintext)
- Retention period?

### 7. Australian Regulatory Compliance
- Privacy Act APP 11: reasonable steps to protect personal info?
- NBD scheme: 30-day notification if breached?
- APRA CPS 234: applicable? If so, information security capability?
- ASD Essential Eight: MFA, patching, application control, admin restrictions, user hardening, macros, backups?

## Severity Definitions

| Severity | Criteria |
|----------|----------|
| 🔴 HIGH | PII exposed, no auth, injectable, compliance violation. MUST fix pre-code. |
| 🟡 MEDIUM | Security misconfiguration, weak controls, missing logging. Fix in Phase 1. |
| 🟢 LOW | Nice-to-have hardening, informational. Document, fix when convenient. |

## Pre-Code Security Checklist

Before writing ANY code:
- [ ] Data classification scheme defined
- [ ] Auth architecture designed (even if Phase 2)
- [ ] Input validation rules specified
- [ ] Audit logging schema defined
- [ ] CORS allowlist determined
- [ ] Dependency audit pipeline configured
- [ ] .env pattern established (gitignored)

## Post-Audit Actions

1. Save audit as `docs/SECURITY_AUDIT.md` in project repo
2. Mark all HIGH items as blocking — no code until resolved
3. Re-run audit after Phase 1 code is complete
4. Update when new dependencies are added

## Example: ExitLens AU Audit

For ExitLens AU, 12 vulnerabilities were found (3 HIGH, 6 MEDIUM, 3 LOW). The 3 HIGH items:
- VULN-001: PII (email, sale price, cost base, net proceeds) unencrypted → AES-256-GCM
- VULN-003: No authentication → API key (Phase 1), Supabase Auth (Phase 2)
- VULN-001 also triggered APP 11 + NBD scheme obligations

See the full audit at `docs/SECURITY_AUDIT.md` in the ExitLens repo for the complete template.
