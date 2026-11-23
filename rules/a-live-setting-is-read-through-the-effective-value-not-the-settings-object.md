# A live setting is read through its effective value at call time, never from the settings object

A setting that an administrator can change on a configuration screen is stored in a database snapshot; code that reads the startup settings object ignores the change while the screen shows it as applied.

**Scope:** any service with a runtime configuration registry (a screen, API or table that overrides defaults).

## Why this exists

**23 Nov 2026 (HandleDispute, spec 38m):** the sign-in and code attempt limiter read `settings.AUTH_RATE_LIMIT_MODE` and the limits directly. The registry stored a changed value and showed it, and only `restart` settings were copied onto the settings object at startup. Switching the mode to `enforce` on the screen would have been audited and done nothing. Tests patched the settings object, so no test exercised the screen path.

## Rules

1. Read every registry setting through the registry's `effective(name)` at call time (it falls back to the settings object when nothing is stored).
2. Add a guard test that the module has no direct read of the registry's settings from the settings object (a text scan for the prefix and for `getattr(settings`).
3. Test through the stored value: set the stored value, leave the settings object at another value, and assert the stored one wins in both directions (enforce and off).
4. A security setting (one whose change should alert) is marked as such in the registry; check that any existing test helper that picks "a non-security setting of kind X" still has one, or change that helper only with the owner's approval.
