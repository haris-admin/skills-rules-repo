# Notification / reminder coverage audit (all agents)

Applies when adding a new `event_type` to `ComplianceCalendarEvent`, a new
`notification_type` to the Notification Centre, a new `related_record_type` (or
`source_type` fallback) on `Notification` rows, a completion/sign-off path that
should retire an alert, or any new record kind meant to be picked up by a
background job — and periodically as a health check.

Skill (procedure): `.claude/skills/notification-coverage-audit/SKILL.md`
(global copy `~/.claude/skills/notification-coverage-audit/` is the
framework-agnostic audit; this file is the YourApp product rule).

This repo has shipped three related gap classes:

| Class | Incidents | What was missing |
|-------|-----------|------------------|
| Created, never scanned | C76 (`Compliance Regulator_ENROLMENT`/`AML_CTF_REVIEW`); C76a (`SCREENING_HIT_REVIEW`/`EMPLOYEE_RESCREEN`/`INDEPENDENT_EVALUATION_DUE`) | reminder/escalation job filter never included the new `event_type` |
| Created, never deep-linked | issue-130 scoped `compute_notification_deep_link()` to `ai_ownership_extractions` only; **issue-272 / C427** (22 Aug 2026) found `compliance_calendar_events` still returned `None`; live **Overdue** CDD Stage 3/4 rows used `cdd_checklists` and were still `None` until **C428 / v0.5.102** | tray rendered a non-clickable `<div>` because the backend never set `deep_link` |
| Read path live, writer never called | **issue-272 / C427** — `resolve_notification()` existed and `list_notifications()` already filtered `delivery_status != "resolved"`, but `grep -rn "resolve_notification\\b" app/` found **zero callers** | actioned alerts never left the tray |

Run all three tables below, not just the reminder-job one.

## C428 product rules (human 22 Aug 2026 — live in v0.5.102)

These are standing product rules, not a one-off change:

1. **If `GET /notifications` returns the row, `deep_link` SHALL be non-null.** Who *receives* a
   notification is already permission-driven (`user_id` + `agency_id` + compliance-critical
   Principal override). The mapper MUST NOT add a second role check. Destination pages keep their
   own 403s.
2. **`create_notification` copies `source_type` onto `related_record_type` when unset.** Aliases
   (`calendar`, `training`, `ttr`, `screening`, `cdd_transactions`) need registry rows too, not
   only explicit `related_record_type=` literals.
3. **Returning `None` for a newly written type is a GAP.** Add a row to
   `NOTIFICATION_DEEP_LINK_ID_ROUTES` / `NOTIFICATION_DEEP_LINK_STATIC_ROUTES` in
   `notification_service.py` **and** a `test_compute_notification_deep_link_*` assertion in the
   same change. The executable guard is
   `test_every_notification_related_record_type_has_a_deep_link` (proven non-vacuous: drop
   `cdd_checklists`, it names that type). If no per-id query param exists, land on the nearest
   existing authenticated page (C428 `design.md` §1) — do **not** invent a "Phase 2 follow-up
   table" instead of a mapper row. That was C427 `design.md` §4; the human rejected it.
4. **Before claiming "the destination page has no query param", grep it.** C427 §4 said
   `/dashboard/CDD` had no `?id=`; `frontend/app/(dashboard)/dashboard/CDD/page.tsx` already
   read `id` (audit trail already used `/dashboard/CDD?id=`). Stale "needs frontend work first"
   notes are not a reason to return `None`.
5. **`SCREENING_HIT` `source_id` MUST be `screening_result_id`, not `matter_id`.** The mapper
   targets `/screening/result/{id}?type=matter`. Old rows that stored a matter id are not
   backfilled.
6. **Tray affordance:** `NotificationTray.tsx` uses `textDecoration: 'none'` on the card
   `<Link>`, so a linked row looks like plain text. Linked rows MUST show a visible **Open**
   label (`var(--c-info)`, no raw hex). Sprint Rule 6: a component wiring test is required, not
   a helper-only test.
7. **`design.md` wins over an issue file's "Recommended fix".** issue-272 said hop through the
   calendar event's `linked_record_*`; C427 design reused `/dashboard/CALENDAR?event_id=` because
   that route already exists.
