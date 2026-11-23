# An owner decision made against the recommendation is recorded verbatim, then spec, ticket and consequences change with it

When the owner picks a different option from the one recommended, the recommendation is dropped everywhere it was written down, and the accepted risk is named.

**Scope:** every agent asking structured questions.

## Why this exists

**23 Nov 2026 (HandleDispute, Q29):** asked what a deploy script should do when it cannot read an optional setting, the owner chose "warn and deploy with an empty value" (the agent recommended stopping). The agent-ready ticket had been written for "stop", so it had to be rewritten, and the consequence (a throttled read of the case note signing key ships that feature off with a green result) was recorded as accepted.

## Rules

1. Record the question, the selected option and its description exactly, and what it decides and does not decide.
2. Amend the spec's requirement text and tasks, and rewrite any ticket or brief that assumed the other option, before dispatching an implementer.
3. State the accepted consequence in plain words in the decision record and in the next report.
4. If the option text misdescribes the system (for example it names HTTP 400 and the route answers 422), implement the stated intent, record the correction, and tell the owner.
