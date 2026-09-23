# Filing a Notion meeting memo into the vault

Use when the owner says a Notion page (meeting memo, call notes, transcript) should be filed into
Alexandria — "pick up what Notion has updated", "add this to the memos and to Alexandria".

## 1. Read the page

- Auth: the **workspace** token from `/mnt/c/Users/habib/.hermes/.env` (`NOTION_TOKEN_WS`, integration
  "My-Token1"). The default `NOTION_TOKEN` integration may not be shared with the page. Header
  `Notion-Version: 2025-09-03`.
- Resolve the page id with `POST /v1/search {"query": "<name>"}`. A meeting memo is usually a CHILD
  PAGE of the venture page — walk `parent` up until `type: workspace` to confirm you have the right
  memo and to learn which venture owns it.
- Content: `GET /v1/pages/{id}/markdown` (agent-friendly markdown; returns the whole page including
  any transcript). Metadata: `GET /v1/pages/{id}` — `last_edited_time` tells you whether the owner
  just updated it.
- Write the markdown to a scratch file and process it there. Memos carrying a full transcript run
  50-100KB; never paste one into the session transcript.

## 2. Normalise the markdown before extracting anything

`GET .../markdown` is a lossy rendering:

- `<br>` is an intra-line separator, not a newline. Replace it with `\n` or the entire memo arrives
  as one unreadable line.
- Strip `<empty-block/>` placeholders.
- Unescape backslash-escaped punctuation (`\$`, `\~`).
- Collapse runs of 3+ blank lines.

## 3. Extract sections by STRUCTURE, then assert the length

**Pitfall (costs a whole write if missed):** a Notion memo page routinely holds the SAME content
twice — an abridged notetaker transcript AND the full verbatim block. A boundary match of the form
`next(line for line in lines if "<phrase>" in line)` therefore hits the FIRST occurrence and slices
the wrong range (observed: the intended digest range came out at 0 characters while the code looked
correct).

- Locate boundaries by section markers (`Summary:`, `Action Items:`, `### <section>`, the block that
  opens the verbatim transcript) — never by a phrase that can appear anywhere in the page.
- **Print the extracted character count plus a head sample before writing anything.** A 0-or-tiny
  extraction is a boundary bug, not an empty memo. Fix the range; never write an empty or truncated
  note (same failure class as the 0-byte `write_text` truncation pitfall in SKILL.md).

## 4. File the set

Under `vault/refined/<topic-or-venture>/`:

- the **digest** note — outcome at a glance, decisions, action items, the substantive feedback or
  facts, with a provenance header (source page title + URL, `last_edited`, transcription method) and
  a pointer to the transcript file;
- the **transcript** as a separate companion file, stamped machine-generated and
  "as-heard — names, figures and terminology unverified";
- update the folder `README.md` index: status, dated milestones, `Contents` list, next steps (tick
  off the preparation items the call completed).

Frontmatter per the tier/frontmatter contract (`tier: refined`, `type: intel|log`, `domain: [...]`,
`source:`, `created:`, `updated:`). Run `date` first — see the dated-artifacts section of SKILL.md.

## 5. Reconcile the owner's own capture against the source

The owner often dictates their own read of the meeting (a voice note) in the same request. Dictated
numbers arrive garbled by speech-to-text (a price becomes unrelated digits, a percentage drifts).
**Verify every number against the transcript/source and file the verified figure, labelled so the
reconciliation is visible** — never transcribe a dictated figure straight into the record. Anything
the source does not support stays labelled unverified.

## 6. Optional: write the capture back to the source page

`PATCH /v1/blocks/{page_id}/children` appends blocks (a divider + a headed "owner summary" block
plus a few bullets is enough).

**Read-back trap:** appended blocks land at the END of the page, so
`GET /v1/blocks/{page_id}/children?page_size=100` returns the FIRST 100 blocks with
`has_more: true` — your new blocks are absent from that response and a naive check reads it as "the
append failed". Follow `next_cursor` until `has_more` is false and confirm the new heading in the true
tail before reporting success. Same rule as `push rc: 0` being no proof a push landed.

## 7. Land it

Behind-check first, scoped `git add` of the folder only, secret scan, Windows-safe ASCII filenames,
commit, push, then prove HEAD == `origin/main`. See SKILL.md for the push-verification and
second-writer rules.
