# Check the ticket board for the same screen before building it (all agents)

Before changing a screen, search the ticket board for open tickets that mention the same screen or fields, and design to all of them.

## Why this exists
**11 Nov 2026, Tap-Ease Start Shift screen:** Haris asked for the ABN first, smaller title and Start shift focused (C80). An open Plane ticket (TAPEA-150) already asked for the order ABN, then the state selector, then the taxi number. The assistant built ABN, taxi number, state selector, shipped it to a device, and only found the ticket afterwards; the order was changed in a follow-up and a new build was needed.

## Rules
1. Search the board (titles and descriptions) for the screen name and each field name before writing the spec. Read tickets that are In Progress or Todo, and tickets created today.
2. List the related tickets in the spec's proposal and state how the design satisfies each, or which conflict needs a decision.
3. When two requests conflict, ask which governs and record both answers verbatim.
4. After finishing, update every related ticket, not only the one you were asked about.
