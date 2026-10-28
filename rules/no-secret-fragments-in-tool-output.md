# Never print secrets, tokens or fragments of them (all agents, all repos)

Applies to every command output, log excerpt, document and message an agent produces.

## Why this exists

**26 Oct 2026:** a production log excerpt printed the decoded JWT payload (user id, email, token id, session id) and a token prefix. Haris:
"Make sure you don't print the token here." The same day the auto mode classifier blocked printing even the last four characters of a stored
Clover app secret ("Credential Materialization").

## Rules

1. Before showing a log, filter lines that carry JWT payloads or token prefixes (in Tap-Ease the `trace_middleware` lines).
2. Compare a secret with booleans (same, present, length class) or compute inside a script that prints only the verdict. If a masked fragment
   would help the user, give the user a short script to run themselves.
3. Never write a one-time code, token or secret into a repo file, a document, an artifact or memory. Delete probe scripts that embedded one.
4. A probe that needs a production secret runs on the box that already has access, reads it there, and prints status and reason fields only.
5. If the classifier blocks a secret-handling action, stop and tell the user. Do not work around it.
6. Record application-side leaks you see (for example logging a JWT payload) as an open item.
