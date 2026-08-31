# Vercel Email Template — Dark Theme

HTML email template used by `vercel_monitor.py` for twice-daily deployment reports. Dark theme matching Pluto's console output aesthetic.

## Structure

```
┌─ Header (dark navy #1a1a2e) ─────────────────────┐
│  🔍 Vercel Monitor — {Project Name}               │
│  {Date — Time AEST}                                │
│  Border: green (#22c55e) or red (#ef4444)          │
├─ Status Banner ───────────────────────────────────┤
│  ✅ ALL CLEAR  or  ⚠️ NEEDS ATTENTION             │
│  {project} | {project_id truncated}                │
├─ Project Health ──────────────────────────────────┤
│  Framework, Deployments count, Alerts count        │
├─ Alerts Section ──────────────────────────────────┤
│  🔴 per-alert rows, or ✅ No issues               │
├─ Logs Link ───────────────────────────────────────┤
│  📄 Full logs: Vercel Dashboard (linked)           │
├─ Footer (dark navy #1a1a2e) ──────────────────────┤
│  Powered by Pluto · Haris Habib's Automation       │
│  Platform · {timestamp} AEST                       │
└───────────────────────────────────────────────────┘
```

## Color Scheme

| Element | Color |
|---------|-------|
| Background | `#0f172a` (slate-900) |
| Card | `#1e293b` (slate-800) |
| Header/Footer | `#1a1a2e` (navy) |
| Healthy green | `#22c55e` |
| Alert red | `#ef4444` |
| Section headers | `#818cf8` (indigo) |
| Muted text | `#94a3b8` (slate-400) |
| Dark muted | `#475569` (slate-600) |

## Recipients

| Project | Recipients |
|---------|-----------|
| AML Hive | `hhsiddiqui@gmail.com`, `shoaib@amlhive.com.au` |

## Subject Format

```
🔍 Vercel Monitor — {Project} [{STATUS}] — {Date Time}
```

Example: `🔍 Vercel Monitor — AML Hive [⚠️ NEEDS ATTENTION] — 05 Jun 09:20 PM`
