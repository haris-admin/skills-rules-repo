# Codex Diagnosis on Test Failure

Route test failures to Codex CLI for root-cause analysis. Added July 2026.

## Pattern

```python
def codex_diagnose(label, test_output, repo_path):
    try:
        prompt = (
            f"{label} test failure. Analyze this output and find root cause. "
            f"Reply: 1) root cause  2) fix steps  3) which files\n{test_output[:4000]}"
        )
        r = subprocess.run(
            ["codex", "exec", "--skip-git-repo-check", prompt],
            capture_output=True, text=True, timeout=120, cwd=str(repo_path),
            env={**os.environ, "CODEX_HOME": str(Path.home() / ".codex")}
        )
        diag = (r.stdout or "")[:2000]
        log_path = Path.home() / ".hermes" / "reviews" / "test_diagnoses.log"
        log_path.parent.mkdir(exist_ok=True)
        with open(log_path, "a") as f:
            f.write(f"\n[{datetime.now()}] {label} FAILURE:\n{diag}\n{'─'*60}\n")
        return True
    except Exception:
        return False

# Usage after test failure:
if result["failed"] > 0:
    codex_diagnose("backend pytest", test_output, REPO_PATH)
```

## Fleet Monitor Report Generation

Same pattern for operational reports. Instead of hand-coded `build_report()`, pipe raw structured data to Codex:

```python
from codex_report import generate_report

data = collect_all_metrics()  # Existing data collection
report = generate_report(data, "AMLHive Fleet Monitor")
print(report)
send_email(report)
```

The `codex_report.py` helper (at `~/.hermes/scripts/codex_report.py`) strips credentials, limits large blobs, and formats a consistent prompt that produces incident-grade reports. This replaces ~120 lines of hand-coded Python formatting with AI-powered analysis.

## Requirements
- Codex CLI installed and authenticated (`codex exec` non-interactive)
- `CODEX_HOME` env var pointing to `~/.codex`
- `--skip-git-repo-check` flag when not in a trusted git directory
- Log directory at `~/.hermes/reviews/` (auto-created)

## Integration in Test Runners
Both the AMLHive daily test runner and A2Square weekly test runner use this pattern as of July 2026. Diagnoses append to `~/.hermes/reviews/test_diagnoses.log` with timestamps for review across nightly/weekly runs.

## Auth Fix (Stale Token)
Codex ChatGPT auth tokens expire periodically with `refresh_token_reused` errors. Fix:
```bash
rm ~/.codex/auth.json
codex login --device-auth
# Enter the device code at https://auth.openai.com/codex/device
```
