# 高级操作

蒸馏 Android Studio 的 Stash、Reset、Revert、Clean、Patch、Submodule、Git Hooks、GPG 签名、SSH/Credential 等高级 Git 操作。

## Stash — 暂存工作区

### 保存 Stash

**🔄 询问用户（对应 AS 的 Stash Changes 对话框）：**

先在对话中列出变更文件并询问 Stash 描述信息（自由文本），然后通过 `ask_user_question` 提供包含范围选项（question='暂存范围？'）：
> - **仅已跟踪文件**（默认） — 只暂存已跟踪文件的修改
> - **含未跟踪文件** — `git stash -u`
> - **含所有文件** — 包括 .gitignore 忽略的文件

```bash
# 暂存所有已跟踪文件的修改（工作区+暂存区）
git stash
git stash push -m "描述信息"

# 包含未跟踪文件
git stash -u
git stash push -u -m "含未跟踪文件"

# 包含所有文件（含 .gitignore 忽略的文件）
git stash -a

# 仅暂存指定文件
git stash push -m "部分暂存" -- <file1> <file2>

# 交互式选择要暂存的内容
git stash push -p
```

### 查看 Stash

**🔄 询问用户（列出 Stash 列表）：**

先执行 `git stash list` 获取列表，通过 `ask_user_question` 提供可点击的 stash 选项（label=stash 描述，description=时间+分支），用户点击即可选择要操作的 stash。

```bash
# 列出所有 stash
git stash list

# 查看最新 stash 的内容
git stash show

# 查看 stash 的详细 diff
git stash show -p
git stash show -p stash@{N}

# 查看指定 stash
git stash show stash@{N}
```

### 恢复 Stash

**🔄 询问用户（对应 AS 的 Unstash Changes 对话框）：**

先执行 `git stash list` 获取列表，通过 `ask_user_question` 提供可点击的 stash 选项让用户选择要恢复的 stash。

选择 stash 后，再通过 `ask_user_question` 提供恢复方式选项（question='选择恢复方式'）：
> - **Pop**（默认）— 恢复并从列表删除
> - **Apply** — 恢复但保留在列表中
> - **恢复到新分支** — 避免与当前分支冲突

**Stash 恢复冲突时：**

通过 `ask_user_question` 提供冲突处理选项（question='恢复 stash 时产生冲突！'）：
> - **解决冲突** — 手动编辑冲突文件
> - **恢复到新分支** — `git stash branch <new-branch>`
> - **放弃恢复** — stash 仍保留在列表中

```bash
# 恢复最新 stash 并从列表删除
git stash pop

# 恢复最新 stash 但保留在列表中
git stash apply

# 恢复指定 stash
git stash pop stash@{N}
git stash apply stash@{N}

# 恢复到新分支（解决 stash 与当前分支冲突）
git stash branch <new-branch> stash@{N}
```

### 删除 Stash

**🔄 询问用户（对应 AS 的 Drop Stash 确认）：**

通过 `ask_user_question` 提供删除选项（question='确认删除 stash@{N}: <描述信息>？⚠️ 删除后不可恢复'）：
> - **删除** — 删除这个 stash
> - **清空全部** — 删除所有 stash（⚠️ 极危险）
> - **取消**

```bash
# 删除指定 stash
git stash drop stash@{N}

# 清空所有 stash（⚠️ 不可恢复）
git stash clear
```

### Stash 典型场景

**场景1：临时切换分支处理紧急事务**
```bash
git stash push -m "feature/xxx 进行中"
git switch hotfix/urgent
# ... 处理完紧急事务 ...
git switch feature/xxx
git stash pop
```

**场景2：拉取远程更新前暂存本地修改**
```bash
git stash push -m "拉取前暂存"
git pull --rebase
git stash pop
# 如果有冲突，手动解决
```

---

## Reset — 重置

### 三种模式

**🔄 询问用户（对应 AS 的 Reset HEAD 对话框）：**

通过 `ask_user_question` 提供重置模式选项（question='重置到 <commit>，请选择模式'）：
> - **Soft** — 仅移动 HEAD，保留暂存区和工作区（安全）
> - **Mixed** — 移动 HEAD + 清空暂存区，保留工作区（安全）
> - **Hard** — 全部重置，丢弃所有变更（⚠️ 危险）

**选择 Hard 模式时的二次确认：**

