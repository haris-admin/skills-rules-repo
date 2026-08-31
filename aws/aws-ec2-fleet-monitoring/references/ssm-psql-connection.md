# SSM + psql Connection Reference

## Quick Diagnostics

```bash
# Check if instance is in SSM
aws ssm describe-instance-information \
  --filters "Key=InstanceIds,Values=i-xxxxxxxxxxxxxxxxx" \
  --region ap-southeast-2

# List all SSM-registered instances
aws ssm describe-instance-information --region ap-southeast-2

# Check IAM role on instance
aws ec2 describe-instances --instance-ids i-xxxxxxxxxxxxxxxxx \
  --query "Reservations[0].Instances[0].[InstanceId,IamInstanceProfile.Arn]" \
  --region ap-southeast-2

# Run command and get result
aws ssm send-command --instance-ids i-xxxxxxxxxxxxxxxxx \
  --document-name AWS-RunShellScript \
  --parameters 'commands=["echo hello"]' \
  --output json --region ap-southeast-2

# Install psql on Amazon Linux 2023
aws ssm send-command --instance-ids i-xxxxxxxxxxxxxxxxx \
  --document-name AWS-RunShellScript \
  --parameters 'commands=["sudo yum install -y postgresql15"]' \
  --output json --region ap-southeast-2
```

## Instance Recycling History (AMLHive)
| Date | Backend ID | Frontend ID |
|------|-----------|-------------|
| Jun 2026 | i-02276d537152046d9 | i-0cf88f6d601f8d4a9 |
| Jul 2026 (early) | i-0bda9f0fde09217e7 | i-0cb6f51d4ff7300b3 |
| Jul 2026 (mid) | i-052ca2acc74707378 (no SSM!) | i-0eb3f1faa213420ce |
| Current | i-05e1c3d33cacb4015 | i-0eb3f1faa213420ce |

## RDS Connection
- **Endpoint:** `amlhive-prod.ch4ykiy82n3q.ap-southeast-2.rds.amazonaws.com`
- **Database:** amlhive
- **User:** amlhive
- **Password:** In Secrets Manager at `amlhive/prod/rds`
- **SSL:** Required (`PGSSLMODE=require`)
- **VPC-only:** NOT reachable from WSL directly — must tunnel through SSM

## psql Column Quirks
- All status values are UPPERCASE: `OPEN`, `ACTIVE`, `SIGNED_OFF`
- `clients` uses `is_archived` (boolean, not `is_active`)
- `kyb_records` uses `status` (not `verification_status`)
- Timestamps in UTC
