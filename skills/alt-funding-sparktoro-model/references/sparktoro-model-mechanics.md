# SparkToro's funding model — mechanics

Source: Rand Fishkin, ["SparkToro Raised a Very Unusual Round of Funding & We're Open-Sourcing Our Docs"](https://sparktoro.com/blog/raised-a-very-unusual-round-of-funding-were-open-sourcing-our-docs/) (2018) and the [Year 3 retrospective](https://sparktoro.com/blog/sparktoro-year-3-retrospective-investor-payback-systemic-challenges-and-v2-on-the-way/). Verify current numbers by re-fetching if it matters to a decision — this is a 2018 raise, not a live term sheet.

## Entity & instrument

- **LLC, not a C-corp.** The LLC structure is what makes profit distribution (dividends to unit-holders) possible on a schedule the founders control — a C-corp/VC preferred-stock stack is built around a priced equity exit, not periodic profit share.
- Investors bought **Class A Units** — not preferred stock, not a SAFE, not a revenue-share note. A unit is a slice of the LLC's economics and (limited) governance, not a claim that converts at a future priced round.

## Money flow, in order

1. Company is profitable in a given year → board/founders can choose to **distribute profits pro rata** to unit-holders, or reinvest in growth. This is a *choice*, not an automatic waterfall — the LLC isn't obligated to distribute just because it's profitable.
2. **Investors get paid back first.** 100% of invested capital ($1.3M in SparkToro's case) must be returned via profit distributions *before founders receive any distribution themselves*.
3. After investor payback, distributions (if the company keeps choosing to make them) flow pro rata to **everyone** holding units — investors, founders, and (per the blog) employees who hold units.
4. **Exit/acquisition carve-out:** if the company is sold, investors get the *greater of* (a) their capital back minus whatever they've already recouped via distributions, or (b) their pro-rata percentage of the sale proceeds. This protects investors from a low-multiple/quick-flip exit that would shortchange a pure capital-return structure.

## Governance

- No board seat requirement, no information-rights covenants mentioned in the public docs.
- **Structural changes need 80%+ of units to approve.** That's the main investor protection — a supermajority veto over changes to the deal, not day-to-day control.
- **Pro-rata rights** in future rounds — investors can maintain their ownership percentage if the company raises again.

## Deal size and process (SparkToro's actual raise)

- Target $1.25M, closed at $1.3M from 35 accredited investors.
- Checks ranged $10K–$100K.
- ~90 days from first outreach to closing, ~75% close rate on the ~47 investor conversations they had.
- No priced valuation was set — because there's no equity percentage being priced, there's no cap-table math to negotiate the way there is in a SAFE/priced round.

## Why founders chose this over VC

Fishkin's stated reasoning (paraphrased from the post):

- Traditional VC preferred stock is underwritten to a "multi-hundred-million-or-billion-dollar outcome." A profitable business doing a few million to tens of millions in revenue is a *failure* by VC-fund-return math, even though it's a success for founders, employees, and a lower-risk investor.
- VC structure gives investors no upside from dividends/profit-share — their only return path is a priced-up round or acquisition, which pressures the company toward growth-at-all-costs and forecloses "stay independent and profitable" as a legitimate outcome.
- The LLC/profit-share structure makes a mid-range outcome (profitable, sustainable, no forced exit) a *good* outcome for investors too, because they get paid via dividends over time instead of needing a markup event.

## What this model explicitly is not

- Not a SAFE or convertible note (no conversion into future-round equity).
- Not revenue-based financing / a revenue-share loan (no fixed repayment cap as a multiple of revenue; distributions are discretionary and tied to *profit*, not top-line revenue).
- Not preferred stock (no liquidation preference stack, no anti-dilution ratchets, no board-seat/veto rights beyond the 80% supermajority on structural change).

## Track record signal (not a guarantee)

SparkToro's Year 3 retrospective reports they returned 100% of investor capital via profit distributions — offered by Fishkin as proof the model can work, not as evidence it will work for any given business. Cite this as "one company's result," not as a base rate.

## Open-source docs

Fishkin published the actual Unit Purchase Agreement and related docs (numbers redacted) for reuse. If a real raise under this model is pursued, start from those primary documents (link in the blog post above) rather than reconstructing them from this summary — this file is a briefing, not a legal source.
