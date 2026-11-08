# Tests that run a deploy script must redirect every host path to a temp folder

A deploy script that writes to a system folder passes on a laptop where the folder does not exist and fails on the CI runner where it does.

**Scope:** shell deploy scripts under test (`remote-deploy.sh` style), any test that runs a script with shimmed docker, curl or aws.

---

## Core Directives

1. **Every host path in the script has an environment override** with the real path as the default (for example `HD_SYSTEMD_DIR`, `HD_ROOT`, `HD_SECRETS_DIR`, `HD_LOCK_FILE`).
2. **The shared test helper sets all of them to a temp folder.** A new override is added to the helper in the same change as the script.
3. **A green local run proves nothing about a path that exists only on the runner.** Read the CI result before calling the fix done.
4. **Tests must not leave files in the working directory** (a stray `backend/s3:/releases/...` folder appeared after an infra run); check `git status` after a test run.

## Why this exists

**8 Nov 2026 (HandleDispute, OpenSpec 53a):** the ClamAV signature timer wrote `/etc/systemd/system/hd-freshclam.service`. Five infra tests failed on the CI runner with `Permission denied`, the backend tests step failed and the production deploy run 42493324959 never reached its deploy jobs. Locally 429 tests passed.
