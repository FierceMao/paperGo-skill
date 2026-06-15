# paperGo-skill

English | [中文](README.zh-CN.md)

`paperGo-skill` is a Codex skill for reviewer-grade research paper reproduction. It helps an agent move from a paper and optional author repository to a source-grounded reproduction plan, dataset manifest, missing-code audit, protocol coverage check, and evidence-backed result report.

The repository follows the OpenAI skills layout: the installable skill lives under `skills/papergo-skill/`, while this repository root contains human-facing documentation and project metadata.

## What It Does

- Extracts paper reproduction requirements: datasets, splits, preprocessing, metrics, main method steps, seeds, hardware, and missing details.
- Resolves paper datasets: download available public datasets when appropriate, or create missing-data manifests with concrete acquisition advice.
- Audits author repositories: identifies missing modules, incomplete scripts, unclear APIs, and implementation risks.
- Reconstructs missing author-code pieces only from paper evidence and caller context, with replaceable helper surfaces when confidence is limited.
- Checks protocol coverage with a paper protocol JSON and experiment result table.
- Normalizes result tables and flags unsupported claims, synthetic-only checks, missing seeds, and incomplete main-method workflows.

## Repository Layout

```text
paperGo-skill/
├── README.md
├── README.zh-CN.md
├── LICENSE
└── skills/
    └── papergo-skill/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        ├── references/
        │   ├── experiment-schema.md
        │   ├── report-template.md
        │   ├── reviewer-grade-checklist.md
        │   └── workflow.md
        └── scripts/
            ├── check_protocol_coverage.py
            ├── inspect_repro_package.py
            └── normalize_results.py
```

## Installation

Install or copy the skill directory into your Codex skills directory:

```powershell
Copy-Item -Recurse .\skills\papergo-skill $env:USERPROFILE\.codex\skills\papergo-skill
```

After installation, start a new Codex session so the skill can be discovered.

## Usage Examples

Ask Codex:

```text
Use $papergo-skill to reproduce this paper. Download datasets that are publicly available, audit the author repository, and report protocol coverage.
```

```text
Use $papergo-skill to inspect this experiment folder and tell me whether the results support a full paper reproduction claim.
```

## Bundled Scripts

Inspect a reproduction package:

```bash
python skills/papergo-skill/scripts/inspect_repro_package.py <folder> --format markdown
```

Normalize a result table:

```bash
python skills/papergo-skill/scripts/normalize_results.py <results.csv> --format markdown
```

Check paper protocol coverage:

```bash
python skills/papergo-skill/scripts/check_protocol_coverage.py protocol.json results.csv --format markdown
```

## Reproduction Standards

The skill is intentionally strict:

- Do not claim full reproduction unless paper datasets, split protocol, main method, metric definitions, commands, and outputs are covered.
- Treat synthetic experiments as mechanism checks unless they are the paper's stated dataset.
- Reconstruct missing code only from paper evidence and author-code caller context.
- Keep deviations out of the main reproduction path unless they are clearly labeled as non-reproduction extras.

## License

MIT License. See [LICENSE](LICENSE).
