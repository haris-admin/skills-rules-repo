---
name: openapi-docs-release-notes
description: >-
  Standardized protocol for publishing human-readable release notes directly at the top of OpenAPI / Swagger UI / ReDoc API documentation (FastAPI description attribute) and maintaining a root RELEASE_NOTES.md. Use when cutting a release, bumping a version, documenting endpoint contract changes, or reviewing interactive API documentation.
---

# OpenAPI & Swagger UI Release Notes Standard

This skill establishes the engineering pattern for publishing rich, human-readable release notes directly at the very top of interactive API documentation (**Swagger UI `/docs`**, **ReDoc `/redoc`**, and **OpenAPI Schema `/openapi.json`**) via the FastAPI `description` parameter, synchronized with a root `RELEASE_NOTES.md`.

Inspired by the proven Tap-Ease and Undispute production architectures, this ensures partners, bank integrators, mobile developers, and operators immediately see what changed in each release without needing external wikis or release portals.

---

## 1. Core Architecture Pattern

FastAPI renders its top-level `description` parameter as GitHub-flavored Markdown in Swagger UI and ReDoc. By structuring `api_description` with reverse-chronological `## Version X.Y.ZZ Release Notes` blocks at the top, the interactive documentation doubles as a living changelog.

### Implementation Pattern (`app/main.py` or `app/asgi.py`):

```python
from app import __version__  # Synchronized with .version

api_description = f"""
# <Project Name> Backend API

## Version {__version__} Release Notes

**<Headline Feature or Fix Area>:**
* **`METHOD /path`** — Description of new endpoint, query parameter, or contract change.
* **Component / Service** — Core architectural improvement, database migration, or security hardening.
* **Compatibility & RFC Compliance** — Explicit confirmation of backward compatibility or breaking change notice.

## Version <Previous Version> Release Notes

**<Previous Feature Area>:**
* Feature bullet point...

---

## API Overview

High-level architecture, base URLs, authentication methods, error handling standards, and developer guidelines.

### Base URLs
- Production: `https://api.example.com`
- Staging: `https://api-stg.example.com`
- Local Development: `http://localhost:<port>`

API Version: {__version__}
OpenAPI Schema: `/openapi.json` (or `/api/v1/openapi.json`)
Swagger UI: `/docs`
ReDoc: `/redoc`
"""

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=api_description,
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
```

---

## 2. Release Notes Content Hygiene

Every `## Version X.Y.ZZ Release Notes` entry must follow these content standards:

1. **Exact Version Heading**: Must match `## Version X.Y.ZZ Release Notes` where `X.Y.ZZ` strictly matches the canonical `.version`.
2. **Categorized Bold Headlines**: Group changes under bold topic headers:
   - `**<Feature Name> Endpoints & Schemas:**`
   - `**Security Hardening & Privacy Mandates:**`
   - `**Database Migrations & Schema Changes:**`
   - `**Bug Fixes & Reliability:**`
3. **Explicit HTTP Method & Path**: Always format route changes with backticks and uppercase methods (e.g. `POST /api/v1/disputes/{case_number}/bank-evidence-pack`).
4. **Parameter & Payload Details**: Call out new request parameters, status code changes, or added JSON fields.
5. **Regulatory & Architectural Traceability**: Mention relevant compliance frameworks (e.g. *Privacy Act 1988 APP 6*, *PCI-DSS*, *Spam Act 2003*, *DNCR Act 2006*, *RFC 8785*).

---

## 3. Synchronous Artifact Triad

When cutting a version or writing release notes, maintain three synchronized artifacts:

1. **`app/main.py` (or `app/asgi.py`)**: Prepend the newest release block to `api_description` so Swagger UI `/docs` displays it at the very top.
2. **`RELEASE_NOTES.md`**: Maintain the complete, unabridged historical log of all releases at the repository root.
3. **`docs/context.md` (or equivalent)**: Update current baseline version and roadmap status table.

---

## 4. Automated Verification Test

Always include a dedicated test ensuring the OpenAPI documentation contains the current release notes:

```python
def test_openapi_description_contains_current_release_notes():
    """Verify that FastAPI app description has release notes for current version."""
    from app import __version__
    from app.main import app

    assert app.description is not None
    assert f"## Version {__version__} Release Notes" in app.description
    
    # Verify openapi schema generation
    schema = app.openapi()
    assert schema["info"]["version"] == __version__
    assert f"## Version {__version__} Release Notes" in schema["info"]["description"]
```
