---
name: paper-workflow-orchestrator
description: Run or resume the complete Standard mathematical-modeling workflow from contest files through reproducible evidence, adaptive formal writing, native-equation Word output, and final render QA. Use as the entry point for complete-paper requests.
---

# MathModel Standard Orchestrator

Use this skill as the only entry router for a complete competition-paper task. Standard targets strong models that can maintain a long evidence chain and execute tools reliably while keeping cost controlled. It does not use Pro multi-agent tournaments or approval checkpoints.

## Start Or Resume

From the contest project root, run:

```bash
python .trae/skills/paper-workflow-orchestrator/scripts/preflight_check.py
python .trae/skills/paper-workflow-orchestrator/scripts/workflow_profile.py --show
python .trae/skills/paper-workflow-orchestrator/scripts/workflow_guard.py --status
```

Read the active workflow profile before routing S1-S5. If `paper_output/context/workflow_profile.json` is absent, `--show` returns implicit `standard` without creating a file. If it reports `beginner-guided`, treat the profile as an execution contract for S1-S5, not merely as explanatory prose.

Read `paper_output/qa/workflow_guard_report.json` and follow `recommended_skill` plus `next_action`. The current files and hashes override conversational memory.

Do not run downstream skills before their guard requirement passes. After a child skill finishes, return here, re-read the active workflow profile, and evaluate status again.

## Active Workflow Profile Contract

When the active profile is `beginner-guided`, enforce all of the following while preserving ordinary Standard delivery:

- **S1:** explain each question in plain language; identify knowns, unknowns, constraints, and the main difficulty before proposing complex methods.
- **S2:** choose a runnable baseline for every question first; declare inputs, outputs, metrics, candidate upgrade models, and explicit upgrade triggers. The candidate upgrade is not yet the adopted main model.
- **S3:** prepare data and visualization work so baseline diagnostics and the predeclared evaluation metrics can actually be computed.
- **S4:** implement the baseline path first. Keep any more complex candidate model behind a separate upgrade hook or clearly separated code path so the baseline remains reproducible.
- **S5:** run the baseline before any upgrade. Upgrade only when at least one declared trigger is supported by real results, such as an inadequate baseline, systematic residuals, constraint violation, instability, or a justified measurable gain. If no trigger is supported, keep the baseline. If an upgrade is tried, compare viable models on accuracy, stability, interpretability, and implementation cost.
- After each major S1-S5 stage, give a beginner-facing explanation of at most 8 lines covering what was done, why, files produced, and what will be checked next.

`beginner-guided` never weakens or bypasses S6 evidence validation, S7 formal authoring, or S8 Word/PDF render validation. Never invent an upgrade trigger, baseline result, comparison result, or successful run.

When the active profile is `standard`, follow the ordinary S0-S8 behavior below without adding beginner-only gates.

## S0-S8

### S0 Input Admission

`preflight_check.py` inventories `problem_files/`, hashes every input, checks runtime dependencies, prepares `paper_output/`, and rejects mixed MathModel editions. Required outputs:

- `paper_output/preflight_report.json`
- `paper_output/input_manifest.json`
- `paper_output/OUTPUT_LAYOUT.md`

### S1 Problem Analysis

Use `$problem-doc-model-selector` to create `paper_output/step1/problem_analysis.json`. Every question, attachment, field, objective, constraint, ambiguity, and required output must be traceable.

### S2 Model And Rubric Route

Use `$modeling-paper-rubric-and-model-selector`. Produce:

- `paper_output/plan/model_route.json`
- `paper_output/plan/rubric_alignment.json`
- `paper_output/plan/scoring_strategy.md`

Use `$authoritative-data-harvester` only when public external data is necessary. Keep source identity and retrieval notes.

### S3 Data And Visualization Plan

Use `$data-cleaning-and-visualization`. Read only files classified in the input manifest and produce a fresh load report, data plan, visualization plan, figure index, and cleaned data. Contest-specific code belongs under `paper_output/code/`, never inside installed skills.

