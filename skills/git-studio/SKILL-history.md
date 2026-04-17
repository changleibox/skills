# 历史查看与标签

蒸馏 Android Studio 的 Git Log、Log 筛选面板、Annotate (Blame)、Diff、两提交对比、Tag 操作。

## Log — 提交日志

### 基础查看

```bash
# 最近 N 条提交（精简）
git log --oneline -<N>

# 图形化分支拓扑
git log --oneline --graph --all --decorate
```

#### ⚠️ GUI 强项：可视化分支图

Android Studio 的图形化分支拓扑在终端中难以完全还原，以下是 CLI 最佳实践：

**推荐全局别名（一次配置，永久使用）：**

```bash
# 简洁分支图（最常用）
git config --global alias.lg "log --oneline --graph --all --decorate -20"
# 使用：git lg

# 带时间和作者的详细分支图
git config --global alias.lga "log --graph --all --decorate --format='%C(auto)%h %C(blue)%an %C(green)%ar %C(reset)%s%C(auto)%d'"
# 使用：git lga

# 只看分支合并点（简化拓扑，适合复杂仓库）
git config --global alias.lgs "log --oneline --graph --all --simplify-by-decoration"
# 使用：git lgs
```

**Agent 增强查看（对特定场景的替代）：**

```bash
# 查看某分支与主分支的分叉/合并关系
git log --oneline --graph main..feature/xxx

# 查看所有分支的最新提交（代替 AS 左侧分支列表）
git branch -a -v --sort=-committerdate

# 查看分支是否已合并
git branch --merged main
git branch --no-merged main

# 查看两个分支的分叉点
git merge-base main feature/xxx
```

**🔄 Agent 可主动提供：**
- 执行 `git lg` 后解读 ASCII 图，用自然语言总结分支关系
- 回答“XX 分支是从哪里分出来的”“哪些分支还没合并”等问题
- 生成 Mermaid 分支图辅助理解复杂拓扑

```

# 详细信息（含 diff 统计）
git log --stat -<N>

# 显示完整 diff
git log -p -<N>
```

### 筛选查看

#### 🔍 Log 筛选面板（对应 AS 的 Git Log 左侧筛选栏）

Android Studio Git Log 窗口左侧有强大的筛选面板，以下是 agent 辅助的等价实现：

**🔄 询问用户（对应 AS 的 Log Filter Panel）：**
> 🔍 日志筛选条件（可组合）：
> | # | 筛选项 | 当前值 |
> |---|---------|--------|
> | 1 | **分支** | 全部 |
> | 2 | **作者** | 全部 |
> | 3 | **日期范围** | 不限 |
> | 4 | **关键词** | 无 |
> | 5 | **文件路径** | 全部 |
> | 6 | **代码内容** | 无 |
> | 7 | **执行查询** — 用当前条件搜索
> | 8 | **重置筛选** — 清空所有条件
>
> 请选择要设置的筛选项编号：

用户选择筛选项后，根据具体筛选项提供进一步选择：

**选择筛选项 1（分支）时，先执行 `git branch -a` 然后以编号形式展示：**
> 选择要筛选的分支：
> | # | 分支 |
> |---|------|
> | 1 | main |
> | 2 | develop |
> | 3 | feature/xxx |
> | ... | [agent 执行 `git branch -a` 动态填充] |
>
> 请选择分支编号：

agent 根据筛选条件组合生成命令：

```bash
# 示例：筛选作者为张三、本周、包含关键词 "login" 的提交
git log --author="张三" --after="2025-04-14" --grep="login" --oneline

# 示例：筛选指定分支、指定文件的提交
git log feature/user-login --oneline -- src/pages/login.dart

# 示例：筛选包含特定代码变更的提交
git log -S "validatePassword" --oneline
```

**Agent 增强：**
- 组合多个筛选条件时，agent 自动拼接参数
- 查询结果过多时，agent 主动建议缩小范围
- 支持多轮筛选，逐步缩小结果集

```bash
# 按作者筛选
git log --author="<name>" --oneline

# 按日期范围
git log --after="2025-01-01" --before="2025-12-31" --oneline

# 按提交信息关键词
git log --grep="<keyword>" --oneline

# 按文件路径（查看某文件的修改历史）
git log --oneline -- <file-path>

# 按代码变更内容（查找"谁加了/删了这段代码"）
git log -S "<code-string>" --oneline
git log -G "<regex-pattern>" --oneline

# 查看两个分支之间的差异提交
git log <branch1>..<branch2> --oneline
```

