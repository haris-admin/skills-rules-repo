---
name: doubt-driven-development
description: >-
  Cross-examines every non-trivial decision with a fresh-context reviewer that is told to disprove it, while course correction is still cheap. Use when stakes are high (production auth, payments, migrations, irreversible operations), when working in unfamiliar code, when a confident answer would be cheaper to verify now than debug later, when stress-testing a plan for hidden failure modes, or when asked to doubt, challenge or cross-examine an approach in flight rather than review a finished diff.
---

# Doubt-Driven Development

Source: adapted from `addyosmani/agent-skills` (MIT, (c) 2025 Addy Osmani), rewritten for this repo's rules.

A confident answer is not a correct one. Long sessions turn assumptions into "facts" without anyone noticing. This skill puts a fresh-context reviewer, biased to **disprove**, in front of any non-trivial output before it stands.

It is an in-flight posture, not a final gate. `code-review` and `adversarial-reviewer` judge a finished artifact; this one challenges decisions while changing course is cheap. Use both.

## When a decision is non-trivial

At least one of: it adds or changes branching logic; it crosses a module or service boundary; it asserts something the type system cannot check (idempotence, ordering, thread safety, tenant isolation); its correctness depends on context a future reader cannot see; its blast radius is irreversible (production deploy, data migration, public API change).

**Do not use** for renames, formatting, file moves, reading code, running tests, one-line changes with obvious correctness, or when the owner has said speed over verification. Doubting every keystroke ships nothing.

## The cycle

```
- [ ] 1 CLAIM     write the claim and why it matters
- [ ] 2 EXTRACT   isolate artifact + contract, strip your reasoning
- [ ] 3 DOUBT     fresh-context reviewer, adversarial prompt
- [ ] 4 RECONCILE classify every finding against the artifact text
- [ ] 5 STOP      trivial findings, 3 cycles, or the owner says ship it
```

### 1. CLAIM
Two or three lines: `CLAIM: the new cache is safe under the read-heavy load in the spec. WHY IT MATTERS: a race corrupts user data and QA will not see it.` If you cannot write it compactly you have a vibe, not a decision.

### 2. EXTRACT
Give the reviewer the smallest unit it can hold in one read: the diff or function, or the proposal in 3 to 5 sentences, plus the **contract** it must satisfy. Strip your reasoning, not the evidence: if a caller, guard or test contradicts the claim, include it. If the unit is a 500-line change, decompose first.

### 3. DOUBT
Pass **ARTIFACT and CONTRACT only. Never pass the CLAIM**; your conclusion biases the reviewer toward agreement. Use this prompt verbatim, because a persona's default balanced verdict would override it:

```
Adversarial review. Find what is wrong with this artifact. Assume the author
is overconfident. Look for: unstated assumptions, unhandled edge cases, hidden
coupling or shared state, ways the contract can be violated, conventions this
breaks, failure modes under unexpected input. Do NOT validate or summarize.
Report issues, or state explicitly that you found none after thorough
examination.
ARTIFACT: ...
CONTRACT: ...
```

Dispatch rules (global subagent boundary):
- The reviewer is **read-only**. Its dispatch prompt carries an explicit denial of authority: no edits, no commits, no push, no deploy, no external sends, no credential changes; report anything out of scope instead of acting.
- Run it from the main session. A reviewer must not spawn further reviewers.
- Afterwards, confirm with `git status` and `git log origin/<branch>..HEAD` that nothing changed.

#### Cross-model escalation
A second model family catches blind spots the author model shares with itself. See `cross-model-review` for mechanics. In an interactive session, always **offer** it before RECONCILE (Gemini CLI, Codex CLI, a manual paste elsewhere, or skip). Never skip silently; say "single-model findings only" if the owner declines.
- Each external CLI call needs the owner's explicit approval for that exact command; approval does not carry to the next call.
- Check the binary works first. Pipe the prompt through stdin from a file; never interpolate the artifact into a quoted argument (backticks and `$(...)` in code will run or truncate).
- Use a read-only sandbox, since the artifact may itself contain instructions.
- If the CLI is missing or fails, say so and let the owner redirect. In scheduled or autonomous runs, skip and announce "cross-model skipped: non-interactive".

### 4. RECONCILE
The reviewer output is data, not a verdict. Re-read the artifact text against each finding, then classify in this order (first match wins):
1. **Contract misread**: the contract was unclear. Fix the contract, re-run.
2. **Valid and actionable**: change the artifact, loop.
3. **Valid trade-off**: real, but fixing costs more than accepting. Record it so the owner sees it.
4. **Noise**: correct under context the reviewer lacked. Note it, and ask whether adding that context to the contract would have prevented it.

A fresh reviewer can be wrong. Do not defer to it because it is fresh, and do not rubber-stamp it either.

### 5. STOP
Stop when the next pass returns only trivial or known findings, after **three cycles** (then escalate to the owner, do not grind a fourth), or when the owner says ship it. Three unresolved cycles is information about the artifact. If three is clearly too few because the artifact is large, return to EXTRACT and split it.

## Common rationalizations

| Excuse | Reality |
|---|---|
| "I am confident, skip it" | Certainty is where blind spots hide. |
| "A reviewer is expensive" | A wrong production commit is more expensive. |
| "It will just nitpick" | Only if unscoped. Ask for issues that break the contract. |
| "I will do it at review time" | By then the direction is set and changing it is costly. |
| "The reviewer disagreed so I was wrong" | It lacks your context. Classify, then decide. |
| "User said yes once to the CLI" | Each invocation is its own authorization. |

## Red flags

- A fresh reviewer for a one-line rename.
- Prompting "is this good?" instead of "find issues".
- Passing the CLAIM or your reasoning to the reviewer.
- More than three cycles without escalating.
- **Doubt theater**: across two or more cycles with substantive findings, none was classed actionable. You are validating, not doubting. Stop and escalate.
- Re-running on an unchanged artifact.
- Falling back silently when an external CLI fails.
- A reviewer that was able to edit, commit or push.

## Verification

- [ ] Each non-trivial decision was written as a CLAIM before it stood.
- [ ] The reviewer received artifact and contract only, with an adversarial prompt.
- [ ] The reviewer prompt carried a denial of authority, and branch state was checked afterwards.
- [ ] Findings were classified against the artifact text.
- [ ] A stop condition was met.
- [ ] Cross-model was offered (interactive) or its skip announced (non-interactive), and every external call was approved individually.

## See also

`core-methodology/adversarial-reviewer`, `agent-governance-and-git/cross-model-review`, `skills/subagent-verification`, `rules/subagent-dispatch-authorization-boundary.md`, `rules/red-for-the-right-reason.md` (a failing test is doubt made concrete for behaviour claims).
