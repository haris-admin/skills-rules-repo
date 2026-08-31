# Credential Verification — Cross-Platform Debugging

**When:** API calls fail with "Bad credentials" / 401 / InvalidClientTokenId / AuthFailure even though you know credentials exist.

## The Pattern

Haris maintains credentials across **6+ locations**, not just 3. Token drift and outright expiration are common:

### Primary .env files
| Location | Path | Owner |
|----------|------|-------|
| WSL Pluto | `/home/habib/.hermes/.env` | Pluto/Hermes |
| Windows Hermes | `/mnt/c/Users/habib/.hermes/.env` | Hermes (Windows) |
| Windows OpenClaw | `/mnt/c/Users/habib/.openclaw/.env` | Gumby/OpenClaw |

### Secondary credential sources (often have DIFFERENT keys)
| Location | Path | Notes |
|----------|------|-------|
| OpenClaw workspace | `/mnt/c/Users/habib/.openclaw/workspace/.env` | Active session env — often newest |
| OpenClaw workspace config | `/mnt/c/Users/habib/.openclaw/workspace/config/.env` | Backup/synced copy |
| AWS credentials file | `~/.aws/credentials` (WSL and Windows) | Named profiles (`[tapease]`, `[default]`) |
| openclaw.json | `/mnt/c/Users/habib/.openclaw/openclaw.json` | References env vars like `${AWS_ACCESS_KEY_ID_TAPEASE}` |

**Key insight:** Different locations can hold completely different credential sets for the SAME service. Don't assume they're copies — check key suffixes.

## Diagnostic Steps

### 1. Sweep ALL locations for the credential
```bash
for f in \
  /home/habib/.hermes/.env \
  "/mnt/c/Users/habib/.hermes/.env" \
  "/mnt/c/Users/habib/.openclaw/.env" \
  "/mnt/c/Users/habib/.openclaw/workspace/.env" \
  "/mnt/c/Users/habib/.openclaw/workspace/config/.env" \
  ~/.aws/credentials; do
  echo "=== $f ==="
  grep -E '<VAR>' "$f" 2>/dev/null | sed 's/\(....\)[^=]*=/\1***=/'
done
```

### 2. Identify unique credential SETS by key suffix
```bash
# Show last 4 chars of each access key found — different suffixes = different IAM users
grep -rh "AWS_ACCESS_KEY" /home/habib/.hermes/.env "/mnt/c/Users/habib/.hermes/.env" \
  "/mnt/c/Users/habib/.openclaw/.env" "/mnt/c/Users/habib/.openclaw/workspace/.env" \
  ~/.aws/credentials 2>/dev/null | sed 's/.*\(....\)$/\1/'
```

### 3. Test each unique credential set
```bash
export AWS_ACCESS_KEY_ID=<key>
export AWS_SECRET_ACCESS_KEY=<secret>
export AWS_DEFAULT_REGION=ap-southeast-2  # try ap-south-1 if this fails
"/mnt/c/Program Files/Amazon/AWSCLIV2/aws.exe" sts get-caller-identity
# Also try: ec2 describe-instances --region ap-south-1 --query 'Reservations[*].Instances[*].InstanceId'
```

### 4. If ALL sets fail with InvalidClientTokenId / UnrecognizedClientException
The credentials are NOT just expired — they've been revoked or deleted from AWS. New IAM access keys must be generated in the AWS Console. No amount of cross-location syncing will help.

## Known Cases

### GitHub PAT (May 2026)
- **Symptom:** `gh auth login --with-token` returned "Bad credentials"
- **Root cause:** WSL `.env` had a completely different token (38 chars, `ghp_zrW27v...`) vs Windows `.env` (40 chars, `ghp_zreOSM...`). The WSL token was an invalid/expired copy.
- **Fix:** Copied the correct 40-char token from Windows `.env` to WSL `.env` via `sed`.

### DeepSeek API Key (May 2026)
- **Symptom:** All cron jobs failed with HTTP 401 "Authentication Fails, Your api key: ****d876 is invalid"
- **Root cause:** The DEEPSEEK_API_KEY ending in `d876` was rejected by DeepSeek's API. The key had been rotated/expired server-side.
- **Impact:** Every cron job (4 total) failed for ~48 hours. Mempalace Inbox Watcher (every 5min) racked up 200+ failures.
- **Fix:** Haris provided new key on May 25. Updated in `.env` and gateway auto-picked it up.
- **Detection pattern:** `grep "401.*invalid" ~/.hermes/logs/errors.log | head -3` — if you see `api key: ****XXXX is invalid`, the key needs rotation, not syncing.

### AWS Tapease Credentials (May 2026)
- **Symptom:** EC2, RDS, CloudWatch ALL failed. 4 different key sets found across 6 locations — ALL returned InvalidClientTokenId.
- **Root cause:** ALL IAM access keys for the Tapease AWS account had been revoked. Not a drift issue — complete key rotation needed.
- **Key sets found:** OTHX (3 locations), TOI2 (3 locations), NFMS/AMHIVE (2 locations), QLGS (`.aws/credentials` default). None valid.
- **Instance IDs preserved from cache:** `i-062b8ef5437ea6e2f` (backend), `i-0aca7e109d0f6e773` (frontend), region `ap-southeast-2`.
- **Fix needed:** Generate new IAM keys in AWS Console, update ALL credential locations.

## Honcho Write Failures

`honcho_conclude` silently fails with "Failed to save conclusion" when:
1. The Hermes gateway hasn't been restarted after `.env` changes that added Honcho configuration
2. The Honcho remote URL or workspace hasn't been picked up by the running gateway process

**Fix:** Restart the Hermes gateway after `.env` changes. The gateway only reads env vars at startup.

**Note:** `honcho_context` and `honcho_search` (reads) may work while `honcho_conclude` (write) fails — they may use different API endpoints or auth paths.