列出将被丢弃的文件变更，通过 `ask_user_question` 提供确认选项（question='⛔ Hard Reset 会丢失所有未提交的修改！'）：
> - **确认 Hard Reset** — 我了解风险
> - **改用 Soft/Mixed** — 保留代码
> - **取消**

**Reset 已推送提交的警告：**

通过 `ask_user_question` 提供选项（question='⚠️ 目标提交已推送到远程！Reset 后需要 force push'）：
> - **继续 Reset** — 这是我的个人分支
> - **改用 Revert** — 更安全，不改写历史
> - **取消**

```bash
# soft：仅移动 HEAD，保留暂存区和工作区
git reset --soft <target>

# mixed（默认）：移动 HEAD + 清空暂存区，保留工作区
git reset <target>
git reset --mixed <target>

# hard：移动 HEAD + 清空暂存区 + 清空工作区（⚠️ 丢失修改）
git reset --hard <target>
```

**三种模式对比：**

| 模式 | HEAD | 暂存区 | 工作区 | 用途 |
|------|------|--------|--------|------|
| `--soft` | 移动 | 保留 | 保留 | 合并多个提交为一个 |
| `--mixed` | 移动 | 清空 | 保留 | 取消暂存，重新选择 |
| `--hard` | 移动 | 清空 | 清空 | 彻底回退，丢弃所有变更 |

### 常用 Reset 操作

```bash
# 撤销最近 N 个提交，但保留代码（重新组织提交）
git reset --soft HEAD~<N>

# 取消所有暂存（回到 git add 之前）
git reset HEAD
git reset  # 等价

# 取消特定文件的暂存
git restore --staged <file>  # 推荐
git reset HEAD -- <file>     # 传统方式

# 回退到指定提交（⚠️ 丢失后续所有变更）
git reset --hard <commit-hash>

# 回退到远程分支状态（丢弃本地所有修改）
git reset --hard origin/<branch>
```

### Reset 安全提示

- `--soft` 和 `--mixed` **安全**，不会丢失代码
- `--hard` **危险**，会丢失未提交的修改
- 已推送的提交被 reset 后，需要 `--force` 推送，影响其他协作者
- 已 reset 的提交可通过 `git reflog` 找回（30天内）

---

## Revert — 撤销提交

与 Reset 不同，Revert 通过**创建新提交**来撤销，不改写历史。

**🔄 询问用户（对应 AS 的 Revert Commit 确认）：**

通过 `ask_user_question` 提供撤销选项（question='撤销提交 <hash>: <message>，将创建新提交来反向撤销'）：
> - **Revert 并自动提交** — 直接生成撤销提交
> - **Revert 不提交** — 仅应用变更到工作区，稍后手动提交

**撤销合并提交时的额外询问：**

通过 `ask_user_question` 提供选项（question='⚠️ 这是一个合并提交，需要指定保留哪个父提交'）：
> - **保留主分支** (parent 1) — 撤销合并进来的变更（最常见）
> - **保留合入分支** (parent 2) — 撤销主分支的变更（罕见）

```bash
# 撤销指定提交
git revert <commit-hash>

# 撤销但不自动提交（可以一次撤销多个后再统一提交）
git revert --no-commit <commit-hash>

# 撤销多个连续提交
git revert <oldest-hash>..<newest-hash>

# 撤销合并提交（需指定保留哪个父提交，通常是 1）
git revert -m 1 <merge-commit-hash>
```

### Revert 控制

```bash
# 继续（解决冲突后）
git revert --continue

# 放弃
git revert --abort
```

### Reset vs Revert 选择

**🔄 当用户要求“回退”时主动询问：**

通过 `ask_user_question` 提供回退方式选项（question='你想要回退/撤销提交，请选择方式'）：
> - **Revert**（推荐）— 创建新提交撤销，安全不改写历史
> - **Reset Soft** — 回退但保留代码在暂存区
> - **Reset Hard** — 彻底回退，丢弃所有变更（⚠️ 危险）

| 场景 | 推荐 | 原因 |
|------|------|------|
| 未推送的提交 | `reset` | 干净，不留痕迹 |
| 已推送的提交 | `revert` | 安全，不改写共享历史 |
| 合并提交 | `revert -m 1` | 唯一安全方式 |
| 整理本地提交 | `reset --soft` | 重新组织提交 |

---

## Clean — 清理未跟踪文件

**🔄 询问用户（对应 AS 的 Clean 操作）：**