### S4 Reproducible Model Code

Use `$model-code-and-result-generator` to write question-specific code under `paper_output/code/modeling/`, including `run_modeling.py` and per-question modules. Code must emit machine-readable result contracts.

### S5 Real Execution

Run the modeling code. Preserve script, input, output, exit-code, size, and SHA-256 records in `paper_output/results/run_manifest.json`. Required evidence includes model results, finite metrics, conclusions, tables, and usable figures. Draft placeholders do not count.

### S6 Evidence Gate

Use `$quality-assurance-auditor` and run official evidence validation:

```bash
python .trae/skills/quality-assurance-auditor/scripts/evidence_gate.py --mode official
```

Do not enter formal writing until `paper_output/qa/evidence_gate_report.json` is PASS and all recorded inputs are still fresh.

### S7 Adaptive Formal Writing

Use `$paper-formal-writer` as the sole formal author:

```bash
python .trae/skills/paper-formal-writer/scripts/build_paper_outline.py
python .trae/skills/paper-formal-writer/scripts/prepare_authoring.py --mode auto
```

Normal competition papers use complete-section drafting, possibly over several turns. Preserve the formal writer's declared competition scope; a short report needs an explicit user-requested scope and reason. Audit every draft with `validate_authoring.py --section`; global repeated failure falls back to section mode. A section’s second repeated category creates a `micro-repair` route; only then may `$paper-micro-unit-generator` repair the queued location. The third repeated category blocks S7 and suggests Lite without switching automatically.

After every active unit passes:

```bash
python .trae/skills/paper-formal-writer/scripts/assemble_sections.py
python .trae/skills/paper-formal-writer/scripts/validate_authoring.py --assembled
```

The Agent must then globally revise the full assembly into `paper_output/final_paper_source.md`; a copy-only promotion is rejected. Finish with:

```bash
python .trae/skills/paper-formal-writer/scripts/validate_authoring.py --final
python .trae/skills/paper-formal-writer/scripts/format_formal_docx.py
```

### S8 Format And Render Gate

Run:

```bash
python .trae/skills/paper-formal-writer/scripts/check_paper_format.py --render required
```

Delivery requires a fresh PASS in `paper_output/format_check_report.json`. Fix the reported source, formula, citation, figure/table, DOCX, pagination, or PDF issue and rerun; never edit the report to force PASS.

## Formal Outputs

```text
paper_output/plan/writing_plan.json
paper_output/context/authoring_state.json
paper_output/qa/draft_audit.json
paper_output/qa/repair_queue.json
paper_output/drafts/sections/*.md
paper_output/drafts/assembled_draft.md
paper_output/final_paper_source.md
paper_output/final_paper.docx
paper_output/format_check_report.json
```

Legacy micro-unit and quickstart outputs remain under `paper_output/drafts/legacy/` and `paper_output/quickstart/`. They can never satisfy S7.

## Non-Negotiable Invariants

- Never invent model results, data sources, successful runs, citations, or validation.
- Every critical numeric claim must trace to current machine-readable evidence.
- Any upstream hash change invalidates dependent S6-S8 reports.
- Each included figure/table must exist, be indexed, cited, and interpreted.
- Formal formulas must become editable Word OMML; no screenshot or plain-text substitution.
- Do not expose skill names, guard commands, or workflow prose in the paper body.
- Do not write contest-specific code into installed skill directories.
- Install one MathModel edition per contest project.

## Recovery

For an interrupted or long task:

```bash
python .trae/skills/paper-workflow-orchestrator/scripts/workflow_profile.py --show
python .trae/skills/paper-workflow-orchestrator/scripts/workflow_guard.py --status
python .trae/skills/context-memory-keeper/scripts/update_workflow_memory.py
```

Read the active workflow profile, guard report, current stage contracts, and `paper_output/context/workflow_memory.json`; continue from the first failing stage instead of replaying completed work.