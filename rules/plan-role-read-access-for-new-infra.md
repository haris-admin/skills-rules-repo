# Plan Role Read Access for New Infrastructure

A new cloud resource ships the read access its read-only plan or drift role needs in the same change, so the drift check can finish its plan.

<!-- IMPORTANT: Do NOT include YAML frontmatter (---) in rules/*.md. Rules must begin with an H1 title on line 1. -->

**Scope:** All agents changing Terraform or other infrastructure-as-code that a read-only CI role plans against (a scheduled drift check, a PR plan).

---

## Core Directives

1. **Ship the plan role's read grant with the resource.** A new KMS key, alias, secret or data source needs its read action on its exact ARN added to the read-only plan role in the same change.
2. **A drift check that exits with a plan error is blind, not green.** Exit 1 (plan failed) is different from exit 2 (drift found). Before calling an infra change done, run the drift workflow by hand and require exit 0 or 2, never 1.
3. **Fix a denied read with the exact action on the exact resource from the error text.** Never widen the role or loosen a condition to make an error go away. Some actions (for example `kms:ListAliases`) require `*` as the resource; grant only that action.
4. **Page on a red drift run.** A weekly check that fails for weeks with no one paged is itself an incident; a failing or blind detector must be visible.

---

## Patterns to Follow

- Add the read grant and the resource in one reviewed plan, with the full untargeted plan read first.
- After the apply, dispatch the drift workflow and record its exit code.

## Patterns to Avoid

- Applying a new resource and relying on the next weekly run to find the missing grant.
- Treating "the workflow is red every week" as background noise.

---

## Verification & Guardrails

- The completion note records the drift workflow's run id and exit code after the apply.
- Related: `rules/terraform-prod-apply-safety.md`, `rules/iam-condition-drift-when-access-fails.md`, `rules/observability-and-error-management.md`.
- Origin: 6 to 7 Oct 2026, a new KMS key applied without read access for the plan role, leaving the weekly drift check failing with a plan error.
