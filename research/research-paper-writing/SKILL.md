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
- **High confidence**: Write full draft, deliver, iterate on feedback.
- **Medium confidence**: Write draft with flagged uncertainties.
- **Low confidence**: Ask 1-2 targeted questions via `clarify`, then draft.
Draft Abstract, Intro, Methods, Experiments, and Related Work autonomously by default, flagging assumptions. Block for human input only when target venue is ambiguous or framings contradict. See [references/project-setup-and-collaboration.md](references/project-setup-and-collaboration.md).

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

### Step 0.5: Create a Structured Plan
Track persistent milestones across sessions via `todo`: one-sentence contribution, literature review, experiment design, execution, analysis, first draft, simulated review, revisions, and submission prep.

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
```
If ANY step fails → mark as [CITATION NEEDED], inform scientist
```

See [references/citation-workflow.md](references/citation-workflow.md) for DOI content negotiation scripts and the complete `CitationManager` class.

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

Many NLP, HCI, and alignment papers require human evaluation as primary or complementary evidence. Design this before running automated experiments to account for IRB lead times, annotator recruitment (Prolific/MTurk), Likert vs pairwise scales, power analysis sample sizes, and Krippendorff's alpha agreement metrics.

See [references/human-evaluation.md](references/human-evaluation.md) for complete guidelines including statistical tests for human eval data, crowdsourcing quality control patterns, annotation checklists, and IRB guidance.

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

When hypotheses fail or results are inconclusive: (1) if the failure mechanism is informative, reframe the contribution around analysis (welcomed by TMLR, ICLR, or NeurIPS Datasets & Benchmarks); (2) if cleanly refuting a popular claim, document the negative finding with rigorous statistical proof; (3) if results are simply inconclusive, pivot experiments rather than forcing a weak narrative. See [references/experiment-patterns.md](references/experiment-patterns.md) for handling null results.

### Step 4.4: Create Figures and Tables

Figures: vector PDF, colorblind-safe palettes, self-contained captions, no in-figure title. Tables: `booktabs`, bold the best value per metric, direction symbols, consistent decimal precision. See [references/experiment-patterns.md](references/experiment-patterns.md#visualization-best-practices) for the SciencePlots setup, standard figure sizes, the Okabe-Ito palette, and complete chart examples, and [references/phase5-paper-drafting.md](references/phase5-paper-drafting.md#tables-and-figures) for the LaTeX table template.

### Step 4.5: Decide: More Experiments or Write?

If core claims are supported and statistically significant, proceed to Phase 5. If results are inconclusive or a critical ablation is missing, return to Phase 2.

### Step 4.6: Write the Experiment Log (Bridge to Writeup)

Before moving to paper writing, create a structured `experiment_log.md` that bridges results to prose — contribution, per-experiment claim/setup/key-result/figures, a figures-to-sections table, failed experiments, and open questions. This prevents hallucinated or misreported numbers. Commit it alongside the results it describes. See [references/experiment-patterns.md](references/experiment-patterns.md#experiment-log-bridge-to-writeup) for the complete template.

---

## Iterative Refinement: Strategy Selection

Any output in this pipeline can be iteratively refined. Use **Autoreason** for mid-tier models on constrained tasks (widest generation-evaluation gap) and code with tests; use **Critique-and-revise** for frontier models on unconstrained tasks and concrete system designs.

The full methodology lives in [references/autoreason-methodology.md](references/autoreason-methodology.md). Load it before running an actual autoreason loop.

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

Categorize reviews into Critical (technical flaws/baselines requiring Phase 2 fixes), High (clarity/ablations for this revision), Medium (minor writing), and Low (future work).

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

## Workshop & Non-Empirical Paper Types

Workshop papers, short papers (ACL Findings), theory papers (theorems and proof sketches), survey/tutorial papers, benchmark/dataset papers, and position papers follow distinct structural and evidence standards. See [references/paper-types.md](references/paper-types.md) for full structural blueprints, contribution standards, and venue mappings.

---

## Hermes Agent Integration

This skill is designed for the Hermes agent, using Hermes tools, delegation, scheduling, and memory for the full research lifecycle. It composes with other Hermes skills (`arxiv` for literature search, `subagent-driven-development` for parallel section drafting, `plan` for Phase 0 setup, `qmd` for local knowledge bases, `diagramming` and `data-science` for figures/analysis), and it supersedes `ml-paper-writing`.

See [references/hermes-agent-integration.md](references/hermes-agent-integration.md) for the complete related-skills table, tool reference, state-management conventions, and decision points requiring human input.

---

## Reviewer Evaluation Criteria & Common Issues

Reviewers evaluate papers across Quality, Clarity, Significance, and Originality. Before submission, ensure:
- Abstracts lead immediately with the core contribution.
- Introductions stay under 1.5 pages with clear signposting.
- Every experiment maps to an explicit hypothesis with statistical significance tests and error bars.
- Figures have self-contained captions and vector resolution.
- Code and hyperparameter artifacts are packaged cleanly.

See [references/reviewer-guidelines.md](references/reviewer-guidelines.md) for full per-venue scoring systems, common concerns, and rebuttal strategies.

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

Templates in `templates/` for: **NeurIPS 2025**, **ICML 2026**, **ICLR 2026**, **ACL**, **AAAI 2026**, **COLM 2025**. See [templates/README.md](templates/README.md) for compilation instructions.

See [references/sources.md](references/sources.md) for the complete external bibliography, writing guides, and API documentation.
