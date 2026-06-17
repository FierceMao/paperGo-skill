# paperGo-skill

[English](README.md) | 中文

`paperGo-skill` 是一个给 Codex 用的论文复现助手。

你给 Codex 一篇论文、作者代码仓库，或者一个实验文件夹。这个 skill 会提醒 Codex：先检查数据、代码、实验流程和结果证据，再判断能不能说“已经复现”。

## 为什么需要它？

论文复现很容易出问题：

- 论文提到的数据集可能找不到；
- 作者仓库可能缺文件、缺脚本；
- 代码能跑，但不一定严格符合论文；
- 只跑了合成小实验，无法实现完整的实验步骤；
- 结果表可能用了不同划分、不同指标或不同随机种子。

`paperGo-skill` 的作用就是把这些问题提前暴露出来。

## 它会让 Codex 做什么？

使用这个 skill 时，Codex 应该按下面的顺序工作：

1. 阅读论文，提取真正的复现要求。
2. 查找论文中提到的数据集。
3. 如果数据公开、体量合适，就下载。
4. 如果数据找不到，就保留目录或清单，并说明怎么获取。
5. 审计作者代码仓库。
6. 如果作者代码缺模块，只能根据论文和调用关系重建。
7. 先跑论文主方法流程，再考虑可选基线。
8. 检查结果是否覆盖论文协议。
9. 明确标注状态：完整复现、部分复现、受阻，还是仅机制检查。

## 适合什么时候用？

你可以这样问 Codex：

```text
使用 $papergo-skill 复现这篇论文。
```

```text
使用 $papergo-skill 审计这个作者仓库，告诉我缺了什么。
```

```text
使用 $papergo-skill 检查这个实验文件夹，判断它能不能支撑完整复现声明。
```

## 它可能产出什么？

根据任务不同，Codex 可能生成：

- 论文复现清单；
- 数据集清单；
- 作者代码审计；
- 主方法修复或实现计划；
- 实验结果汇总表；
- 协议覆盖检查报告；
- 带局限说明的最终复现报告。

## 安装

把 skill 目录复制到 Codex 的 skills 目录：

```powershell
Copy-Item -Recurse .\skills\papergo-skill $env:USERPROFILE\.codex\skills\papergo-skill
```

复制后，新开一个 Codex 会话，让 Codex 重新发现这个 skill。

## 仓库结构

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

## 内置脚本

你也可以直接运行内置脚本。

检查复现文件夹：

```bash
python skills/papergo-skill/scripts/inspect_repro_package.py <folder> --format markdown
```

汇总结果表：

```bash
python skills/papergo-skill/scripts/normalize_results.py <results.csv> --format markdown
```

检查结果是否覆盖论文协议：

```bash
python skills/papergo-skill/scripts/check_protocol_coverage.py protocol.json results.csv --format markdown
```

## 许可证

MIT License。见 [LICENSE](LICENSE)。
