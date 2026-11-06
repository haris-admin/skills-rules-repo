# Dependency major upgrades ship in their own release, verified twice and live

Security upgrades inside the current major go first; a new major (for example Pillow 13, starlette 1.x) is its own release with a quiet-database double run and a live check of the path that uses it.

**Scope:** all agents upgrading dependencies in a production system.

---

## Core Directives

1. **Split the releases**: fixes inside the major first; the new major later, on its own, so a regression has one cause.
2. **Cap by design, then lift by decision**: record a version cap with its reason, and lift it only on the owner's decision, replacing the floor test in the same change.
3. **Prove it twice**: run the full suite twice in a row on a quiet database, list every package that changed in the lock, run the vulnerability audit before and after, and classify any failure as regression, contention or flaky with evidence.
4. **Check the live path**: after the deploy send a harmless synthetic input through the code that uses the library (an image and a PDF through the OCR route) and keep it small and non-personal.
5. **Release from the right base**: build the release branch from `main` plus only the approved commits when other work sits on `dev`, then merge back.

## Why this exists

**6 Nov 2026 (HandleDispute):** pypdf, certifi and starlette 0.52 shipped as 0.240.23; Pillow 13 and starlette 1.10 shipped alone as 0.240.24 after 8 clean suite runs (44 advisories to none), verified live with a blank PNG and PDF.
