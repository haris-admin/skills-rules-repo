# Production logs are archived to storage before CloudWatch retention deletes them (all projects)

Applies whenever an agent reviews or designs production logging.

## Why this exists

Tap-Ease POS, 21 Nov 2026. The production POS backend log group `/tapease/pos-backend/production` had 30-day retention, no subscription filter and no export task, so
its logs would be deleted permanently. The POS nginx groups were empty (0 bytes, agent not shipping) and the repo had no S3 log resource. Haris asked for backend logs to be
routed to S3 (RW-109). Draft spec: `openspec/changes/log-archive-s3-bucket/` in the mapp repo.

## Rule

1. In a production health review, list for each log group: retention, subscription filters, export tasks, and stored bytes. Empty groups are a finding.
2. Logs that matter for payments or audit are archived to a private, encrypted bucket with a lifecycle rule before retention deletes them.
3. A bucket alone is not enough. Encryption, public access block, bucket policy, lifecycle and the shipping path (Firehose or export task) are separate specs and all must exist before a log is written.
4. Personal data in logs is kept in full by owner decision; secrets and full card numbers stay masked (`external-calls-logged-request-and-response-mask-secrets.md`).
5. Name the account and profile read. If a log the owner mentions (for example CloudFront) is not found, ask which account, do not assume none exists.

## How to apply

Run the checks read-only with explicit `--profile` and `--region`. Related: `a-log-search-proves-absence-only-for-the-window-it-covers.md`.
