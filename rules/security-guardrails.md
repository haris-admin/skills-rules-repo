# Security Guardrails & Safe Coding Guidelines

Enforce baseline security standards across all codebases and AI-assisted workflows.

## Critical Guardrails

1. **Zero Secrets in Code**:
   - Never commit passwords, API keys, bearer tokens, private certificates, or secrets to version control.
   - Use environment variables (`.env`, secret managers) and ensure `.env` is ignored by `.gitignore`.

2. **Sanitize & Validate All Inputs**:
   - Prevent SQL Injection: Use parameterized queries or ORMs with prepared statements.
   - Prevent Command Injection: Never pass unvalidated user inputs directly into `eval`, `exec`, or shell execution calls.
   - Prevent Cross-Site Scripting (XSS): Properly escape or sanitize HTML and user-rendered templates.

3. **Principle of Least Privilege**:
   - Grant the minimum permissions required for database users, IAM roles, and file operations.
   - Restrict write access to sensitive files and directories.

4. **Cryptographic Standards**:
   - Do not use deprecated hash functions (MD5, SHA1) for security-sensitive purposes. Use SHA-256 or bcrypt/argon2 for password hashing.
   - Use cryptographically secure random number generators (e.g. `crypto.randomBytes` or Python's `secrets` module).

5. **Safe AI Automation**:
   - When executing commands or tool calls on behalf of the user, never execute destructive commands (like recursive unconstrained deletes) without sanity checks.
