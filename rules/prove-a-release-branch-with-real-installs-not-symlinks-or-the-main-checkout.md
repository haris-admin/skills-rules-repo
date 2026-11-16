# Prove a release branch with real installs, not symlinks or the main checkout

Applies when a release is verified in a scratch worktree.

**Scope:** all agents preparing a release; HandleDispute (Python 3.13 backend, Next.js static export).

---

## Why this exists

HandleDispute, 17 Nov 2026: `next build` failed in a worktree whose `node_modules` was a symlink to the main checkout (the bundler could not resolve `next`), so the static export of a new page was unproven until a real `npm ci` ran in the release worktree. Bandit under Python 3.13 had been "not installed" for a day until it was built in a throwaway virtual environment with the CI version.

## Core Directives

1. **Run a real `npm ci` in the release worktree,** then `tsc --noEmit`, the full test run and the production build (with the public API URL set); check that the new page is in the output.
2. **Install a scanner in a throwaway virtual environment** from the project interpreter at the version CI pins (`python -m venv`, `pip install bandit==1.8.6`) and run the CI command against the checked-out source, not the main checkout.
3. **Run the CI gate commands on the release branch itself:** format, lint, security scan, contract guard, snapshot check, the smoke subset (`pytest -m smoke` alone; combining a marker with a file path can collect nothing and exit 5).
4. **State what was not run** (end to end tests that need the live stack, real third-party services, accessibility tooling that is not installed).
5. **Keep the release branch local until the owner asks for a push.** A fast-forward push of the main branch deploys nothing in this project; the owner starts the deploy.
