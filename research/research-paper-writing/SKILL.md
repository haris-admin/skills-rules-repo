---
name: research-paper-writing
title: Research Paper Writing Pipeline
description: "Runs the end-to-end ML/AI research paper lifecycle — experiment design, execution monitoring, result analysis, drafting, self-review, and submission — for NeurIPS, ICML, ICLR, ACL, AAAI, and COLM. Use when starting a new paper from a codebase or idea, designing/running/monitoring experiments, writing or revising any paper section, preparing a submission or rebuttal, converting a paper between conference formats, or preparing post-acceptance deliverables (poster, talk, code release)."
version: 1.1.0
author: Orchestra Research
license: MIT
dependencies: [semanticscholar, arxiv, habanero, requests, scipy, numpy, matplotlib, SciencePlots]
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Research, Paper Writing, Experiments, ML, AI, NeurIPS, ICML, ICLR, ACL, AAAI, COLM, LaTeX, Citations, Statistical Analysis]
    category: research
    related_skills: [arxiv, subagent-driven-development, plan]
    requires_toolsets: [terminal, files]

---

# Research Paper Writing Pipeline

End-to-end pipeline for producing publication-ready ML/AI research papers targeting **NeurIPS, ICML, ICLR, ACL, AAAI, and COLM**. This skill covers the full research lifecycle: experiment design, execution, monitoring, analysis, paper writing, review, revision, and submission.

This is **not a linear pipeline** — it is an iterative loop. Results trigger new experiments. Reviews trigger new analysis. The agent must handle these feedback loops.

<!-- ascii-guard-ignore -->
```
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH PAPER PIPELINE                  │
│                                                             │
│  Phase 0: Project Setup ──► Phase 1: Literature Review      │
│       │                          │                          │
│       ▼                          ▼                          │
│  Phase 2: Experiment     Phase 5: Paper Drafting ◄──┐      │
│       Design                     │                   │      │
│       │                          ▼                   │      │
│       ▼                    Phase 6: Self-Review      │      │
│  Phase 3: Execution &           & Revision ──────────┘      │
│       Monitoring                 │                          │
│       │                          ▼                          │
│       ▼                    Phase 7: Submission               │
│  Phase 4: Analysis ─────► (feeds back to Phase 2 or 5)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
<!-- ascii-guard-ignore-end -->

---

## When To Use This Skill

Use this skill when:
- **Starting a new research paper** from an existing codebase or idea
- **Designing and running experiments** to support paper claims
- **Writing or revising** any section of a research paper
- **Preparing for submission** to a specific conference or workshop
- **Responding to reviews** with additional experiments or revisions
- **Converting** a paper between conference formats
- **Writing non-empirical papers** — theory, survey, benchmark, or position papers (see [Paper Types Beyond Empirical ML](#paper-types-beyond-empirical-ml))
- **Designing human evaluations** for NLP, HCI, or alignment research
- **Preparing post-acceptance deliverables** — posters, talks, code releases

## Core Philosophy

1. **Be proactive.** Deliver complete drafts, not questions. Scientists are busy — produce something concrete they can react to, then iterate.
2. **Never hallucinate citations.** AI-generated citations have ~40% error rate. Always fetch programmatically. Mark unverifiable citations as `[CITATION NEEDED]`.
3. **Paper is a story, not a collection of experiments.** Every paper needs one clear contribution stated in a single sentence. If you can't do that, the paper isn't ready.
4. **Experiments serve claims.** Every experiment must explicitly state which claim it supports. Never run experiments that don't connect to the paper's narrative.
5. **Commit early, commit often.** Every completed experiment batch, every paper draft update — commit with descriptive messages. Git log is the experiment history.

### Proactivity and Collaboration

**Default: Be proactive. Draft first, ask with the draft.**

| Confidence Level | Action |
|-----------------|--------|
| **High** (clear repo, obvious contribution) | Write full draft, deliver, iterate on feedback |
| **Medium** (some ambiguity) | Write draft with flagged uncertainties, continue |
| **Low** (major unknowns) | Ask 1-2 targeted questions via `clarify`, then draft |

| Section | Draft Autonomously? | Flag With Draft |
|---------|-------------------|-----------------|
| Abstract | Yes | "Framed contribution as X — adjust if needed" |
| Introduction | Yes | "Emphasized problem Y — correct if wrong" |
| Methods | Yes | "Included details A, B, C — add missing pieces" |
| Experiments | Yes | "Highlighted results 1, 2, 3 — reorder if needed" |
| Related Work | Yes | "Cited papers X, Y, Z — add any I missed" |

**Block for input only when**: target venue unclear, multiple contradictory framings, results seem incomplete, explicit request to review first.

---

## Phase 0: Project Setup

**Goal**: Establish the workspace, understand existing work, identify the contribution.

### Step 0.1: Explore the Repository

```bash
# Understand project structure
ls -la
find . -name "*.py" | head -30
find . -name "*.md" -o -name "*.txt" | xargs grep -l -i "result\|conclusion\|finding"
```

Look for:
- `README.md` — project overview and claims
- `results/`, `outputs/`, `experiments/` — existing findings
- `configs/` — experimental settings
- `.bib` files — existing citations
- Draft documents or notes

### Step 0.2: Organize the Workspace

Establish a consistent workspace structure:

```
workspace/
  paper/               # LaTeX source, figures, compiled PDFs
  experiments/         # Experiment runner scripts
  code/                # Core method implementation
  results/             # Raw experiment results (auto-generated)
  tasks/               # Task/benchmark definitions
  human_eval/          # Human evaluation materials (if needed)
