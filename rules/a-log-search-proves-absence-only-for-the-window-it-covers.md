# A log search proves absence only for the window it covers (all agents)

Applies whenever an agent reports "nothing happened", "no request arrived" or "I cannot find it" from a log.

## Why this exists

Tap-Ease, 9 Nov 2026 (v4.5.21 release). Haris said a customer had clicked the Clover link for terminal 1020. The box log and 30 days of CloudWatch showed no
callback for that merchant, and the agent said so (correct at 02:32 UTC). The approval was actually recorded at 02:47 UTC. The release restart at 02:56 UTC
then moved and pruned the log files, so every later search covered only the time after the restart and still found nothing. The credential row (created
02:47:25) only came to light when Haris ran a database listing. A subagent had also reported "this merchant only appears on 6 Nov" from CloudWatch, which lags
the box log by minutes to hours.

## Rule

1. State the window and the source of every negative finding ("no callback in the box log from 02:59 UTC to 03:28 UTC").
2. For a question about whether something happened, ask the system of record first (the database row), not a log.
3. After any deploy, restart or log rotation, re-run the check. The log may now start after the event.
4. Treat a negative from a lagging source (CloudWatch, a forwarded stream) or from a subagent as a hypothesis until checked against the live source.
5. When a person tells you something happened and your search disagrees, say "my search covers X to Y" and offer the database check. Do not say it did not happen.

## How to apply

Prefer a read-only count from the table (`SELECT ... FROM clover_merchant_credentials WHERE merchant_id = ...`) over a grep. If only logs exist, name the
files and times covered. Related: `deploy-state-needs-independent-reads.md`, `deployed-vs-local-code-parity.md`.
