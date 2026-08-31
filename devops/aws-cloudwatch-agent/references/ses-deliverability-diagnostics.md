# SES Deliverability Diagnostics — TapEase

## Quick Checks

```bash
alias ses="aws --profile tapease ses --region ap-southeast-2"
```

| Check | Command | What to Look For |
|---|---|---|
| Verified identities | `ses list-identities` | `tapease.com.au`, `help@tapease.com.au` present |
| Verification status | `ses get-identity-verification-attributes --identities tapease.com.au help@tapease.com.au` | `VerificationStatus: Success` |
| Sending quota | `ses get-send-quota` | `Max24HourSend: 50000`, `SentLast24Hours` well below limit |
| DKIM status | `ses get-identity-dkim-attributes --identities tapease.com.au` | `DkimEnabled: true` — if false, enable it |
| MAIL FROM domain | `ses get-identity-mail-from-domain-attributes --identities tapease.com.au` | `MailFromDomainStatus: Success` for `mail.tapease.com.au` |
| Bounce config | `ses get-identity-notification-attributes --identities tapease.com.au` | `ForwardingEnabled: true` |

## DKIM — Most Common Deliverability Issue

SES may return 200 OK for `SendEmail` but the receiving server (Gmail, Outlook)
may reject or spam-folder the message if DKIM is disabled.

**Check:**
```bash
aws --profile tapease ses get-identity-dkim-attributes \
  --region ap-southeast-2 --identities tapease.com.au
```

**Expected:** `{"DkimEnabled": true, "DkimVerificationStatus": "Success"}`

**If disabled, fix with:**
```bash
aws --profile tapease ses set-identity-dkim-enabled \
  --region ap-southeast-2 \
  --identity tapease.com.au \
  --dkim-enabled
```

**DNS records to publish** (3 CNAMEs):
```
oceqbnlzjdvxewqe4nbgmogr2k6ztsip._domainkey.tapease.com.au → dkim-mta-01.amazonses.com
vekkzrg3bxge3nogbzo6olwvdla4gce3._domainkey.tapease.com.au → dkim-mta-02.amazonses.com
hz6ai7dkyciqld7m6oix2oif3ajhpdqz._domainkey.tapease.com.au → dkim-mta-03.amazonses.com
```

**Verify propagation:**
```bash
dig CNAME oceqbnlzjdvxewqe4nbgmogr2k6ztsip._domainkey.tapease.com.au +short
# → "dkim-mta-01.amazonses.com"
```

## SPF

Add to DNS:
```
tapease.com.au TXT "v=spf1 include:amazonses.com ~all"
```

## Password Reset Email Flow

Sender: `help@tapease.com.au` (from `EMAIL_FROM` in .env)
Reset link domain: `https://tapease.com.au/reset-password?token=...` (from `EMAIL_URL`)
SES region: `ap-southeast-2`
Auth: IAM role (`SES_USE_IAM_ROLE=true`) — uses instance profile

**The backend says "sent successfully" even when DKIM is disabled.**
This only means SES accepted the send — not that the email reached the user's inbox.
When DKIM is off, the email leaves SES but Gmail/Outlook apply stricter spam filtering.

## Sandbox Detection

SES sandbox accounts have `Max24HourSend: 200` and can only send to verified
identities. TapEase has `Max24HourSend: 50000` — production-level, not sandbox.

## Bounce & Complaint Notifications

Currently `ForwardingEnabled: true` with no SNS topic configured.
Bounce/complaint notifications go to the identity's verified email inbox.

To enable proactive monitoring, create an SNS topic:
```bash
aws sns create-topic --name tapease-ses-bounces --region ap-southeast-2
aws ses set-identity-notification-topic \
  --region ap-southeast-2 \
  --identity tapease.com.au \
  --notification-type Bounce \
  --sns-topic arn:aws:sns:ap-southeast-2:707843605914:tapease-ses-bounces
```

## Permission Limits

The `IAM_GRAFANA` user (used by `aws --profile tapease`) has limited SES access:
- ✅ `ListIdentities`, `GetIdentityVerificationAttributes`, `GetIdentityDkimAttributes`
- ✅ `GetIdentityMailFromDomainAttributes`, `GetIdentityNotificationAttributes`
- ✅ `GetSendQuota`
- ❌ `GetSendStatistics`, `ListIdentityPolicies`, `GetAccountSendingEnabled`

For full SES debugging, use the EC2 instance role (`tapease-backend-role-production`)
via SSM Run Command.
