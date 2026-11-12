# Search summaries are leads, fetch the source

A web search result summary is a pointer, not evidence. Before a claim from a search summary goes into a spec, a context page or an answer as fact, fetch the source page and read it, or mark the claim Not confirmed.

**Scope:** every agent doing vendor, standards, pricing or capability research.

## Why this exists

Added 12 Nov 2026 (Haris, POS terminal research). A search summary said a vendor's middleware supports plug-ins on the terminal and that terminal plug-ins are built only by the vendor. Fetching the vendor page showed neither sentence. Another agent's page had already marked the plug-in statement Confirmed from a source nobody could point to. The same search also returned a competing vendor's guide for a similar feature, which looked like an answer and was not.

## Core Directives

1. **Fetch before you state.** Open the cited page and quote the sentence (under 15 words, with attribution) or paraphrase it. If the page does not say it, the claim is Not confirmed.
2. **Say which it is.** Write "Confirmed (page, section)" or "Not confirmed (search summary only)". Never leave a bare claim.
3. **Another vendor's guide is not this vendor's behaviour.** Use it only as a hint for what to ask.
4. **A page that does not mention a feature is silence, not a no.** Record "not shown on the page", not "not supported".
5. **Check an existing "Confirmed" that has no visible source.** Ask who holds the source, or mark it unresolved and tell the owner.
6. **Date it.** Vendor pages change; record the date you read it.

## Patterns to Follow

- "Confirmed (vendor page, read 12 Nov 2026): supports three terminal ranges."
- "Not confirmed: terminal plug-ins are vendor-built. A search summary said so; the fetched page did not."

## Patterns to Avoid

- Copying a search summary sentence into a spec as fact.
- Treating a competitor's integration guide as proof of how this product behaves.
- Reading "not mentioned" as "not possible".

## Verification & Guardrails

- Every external-capability claim in a deliverable has a source URL and a status.
- Open questions list what to ask the vendor, in generic words, with no personal or project details.
