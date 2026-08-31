---
name: deep-research
description: Conduct thorough multi-source research on a topic using web search, academic sources, and codebase exploration to produce a synthesised, citation-backed answer.
---

# Deep Research Skill

## When to use
Invoke when the user asks a question that requires:
- Exploring multiple sources beyond the local codebase.
- Comparing approaches, libraries, or architectural patterns.
- Investigating a bug or behaviour across documentation, issues, and forums.
- Building a literature review or evidence-backed recommendation.

## Workflow

1. **Clarify scope.** Confirm what the user wants to know and the desired depth (quick overview vs. exhaustive survey). Default to focused and actionable.
2. **Local first.** Search the codebase (Grep, Glob, Read) for existing implementations, comments, or prior art that relates to the question.
3. **Web search.** Use WebSearch to find authoritative sources — official docs, GitHub issues, Stack Overflow answers, academic papers. Prioritise primary sources over blog summaries.
4. **Fetch and verify.** Use WebFetch to read the most promising results. Cross-reference claims across at least two independent sources before reporting them as fact.
5. **Synthesise.** Combine findings into a structured Markdown answer:
   - **Summary** — one-paragraph answer to the question.
   - **Key findings** — bulleted evidence with inline source attribution.
   - **Recommendations** — actionable next steps tailored to this project.
   - **Sources** — numbered list of URLs consulted.
6. **Deliver.** Output the synthesis directly. If the user wants it saved, write to `docs/research/` following project file organisation rules.

## Constraints
- Never fabricate citations or URLs. If a source cannot be verified, say so.
- Respect the Burrito First rule: deliver the high-value insight, not an exhaustive dump.
- Flag when research is inconclusive or sources conflict — surface the gap rather than guessing.
- Keep research focused. If the scope balloons, check in with the user before continuing.
- Use Australian English in all output.
