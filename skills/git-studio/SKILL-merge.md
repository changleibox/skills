# 合并与变基

蒸馏 Android Studio 的 Merge、Rebase、Cherry-pick 及冲突解决全流程。

## Merge — 合并分支

### 合并前询问

**🔄 询问用户（对应 AS 的 Merge into Current 对话框）：**

通过 `ask_user_question` 提供合并策略选项（question='将 <source-branch> 合并到当前分支 <current-branch>，请选择合并策略'）：
> - **Merge** — 创建合并提交，保留分支拓扑（推荐）
> - **Squash and Merge** — 压缩为单个提交，历史更干净
> - **Rebase** — 变基合并，保持线性历史

### 标准合并

```bash
# 将指定分支合并到当前分支
git merge <branch>

# 合并时生成合并提交（即使可以快进）
git merge --no-ff <branch>

# 快进合并（默认，不产生额外提交）
git merge --ff-only <branch>

# 合并时压缩为单次提交
git merge --squash <branch>
```

**合并策略选择：**

| 策略 | 命令 | 适用场景 |
|------|------|----------|
| Fast-forward | `git merge --ff-only` | 目标分支无新提交，保持线性 |
| No-fast-forward | `git merge --no-ff` | 保留分支历史，推荐用于 feature 合并 |
| Squash | `git merge --squash` | 将整个分支压缩为一个提交 |

### Squash 合并流程

```bash
# 1. 切到目标分支
git switch main

# 2. Squash 合并
git merge --squash feature/xxx

# 3. 提交（此时暂存区包含所有变更，需手动提交）
git commit -m "feat: 完成xxx功能"
```

### 放弃合并

```bash
# 合并过程中放弃
git merge --abort

# 合并完成但未提交时重置
git reset --merge
```

---

## Rebase — 变基

### 标准变基

```bash
# 将当前分支变基到目标分支
git rebase <target-branch>

# 变基到指定提交
git rebase <commit-hash>

# 变基时保留合并提交
git rebase --rebase-merges <target-branch>
```

**典型场景：同步主分支最新代码到特性分支**

```bash
# 当前在 feature/xxx 分支
git rebase main

# 等价于 pull --rebase
git pull --rebase origin main
```

### 交互式 Rebase

Android Studio 的 "Interactively Rebase from Here" 等价操作：

```bash
# 交互式变基最近 N 个提交
git rebase -i HEAD~<N>

# 交互式变基到指定提交
git rebase -i <commit-hash>
```

**编辑器中的操作指令：**

| 指令 | 缩写 | 说明 |
|------|------|------|
| `pick` | `p` | 保留提交 |
| `reword` | `r` | 保留提交但修改提交信息 |
| `edit` | `e` | 暂停，允许修改提交内容 |
| `squash` | `s` | 与前一个提交合并，保留两者信息 |
| `fixup` | `f` | 与前一个提交合并，丢弃此提交信息 |
| `drop` | `d` | 删除提交 |

**CLI 替代方案（避免打开编辑器）：**

```bash
# 合并最近 N 个提交为一个（自动 squash）
git reset --soft HEAD~<N>
git commit -m "新的提交信息"

# 修改最近一个提交的信息
git commit --amend -m "新信息"

# 自动 fixup（将当前暂存的变更合入指定提交）
git commit --fixup=<commit-hash>
git rebase -i --autosquash <commit-hash>~1
```

#### ⚠️ GUI 强项：拖拽排序提交

Android Studio 交互式 Rebase 支持拖拽排序提交，以下是 agent 辅助的等价替代——通过逐个点选实现排序：

**🤖 Agent 辅助流程：**

1. 列出待操作的提交列表：
```bash
git log --oneline --reverse HEAD~<N>..HEAD
```

2. **🔄 询问用户（逐个点选排序）：**

   通过 `ask_user_question` 提供可点击的提交选项（label=提交信息，description=commit hash），用户逐个点选确定新顺序（点选顺序 = 最终排序）。

   用户每次点选一个，agent 实时更新剩余列表，再次通过 `ask_user_question` 提供剩余选项，直到所有提交都被选完。

3. Agent 展示最终排序结果并确认：
   > 最终提交顺序（从旧到新）：
   > ```
   > 1. ghi9012 feat: 注册页面
   > 2. abc1234 feat: 用户登录
   > 3. jkl3456 refactor: 抽取工具类
   > 4. def5678 fix: 修复样式
   > 5. mno7890 docs: 更新 README
   > ```
   > ⚠️ 即将对这 5 个提交执行 rebase 重排，操作不可撤销（可通过 reflog 恢复）。
   > 确认执行？(y/n)

4. Agent 自动生成 rebase-todo 并通过 `GIT_SEQUENCE_EDITOR` 免编辑器执行：
```bash
# agent 根据用户点选顺序生成 todo 文件
cat > /tmp/rebase-todo << 'EOF'
pick ghi9012 feat: 注册页面
pick abc1234 feat: 用户登录
pick jkl3456 refactor: 抽取工具类
pick def5678 fix: 修复样式
pick mno7890 docs: 更新 README
EOF

# 通过 GIT_SEQUENCE_EDITOR 直接写入，无需手动编辑
GIT_SEQUENCE_EDITOR="cp /tmp/rebase-todo" git rebase -i HEAD~5
```

**同样支持其他操作的逐个点选：**

点选流程同样适用于 squash、drop、reword 等操作：

- **合并(squash)**：点选要合并的提交编号 → agent 生成 `squash` 指令
- **删除(drop)**：点选要删除的提交编号 → agent 生成 `drop` 指令
- **修改信息(reword)**：点选提交编号 → agent 询问新的提交信息
- **组合操作**：用户描述想要的效果，agent 自动组合指令

