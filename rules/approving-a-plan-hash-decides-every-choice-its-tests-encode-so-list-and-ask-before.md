# Approving a plan hash decides every choice its tests encode, so list them and ask first

A test that asserts one reading of an open choice makes that choice part of the approval. Do not call such a choice non-blocking.

**Scope:** plans whose tests are written before the owner has answered every open choice.

---

## Core Directives

1. **List the encoded choices** under one heading named like 'Decided by approving this hash', in the STATE line and in section 0.
2. **Ask them in a batch with a recommendation** (accept all, one by one, or change some) and record the answer verbatim.
3. **Do not edit the owner's decision text** to fit the plan; record a correction note instead (for example a wrong count in an option description).
4. **A requirement change voids reviews of the changed scope**: renew them.

## Why this exists

**23 Nov 2026 (SonoVantage database plan):** reviews 6 and 7 found that choices C7, C10, C14 to C17 and C20 were called non-blocking while tests already depended on them. The owner accepted them as a batch (D76) before revision 8.
