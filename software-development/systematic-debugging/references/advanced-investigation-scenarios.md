# Advanced Phase 1 Investigation Scenarios

Four specialized Phase 1 (Root Cause Investigation) techniques for scenarios beyond the basic "read errors, reproduce, check changes, trace data flow" loop. Load this when the basic Phase 1 steps in SKILL.md don't explain what you're seeing — a cache-masked bug, a bug on a different branch than the one checked out, a cascade of seemingly-separate errors, or a dependency-injection/protocol registration failure.

## Contents

- [Cache Masking (.pyc, .pytest_cache, node_modules/.cache)](#cache-masking-pyc-pytest_cache-node_modulescache)
- [Multi-Branch \& Cross-Version Error Tracing](#multi-branch--cross-version-error-tracing)
- [Error Cascade Analysis — Tracing Through Dependent Stages](#error-cascade-analysis--tracing-through-dependent-stages)
- [DI Container / Protocol Registration Debugging](#di-container--protocol-registration-debugging)

## Cache Masking (.pyc, .pytest_cache, node_modules/.cache)

**WHEN tests pass but you suspect the source code is broken (e.g., after a refactor/extraction):**

Python (and some JS tools) cache compiled bytecode. Tests can pass from stale cache even when the source `.py` file is syntactically invalid.

**Symptoms of cache masking:**
- All tests pass but a direct import fails: `python3 -c "from module import thing"` → SyntaxError
- You deleted a function but tests still find it
- A refactor you're certain removed code, yet tests are green

**Action — Clear and re-verify:**
```bash
# Clear Python caches
rm -rf __pycache__ .pytest_cache tests/**/__pycache__ src/**/__pycache__

# Re-run tests from clean state
pytest tests/ -q

# ALSO: direct import check
python3 -c "import sys; sys.path.insert(0, 'src/backend'); from module import thing; print('OK')"
```

**If tests now fail:** The source was broken all along. The cache was hiding it. Fix the source.

**If direct import fails but pytest passes:** pytest is loading from a different cache. Check for `.pyc` files in unexpected locations or a stale virtual environment.

## Multi-Branch & Cross-Version Error Tracing

**WHEN a bug is reported from a deployed/remote version but the code on your current branch doesn't match:**

The deployed version may have features (endpoints, services, models) that don't exist in your workspace. **Do not assume the bug is in the code you have checked out.**

**Procedure:**

1. **Identify the deployed version** — Check the running instance:
   ```bash
   # From the deployed API docs or /openapi.json
   web_extract(urls=["https://deployed-instance/docs"])
   # Look for: "Version: X.Y.Z" or "API Version: X.Y.Z"
   ```

2. **Find the feature branch** — List remote branches to locate the version that matches:
   ```bash
   git fetch origin
   git branch -r
   git tag -l | sort -V  # Tags often match release versions
   ```
   Look for branch names containing feature keywords (`card`, `integration`, etc.) or matching the version prefix.

3. **Check if the feature exists on your branch** — Search your current branch first:
   ```bash
   search_files(pattern="endpoint_path_or_function_name", path="app/", file_glob="*.py")
   ```
   If nothing found, the feature is on a different branch.

4. **Read code from the feature branch** — `git show` reads files from any branch without switching:
   ```bash
   git show origin/feature-branch:path/to/file.py
   ```
   Use this to read routers, services, models, and config from the branch that has the deployed code.

5. **Trace the error through the feature branch** — Follow the same technique as single-branch debugging but executed through `git show` pipes. Read the full chain: router → model validation → service call → external API call.

6. **Check DI container registration** — When the error is about an "unknown protocol" or "unsupported protocol", look at:
   - The dependency injection container: `app/dependencies/container.py`
   - The service protocol: `app/services/protocols.py`
   - The startup registration: `app/asgi.py` imports
   - The service module's bottom (where `Container.register()` is called)

   An `"UnsupportedProtocol"` error often means httpx received an empty/malformed base URL because the config for the external service (CARD_SERVICE_BASE_URL, etc.) is missing or empty.

7. **Determine fix location** — Decide whether to:
   - Fix on your branch and request a forward-merge to the feature branch
   - Cherry-pick the fix to the feature branch
   - Alert the user that the fix needs to go into a specific branch

## Error Cascade Analysis — Tracing Through Dependent Stages

**WHEN a user reports multiple errors that appear to be separate bugs (e.g., A fails, then B fails, then C fails):**

The errors are often NOT independent — one validation failure at an earlier stage blocks everything downstream. Fix the root validation, and the cascade resolves itself.

**Procedure:**

1. **Map the dependency chain** — Read the errors in reverse order. Identify which step depends on which:
   ```
   C fails ("no card assigned") → depends on B succeeding
   B fails ("missing KYC fields") → depends on A providing those fields
   A fails ("extra inputs not permitted for dob") → FIELD NOT ACCEPTED BY VALIDATION
   ```
   Root cause is stage A. Fixing A unblocks B, which unblocks C.

2. **Classify each error in the cascade:**
   - **Direct error** — The actual root cause (validation rejection, missing config, etc.)
   - **Downstream error** — A consequence of the root cause that looks like a separate bug
   - **Symptom error** — The user-facing error that triggered the report

3. **Verify the chain** — For each downstream error, confirm the prerequisite:
   ```python
   # B's code checks for field from A
   if not user["dob"]:  # ← This will always be None if A doesn't save it
       missing_fields.append("dob")
   ```
   When every downstream error traces back to the same root validation failure, you have a confirmed cascade.

4. **Fix at the source** — Address the root validation/acceptance issue. Do NOT patch downstream checks — they are correct guardrails. The fix belongs at the stage where the data is first rejected.

**Example from a real session:**
| Error | Looks Like | Actually Is |
|-------|-----------|-------------|
| `"/admin/cards/5/kyc" → "No card assigned"` | Card assign bug | Downstream — card assign never ran |
| `"/admin/cards/assign" → "Missing KYC fields: dob"` | KYC validation bug | Downstream — `dob` was never saved |
| `"/admin/update_user_profile" → "Extra inputs not permitted" on dob` | Validation bug | **ROOT CAUSE** — model had `extra="forbid"` & no `dob` field |

**BEFORE diagnosing the last error in the chain, trace backward to find the first error.** Fix the first one, re-test the flow, and the rest often vanish.

## DI Container / Protocol Registration Debugging

**WHEN the error message contains "UnsupportedProtocol", "No factory registered", or mentions a service protocol by name:**

The dependency injection container doesn't have the required service registered. This is a startup/configuration issue, not a runtime logic bug.

**Common causes:**
- The service module is not imported at startup (check `app/asgi.py` for the import)
- The service module's `Container.register()` call at module bottom didn't execute
- The service requires config (`base_url`, `client_id`, etc.) that's empty or missing
- The container's `get()` raises `ValueError` when no factory is registered

**Trace path:**
- Check the container registration (`app/dependencies/container.py`)
- Check the service module bottom for `Container.register()`
- Check startup import in `asgi.py`
- Check the protocol definition in `app/services/protocols.py`
- Check config defaults (empty string = httpx "UnsupportedProtocol")

"UnsupportedProtocol" from httpx specifically means the `base_url` is an empty string. The config defaults to `""` when the env var is not set, and httpx raises this when trying to make a request to an empty URL.
