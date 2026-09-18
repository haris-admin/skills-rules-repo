---
name: incremental-version-bumping
description: Mandatory version bumping protocol: 0.10.0 baseline, defect fixes 0.10.01 onward, new feature releases 0.20.0, 0.30.0, etc.
---

# Incremental Version Bumping Standard

This document defines the official versioning lifecycle for the Undispute platform.

---

## 1. Version Format & Rules

Every release and atomic check-in follows the strict two-tier milestone and defect convention:

$$\text{Milestone Base: } 0.F0.0 \quad \longrightarrow \quad \text{Defect / Increment: } 0.F0.NN$$

Where:
* $F$ is the Feature / Capability number ($1, 2, 3, 4, 5, 6, 7$).
* $NN$ is the zero-padded two-digit defect fix / patch increment ($01, 02, 03, \dots, 99$).

---

## 2. Capability Milestone Roadmap

| Feature / Capability | Initial Release | Defect / Patch Fix Sequence | Scope |
| :--- | :--- | :--- | :--- |
| **Feature 1: Foundation & Data Architecture** | **`0.10.0`** | **`0.10.01`** *(Current)*, `0.10.02`, `0.10.03`... | Core Schema, Migrations, Logging & Observability |
| **Feature 2: Centralized Verification & OTP** | **`0.20.0`** | `0.20.01`, `0.20.02`, `0.20.03`... | OTP generation, rate limiting, verification tokens |
| **Feature 3: Merchant Directory & Intake** | **`0.30.0`** | `0.30.01`, `0.30.02`, `0.30.03`... | ABN / Name lookup, pre-claim outreach gating |
| **Feature 4: Dispute Intents & Evidence** | **`0.40.0`** | `0.40.01`, `0.40.02`, `0.40.03`... | Cardholder intake, transaction tuple matching, evidence dropzone |
| **Feature 5: Case Management State Machine** | **`0.50.0`** | `0.50.01`, `0.50.02`, `0.50.03`... | 48-hour SLA timers, settlement negotiation states |
| **Feature 6: Resolution Record & Bank Pack** | **`0.60.0`** | `0.60.01`, `0.60.02`, `0.60.03`... | Cryptographic settlement proof, signed PDF evidence packs |
| **Feature 7: Web Portals & Demo Suite** | **`0.70.0`** | `0.70.01`, `0.70.02`, `0.70.03`... | Next.js interactive UI, Cardholder & Merchant portals |
| **General Availability (Production Launch)** | **`1.00.0`** | `1.00.01`, `1.00.02`, `1.00.03`... | Live production deployment |

---

## 3. Synchronization Checklist

Whenever a defect fix or atomic commit is made, update the version synchronously across:
1. [`.version`](file:///Users/harishabib/code/github/haris-admin/undispute-scheme-neutral-resolution/.version): `0.X0.NN` (Canonical source of truth)
2. [`backend/pyproject.toml`](file:///Users/harishabib/code/github/haris-admin/undispute-scheme-neutral-resolution/backend/pyproject.toml): `version = "0.X0.NN"`
3. [`backend/app/__init__.py`](file:///Users/harishabib/code/github/haris-admin/undispute-scheme-neutral-resolution/backend/app/__init__.py): `__version__ = "0.X0.NN"`
4. [`backend/app/main.py`](file:///Users/harishabib/code/github/haris-admin/undispute-scheme-neutral-resolution/backend/app/main.py): `version="0.X0.NN"` (FastAPI constructor and `GET /` endpoint) AND prepend `## Version 0.X0.NN Release Notes` to `api_description` (per `openapi-docs-release-notes` skill)
5. `frontend/package.json` & `frontend/package-lock.json`: `"version": "0.X0.NN"`
6. `frontend/src/config/version.ts`: `VERSION = "0.X0.NN"`
7. `RELEASE_NOTES.md`: Prepend latest `## Version 0.X0.NN Release Notes` block at top

