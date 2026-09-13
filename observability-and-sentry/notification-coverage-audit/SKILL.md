---
name: notification-coverage-audit
description: Audit event notifications, email alerts, and in-app trays to ensure 100% deep-link completeness and trigger coverage. Use when adding a new notification type, reviewing an existing notification/email/tray feature, or investigating a report that a notification didn't fire or its link goes nowhere.
---

# Notification Coverage Audit

## Audit Requirements
1. **Deep-Link Completeness**: Every notification row and email CTA must contain a valid, non-null deep link navigating directly to the impacted record.
2. **Trigger Alignment**: When an entity status changes, the corresponding notification event must fire reliably.
3. **Read/Resolve Lifecycle**: Ensure marked-as-read and resolution actions correctly retire active tray items.

