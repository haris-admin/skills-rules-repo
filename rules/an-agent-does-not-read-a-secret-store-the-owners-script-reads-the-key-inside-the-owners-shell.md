# An agent does not read a secret store; the owner's script reads the key inside the owner's shell

If a task needs a credential that lives in a secrets manager, the agent writes a script that fetches one key and uses it in the owner's shell. The value never enters the agent's context.

**Scope:** any task where the owner says the token is in a secrets store and offers it to the agent.

---

## Core Directives

1. **Decline the read, offer the script.** Say plainly that a shared production secret holds more than one key and that the agent will not read it; write a script that reads ONE named key with the owner's own profile and region.
2. **Never print it, never put it in arguments.** Pass it to the tool through a stdin config or an environment variable, never on a command line, and never echo it.
3. **Use the same profile and region as the other scripts.** A `ResourceNotFound` from a secrets manager usually means the wrong default profile or region, so read the sibling scripts for the right ones.
4. **Fail visibly.** If the key, profile or scope is wrong, print which of those to check and exit non-zero; do not fall back to anything.

## Why this exists

**23 Nov 2026 (SonoVantage):** the owner pointed at the production secret for a Cloudflare token. The script read the key itself; the first run failed with ResourceNotFound because the shell's default profile was wrong, and the fix was the project's `chargerail` profile and `ap-southeast-2`. The token never appeared in the chat. Related: [no secret fragments in tool output](./no-secret-fragments-in-tool-output.md).
