# Structuring a SparkToro-style raise under Australian law — orientation notes

**This file is not legal advice and must not be treated as a substitute for a licensed Australian
corporate/securities lawyer.** Its job is to brief Claude on where the US mechanics in
`sparktoro-model-mechanics.md` don't transplant cleanly, so a fit memo or term sheet outline
flags the right open questions instead of silently assuming US structure works unchanged. Any
real raise needs professional sign-off before a single dollar moves.

## There is no direct Australian equivalent of a US pass-through LLC

SparkToro's model leans on the LLC's ability to distribute profits to unit-holders without
entity-level tax first. Australia has two structures that each capture *part* of that, with a
real trade-off between them:

| | **Pty Ltd (company) + bespoke share class** | **Unit trust** |
|---|---|---|
| Tax | Company tax (25% base-rate-entity threshold, verify current ATO rate) paid first; dividends can carry **franking credits**, so AU-resident holders get an offset — softer than raw double tax, but non-resident investors don't benefit from franking. | Distributions flow through to unit-holders and are taxed at their marginal rate — closer to the LLC's pass-through economics SparkToro actually used. |
| Regulatory | Standard startup vehicle; offering shares is a Ch 6D "securities" offer. | Offering units broadly can be caught as a **managed investment scheme (MIS)** under Ch 5C — a materially heavier regime (potential AFSL/responsible-entity requirement) unless a wholesale-only or other exemption clearly applies. |
| Familiarity | What every AU startup lawyer, ASIC form, and cap-table tool already assumes. | Less common for an operating tech company; more legal novelty = more legal cost and more ways to get it wrong. |

**Working default:** lean toward a Pty Ltd with a bespoke share class or a shareholders'-agreement
side-deed carrying the profit-share mechanics, rather than a trust — the MIS/AFSL trap on the
trust side is a real regulatory risk, not just a technicality, and most of what makes SparkToro's
model attractive (capital-back-first waterfall, discretionary distributions, no forced exit) can
be replicated inside ordinary share rights + a shareholders' agreement without needing a trust at
all. Confirm this default with a lawyer rather than treating it as settled — it depends on investor
count, residency mix, and how much tax pass-through actually matters to the specific raise.

## Fundraising-exemption reality check

Any offer of securities to Australian investors generally needs a disclosure document (prospectus)
under Ch 6D **unless an exemption applies**. The two exemptions that matter here:

- **Sophisticated/wholesale investor exemption (s708(8)):** investor needs net assets ≥$2.5M or
  gross income ≥$250K/yr for the last two years, **certified by a qualified accountant** — this
  certificate requirement is real friction vs. the US accredited-investor self-certification
  SparkToro relied on. Budget time for it in any close-rate/timeline estimate.
- **Small-scale personal offer exemption (s708(1)):** ≤20 investors and ≤$2M raised in any rolling
  12-month period, offers made personally (not broad solicitation). SparkToro's 35-investor/$1.3M
  raise would **not** fit this cap as-is — a same-shape AU raise either needs to stay under 20
  investors, spread across >12 months, or lean on the wholesale exemption instead.

Flag this explicitly in any fit memo for an AU venture: the investor-count and check-size
assumptions from the SparkToro playbook may need to shrink or restructure to fit an available
exemption, and that's a legal-scoping question, not a commercial preference.

## Tax framing to hand to an advisor, not to decide unassisted

- Company route: entity-level tax now, franking credits later — most tax-efficient for AU-resident
  individual investors, weaker for foreign investors or entities that can't use imputation credits.
- Trust route: no entity-level tax if fully distributed, but carries the MIS exposure above and is
  less familiar to most cap-table/legal tooling.
- Get actual advice on which fits the venture's likely investor mix (resident individuals vs.
  funds vs. offshore angels) before picking — don't default silently to one path in a term sheet
  outline without naming this as an open decision.

## What still transplants cleanly

The *economic* mechanics from `sparktoro-model-mechanics.md` are jurisdiction-agnostic contract
terms and can generally be drafted into an AU shareholders' agreement or unit-holders' agreement
largely as-is, once the entity choice above is settled:

- Capital-back-first waterfall before founder distributions.
- Discretionary (not automatic) distribution of profits, decided year to year.
- Greater-of protection on acquisition (capital-back vs. pro-rata share of proceeds).
- 80%+ supermajority vote to change the structure.
- Pro-rata participation rights in future rounds.

Treat those five terms as the reusable core of the model regardless of jurisdiction; treat the
entity choice and exemption pathway as the AU-specific redesign work.
