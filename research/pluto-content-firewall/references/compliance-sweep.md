# Compliance Sweep Procedure

## When to Run
- After any new blog post is added to harishabib_au_code
- Before any deployment to GitLab main
- Weekly, as part of routine review

## Firewalled Terms (grep-ready, case-insensitive)

```bash
FIREWALL="aml hive|finai|fin ai|paylicence|pay licence|exitlens|exit lens|tokenpilot|token pilot|cloudproof|cloud proof|tapease|tap ease|agentgate|agent gate|cloudwise|cloud wise|verifylink|verify link|ndis billbot|regstack|extrisk"
```

## Sweep Command

From the harishabib_au_code repo:

```bash
grep -rniE "$FIREWALL" src/content/blog/ linkedin/ src/content/internal/ --include="*.md" --include="*.mdx"
```

## Resolution

For each hit:
1. **Blog post (public):** Remove or replace with generic description. Commit immediately.
2. **LinkedIn post:** Remove or delete entire file if it's a pure product ad. Commit.
3. **Internal post:** Flag — internal posts are redirected to /restricted but should still be clean.

## What NOT to strip

- **Third-party commercial products** (Snyk, Sysdig, Microsoft, AWS, Docker, etc.) — these are allowed
- **Regulatory bodies** (AUSTRAC, ASIC, APRA) — these are fine
- **Open-source tools** (Trivy, Kubernetes, Astro) — these are fine

The rule is: **no HARIS'S products**, not no commercial products.