### Rebase 控制

```bash
# 继续（解决冲突后）
git rebase --continue

# 跳过当前提交
git rebase --skip

# 放弃整个 rebase
git rebase --abort
```

### Rebase vs Merge 决策

**🔄 当用户意图不明确时，主动询问（对应 AS 的 Git Pull 策略选择）：**

通过 `ask_user_question` 提供合入方式选项（question='将分支 <source> 的变更合入 <target>，请选择方式'）：
> - **Rebase** — 保持线性历史，适合同步主分支更新
> - **Merge** — 保留分支拓扑，适合特性分支合回主分支
> - **Squash Merge** — 压缩为单提交，适合清理历史

| 场景 | 推荐 | 理由 |
|------|------|------|
| 同步主分支到特性分支 | `rebase` | 保持线性历史 |
| 特性分支合回主分支 | `merge --no-ff` | 保留分支信息 |
| 个人分支整理提交 | `rebase -i` | 清理历史 |
| 共享分支 | `merge` | 不改写已推送的历史 |

**黄金法则：不要 rebase 已推送到共享分支的提交。**

**如果用户要求 rebase 已推送的分支，必须警告：**

通过 `ask_user_question` 提供选项（question='⛔ 分支 <branch> 已推送到远程！Rebase 会改写提交历史，完成后需要 force push'）：
> - **继续 Rebase** — 这是我的个人分支，没关系
> - **改用 Merge** — 更安全的方式
> - **取消**

---

## Cherry-pick — 拣选提交

**🔄 询问用户（对应 AS 的 Cherry-pick 操作）：**

通过 `ask_user_question` 提供拣选选项（question='拣选提交到当前分支 <current-branch>，请确认'）：
> - **Cherry-pick 并自动提交** — 直接应用并生成新提交
> - **Cherry-pick 不提交** — 仅应用变更到暂存区，稍后手动提交

```bash
# 拣选单个提交
git cherry-pick <commit-hash>

# 拣选多个提交
git cherry-pick <hash1> <hash2> <hash3>

# 拣选一个范围（不含起始，含结束）
git cherry-pick <start-hash>..<end-hash>

# 拣选但不自动提交（仅应用变更到暂存区）
git cherry-pick --no-commit <commit-hash>
```

### Cherry-pick 控制

```bash
# 继续（解决冲突后）
git cherry-pick --continue

# 跳过当前提交
git cherry-pick --skip

# 放弃
git cherry-pick --abort
```

### 查找要拣选的提交

```bash
# 查看其他分支的提交列表
git log <branch> --oneline -20

# 查看提交的具体内容
git show <commit-hash>

# 查找包含特定关键词的提交
git log --all --grep="关键词" --oneline
```

---

## 冲突解决

### 识别冲突

```bash
# 查看冲突文件列表
git diff --name-only --diff-filter=U

# 查看冲突状态
git status
```

冲突文件中的标记：
```
<<<<<<< HEAD (当前分支)
当前分支的代码
=======
传入分支的代码
>>>>>>> branch-name (合并来源)
```

### 解决策略

**🔄 检测到冲突时询问用户（对应 AS 的 Conflicts 对话框）：**

列出冲突文件后，通过 `ask_user_question` 提供解决方式选项（question='⚠️ 发现 N 个文件冲突'）：
> - **逐文件解决**（推荐）— 打开每个文件，AI 分析并建议合并方案
> - **全部接受当前分支** (Accept Ours) — 丢弃传入的变更
> - **全部接受传入分支** (Accept Theirs) — 丢弃当前的变更
> - **放弃操作** — abort 回到操作前状态

**对单个文件的冲突，通过 `ask_user_question` 提供处理选项（question='文件 <filename> 冲突'）：**
> - **AI 智能合并** — 分析双方意图，生成合并结果
> - **接受当前分支** (Accept Ours)
> - **接受传入分支** (Accept Theirs)
> - **跳过此文件** — 稍后手动处理

### 冲突解决后续

**🔄 所有冲突解决后通过 `ask_user_question` 提供确认选项（question='✅ 所有冲突已解决，请确认'）：**
> - **继续** — 完成合并/变基/拣选操作
> - **查看合并结果** — 先检查合并后的内容再继续
> - **放弃** — abort 回到操作前状态

```bash
# 暂存所有已解决的文件
git add .

# 根据当前操作继续
git merge --continue      # 合并冲突
git rebase --continue     # 变基冲突
git cherry-pick --continue # 拣选冲突

# 确认没有剩余冲突
git diff --name-only --diff-filter=U
```

### 预防冲突

```bash
# 合并前先预览差异
git diff <current-branch>..<target-branch> --stat

# 使用 dry-run 检查（仅 merge 支持）
git merge --no-commit --no-ff <branch>
git merge --abort  # 预览后放弃

# 频繁同步上游减少冲突范围
git pull --rebase origin main
```

## 操作安全总结

| 操作 | 可逆性 | 影响远程 | 风险等级 |
|------|--------|----------|----------|
| `merge` | `--abort` 或 `reset` | 推送后不可逆 | 低 |
| `merge --squash` | `reset` | 推送后不可逆 | 低 |
| `rebase` | `--abort` 或 `reflog` | **改写历史** | 中 |
| `rebase -i` | `--abort` 或 `reflog` | **改写历史** | 高 |
| `cherry-pick` | `--abort` 或 `revert` | 推送后需 revert | 低 |
