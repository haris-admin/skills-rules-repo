# Business identifiers are stored columns from their own sequences (all agents, all repos)

Applies to human-visible business identifiers (transaction IDs, shift numbers, invoice codes); store them in dedicated, unique columns backed by their own database sequences, never derived from primary keys.

## Why this exists
**8 Nov 2026, Tap-Ease C65C:** the first design computed the Transaction ID and shift number from the primary key (1000000000 + id, S-(100000 + id)) and restarted the primary key sequences. Legacy ids and new ids collided, the wrong trip resolved, and staging returned 500 (duplicate key) on every trip create until migration 0035 replaced it.

## Rules
1. A number people see (transaction id, shift number, invoice number) is a stored, unique, NOT NULL column with its own database sequence. Never derive it from a primary key at read time and never repurpose the key.
2. Do not restart a primary key sequence to make ids look bigger. If one was restarted, reset it to max(id)+1 only when that is safe, in a new migration. Never edit a migration that is already pushed.
3. Backfill existing rows in the migration, create the sequence at max+1, then add NOT NULL. Give the migration a tested downgrade and upgrade on a scratch database with legacy rows.
4. Test with real migrations against a disposable Postgres: legacy rows survive, a new row gets a higher identifier, no collision.
5. When a requirement changes the identifier scheme, remove tests of the old arithmetic together with the spec (tests change only when requirements change).