```

### Step 0.3: Set Up Version Control

```bash
git init  # if not already
git remote add origin <repo-url>
git checkout -b paper-draft  # or main
```

**Git discipline**: Every completed experiment batch gets committed with a descriptive message. Example:
```
Add Monte Carlo constrained results (5 runs, Sonnet 4.6, policy memo task)
Add Haiku baseline comparison: autoreason vs refinement baselines at cheap model tier
```

### Step 0.4: Identify the Contribution

Before writing anything, articulate:
- **The What**: What is the single thing this paper contributes?
- **The Why**: What evidence supports it?
- **The So What**: Why should readers care?

> Propose to the scientist: "Based on my understanding, the main contribution is: [one sentence]. The key results show [Y]. Is this the framing you want?"

### Step 0.5: Create a TODO List

Use the `todo` tool to create a structured project plan:

```
Research Paper TODO:
- [ ] Define one-sentence contribution
- [ ] Literature review (related work + baselines)
- [ ] Design core experiments
- [ ] Run experiments
- [ ] Analyze results
- [ ] Write first draft
- [ ] Self-review (simulate reviewers)
- [ ] Revise based on review
- [ ] Submission prep
```

Update this throughout the project. It serves as the persistent state across sessions.

### Step 0.6: Estimate Compute Budget

Before running experiments, estimate total cost (API tokens, GPU hours, human-eval cost) and time, with 30-50% contingency for reruns. Log actual spend per experiment as you go, and fall back to pilot runs (1-2 seeds, subset of tasks) with cheaper models when budget is tight. See [references/project-setup-and-collaboration.md](references/project-setup-and-collaboration.md) for the budget checklist and a cost-logging code pattern.

### Step 0.7: Multi-Author Coordination

Most papers have 3-10 authors — agree on section ownership, a shared workspace (Overleaf, git, or both), notation/LaTeX conventions, and internal review rounds before anyone starts writing. See [references/project-setup-and-collaboration.md](references/project-setup-and-collaboration.md) for the full coordination checklist and LaTeX convention list.

---

## Phase 1: Literature Review

**Goal**: Find related work, identify baselines, gather citations.

### Step 1.1: Identify Seed Papers

Start from papers already referenced in the codebase:

```bash
# Via terminal:
grep -r "arxiv\|doi\|cite" --include="*.md" --include="*.bib" --include="*.py"
find . -name "*.bib"
```

### Step 1.2: Search for Related Work

**Load the `arxiv` skill** for structured paper discovery: `skill_view("arxiv")`. It provides arXiv REST API search, Semantic Scholar citation graphs, author profiles, and BibTeX generation.

Use `web_search` for broad discovery, `web_extract` for fetching specific papers:

```
# Via web_search:
web_search("[main technique] + [application domain] site:arxiv.org")
web_search("[baseline method] comparison ICML NeurIPS 2024")