### 格式化输出

```bash
# 自定义格式
git log --pretty=format:"%h %an %ar %s" -<N>

# 常用 format 占位符：
#   %h  短哈希    %H  长哈希
#   %an 作者名    %ae 作者邮箱
#   %ar 相对时间  %ad 日期
#   %s  提交信息  %b  正文
```

### 查看单个提交

```bash
# 查看提交的完整信息和 diff
git show <commit-hash>

# 仅查看提交修改的文件列表
git show --name-only <commit-hash>

# 查看统计摘要
git show --stat <commit-hash>
```

### Log 右键上下文菜单（对应 AS 的 Log 提交右键操作）

在 Android Studio 的 Git Log 中右键点击某个提交，会出现以下菜单：

**🔄 询问用户（对应 AS Log 右键菜单）：**
> 选中提交：`<commit-hash>` - `<commit-message>`
> 可执行的操作：
> 1. **Copy Revision Number** — 复制提交哈希
> 2. **Create Tag...** — 基于此提交创建标签
> 3. **New Branch...** — 基于此提交创建分支
> 4. **Checkout Revision** — 检出此提交（进入 Detached HEAD）
> 5. **Reset Current Branch to Here...** — 重置当前分支到此提交
> 6. **Revert Commit** — 撤销此提交的变更
> 7. **Cherry-Pick** — 拣选此提交到当前分支
> 8. **Interactively Rebase from Here** — 从此提交开始交互式变基
> 9. **Select for Compare** — 选择为对比基准
> 10. **Show Diff with Working Tree** — 与工作目录对比
> 11. **取消**

```bash
# 1. Copy Revision Number
git rev-parse <commit-hash>        # 完整哈希
git rev-parse --short <commit-hash> # 短哈希

# 2. Create Tag... → 见下方 Tag 章节
git tag <tag-name> <commit-hash>

# 3. New Branch...
git branch <branch-name> <commit-hash>
git checkout -b <branch-name> <commit-hash>  # 创建并切换

# 4. Checkout Revision
git checkout <commit-hash>
# → 进入 Detached HEAD 状态，见下方警告

# 5. Reset Current Branch to Here... → 见 SKILL-advanced.md Reset 章节
# 会触发 Reset 模式选择对话框

# 6. Revert Commit → 见 SKILL-advanced.md Revert 章节
git revert <commit-hash>

# 7. Cherry-Pick → 见 SKILL-merge.md Cherry-pick 章节
git cherry-pick <commit-hash>

# 8. Interactively Rebase from Here → 见 SKILL-merge.md Interactive Rebase 章节
git rebase -i <commit-hash>^

# 9-10 见下方 Diff 章节
```

**Checkout Revision 警告对话框（对应 AS 的 Detached HEAD 警告）：**

> ⚠️ **即将进入 Detached HEAD 状态！**
> 你正在检出提交 `<commit-hash>`，而不是分支。
> 在此状态下的提交可能会丢失，除非创建新分支。
> 1. **继续 Checkout** — 我了解风险
> 2. **Checkout 并创建新分支** — 基于此提交创建分支（推荐）
> 3. **取消**

```bash
# 继续 Checkout
git checkout <commit-hash>

# Checkout 并创建新分支
git checkout -b <new-branch> <commit-hash>
```

---

## Blame — 逐行追溯

Android Studio 的 "Annotate with Git Blame" 等价：

```bash
# 查看文件每一行的最后修改者
git blame <file>

# 查看指定行范围
git blame -L <start>,<end> <file>

# 忽略空白变更
git blame -w <file>

# 检测行移动和复制（跨文件追溯）
git blame -M <file>   # 检测文件内移动
git blame -C <file>   # 检测跨文件复制
git blame -CCC <file> # 更激进的跨文件检测

# 查看某次提交之前的 blame（追溯更早的修改）
git blame <commit-hash>^ -- <file>
```

**Blame 输出解读：**
```
a1b2c3d4 (张三 2025-03-15 10:30:00 +0800  42) some code here
^-------   ^---  ^-----------------------  ^--  ^-----------
提交哈希    作者   时间                       行号  代码内容
```

