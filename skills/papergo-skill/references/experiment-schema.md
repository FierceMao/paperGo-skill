# Experiment Metadata And Table Schema

Use this reference when creating or normalizing experiment records.

## Recommended Run Metadata

```json
{
  "run_id": "string",
  "method": "string",
  "dataset": "string",
  "split": "train|val|test|custom",
  "seed": 0,
  "config": "path/to/config.yaml",
  "checkpoint": "path/to/model.pt",
  "commit": "git-sha-if-known",
  "hardware": "gpu/cpu description",
  "started_at": "ISO timestamp",
  "finished_at": "ISO timestamp",
  "notes": "free text"
}
```

## Paper Protocol JSON

Create this file before implementing a full paper workflow. A compact version is enough, but every entry must include provenance.

```json
{
  "paper": {
    "title": "string",
    "doi": "string-or-empty",
    "source": "paper|supplement|author-code|inferred"
  },
  "datasets": [
    {
      "name": "string",
      "source": "url-or-local-path-or-empty",
      "status": "available|downloaded|missing|gated|too-large|unknown",
      "split_protocol": "string",
      "preprocessing": "string",
      "provenance": "source-stated|author-code-observed|inferred|missing",
      "advice": "how to obtain or verify when missing"
    }
  ],
  "main_method": {
    "name": "string",
    "workflow_steps": [
      {
        "step": "string",
        "paper_evidence": "section/equation/algorithm",
        "implementation": "path:function-or-class",
        "status": "implemented|stub|missing|approximate"
      }
    ],
    "forbidden_deviations": [
      "convenience changes that must not enter the main reproduction path"
    ]
  },
  "missing_author_code": [
    {
      "symbol": "string",
      "caller": "path:line-or-function",
      "paper_evidence": "section/equation/algorithm",
      "implementation": "path:function-or-class",
      "confidence": "high|medium|low|blocked",
      "replacement_notes": "how a human can modify this"
    }
  ],
  "required_results": {
    "methods": ["main-method-name"],
    "metrics": ["auc", "gmean", "f1"],
    "folds": 5,
    "seeds": ["paper-stated-or-list"],
    "must_cover_all_available_datasets": true
  }
}
```

Use `scripts/check_protocol_coverage.py protocol.json results.csv --format markdown` after running experiments.

## Recommended Classification Metrics

- `n_samples`
- `n_classes`
- `accuracy`
- `macro_f1`
- `weighted_f1`
- `precision_macro`
- `recall_macro`
- `auc`
- `gmean`
- `balanced_accuracy`
- `per_class_precision`
- `per_class_recall`
- `minority_recall`
- `majority_recall`
- `confusion_matrix`

For class imbalance, do not rely on accuracy alone.

## Recommended Detection Metrics

- `map`
- `map_50`
- `map_75`
- `mar`
- `iou_thresholds`
- `n_images`
- `n_instances`
- `per_class_ap`

Always state the benchmark protocol if known.

## Recommended Segmentation Metrics

- `miou`
- `dice`
- `pixel_accuracy`
- `boundary_f1`
- `n_images`
- `per_class_iou`

## Paper Table Columns

Use the narrowest table that supports the claim.

### Baseline Table

| Method | Dataset | Split | Metric | Score | Seeds | Notes |
|---|---|---|---|---:|---:|---|

### Ablation Table

| Variant | Changed Component | Metric | Delta | Notes |
|---|---|---:|---:|---|

### Multi-Dataset Table

| Method | Dataset A | Dataset B | Dataset C | Avg. |
|---|---:|---:|---:|---:|

### Protocol Coverage Table

| Requirement | Required | Observed | Status | Evidence |
|---|---|---|---|---|

Use statuses: `covered`, `partial`, `missing`, `blocked`, `not-applicable`.

## Required Caveats

Add caveats when:

- seed count is 1 or unknown;
- dataset split is inferred;
- preprocessing differs between methods;
- metrics are copied from logs without recomputation;
- class counts are missing;
- hardware/runtime is not comparable;
- a result file lacks timestamps or run IDs.
- paper datasets are replaced by synthetic mechanism checks;
- author-code helpers are reconstructed with medium or low confidence;
- any main-method step is a stub, approximate, or outside the paper logic;
- README commands or output paths differ from actual artifacts.
