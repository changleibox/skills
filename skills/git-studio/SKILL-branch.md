# 分支管理

蒸馏 Android Studio 的 Branch 面板全部操作。

## 查看分支

```bash
# 查看本地分支（*标记当前分支）
git branch

# 查看所有分支（含远程）
git branch -a

# 查看分支及最后提交
git branch -v

# 查看分支及上游跟踪关系
git branch -vv

# 查看已合并/未合并到当前分支的分支
git branch --merged
git branch --no-merged
```

## 创建分支

**🔄 询问用户（对应 AS 的 New Branch 对话框）：**
> 请提供新分支信息：
> - **分支名称**：（如 `feature/xxx`、`bugfix/xxx`）
> - **基于哪个分支创建**？（默认：当前 HEAD）
>
> 先执行 `git branch -a` 获取分支列表，以编号形式展示：
>
> | # | 分支 | 说明 |
> |---|------|------|
> | 1 | main | 本地 |
> | 2 | develop | 本地 |
> | 3 | HEAD | 当前提交 |
> | ... | [agent 执行 `git branch -a` 动态填充] | |
>
> 请选择分支编号（默认：3，即当前 HEAD）：
>
> - **是否立即切换到新分支**？（默认：是）

```bash
# 基于当前 HEAD 创建
git branch <name>

# 创建并切换
git checkout -b <name>
# 或（推荐，语义更明确）
git switch -c <name>

# 基于指定提交/分支/标签创建
git checkout -b <name> <base>
git switch -c <name> <base>

# 基于远程分支创建本地跟踪分支
git checkout -b <local-name> origin/<remote-name>
git switch -c <local-name> origin/<remote-name>
```

**命名建议（Android Studio 惯例）：**

| 前缀 | 用途 | 示例 |
|------|------|------|
| `feature/` | 新功能 | `feature/user-login` |
| `bugfix/` | Bug修复 | `bugfix/null-pointer-fix` |
| `hotfix/` | 紧急修复 | `hotfix/crash-on-launch` |
| `release/` | 发布准备 | `release/v2.0.0` |
| `refactor/` | 重构 | `refactor/database-layer` |

## 切换分支

**🔄 询问用户（对应 AS 的 Branches Popup 选择分支）：**

先执行 `git branch -a` 获取分支列表，然后以编号形式展示：

> 切换到哪个分支？
> | # | 分支 | 说明 |
> |---|------|------|
> | 1 | main | 本地 |
> | 2 | develop | 本地 |
> | 3 | feature/user-login | 本地 |
> | 4 | remotes/origin/feature/xxx | 远程（将自动创建本地跟踪分支） |
> | ... | [agent 执行 `git branch -a` 动态填充] | |
>
> 请选择分支编号：

```bash
# 切换到已有分支
git checkout <branch>
git switch <branch>

# 切换到上一个分支
git checkout -
git switch -
```

**切换前检查：**

```bash
git status --short
```

- 工作区干净 → 直接切换
- 有未提交变更 → **🔄 询问用户（对应 AS 的 Smart Checkout 对话框）：**

> ⚠️ 当前分支有未提交的变更：
> [列出变更文件]
> 切换到 `<target-branch>` 前需要处理这些变更：
> 1. **Smart Checkout**（推荐）— 自动 stash → 切换 → unstash
> 2. **提交变更** — `git add . && git commit -m "wip: save before switch"` 后切换
> 3. **强制切换** — 带着变更切换（可能失败）
> 4. **取消** — 留在当前分支

**Smart Checkout 实现：**
```bash
git stash push -m "auto-stash before checkout to <target-branch>"
git checkout <target-branch>
git stash pop
```

**Smart Checkout 后 unstash 冲突：**
> ⚠️ 切换成功，但恢复 stash 时产生冲突。
> 1. **手动解决冲突** — 编辑冲突文件后 `git add .`
> 2. **丢弃 stash 的变更** — `git checkout -- .`（变更仍在 stash 中）
> 3. **切回原分支** — 放弃切换

**带着变更切换失败时：**
```
error: Your local changes would be overwritten by checkout
```
**🔄 询问用户：**
> 带着变更切换失败，目标分支与当前变更有冲突。
> 1. **Stash 后切换** — `git stash push -m "..."`
> 2. **提交后切换** — 先 commit 再切换
> 3. **取消** — 留在当前分支

## 删除分支

**🔄 询问用户（对应 AS 的 Delete Branch 确认对话框）：**
> 确认删除分支 `<name>`？
> - 分支状态：[已合并/未合并]
> - 最后提交：`<last commit message>` (<date>)
> 1. **删除** — 删除本地分支
> 2. **删除本地+远程** — 同时删除远程分支
> 3. **取消**

