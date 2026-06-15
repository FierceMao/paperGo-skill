---
name: papergo-skill
description: Use for reviewer-grade research paper reproduction and experiment-package analysis: extracting paper protocols, locating/downloading available datasets, auditing author code, reconstructing missing code only from paper evidence, checking implementation/protocol coverage, running main-method experiments, normalizing metrics, and producing evidence-backed reproduction reports. Trigger when users mention reproducing a paper, author repositories, missing code, datasets, baselines, ablations, result tables, arXiv/PDF method extraction, experiment reproducibility, or reviewer-style reproduction audits. Do not use for general literature summaries without reproduction or experiment-planning intent.
---

# paperGo Skill

## Purpose

Help Codex turn a paper, repository, or experiment folder into a reproducible research plan and evidence-backed report. Favor source-grounded extraction, deterministic inspection, and clear uncertainty over polished but unsupported claims.

## Hard Rules

- Treat paper text, official supplementary material, and author code as the authority, in that order when they conflict. Label every implementation decision as source-stated, author-code-observed, inferred, or missing.
- If the paper names public datasets, search local artifacts and official/public sources. Download datasets that are reasonably available and not large or gated; otherwise create the expected directory/manifest only, record the failed lookup, and give concrete acquisition advice.
- Never intentionally deviate from the paper method or add convenience extensions without marking them as non-reproduction extras and keeping them outside the main method path. The default implementation must follow the paper logic.
- If author code is missing modules or functions, reconstruct them only after reading the relevant paper algorithm, equations, and surrounding author code. Put uncertain parts behind small, documented functions/classes with clear names, parameters, and comments so a human can replace them easily.
- Do not claim full reproduction unless paper datasets, split protocol, main method, metric definitions, commands, and outputs are all present. If only synthetic or partial checks are run, call it a mechanism check or partial reproduction.
- Reproduce the paper's complete main-method experimental workflow first. Do not require all third-party baselines unless the user asks; do include the paper's datasets, preprocessing, splits, metrics, main method variants/ablations needed to support the paper's own claim.
- Keep README and run instructions synchronized with actual scripts, output paths, and status labels.

## Core Workflow

1. Identify the task type:
   - Paper-to-plan: paper PDF, arXiv page, README, or method draft.
   - Experiment audit: code/data/result folder.
   - Result synthesis: CSV/JSON/log outputs, ablations, baseline comparisons.
   - Paper-ready reporting: metrics table, figure list, reproducibility caveats.
2. Inspect available artifacts before reasoning:
   - Use `scripts/inspect_repro_package.py` for folders.
   - Use `scripts/normalize_results.py` for result CSV/JSON files.
   - Use `scripts/check_protocol_coverage.py` when a paper protocol JSON and result table exist.
   - Read only the relevant reference file after the task shape is known.
3. Extract reproducibility requirements:
   - Task, dataset, split protocol, model, training setup, metrics, baselines, ablations, hardware, seeds, and reported numbers.
   - Mark each item as source-stated, inferred, missing, or needs user confirmation.
4. Resolve datasets:
   - Create a `data_manifest` with dataset name, source URL/path, access status, checksum if available, license/access notes, and acquisition advice for missing data.
   - Download available datasets only when size, license, and network permissions are acceptable.
   - Create empty expected directories only for unavailable or gated data, and never silently substitute unrelated datasets.
5. Build an execution plan:
   - Start with import checks and a smallest paper-faithful run.
   - Implement the paper's main workflow before optional baselines.
   - Add ablations only after the main method path is executable.
   - Include commands, expected outputs, and validation checks.
6. Report with provenance:
   - Separate observed facts from interpretation.
   - Include metric denominators or sample counts whenever available.
   - State missing artifacts and blocked assumptions plainly.

## Resource Map

- `scripts/inspect_repro_package.py`: Scan a project or experiment folder and emit JSON or Markdown with papers, configs, data manifests, code files, result files, environment files, and likely risks.
- `scripts/normalize_results.py`: Load CSV/JSON result files, detect metric columns, group by model/dataset/split/seed when present, and emit Markdown/CSV/LaTeX-style summaries.
- `scripts/check_protocol_coverage.py`: Compare a paper protocol JSON against a result CSV/JSON and report missing datasets, methods, metrics, folds, and seed evidence.
- `references/workflow.md`: Read for end-to-end paper reproduction, experiment audit, and result synthesis workflow details.
- `references/report-template.md`: Read when the user asks for a paper-ready report, reproduction plan, ablation summary, or reviewer-facing explanation.
- `references/experiment-schema.md`: Read when designing metadata, result tables, baseline matrices, or reproducibility checklists.
- `references/reviewer-grade-checklist.md`: Read before finalizing any reproduction claim or when asked to audit a reproduction.

## Task Patterns

### Paper-To-Plan

Use when the user gives a paper, arXiv URL, PDF, method section, or repository and asks how to reproduce it.

1. Extract the reproducibility card from the paper or README.
2. Extract a protocol JSON using `references/experiment-schema.md`.
3. Identify and resolve datasets before proposing final commands.
4. Audit author code for missing pieces and map every missing piece to paper evidence before implementing it.
5. Produce a staged plan:
   - Stage 0: environment and data availability.
   - Stage 1: smallest paper-faithful main-method run.
   - Stage 2: full paper workflow for the main method.
   - Stage 3: ablations and sensitivity checks.
   - Stage 4: paper-ready result packaging.

### Experiment Audit

Use when the user provides a folder.

Run:

```bash
python scripts/inspect_repro_package.py <project-or-experiment-folder> --format markdown
```

Then inspect files called out by the script before making conclusions. Prioritize `README`, environment files, configs, dataset manifests, training scripts, evaluation scripts, and result tables.

### Result Synthesis

Use when the user provides experiment outputs.

Run:

```bash
python scripts/normalize_results.py <results.csv-or-json> --format markdown
```

Use the normalized output as evidence, then explain:

- best and second-best methods,
- per-dataset or per-class tradeoffs,
- variance across seeds if present,
- missing denominators or incomplete comparisons,
- which claims are safe for a paper table.

### Paper-Ready Report

Use `references/report-template.md`. Keep the report concise and evidence-backed. Avoid inventing numbers, implementation details, datasets, or citations.

### Reviewer-Grade Audit

Use `references/reviewer-grade-checklist.md`. Lead with blocking protocol or implementation mismatches. Include file/line references when auditing code.

## Validation Rules

- Do not claim an experiment is reproduced unless code, data, command, metric, and output evidence are all present or explicitly provided.
- Do not compare methods unless metrics share the same dataset, split, and evaluation protocol.
- Always flag missing seeds, missing standard deviations, unclear splits, absent class counts, and missing environment details.
- Always flag missing paper datasets, synthetic substitutions, incomplete main-method workflow, unverified helper reconstruction, and any output generated from non-paper settings.
- For imbalanced classification, prefer per-class metrics, macro metrics, confusion matrix, and sample counts over accuracy alone.
- For object detection or segmentation, include IoU/mAP threshold details when available.
- For paper writing, label all generated prose as interpretation unless it directly cites observed artifacts.

## Safety And Boundaries

- Do not fabricate paper results, citations, datasets, command outputs, or hardware details.
- Do not download large datasets or install heavy dependencies without user approval.
- Do not overwrite experiment outputs; write derived summaries to new files only when the user asks.
- Treat unpublished papers, private datasets, and proprietary experiment logs as sensitive.
