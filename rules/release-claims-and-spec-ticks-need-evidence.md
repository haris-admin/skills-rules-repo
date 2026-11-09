# Release-note claims and ticked tasks need evidence (all agents)

Extends `ci-gate-commands-run-locally-before-push` and the "a ticked task is a claim" rule.

## Why this exists
**8 Nov 2026, Tap-Ease:** a blind review of versions 1.1.11 and 1.1.12 found nine specs with every task ticked including device screenshots that were not in the repo, a claimed unit test that did not exist, a status "verified on the Flex" next to unticked Flex tasks, "tax-compliant" and "all tests passing" in the release notes that no test run supported, and one press value stated three ways (0.92, 0.95, 0.96).

## Rules
1. A tick cites a test name or a file that exists. Screenshots and device evidence are committed or the task stays unticked.
2. Release notes state only what a recorded command, with date and result, supports. Compliance wording ("tax-compliant") needs a source.
3. A number stated in a spec, the code and the notes comes from one configuration default, and a test asserts the default once.
4. Before a release, dispatch a blind adversarial review that sees the code and specs, not the closeout. Record its decisions verbatim, as structured answers, one at a time.
5. When the review reopens a spec, add a dated "Status correction" banner and untick, so the next agent sees the truth first.
