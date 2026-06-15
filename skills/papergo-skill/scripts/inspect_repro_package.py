#!/usr/bin/env python3
"""Inspect a research reproduction package and summarize reproducibility evidence.

This script is intentionally dependency-free. It scans file names, common config
formats, shallow result tables, and dataset-like folders without executing project
code.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PAPER_EXTS = {".pdf", ".tex", ".bib"}
CODE_EXTS = {".py", ".ipynb", ".sh", ".bat", ".ps1", ".R", ".m", ".jl"}
CONFIG_EXTS = {".yaml", ".yml", ".json", ".toml", ".ini", ".cfg"}
RESULT_EXTS = {".csv", ".tsv", ".json", ".jsonl", ".log", ".txt"}
ENV_NAMES = {
    "requirements.txt",
    "environment.yml",
    "environment.yaml",
    "pyproject.toml",
    "poetry.lock",
    "conda.yml",
    "Dockerfile",
    "docker-compose.yml",
}
DATA_HINTS = {"data", "dataset", "datasets", "images", "labels", "annotations", "splits"}
RESULT_HINTS = {"result", "results", "eval", "evaluation", "metrics", "logs", "runs", "outputs"}
TRAIN_HINTS = {"train", "fit", "trainer", "finetune", "pretrain"}
EVAL_HINTS = {"eval", "evaluate", "test", "metric", "infer", "predict"}
METRIC_NAMES = {
    "acc",
    "accuracy",
    "auc",
    "auroc",
    "ap",
    "map",
    "f1",
    "f_measure",
    "macro_f1",
    "precision",
    "recall",
    "gmean",
    "g_mean",
    "geometric_mean",
    "balanced_accuracy",
    "minority_recall",
    "majority_recall",
    "sensitivity",
    "specificity",
    "iou",
    "miou",
    "loss",
    "rmse",
    "mae",
}


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def iter_files(root: Path, max_files: int) -> list[Path]:
    skipped = {".git", ".venv", "venv", "__pycache__", "node_modules", ".mypy_cache"}
    out: list[Path] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skipped and not d.startswith(".ipynb_checkpoints")]
        for name in files:
            out.append(Path(current) / name)
            if len(out) >= max_files:
                return out
    return out


def classify_files(files: list[Path], root: Path) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for path in files:
        lower_name = path.name.lower()
        lower_rel = rel(path, root).lower()
        suffix = path.suffix.lower()

        if suffix in PAPER_EXTS or lower_name in {"readme.md", "readme.txt"}:
            groups["papers_and_docs"].append(rel(path, root))
        if lower_name in {n.lower() for n in ENV_NAMES}:
            groups["environment"].append(rel(path, root))
        if suffix in CONFIG_EXTS:
            groups["configs"].append(rel(path, root))
        if suffix in CODE_EXTS:
            groups["code"].append(rel(path, root))
        if suffix in RESULT_EXTS and any(h in lower_rel for h in RESULT_HINTS):
            groups["results"].append(rel(path, root))
        if any(h in lower_rel.split("/") for h in DATA_HINTS):
            groups["data_related"].append(rel(path, root))
        if suffix in CODE_EXTS and any(h in lower_name for h in TRAIN_HINTS):
            groups["training_entrypoints"].append(rel(path, root))
        if suffix in CODE_EXTS and any(h in lower_name for h in EVAL_HINTS):
            groups["evaluation_entrypoints"].append(rel(path, root))
    return {k: sorted(v) for k, v in groups.items()}


def extension_counts(files: list[Path]) -> dict[str, int]:
    counter = Counter(path.suffix.lower() or "<none>" for path in files)
    return dict(counter.most_common())


def infer_dataset_classes(files: list[Path], root: Path) -> dict[str, Any]:
    """Infer class names from common image-folder layouts without reading images."""
    image_exts = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
    class_counts: Counter[str] = Counter()
    split_counts: Counter[str] = Counter()

    for path in files:
        if path.suffix.lower() not in image_exts:
            continue
        parts = path.relative_to(root).parts
        lower_parts = [p.lower() for p in parts]
        split = next((p for p in lower_parts if p in {"train", "val", "valid", "validation", "test"}), None)
        if split:
            split_counts[split] += 1
            idx = lower_parts.index(split)
            if idx + 1 < len(parts) - 1:
                class_counts[parts[idx + 1]] += 1
        elif len(parts) >= 2:
            class_counts[parts[-2]] += 1

    return {
        "image_count": int(sum(class_counts.values())),
        "class_counts": dict(class_counts.most_common()),
        "split_image_counts": dict(split_counts.most_common()),
    }


def sample_metric_columns(path: Path) -> list[str]:
    try:
        if path.suffix.lower() == ".csv":
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle)
                return [c for c in (reader.fieldnames or []) if c and c.lower() in METRIC_NAMES]
        if path.suffix.lower() == ".tsv":
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle, delimiter="\t")
                return [c for c in (reader.fieldnames or []) if c and c.lower() in METRIC_NAMES]
        if path.suffix.lower() == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return [k for k in data if k.lower() in METRIC_NAMES]
            if isinstance(data, list) and data and isinstance(data[0], dict):
                return [k for k in data[0] if k.lower() in METRIC_NAMES]
    except Exception:
        return []
    return []


def metric_inventory(result_files: list[str], root: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for item in result_files[:100]:
        columns = sample_metric_columns(root / item)
        if columns:
            out[item] = columns
    return out


def build_risks(groups: dict[str, list[str]], dataset: dict[str, Any], metrics: dict[str, list[str]]) -> list[str]:
    risks: list[str] = []
    if not groups.get("environment"):
        risks.append("No obvious environment file found.")
    if not groups.get("data_related"):
        risks.append("No obvious dataset files, data directory, split file, or dataset manifest found.")
    if not groups.get("training_entrypoints"):
        risks.append("No obvious training entrypoint found.")
    if not groups.get("evaluation_entrypoints"):
        risks.append("No obvious evaluation entrypoint found.")
    if not groups.get("results"):
        risks.append("No obvious result or metric files found.")
    if dataset["image_count"] and not dataset["split_image_counts"]:
        risks.append("Image dataset-like files found, but train/val/test split folders were not clear.")
    if groups.get("results") and not metrics:
        risks.append("Result-like files found, but common metric columns were not detected.")
    if groups.get("results"):
        result_names = " ".join(groups.get("results", [])).lower()
        if "synthetic" in result_names and not groups.get("data_related"):
            risks.append("Synthetic result files found without paper dataset evidence; treat as mechanism checks, not full reproduction.")
    return risks


def inspect(root: Path, max_files: int) -> dict[str, Any]:
    files = iter_files(root, max_files)
    groups = classify_files(files, root)
    dataset = infer_dataset_classes(files, root)
    metrics = metric_inventory(groups.get("results", []), root)
    return {
        "root": str(root),
        "file_count_scanned": len(files),
        "extension_counts": extension_counts(files),
        "groups": groups,
        "dataset_inference": dataset,
        "metric_inventory": metrics,
        "risks": build_risks(groups, dataset, metrics),
    }


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Reproducibility Package Inspection",
        "",
        f"- Root: `{report['root']}`",
        f"- Files scanned: {report['file_count_scanned']}",
        "",
        "## Key Files",
    ]
    for group, items in report["groups"].items():
        lines.append(f"### {group.replace('_', ' ').title()}")
        for item in items[:30]:
            lines.append(f"- `{item}`")
        if len(items) > 30:
            lines.append(f"- ... {len(items) - 30} more")
        lines.append("")

    dataset = report["dataset_inference"]
    lines.extend(["## Dataset Inference", ""])
    lines.append(f"- Image files assigned to inferred classes: {dataset['image_count']}")
    if dataset["split_image_counts"]:
        lines.append("- Split image counts:")
        for split, count in dataset["split_image_counts"].items():
            lines.append(f"  - {split}: {count}")
    if dataset["class_counts"]:
        lines.append("- Top inferred classes:")
        for cls, count in list(dataset["class_counts"].items())[:20]:
            lines.append(f"  - {cls}: {count}")
    lines.append("")

    lines.extend(["## Metric Inventory", ""])
    if report["metric_inventory"]:
        for file_name, columns in report["metric_inventory"].items():
            lines.append(f"- `{file_name}`: {', '.join(columns)}")
    else:
        lines.append("- No common metric columns detected in result-like files.")
    lines.append("")

    lines.extend(["## Reproducibility Risks", ""])
    if report["risks"]:
        for risk in report["risks"]:
            lines.append(f"- {risk}")
    else:
        lines.append("- No obvious structural risks detected by this shallow scan.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", help="Project, paper, or experiment folder to inspect")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--max-files", type=int, default=5000)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Path does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Expected a directory: {root}")

    report = inspect(root, args.max_files)
    if args.format == "markdown":
        print(to_markdown(report))
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
