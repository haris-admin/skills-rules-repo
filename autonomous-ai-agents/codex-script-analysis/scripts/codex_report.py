#!/usr/bin/env python3
"""
Codex Report Generator — reusable helper for scripts that need AI-powered analysis.
Drop into any script with: from codex_report import generate_report
"""
import subprocess, json, os
from pathlib import Path

CODEX_HOME = str(Path.home() / ".codex")

def generate_report(raw_data: dict, job_label: str) -> str:
    """Send raw monitoring data to Codex and get back a formatted report."""
    
    # Trim oversized fields to stay within prompt limits
    safe = dict(raw_data)
    for key in list(safe.keys()):
        if isinstance(safe[key], str) and len(safe[key]) > 5000:
            safe[key] = safe[key][:2000] + f"… [{len(safe[key])} chars total]"
    
    prompt = (
        f"You are the {job_label} monitor. "
        f"Analyze the raw monitoring data below and produce a concise incident report.\n\n"
        f"RULES:\n"
        f"- Use red 🔴 ONLY for P0/P1 live-impacting issues (downtime, data loss, auth failure)\n"
        f"- Use amber 🟡 for drift/P2 (one-off errors, CPU credits low, non-critical)\n"
        f"- Use green ✅ for healthy sections\n"
        f"- Start with a one-line severity bar: '✅ ALL CLEAR' / '⚠️ X issues' / '🔴 X critical'\n"
        f"- Group findings by section (Public Health, Docker, CloudWatch, Sentry, RDS, Cloudflare)\n"
        f"- End with '→ Next: ' recommended action\n"
        f"- Keep under 100 lines — this goes to Telegram\n\n"
        f"RAW DATA:\n{json.dumps(safe, default=str, indent=2)[:10000]}"
    )
    
    try:
        r = subprocess.run(
            ["codex", "exec", "--skip-git-repo-check", prompt],
            capture_output=True, text=True, timeout=180,
            env={**os.environ, "CODEX_HOME": CODEX_HOME}
        )
        report = (r.stdout or "").strip()
        if not report:
            report = r.stderr[:500] if r.stderr else "[Codex returned empty]"
    except subprocess.TimeoutExpired:
        report = "⚠️ Codex report timed out (180s) — falling back to raw summary"
    except FileNotFoundError:
        report = "⚠️ Codex CLI not found — install via npm install -g @openai/codex"
    except Exception as e:
        report = f"⚠️ Codex report error: {e}"
    
    return report

def diagnose_test_failure(label: str, test_output: str) -> str:
    """Route test failure output to Codex for root-cause diagnosis."""
    prompt = (
        f"AMLHive {label} test failure. Analyze this output and identify the root cause. "
        f"Reply with:\n"
        f"1. Root cause (1-2 sentences)\n"
        f"2. Fix steps (bullet list)\n"
        f"3. Which file(s) to change\n\n{test_output[:6000]}"
    )
    try:
        r = subprocess.run(
            ["codex", "exec", "--skip-git-repo-check", prompt],
            capture_output=True, text=True, timeout=120,
            env={**os.environ, "CODEX_HOME": CODEX_HOME}
        )
        return (r.stdout or r.stderr or "")[:2000]
    except Exception as e:
        return f"[Codex diagnosis failed: {e}]"

def append_diagnosis(log_name: str, label: str, diagnosis: str):
    """Write diagnosis to the central reviews log."""
    log_dir = Path.home() / ".hermes" / "reviews"
    log_dir.mkdir(exist_ok=True)
    with open(log_dir / log_name, "a") as f:
        from datetime import datetime, timezone, timedelta
        ts = datetime.now(timezone(timedelta(hours=10))).strftime("%Y-%m-%d %H:%M:%S AEST")
        f.write(f"\n[{ts}] {label}:\n{diagnosis}\n{'─'*60}\n")

if __name__ == "__main__":
    # Quick self-test
    test = {"health": {"api": 200, "frontend": 200}, "status": "all green"}
    print(generate_report(test, "Self-Test"))