先执行 `git clean -n` 预览将被删除的文件，在对话中展示后，通过 `ask_user_question` 提供删除范围选项（question='⚠️ 以上未跟踪文件将被删除，不可恢复！'）：
> - **仅未跟踪文件** — `git clean -f`
> - **未跟踪文件+目录** — `git clean -fd`
> - **含 .gitignore 忽略的文件** — `git clean -fdx`（⛔ 极危险）

```bash
# 预览将被删除的文件（dry-run）
git clean -n

# 删除未跟踪的文件
git clean -f

# 删除未跟踪的文件和目录
git clean -fd

# 包括 .gitignore 忽略的文件
git clean -fdx

# 交互式选择
git clean -i
```

**⚠️ Clean 是不可恢复的，务必先 `-n` 预览！**

---

## Restore — 恢复文件

Git 2.23+ 推荐使用 `restore` 替代部分 `checkout` 和 `reset` 操作：

**🔄 询问用户（对应 AS 的 Rollback/Discard Changes 确认）：**

列出将被恢复的文件及变更摘要，通过 `ask_user_question` 提供确认选项（question='⚠️ 确认丢弃以下文件的修改？此操作不可恢复！'）：
> - **确认丢弃** — 恢复到上次提交的状态
> - **取消** — 保留修改

```bash
# 撤销工作区的修改（恢复到暂存区状态）
git restore <file>

# 撤销暂存（从暂存区移除，保留工作区修改）
git restore --staged <file>

# 恢复文件到指定提交的状态
git restore --source=<commit-hash> <file>

# 同时撤销暂存和工作区修改（恢复到上次提交）
git restore --staged --worktree <file>
```

---

## Reflog — 操作日志（后悔药）

**🔄 当用户想找回丢失的提交/分支时询问：**

通过 `ask_user_question` 提供选项（question='想要找回什么？'）：
> - **误操作的 reset --hard** — 从 reflog 找回丢弃的提交
> - **被删除的分支** — 找到分支最后的提交并重建
> - **被 rebase 覆盖的提交** — 找到 rebase 前的状态
> - **查看操作历史** — 仅查看 reflog

```bash
# 查看所有 HEAD 移动记录
git reflog

# 查看指定分支的 reflog
git reflog show <branch>

# 恢复到 reflog 中的某个状态
git reset --hard HEAD@{N}

# 从 reflog 创建新分支（找回被删的分支/提交）
git checkout -b <recovery-branch> HEAD@{N}
```

**Reflog 可以救回的操作：**
- 误操作的 `reset --hard`
- 被删除的分支
- 被 rebase 覆盖的提交
- 任何导致提交"消失"的操作

**注意：** Reflog 记录默认保留 90 天，过期后无法恢复。

---

## Worktree — 多工作树

Android Studio 不直接支持，但是处理多分支并行开发的利器：

### 创建 Worktree

**🔄 询问用户（创建多工作树）：**

先执行 `git branch -a` 获取分支列表，通过 `ask_user_question` 提供可点击的分支选项（label=分支名，description=本地/远程），用户点击选择要创建工作树的分支。

选择分支后，在对话中询问工作目录路径（自由文本）和是否创建新分支。

### 管理 Worktree

**🔄 询问用户（列出/删除工作树）：**

先执行 `git worktree list` 获取列表，通过 `ask_user_question` 提供可点击的工作树选项（label=分支名，description=路径+状态）。

选择工作树后，通过 `ask_user_question` 提供操作选项：
> - **删除工作树** — 移除选中的工作树
> - **清理失效工作树** — `git worktree prune`

```bash
# 为其他分支创建独立工作目录
git worktree add <path> <branch>

# 创建新分支的工作树
git worktree add -b <new-branch> <path> <base>

# 列出所有工作树
git worktree list

# 删除工作树
git worktree remove <path>

# 清理失效的工作树
git worktree prune
```

**典型场景：** 在不切换分支的情况下，同时查看/编辑多个分支的代码。

---

## Patch — 补丁创建与应用

Android Studio 的 **VCS → Patch → Create Patch / Apply Patch** 等价操作。

### 创建 Patch

**🔄 询问用户（对应 AS 的 Create Patch 对话框）：**

通过 `ask_user_question` 提供补丁来源选项（question='创建补丁文件，选择来源'）：
> - **工作区变更** — 未提交的修改
> - **指定提交范围** — 从 commit1 到 commit2
> - **指定文件的变更** — 仅部分文件

选择后在对话中询问保存路径（自由文本，默认 `./changes.patch`）。

