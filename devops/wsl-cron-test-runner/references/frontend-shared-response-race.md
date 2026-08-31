# Frontend Async Latch Race — shared-Response mock (Aug 2026)

## Symptom

`frontend/tests/unit/lib/api.test.ts > short-circuits concurrent signout calls
if signOutInFlight is true` fails intermittently/consistently:
`expected "vi.fn()" to be called 1 times, but got 2 times`. Cron suite shows
`170 passed, 1 failed` on vitest while backend + Playwright pass.

## Root cause — TWO layers

1. **Production bug (real):** `signOutAndRedirectAfter401()` reset its
   `signOutInFlight` latch *inside* `supabase.auth.signOut().then()`. With an
   instantly-resolving mock, the latch was cleared before a sibling 401 handler
   in the same burst ran → second handler fired signOut again.

2. **Test-mock amplifier (what makes it deterministic):** the test's
   `mockFetch()` returns ONE shared `Response` object for every call.
   `await response.json()` on the SHARED response resolves for p1, but p2's
   `.json()` (body stream already consumed) resolves LATER — after p1's whole
   signout chain has settled. Any latch that is claimed only after `.json()`
   parsing is therefore cleared by the time p2's handler runs.

## The fix pattern — claim the burst latch BEFORE parsing

Extract one `handleUnauthorizedResponse(response)` used by every
`fetchWithAuth*` wrapper:

```ts
let signOutInFlight: Promise<void> | null = null
let signOutBurstClaimed = false

async function handleUnauthorizedResponse(response: Response): Promise<{ detail?: unknown }> {
  if (response.status === 401 && typeof window !== 'undefined') {
    if (signOutBurstClaimed || signOutInFlight) {
      // sibling already owns this burst's signout — parse for the thrown error only
      return (await response.json().catch(() => ({}))) as { detail?: unknown }
    }
    signOutBurstClaimed = true          // SYNCHRONOUS claim, before json
    const errorBody = (await response.json().catch(() => ({}))) as { detail?: unknown }
    const reason = loginReasonFromMeResponse(401, errorBody.detail) || 'session_invalid'
    signOutInFlight = (async () => {
      const email = await sessionEmailBeforeSignOut()
      clearMeProfileCache(); clearHelpContentCache(); clearImpersonation()
      const supabase = createClient()
      await supabase.auth.signOut()
      if (!isAuthPublicPage()) {
        window.location.replace(redirectPathForAuthReason(reason, email))
      }
    })().finally(() => {
      signOutInFlight = null
      signOutBurstClaimed = false
    })
    return errorBody
  }
  return (await response.json().catch(() => ({}))) as { detail?: unknown }
}
```

Call sites become `const errorData = await handleUnauthorizedResponse(response)`
inside `if (!response.ok)`, then build + throw the Error as before.

## Why NOT the tempting alternatives

- **`setTimeout(() => latch = false, 0)` release** — breaks test isolation:
  vitest resolves `vi.waitFor` on its first poll before the macrotask fires, so
  the latch from test N leaks into test N+1 (3 tests fail instead of 1).
- **Promise-as-latch with `.finally()` only** — fixes isolation but NOT the
  race: the shared-Response `json()` delay means p2's handler runs after the
  `.finally()` cleared it.
- **queueMicrotask / double-await tricks** — same timing problem; the sibling
  handler is scheduled after the whole chain settles.

The synchronous claim-before-json is the only pattern that survives both the
shared-Response delay and per-test module reuse. `signOutBurstClaimed` +
`signOutInFlight` both checked keeps it robust even if a sibling arrives mid-chain.

## Verification

- `npx vitest run tests/unit/lib/api.test.ts` → 85 passed
- Full frontend: `npx vitest run` → 1771 passed, `tsc --noEmit` clean
- Cron runner must still be pointed at origin/dev (mirror semantics) — local-only
  fixes get wiped by the 03:00 `reset --hard` (see no-fake-pass-guard.md / mirror semantics).