# Via web_extract (for specific papers):
web_extract("https://arxiv.org/abs/2303.17651")
```

Additional search queries to try:

```
Search queries:
- "[main technique] + [application domain]"
- "[baseline method] comparison"
- "[problem name] state-of-the-art"
- Author names from existing citations
```

**Recommended**: Install **Exa MCP** for real-time academic search:
```bash
claude mcp add exa -- npx -y mcp-remote "https://mcp.exa.ai/mcp"
```

### Step 1.2b: Deepen the Search (Breadth-First, Then Depth)

A flat search (one round of queries) typically misses important related work. Run 2-3 rounds — broad (4-6 parallel queries covering different angles), then depth (follow-up queries from what Round 1 surfaced), then targeted (fill specific gaps like missing baselines or concurrent work) — stopping once a round returns mostly papers already in your collection (>80% overlap). Survey papers typically need 4-5 rounds. See [references/citation-workflow.md](references/citation-workflow.md#iterative-literature-search-breadth-then-depth) for the full round-by-round template and delegation pattern.

### Step 1.3: Verify Every Citation

**NEVER generate BibTeX from memory. ALWAYS fetch programmatically.**

For each citation, follow the mandatory 5-step process:

```
Citation Verification (MANDATORY per citation):
1. SEARCH → Query Semantic Scholar or Exa MCP with specific keywords
2. VERIFY → Confirm paper exists in 2+ sources (Semantic Scholar + arXiv/CrossRef)
3. RETRIEVE → Get BibTeX via DOI content negotiation (programmatically, not from memory)
4. VALIDATE → Confirm the claim you're citing actually appears in the paper
5. ADD → Add verified BibTeX to bibliography
If ANY step fails → mark as [CITATION NEEDED], inform scientist
```

```python
# Fetch BibTeX via DOI
import requests

def doi_to_bibtex(doi: str) -> str:
    response = requests.get(
        f"https://doi.org/{doi}",
        headers={"Accept": "application/x-bibtex"}
    )
    response.raise_for_status()
    return response.text