**追溯某行代码的完整变更历史：**
```bash
# 找到某行的最后修改提交
git blame -L <line>,<line> <file>

# 查看该提交的详情
git show <commit-hash>

# 继续追溯更早的修改
git blame <commit-hash>^ -L <line>,<line> <file>
```

### Annotate Previous Revision — 递归追溯上一版本

对应 AS 的 **Blame 视图中点击注解行 → Show Diff / Annotate Previous Revision**：

**🔄 询问用户（对应 AS 的 Annotate Previous Revision 操作）：**
> Blame 追溯：行 `<line>` 最后由提交 `<commit-hash>` 修改。
> 进一步操作：
> 1. **Annotate Previous Revision** — 查看此提交之前的 Blame（递归追溯）
> 2. **Show Diff** — 查看此提交的完整变更
> 3. **Copy Revision Number** — 复制提交哈希
> 4. **Annotate Revision** — 查看此提交时的完整 Blame
> 5. **返回当前版本 Blame**
> 6. **取消**

```bash
# Annotate Previous Revision — 查看此行在上一版本的 blame
git blame <commit-hash>^ -- <file>

# 指定行范围的递归追溯
git blame <commit-hash>^ -L <line>,<line> <file>

# Show Diff — 查看该提交的变更
git show <commit-hash> -- <file>

# Annotate Revision — 查看某次提交时的完整 blame
git blame <commit-hash> -- <file>
```

> 💡 **Agent 递归追溯**：当用户连续选择「Annotate Previous Revision」时，agent 自动将 `<commit-hash>` 替换为上一层提交的哈希，实现 AS 中点击注解行不断向前追溯的体验。

---

## Diff — 差异比较

### 工作区差异

```bash
# 工作区 vs 暂存区（未暂存的修改）
git diff

# 暂存区 vs 上次提交（已暂存的修改）
git diff --cached
git diff --staged  # 同义

# 工作区 vs 上次提交（所有修改）
git diff HEAD
```

### 提交间差异

#### Select for Compare — 两提交对比

Android Studio 支持右键提交 **Select for Compare**，再右键另一提交 **Compare with Selected**，以下是 agent 辅助的等价实现：

**🔄 询问用户（对应 AS 的 Select for Compare / Compare with Selected）：**
> 对比两个提交的差异：
> - **提交1**：（输入 hash、分支名或 `HEAD~N`）
> - **提交2**：（输入 hash、分支名或 `HEAD`）
> - **查看方式**：
>   1. **文件列表** — 仅查看变更的文件
>   2. **统计概览** — 各文件增删行数
>   3. **完整 Diff** — 查看所有变更详情
>   4. **指定文件的 Diff** — 只看某个文件

```bash
# 两个提交之间的变更文件列表
git diff <commit1> <commit2> --name-only

# 两个提交之间的统计
git diff <commit1> <commit2> --stat

# 两个提交之间的完整 diff
git diff <commit1> <commit2>

# 两个提交之间指定文件的 diff
git diff <commit1> <commit2> -- <file>
```

#### Show Diff with Working Tree

Android Studio 支持右键提交 **Show Diff with Working Tree**，比较某次提交与当前工作区的差异：

```bash
# 指定提交 vs 当前工作区
git diff <commit>

# 指定提交 vs 当前工作区（仅文件列表）
git diff <commit> --name-only

# 指定提交 vs 当前工作区（指定文件）
git diff <commit> -- <file>

# HEAD vs 工作区（所有未提交的变更）
git diff HEAD
```

### 提交间差异（已有命令补充）

```bash
# 两个提交之间
git diff <commit1> <commit2>

# 两个分支之间
git diff <branch1>..<branch2>

# 只看文件列表
git diff <commit1> <commit2> --name-only

# 只看统计
git diff <commit1> <commit2> --stat

# 只看指定文件的差异
git diff <commit1> <commit2> -- <file>
```

### Diff 显示选项

```bash
# 忽略空白差异
git diff -w

# 逐词差异（而非逐行）
git diff --word-diff

# 显示差异摘要（新增/删除/修改）
git diff --diff-filter=ADM --name-status
# A=Added, D=Deleted, M=Modified, R=Renamed, C=Copied
```

### Compare with Branch — 与其他分支对比

Android Studio 支持右键文件 **Git → Compare with Branch**，或在 Diff 视图中选择分支对比：

**🔄 询问用户（对应 AS 的 Compare with Branch 对话框）：**

先执行 `git branch -a` 获取分支列表，然后以编号形式展示：

