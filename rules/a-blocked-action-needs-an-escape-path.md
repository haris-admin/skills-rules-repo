# A rule that blocks a user action ships with a way out (all agents, all repos)

Applies whenever a requirement blocks a user action (such as ending a shift, submitting a form, or deleting a resource); every block must provide a clear exit path under the same condition.

## Why this exists
**9 Nov 2026, Tap-Ease C22C:** Haris ruled that a shift cannot be ended without a paid transaction. Built alone, that traps a driver who started a shift by mistake: it can be neither ended nor left. The gap was surfaced before release, and Haris chose a separate "Cancel Shift" action that is offered exactly when End Shift is blocked.

## Rules
1. When a requirement blocks an action (End Shift, delete, submit), list every state in which the user is now stuck and name the exit for each (cancel, support route, admin override). Ask the human for any exit that needs a new route, status or Portal call.
2. Offer the exit under exactly the same condition as the block, so no state has neither. Test both sides: blocked and exit offered; not blocked and exit hidden.
3. Do not ship the block to users before the exit exists, or write down who unblocks them (the register row says so).
4. A destructive exit is checked again on the server; the screen condition is not the guard.
5. Record where the human's answer differed from the recommendation, so the reason survives.
