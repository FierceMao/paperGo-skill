#!/usr/bin/env python3
"""Check whether experiment outputs cover a paper reproduction protocol.

The protocol is a JSON file shaped by references/experiment-schema.md. The
result file may be CSV, TSV, or JSON rows. This script does not validate model
quality; it checks coverage evidence: datasets, methods, metrics, folds, seeds,
and unavailable dataset notes.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    if suffix == ".tsv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle, delimiter="\t"))
    if suffix == ".json":
        data = load_json(path)
        if isinstance(data, list):
            return [row for row in data if isinstance(row, dict)]
        if isinstance(data, dict):
            for key in ("rows", "results", "metrics", "data"):
                value = data.get(key)
                if isinstance(value, list):
                    return [row for row in value if isinstance(row, dict)]
            if all(not isinstance(v, (list, dict)) for v in data.values()):
                return [data]
    raise SystemExit(f"Unsupported result file: {path}")


def lower_key_map(rows: list[dict[str, Any]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in rows:
        for key in row:
            out.setdefault(key.lower(), key)
    return out


def values(rows: list[dict[str, Any]], column: str | None) -> set[str]:
    if not column:
        return set()
    return {str(row.get(column, "")).strip() for row in rows if str(row.get(column, "")).strip()}


def metric_columns(rows: list[dict[str, Any]], key_map: dict[str, str]) -> set[str]:
    observed = set()
    metric_name_col = key_map.get("metric")
    if metric_name_col:
        observed.update(v.lower() for v in values(rows, metric_name_col))
    for key in key_map:
        observed.add(key)
    return observed


def status(ok: bool, partial: bool = False) -> str:
    if ok:
        return "covered"
    if partial:
        return "partial"
    return "missing"


def check(protocol: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    key_map = lower_key_map(rows)
    dataset_col = key_map.get("dataset")
    method_col = key_map.get("method") or key_map.get("algorithm") or key_map.get("model")
    fold_col = key_map.get("fold") or key_map.get("split")
    seed_col = key_map.get("seed") or key_map.get("random_state")

    observed_datasets = values(rows, dataset_col)
    observed_methods = values(rows, method_col)
    observed_metrics = metric_columns(rows, key_map)
    observed_folds = values(rows, fold_col)
    observed_seeds = values(rows, seed_col)

    protocol_datasets = protocol.get("datasets", [])
    available_statuses = {"available", "downloaded"}
    required_datasets = [
        str(item.get("name", ""))
        for item in protocol_datasets
        if item.get("status") in available_statuses and item.get("name")
    ]
    missing_datasets = [
        str(item.get("name", ""))
        for item in protocol_datasets
        if item.get("status") not in available_statuses and item.get("name")
    ]

    required_results = protocol.get("required_results", {})
    required_methods = [str(m) for m in required_results.get("methods", [])]
    main_name = protocol.get("main_method", {}).get("name")
    if main_name and main_name not in required_methods:
        required_methods.append(str(main_name))
    required_metrics = [str(m).lower() for m in required_results.get("metrics", [])]
    required_folds = required_results.get("folds")
    required_seeds = required_results.get("seeds", [])

    rows_out: list[dict[str, str]] = []

    dataset_ok = all(name in observed_datasets for name in required_datasets)
    rows_out.append(
        {
            "requirement": "available datasets covered",
            "required": ", ".join(required_datasets) or "(none)",
            "observed": ", ".join(sorted(observed_datasets)) or "(none)",
            "status": status(dataset_ok, bool(observed_datasets)),
            "evidence": f"{len(rows)} result rows",
        }
    )
    if missing_datasets:
        rows_out.append(
            {
                "requirement": "unavailable datasets documented",
                "required": ", ".join(missing_datasets),
                "observed": "see protocol dataset statuses",
                "status": "blocked",
                "evidence": "dataset status is not available/downloaded",
            }
        )

    method_ok = all(name in observed_methods for name in required_methods)
    rows_out.append(
        {
            "requirement": "required methods covered",
            "required": ", ".join(required_methods) or "(none)",
            "observed": ", ".join(sorted(observed_methods)) or "(none)",
            "status": status(method_ok, bool(observed_methods)),
            "evidence": f"method column: {method_col or '(missing)'}",
        }
    )

    metric_ok = all(metric in observed_metrics for metric in required_metrics)
    rows_out.append(
        {
            "requirement": "required metrics covered",
            "required": ", ".join(required_metrics) or "(none)",
            "observed": ", ".join(sorted(m for m in observed_metrics if m)) or "(none)",
            "status": status(metric_ok, bool(observed_metrics)),
            "evidence": "metric columns or long-format metric names",
        }
    )

    if required_folds:
        try:
            fold_ok = len(observed_folds) >= int(required_folds)
        except (TypeError, ValueError):
            fold_ok = False
        rows_out.append(
            {
                "requirement": "fold evidence",
                "required": str(required_folds),
                "observed": str(len(observed_folds)) if observed_folds else "(none)",
                "status": status(fold_ok, bool(observed_folds)),
                "evidence": f"fold/split column: {fold_col or '(missing)'}",
            }
        )

    if required_seeds and required_seeds != ["paper-stated-or-list"]:
        required_seed_text = {str(seed) for seed in required_seeds}
        seed_ok = required_seed_text.issubset(observed_seeds)
        rows_out.append(
            {
                "requirement": "seed evidence",
                "required": ", ".join(sorted(required_seed_text)),
                "observed": ", ".join(sorted(observed_seeds)) or "(none)",
                "status": status(seed_ok, bool(observed_seeds)),
                "evidence": f"seed column: {seed_col or '(missing)'}",
            }
        )
    elif not observed_seeds:
        rows_out.append(
            {
                "requirement": "seed evidence",
                "required": "paper-stated or explicit run seed",
                "observed": "(none)",
                "status": "partial",
                "evidence": "no seed/random_state column detected",
            }
        )

    return rows_out


def to_markdown(rows: list[dict[str, str]]) -> str:
    columns = ["requirement", "required", "observed", "status", "evidence"]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(col, "")).replace("\n", " ") for col in columns) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("protocol_json", help="Paper protocol JSON file")
    parser.add_argument("result_file", help="CSV, TSV, or JSON result table")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    protocol = load_json(Path(args.protocol_json))
    rows = load_rows(Path(args.result_file))
    report = check(protocol, rows)
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(to_markdown(report))


if __name__ == "__main__":
    main()
