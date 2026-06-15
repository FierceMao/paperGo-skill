# Reproduction Report Templates

Use these templates for paper-ready or engineering-facing output.

## Reproduction Plan

```markdown
# Reproduction Plan: <Paper or Method>

## Objective

<One paragraph describing the reproduction target.>

## Evidence Available

| Artifact | Status | Notes |
|---|---|---|
| Paper | available/missing | |
| Code | available/missing | |
| Dataset | available/missing | |
| Results | available/missing | |
| Environment | available/missing | |

## Paper Protocol Coverage

| Requirement | Status | Evidence | Blocker Or Next Action |
|---|---|---|---|
| Dataset availability | | | |
| Split/preprocessing protocol | | | |
| Main method workflow | | | |
| Missing author-code reconstruction | | | |
| Metrics | | | |
| Output tables | | | |

## Reproducibility Card

| Field | Value | Provenance |
|---|---|---|
| Task | | source-stated/observed/inferred/missing |
| Dataset | | |
| Split | | |
| Metric | | |
| Baselines | | |
| Main method | | |
| Seeds | | |
| Hardware | | |

## Execution Ladder

1. Environment check:
2. Dataset lookup/download or missing-directory manifest:
3. Paper protocol JSON:
4. Main method import/smoke check:
5. Full paper main-method workflow:
6. Paper-required ablations/variants:
7. Protocol coverage check:
8. Report packaging:

## Risks And Missing Information

- 

## Next Actions

- 
```

## Result Synthesis

```markdown
# Experiment Result Summary

## Headline

<Answer-first summary of the result, with caveats.>

## Reproduction Status

- Status: ready/partial/blocked/reported-only/unverified
- Full-paper claim allowed: yes/no
- Reason:

## Protocol Coverage

<Insert output from check_protocol_coverage.py, or a manual equivalent.>

## Comparable Results

<Insert normalized metric table.>

## Interpretation

- Best supported claim:
- Tradeoff:
- Variance or uncertainty:
- Missing comparisons:
- Paper-vs-current-protocol mismatch:

## Paper-Ready Text

<A concise paragraph suitable for an experiment section.>

## Caveats

- 
```

## Reproduction Status Labels

- `ready`: enough artifacts exist to run or verify the next step.
- `partial`: useful evidence exists, but key items are missing.
- `blocked`: a required artifact, credential, dataset, or decision is missing.
- `reported-only`: numbers exist only in paper text, not in runnable outputs.
- `unverified`: outputs exist but metric protocol or data split is unclear.

## Reviewer-Grade Report Opening

Use this shape when auditing completed reproduction work:

```markdown
# Reproduction Audit: <Paper or Method>

## Blocking Findings

<List protocol or implementation mismatches first, with file/line evidence.>

## Non-Blocking Findings

<List README drift, environment pinning gaps, missing optional baselines, and presentation issues.>

## Code And Protocol Alignment

| Paper Requirement | Implementation | Evidence | Status |
|---|---|---|---|

## Result Validity

<State which claims are supported, partial, or unsupported.>
```
