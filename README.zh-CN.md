# paperGo-skill

[English](README.md) | 中文

`paperGo-skill` 是一个面向 Codex 的论文复现 skill。它帮助 agent 从论文本身，建立有来源依据的复现计划、数据收集、算法实现、实验验证等。

本仓库参考 OpenAI skills 的组织方式：可安装的 skill 位于 `skills/papergo-skill/`，仓库根目录只放说明文档和项目元信息。

## 能做什么

- 提取论文复现要求：数据集、划分协议、预处理、指标、主方法步骤、随机种子、硬件和缺失信息。
- 解析论文数据集：能公开获取且体量合适的数据就下载；找不到、受限或过大的数据只保留目录/清单，并给出获取建议。
- 审计作者仓库：识别缺失模块、不完整脚本、不清晰 API 和实现风险。
- 对缺失作者代码进行严格重建：只能依据论文内容和作者代码调用关系实现；不确定部分要做成小而清晰、方便人工替换的函数或类。
- 用论文协议 JSON 和结果表检查协议覆盖情况。
- 规范化实验结果表，并提示不支持的结论、只有合成实验、缺少 seed、主流程不完整等问题。

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

## 安装

将 skill 目录复制到 Codex skills 目录：

```powershell
Copy-Item -Recurse .\skills\papergo-skill $env:USERPROFILE\.codex\skills\papergo-skill
```

复制后重启或新开 Codex 会话，让 Codex 重新发现 skill。

## 使用示例

可以这样向 Codex 提问：

```text
使用 $papergo-skill 复现这篇论文。能公开获取的数据请下载，审计作者仓库，并报告实验协议覆盖情况。
```

```text
使用 $papergo-skill 检查这个实验文件夹，判断当前结果是否足以支撑完整论文复现声明。
```

## 内置脚本

检查复现包结构：

```bash
python skills/papergo-skill/scripts/inspect_repro_package.py <folder> --format markdown
```

规范化结果表：

```bash
python skills/papergo-skill/scripts/normalize_results.py <results.csv> --format markdown
```

检查论文协议覆盖：

```bash
python skills/papergo-skill/scripts/check_protocol_coverage.py protocol.json results.csv --format markdown
```

## 复现标准

这个 skill 故意保持严格：

- 只有论文数据集、划分协议、主方法、指标定义、运行命令和输出证据都齐全时，才允许称为完整复现。
- 合成实验默认只能称为机制检查，除非它本身就是论文规定数据。
- 缺失代码只能依据论文证据和作者代码调用关系重建。
- 不允许把便利性修改、随意拓展或替代算法混进主复现路径；如确实需要，必须标为非复现扩展。

## 许可证

MIT License。见 [LICENSE](LICENSE)。
