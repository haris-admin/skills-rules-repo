# Check the instance role before changing a container log driver

Switching a container to the `awslogs` driver makes the container fail to start if the host's IAM role cannot write the log group. Read the role first.

**Scope:** any agent changing `logging:` in a compose file or Docker daemon config on an EC2 host.

## Why this exists

Tap-Ease C84, 15 Nov 2026. The compose default sent staging logs to `/tapease/pos-backend/staging`. A read-only look at the staging instance profile showed its logs policy allowed only `/tapease/dev/*`, so the driver would have been denied and the staging container would not have started. The default was changed to `/tapease/dev/pos-backend`, with a test, before any deploy.

## Core Directives

1. **Read the role:** `aws ec2 describe-instances` for the instance profile, then `aws iam get-role-policy` for the logs policy, and compare the group name with its allowed resource.
2. **Staging and production use different groups** and different roles; do not share one default.
3. **A group created by the driver has no retention.** Set it (for example 30 days) or add it to Terraform.
4. **Production infrastructure in Terraform is applied by the owner.** Run the plan, read it, and if the plan is empty check AWS before assuming something is wrong (the resources may already exist).
5. **After the deploy, read CloudWatch, not `docker logs`:** the host command may stop working with this driver.

## Patterns to Avoid

- Copying the production log group name into the staging compose file.
- Treating an empty Terraform plan as success without confirming the resources exist.
