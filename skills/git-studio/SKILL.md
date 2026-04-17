---
name: git-studio
description: 蒸馏 Android Studio Git 工具的全流程操作技能，100%覆盖 Clone/Init、提交、Changelist、Shelve、分支管理、合并/Rebase/Cherry-pick、冲突解决、远程操作、Stash、历史查看、标签、Reset/Revert、Patch、Submodule、Git Hooks、GPG 签名等完整 Git 工作流。当用户涉及任何 Git 操作（如"克隆"、"初始化"、"提交"、"切换分支"、"合并"、"查看日志"、"暂存"、"回退"、"补丁"、"子模块"等）时触发。
---

# Git Studio — 完整 Git 工作流技能

蒸馏 Android Studio 内置 Git 工具的所有操作流程，以 CLI 方式 100% 保真实现等价能力。

## 何时使用

- 用户提到任何 Git 操作关键词：克隆、初始化、提交、分支、合并、rebase、stash、shelve、回退、日志、tag、补丁、子模块 等
- 用户要求执行版本控制相关操作
- 用户遇到 Git 冲突、推送失败等问题

## 操作路由

根据用户意图路由到对应模块：

| 用户意图 | 路由目标 | 关键词 |
|----------|----------|--------|
| 克隆/初始化 | [本文件 → 仓库初始化](#仓库初始化) | clone、init、克隆、初始化 |
| 提交代码 | [本文件 → 提交流程](#提交流程) | 提交、commit、push |
| 变更列表 | [本文件 → Changelist](#changelist--变更列表) | changelist、变更列表 |
| 搁置变更 | [本文件 → Shelve](#shelve--搁置变更) | shelve、搁置 |
| 文件级操作 | [本文件 → 文件级操作](#文件级git操作) | 单文件提交、文件历史、annotate |
| 远程同步 | [本文件 → 远程操作](#远程操作) | push、pull、fetch、推送、拉取 |
| 分支操作 | [SKILL-branch.md](SKILL-branch.md) | 分支、branch、切换、checkout |
| 合并/变基 | [SKILL-merge.md](SKILL-merge.md) | merge、rebase、cherry-pick、冲突 |
| 查看历史 | [SKILL-history.md](SKILL-history.md) | log、日志、blame、diff、tag、标签 |
| 高级操作 | [SKILL-advanced.md](SKILL-advanced.md) | stash、reset、revert、暂存、回退、撤销、patch、submodule、hooks |

---

## 仓库初始化

### Clone — 克隆远程仓库

Android Studio 的 **VCS → Get from Version Control** 等价操作。

**🔄 询问用户（对应 AS 的 Clone Repository 对话框）：**
> 克隆远程仓库：
> - **仓库 URL**：（HTTPS/SSH 地址）
> - **克隆到目录**：（默认：当前目录下以仓库名命名）
> - **克隆选项**：
>   1. **完整克隆**（默认）— 克隆全部历史
>   2. **浅克隆** — `--depth 1`，仅最新提交（快速）
>   3. **指定分支克隆** — `--branch <name>`
>   4. **取消**

```bash
# 完整克隆
git clone <url>
git clone <url> <directory>

# 浅克隆（仅最新提交，节省时间和空间）
git clone --depth 1 <url>

# 克隆指定分支
git clone --branch <branch-name> <url>

# 克隆并设置目录名
git clone <url> <custom-dir-name>

# 递归克隆（含子模块）
git clone --recurse-submodules <url>

# 稀疏克隆（仅克隆部分目录，大仓库适用）
git clone --filter=blob:none --sparse <url>
cd <repo>
git sparse-checkout set <dir1> <dir2>
```

**克隆后自动执行：**
```bash
cd <cloned-dir>
git branch -a              # 查看所有分支
git remote -v              # 确认远程地址
git log --oneline -5       # 查看最近提交
```

### Init — 初始化本地仓库

Android Studio 的 **VCS → Enable Version Control Integration** 等价操作。

**🔄 询问用户（对应 AS 的 Enable Version Control Integration 对话框）：**
> 在当前目录初始化 Git 仓库：
> - 目录：`<current-dir>`
> - **初始选项**：
>   1. **标准初始化** — 创建空仓库
>   2. **初始化并关联远程** — 同时设置 remote origin
>   3. **取消**

```bash
# 标准初始化
git init

# 初始化并创建初始提交
git init
git add .
git commit -m "Initial commit"

# 初始化并关联远程仓库
git init
git remote add origin <url>
git add .
git commit -m "Initial commit"
git push -u origin main

# 初始化指定默认分支名
git init --initial-branch=main
```

**初始化后建议操作：**
```bash
# 创建 .gitignore（agent 根据项目类型自动生成）
# 如 Flutter 项目:
cat > .gitignore << 'EOF'
.dart_tool/
.packages
build/
*.iml
.idea/
.flutter-plugins
.flutter-plugins-dependencies
EOF

git add .gitignore
git commit -m "chore: add .gitignore"
```

---

## 通用前置：环境检查

每次操作前确认 Git 环境：

```bash
# 确认在 Git 仓库内
git rev-parse --is-inside-work-tree

# 当前分支
git branch --show-current

# 工作区状态概览
git status --short
```

如果不在 Git 仓库内：
- 提示用户并询问是否需要 **Clone** 或 **Init**
- 路由到 [仓库初始化](#仓库初始化)

---

## 提交流程

### 阶段1：检查工作区状态

```bash
git status
```

**判断暂存区：**
- 有暂存内容 → 继续阶段2
- 暂存区为空但有未暂存变更 → **🔄 询问用户：**
  > 暂存区为空，但检测到以下未暂存的文件变更：
  > [列出变更文件]
  > 请选择：
  > 1. **暂存全部** (`git add .`)
  > 2. **选择文件暂存**（列出文件让用户勾选）
  > 3. **取消提交**
- 工作区干净 → 提示"没有需要提交的变更"

**暂存文件的方式：**

```bash
# 暂存全部
git add .

# 暂存指定文件
git add <file1> <file2>

# 交互式选择（逐文件确认）
git add -i

# 逐块暂存（选择文件中的部分变更）
git add -p <file>
```

#### ⚠️ GUI 强项：逐行 Stage / Partial Commit

Android Studio 支持在 Diff 视图中用鼠标选择部分行进行暂存，CLI 的 `git add -p` 交互成本较高，以下是 agent 辅助的最佳替代：

**🤖 Agent 辅助流程（推荐）：**

1. 列出变更概览：
```bash
git diff --stat
```

2. 用户指定要部分暂存的文件后，agent 展示该文件的所有变更块(hunk)：
```bash
git diff <file>
```

3. **🔄 询问用户：**
   > 文件 `<file>` 有以下变更块：
   > ```
   > Hunk 1 (L10-L15): 添加了 import 语句
   > Hunk 2 (L42-L58): 修改了 login 方法
   > Hunk 3 (L80-L85): 修复了注释错别字
   > ```
   > 请选择要暂存的变更块（多选）：
   > 1. **全部暂存**
   > 2. **按编号选择**，如 `1,2`
   > 3. **排除编号**，如 `!3`（暂存除了 Hunk 3 以外的全部）

4. Agent 根据选择自动执行，两种方式：

```bash
# 方式 A：通过 patch 精确控制（agent 生成 patch 文件）
git diff <file> > /tmp/full.patch
# agent 提取用户选择的 hunk 生成 partial.patch
git apply --cached /tmp/partial.patch

# 方式 B：自动应答 git add -p 的交互提示
# agent 根据用户选择生成 y/n 序列
printf 'y\nn\ny\n' | git add -p <file>
```

5. 确认暂存结果：
```bash
git diff --cached --stat
```

**简化场景的直接命令：**

```bash
# 场景：暂存某文件的所有变更（最常见）
git add <file>

# 场景：排除某些文件，暂存其余全部
git add .
git reset HEAD <不想暂存的文件>

# 场景：只暂存新增文件，不暂存修改
git add --intent-to-add <new-file>
git add -p <new-file>
```

### 阶段2：查看暂存内容

```bash
# 查看暂存区与上次提交的差异
git diff --cached

# 仅查看变更文件列表
git diff --cached --name-only

# 查看统计摘要
git diff --cached --stat
```

### 阶段3：生成提交信息

分析 diff 内容，生成简洁清晰的提交信息：

```
<type>(<scope>): <subject>

<body>
```

**Type 速查：**
- `feat` 新功能 | `fix` 修复 | `refactor` 重构 | `style` 格式
- `docs` 文档 | `test` 测试 | `perf` 性能 | `chore` 杂项

**Subject 规则：** 动词开头、50字符内、不加句号

### 阶段4：执行提交

**🔄 询问用户（对应 AS 的 Commit 对话框 — 完整选项）：**
> 📋 提交确认：
> - **提交信息**：`<已生成的提交信息>`
> - **提交选项**：
>   - ☐ **Amend** — 修改上次提交（默认：否）
>   - ☐ **Sign-off** — 添加 `Signed-off-by` 签名行（默认：否）
>   - ☐ **GPG Sign** — GPG 签名提交（默认：按全局配置）
>   - **Author**：（默认：当前 `user.name <user.email>`，如需使用其他作者身份请指定）
> - **Before Commit 检查**：
>   - ☐ **Reformat Code** — 提交前格式化代码
>   - ☐ **Optimize Imports** — 移除无用导入
>   - ☐ **Analyze Code** — 静态分析检查
>   - ☐ **Check TODO** — 检查未完成的 TODO 注释
> - **操作**：
>   1. **Commit** — 仅提交到本地
>   2. **Commit and Push** — 提交并推送到远程（默认）
>   3. **修改提交信息** — 编辑后再提交
>   4. **取消**

**Before Commit 检查执行（agent 辅助）：**
```bash
# Reformat Code — agent 根据项目类型执行格式化
# Flutter: dart format .
# Node.js: npx prettier --write .
# Python: black .

# Analyze Code — agent 根据项目类型执行静态分析
# Flutter: dart analyze
# Node.js: npx eslint .
# Python: pylint <module>

# Check TODO — 列出代码中的 TODO
git diff --cached | grep -n 'TODO\|FIXME\|HACK\|XXX'
```

```bash
# 标准提交
git commit -m "<message>"

# 多行提交信息
git commit -m "<subject>" -m "<body>"

# 带 Sign-off 签名
git commit -s -m "<message>"

# 带 GPG 签名
git commit -S -m "<message>"

# 指定其他作者
git commit --author="Name <email>" -m "<message>"

# 组合选项
git commit -s -S --author="Name <email>" -m "<message>"
```

**如果用户选择 Amend（修改上次提交）：**

**🔄 询问用户（对应 AS 的 Amend Commit 复选框）：**
> ⚠️ 你要修改上次提交，请确认：
> - 上次提交：`<最近一条commit信息>`
> 1. **Amend 并修改信息** — 重写提交信息
> 2. **Amend 保留信息** — 仅追加变更到上次提交
> 3. **取消** — 作为新提交

```bash
git commit --amend -m "<new message>"  # 修改信息
git commit --amend --no-edit            # 保留信息
```

**Amend 已推送提交的警告：**

如果检测到上次提交已推送到远程：
> ⚠️ **警告：上次提交已推送到远程！**
> Amend 后需要 force push，可能影响其他协作者。
> 1. **继续 Amend** — 我了解风险，稍后 force push
> 2. **改为新提交** — 更安全的方式

### 阶段5：推送

**🔄 询问用户（如果阶段4未选择 Commit and Push）：**
> 提交成功！是否推送到远程？
> 1. **推送**（默认）
> 2. **暂不推送**

```bash
git push
```

推送失败时参见 [远程操作 → 推送失败处理](#推送失败处理)。

---

## 远程操作

### Fetch — 获取远程更新

```bash
# 获取所有远程更新（不修改工作区）
git fetch --all

# 获取指定远程
git fetch origin

# 获取并清理已删除的远程分支
git fetch --prune
```

**用途：** 查看远程有什么新变更，但不改变本地代码。

### Pull — 拉取并合并

**🔄 询问用户（对应 AS 的 Update Project 对话框）：**
> 拉取远程更新，请选择合并策略：
> 1. **Rebase**（推荐）— `git pull --rebase`，保持线性历史
> 2. **Merge** — `git pull`，保留合并提交
> 3. **取消**

```bash
# 用户选择 Merge
git pull

# 用户选择 Rebase
git pull --rebase

# 拉取指定分支
git pull origin <branch>
```

**Pull 冲突处理：**
- merge 模式冲突 → 参见 [SKILL-merge.md](SKILL-merge.md) 冲突解决
- rebase 模式冲突 → 参见 [SKILL-merge.md](SKILL-merge.md) Rebase 冲突

### Push — 推送到远程

```bash
# 推送当前分支
git push

# 首次推送新分支（设置上游跟踪）
git push -u origin <branch>

# 推送所有分支
git push --all

# 推送标签
git push --tags

# 推送单个标签
git push origin <tag-name>
```

### 推送失败处理

**情况1：远程有新提交**
```
! [rejected] main -> main (fetch first)
```

**🔄 询问用户（对应 AS 的 Push Rejected 对话框）：**
> ⚠️ 推送被拒绝：远程分支有新的提交。
> 请选择同步方式：
> 1. **Rebase**（推荐）— 将本地提交变基到远程最新，保持线性历史
> 2. **Merge** — 创建合并提交，保留分支拓扑
> 3. **取消** — 暂不推送

```bash
# 用户选择 Rebase
git pull --rebase
git push

# 用户选择 Merge
git pull
git push
```

**情况2：分支无上游**
```
fatal: The current branch xxx has no upstream branch
```

处理：
```bash
git push -u origin <current-branch>
```

**情况3：强制推送（危险操作）**
```bash
# ⚠️ 仅在明确需要时使用，会覆盖远程历史
git push --force-with-lease   # 安全版，拒绝覆盖他人提交
git push --force              # 危险版，无条件覆盖
```

**🔄 强制推送确认（对应 AS 的 Force Push 警告对话框）：**
> ⛔ **危险操作：Force Push**
> 这将覆盖远程分支 `<branch>` 的历史，可能导致其他协作者的工作丢失。
> - 当前分支：`<branch>`
> - 远程有 `<N>` 个你没有的提交将被覆盖
>
> 1. **Force Push (--force-with-lease)** — 安全版，若远程有他人新提交则拒绝
> 2. **Force Push (--force)** — 无条件覆盖（极危险）
> 3. **取消** — 不推送

### Remote 管理

```bash
# 查看远程仓库
git remote -v

# 添加远程
git remote add <name> <url>

# 修改远程 URL
git remote set-url origin <new-url>

# 删除远程
git remote remove <name>
```

---

## Changelist — 变更列表

Android Studio 支持将未提交的变更组织到多个 Changelist 中，每个 Changelist 可以独立命名和提交。CLI 没有内置 Changelist 概念，以下是 agent 辅助的等价实现：

**🤖 Agent 辅助流程（模拟 AS Changelist）：**

1. 列出所有变更文件：
```bash
git status --short
```

2. **🔄 询问用户（对应 AS 的 Move to Another Changelist 对话框）：**
   > 当前变更文件：
   > | # | 状态 | 文件 |
   > |---|------|------|
   > | 1 | M | src/pages/home.dart |
   > | 2 | M | src/models/user.dart |
   > | 3 | A | src/pages/login.dart |
   > | 4 | M | pubspec.yaml |
   > | 5 | M | test/home_test.dart |
   >
   > 请将文件分组到变更列表：
   > - **列表1名称**：（如 "用户登录功能"）
   >   - 包含文件编号：（如 `2,3`）
   > - **列表2名称**：（如 "首页优化"）
   >   - 包含文件编号：（如 `1,5`）
   > - 未分配的文件将归入 "Default Changelist"

3. 按用户分组逐个提交：
```bash
# Changelist 1: 用户登录功能
git add src/models/user.dart src/pages/login.dart
git commit -m "feat(auth): 添加用户登录功能"

# Changelist 2: 首页优化
git add src/pages/home.dart test/home_test.dart
git commit -m "refactor(home): 优化首页布局"

# Default Changelist: 剩余文件
git add pubspec.yaml
git commit -m "chore: update dependencies"
```

**简化操作：**
```bash
# 场景：仅想把部分文件单独提交（最常见的 Changelist 用途）
git add <file1> <file2>
git commit -m "<message>"
# 然后提交剩余文件
git add .
git commit -m "<message>"
```

---

## Shelve — 搁置变更

Android Studio 的 **Shelve Changes** 功能类似 Stash，但更精细——支持搁置部分文件或部分变更块，并可附带描述。CLI 使用 `git stash` + agent 辅助实现等价效果：

### Shelve Changes

**🔄 询问用户（对应 AS 的 Shelve Changes 对话框）：**
> 搁置变更：
> [列出所有变更文件，支持勾选]
> | # | 状态 | 文件 | 搁置? |
> |---|------|------|-------|
> | 1 | M | src/pages/home.dart | ☑ |
> | 2 | M | src/models/user.dart | ☑ |
> | 3 | A | src/pages/login.dart | ☐ |
>
> - **搁置描述**：（如 "WIP: 用户系统重构"）
> - 选择要搁置的文件（默认全部）：
>   1. **全部搁置**
>   2. **按编号选择**，如 `1,2`
>   3. **取消**

```bash
# 搁置全部变更
git stash push -m "shelve: <描述信息>"

# 搁置指定文件（等价于 AS 的部分 Shelve）
git stash push -m "shelve: <描述>" -- <file1> <file2>

# 搁置部分变更块（等价于 AS 的行级 Shelve）
git stash push -p -m "shelve: <描述>"
```

### Unshelve Changes

**🔄 询问用户（对应 AS 的 Unshelve Changes 对话框）：**
> 恢复搁置的变更：
> [列出所有 shelve 记录]
> | # | 描述 | 时间 | 文件数 |
> |---|------|------|--------|
> | 0 | shelve: WIP: 用户系统重构 | 2小时前 | 2 files |
> | 1 | shelve: 首页临时修改 | 昨天 | 1 file |
>
> 请选择：
> 1. **Pop**（恢复并删除）
> 2. **Apply**（恢复但保留）
> 3. **查看内容** — `git stash show -p stash@{N}`
> 4. **删除** — 不恢复，直接删除
> 5. **取消**

```bash
# 恢复并删除
git stash pop stash@{N}

# 恢复但保留
git stash apply stash@{N}

# 查看搁置内容
git stash show -p stash@{N}

# 删除搁置
git stash drop stash@{N}
```

**Shelve vs Stash 的区别（AS 视角）：**
- AS 的 Shelve 支持多个独立命名的搁置，互不影响
- CLI 用 `git stash` 模拟，通过 `-m` 描述区分不同搁置
- 效果完全等价，Unshelve = Stash Pop/Apply

---

## 文件级Git操作

Android Studio 的文件右键菜单 **Git → ...** 对应的操作：

### Add — 添加文件到版本控制

对应 AS 的 **Git → Add**（新文件首次纳入版本控制）：

```bash
# 添加单个文件
git add <file>

# 添加目录
git add <directory>/

# 添加所有新文件
git add --all
```

### Commit File — 单文件提交

对应 AS 的 **Git → Commit File**：

```bash
git add <file>
git commit -m "<type>(<scope>): <message>"
```

### Revert File — 撤销单文件修改

对应 AS 的 **Git → Rollback**（右键菜单）：

**🔄 询问用户：**
> ⚠️ 确认撤销文件 `<file>` 的所有修改？此操作不可恢复。
> 1. **确认撤销** — 恢复到上次提交的状态
> 2. **取消**

```bash
# 撤销工作区修改
git restore <file>

# 撤销暂存+工作区修改
git restore --staged --worktree <file>

# 恢复到指定提交的状态
git restore --source=<commit> <file>
```

### Show History for File — 查看单文件历史

对应 AS 的 **Git → Show History**：

```bash
# 查看文件的提交历史
git log --oneline -- <file>

# 查看文件历史（含重命名追踪）
git log --oneline --follow -- <file>

# 查看文件每次修改的详细 diff
git log -p -- <file>

# 查看文件每次修改的统计
git log --stat -- <file>
```

### Annotate — 逐行标注

对应 AS 的 **Git → Annotate with Git Blame**（编辑器左侧栏）：

```bash
git blame <file>
git blame -L <start>,<end> <file>
```

详见 [SKILL-history.md → Blame](SKILL-history.md#blame--逐行追溯)。

### Show History for Selection — 选中代码的历史

对应 AS 的 **Git → Show History for Selection**（编辑器中选中代码后右键）：

```bash
# 查看指定行范围的变更历史
git log -L <start>,<end>:<file>

# 查看指定函数的变更历史（Git 自动识别函数边界）
git log -L :<function-name>:<file>
```

### Add to .gitignore

对应 AS 的 **Git → Add to .gitignore**（右键文件/目录）：

**🔄 询问用户：**
> 将以下内容添加到 `.gitignore`？
> - **目标**：`<file-or-pattern>`
> - **添加到**：
>   1. **项目根 `.gitignore`**（推荐）
>   2. **全局 `.gitignore`** — `~/.gitignore_global`
>   3. **取消**

```bash
# 添加到项目 .gitignore
echo "<pattern>" >> .gitignore
git add .gitignore

# 添加到全局 .gitignore
echo "<pattern>" >> ~/.gitignore_global
git config --global core.excludesFile ~/.gitignore_global

# 如果文件已被跟踪，需要先从索引中移除
git rm --cached <file>
echo "<file>" >> .gitignore
git add .gitignore
git commit -m "chore: add <file> to .gitignore"
```

### Compare with Branch — 文件与其他分支对比

对应 AS 的 **Git → Compare with Branch**：

**🔄 询问用户：**
> 将文件 `<file>` 与哪个分支对比？
> [列出分支列表]

```bash
# 与指定分支对比
git diff <branch> -- <file>

# 与远程分支对比
git diff origin/<branch> -- <file>
```

---

## 快捷操作速查

| 操作 | 命令 | 说明 |
|------|------|------|
| 快速提交全部 | `git add . && git commit -m "msg"` | 暂存全部+提交 |
| 查看状态 | `git status -s` | 精简状态 |
| 撤销暂存 | `git restore --staged <file>` | 从暂存区移除 |
| 撤销工作区修改 | `git restore <file>` | ⚠️ 需确认，不可恢复 |
| 查看最近提交 | `git log --oneline -10` | 最近10条 |
| 查看当前分支 | `git branch --show-current` | 当前分支名 |

## 错误处理

### 通用错误

| 错误信息 | 原因 | 解决 |
|----------|------|------|
| `not a git repository` | 不在 Git 仓库内 | `cd` 到项目根目录 |
| `nothing to commit` | 无变更 | 确认文件已修改并暂存 |
| `pathspec 'xxx' did not match` | 文件路径不存在 | 检查路径拼写 |
| `Permission denied` | 无权限 | 检查 SSH key 或仓库权限 |
| `Connection refused` | 网络问题 | 检查网络和远程 URL |

### 操作中断恢复

检测到未完成的操作时，**🔄 询问用户：**

**Rebase 进行中：**
> ⚠️ 检测到 rebase 操作尚未完成。
> 1. **继续 Rebase** (`git rebase --continue`) — 已解决冲突，继续
> 2. **跳过当前提交** (`git rebase --skip`) — 放弃此提交的变更
> 3. **放弃 Rebase** (`git rebase --abort`) — 回到 rebase 前的状态

**Merge 进行中：**
> ⚠️ 检测到 merge 操作尚未完成。
> 1. **完成 Merge** — 解决冲突后 `git add . && git commit`
> 2. **放弃 Merge** (`git merge --abort`) — 回到 merge 前的状态

**Cherry-pick 进行中：**
> ⚠️ 检测到 cherry-pick 操作尚未完成。
> 1. **继续 Cherry-pick** (`git cherry-pick --continue`)
> 2. **放弃 Cherry-pick** (`git cherry-pick --abort`)

## 模块导航

- **分支管理**（创建/切换/删除/重命名/跟踪）→ [SKILL-branch.md](SKILL-branch.md)
- **合并与变基**（Merge/Rebase/Cherry-pick/冲突解决）→ [SKILL-merge.md](SKILL-merge.md)
- **历史与标签**（Log/Blame/Diff/Tag/筛选/对比）→ [SKILL-history.md](SKILL-history.md)
- **高级操作**（Stash/Reset/Revert/Clean/Patch/Submodule/Hooks/GPG）→ [SKILL-advanced.md](SKILL-advanced.md)
- **使用示例** → [examples.md](examples.md)

### VCS 操作快捷入口（对应 AS 的 VCS Operations Popup — Alt+`）

**🔄 当用户输入模糊的 Git 指令时，主动提供操作菜单：**
> Git 操作：
> 1. **Commit** — 提交变更
> 2. **Push** — 推送到远程
> 3. **Pull / Update** — 拉取远程更新
> 4. **Branches** — 分支管理
> 5. **Merge** — 合并分支
> 6. **Stash / Shelve** — 暂存/搁置变更
> 7. **Log / History** — 查看历史
> 8. **Rollback** — 回退/撤销
> 9. **其他** — 输入具体操作