8. **Mapper is read-time** (`GET /notifications` calls `compute_notification_deep_link`). No
   historical-row backfill and no resolve-sweep cron unless the human asks.

## ACR evidence-capture (C429) — cross-reference only

This rule **cross-references** [acr-evidence-capture-standard.md](acr-evidence-capture-standard.md).
Do **not** merge the two rules. Do **not** create a second synonym list here.

Mapper membership (`NOTIFICATION_DEEP_LINK_*`) is required **only when a notification writer
exists** for that type. Adding an ACR locator or an
`acr_evidence_manifest_entries.source_record_type` does **not** by itself require a mapper row.
Evidence-only types stay out of this file's tables. If you *do* add a `create_notification`
writer, C428 still applies (visible tray row ⇒ non-null `deep_link`).

## 1. Reminder / escalation job coverage (C76 / C76a)

- **Creation call sites:** grep `event_type="` across `app/services/*.py` and
  `app/workers/*.py` — every `calendar_service.create_compliance_event(...)` call.
- **Scan call sites:** `app/workers/calendar_worker.py` — `_COMPLIANCE_DEADLINE_EVENT_TYPES`
  (used by `send_compliance_deadline_alerts`), plus any type-specific job (e.g.
  `check_cdd_overdue` only handles `CDD_OVERDUE`; `training_worker.py` handles
  `TRAINING_DUE`/`TRAINING_RENEWAL` separately — not in `calendar_worker.py` at all).
  `send_urgent_overdue_alerts` (C76a) is deliberately **unfiltered by type** — it
  covers everything, so a type missing from `_COMPLIANCE_DEADLINE_EVENT_TYPES` is
  still covered post-due-date by that job, just not pre-due-date.
- **Registration check:** every job must appear in `app/workers/__init__.py`
  `WorkerSettings.cron_jobs` — a function defined in `calendar_worker.py` but not
  in that list never runs.

```
| event_type | Created at | Pre-due reminder job | Post-due escalation job | Verdict |
```

A GAP is a type with **NONE** in both reminder and escalation columns.

## 2. Tray deep-link coverage (issue-272 / C427 / C428)

`frontend/components/NotificationTray.tsx` already renders a real `<Link>` whenever
`deep_link` is non-null. A missing click-through is almost always the backend mapper,
not the frontend.

```bash
# Discriminators actually written onto Notification rows
grep -rn 'related_record_type=' backend/app --include='*.py'

# Branches that actually return a route
# (backend/app/services/notification_service.py::compute_notification_deep_link)
```

```
| related_record_type | Written at | deep_link branch | Verdict |
```

A GAP is a type written somewhere whose mapper branch is missing. C428
(`openspec/changes/428-notification-tray-complete-deep-links/`) maps every writer
literal; the executable guard is
`test_every_notification_related_record_type_has_a_deep_link`. Do not add an
unverified route guess — if a destination page does not exist yet, land on the
nearest existing authenticated page (C428 `design.md` §1) rather than returning
`None`.

When adding a new `related_record_type=` / `source_type=` at a
`create_notification` site, add the mapper registry row **and** a
`test_compute_notification_deep_link_*` assertion in the same change. Returning
`None` for a newly written type is a GAP.

## 3. Resolution lifecycle writers (issue-272 / C427)

If the read path already hides a terminal state, the setter must have callers.

```bash
grep -rn 'resolve_notification(' backend/app --include='*.py'
# definition-only (one hit) = GAP — that was C427: function built, never called
```

Every `create_notification` / `create_notifications_for_role` path that the tray
treats as an action item needs a matching `resolve_notification(...)` at the
record's completion/sign-off/dismiss site, with the **same**
`(related_record_id, related_record_type)` pair the create site wrote (C427
screening-hit reviews are keyed to the `compliance_calendar_events` id, not the
`screening_result` id). Completing an already-done record is not a backfill —
C427 does not sweep historical stale rows; do not invent a cron for that unless
the human asks.

## After finding a gap

Log it via `/prod-issue` before fixing (this repo's convention) — do not
implement the fix silently.

**Spec wins over the issue file's "Recommended fix".** issue-272's recommended
fix said hop through the calendar event's `linked_record_*`; C427 `design.md` §1
said reuse `/dashboard/CALENDAR?event_id=` because that route already exists.
Cursor implemented the design, not the issue's guess.
