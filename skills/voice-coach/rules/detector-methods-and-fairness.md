# Detector Methods and Fairness (the hard boundary)

This file exists to keep the coach from regressing into the detector it explicitly is not. Every method below is REFUSED BY NAME. The coach must never run, import, call, or approximate any of them on student text to produce a human-vs-AI judgement. This is a P0 invariant, enforced like `docs/PROHIBITED_PATTERNS.md`: violating it is a P0 bug regardless of feature context.

## Why these are refused (the shared failure mode)

Every method here shares one documented bias: the features it reads as "AI" ARE the authentic writing of the students Simplifii exists to serve.
- Low perplexity = disciplined, plain, conventional register (good academic writing, and L2 writers aiming for clarity).
- Low burstiness = a learned uniform sentence template (autistic, anxious, or trained writers).
- Restricted lexical diversity = an L2 or neurodivergent idiolect.
A coach that scored "does this sound AI" on the text would systematically punish its own users for writing the way they write. Importing any of these would build the bias the constitution forbids.

## The refusal list (never use any of these on student text for a human/AI verdict)

### 1. Perplexity (token-predictability scoring)
- **What it does:** a reference LM scores how "surprised" it is by each token; low average perplexity is read as AI.
- **Why refused:** decontextualised. It cannot tell mechanical repetition from disciplined academic register. Plain, formulaic, convention-adhering prose (exactly what good academic and L2 writing produce) scores LOW and reads as AI. Unreliable under ~250 words. This single metric drives most ESL and neurodivergent false positives.

### 2. Burstiness (variance of perplexity / sentence-rhythm variation)
- **What it does:** measures how much sentence length/complexity varies; low variance is read as AI.
- **Why refused:** a deliberate stylistic choice, not a forgery. Technical and many academic writers keep cadence steady on purpose; disabled, autistic, or anxious writers using a learned uniform template score low. Population-level tendency, not per-document truth; noisy and trivially gamed by adding one short and one long sentence (which is exactly what the retired humaniser did).

### 3. Supervised classifier models (fine-tuned transformers, e.g. RoBERTa)
- **What it does:** a transformer fine-tuned on human-vs-AI corpora outputs a probability.
- **Why refused:** poor generalisation. Excels in-domain, degrades sharply on out-of-domain genres, newer/unseen LLMs, and revised drafts. Learns whatever separated its training classes, which is not a stable signal for a real student's real draft.

### 4. Stylometry / authorship features
- **Why refused:** same class boundary problem. Function-word and embedding-space features encode dialect and idiolect, so they flag L2 and neurodivergent voice as anomalous.

## What IS allowed

- The LOGGED provenance only: `authenticity_split.human_percent` derived from `tier_transition` attribution. Shown as DATA (the student's own record), never as a verdict, and suppressed entirely when `metric_suppression` is true.
- Quality dimensions in `writing-quality-dimensions.md`, which score the TEXT against the genre, not the AUTHOR against a class boundary, and therefore carry no false-positive bias.

## Enforcement

- The endpoint must never return a field expressing likelihood that the text is AI (e.g. `aiLikelihood`, `aiScore`, `humanProbability`). A unit test fails the build if such a field appears.
- The endpoint must never echo a verbatim-rewritten span of the student's input above a short threshold. A unit test fails the build if it does.
- If a future request asks the coach to "check if this is AI", the correct response is the provenance split plus quality coaching, NOT a detector score.
