# A Lambda image must match the function architecture, and a deploy is proven by a run (all agents)

Applies to anything that sets a container image on an AWS Lambda function, by hand, by Terraform or by CI, and to anyone reporting that such a deploy worked.

## Why this exists

20 Oct 2026, Tap-Ease Lambda ETL. The staging function `tapease-clover-sync-staging` is arm64. A CI-built `linux/amd64` image from the shared dev ECR repository was set on it. Lambda accepted the update (`LastUpdateStatus: Successful`, `State: Active`) and the one-minute schedule stayed enabled. Every run then failed in about 18 ms with `Runtime.InvalidEntrypoint`, nothing was logged by the application, and nobody was alerted. It was found about 25 hours later only because someone asked whether the function used its OAuth token. Recovery took one rebuild and one in-place deploy.

## Core Directives

1. **Match architecture before you set an image.** Read the image config (`architecture`) and the function `Architectures`. They must be equal. A mismatch is a stop, not a warning.
2. **A shared repository does not mean a shared image.** When CI and a manual script push different architectures to one ECR repository, never point a function at `latest` or a commit tag. Pin by digest or by a tag prefix that only one builder writes.
3. **`Successful` is not proof.** `LastUpdateStatus` says the update was accepted. Prove a deploy with a fresh application log line from the new version and an `Errors` metric of 0 for the next scheduled runs.
4. **Alarm on errors for any scheduled function.** An `Errors` alarm (greater than 0 for two periods) on every scheduled Lambda, staging included. A function that fails every run and says nothing is the worst case.
5. **Record who set the image.** If you find an image you did not set, say so and look for the writer (CI job, Terraform state, console) before you overwrite it, so the cause is fixed and not only the symptom.

## Patterns to Follow

```bash
aws lambda get-function-configuration --function-name <fn> --query '[Architectures,LastUpdateStatus]'
aws ecr batch-get-image --repository-name <repo> --image-ids imageDigest=<digest> --query 'images[0].imageManifest'   # then read config.architecture
aws cloudwatch get-metric-statistics --namespace AWS/Lambda --metric-name Errors --dimensions Name=FunctionName,Value=<fn> ...
```

## Patterns to Avoid

- Treating `LastUpdateStatus: Successful` as "it works".
- Letting `latest` or a commit tag in a mixed-architecture repository decide what a function runs.
- Reading an empty log as "nothing to report" without checking the invocation and error counts.
