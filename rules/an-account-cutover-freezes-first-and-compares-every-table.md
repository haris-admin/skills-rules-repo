# An account or host cutover freezes, takes the last backup after the stop, and compares every table (all agents, all repos)

Applies when production data moves to a new host, database or cloud account.

## Why this exists
**14 Nov 2026, HandleDispute cutover to its own AWS account (OpenSpec 77):** the rehearsal restored an older backup, so the final copy needed its own freeze. The cutover ran in a fixed order with a checked exit at each step, and moved DNS only after exact row counts of all 52 tables matched. The same checks found two gaps that a "healthy" answer did not: the nightly backup timer was missing on the new host, and the rehearsal restored the database but not the evidence files.

## Rules
1. Order: copy the exact production image (identical digest), stop writes on the old side, take a fresh backup after the stop, verify it against its manifest, restore into the new side, mirror the production settings, deploy, compare, then change DNS. Never change DNS first.
2. Write each step as a short owner script with an abort that starts the old side again, and say in the plan what the rollback loses once real users write to the new side.
3. Compare exact row counts of every table between the frozen old database and the restored one. Names and counts only, never data. A mismatch stops the cutover.
4. Restore every kind of state: the database, the evidence or upload files (check the archive for unsafe paths and links, never merge over existing files, never print file names), settings, the backup timer, monitoring.
5. A key or token has one source. Look up its real location by name only (never the value) before copying; a secret named in conversation may live elsewhere.
6. Prove traffic arrives on the new side with a unique marker in its own access log while the old side is stopped; an HTTP 200 alone does not show which side answered.
7. Keep the old side, stopped, for the rollback window and record the earliest removal date.
