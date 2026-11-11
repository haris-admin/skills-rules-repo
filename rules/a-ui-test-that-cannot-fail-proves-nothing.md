# A UI test that cannot fail proves nothing: delete it and use device evidence (all agents)

If the test harness cannot reproduce the defect the owner sees, a test that passes before the fix is worthless. Do not keep it as a guard. Say so and prove the fix on the real device.

## Why this exists
**11 Nov 2026, Tap-Ease terminal app (C78):** after the Inter font was added, the bottom tab label "Transactions" wrapped to "Transaction / s" on the Flex 4. A Robolectric test that asserted one line passed before the fix, because the test environment does not measure real font widths. The fix was confirmed from a device screenshot. In the same session a typography test that passed before the change was strengthened until it failed first.

## Rules
1. Run every new UI test against the old code first. If it passes, it is not testing the change: strengthen it, or delete it.
2. Robolectric and similar harnesses do not measure real fonts, real screen sizes or real focus on the first frame; treat text-fit, clipping and default focus as device checks.
3. When a test must be dropped for this reason, record the reason in the spec task and attach the device evidence (screenshot or log) instead.
4. A test environment's own artefact (for example default initial focus) must not be asserted as product behaviour; assert the transition the user cares about.
