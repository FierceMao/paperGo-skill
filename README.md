# paperGo-skill

English | [中文](README.zh-CN.md)

`paperGo-skill` helps Codex reproduce research papers more carefully.

Give Codex a paper, an author repository, or an experiment folder. This skill tells Codex how to check the paper's data, code, experiment protocol, and results before making any reproduction claim.

In short: **paperGo helps Codex avoid saying "reproduced" too early.**

## Why Use It?

Reproducing a paper is easy to get wrong:

- the paper may mention datasets that are hard to find;
- the author repository may miss files or scripts;
- the code may run, but not follow the paper exactly;
- a synthetic demo may be mistaken for a full paper reproduction;
- result tables may use different splits, metrics, or seeds.

`paperGo-skill` is designed to catch these problems.

## What It Asks Codex To Do

When you use this skill, Codex should:

1. Read the paper and extract the real reproduction requirements.
2. Look for the paper's datasets.
3. Download public datasets when possible.
4. If a dataset cannot be found, keep a folder or manifest and explain how to get it.
5. Audit the author repository.
6. Rebuild missing code only when the paper explains enough to do so.
7. Run the paper's main method workflow before optional baselines.
8. Check whether the final results really cover the paper protocol.
9. Clearly label the status as full reproduction, partial reproduction, blocked, or mechanism check.

## Good Use Cases

Use `paperGo-skill` when you want to ask Codex things like:

```text
Use $papergo-skill to reproduce this paper.
```

```text
Use $papergo-skill to audit this author repository and tell me what is missing.
```

```text
Use $papergo-skill to check whether this experiment folder is enough for a full reproduction claim.
```

## What It Produces

Depending on the task, Codex may create:

- a paper reproduction checklist;
- a dataset manifest;
- an author-code audit;
- a repaired main-method implementation plan;
- a result summary table;
- a protocol coverage report;
- a final reproduction report with limitations.

## Install

Copy the skill folder into your Codex skills directory:

```powershell
Copy-Item -Recurse .\skills\papergo-skill $env:USERPROFILE\.codex\skills\papergo-skill
```

Then start a new Codex session so the skill can be discovered.

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

## Helper Scripts

You can also run the bundled scripts directly.

Inspect a reproduction folder:

```bash
python skills/papergo-skill/scripts/inspect_repro_package.py <folder> --format markdown
```

Summarize a result table:

```bash
python skills/papergo-skill/scripts/normalize_results.py <results.csv> --format markdown
```

Check whether results cover the paper protocol:

```bash
python skills/papergo-skill/scripts/check_protocol_coverage.py protocol.json results.csv --format markdown
```

## Important Notes

- A runnable script is not the same as a reproduced paper.
- Synthetic data checks are only mechanism checks unless the paper itself uses synthetic data.
- Missing author code should only be rebuilt from paper evidence and caller context.
- If data, splits, metrics, or outputs are missing, the report should say so clearly.

## License

MIT License. See [LICENSE](LICENSE).
