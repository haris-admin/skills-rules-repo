# ADS Component Catalog

Reference for `atlassian-design-system`. Source: <https://atlassian.design/components>.
Status markers (Beta / Early access / Caution / Deprecated) are as published at review time —
**re-check before adopting**, especially for anything marked Beta or Caution.

## Forms and inputs
Button · Calendar · Checkbox · Comment · Date time picker · Dropdown menu · Focus ring · Form · Radio ·
Range · Select · Text area · Text field · Toggle

## Images and icons
Avatar · Avatar group · Icon *(Beta)* · Image *(Beta)* · Logo · Object · Tile

## Labels
Badge · Date label · **Lozenge** · Tag · Tag group

> **Lozenge** is Atlassian's status pill. It is *not* a "badge" — `Badge` is a numeric tally.
> Getting this vocabulary right is most of the value of matching their names.

## Layout and structure
Page *(Caution)* · Page header · Panel *(Beta)*

## Loading
Progress bar · Skeleton *(Early access)* · Spinner

## Messaging
Banner · Empty state · Flag · Inline message · Modal dialog · Spotlight · Section message

> The messaging set is a decision tree, and using the wrong one is the most common ADS mistake:
> - **Banner** — prominent, page/top-level message
> - **Section message** — alerts to a *section* of the screen
> - **Inline message** — important info / action required, inline
> - **Flag** — confirmations and acknowledgments, minimal interaction, usually in a flag group
> - **Empty state** — no data yet, and what to do next
> - **Spotlight** — focus attention on a specific element to educate (onboarding)
> - **Modal dialog** — requires interaction, layered above the page

## Navigation
Breadcrumbs · Link · Menu · Navigation system · Pagination · Tabs

## Overlays and layering
Blanket · Drawer · Inline dialog *(Caution)* · Popup · Tooltip

## Status indicators
Progress indicator · Progress tracker

## Text and data display
Code · **Dynamic table** · Heading *(Beta)* · **Inline edit** · Table *(Caution)* · Table tree ·
Visually hidden

> `Dynamic table` (built-in pagination, sorting, re-ordering) is the default for data grids;
> plain `Table` carries a Caution and should be a deliberate choice. `Visually hidden` is the correct
> way to keep text available to screen readers while removing it visually — not `display:none`.

## Primitives
Box · Pressable · Anchor · Inline · Stack · Flex *(Beta)* · Grid *(Beta)* · Bleed · **XCSS**
*(Caution)* · Responsive · Text *(Beta)* · MetricText *(Beta)* · Focusable

> **Primitives are the answer to "the component doesn't do exactly what I need."** Compose
> (`Box` + `Inline`/`Stack` + `Text`) rather than forking a component — you keep token access and
> focus/layout correctness. `XCSS` is the tokens-first CSS-in-JS escape hatch; `Focusable` gives a
> focus ring without re-implementing it.

## Libraries
CSS *(Beta)* · CSS reset · Design tokens · Motion · Popper · Portal · Pragmatic drag and drop

## Tooling
App provider *(Beta)* · ESLint plugin · Storybook addon · Stylelint plugin · UI Styling Standard

> The tooling is what turns the standards into automation. Wire the ESLint + Stylelint plugins into
> CI or the rules remain documentation nobody enforces.

## Deprecated — do not use for new work
Atlassian navigation · Layout grid · Onboarding (spotlight) · Page layout · Side navigation

## Page index
<https://atlassian.design/components> · Tokens library
<https://atlassian.design/components/tokens/all-tokens>
