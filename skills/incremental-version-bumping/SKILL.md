---
name: incremental-version-bumping
description: >-
  Enforce mandatory incremental version bumping protocol across agent environments (Claude Code, Antigravity, Cursor, Codex, Devin) with 0.F0.0 feature baselines and 0.F0.NN defect increments. Use when tagging a release, incrementing project version files (.version), creating atomic commit check-ins, or reviewing semantic version hygiene.
---

# Incremental Version Bumping Standard

This standard defines the mandatory versioning lifecycle and atomic check-in protocol across all repositories and agent environments (**Claude Code, Antigravity, Cursor, Codex, Devin**).

---

## 1. Version Format & Rules

Every release, feature milestone, and atomic check-in follows the strict two-tier milestone and defect convention:

$$\text{Milestone Base: } 0.F0.0 \quad \longrightarrow \quad \text{Defect / Increment: } 0.F0.NN$$

Where:
* $F$ is the Feature / Capability number ($1, 2, 3, 4, 5, 6, 7, \dots$).
* $NN$ is the zero-padded two-digit defect fix / atomic patch increment ($01, 02, 03, \dots, 99$).

### Rule Summary
1. **Baseline / Feature Inception**: Every new capability or foundational milestone starts at **`0.F0.0`** (or `0.F0.00`).
2. **Defect & Patch Increments**: Every bug fix, security patch, atomic commit, or sub-task increments $NN$: `0.F0.01`, `0.F0.02`, `0.F0.03`...
3. **Major Capability Promotion**: When advancing to the next major capability milestone, increment the tens place: `0.10.0` $\to$ `0.20.0` $\to$ `0.30.0` $\to$ `0.40.0` $\to$ `0.50.0` $\to$ `0.60.0` $\to$ `0.70.0`.
4. **General Availability (GA)**: Reaching full production launch promotes to **`1.00.0`** (with patches `1.00.01`, `1.00.02`...).

---

## 2. Capability Milestone Roadmap (Reference Architecture)

| Feature / Capability | Initial Release | Defect / Patch Fix Sequence | Scope |
| :--- | :--- | :--- | :--- |
| **Feature 1: Foundation & Data Architecture** | **`0.10.0`** | **`0.10.01`** *(Current)*, `0.10.02`, `0.10.03`... | Core Schema, Migrations, Logging & Observability, Security Baselines |
| **Feature 2: Centralized Verification & OTP / Auth** | **`0.20.0`** | `0.20.01`, `0.20.02`, `0.20.03`... | OTP generation, rate limiting, verification tokens, RBAC policies |
| **Feature 3: Merchant Directory & Intake / Catalog** | **`0.30.0`** | `0.30.01`, `0.30.02`, `0.30.03`... | ABN / Name lookup, pre-claim outreach gating, directory indexing |
| **Feature 4: Dispute Intents & Evidence / Core Engine**| **`0.40.0`** | `0.40.01`, `0.40.02`, `0.40.03`... | Intake flows, transaction tuple matching, evidence dropzone |
| **Feature 5: Case Management & State Machine** | **`0.50.0`** | `0.50.01`, `0.50.02`, `0.50.03`... | SLA timers, settlement negotiation states, automated loops |
| **Feature 6: Resolution Record & Signed Proof** | **`0.60.0`** | `0.60.01`, `0.60.02`, `0.60.03`... | Cryptographic settlement proof, signed PDF evidence packs |
| **Feature 7: Web Portals & Demo Suite** | **`0.70.0`** | `0.70.01`, `0.70.02`, `0.70.03`... | Interactive UI, Cardholder/Student & Merchant/Admin portals |
| **General Availability (Production Launch)** | **`1.00.0`** | `1.00.01`, `1.00.02`, `1.00.03`... | Live production deployment |

---

## 3. Synchronization Checklist Across Manifests

Whenever a feature milestone or defect/atomic commit is made, update the version synchronously across all relevant manifests:

### For Node / React / Web Platforms (e.g. Simplifii-OS):
1. **`package.json`**: `"version": "0.X0.NN"`
2. **`package-lock.json`**: `"version": "0.X0.NN"` (root and `packages[""]`)
3. **`.version`** (when present): `0.X0.NN`
4. **Telemetry / Runtime App Config** (if reporting version to health/status endpoints)

### For Python / FastAPI / Microservice Backends (e.g. Undispute):
1. **`backend/pyproject.toml`**: `version = "0.X0.NN"`
2. **`backend/app/__init__.py`**: `__version__ = "0.X0.NN"`
3. **`backend/app/main.py`**: `version="0.X0.NN"` (FastAPI constructor and `GET /` endpoint)
4. **`frontend/package.json`** (when frontend is initialized): `"version": "0.X0.NN"`

---

## 4. Universal Agent Mandate (Claude, Antigravity, Cursor, Codex, Devin)

1. **Bump Before / With Every Change:** Never commit code changes without synchronously bumping the version in all manifests.
2. **Commit Locally on Green Milestones:** Do not wait to be asked for local commits; commit at small, revertible Green milestones using pathspec:
   ```bash
   git add <file1> <file2> && git commit -m "feat(scope): 0.10.01 - description"
   ```
3. **Pathspec Hygiene:** Always specify exact files. Never run bare `git add .` or `git add -A`.
4. **Push Boundary:** Push to remote only when explicitly requested by the human or instructed by the execution plan.
