# Regression tests sit at the layer where the bug lives (all agents)

Applies to regression testing for bug fixes; write tests that fail against pre-fix code at the exact layer where the bug resides, verifying real callbacks, wiring, and one-shot event consumption.

## Why this exists
**8 Nov 2026, Tap-Ease C71D:** "Keep on waiting" did nothing because the `PreviewScreen` wrapper passed `onKeepWaiting = {}`. The regression test exercised `PreviewScreenContent`, so it could not have failed before the fix. The same no-op default remained on three other screens. A one-shot navigation flag (`navigateToPaymentCard`) was never consumed, so returning to Preview could restart a card payment.

## Rules
1. A regression test fails (Red) against the pre-fix code at the layer that held the bug. Confirm that before calling it a test of the fix.
2. Callback parameters that must be wired get no default value; the compiler then finds the missing wiring.
3. One-shot events are consumed once. Test: leave and return, and nothing fires on its own.
4. A fix for a pattern is applied to every instance of the pattern in the same change, with a test per screen.
