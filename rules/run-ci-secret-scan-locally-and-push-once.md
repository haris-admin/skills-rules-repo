# Run the CI secret scan locally, and push once

Before pushing a branch that CI will scan with Gitleaks, and when deciding how often to push. Applies to all agents on repos with a Gitleaks workflow.

**Scope:** any repo with `.github/workflows/gitleaks.yml` (Simplifii-OS, 5 Oct 2026).

---

## Why this exists

A made-up JWT-shaped placeholder in a unit-test fixture (`'header.eyJyb2xl….signature'`) failed the hosted Gitleaks job (`generic-api-key`) after a push. The log said only "leaks found: 1" because the scan runs with `--redact`, so the finding could not be read from CI. It took a second push to fix, leaving a permanent red run in history. The owner then asked for fewer pushes: do the work and commits locally, push once.

## Core Directives

1. **Use the CI's Gitleaks version locally.** Read `GITLEAKS_VERSION` from the workflow, download that release for your platform, and run it over the range you are about to push: `gitleaks git --redact --no-banner --exit-code 1 --log-opts="<base>..<head>" .` Add `--report-format json --report-path <file>` to get the rule, file and line locally.
2. **Fake fixtures still trip scanners.** For a deliberately fake credential-shaped string, add `// gitleaks:allow` on the line and add the finding's fingerprint (`<commit>:<file>:<rule>:<line>`) to `.gitleaksignore` with a comment saying it is a fake. Prefer building such strings in the test (`['sb','secret','x'].join('_')`) so no literal exists.
3. **Commit locally, push once.** Make changes and commit as you go; run the tests, style check and the local scan; push once when the owner says. Do not push to see whether CI is green.
4. **Check CI on the right repo.** If the same branch is on two remotes, one may have no working runners (jobs end in seconds with runner id 0). Read the run that actually executed.
5. **Never put a real key in a fixture to make a test realistic.** Use obviously fake text.

---

## Patterns to Follow

```bash
V=$(grep -oE 'GITLEAKS_VERSION: *"?[0-9.]+' .github/workflows/gitleaks.yml | grep -oE '[0-9.]+$')
curl -sSL -o gl.tgz "https://github.com/gitleaks/gitleaks/releases/download/v$V/gitleaks_${V}_darwin_arm64.tar.gz" && tar -xzf gl.tgz gitleaks
./gitleaks git --redact --no-banner --exit-code 1 --log-opts="origin/<branch>..HEAD" .
```

## Patterns to Avoid

- Pushing to find out whether the scan passes.
- Reading a redacted CI log and guessing the file.
- Three pushes in a row on one afternoon.
