# Agent-ready ticket template

Copy this whole template into the ticket description. Replace every angle bracket. Write "None" where a section does not apply. Do not delete sections.

```
TITLE: [ID] <short plain title in sentence case>
STATE: Todo      LABELS: agent-ready, tier-<small|medium|large>, <type>, <NFR label if any>
PRIORITY: <urgent|high|medium|low>      ASSIGNEE: <agent or person>      ESTIMATE: <steps and files count>

1. WHY (two to four sentences)
   <The problem in plain words, who is affected, what goes wrong today. No jargon without a definition.>
   Owner's words (verbatim): "<quote>"        Source: <link or file path and date>
   Terms used here: <term> = <one-line meaning>; <term> = <one-line meaning>

2. DONE MEANS (acceptance criteria, numbered, each testable)
   AC1. <Observable outcome with numbers, for example "at 320, 360, 390 and 768 px every highlight is fully inside the viewport">
   AC2. <Negative case: what must NOT happen>
   AC3. <...>

3. TRACE
   Origin spec: <openspec/changes/NN-slug>        Amendment id: <NNx>        Requirement ids: <R1, R2>        Task ids: <TNNx.01 ...>

4. SCOPE
   In scope: <bullet list>
   Out of scope (do not touch): <bullet list, include files and behaviours>
   Files you may change (complete list):
     - <path>  (create|edit)  <one line why>
   Files you must not touch: <list>, plus every file not listed above.

5. BEFORE YOU START (preflight, run these and compare)
   - <command>   expected: <exact output or exit code>
   - Branch: work on <dev or a worktree path>; base commit <hash>. Check: `git rev-parse --short HEAD` expected <hash>.
   - Environment: <how to start the dependencies, with the safe local-env script, never against production>

6. STEPS (do them in this order; one action each)
   Step 1 (test first, RED): create <test file path> with these tests:
       <test name> : <given fixture values> / <when> / <then exact assertion>
       <test name> : <negative case>
     Run: <exact command that runs only these tests>
     It must FAIL with: <the expected failure message or reason>. If it fails for any other reason (import error, crash, connection), stop and fix
     the test setup, because that is not the right red.
   Step 2 (GREEN): in <file>, find <function or section> (locate with: <grep -n command>). Change exactly this:
       BEFORE:
         <exact current text>
       AFTER:
         <exact new text>
     Run: <the same command>. Expected: <N passed>.
   Step 3 (related suite): run <command>. Expected: <summary>. Read the log summary line and the exit code, not a background notification.
   Step 4 (gates): run each and expect exit 0:
         <format check command>   <lint command>   <type check command>   <security scan if backend>   <contract guard / snapshot checks if relevant>
   Step 5 (visual or runtime check, if UI or API): <exact URL, viewport widths, what must be visible, how to capture the screenshot>
   Step 6 (record): update <tasks.md ticks> only after the evidence exists; update <docs to sync>; add the evidence comment to this ticket.
   Step 7 (commit locally): `git add <exact paths>` then `git commit -m "<type>(<scope>): <message> (<spec id>)"`. Then run `git show --stat HEAD`
     and `git log --oneline -3`. Do not push.

7. CONSTRAINTS (prohibitions with reasons)
   - Do not change any route's status code or response field (the API contract is frozen; ask the owner).
   - Do not hardcode a value a person might change (admin-managed or configurable with a documented default).
   - Never print or log a secret, token or part of one.
   - <any ticket-specific prohibition>

8. DENIAL OF AUTHORITY
   You may not: git push, merge into any other branch, deploy, run any workflow, send any email, SMS or message, call a live provider, rotate or print a
   secret, delete data or files, edit a test to make it pass, or touch files outside section 4. Silence in this ticket is a denial. If you find anything
   useful outside this scope, write it as a comment on this ticket and stop on that item.

9. STOP AND ASK (comment on this ticket and wait) IF
   - a test fails and the requirement seems to disagree with the test;
   - the change would need a different status code, response field or database schema than section 6 states;
   - a file outside section 4 must change;
   - a command's output differs from the expected output in this ticket;
   - you cannot make a step succeed after two honest attempts.

10. EVIDENCE TO ATTACH WHEN DONE
   - Output summary lines and exit codes of every command in steps 1 to 5 (no secrets).
   - Commit hash and `git show --stat HEAD` output.
   - Screenshots or response samples named in step 5.
   - A note of anything you did not verify.
   Another agent or the owner checks this. "Done" is not accepted without it.

11. ROLLBACK
   <exact commands or "git revert <hash>" and what to re-run to confirm the previous behaviour>

12. DEPENDENCIES AND ORDER
   Blocked by: <ticket ids or None>      Unblocks: <ticket ids>      Release note needed: <yes or no>      Version bump: <rule or None>
```
