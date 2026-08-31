# EC2 Instance Auto-Discovery by Name Tag

## Problem
EC2 instance IDs change every time an instance is recycled (AMI rebuild, auto-scaling, termination). Hardcoded IDs in monitor scripts cause persistent P0 "Instance not found" alerts.

## Solution: `get_instance_id()` Tag-Based Discovery

```python
import subprocess, json

_INSTANCE_CACHE = {}
def get_instance_id(name_tag, hardcoded_fallback=None):
    """Discover running EC2 instance ID by Name tag. Caches per script run."""
    if name_tag in _INSTANCE_CACHE:
        return _INSTANCE_CACHE[name_tag]
    try:
        r = subprocess.run([
            "aws","ec2","describe-instances",
            "--filters",f"Name=tag:Name,Values={name_tag}","Name=instance-state-name,Values=running",
            "--query","Reservations[*].Instances[*].[InstanceId]",
            "--region", "ap-southeast-2", "--output","json"
        ], capture_output=True, text=True, timeout=15)
        data = json.loads(r.stdout)
        if data and data[0] and data[0][0]:
            inst_id = data[0][0][0]
            _INSTANCE_CACHE[name_tag] = inst_id
            return inst_id
    except Exception:
        pass
    if hardcoded_fallback:
        _INSTANCE_CACHE[name_tag] = hardcoded_fallback
        return hardcoded_fallback
    return None
```

## How to Use

```python
# At module level — runs once on import
# The fallback IDs below are the LAST KNOWN CORRECT values.
# Update them when instances are recycled if auto-discovery fails.
BACKEND_ID = get_instance_id("amlhive-prod", "i-05e1c3d33cacb4015")
FRONTEND_ID = get_instance_id("amlhive-frontend", "i-0eb3f1faa213420ce")
```

- First argument: EC2 Name tag value
- Second argument: Fallback ID for when EC2 is unreachable (script continues working during outages)
- Cached: only calls `describe-instances` once per script run
- Importable: put it in a shared module, import from other scripts

## ⚠️ Important: SSM Registration is Separate

Tag-based discovery finds RUNNING EC2 instances, but an instance can be running WITHOUT SSM Agent registered. This is a recurring issue when instances are launched without the proper IAM instance profile.

**To verify SSM is working:**
```bash
aws ssm describe-instance-information \
  --filters "Key=InstanceIds,Values=$(get_instance_id amlhive-prod)" \
  --region ap-southeast-2
# If InstanceInformationList is empty → no SSM; check IAM role
```

**If SSM is missing:**
1. Check IAM instance profile: `aws ec2 describe-instances --instance-ids <id> --query 'Reservations[0].Instances[0].IamInstanceProfile'`
2. The role must have `AmazonSSMManagedInstanceCore` attached
3. If no instance profile is attached, create one with the SSM managed policy and associate it via `aws ec2 associate-iam-instance-profile`
4. The SSM agent takes 1-2 minutes to register after the role is attached

## Recycle History (AMLHive)

| Date | Backend ID | Frontend ID | Notes |
|------|-----------|-------------|-------|
| Jul 19 2026 | `i-05e1c3d33cacb4015` | `i-0eb3f1faa213420ce` | **Current.** Both SSM Online. Backend has psql installed (yum). |
| Jul 18 2026 | `i-052ca2acc74707378` | (same) | Launched Jul 18 13:38. **This backend had NO SSM** — replaced with i-05e1c3d3... |
| Jul 16 2026 | `i-0bda9f0fde09217e7` | `i-0cb6f51d4ff7300b3` | Replaced Jul 16 13:31. Previous instances terminated. |
| Jun/Jul 2026 | `i-02276d537152046d9` | `i-0cf88f6d601f8d4a9` | Original instances from June 2026 deployment. |

## Where Applied
- `amlhive_prod_monitor.py` — `BACKEND_INSTANCE_ID`, `FRONTEND_INSTANCE_ID`
- `amlhive_daily_report.py` — `BACKEND_ID`

## Self-Test Command
```bash
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=amlhive-prod" "Name=instance-state-name,Values=running" \
  --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,LaunchTime]' \
  --region ap-southeast-2 --output table
```
