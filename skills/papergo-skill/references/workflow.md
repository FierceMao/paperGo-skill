# Research Reproduction Workflow

Use this reference when a task needs more detail than the main `SKILL.md` workflow.

## 1. Reproducibility Card

Extract or create this card before planning experiments:

- Paper or method name
- Research task
- Dataset names and versions
- Split protocol
- Input/output shapes
- Evaluation metrics
- Baselines
- Main model components
- Training objective
- Optimizer and schedule
- Hardware and runtime
- Random seeds and repetitions
- Reported headline numbers
- Code and data availability
- Missing information

Each field should be marked as:

- `source-stated`: directly present in paper/code.
- `observed`: found in files or outputs.
- `inferred`: reasonable inference from artifacts.
- `missing`: not available.
- `needs-user`: cannot proceed safely without user input.

## 2. Dataset Resolution Protocol

Use this before writing final experiment commands.

1. List every dataset named by the paper, including variants, imbalance ratios, preprocessing, and source if stated.
2. Search local files first. Then use official dataset sources, author links, benchmark repositories, or paper supplementary links.
3. Download data only when it is public, license-compatible, reasonably sized, and approved when network or large downloads are required.
4. If a dataset cannot be found, create the expected directory and a manifest entry with:
   - `status: missing`
   - attempted sources or queries
   - why it is unavailable
   - exact recommendation for obtaining it
5. Do not substitute synthetic or adjacent datasets in the paper workflow. Put synthetic checks in a separate `mechanism_checks/` or clearly labeled experiment group.

## 3. Missing Author-Code Reconstruction

When author code imports missing modules or leaves algorithm pieces undefined:

1. Read the paper algorithm, equations, and method text for the missing piece.
2. Read caller/callee context in author code.
3. Implement the smallest paper-faithful helper that satisfies the caller contract.
4. Put uncertain assumptions in compact, replaceable functions/classes with typed parameters.
5. Add comments only where they identify a paper-derived assumption or uncertainty.
6. Record a traceability table: missing symbol, paper evidence, author-code caller, implementation location, confidence.
7. If a helper cannot be implemented or only approximated, create a stub with a clear exception or conservative fallback, plus a TODO that identifies the exact paper evidence still needed.

## 4. Minimal Reproduction Ladder

Prefer this order:

1. Environment import or compile check.
2. Dataset availability and split verification.
3. Evaluation-only path on a tiny paper dataset slice if available.
4. Smallest paper-faithful main-method run.
5. Full paper main-method workflow: datasets, preprocessing, splits, metric definitions, and output tables.
6. Paper-required variants or ablations for the main method.
7. Optional baselines requested by the user.
8. Multi-seed or sensitivity checks.
9. Protocol coverage check and paper-ready report.

Do not call a synthetic smoke test a reproduction. It is only a mechanism check.

## 5. Experiment Audit Questions

- Is there a single command for training?
- Is there a single command for evaluation?
- Are dataset paths configurable?
- Are random seeds configurable?
- Are metrics computed by code or copied into notes?
- Are output directories timestamped or overwritten?
- Are class/sample counts reported?
- Are train/validation/test splits disjoint?
- Are dependencies pinned?
- Are GPU/CPU requirements stated?
- Does the result table cover every paper dataset that was available?
- Does the code implement the paper main method without unmarked convenience deviations?
- Are missing author-code reconstructions traceable to paper text or author-code call sites?

## 6. Result Synthesis Rules

- Compare only runs with matching dataset, split, metric, and preprocessing.
- Preserve denominators and sample counts.
- If multiple seeds exist, report mean and standard deviation.
- If only one run exists, say it is a single-run result.
- For imbalanced data, prefer macro/per-class metrics and confusion matrix.
- For detection, include IoU thresholds and mAP variant.
- For segmentation, include Dice/IoU definitions if available.
- Separate paper-workflow results from synthetic mechanism checks.
- State whether a missing dataset or reconstructed helper blocks full reproduction.

## 7. Writing Rules

- Use "the artifacts show" for observed facts.
- Use "the paper states" for paper claims.
- Use "likely" only for clearly marked inference.
- Avoid "proves", "guarantees", or "state-of-the-art" unless directly supported.
- Avoid "full reproduction" unless the protocol coverage check passes.