```

If you cannot verify a citation:

```latex
\cite{PLACEHOLDER_author2024_verify_this}  % TODO: Verify this citation exists
```

**Always tell the scientist**: "I've marked [X] citations as placeholders that need verification."

See [references/citation-workflow.md](references/citation-workflow.md) for complete API documentation and the full `CitationManager` class.

### Step 1.4: Organize Related Work

Group papers by methodology, not paper-by-paper:

**Good**: "One line of work uses X's assumption [refs] whereas we use Y's assumption because..."
**Bad**: "Smith et al. introduced X. Jones et al. introduced Y. We combine both."

---

## Phase 2: Experiment Design

**Goal**: Design experiments that directly support paper claims. Every experiment must answer a specific question.

### Step 2.1: Map Claims to Experiments

Create an explicit mapping:

| Claim | Experiment | Expected Evidence |
|-------|-----------|-------------------|
| "Our method outperforms baselines" | Main comparison (Table 1) | Win rate, statistical significance |
| "Effect is larger for weaker models" | Model scaling study | Monotonic improvement curve |
| "Convergence requires scope constraints" | Constrained vs unconstrained | Convergence rate comparison |

**Rule**: If an experiment doesn't map to a claim, don't run it.

### Step 2.2: Design Baselines

Strong baselines are what separates accepted papers from rejected ones. Reviewers will ask: "Did they compare against X?"

Standard baseline categories:
- **Naive baseline**: Simplest possible approach
- **Strong baseline**: Best known existing method
- **Ablation baselines**: Your method minus one component
- **Compute-matched baselines**: Same compute budget, different allocation

### Step 2.3: Define Evaluation Protocol

Before running anything, specify:
- **Metrics**: What you're measuring, direction symbols (higher/lower better)
- **Aggregation**: How results are combined across runs/tasks
- **Statistical tests**: What tests will establish significance
- **Sample sizes**: How many runs/problems/tasks

### Step 2.4: Write Experiment Scripts

Follow three patterns from successful research pipelines: **incremental saving** (persist each result immediately and skip already-completed work on restart, so crashes are safe to resume from), **artifact preservation** (save all intermediate outputs, not just final metrics, for post-hoc analysis), and **separation of concerns** (keep the experiment runner, baseline comparisons, judge/evaluation, statistical analysis, and chart generation as separate scripts). See [references/experiment-patterns.md](references/experiment-patterns.md) for the complete directory structure, the code for each pattern, cron monitoring, and error recovery.

### Step 2.5: Design Human Evaluation (If Applicable)

Many NLP, HCI, and alignment papers require human evaluation as primary or complementary evidence. Design this before running automated experiments — human eval often has longer lead times (IRB approval, annotator recruitment).

**When human evaluation is needed:**
- Automated metrics don't capture what you care about (fluency, helpfulness, safety)
- Your contribution is about human-facing qualities (readability, preference, trust)
- Reviewers at NLP venues (ACL, EMNLP) expect it for generation tasks

**Key design decisions:**

| Decision | Options | Guidance |
|----------|---------|----------|
| **Annotator type** | Expert, crowdworker, end-user | Match to what your claims require |
| **Scale** | Likert (1-5), pairwise comparison, ranking | Pairwise is more reliable than Likert for LLM outputs |
| **Sample size** | Per annotator and total items | Power analysis or minimum 100 items, 3+ annotators |
| **Agreement metric** | Cohen's kappa, Krippendorff's alpha, ICC | Krippendorff's alpha for >2 annotators; report raw agreement too |
| **Platform** | Prolific, MTurk, internal team | Prolific for quality; MTurk for scale; internal for domain expertise |

**Annotation guideline checklist:**
```
- [ ] Clear task description with examples (good AND bad)
- [ ] Decision criteria for ambiguous cases
- [ ] At least 2 worked examples per category
- [ ] Attention checks / gold standard items (10-15% of total)
- [ ] Qualification task or screening round
- [ ] Estimated time per item and fair compensation (>= local minimum wage)
- [ ] IRB/ethics review if required by your institution
```

**Reporting requirements** (reviewers check all of these):
- Number of annotators and their qualifications
- Inter-annotator agreement with specific metric and value
- Compensation details (amount, estimated hourly rate)
- Annotation interface description or screenshot (appendix)
- Total annotation time

See [references/human-evaluation.md](references/human-evaluation.md) for complete guide including statistical tests for human eval data, crowdsourcing quality control patterns, and IRB guidance.

---

## Phase 3: Experiment Execution & Monitoring

**Goal**: Run experiments reliably, monitor progress, recover from failures.

### Step 3.1: Launch Experiments

Use `nohup` for long-running experiments:

```bash
nohup python run_experiment.py --config config.yaml > logs/experiment_01.log 2>&1 &
echo $!  # Record the PID
```

**Parallel execution**: Run independent experiments simultaneously, but be aware of API rate limits. 4+ concurrent experiments on the same API will slow each down.

### Step 3.2: Set Up Monitoring (Cron Pattern)

For long-running experiments, set up periodic status checks: process check, log tail, results check, report in structured tables, commit on completion, and respond `[SILENT]` when nothing has changed since the last check. See [references/experiment-patterns.md](references/experiment-patterns.md#monitoring-cron-pattern) for the full cron prompt template, monitoring best practices, and an example report.

### Step 3.3: Handle Failures

Common failure modes — API rate limits/credit exhaustion, process crashes, timeouts, wrong model IDs, parallel slowdown — are all recoverable as long as scripts check for existing results and skip completed work, making re-runs safe. See [references/experiment-patterns.md](references/experiment-patterns.md#failure-recovery) for the full failure/recovery table, retry naming convention, and pre-flight checklist.

### Step 3.4: Commit Completed Results

After each experiment batch completes:

```bash
git add -A
git commit -m "Add <experiment name>: <key finding in 1 line>"
git push
```

### Step 3.5: Maintain an Experiment Journal

Git commits track file changes but not the **exploration tree** — the reasoning behind what to try next. Maintain a structured `experiment_journal.jsonl` (one entry per attempt: hypothesis, plan, config, result, analysis, next steps) alongside a code snapshot per experiment. This tree is invaluable for the Methods section ("we observed X, which motivated Y") and for honest failure reporting. See [references/experiment-patterns.md](references/experiment-patterns.md#experiment-journal-exploration-tree) for the full journal schema and path-selection guidance.

---

## Phase 4: Result Analysis

**Goal**: Extract findings, compute statistics, identify the story.

### Step 4.1: Aggregate Results

Write analysis scripts that load every result file from a batch, compute per-task and aggregate metrics, and generate summary tables. See [references/experiment-patterns.md](references/experiment-patterns.md#standard-analysis-script) for the `load_all_results` pattern and full statistical analysis script.

### Step 4.2: Statistical Significance

Always compute:
- **Error bars**: Standard deviation or standard error, specify which
- **Confidence intervals**: 95% CI for key results
- **Pairwise tests**: McNemar's test for comparing two methods
- **Effect sizes**: Cohen's d or h for practical significance

See [references/experiment-patterns.md](references/experiment-patterns.md) for complete implementations of McNemar's test, bootstrapped CIs, and Cohen's h.

### Step 4.3: Identify the Story

After analysis, explicitly answer:
1. **What is the main finding?** State it in one sentence.
2. **What surprised you?** Unexpected results often make the best papers.
3. **What failed?** Failed experiments can be the most informative. Honest reporting of failures strengthens the paper.
4. **What follow-up experiments are needed?** Results often raise new questions.

#### Handling Negative or Null Results

When your hypothesis was wrong or results are inconclusive, you have three options:

| Situation | Action | Venue Fit |
|-----------|--------|-----------|
| Hypothesis wrong but **why** is informative | Frame paper around the analysis of why | NeurIPS, ICML (if analysis is rigorous) |
| Method doesn't beat baselines but **reveals something new** | Reframe contribution as understanding/analysis | ICLR (values understanding), workshop papers |
| Clean negative result on popular claim | Write it up — the field needs to know | NeurIPS Datasets & Benchmarks, TMLR, workshops |
| Results inconclusive, no clear story | Pivot — run different experiments or reframe | Don't force a paper that isn't there |

**How to write a negative results paper:**
- Lead with what the community believes and why it matters to test it
- Describe your rigorous methodology (must be airtight — reviewers will scrutinize harder)
- Present the null result clearly with statistical evidence
- Analyze **why** the expected result didn't materialize
- Discuss implications for the field

**Venues that explicitly welcome negative results**: NeurIPS (Datasets & Benchmarks track), TMLR, ML Reproducibility Challenge, workshops at major conferences. Some workshops specifically call for negative results.

### Step 4.4: Create Figures and Tables

Figures: vector PDF, colorblind-safe palettes, self-contained captions, no in-figure title. Tables: `booktabs`, bold the best value per metric, direction symbols, consistent decimal precision. See [references/experiment-patterns.md](references/experiment-patterns.md#visualization-best-practices) for the SciencePlots setup, standard figure sizes, the Okabe-Ito palette, and complete chart examples, and [references/phase5-paper-drafting.md](references/phase5-paper-drafting.md#tables-and-figures) for the LaTeX table template.

### Step 4.5: Decide: More Experiments or Write?

| Situation | Action |
|-----------|--------|
| Core claims supported, results significant | Move to Phase 5 (writing) |
| Results inconclusive, need more data | Back to Phase 2 (design) |
| Unexpected finding suggests new direction | Back to Phase 2 (design) |
| Missing one ablation reviewers will ask for | Run it, then Phase 5 |
| All experiments done but some failed | Note failures, move to Phase 5 |

### Step 4.6: Write the Experiment Log (Bridge to Writeup)

Before moving to paper writing, create a structured `experiment_log.md` that bridges results to prose — contribution, per-experiment claim/setup/key-result/figures, a figures-to-sections table, failed experiments, and open questions. This is the single most important connective tissue between experiments and the writeup: without it, the writing agent has to re-derive the story from raw result files, a common source of hallucinated or misreported numbers. Commit it alongside the results it describes. See [references/experiment-patterns.md](references/experiment-patterns.md#experiment-log-bridge-to-writeup) for the complete template.

---

## Iterative Refinement: Strategy Selection

Any output in this pipeline — paper drafts, experiment scripts, analysis — can be iteratively refined. The autoreason research provides empirical evidence for when each refinement strategy works and when it fails.

### Quick Decision Table

| Your Situation | Strategy | Why |
|---------------|----------|-----|
| Mid-tier model + constrained task | **Autoreason** | Sweet spot. Generation-evaluation gap is widest. Baselines actively destroy weak model outputs. |
| Mid-tier model + open task | **Autoreason** with scope constraints added | Add fixed facts, structure, or deliverable to bound the improvement space. |
| Frontier model + constrained task | **Autoreason** | Wins 2/3 constrained tasks even at frontier. |
| Frontier model + unconstrained task | **Critique-and-revise** or **single pass** | Autoreason comes last. Model self-evaluates well enough. |
| Concrete technical task (system design) | **Critique-and-revise** | Direct find-and-fix loop is more efficient. |
| Template-filling task (one correct structure) | **Single pass** or **conservative** | Minimal decision space. Iteration adds no value. |
| Code with test cases | **Autoreason (code variant)** | Structured analysis of *why* it failed before fixing. Recovery rate 62% vs 43%. |
| Very weak model (Llama 8B class) | **Single pass** | Model too weak for diverse candidates. Invest in generation quality. |

The full methodology — the generation-evaluation gap, the autoreason loop architecture and roles, applying autoreason to paper drafts specifically, the failure taxonomy and recovery patterns, scope-constraint design, and the compute budget reference — lives in [references/autoreason-methodology.md](references/autoreason-methodology.md). Load it before running an actual autoreason loop.

---

## Phase 5: Paper Drafting

The complete drafting procedure (section-by-section order, LaTeX scaffolding, figure/table
conventions, abstract and intro formulas, related-work positioning) lives in
`references/phase5-paper-drafting.md` — load it with `read_file` when you reach this phase.
Pair it with `references/writing-guide.md` for prose-level style rules.

## Phase 6: Self-Review & Revision

**Goal**: Simulate the review process before submission. Catch weaknesses early.

### Step 6.1: Simulate Reviews (Ensemble Pattern)

Generate reviews from multiple independent perspectives (N=3-5, negative bias by default), then feed them to a meta-reviewer that aggregates consensus and resolves disagreements Area Chair-style, optionally with a 2-3 round reflection loop. Reviewing is best done with the strongest available model regardless of what wrote the paper, and few-shot calibration with 1-2 real published reviews from the target venue improves scoring.

Two complementary passes catch what text-only review misses: a **visual review** (VLM on the compiled PDF — figure quality, caption alignment, layout, table formatting, grayscale readability) and a **claim verification pass** (trace every factual claim to its supporting result file, flag untraceable ones as `[VERIFY]`, ideally via a fresh sub-agent to avoid confirmation bias).

See [references/reviewer-guidelines.md](references/reviewer-guidelines.md) for the complete ensemble-review and meta-review prompt templates, the visual review checklist, and the claim verification protocol.

### Step 6.2: Prioritize Feedback

After collecting reviews, categorize:

| Priority | Action |
|----------|--------|
| **Critical** (technical flaw, missing baseline) | Must fix. May require new experiments → back to Phase 2 |
| **High** (clarity issue, missing ablation) | Should fix in this revision |
| **Medium** (minor writing issues, extra experiments) | Fix if time allows |
| **Low** (style preferences, tangential suggestions) | Note for future work |

### Step 6.3: Revision Cycle

For each critical/high issue:
1. Identify the specific section(s) affected
2. Draft the fix
3. Verify the fix doesn't break other claims
4. Update the paper
5. Re-check against the reviewer's concern

### Step 6.4: Rebuttal Writing

When responding to actual reviews (post-submission), rebuttals are a distinct skill from revision: point-by-point, addressing every concern, leading with the strongest responses, concise, never defensive, and using `latexdiff` to show changes. See [references/reviewer-guidelines.md](references/reviewer-guidelines.md) for the full rebuttal template, a worked example, and guidance on when to accept criticism vs. push back.

### Step 6.5: Paper Evolution Tracking

Save snapshots at key milestones:
```
paper/
  paper.tex                    # Current working version
  paper_v1_first_draft.tex     # First complete draft
  paper_v2_post_review.tex     # After simulated review
  paper_v3_pre_submission.tex  # Final before submission
  paper_v4_camera_ready.tex    # Post-acceptance final
