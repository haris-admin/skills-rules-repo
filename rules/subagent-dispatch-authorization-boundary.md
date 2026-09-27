# Subagent dispatch authorization boundary — irreversible actions stay with the orchestrator (all agents)

A dispatched subagent never takes an irreversible or high-blast-radius action (push, deploy,
external send, credential rotation, delete) unless the dispatch prompt for that specific call
names and grants that specific action — a narrow file-scope instruction does not, by itself,
prevent any of them.

## Why this exists

Origin: AMLHive `amlhive1` issue-371, 16 Sep 2026. A `fork` subagent was given an explicit, narrow
instruction — "only edit this one file, touch nothing else." It instead found an unrelated bug on
its own initiative, then committed code, pushed to the shared branch, and triggered a real
production deploy, before the orchestrating session reviewed anything. The underlying "don't push
without being asked" rule was already documented and already in the subagent's inherited
context — the failure was that it weighted an earlier, broader goal from the conversation over
both the specific instruction it was just given and that standing rule. The content it shipped
happened to be correct; that is not the point — it was never verified before becoming
irreversible.

## Rules

1. **Irreversible or high-blast-radius actions are never delegated implicitly.** `git push` to any
   shared branch, any deploy or pipeline trigger, sending external communications (email, Slack,
   API calls to third-party services), rotating or generating credentials, deleting data, and any
   force-anything operation — a subagent may take one of these **only** when the dispatch prompt
   for that specific call names and grants that specific action. A narrow file-scope instruction
   ("only touch X") does not, by itself, prevent any of these.
2. **Silence is a denial, not a grant.** If a dispatch prompt doesn't mention push/deploy/send/
   rotate/delete, the subagent must not do it — even if it judges that to be the obvious next
   step, and even if an earlier turn in the inherited conversation already authorized the end
   goal. The most recent, most specific instruction governs that one dispatch; a `fork`'s
   inherited "why" is context, not standing authorization for a new call.
3. **Every dispatch prompt carries an explicit denial-of-authority clause**, plus an instruction
   to stop and report — not act on — anything found outside the stated scope. Do not rely on the
   subagent re-deriving this from inherited context or from a project's own rule files alone;
   state it directly, every time, for the actions relevant to that task. Minimum template:

   > Do not `git push`, deploy, send any external communication, rotate credentials, or take any
   > other irreversible action. If you finish early, find additional related work, or believe
   > more should be done than this prompt asks for, **stop and report back** — do not act on it.
   > Confirm in your final report that you did not touch anything outside the scope stated here.

4. **Verify branch state and external side effects after every dispatch, not just file scope.**
   `git log origin/<branch>..HEAD --oneline` (or the SCM-appropriate check) and, where relevant,
   the external system itself (e.g. `gh run list`) — before trusting a subagent's self-report or
   dispatching the next one. Treat "nothing was pushed/sent" as something to confirm, not assume.
5. **A good find outside scope is kept, not discarded** — but the action on it goes through the
   normal authorization flow, deliberately, by the orchestrator or a newly and explicitly
   authorized dispatch. Scope discipline governs who takes the action and when, never whether a
   real finding gets acted on eventually.

6. **The workspace is shared state too: check it after every dispatch** (Simplifii-OS, 26 Sep
   2026). Verifying pushes is not enough; subagents also changed local state nobody asked for:
   - One ran `git stash` / `git stash pop` to "mutation-check" a fix although the prompt said no
     stash. Name `git stash` explicitly ("not even temporarily") in the denial clause, and run
     `git stash list` after the dispatch.
   - One regenerated a baseline file (`UPDATE_A11Y_BASELINE=1` on a script that ignored its
     arguments) and had to restore it. After each dispatch, diff every generated or baseline file
     (`git status --porcelain`), not only the files in scope.
   - One left a test run alive in the background. Check for stray processes (`pgrep -fl
     "react-scripts test"`, load generators such as `yes`) before starting the next step.
7. **Do not commit while a subagent is editing files your pre-commit hook reads.** The hook runs
   the tool the subagent may be halfway through changing (here `scripts/check-style.js`), so the
   commit is judged by an unfinished script. Wait for the dispatch to finish, or commit only after
   verifying the tool is unchanged.
8. **A subagent's "root cause" is a claim.** Re-read the cited file:line before closing an issue
   on it (a "React warning in CourseCard" turned out to be a wrong-shaped test mock; the claim was
   right, and confirming it took two reads).

## Related

- `subagent-verification-protocol.md` — the companion post-hoc check: verify a subagent's
  self-report and scope after it returns, not just authorize it before dispatch.
- `implementer-neutral-handover-and-claude-feedback.md` — the sibling rule for durable handoffs
  when one agent hands direction to another rather than dispatching a subagent directly.
- AMLHive `docs/agent_rules/subagent-dispatch-authorization-boundary.md` — the fuller source
  version, with the full issue-371 incident writeup.
