---
name: prod-issue-management
description: Maintain a unified global production issue register with structured investigation templates and verification evidence.
---

# Production Issue Management

## Issue Document Template
Each defect document (`issue-NNN-<slug>.md`) must contain:
1. **Header**: ID, Layer (Frontend/Backend/Infra), Severity (P1/P2/P3), Status (Investigating/In Progress/Resolved).
2. **Sentry Event / Trace**: Timestamp, route, error message, stack trace.
3. **Root Cause Analysis**: Why the issue occurred and why automated tests didn't catch it previously.
4. **Fix & Prevention**: Code changes, regression tests added, and standing rules updated.
5. **Verification Evidence**: Test commands and logs demonstrating resolution.