```bash
# 工作区变更生成 patch
git diff > changes.patch

# 暂存区变更生成 patch
git diff --cached > staged.patch

# 指定提交范围生成 patch
git diff <commit1> <commit2> > range.patch

# 指定文件的变更
git diff -- <file1> <file2> > partial.patch

# 将提交导出为 patch 文件（含提交信息）
git format-patch -<N>                    # 最近 N 个提交
git format-patch <commit1>..<commit2>    # 指定范围
git format-patch -o <output-dir> HEAD~3  # 输出到指定目录
```

### 应用 Patch

**🔄 询问用户（对应 AS 的 Apply Patch 对话框）：**

先在对话中询问补丁文件路径（自由文本），然后通过 `ask_user_question` 提供应用方式选项（question='选择应用方式'）：
> - **直接应用** (apply) — 仅修改文件，不创建提交
> - **应用并提交** (am) — 应用 format-patch 生成的补丁，保留提交信息
> - **预览** (dry-run) — 仅检查能否应用

```bash
# 预览 patch 是否能应用
git apply --check <file.patch>

# 应用 patch（仅修改文件，不提交）
git apply <file.patch>

# 应用到暂存区
git apply --cached <file.patch>

# 应用 format-patch 生成的补丁（保留提交信息）
git am <file.patch>
git am *.patch             # 批量应用

# patch 应用失败（有冲突）时
git apply --3way <file.patch>   # 尝试三路合并

# am 失败时
git am --abort              # 放弃
git am --skip               # 跳过当前补丁
git am --continue           # 解决冲突后继续
```

### Patch 管理

```bash
# 查看 patch 内容摘要
git apply --stat <file.patch>

# 反向应用（撤销 patch）
git apply -R <file.patch>
```

---

## Submodule — 子模块

Android Studio 自动识别和管理 Git 子模块，以下是 CLI 等价操作。

### 添加子模块

**🔄 询问用户：**
> 添加子模块：
> - **仓库 URL**：
> - **本地路径**：（默认：仓库名）
> - **指定分支**：（可选）

```bash
# 添加子模块
git submodule add <url> <path>

# 添加并指定分支
git submodule add -b <branch> <url> <path>

# 提交子模块变更
git add .gitmodules <path>
git commit -m "chore: add submodule <name>"
```

### 初始化与更新

```bash
# 克隆后初始化子模块
git submodule init
git submodule update

# 或一步到位
git submodule update --init --recursive

# 更新子模块到远程最新
git submodule update --remote

# 更新所有子模块
git submodule update --remote --recursive

# 查看子模块状态
git submodule status
```

### 删除子模块

**🔄 询问用户：**

通过 `ask_user_question` 提供确认选项（question='确认删除子模块 <path>？此操作将移除子模块的所有引用'）：
> - **确认删除**
> - **取消**

```bash
# 1. 删除子模块配置
git submodule deinit -f <path>

# 2. 删除 .git/modules 中的缓存
git rm -f <path>

# 3. 删除缓存目录（如果存在）
# rm -rf .git/modules/<path>

# 4. 提交
git commit -m "chore: remove submodule <name>"
```

### 子模块常用操作

```bash
# 在所有子模块中执行命令
git submodule foreach 'git pull origin main'
git submodule foreach 'git status'

# 查看子模块 diff
git diff --submodule

# 子模块切换到指定提交
cd <submodule-path>
git checkout <commit-hash>
cd ..
git add <submodule-path>
git commit -m "chore: update submodule to <version>"
```

---

## GPG 签名

Android Studio 支持 GPG 签名提交（Sign-off / GPG Sign）。

### 配置 GPG 签名

**🔄 询问用户（对应 AS 的 Settings → Version Control → Git → GPG 配置）：**

先读取 `git config user.signingkey` 展示当前状态，通过 `ask_user_question` 提供配置选项（question='GPG 签名配置'）：
> - **选择已有 GPG Key** — 从已有密钥中选择
> - **查看可用密钥列表** — 列出所有 GPG 密钥
> - **开启/关闭自动签名** — 所有提交和标签自动签名
> - **跳过** — 不配置签名

```bash
# 查看已有 GPG key
gpg --list-secret-keys --keyid-format=long

# 配置 Git 使用 GPG key
git config --global user.signingkey <GPG-KEY-ID>

# 开启自动签名
git config --global commit.gpgsign true
git config --global tag.gpgsign true

# 关闭自动签名
git config --global commit.gpgsign false
git config --global tag.gpgsign false
```