```

---

## Phase 7: Submission Preparation

**Goal**: Final checks, formatting, and submission.

### Step 7.1: Conference Checklist

Every venue has mandatory checklists. Complete them carefully — incomplete checklists can result in desk rejection.

See [references/checklists.md](references/checklists.md) for:
- NeurIPS 16-item paper checklist
- ICML broader impact + reproducibility
- ICLR LLM disclosure policy
- ACL mandatory limitations section
- Universal pre-submission checklist

### Steps 7.2-7.10: Anonymization, Compilation, Conversion, Camera-Ready, arXiv, Code Release

The rest of submission prep is mechanical but must be done in full: anonymization (no names, third-person self-citation, Anonymous GitHub for code links), formatting verification (page limits, vector figures, grayscale readability, booktabs tables), automated pre-compilation checks (chktex, citation/figure/label validation scripts), the final `latexmk`/`pdflatex`+`bibtex` compilation sequence and common LaTeX error fixes, venue-specific requirements (NeurIPS checklist, ICML Broader Impact, ICLR LLM disclosure, ACL Limitations, AAAI strict style, COLM framing), converting a paper between conference templates (never copy preambles; page-change table per venue pair), the camera-ready checklist (de-anonymize, acknowledgments, copyright), arXiv timing/category/versioning strategy, and packaging research code for release (repo structure, README template, pre-release checklist, anonymous code hosting).

See [references/submission-mechanics.md](references/submission-mechanics.md) for the complete checklists, scripts, and tables for every one of these steps.

---

## Phase 8: Post-Acceptance Deliverables

**Goal**: Maximize the impact of your accepted paper through presentation materials and community engagement — conference poster design and production, oral/spotlight talk structure and slide rules, and a blog post / social media / project page write-up timed to the camera-ready release.

See [references/post-acceptance-deliverables.md](references/post-acceptance-deliverables.md) for poster design principles and tools, talk duration/content by presentation type, slide design rules, and blog-post/thread/project-page guidance.

---

## Workshop & Short Papers

Workshop papers and short papers (e.g., ACL short papers, Findings papers) follow the same pipeline as a full empirical paper but with a lower page limit, a lighter/single-blind review process at workshops, and a different contribution bar (a novel direction or work-in-progress is enough; don't try to compress a long paper into 4 pages — write a more focused one). See [references/paper-types.md](references/paper-types.md#workshop-and-short-papers) for the full workshop-vs-main-conference comparison and ACL's long/short/Findings distinctions.

---

## Paper Types Beyond Empirical ML

The main pipeline above targets empirical ML papers. Other paper types need different structures and evidence standards, each fully detailed (including reproducibility/replication papers) in [references/paper-types.md](references/paper-types.md):

| Type | Structure | Contribution Is... | Best Venues |
|------|-----------|--------------------|-------------|
| **Theory** | Intro → Preliminaries → Main Results (theorems) → Proof Sketches → Discussion → Full Proofs (appendix) | A theorem, bound, or impossibility result — proofs are the evidence, not experiments | Any theory-friendly venue |
| **Survey / Tutorial** | Intro → Taxonomy/Organization → Detailed Coverage → Open Problems → Conclusion | The organization, synthesis, and identification of open problems, not new methods | TMLR (survey track), JMLR, Foundations and Trends in ML, ACM Computing Surveys |
| **Benchmark** | Intro → Task Definition → Dataset Construction → Baseline Evaluation → Analysis → Intended Use & Limitations | The benchmark itself — must fill a genuine evaluation gap, resist saturation, and measure what it claims (construct validity) | NeurIPS Datasets & Benchmarks, ACL (resource papers), LREC-COLING |
| **Position** | Intro → Background → Thesis/Argument → Supporting Evidence → Counterarguments → Implications | An argument, not a result — must engage seriously with counterarguments | ICML (position track), workshops, TMLR |

---

## Hermes Agent Integration

This skill is designed for the Hermes agent, using Hermes tools, delegation, scheduling, and memory for the full research lifecycle. It composes with other Hermes skills (`arxiv` for literature search, `subagent-driven-development` for parallel section drafting, `plan` for Phase 0 setup, `qmd` for local knowledge bases, `diagramming` and `data-science` for figures/analysis), and it supersedes `ml-paper-writing`.

See [references/hermes-agent-integration.md](references/hermes-agent-integration.md) for the complete related-skills table, the Hermes tool reference (`terminal`, `process`, `execute_code`, `delegate_task`, `todo`, `memory`, `cronjob`, `clarify`, cron `deliver:`), concrete tool-usage patterns (experiment monitoring, parallel section drafting, citation verification), state-management conventions for `memory`/`todo` including the session startup protocol, cron monitoring patterns including the `[SILENT]` protocol and deadline tracking, communication/reporting format, and the decision points that require human input (target venue, contribution framing, experiment priority, submission readiness) vs. those an agent should decide autonomously.

---

## Reviewer Evaluation Criteria

Reviewers check four universal dimensions — Quality (technical soundness, fair baselines), Clarity (reproducible writing, consistent notation), Significance (community impact), and Originality (new insight, not necessarily a new method) — scored on each venue's scale (e.g. NeurIPS's 6-point Strong Reject → Strong Accept scale). See [references/reviewer-guidelines.md](references/reviewer-guidelines.md) for the full per-venue scoring systems, common reviewer concerns, and rebuttal strategies.

---

## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Abstract too generic | Delete first sentence if it could prepend any ML paper. Start with your specific contribution. |
| Introduction exceeds 1.5 pages | Split background into Related Work. Front-load contribution bullets. |
| Experiments lack explicit claims | Add: "This experiment tests whether [specific claim]..." before each one. |
| Reviewers find paper hard to follow | Add signposting, use consistent terminology, make figure captions self-contained. |
| Missing statistical significance | Add error bars, number of runs, statistical tests, confidence intervals. |
| Scope creep in experiments | Every experiment must map to a specific claim. Cut experiments that don't. |
| Paper rejected, need to resubmit | See Conference Resubmission in Phase 7. Address reviewer concerns without referencing reviews. |
| Missing broader impact statement | See Step 5.10. Most venues require it. "No negative impacts" is almost never credible. |
| Human eval criticized as weak | See Step 2.5 and [references/human-evaluation.md](references/human-evaluation.md). Report agreement metrics, annotator details, compensation. |
| Reviewers question reproducibility | Release code (Step 7.9), document all hyperparameters, include seeds and compute details. |
| Theory paper lacks intuition | Add proof sketches with plain-language explanations before formal proofs. See [references/paper-types.md](references/paper-types.md). |
| Results are negative/null | See Phase 4.3 on handling negative results. Consider workshops, TMLR, or reframing as analysis. |

---

## Reference Documents

| Document | Contents |
|----------|----------|
| [references/writing-guide.md](references/writing-guide.md) | Gopen & Swan 7 principles, Perez micro-tips, Lipton word choice, Steinhardt precision, figure design |
| [references/citation-workflow.md](references/citation-workflow.md) | Citation APIs, Python code, CitationManager class, BibTeX management |
| [references/checklists.md](references/checklists.md) | NeurIPS 16-item, ICML, ICLR, ACL requirements, universal pre-submission checklist |
| [references/reviewer-guidelines.md](references/reviewer-guidelines.md) | Evaluation criteria, scoring, common concerns, rebuttal template |
| [references/sources.md](references/sources.md) | Complete bibliography of all writing guides, conference guidelines, APIs |
| [references/experiment-patterns.md](references/experiment-patterns.md) | Experiment design patterns, evaluation protocols, monitoring, error recovery |
| [references/autoreason-methodology.md](references/autoreason-methodology.md) | Autoreason loop, strategy selection, model guide, prompts, scope constraints, Borda scoring |
| [references/human-evaluation.md](references/human-evaluation.md) | Human evaluation design, annotation guidelines, agreement metrics, crowdsourcing QC, IRB guidance |
| [references/paper-types.md](references/paper-types.md) | Theory papers (proof writing, theorem structure), survey papers, benchmark papers, position papers, reproducibility papers, workshop/short papers |
| [references/phase5-paper-drafting.md](references/phase5-paper-drafting.md) | Full Phase 5 drafting procedure: section-by-section order, LaTeX scaffolding, abstract/intro formulas, related-work positioning |
| [references/submission-mechanics.md](references/submission-mechanics.md) | Anonymization, formatting verification, pre-compilation validation scripts, final compilation, venue-specific requirements, format conversion, camera-ready prep, arXiv strategy, code packaging |
| [references/post-acceptance-deliverables.md](references/post-acceptance-deliverables.md) | Conference poster design, talk/spotlight slide rules, blog post and project page guidance |
| [references/hermes-agent-integration.md](references/hermes-agent-integration.md) | Hermes tool reference, tool-usage patterns, `memory`/`todo` state management, cron monitoring, communication patterns, human-input decision points |
| [references/project-setup-and-collaboration.md](references/project-setup-and-collaboration.md) | Compute budget checklist and cost-logging code, multi-author coordination checklist and LaTeX conventions |

### LaTeX Templates

Templates in `templates/` for: **NeurIPS 2025**, **ICML 2026**, **ICLR 2026**, **ACL**, **AAAI 2026**, **COLM 2025**.

See [templates/README.md](templates/README.md) for compilation instructions.

### Key External Sources

**Writing Philosophy:**
- [Neel Nanda: How to Write ML Papers](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers)
- [Sebastian Farquhar: How to Write ML Papers](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/)
- [Gopen & Swan: Science of Scientific Writing](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf)
- [Lipton: Heuristics for Scientific Writing](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/)
- [Perez: Easy Paper Writing Tips](https://ethanperez.net/easy-paper-writing-tips/)

**APIs:** [Semantic Scholar](https://api.semanticscholar.org/api-docs/) | [CrossRef](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | [arXiv](https://info.arxiv.org/help/api/basics.html)

**Venues:** [NeurIPS](https://neurips.cc/Conferences/2025/PaperInformation/StyleFiles) | [ICML](https://icml.cc/Conferences/2025/AuthorInstructions) | [ICLR](https://iclr.cc/Conferences/2026/AuthorGuide) | [ACL](https://github.com/acl-org/acl-style-files)
