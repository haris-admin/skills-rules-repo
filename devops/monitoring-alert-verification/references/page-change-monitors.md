# Page-change monitors

For watching an external page that changes **in place** — a regulator's guidance page, a
competitor's pricing page, a vendor's docs — where there is no feed, no changelog and no API. The
only signal is a diff of what the page says today against what it said last time.

## 1. A 200 is not a capture

Assert the capture is **substantive** before storing it as a baseline: check for the tokens you are
actually watching (the price values, the table rows, a known sentence). A response that is 200 and
a few kilobytes is a shell — an empty baseline makes every later diff meaningless, and it fails
*silently* because the monitor still looks healthy.

Two capture paths, and the choice matters more than the parsing:

- A plain HTTP fetch returns only server-rendered HTML. Pages built as client-side apps return a
  shell with **no content in it** — the numbers are fetched and rendered by JavaScript. If the
  extraction is empty or far too small, that is the diagnosis, not a parsing bug.
- The rendering extraction path (whatever the environment exposes for it) returns the rendered text
  and works on those pages. When both are available, save the curl output for a byte-level diff and
  the rendered text for the value-level diff.

## 2. The determinism contract for diff-gated monitors

Stdout is hashed as exact bytes by the gate, so **the output must be a function of the page alone**.

Emit, in a fixed order:

- the source URL and HTTP status;
- the page's own as-of/updated date if it carries one (this is the best human-readable signal that
the content is stale or fresh);
- the watched values — table rows sorted, key numbers, section headings in document order;
- the obligation-bearing sentences (filter your domain's keywords), normalised and deduped in order;
- a content hash of the normalised visible text, truncated for readability.

Never emit: timestamps, durations, run counters, hostnames, "now", or anything derived from a set's
iteration order. Never end with a trailing newline (`sys.stdout.write`), because a stored baseline
that was stripped will then differ from every subsequent run and fire the gate every tick.

## 3. Baseline discipline

- Keep **two** artefacts: the raw capture (provenance, byte-level diffs) and a **structured baseline**
  of the watched values (JSON keyed by what it is, with the capture date and the capture method
  recorded). A future change is then a value diff — "medium plan moved 1500 → 1650" — instead of a
  text diff nobody can read.
- Store the baseline where the monitor and any later analysis both look, and name the file by subject,
  not by date, so successive captures overwrite the value snapshot rather than accumulating.
- Where the question is "how has this changed over time?", a dated rendered snapshot per capture is
  what makes history diffable; do not depend on a third-party archive service being writable.

## 4. The waking prompt

The agent only runs when the page changed, and it has one job: decide whether the change is
substantive and what it means.

- Require it to **verify the change against the live page** — the diff is the trigger, not the
  evidence.
- Force a classification: numbers refresh / clarification / new obligation / scope change /
  reorganisation. Forbid inflating a numbers refresh into a rule change, and forbid softening an
  obligation change into "a refresh". If it cannot tell, it must say so.
- Require the quoted wording or the exact values as evidence, and the page's own as-of date.
- Give it an explicit escape hatch for churn the gate cannot filter (navigation, footer, dates,
  analytics links): answer with the platform's suppress token and nothing else.
- State that a fetch/parse failure is itself the finding, and that the baseline may be stale.

## 5. Verification before you trust it

1. `cmp -s` two consecutive runs of the source — must be identical.
2. Compare the gate's stored baseline hash with a fresh run of the source — must match.
3. Trigger one real tick and confirm the engine reports the change-gate suppressed the agent run
   (`no_change`), then read the job's output file to confirm nothing was delivered on a quiet tick.
4. Break it on purpose once: point the source at a URL that fails and confirm the output changes and
   the agent wakes. A monitor whose failure looks exactly like its silence is untested.
