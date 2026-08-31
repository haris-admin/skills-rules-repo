# Weekly Codex Review — OpenRouter Free Pattern

Both weekly review scripts (`weekly_amlhive_codex_review.py`, `weekly_tapease_codex_review.py`) were rewritten July 23, 2026 to use OpenRouter free models instead of `codex exec`.

## Architecture

```
Python script
  ├── Collects repo data locally (git log, test results, file structure)
  ├── Builds structured prompt with collected data
  └── Calls chat_with_fallback(prompt) → returns analysis
```

No Codex CLI, no auth, no PATH issues. Pure API calls.

## Data Collection Pattern

```
def collect_data(repo_path):
    data = {}
    data["branch"] = run(["git", "branch", "--show-current"], repo_path)
    data["recent_commits"] = run(["git", "log", "--oneline", "-20"], repo_path)
    data["uncommitted"] = run(["git", "status", "--short"], repo_path)
    data["tests"] = run([pytest_bin, "tests/", "-q", "--no-header"], repo_path, timeout=120)
    data["structure"] = run(["find", ".", "-name", "*.py", "|", "head", "-30"], repo_path)
    return data
```

## Prompt Structure

The prompt includes:
- Branch name + recent commit history
- Uncommitted changes and diff stat
- Test results (pytest output)
- File structure overview
- Security scan findings

The LLM analyzes all data and produces a structured report with CRITICAL/HIGH/MEDIUM/LOW findings.

## Fallback Chain

1. OpenRouter free (gemma-4, nemotron, openrouter/free)
2. DeepSeek API (deepseek-v4-pro)
