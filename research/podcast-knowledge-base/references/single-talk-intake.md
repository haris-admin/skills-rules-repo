# Filing a single talk across all three stores

For a one-off video the user hands over (masterclass, webinar, conference session, cohort call): fetch the
transcript, write an analysed brief, then land the same material in **Alexandria (vault), Notion, and
Honcho**. The three writes are independent, and a session is not done until each has been read back.

## 1. Fetch

```bash
python3 ~/.hermes/scripts/fetch_one_transcript.py --video <ID> --out ~/.hermes/cache/scratch/yt_<ID>.txt
```

Exit 3 (or 0 chars) is a BLOCK: stop and report it. Never file a thin transcript as a brief.

Metadata without yt-dlp: `https://www.youtube.com/oembed?url=<watch-url>` gives title + author; the watch
page HTML carries `uploadDate` in its JSON-LD. **A `publishDate` in US Pacific converts to the NEXT day
in AEDT** — convert before naming a file, and prefer the publish date over "the day I processed it" so a
backlog does not file everything under one date.

Unlisted videos cannot be enumerated from channel uploads, playlists or search — see the SKILL.md rule.
Do not burn turns hunting siblings; ask for the link.

## 2. Analyse a 100k-char transcript without reading it whole

Three cheap passes beat one long read:

1. **Term census** — `re.findall(term, txt, re.I)` over 15-20 candidate topic words, printed with counts.
   The counts tell you what the talk is actually about before you commit to a title.
2. **Even sampling** — slice at `len(txt)//9` and print ~600 chars at each of the 9 offsets. That recovers
   the arc (framing → list → Q&A) in one screen.
3. **Ordinal extraction** — when the speaker says they have N rules/principles/lessons, regex the ordinals
   (`number (one|two|…|ten|\d+)`) and print ~500 chars from each hit. This reconstructs the list in the
   speaker's own words; keep a seen-set because a speaker repeats "number one" when summarising.

**Expect a missing ordinal.** Auto-captions drop the marker when the speaker moves on conversationally
("moving on to the next one" between items 3 and 5). Recover the item from the segment between its
neighbours, then **state in the brief that the list follows spoken order** — never silently renumber to
make it tidy.

Captions carry no punctuation and no speaker attribution. Set the brief's confidence to medium, mark Q&A
attributions as approximate, and never quote a figure from the talk as our own research.

## 3. Vault (Alexandria)

One brief + one raw transcript + an index row:

```
vault/refined/<domain>/<series>/NN-<slug>-<YYYY-MM-DD>.md              # analysed
vault/refined/<domain>/<series>/NN-<slug>-<YYYY-MM-DD>.transcript.md   # raw: tier raw, confidence medium
vault/refined/<domain>/<series>/README.md                             # index table
```

Brief frontmatter: `id`, `title`, `tier` (`refined`|`raw`), `type` (`intel`|`reference`), `domain`,
`source` (the URL), `created`, `updated`, `status`, `confidence`, `owner`.

Body shape that has worked: **Framing** (how it relates to the previous session) → **the enumerated list
in the speaker's own order** → **panel/Q&A notes** → **Why this matters for us** → **Caveats**
(captions, unattributed quotes, claims not verified).

Commit with the vault convention, add the specific paths only (never `git add -A`), retry the push on
`ECHILD`/rejection, and verify with `ls-remote` — `rc: 0` is not proof on this host.

## 4. Notion

`~/.hermes/scripts/baa_masterclass_add.py --video <ID> --session <N> --title "<title>"` does transcript
plus child page in one command for the masterclass series (the parent id is defaulted in the script). For
anything else, create the child page from markdown and append the transcript as paragraph blocks in
batches; read the page back and count its blocks before claiming it landed.

## 5. Honcho

One dedicated session per talk, peers `pluto` + `haris`, metadata carrying `kind`, `program`,
`session_no`, `video_id`. Post the **brief as message 1** (Alexandria path in its metadata), then the
transcript in chunks. Limits and the verification loop live in `pluto-honcho-signal-bridge` under
"Writing a document INTO Honcho" — short version: 25,000 chars per message, ~23,000-char chunks, read the
messages back before reporting success.

Then trigger a dream (`observer`/`observed`/`dream_type`; shorthand field names are rejected) and read the
conclusions it returns. After two sessions of the same series it states the filing convention inductively,
which is the proof the material was absorbed rather than merely stored.

## Verification checklist

- [ ] `git ls-remote` == local HEAD for the vault commit; secret scan of the new files clean
- [ ] transcript char/word count stated in the brief and in the report
- [ ] Notion page read back, with its block count
- [ ] Honcho `messages/list` count and total chars match what was posted
- [ ] dream completed and its conclusions quoted, or an explicit "0 created"

## Pitfalls

- **Reporting "stored" off a successful POST.** Every one of these stores accepts a write it then drops
  (block caps, message caps, push lies). Read each one back.
- **Filing under the processing date.** A two-talk backlog collapses into one day and the series order is
  lost; use the publish date, converted from US Pacific to AEDT.
- **Naming files from a guessed title.** Take the title from oEmbed, then slug it.
- **Letting length stand in for quality.** Say the text is auto-captions and keep the raw file so any quote
  can be re-checked later — a brief whose quotes cannot be re-verified is not intelligence.
