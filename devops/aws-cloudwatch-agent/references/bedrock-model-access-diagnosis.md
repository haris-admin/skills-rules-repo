# Bedrock Model Access Diagnosis

## Problem
`AccessDeniedException` when invoking Bedrock models despite:
- `AmazonBedrockFullAccess` IAM policy attached
- EULA accepted in Bedrock console
- Models visible in `list-foundation-models`
- Correct region

## Root Cause
Bedrock has **two separate gates** for model access:
1. **IAM permissions** — Does the user/role have `bedrock:InvokeModel` permission?
2. **Model Access** — Has the model been explicitly **granted** in the Bedrock console under "Model Access"?

An accepted EULA + correct IAM is NOT sufficient. Each model must be toggled ON in Bedrock → Model Access → Manage Model Access. For newer models (Claude 5, Opus 4-8, Fable-5), AWS Support may need to manually add them. This is the standard `AccessDeniedException` despite everything looking correct.

## Diagnostic Pipeline

### 1. Verify IAM Identity
```bash
aws sts get-caller-identity --region ap-southeast-2 --output json
# Returns Account, UserId, Arn — confirm it's the right account
```

### 2. Check IAM Policy
```bash
# List attached policies
aws iam list-attached-user-policies --user-name IAM_MONITOR --region ap-southeast-2 --output json
# Look for: "AmazonBedrockFullAccess" or "BedrockFullAccess" or custom with bedrock:InvokeModel

# If inline policies:
aws iam list-user-policies --user-name IAM_MONITOR --region ap-southeast-2 --output json
```

### 3. List Available Models (Foundation)
```bash
aws bedrock list-foundation-models \
  --region ap-southeast-2 \
  --query "modelSummaries[?contains(providerName,'Anthropic')].[modelId,modelStatus]" \
  --output json
```
Models showing up here means they exist in the region, NOT that the account has access.

### 4. Check Custom Models and Provisioned Throughput
```bash
aws bedrock list-custom-models --region ap-southeast-2 --output json
aws bedrock list-provisioned-model-throughputs --region ap-southeast-2 --output json
```
Empty lists = no model access granted yet.

### 5. Test Invocation Directly
```python
import boto3, json, base64

client = boto3.client("bedrock-runtime", region_name="ap-southeast-2")
body = json.dumps({
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 5,
    "messages": [{"role": "user", "content": "hi"}]
})
body_b64 = base64.b64encode(body.encode()).decode()

for model in ["anthropic.claude-sonnet-5", "anthropic.claude-opus-4-8"]:
    try:
        resp = client.invoke_model(
            modelId=model,
            body=body.encode(),
            contentType="application/json",
            accept="application/json"
        )
        print(f"{model}: LIVE")
    except client.exceptions.AccessDeniedException:
        print(f"{model}: DENIED — model not granted in Model Access")
    except Exception as e:
        print(f"{model}: {e}")
```

### 6. Try Different Regions
```bash
for region in ap-southeast-2 us-west-2 us-east-1; do
  echo -n "$region: "
  aws bedrock-runtime invoke-model \
    --model-id anthropic.claude-sonnet-5 \
    --body "$(echo '{"anthropic_version":"bedrock-2023-05-31","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}' | base64)" \
    --content-type application/json --accept application/json \
    --region $region /tmp/t.json 2>&1 | head -1
done
```
If ALL regions return AccessDeniedException, the model hasn't been granted to the account anywhere.

### 7. Check AWS Support Case
```bash
aws support describe-cases --case-id-list CASE_ID --region us-east-1 --output json
```
Note: `aws support` commands require the `support` feature to be enabled for the IAM user.

## Resolution Paths

| Scenario | Fix |
|----------|-----|
| IAM policy missing bedrock:InvokeModel | Attach `AmazonBedrockFullAccess` or custom policy |
| Models listed but not granted | Go to Bedrock console → Model Access → Manage Model Access → toggle models ON |
| "AccessDeniedException" despite everything above | **AWS Support case required** — the model needs to be added to the account's backend allowlist |
| Support case open but not resolved | Reply to case asking for status update; escalation may be needed |

## Support Case Pattern (for newer Claude models)

Support case subject template:
```
Bedrock model access request: anthropic.claude-sonnet-5, anthropic.claude-opus-4-8,
anthropic.claude-fable-5 (ap-southeast-2) - AccessDeniedException despite accepted EULA and correct IAM
```

Include in the case:
1. Account ID
2. Region(s) needed
3. Model IDs (exact, from list-foundation-models)
4. Error message: `AccessDeniedException`
5. Confirmation that EULA was accepted
6. IAM policy attached: `AmazonBedrockFullAccess`
7. Request: "Please grant access to these models in ap-southeast-2"

## Verification
After resolution:
```bash
aws bedrock-runtime invoke-model \
  --model-id anthropic.claude-sonnet-5 \
  --body "$(echo '{"anthropic_version":"bedrock-2023-05-31","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}' | base64)" \
  --content-type application/json --accept application/json \
  --region ap-southeast-2 /tmp/t.json && cat /tmp/t.json
```
Should return valid response with content, not AccessDeniedException.
