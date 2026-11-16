# Whether a document is stale is decided by version control, not by how sure it sounds

When code and the document that describes it may have drifted apart, compare their commit history before trusting or editing the document. Applies to every agent reading or correcting a README, runbook, spec, design note or handoff file.

## Why this exists

Added 16 Nov 2026 from the review of `addyosmani/agent-skills` (`documentation-and-adrs`, MIT). A document that was true when written keeps reading as authoritative after the code moves on. This repo already requires fresh independent reads for deploy state (`deploy-state-needs-independent-reads.md`) and treats ticked tasks as claims (`ticked-tasks-are-claims-verify-before-trusting.md`). This rule applies the same discipline to prose documents.

## Rules

1. Before relying on a document about a piece of code, compare the last commit that touched the code with the last commit that touched the document:
   ```bash
   code=$(git log -1 --format=%H -- path/to/code)
   doc=$(git log -1 --format=%H -- path/to/doc.md)
   if [ "$code" = "$doc" ]; then echo "current: changed together"
   elif git merge-base --is-ancestor "$doc" "$code"; then echo "stale: code changed after the doc"
   elif git merge-base --is-ancestor "$code" "$doc"; then echo "current: doc changed after the code"
   else echo "cannot tell"; fi
   ```
2. If the history is unordered (divergent branches, a rebase, a shallow clone, a squash that rewrote both), the answer is **cannot tell**. Say that. Never report it as current.
3. A document the code has outrun is a lead, not evidence. Read the code, then say which statements you confirmed.
4. When you correct a document that has a change log, append a dated entry saying why it changed. Never rewrite or collapse earlier entries: git keeps the old text, but the log is the only record of the reasons.
5. When you correct a document, restore any qualifier or caveat the edit would lose, and check that every command and path it names still works.
6. Documentation describes the current state in timeless language. Put change history in the changelog or the commit, not in the body of the document.

## How to apply

Run the comparison when a handoff note, runbook or spec is about to drive an action, and quote the result (current, stale or cannot tell) next to your claim. For a project that wants a standing guard, add the same comparison to a CI check over the documents that name specific source paths.
