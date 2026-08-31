# EC2 Instance Discovery Commands

## List ALL instances (all states, all tags)
```bash
aws ec2 describe-instances --region ap-southeast-2 \
  --query "Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType,LaunchTime,Tags[?Key=='Name'].Value|[0]]" \
  --output table
```

## Find by Name tag (running only)
```bash
aws ec2 describe-instances --region ap-southeast-2 \
  --filters "Name=tag:Name,Values=amlhive-prod-backend" "Name=instance-state-name,Values=running" \
  --query "Reservations[*].Instances[*].[InstanceId,InstanceType,LaunchTime]" \
  --output json
```

## Find by Name tag (all states)
```bash
aws ec2 describe-instances --region ap-southeast-2 \
  --filters "Name=tag:Name,Values=amlhive-prod-frontend" \
  --query "Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType]" \
  --output table
```

## Get IAM profile for an instance
```bash
aws ec2 describe-instances --instance-ids i-xxxxxxxxxxxxxxxxx \
  --query "Reservations[0].Instances[0].[InstanceId,IamInstanceProfile.Arn]" \
  --region ap-southeast-2 --output json
```

## SSM describe (check agent registration)
```bash
aws ssm describe-instance-information \
  --filters "Key=InstanceIds,Values=i-xxxxxxxxxxxxxxxxx" \
  --region ap-southeast-2 --output json

# All SSM instances
aws ssm describe-instance-information --region ap-southeast-2 --output json
```

## Cross-reference EC2 vs SSM
```bash
python3 << 'EOF'
import subprocess, json
env = load_aws_creds()
# Get all EC2 instances
ec2 = json.loads(subprocess.run(["aws","ec2","describe-instances","--region","ap-southeast-2","--output","json"],
    capture_output=True, text=True, timeout=30, env=env).stdout)
# Get all SSM instances
ssm = json.loads(subprocess.run(["aws","ssm","describe-instance-information","--region","ap-southeast-2","--output","json"],
    capture_output=True, text=True, timeout=15, env=env).stdout)
ssm_ids = set(i["InstanceId"] for i in ssm.get("InstanceInformationList",[]))
for res in ec2.get("Reservations",[]):
    for inst in res.get("Instances",[]):
        tags = {t["Key"]: t["Value"] for t in inst.get("Tags",[])}
        if tags.get("Name"):
            ssm_ok = "✅ SSM" if inst["InstanceId"] in ssm_ids else "❌ NO SSM"
            print(f"{inst['InstanceId']:20s} {inst['State']['Name']:12s} {tags['Name']:25s} {ssm_ok}")
EOF
```

## Instance Tag Drift (Jul 2026)
Tags can change when instances are recycled. The current AMLHive production tags are:
- Backend: `amlhive-prod-backend`
- Frontend: `amlhive-prod-frontend`

Previously: `amlhive-prod` and `amlhive-frontend`. If auto-discovery fails, check current tags:
```bash
aws ec2 describe-tags --filters "Name=resource-id,Values=i-xxxxxxxxx" --region ap-southeast-2
```
