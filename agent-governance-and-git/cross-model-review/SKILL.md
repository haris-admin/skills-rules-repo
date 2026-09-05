---
name: cross-model-review
description: For a security- or compliance-critical design/spec review, prefer engaging a genuinely different underlying model, not just a fresh context window of the same model.
---

# Cross-Model Adversarial Review

## Directives

1. **A fresh context of the same model shares the same blind spots as the author.** For
   high-stakes review (security, compliance, an already-approved plan being amended), route the
   review through a different underlying model when one is available, not just a new conversation
   with the same one.
2. **Give the reviewing model an explicit adversarial mandate**: assume the design/code is wrong
   and try to prove it, rather than checking it against a completeness checklist. A checklist pass
   confirms the obvious; an adversarial pass finds the self-contradiction the author couldn't see.
3. **Verify the review's own claims before acting on them** — a reviewing model can also overstate
   scope (e.g. "this bug affects ~14 files" when a corrected check later found 7) or miss that a
   citation only checks one of two places a guard can actually live. Spot-check at least the
   review's most consequential claims against live source before treating them as ground truth.
