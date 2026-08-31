# No root or unbounded credentials for agents (all agents, all repos)

Applies to **every** agent surface — Claude Code, Codex, Cursor, Gemini/Antigravity, and any
browser-automation tool — whenever an agent touches a cloud console, a cloud CLI, or any
authenticated session. An agent must never operate with credentials that have **no permission
ceiling**.

## Why this exists

**30 Jul – 1 Aug 2026, AWS account `560205084533`.** The `yourapp-cloudtrail-root-usage` CloudWatch
alarm (C345 D2 — *"Root should never be used — treat as an incident"*) fired twice. CloudTrail
showed two **root** console sessions:

| Time (UTC) | Activity |
|---|---|
| 30 Jul 05:42 | `ConsoleLogin` → `ListNotificationHubs`, `ListApplications`, `DescribeRegions` |
| 30 Jul 23:13 | `ConsoleLogin` → 48× `GetFoundationModelAvailability`, `ListFoundationModels`, `GetUseCaseForModelAccess` |

All 50 calls were **reads**: `mfaAuthenticated: true`, Australian source IP, Chrome on macOS. Asked
who it was, the human answered *"probably me"*, then *"or codex using browser"*. **Attribution was
never established.**

The second answer is the reason this rule exists. If an AI agent was driving a browser inside an
authenticated **root** session, that is a privilege-boundary failure *regardless of outcome*:

- **Root has no permission ceiling.** The calls happened to be reads, but no IAM policy, SCP, or
  approval step would have stopped a write, a key rotation, or a resource deletion. The benign
  outcome was **luck, not control**.
- **Browser agents inherit whatever session the browser already holds.** An agent told "check
  Bedrock model access" will happily use a logged-in root tab, with no signal that it is unbounded.
  The agent cannot detect this and will not warn you.
- It silently defeats every least-privilege control built in `00e`/`00f`, and sidesteps
  `privilege-change-blast-radius-audit.md`.
- **The pattern is live, not hypothetical** — agent browser automation is in routine use on this
  machine (a `claude-in-chrome` session queried data.gov.au the same week).

Contributing cause worth remembering: the agent had told the human that the AWS **credit balance**
is only readable from the Billing console, which plausibly prompted a root login. **An agent's own
instruction can be what triggers the root usage it later flags.** Prefer suggesting a
least-privilege path over "go log into the console."

## Rules

1. **Never operate, or ask a human to operate, an AWS/GCP/Azure **root** or account-owner session
   for agent work.** Not for reads, not "just to check something". If a task appears to need root,
   stop and say so — do not proceed via root and mention it afterwards.

2. **Never drive a browser that holds a root/account-owner session.** Before any browser automation
   against a cloud console, confirm the logged-in identity is a scoped role. If it is root, or you
   cannot tell, **stop and ask the human to sign out of root first**. "I could not determine the
   identity" is a stop condition, not a reason to continue.

3. **Use a scoped identity with an explicit permission boundary.** Console/CLI work uses a
   least-privilege IAM role or user. In this repo, prefer `--profile yourapp` (see
   `aws-profile-and-secret-recovery.md`); never fall back to root because a scoped call was denied —
   an `AccessDenied` is information, not an obstacle to route around.

4. **Fix the permission gap, don't escalate around it.** If a scoped identity cannot do a legitimate
   task, the correct outcome is a grant to that identity, recorded — not a root session. Example
   from this incident: enabling *"IAM user and role access to Billing information"* removes the only
   two reasons root was used (credit balance, Bedrock model access).

5. **Treat every root-usage alarm as an incident until attributed.** Do not close it on "probably
   me". Record what was done, whether calls were reads or writes, the source IP, MFA status, and the
   attribution status **as stated** — never upgrade a qualified answer into a confirmation (see
   `no-fabricated-human-decisions.md`). A fired-and-dismissed security alarm must leave a written
   trace, or the next one gets waved through.

6. **Casual root usage destroys the alarm's value.** Every routine root login trains the team to
   ignore the alert. This repo already has the cautionary case: the AWS cost budget sat in `ALARM`
   at 210% of limit for two weeks and produced no response.

## Applying this beyond AWS

The same reasoning covers any unbounded credential an agent might inherit: a `postgres`
superuser/owner role (see `issue-153` and the C317 role split), a GitHub owner/admin token where a
scoped one exists, a Cloudflare account-wide token, or a password manager unlocked in an
agent-drivable browser. **The question is never "did anything bad happen" — it is "what would have
stopped it".**

## Verification

- `aws cloudtrail lookup-events --lookup-attributes AttributeKey=Username,AttributeValue=root`
  should return **nothing** for any window in which an agent was working.
- Root console logins are recorded in `us-east-1` as `ConsoleLogin` even for other-region activity —
  check there, not only in the working region.
- Confirm the alarm still routes somewhere a human reads (in this repo, see C96a `T96a.11`'s tiered
  routing: `admin@yourapp.com.au` for all AWS alarms, escalated to `shoaib@yourapp.com.au` +
  `hhsiddiqui@gmail.com` when required).