### GPG 签名提交

```bash
# 单次签名提交
git commit -S -m "<message>"

# Sign-off（添加 Signed-off-by 行）
git commit -s -m "<message>"

# 签名 + Sign-off
git commit -S -s -m "<message>"

# 验证提交签名
git log --show-signature -1

# 验证标签签名
git tag -v <tag-name>
```

### 签名标签

```bash
# 创建签名标签
git tag -s <tag-name> -m "<message>"

# 验证
git tag -v <tag-name>
```

---

## Git Hooks — 钩子

Android Studio 自动识别且尊重项目的 Git Hooks，以下是 CLI 管理方式。

### 常用 Hooks

| Hook | 触发时机 | 典型用途 |
|------|----------|----------|
| `pre-commit` | commit 前 | 代码格式化、lint、单元测试 |
| `commit-msg` | 编辑提交信息后 | 校验 commit message 格式 |
| `pre-push` | push 前 | 运行测试套件 |
| `post-merge` | merge 后 | 自动安装依赖 |
| `post-checkout` | checkout 后 | 自动安装依赖 |
| `prepare-commit-msg` | 提交信息编辑器打开前 | 自动填充模板 |

### 管理 Hooks

```bash
# Hooks 存储位置
ls .git/hooks/

# 查看当前配置的 hooks 目录
git config core.hooksPath

# 设置自定义 hooks 目录（团队共享）
git config core.hooksPath .githooks

# 创建 pre-commit hook 示例
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/sh
# 提交前运行 lint
flutter analyze
if [ $? -ne 0 ]; then
  echo "❌ Lint 失败，请修复后再提交"
  exit 1
fi
EOF
chmod +x .git/hooks/pre-commit
```

### 跳过 Hooks

**🔄 询问用户（当 hook 失败时）：**

在对话中展示 hook 错误信息，通过 `ask_user_question` 提供选项（question='⚠️ pre-commit hook 执行失败，提交被拒绝'）：
> - **修复问题后重新提交**（推荐）
> - **跳过 hook 提交** — `git commit --no-verify`
> - **取消提交**

```bash
# 跳过 pre-commit 和 commit-msg hook
git commit --no-verify -m "<message>"

# 跳过 pre-push hook
git push --no-verify
```

---

## SSH 与 Credential 配置

Android Studio 的 **Settings → Version Control → Git** 配置等价操作。

### SSH Key 配置

**🔄 询问用户（对应 AS 的 Settings → Version Control → Git → SSH executable 配置）：**

先读取 `ls ~/.ssh/` 和 `ssh -T git@github.com` 展示当前状态，通过 `ask_user_question` 提供配置选项（question='SSH 配置'）：
> - **生成新 SSH Key** — 创建 ed25519 密钥对
> - **添加到 ssh-agent** — 将已有密钥加载到 agent
> - **测试连接** — 验证 SSH 连接到 GitHub/Gitee
> - **查看公钥** — 复制到代码托管平台
> - **跳过** — 不修改 SSH 配置

```bash
# 检查现有 SSH key
ls -la ~/.ssh/

# 生成新的 SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

# 添加到 ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 测试连接
ssh -T git@github.com
ssh -T git@gitee.com

# 查看公钥（复制到平台配置）
cat ~/.ssh/id_ed25519.pub
```

### Credential 配置

**🔄 询问用户（对应 AS 的 Settings → Version Control → Git → Credential Helper 配置）：**

先读取 `git config credential.helper` 展示当前配置，通过 `ask_user_question` 提供凭据存储选项（question='凭据存储方式'）：
> - **macOS 钥匙串** — `osxkeychain`（推荐 macOS 用户）
> - **内存缓存** — `cache`（默认15分钟过期）
> - **内存缓存（自定义时长）** — 指定缓存秒数
> - **永久存储** — `store`（明文保存，⚠️ 不推荐）
> - **清除已缓存凭据** — 清空当前缓存
> - **跳过** — 不修改凭据配置

```bash
# 查看当前 credential helper
git config --global credential.helper

# macOS: 使用钥匙串
git config --global credential.helper osxkeychain

# Linux: 缓存到内存（默认15分钟）
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=3600'

# 永久存储（明文，不推荐）
git config --global credential.helper store

# 清除缓存的凭据
git credential-cache exit
```

### HTTPS vs SSH 切换

**🔄 询问用户：**

