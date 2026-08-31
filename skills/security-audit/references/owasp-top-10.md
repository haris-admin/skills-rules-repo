# OWASP Top 10 Quick Reference

1. **A01: Broken Access Control**: Verify users cannot act outside their intended permissions (IDOR, path traversal, missing JWT role checks).
2. **A02: Cryptographic Failures**: Ensure data in transit and at rest is strongly encrypted. No plaintext passwords or weak hashes.
3. **A03: Injection**: Prevent SQL, NoSQL, OS command, and LDAP injections via parameterized queries and strict input validation.
4. **A04: Insecure Design**: Ensure threat modeling, defense-in-depth, and rate limiting against brute force attacks.
5. **A05: Security Misconfiguration**: Avoid default credentials, verbose error stack traces exposed to clients, and unneeded open ports.
6. **A06: Vulnerable and Outdated Components**: Keep dependencies updated and monitor for known CVEs.
7. **A07: Identification and Authentication Failures**: Enforce strong password policies, multi-factor authentication, secure session timeouts.
8. **A08: Software and Data Integrity Failures**: Verify plugins, libraries, and CDNs using subresource integrity (SRI) and signed artifacts.
9. **A09: Security Logging and Monitoring Failures**: Ensure audit logs capture critical events (logins, privilege escalations, financial transactions) without logging sensitive PII.
10. **A10: Server-Side Request Forgery (SSRF)**: Validate and restrict URLs fetched by backend services; prevent access to internal metadata endpoints (`169.254.169.254`, `localhost`).
