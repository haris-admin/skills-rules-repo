# Every public page shares one header and footer, and each audience has its own page (all agents, all web repos)

Applies when an agent adds or changes a page of a public website that has more than one audience (customer, business, enterprise).

## Why this exists
**15 Nov 2026, HandleDispute (OpenSpecs 60a, 78, ADR-011):** the footer was written inside the home page, so the separate cardholder page had none while the merchant tab (inside the home page) did. The owner: "we need to keep a consistent experience ... why don't we have it for the merchant and others?"

## Rules
1. Shared chrome (header, footer, legal links, contact address) is one component used by every page. Do not write it inline in a page.
2. Give each audience its own route with the same shell, rather than hiding one behind a tab on the home page. Keep old links working: forward the old URL to the new page and carry its query values (tokens and references in emails already sent).
3. A standalone page's footer items are links to the home page view; on the home page they switch the view in place.
4. Test each page for the footer landmark, the contact address and the navigation targets; when a requirement changes a target, change the test and the spec together and record the owner's words.
5. Check a real browser after release: footer present, old link forwards, sign-in fields show. A static export needs the host to serve `/name` from `name.html`.
6. An audience with no content yet (enterprise) is a draft spec with the owner's open decisions, not an empty page.
