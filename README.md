# Qoder Skills Repository

这是一组用于 Qoder AI 的技能（Skills）集合，用于增强 AI 在特定任务场景下的能力。

## 技能列表

| 技能名称 | 描述 | 分类 |
|---------|------|------|
| [ancestry-i18n](./ancestry-i18n/) | Ancestry 项目国际化处理工具，自动将中文字符串替换为 S.strings 调用并更新 ARB 文件 | 代码处理 |
| [commit](./commit/) | Git 提交助手，智能生成符合 Conventional Commits 规范的提交信息，并在提交前进行代码审查和验证 | Git 工作流 |
| [service-bill](./service-bill/) | 业务类单据生成工具，基于现有代码架构生成标准化的销售、进货、调拨等物流类单据组件 | 代码生成 |
| [wbs-split](./wbs-split/) | 智能 WBS 拆分工具，通过 AI 协同从网页内容提取表格数据并进行任务拆分 | 项目管理 |
| [yunxiao-bug-fix](./yunxiao-bug-fix/) | 云效 Bug 工作项全生命周期管理，涵盖工作项查询、详情获取、评论提交、状态流转等操作 | 项目管理 |

## 目录结构

```
skills/
├── README.md                    # 本文件
├── ancestry-i18n/              # 国际化处理技能
│   ├── SKILL.md                # 技能文档（必需）
│   ├── config.json             # 配置文件（可选）
│   ├── examples.md             # 使用示例（可选）
│   └── scripts/                # 脚本目录（可选）
│       └── i18n_helper.py
├── commit/                     # Git 提交助手技能
│   └── SKILL.md
├── service-bill/               # 业务单据生成技能
│   └── SKILL.md
├── wbs-split/                  # WBS 拆分技能
│   ├── SKILL.md
│   ├── config.json
│   └── scripts/
│       └── wbs_split.py
└── yunxiao-bug-fix/            # 云效 Bug 管理技能
    └── SKILL.md
```

## 技能文件说明

### SKILL.md（必需）

每个技能必须包含一个 `SKILL.md` 文件，这是技能的核心文档。文件格式如下：

```markdown
---
name: skill-name
description: 技能描述
trigger:                        # 可选，触发关键词
  - 关键词1
  - 关键词2
---

# 技能标题

技能详细说明...
```

### config.json（可选）

配置文件用于定义技能的参数、约束和依赖：

```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "技能描述",
  "author": "作者",
  "category": "分类",
  "tags": ["标签1", "标签2"],
  "dependencies": ["依赖包"],
  "parameters": {
    "param1": {
      "type": "string",
      "required": true,
      "description": "参数描述"
    }
  }
}
```

### examples.md（可选）

示例文档用于展示技能的具体使用场景和效果。

### scripts/（可选）

脚本目录用于存放技能需要用到的辅助脚本。

## 如何使用

在 Qoder 中，可以通过以下方式调用技能：

```
/run <skill-name> [参数]
```

例如：

```
/run ancestry-i18n --path lib/src/pages/
/run wbs-split --url "https://lanhuapp.com/..."
/run commit
```

## 如何创建新技能

1. 创建技能目录：`mkdir <skill-name>`
2. 创建 `SKILL.md` 文件并编写技能文档
3. 根据需要创建 `config.json`、`examples.md` 和 `scripts/` 目录
4. 在本 README 中添加技能描述

## 技能分类

- **代码处理**：ancestry-i18n
- **代码生成**：service-bill
- **Git 工作流**：commit
- **项目管理**：wbs-split, yunxiao-bug-fix