> 与哪个分支对比当前分支的差异？
> | # | 分支 |
> |---|------|
> | 1 | main |
> | 2 | develop |
> | 3 | feature/xxx |
> | ... | [agent 执行 `git branch -a` 动态填充] |
>
> 请选择分支编号：
>
> 选择分支后，对比范围：
>   1. **完整分支对比** — 所有文件差异
>   2. **指定文件对比** — 仅对比某个文件
>   3. **取消**

```bash
# 当前分支与目标分支的完整差异
git diff <branch>

# 当前分支与目标分支的差异文件列表
git diff <branch> --name-only

# 当前分支与目标分支的统计
git diff <branch> --stat

# 对比指定文件
git diff <branch> -- <file>

# 对比远程分支
git diff origin/<branch>
```

---

## Tag — 标签管理

### 查看标签

```bash
# 列出所有标签
git tag

# 按模式筛选
git tag -l "v1.*"

# 查看标签详情
git show <tag-name>

# 按时间排序
git tag --sort=-creatordate
```

### 创建标签

**🔄 询问用户（对应 AS 的 New Tag 对话框）：**
> 创建新标签：
> - **标签名称**：（如 `v1.0.0`）
> - **基于哪个提交**？
>
> 先执行 `git log --oneline -15` 获取最近提交，以编号形式展示：
>
> | # | 提交 | 信息 |
> |---|------|------|
> | 1 | `abc1234` | feat: 用户登录 |
> | 2 | `def5678` | fix: 修复样式 |
> | ... | [agent 执行 `git log --oneline -15` 动态填充] | |
>
> 请选择提交编号（默认：1，即当前 HEAD）：
>
> - **标签类型**：
>   1. **附注标签**（推荐）— 含作者/日期/信息
>   2. **轻量标签** — 仅名称指向提交
> - **标签消息**：（附注标签需要）
> - **是否立即推送到远程**？（默认：是）

```bash
# 轻量标签（仅名称指向提交）
git tag <tag-name>
git tag <tag-name> <commit-hash>

# 附注标签（推荐，含作者/日期/信息）
git tag -a <tag-name> -m "<message>"
git tag -a <tag-name> <commit-hash> -m "<message>"
```

**命名约定：** `v<major>.<minor>.<patch>`，如 `v1.2.3`

### 推送标签

```bash
# 推送单个标签
git push origin <tag-name>

# 推送所有标签
git push --tags

# 仅推送附注标签（推荐）
git push --follow-tags
```

### 删除标签

**🔄 询问用户（对应 AS 的 Delete Tag 确认）：**
> 确认删除标签 `<tag-name>`？
> - 标签指向：`<commit>` (<date>)
> 1. **删除本地标签** — 仅删除本地
> 2. **删除本地+远程标签** — 同步删除远程
> 3. **取消**

```bash
# 删除本地标签
git tag -d <tag-name>

# 删除远程标签
git push origin --delete <tag-name>
# 或
git push origin :refs/tags/<tag-name>
```

### 基于标签操作

**🔄 切换到标签时询问用户（对应 AS 的 Checkout Tag 警告）：**
> ⚠️ 切换到标签 `<tag-name>` 会进入 **Detached HEAD** 状态。
> 在此状态下的提交不属于任何分支，可能被丢失。
> 1. **基于标签创建新分支**（推荐）— 在新分支上工作
> 2. **仅查看** — 进入 Detached HEAD，仅浏览代码
> 3. **取消**

```bash
# 切换到标签（进入 detached HEAD）
git checkout <tag-name>

# 基于标签创建新分支
git checkout -b <branch-name> <tag-name>

# 查看两个标签之间的提交
git log <tag1>..<tag2> --oneline
```

---

## 实用组合技

### 查找引入 Bug 的提交

```bash
# 方法1：二分查找
git bisect start
git bisect bad          # 当前版本有 bug
git bisect good <hash>  # 已知无 bug 的版本
# Git 会自动 checkout 中间提交，测试后标记：
git bisect good  # 或 git bisect bad
# 找到后结束
git bisect reset

# 方法2：按代码内容搜索
git log -S "有问题的代码" --oneline
```

### 查看文件在某个时间点的内容

```bash
# 查看文件在某次提交时的内容
git show <commit-hash>:<file-path>

# 查看文件在某个日期的内容
git show $(git rev-list -1 --before="2025-01-01" HEAD):<file-path>
```
