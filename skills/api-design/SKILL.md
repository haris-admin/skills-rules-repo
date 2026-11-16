---
name: api-design
description: >-
  Designs and evolves stable APIs and module boundaries: REST, OpenAPI, GraphQL schemas, RPC interfaces and typed contracts between modules. Use when creating, refactoring or documenting an API, defining the contract between frontend and backend, adding fields or routes to an existing endpoint, choosing error semantics, pagination, idempotency or versioning, or deciding whether a change to a public interface is safe.
---

# API Design

Source: Hyrum's Law, one-version rule and addition-over-modification guidance adapted from `addyosmani/agent-skills` `api-and-interface-design` (MIT, (c) 2025 Addy Osmani), merged with this repo's earlier standards and rules.

**An existing route's status codes and response fields are frozen unless the owner approves a change** (`rules/api-contract-frozen-unless-approved.md`). Message text, logging and documentation may change. If a fix seems to need a status or field change, propose it with the clients affected and wait. Pin the current status in a test before touching the message.

## Principles

### Hyrum's Law
With enough users, every observable behaviour gets depended on, including error text, ordering and timing, whatever the contract says. So: expose only what you intend to commit to, do not leak implementation detail, and plan for removal at design time (see `deprecation-and-migration`). Contract tests do not catch undocumented dependence.

### One version
Avoid making consumers choose between versions of the same thing. Prefer evolving one contract by addition over forking a v2 that both must support.

### Contract first
Write the interface (OpenAPI, GraphQL schema or types) before the implementation, review it, then build against it. Generate or update the spec in the same change as the code.

### Prefer addition over modification
Add optional fields. Do not remove a field, change a type, tighten validation on existing input, or reorder semantics for existing callers. Optional-new, never required-new, on an existing route. Optional reporting fields on a critical endpoint are parsed leniently (`rules/optional-reporting-fields-on-a-critical-endpoint-are-parsed-leniently.md`).

### Validate at the boundary
Validate and type every external input where it enters, before it reaches the database or a third party. Inside the boundary, trust the types.

## Workflow

1. **Model resources.** Plural nouns (`/users`, `/orders/{id}/items`). Standard verbs: `GET` safe and idempotent, `POST` create, `PUT` full replace, `PATCH` partial, `DELETE` remove. Predictable, consistent naming and one casing convention across payloads.
2. **Design requests and responses.** One error envelope everywhere:
   ```json
   {"error": {"code": "RESOURCE_NOT_FOUND", "message": "User 123 does not exist", "details": []}}
   ```
   Use cursor or limit-offset pagination on every collection, and filtering by query parameter. Status codes per [the guide](./references/rest-guidelines.md).
3. **Idempotency and versioning.** Mutating financial or critical operations accept an `Idempotency-Key`; a replay with the same key returns the original result and never repeats the effect. Version by path (`/api/v1/`) or header, and only for a genuinely breaking change the owner approved.
4. **Specify.** Produce or update the OpenAPI 3 document or GraphQL schema.
5. **Errors and secrets.** Provider errors: pass the detail through on the admin side, return a generic message on the user side, and log the provider body for engineers (`rules/provider-errors-admin-detail-user-generic.md`). Never echo secrets or internal paths in an error.

## Typed interface patterns (TypeScript and Python alike)

- Use **discriminated unions** for variants instead of boolean flags plus optional fields.
- Separate **input** and **output** types; do not reuse the persisted model as the request body.
- Use **branded or newtype IDs** so a user ID cannot be passed where an order ID is expected.
- Identifiers are stored columns from the system's own sequences, never derived from display values (`rules/identifiers-are-stored-columns-from-own-sequences.md`).

## Common rationalizations

| Excuse | Reality |
|---|---|
| "It is internal, so the contract can change" | Internal consumers depend on behaviour too (Hyrum). |
| "Just change the status code, it is more correct" | Frozen unless approved. Propose it. |
| "We will document it after" | The spec is the contract. Write it first. |
| "Add a required field, clients will update" | That breaks every client that has not. Add it optional. |
| "A retry is harmless" | Without an idempotency key a retry repeats the charge. |

## Red flags

- A status code or response field changed as a side effect of a fix.
- A test that asserts message text only.
- Collection endpoints with no pagination.
- Different error shapes across routes.
- A persisted model returned directly as the response.
- A version bump to avoid thinking about compatibility.

## Verification

- [ ] The contract (OpenAPI or schema) exists and matches the code.
- [ ] No existing status code or field changed without owner approval; tests pin the existing ones.
- [ ] New fields on existing routes are optional.
- [ ] Inputs are validated at the boundary; errors use one envelope.
- [ ] Mutating critical operations are idempotent.
- [ ] Error detail follows the admin and user rule.

## Reference

- [RESTful Best Practices & Status Code Guide](./references/rest-guidelines.md)
- Related: `deprecation-and-migration`, `api-endpoints`, `rules/backend-python-fastapi.md`
