# Feel and display values are per-terminal configuration (Tap-Ease and similar fleets)

Applies to tunable UI and hardware settings across device fleets; treat values like timers, animation scales, sounds, and support contacts as configurable defaults rather than hardcoded literals.

## Why this exists
**8 Nov 2026, Haris (C75 OP-4, OP-8, OP-8a, OP-8b):** "I want to make it configurable, so maybe tomorrow I might make it 0.88 or something." QR dialog timers, button press scale and tint, button sound, link expiry, support contact and privacy URL were constants or repeated literals.

## Rules
1. Values a person may tune (timers, animation strength, sound on or off, support contact) are configuration with a documented default and a valid range, served per terminal (terminal value, fleet default, code default), changeable without a new APK.
2. Invalid values are ignored and rejected on write.
3. Tests change the configured value and assert the behaviour follows; the literal default is asserted once.
4. Any new alert or flash (for example a flashing border in the last 10 percent) stays under 3 flashes per second and never changes the size, position or contrast of a scannable code.
