# A database major upgrade is rehearsed, counted, backed up, then cut over (all agents, all repos)

**Origin (Tap-Ease, 15 Nov 2026, postgres-17-everywhere).** The staging POS terminal database (a Docker container) was on Postgres 16 while everything else was 17. It was moved to 17.9 with no data loss using the steps below. The first cutover run stopped before changing anything because the host had no `docker compose` plugin, which is exactly what the fail-early structure is for.

## Rules
1. **Inventory first, read-only.** Find every environment's real version (RDS describe, container image, CI pins, local) before proposing work. Production may already be there.
2. **Guard test for drift.** A test fails if any compose or workflow file names another major; prove it can fail (RED, or a temporary mutation if the repo is already compliant).
3. **One script, two modes.** `rehearse` dumps the live database, restores it into a throwaway container of the new major, compares exact per-table row counts, and removes the container. `cutover` runs the rehearsal first and stops on any difference. Never print passwords or env values.
4. **Guards at the top:** refuse unless the target container exists, is the old major, and the environment is the intended one; detect the available tool (`docker compose` or `docker-compose`) before any change.
5. **Back up the old volume before removing it,** write a ROLLBACK note next to it, and keep it until the owner releases it. Dumps contain role details: delete them only on the owner's word.
6. **Order of repo changes:** change the compose or image pin in the app repo only after the cutover, otherwise a deploy starts the new major on the old data directory and fails.
7. **The owner runs it** through a short `~/x.sh` wrapper; the agent reads the evidence, then records the result in the spec and the docs.

Related: `terraform-safety`, `handoff-commands-as-short-script-files`.