**未合并分支删除警告：**
当分支未合并时 `git branch -d` 会拒绝：
```
error: The branch '<name>' is not fully merged.
```
**🔄 询问用户：**
> ⚠️ 分支 `<name>` 还有未合并的提交！删除后这些提交可能丢失。
> [列出未合并的提交]
> 1. **强制删除** (`git branch -D`) — 我确认不再需要这些提交
> 2. **先合并再删除** — 跳转到合并流程
> 3. **取消** — 保留分支

## 重命名分支

**🔄 询问用户（对应 AS 的 Rename Branch 对话框）：**
> 重命名分支 `<old-name>`，请输入新名称：
> - 是否同步重命名到远程？（默认：是）

```bash
# 重命名当前分支
git branch -m <new-name>

# 重命名指定分支
git branch -m <old-name> <new-name>

# 同步重命名到远程（删旧推新）
git push origin --delete <old-name>
git push -u origin <new-name>
```

## 上游跟踪

```bash
# 设置当前分支的上游
git branch -u origin/<branch>
# 或在推送时设置
git push -u origin <branch>

# 取消上游跟踪
git branch --unset-upstream

# 查看跟踪关系
git branch -vv
```

## 分支右键菜单（对应 AS 的 Branches Popup 右键操作）

Android Studio 右下角分支弹出窗中，右键点击分支会显示完整操作菜单：

**🔄 询问用户（对应 AS 分支右键菜单）：**
> 选中分支：`<branch-name>`
> 可执行的操作：
> 1. **Checkout** — 切换到此分支
> 2. **New Branch from ‘<branch>’...** — 基于此分支创建新分支
> 3. **Compare with Current** — 与当前分支对比
> 4. **Show Diff with Working Tree** — 与工作目录对比
> 5. **Rebase Current onto ‘<branch>’** — 将当前分支变基到此分支
> 6. **Merge ‘<branch>’ into Current** — 将此分支合并到当前
> 7. **Checkout and Rebase onto Current** — 先切换到此分支，再变基到当前
> 8. **Pull into ‘<branch>’ Using Merge/Rebase** — 拉取远程更新
> 9. **Rename...** — 重命名分支
> 10. **Delete** — 删除分支
> 11. **取消**

```bash
# 1. Checkout
git checkout <branch>

# 2. New Branch from '<branch>'...
git checkout -b <new-branch> <branch>

# 3. Compare with Current
git diff HEAD..<branch> --name-only
git log HEAD..<branch> --oneline

# 4. Show Diff with Working Tree
git diff <branch>

# 5. Rebase Current onto '<branch>' → 见 SKILL-merge.md Rebase 章节
git rebase <branch>

# 6. Merge '<branch>' into Current → 见 SKILL-merge.md Merge 章节
git merge <branch>

# 7. Checkout and Rebase onto Current
# 步骤1：记住当前分支名
CURRENT=$(git branch --show-current)
# 步骤2：切换到目标分支
git checkout <branch>
# 步骤3：变基到原分支
git rebase $CURRENT

# 8. Pull into '<branch>' Using Merge
git checkout <branch>
git pull origin <branch>
# Pull into '<branch>' Using Rebase
git checkout <branch>
git pull --rebase origin <branch>

# 9. Rename... → 见上方 "重命名分支" 章节
# 10. Delete → 见上方 "删除分支" 章节
```

## 比较分支

**🔄 询问用户（对应 AS 的 Compare Branches 对话框）：**

先执行 `git branch -a` 获取分支列表，然后以编号形式展示：

> 选择要对比的分支（当前分支：`<current-branch>`）：
> | # | 分支 |
> |---|------|
> | 1 | main |
> | 2 | develop |
> | 3 | feature/xxx |
> | ... | [agent 执行 `git branch -a` 动态填充] |
>
> 请选择要对比的分支编号：

```bash
# 两个分支的差异文件列表
git diff <branch1>..<branch2> --name-only

# 两个分支的详细差异
git diff <branch1>..<branch2>

# branch2 相对于 branch1 的新提交
git log <branch1>..<branch2> --oneline

# 两个分支的共同祖先
git merge-base <branch1> <branch2>
```

## 分支操作最佳实践

1. **及时删除已合并分支**：`git branch --merged | grep -v "main\|master\|develop" | xargs git branch -d`
2. **定期同步远程**：`git fetch --prune` 清理过时的远程跟踪
3. **使用描述性分支名**：遵循 `<type>/<description>` 模式
4. **避免在共享分支上 force push**
5. **切换前确认工作区状态**：养成 `git status` 的习惯
