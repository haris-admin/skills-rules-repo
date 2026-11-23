# A failing FIFO consumer blocks its message group, so check the DLQ after every test

On an SQS FIFO queue a message that cannot be processed holds back every later message in the same `MessageGroupId`. Read the queue depths and the log after each staging test, not only at the end.

**Scope:** any agent testing an SQS FIFO integration (Portal and MApp share `pos-to-portal.fifo` and `portal-to-pos.fifo`).

## Why this exists

Tap-Ease Portal 4.60.01, 21 Nov 2026. MApp's `pos.shift.cancelled` carried four fields the Portal's strict model forbade. Each receive failed validation (`outcome=invalid_event`), the log said "preserving FIFO order ... blocked_after_retry", and the terminal's group stalled until the message reached the dead-letter queue after 5 receives. The owner's shift tests still passed because live start and close run over HTTP, so nothing looked wrong until the queue counts and log were read. Separately, two Portal terminal events landed in the other DLQ because MApp rejected them.

## Core Directives

1. **After every staging test read:** `ApproximateNumberOfMessages` and `ApproximateNumberOfMessagesNotVisible` for both queues and both DLQs, and the log lines `SQS inbound response` and `SQS outbound result` with their `outcome=`. A non-zero DLQ count means a contract gap, not noise.
2. **Count, do not print bodies,** when a message may hold personal data or tokens. The DLQ message ids and event ids are enough to ask the other side.
3. **A fix does not rescue a dead-lettered message.** After deploying the fix, move the message back (`aws sqs start-message-move-task --source-arn "<dlq arn>" --destination-arn "<queue arn>"`) with the owner's OK, then confirm `outcome=processed` and the database row.
4. **Business failures that cannot succeed on retry are answered, not retried.** Allowlist the stable failure code and publish the agreed rejection event (owner decision D10, 21 Nov 2026), so a bad message cannot hold a terminal's whole queue.
5. **A requirement that changes an old test changes the spec and the test together.** The old test required cancel conflicts to stay unacknowledged for DLQ redrive; D10 replaced that.
