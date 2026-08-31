---
name: security-audit
description: >-
  Perform automated and static security audits, vulnerability assessments, secret detection, and OWASP Top 10 compliance checks. Use when asked to audit security, scan for secrets, or review code vulnerabilities.
---

# Security Audit & Vulnerability Assessment Skill

Guides the agent in analyzing codebases for security vulnerabilities, misconfigurations, and credential exposures.

## Workflow

1. **Step 1: Secret & Credential Scanning**
   - Search for accidental hardcoded secrets (API keys, private tokens, passwords, private keys, `.env` files checked into git).
   - Verify `.gitignore` contains sensitive credential files.

2. **Step 2: Injection & Vulnerability Inspection**
   - Check all entry points receiving external input (HTTP parameters, CLI arguments, query strings, headers, file uploads).
   - Confirm proper parameterization for SQL queries, sanitization for HTML rendering, and safe execution for shell commands.
   - Review authentication and authorization controls on sensitive endpoints.

3. **Step 3: Dependency & Configuration Audit**
   - Check package manifests (`package.json`, `requirements.txt`, `Cargo.toml`, `go.mod`) for vulnerable or outdated dependencies.
   - Verify CORS configurations, CSRF protection, secure cookie flags (`HttpOnly`, `Secure`, `SameSite`), and Content-Security-Policy (CSP) headers.

4. **Step 4: Report Findings**
   - Present a prioritized vulnerability matrix:
     - **Vulnerability**: Name and CVE/CWE if applicable.
     - **Severity**: Critical, High, Medium, Low.
     - **Location**: Specific file and line number.
     - **Remediation**: Concrete code fix or configuration change.

## Reference

- [OWASP Top 10 Security Reference](./references/owasp-top-10.md)