先读取 `git remote -v` 展示当前远程 URL，通过 `ask_user_question` 提供切换选项（question='远程仓库协议切换'）：
> - **切换到 SSH** — 使用 SSH 密钥认证
> - **切换到 HTTPS** — 使用用户名/密码认证
> - **保持不变**

```bash
# 查看当前远程 URL
git remote -v

# 从 HTTPS 切换到 SSH
git remote set-url origin git@github.com:<user>/<repo>.git

# 从 SSH 切换到 HTTPS
git remote set-url origin https://github.com/<user>/<repo>.git
```

---

## Git 配置管理

Android Studio 的 **Settings → Version Control → Git** 等价操作。

**🔄 询问用户（对应 AS 的 Settings → Version Control → Git 配置面板）：**

先执行 `git config --list` 读取当前配置，在对话中展示当前配置值，然后通过 `ask_user_question`（multiSelect=true）提供可点击的配置项选项（question='选择要修改的配置项'）：
> - **用户名** (user.name) — 当前: [agent 读取展示]
> - **邮箱** (user.email) — 当前: [agent 读取展示]
> - **默认分支名** (init.defaultBranch) — 当前: [agent 读取展示]
> - **默认编辑器** (core.editor) — 当前: [agent 读取展示]
> - **换行符处理** (core.autocrlf) — 当前: [agent 读取展示]
> - **Pull 策略** (pull.rebase) — 当前: [agent 读取展示]
> - **自动 GPG 签名** (commit.gpgsign) — 当前: [agent 读取展示]
> - **查看全部配置** — 列出所有 git config

用户点击选择后，在对话中询问新值（自由文本）。

```bash
# 查看所有配置
git config --list --show-origin

# 查看全局配置
git config --global --list

# 设置用户信息
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"

# 设置默认分支名
git config --global init.defaultBranch main

# 设置默认编辑器
git config --global core.editor "code --wait"

# 设置换行符处理
git config --global core.autocrlf input    # macOS/Linux
git config --global core.autocrlf true     # Windows

# 设置 diff 工具
git config --global diff.tool vscode
git config --global difftool.vscode.cmd 'code --wait --diff $LOCAL $REMOTE'

# 设置 merge 工具
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'
```

## Git Archive — 导出项目

对应 AS 的 **Git → Export** 功能：

**🔄 询问用户（对应 AS 的 Export 对话框）：**

通过 `ask_user_question` 提供导出内容选项（question='导出项目归档，选择导出内容'）：
> - **当前 HEAD** — 导出当前分支最新代码
> - **指定分支/标签/提交** — 指定版本
> - **指定子目录** — 仅导出部分目录

选择后，通过 `ask_user_question` 提供格式选项（question='选择导出格式'）：
> - **tar.gz**（默认）
> - **zip**
> - **tar**

最后在对话中询问输出路径（自由文本）。

```bash
# 导出当前 HEAD 为 tar.gz
git archive --format=tar.gz --prefix=<project-name>/ HEAD -o <output>.tar.gz

# 导出为 zip
git archive --format=zip --prefix=<project-name>/ HEAD -o <output>.zip

# 导出指定分支/标签
git archive --format=tar.gz <branch-or-tag> -o <output>.tar.gz

# 导出指定子目录
git archive --format=tar.gz HEAD:<subdir>/ -o <output>.tar.gz

# 导出并排除某些文件（使用 .gitattributes）
# 在 .gitattributes 中添加：test/ export-ignore
git archive --format=tar.gz HEAD -o <output>.tar.gz
```

## 操作安全等级总结

| 操作 | 安全等级 | 可恢复性 | 说明 |
|------|----------|----------|------|
| `stash` | 安全 | `stash pop/apply` | 可随时恢复 |
| `reset --soft` | 安全 | 代码仍在暂存区 | 不丢失任何内容 |
| `reset --mixed` | 安全 | 代码仍在工作区 | 不丢失任何内容 |
| `revert` | 安全 | 新提交可再次 revert | 不改写历史 |
| `restore` | 中等 | 暂存区有备份时可恢复 | 工作区修改可能丢失 |
| `apply patch` | 安全 | `apply -R` 反向应用 | 可撤销 |
| `reset --hard` | 危险 | `reflog`（30天内） | 丢弃所有未提交修改 |
| `clean -f` | 危险 | 不可恢复 | 永久删除未跟踪文件 |
| `clean -fdx` | 极危险 | 不可恢复 | 连忽略文件一起删除 |
