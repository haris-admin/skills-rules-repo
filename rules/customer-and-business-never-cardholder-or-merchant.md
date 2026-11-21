# Customer and business, never cardholder or merchant

In prose, tickets, specs, emails and UI text, say "customer" for the person raising a dispute and "business" for the party disputed. Portals are the customer portal, business portal, admin portal and enterprise portal.

**Scope:** all agents writing for the HandleDispute owner.

---

## Core Directives

1. **Transform the old words silently**: the owner uses them by habit.
2. **Leave code identifiers, API paths, database names and spec names alone**: the API contract is frozen.
3. **Business roles are business owner, business manager and business employee (staff), and the business itself.** External parties of a business are backlog.
4. **Ask when a scenario is unclear** instead of guessing which word applies.

## Why this exists

**21 Nov 2026 (HandleDispute):** the owner stated the rule while specifying the portals ("we should not refer to the customer as a cardholder ... use the term business"), building on spec 96, which applied the wording to pages, emails, SMS and documents.
