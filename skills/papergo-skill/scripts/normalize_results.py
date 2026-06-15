#!/usr/bin/env python3
"""Normalize experiment result CSV/JSON files into compact comparison tables."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev
from typing import Any


DEFAULT_GROUP_COLUMNS = ["method", "model", "algorithm", "dataset", "split", "seed", "class"]
DEFAULT_METRIC_COLUMNS = [
    "accuracy",
    "acc",
    "f1",
    "f_measure",
    "macro_f1",
    "precision",
    "recall",
    "auc",
    "auroc",
    "gmean",
    "g_mean",
    "geometric_mean",
    "balanced_accuracy",
    "minority_recall",
    "majority_recall",
    "sensitivity",
    "specificity",
    "ap",
    "map",
    "miou",
    "iou",
    "loss",
]


def coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().rstrip("%")
    if not text:
        return None
    try:
        val = float(text)
    except ValueError:
        return None
    if str(value).strip().endswith("%"):
        return val / 100.0
    return val


def load_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    if suffix == ".tsv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle, delimiter="\t"))
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [row for row in data if isinstance(row, dict)]
        if isinstance(data, dict):
            if all(isinstance(v, (int, float, str, type(None))) for v in data.values()):
                return [data]
            for key in ("results", "metrics", "rows", "data"):
                value = data.get(key)
                if isinstance(value, list):
                    return [row for row in value if isinstance(row, dict)]
    raise SystemExit(f"Unsupported or unrecognized result file: {path}")


def detect_columns(rows: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    keys: list[str] = []
    seen = set()
    for row in rows:
        for key in row:
            if key not in seen:
                keys.append(key)
                seen.add(key)

    lower = {key.lower(): key for key in keys}
    groups = [lower[c] for c in DEFAULT_GROUP_COLUMNS if c in lower]
    metrics = [lower[c] for c in DEFAULT_METRIC_COLUMNS if c in lower]

    if not metrics:
        metrics = [key for key in keys if sum(coerce_float(row.get(key)) is not None for row in rows) >= max(1, len(rows) // 2)]
    return groups, metrics


def summarize(rows: list[dict[str, Any]], group_cols: list[str], metric_cols: list[str]) -> list[dict[str, Any]]:
    bucket: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    if not group_cols:
        group_cols = ["__all__"]
        for row in rows:
            row["__all__"] = "all"

    for row in rows:
        key = tuple(row.get(col, "") for col in group_cols)
        bucket[key].append(row)

    summary: list[dict[str, Any]] = []
    for key, group_rows in bucket.items():
        out: dict[str, Any] = {col: key[idx] for idx, col in enumerate(group_cols) if col != "__all__"}
        out["n"] = len(group_rows)
        for metric in metric_cols:
            vals = [coerce_float(row.get(metric)) for row in group_rows]
            vals = [v for v in vals if v is not None]
            if not vals:
                continue
            out[f"{metric}_mean"] = mean(vals)
            if len(vals) > 1:
                out[f"{metric}_std"] = stdev(vals)
            out[f"{metric}_count"] = len(vals)
        summary.append(out)
    return summary


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def to_markdown(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "No rows to summarize."
    columns = list(rows[0].keys())
    for row in rows[1:]:
        for key in row:
            if key not in columns:
                columns.append(key)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(fmt(row.get(col, "")) for col in columns) + " |")
    return "\n".join(lines)


def to_csv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    columns = list(rows[0].keys())
    for row in rows[1:]:
        for key in row:
            if key not in columns:
                columns.append(key)
    output = [",".join(columns)]
    for row in rows:
        output.append(",".join(fmt(row.get(col, "")) for col in columns))
    return "\n".join(output)


def to_latex(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "% No rows to summarize."
    columns = list(rows[0].keys())
    for row in rows[1:]:
        for key in row:
            if key not in columns:
                columns.append(key)
    lines = [
        "\\begin{tabular}{" + "l" * len(columns) + "}",
        " \\toprule",
        " & ".join(columns) + " \\\\",
        " \\midrule",
    ]
    for row in rows:
        lines.append(" & ".join(fmt(row.get(col, "")) for col in columns) + " \\\\")
    lines.extend([" \\bottomrule", "\\end{tabular}"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_file", help="CSV, TSV, or JSON result file")
    parser.add_argument("--format", choices=["markdown", "csv", "latex", "json"], default="markdown")
    parser.add_argument("--group-by", default="", help="Comma-separated grouping columns. Defaults to detected columns.")
    parser.add_argument("--metrics", default="", help="Comma-separated metric columns. Defaults to detected metrics.")
    args = parser.parse_args()

    path = Path(args.result_file).resolve()
    rows = load_rows(path)
    detected_groups, detected_metrics = detect_columns(rows)
    group_cols = [c.strip() for c in args.group_by.split(",") if c.strip()] or detected_groups
    metric_cols = [c.strip() for c in args.metrics.split(",") if c.strip()] or detected_metrics
    summary = summarize(rows, group_cols, metric_cols)

    if args.format == "json":
        print(json.dumps({"group_by": group_cols, "metrics": metric_cols, "rows": summary}, indent=2, ensure_ascii=False))
    elif args.format == "csv":
        print(to_csv(summary))
    elif args.format == "latex":
        print(to_latex(summary))
    else:
        print(to_markdown(summary))


if __name__ == "__main__":
    main()
