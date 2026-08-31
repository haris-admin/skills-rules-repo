#!/usr/bin/env python3
"""Month-end completion gate — prints STABLE output until the Month-End Review
output file for the just-ended month exists, then prints a DIFFERENT stable
string once per completion. Use as a cron monitor on the Start-of-Month job so
it fires only AFTER the Month-End Review finishes (whatever time that takes).

Deterministic (no timestamps in the common path) — critical for monitor hashing:
- non-1st day → "NOT_FIRST_DAY" (stable, no agent fire)
- 1st day, output file missing → "NOT_COMPLETE" (stable, no agent fire)
- 1st day, output file present → "MONTH_END_COMPLETE <YYYY-MM>" (changed once)
"""
import datetime
from pathlib import Path

today = datetime.date.today()
if today.day != 1:
    print("NOT_FIRST_DAY")
    raise SystemExit(0)

# Just-ended month = previous calendar month
if today.month == 1:
    ym = f"{today.year - 1}-12"
else:
    ym = f"{today.year}-{today.month - 1:02d}"

out = Path.home() / ".hermes" / "research_outputs" / f"month-end-{ym}.md"
print(f"MONTH_END_COMPLETE {ym}" if out.is_file() else "NOT_COMPLETE")
