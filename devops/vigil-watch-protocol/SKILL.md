---
name: vigil-watch-protocol
description: Vigil's monitoring & escalation protocol — fleet monitors, cron health, test watch, RED/YELLOW/GREEN alerting. Use for any monitoring task.
---

# Vigil Watch Protocol

## Trigger
Any monitoring task: fleet health, cron status, test suite watch, escalation, alert triage.

## Method

1. **Fleet monitors** (4x daily: 5/11/17/23 AEST):
   - AMLHive: EC2, Docker, RDS, Lambda, Sentry — `pluto-fleet-monitor` pattern
   - TapEase: backend t4g.medium, frontend t4g.small, RDS db.t4g.small, clover-sync, payouts
   - Use: `~/.hermes/scripts/*fleet*.py`, `*monitor*.py`
2. **Verify before alerting** — cross-reference (cross_ref_verify pattern). False positives are worse than silence.
3. **Severity tiers**:
   - 🔴 RED: P0/P1 live issues only → escalate immediately
   - 🟡 YELLOW: decision needed
   - 🟢 GREEN: FYI
4. **Escalation**:
   - RED → HTML email via purelymail (smtp.purelymail.com:587, operator@harishabib.au) to hhsiddiqui+shoaib+tech
   - Telegram to AMLHive group (-1004485329864)
5. **Cron health**: weekly error counts + trends; feed Sol's weekly review.

## Monitoring rules
- Source labels per section · evidence counts header
- Only ALERT_PATTERNS trigger — no generic ERROR/SSL noise
- Timezone: AML Hive = timestamptz UTC (pre-compute in Python) · Tapease = AEST no-tz. NEVER mix.
- Secrets by key name only, never print.

## Known traps
- A2Square weekly suite (Monday 02:30) — webServer race condition
- AMLHive daily flake — `--retries=1` recommended, NOT approved
- Sentry JS errors = P2 drift, not P0

## Delivery
- Fleet Monitor template: emoji + box-drawing + summary/detail.
- Silence when healthy = correct behavior.
