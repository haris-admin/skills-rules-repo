#!/usr/bin/env python3
"""
Template: Weekly Automated Codex Review — Cron Script
=====================================================
Use this as a starting point for scheduled Codex code reviews.
Run via Hermes cron as no_agent=true script.
Customise: REVIEWS dict, model, timeouts, report format.

Scheduled example (in Hermes):
  0 2 * * 2 → Tapease (Tuesday)
  0 2 * * 5 → AML Hive (Friday)
"""

import subprocess, json, sys, concurrent.futures
from datetime import datetime, timezone, timedelta

# ── CONFIG ──────────────────────────────────────────────────────────
MODEL = "gpt-5.6-sol"
CODEX_TIMEOUT = 1800          # 30 min per review
CODEX_ARGS = [
    "codex", "exec",
    "--model", MODEL,
    "--sandbox", "danger-full-access",
    "--dangerously-bypass-approvals-and-sandbox",
    "--json",
]

REVIEWS = {
    "Project Name — Component": {
        "cwd": "/path/to/repo",
        "prompt": (
            "Run a comprehensive code review:\n"
            "1. Check project structure — framework, key files\n"
            "2. Run tests (pytest/jest/vitest)\n"
            "3. Run lint + type checks (ruff/eslint/mypy/tsc)\n"
            "4. Check for security issues (PII logging, XSS, auth, injection)\n"
            "5. Check dependency health (npm audit / pip-audit)\n"
            "Report: CRITICAL/HIGH/MEDIUM/LOW findings, test results. Concise."
        )
    },
}

# ── OUTPUT PARSING ─────────────────────────────────────────────────

def extract_review(raw_output: str) -> str:
    """Parse Codex JSONL output for the final assistant message."""
    for line in raw_output.split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if obj.get('type') == 'message':
                content = obj.get('content', '')
                if content and len(content) > 100:
                    return content.strip()
        except (json.JSONDecodeError, KeyError):
            pass
    # Fallback: last 80 non-JSON lines
    lines = [l for l in raw_output.split('\n')
             if not l.strip().startswith('{') or '"type"' not in l]
    return '\n'.join(lines[-80:]).strip()


# ── EXECUTION ───────────────────────────────────────────────────────

def run_review(name: str, cwd: str, prompt: str) -> tuple[str, float]:
    """Run one codex exec review and return (text, elapsed_seconds)."""
    import time
    print(f"[{name}] Starting...", file=sys.stderr, flush=True)
    start = time.time()
    try:
        result = subprocess.run(
            CODEX_ARGS + ["-C", cwd],
            input=prompt.encode(),
            capture_output=True,
            timeout=CODEX_TIMEOUT,
        )
        elapsed = time.time() - start
        text = extract_review(result.stdout.decode(errors='replace'))
        if len(text) > 4000:
            text = text[:4000] + "\n\n... [truncated]"
        print(f"[{name}] Done in {elapsed:.0f}s", file=sys.stderr, flush=True)
        return text, elapsed
    except subprocess.TimeoutExpired:
        print(f"[{name}] TIMEOUT", file=sys.stderr, flush=True)
        return "⚠️ Review timed out", CODEX_TIMEOUT
    except Exception as e:
        print(f"[{name}] ERROR: {e}", file=sys.stderr, flush=True)
        return f"⚠️ Review failed: {e}", 0


# ── MAIN ────────────────────────────────────────────────────────────

def main():
    now = datetime.now(timezone(timedelta(hours=10)))
    report = [
        f"★ Weekly Codex Review — Custom",
        f"   {now.strftime('%A %d %B %Y, %I:%M %p AEST')}",
        "",
    ]

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = {
            pool.submit(run_review, name, info["cwd"], info["prompt"]): name
            for name, info in REVIEWS.items()
        }
        for future in concurrent.futures.as_completed(futures):
            name = futures[future]
            text, elapsed = future.result()
            results[name] = text
            results[f"{name}_time"] = elapsed

    for name in REVIEWS:
        elapsed = results.get(f"{name}_time", 0)
        report.append(f"─── {name} ({elapsed:.0f}s) ───")
        report.append(results.get(name, "No results"))
        report.append("")

    print('\n'.join(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
