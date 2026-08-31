# Security & Secrets Management

Universal security protocols, secrets hygiene, and credential protection.

## Core Security Rules

1. **Zero Hardcoded Secrets**:
   - Never commit API keys, private keys, database passwords, tokens, or credentials into source code.
   - Use `.env` files locally and ensure `.env*` (except `.env.example`) is listed in `.gitignore`.
   - Inject production secrets via secure secret managers (e.g. 1Password CLI `op run`, AWS Secrets Manager, Vault).

2. **Authentication & Authorization**:
   - Never store plain text passwords; use salted cryptographic hashes (e.g. Argon2, bcrypt).
   - Validate permissions and tenant boundaries on every backend request (Defense-in-Depth).
   - Use short-lived access tokens and implement secure token refresh mechanics.

3. **Input Sanitization & Injection Prevention**:
   - Prevent SQL Injection by using ORMs or parameterized queries exclusively.
   - Prevent XSS by sanitizing user-generated HTML and using framework-level escaping.
   - Prevent SSRF by validating and restricting user-supplied URLs.

4. **Dependency Scanning & Audits**:
   - Regularly run `npm audit`, `pip audit`, or `cargo audit` to identify and patch vulnerable dependencies.
   - Remove unused dependencies to minimize attack surfaces.
