#!/usr/bin/env python3
"""Month-end detector for date-gated crons.
Prints MONTH_END <date> only on the last calendar day of the month,
otherwise NOT_MONTH_END. Deterministic (no timestamps) so the cron monitor
fires only on the actual month-end. Handles Dec 31 and Feb 28/29."""
import datetime

today = datetime.date.today()
if today.month == 12:
    last = datetime.date(today.year, 12, 31)
else:
    last = datetime.date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)

print(f"MONTH_END {today.isoformat()}" if today == last else "NOT_MONTH_END")
