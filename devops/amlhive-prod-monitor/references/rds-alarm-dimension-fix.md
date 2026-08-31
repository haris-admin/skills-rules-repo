# RDS CloudWatch Alarm Dimension Fix

## Symptom
Monitor shows 3 RDS alarms in INSUFFICIENT_DATA state despite metrics flowing:
- `amlhive-rds-high-cpu`
- `amlhive-rds-high-connections`
- `amlhive-rds-low-free-storage`

## Root Cause
The alarm's `DBInstanceIdentifier` dimension is set to an internal RDS resource ID (e.g., `db-RJ5PJ64M2VYAPOYFOWTC63KWH4`) instead of the actual DB instance name (`amlhive-prod`). CloudWatch RDS metrics publish with `DBInstanceIdentifier=amlhive-prod`, so the alarm can never match data points → permanent INSUFFICIENT_DATA.

## Verification

```python
import sys, subprocess, json
sys.path.insert(0, "/home/habib/.hermes/scripts")
from amlhive_prod_monitor import load_aws_creds, REGION

env = load_aws_creds()

# Check current alarm dimensions
cmd = [
    "aws", "cloudwatch", "describe-alarms", "--region", REGION,
    "--alarm-names",
    "amlhive-rds-high-cpu",
    "amlhive-rds-high-connections",
    "amlhive-rds-low-free-storage",
    "--query", "MetricAlarms[].[AlarmName,Dimensions[0].Value,StateValue]",
    "--output", "table"
]
subprocess.run(cmd, env=env)

# Confirm metrics DO flow for the correct dimension
from datetime import datetime, timedelta, timezone
now = datetime.now(timezone.utc)
start = now - timedelta(hours=2)
for metric in ["CPUUtilization", "DatabaseConnections", "FreeStorageSpace"]:
    cmd = [
        "aws", "cloudwatch", "get-metric-statistics",
        "--region", REGION,
        "--namespace", "AWS/RDS",
        "--metric-name", metric,
        "--dimensions", "Name=DBInstanceIdentifier,Value=amlhive-prod",
        "--start-time", start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "--end-time", now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "--period", "300",
        "--statistics", "Average",
        "--output", "json"
    ]
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    points = json.loads(result.stdout).get("Datapoints", [])
    print(f"{metric}: {len(points)} points")
```

## Fix Commands

Run these to overwrite all 3 alarms with the correct dimension:

```python
import subprocess
# (load env same as above)

alarms = [
    ("amlhive-rds-high-connections", "DatabaseConnections", 80, "GreaterThanThreshold", 2, "Average", "Count"),
    ("amlhive-rds-high-cpu", "CPUUtilization", 80, "GreaterThanThreshold", 3, "Average", "Percent"),
    ("amlhive-rds-low-free-storage", "FreeStorageSpace", 10737418240, "LessThanThreshold", 2, "Average", "Bytes"),
]

for name, metric, threshold, op, periods, stat, unit in alarms:
    cmd = [
        "aws", "cloudwatch", "put-metric-alarm",
        "--region", REGION,
        "--alarm-name", name,
        "--metric-name", metric,
        "--namespace", "AWS/RDS",
        "--statistic", stat,
        "--period", "300",
        "--evaluation-periods", str(periods),
        "--threshold", str(threshold),
        "--comparison-operator", op,
        "--dimensions", "Name=DBInstanceIdentifier,Value=amlhive-prod",
        "--unit", unit,
    ]
    cmd += ["--treat-missing-data", "breaching" if "Greater" in op else "notBreaching"]
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    print(f"{name}: {'OK' if result.returncode == 0 else 'FAILED: ' + result.stderr.strip()}")
```

## After Fix
- Alarms transition from INSUFFICIENT_DATA within ~15 min (3 evaluation periods × 300s)
- Verify with `describe-alarms` query above
- If still INSUFFICIENT_DATA after 20 min, check that the metric name/statistic/period match what's actually published
