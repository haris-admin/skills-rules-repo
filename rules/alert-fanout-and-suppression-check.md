# New alert paths: expect fan-in from other sessions, and check suppression before testing (all agents)

Applies when adding email, Slack or pager alerts to scripts that several agents or sessions run.

## Why this exists

**3 Nov 2026 (ChargeRail):** deploy scripts were wired to send a `deploy_ok` alert. Another session deployed minutes later, which used the 30 minute rate limit window, so the founder-approved test email was suppressed. The rate limit worked as designed, but the test could not prove delivery.

## Rules

1. Wiring a script to alert means every future run by any session sends mail. Say so to the founder when it is wired, and record which scripts now alert.
2. Before sending an approved test, read the per-type rate limit state (read-only) and pick a type whose window is clear, or wait for the window to end. Do not clear the state or bypass the limit to force a send.
3. A test approval covers one send. If the test is suppressed, report that and ask before sending another.
4. A new check that fires on its first run is a finding, not noise: read the cause before silencing it (the ChargeRail backup fault was found this way).
5. Background scheduling (systemd timers, cron) on shared production boxes is blocked for agents by the auto mode classifier. Give the founder a short script and say why.
