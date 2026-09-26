# Evals Use the Production Prompt, Imported

An eval of an AI prompt must import the exact prompt text production sends from one shared module, never copy it and never extract it from source code with a regex.

## Why this exists

Simplifii-OS, 26 Sep 2026: `evals/aura-model-compare/run.mjs` read AURA's rails by regex-matching the `INTEGRITY_GUARDRAIL` string literal in `api/tutor.js`. Two changes would each have made it send no rails at all, silently: a comment added inside the string concatenation (the loader treated it as unsafe and dropped the rails), and moving the constant to its own module (the regex found nothing). The eval would still have run and reported results for a prompt production never sends.

## Rule

1. Put the prompt text (or its loader) in one module that production imports.
2. Every eval, script and test imports that module. No copies, no regex over source files.
3. Add a test that the endpoint's captured prompt ends with (or contains) exactly the imported text, and that the eval's provider sends the same text.
4. An eval that cannot find its prompt must fail loudly, never fall back to an empty string.
5. Keep the eval cases and the grading criteria in reviewable data files (JSON), separate from the harness code, so people can read and change what is checked.

## Related

- `red-for-the-right-reason.md` (prove the checks can fail)
