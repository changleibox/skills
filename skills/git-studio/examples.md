# Git Studio 使用示例

## 示例1：日常开发提交流程

**用户说：** "提交一下代码"

```bash
# 1. 检查状态
git status

# 2. 暂存变更
git add .

# 3. 查看暂存内容
git diff --cached --stat

# 4. 提交
git commit -m "feat(goods): 添加商品分类筛选功能"

# 5. 推送
git push
```

---

## 示例2：创建特性分支开发

**用户说：** "我要开发用户登录功能，帮我建个分支"

```bash
# 1. 确保在最新主分支
git switch main
git pull --rebase

# 2. 创建并切换到特性分支
git switch -c feature/user-login

# 3. 推送并设置上游
git push -u origin feature/user-login
```

---

## 示例3：合并特性分支回主分支

**用户说：** "功能做完了，合并回 main"

```bash
# 1. 切到主分支并更新
git switch main
git pull --rebase

# 2. 合并特性分支
git merge --no-ff feature/user-login

# 3. 推送
git push

# 4. 删除已合并的特性分支
git branch -d feature/user-login
git push origin --delete feature/user-login
```

---

## 示例4：处理推送冲突

**用户说：** "push 失败了"

```bash
# 1. 使用 rebase 拉取
git pull --rebase

# 2. 如果无冲突，自动完成，重新推送
git push

# 3. 如果有冲突
git diff --name-only --diff-filter=U    # 查看冲突文件
# 手动解决冲突...
git add .
git rebase --continue
git push
```

---

## 示例5：临时切换分支处理紧急 Bug

**用户说：** "线上有个紧急 bug，要切分支修"

```bash
# 1. 暂存当前工作
git stash push -m "feature/xxx 进行中"

# 2. 切到主分支创建 hotfix
git switch main
git pull
git switch -c hotfix/crash-fix

# 3. 修复后提交推送
git add .
git commit -m "fix: 修复启动崩溃问题"
git push -u origin hotfix/crash-fix

# 4. 合并回主分支
git switch main
git merge --no-ff hotfix/crash-fix
git push

# 5. 回到原来的分支恢复工作
git switch feature/xxx
git stash pop
```

---

## 示例6：回退错误提交

**用户说：** "刚才的提交有问题，撤回"

**情况A：未推送**
```bash
# 撤销提交，保留代码
git reset --soft HEAD~1
# 修改后重新提交
```

**情况B：已推送**
```bash
# 创建撤销提交
git revert HEAD
git push
```

---

## 示例7：查找谁修改了某行代码

**用户说：** "这行代码谁改的"

```bash
# 查看文件的逐行追溯
git blame lib/src/pages/home_page.dart -L 42,50

# 查看该提交的详情
git show <commit-hash>
```

---

## 示例8：Cherry-pick 特定提交

**用户说：** "把 develop 分支那个修复拣过来"

```bash
# 1. 查找目标提交
git log develop --oneline -20

# 2. 拣选
git cherry-pick <commit-hash>

# 3. 推送
git push
```

---

## 示例9：整理本地提交历史

**用户说：** "最近3个提交合并成一个"

```bash
# 软重置到3个提交之前
git reset --soft HEAD~3

# 重新提交
git commit -m "feat(bills): 完成销售单功能"
```

---

## 示例10：打版本标签

**用户说：** "发布 v2.0.0"

```bash
# 创建附注标签
git tag -a v2.0.0 -m "Release v2.0.0: 新增用户系统"

# 推送标签
git push origin v2.0.0
```

---

## 示例11：找回误删的分支

**用户说：** "分支删错了，能恢复吗"

```bash
# 1. 查看 reflog 找到分支最后的提交
git reflog | grep "feature/xxx"

# 2. 基于找到的提交重建分支
git checkout -b feature/xxx HEAD@{N}
```

---

## 示例12：Worktree 并行开发

**用户说：** "想同时看两个分支的代码"

```bash
# 在 ../project-hotfix 目录打开 hotfix 分支
git worktree add ../project-hotfix hotfix/urgent

# 完成后清理
git worktree remove ../project-hotfix
```

---

## 示例13：克隆远程仓库

**用户说：** "把这个项目克隆下来 git@github.com:user/project.git"

```bash
# 完整克隆
git clone git@github.com:user/project.git
cd project

# 查看分支和远程
git branch -a
git remote -v
git log --oneline -5
```

---

## 示例14：浅克隆大仓库

**用户说：** "这个仓库太大了，快速克隆一下就行"

```bash
# 浅克隆（仅最新提交）
git clone --depth 1 <url>
```

---

## 示例15：Changelist 分组提交

**用户说：** "这些改动分两次提交，登录相关的一次，首页相关的一次"

```bash
# 第一组：登录相关
git add src/models/user.dart src/pages/login.dart
git commit -m "feat(auth): 添加用户登录功能"

# 第二组：首页相关
git add src/pages/home.dart test/home_test.dart
git commit -m "refactor(home): 优化首页布局"

# 剩余文件
git add .
git commit -m "chore: update dependencies"
```

---

## 示例16：搁置当前工作（Shelve）

**用户说：** "把当前改动先搁一下，一会儿再弄"

```bash
# 搁置全部变更
git stash push -m "shelve: WIP用户系统重构"

# 搁置部分文件
git stash push -m "shelve: 仅首页修改" -- src/pages/home.dart

# 恢复搁置
git stash list
git stash pop stash@{0}
```

---

## 示例17：创建和应用补丁

**用户说：** "把这个修改导出成 patch 发给同事"

```bash
# 导出工作区变更为 patch
git diff > fix-login-bug.patch

# 导出最近3个提交为 patch 文件
git format-patch -3

# 同事应用 patch
git apply --check fix-login-bug.patch   # 先预览
git apply fix-login-bug.patch           # 应用
```

---

## 示例18：管理子模块

**用户说：** "把公共组件库作为子模块加进来"

```bash
# 添加子模块
git submodule add git@github.com:team/common-ui.git libs/common-ui
git commit -m "chore: add common-ui submodule"

# 克隆后初始化子模块
git submodule update --init --recursive

# 更新子模块到最新
git submodule update --remote
```

---

## 示例19：Log 筛选查找提交

**用户说：** "找一下张三上周关于登录的提交"

```bash
git log --author="张三" --after="2026-04-06" --before="2026-04-13" --grep="登录" --oneline
```

---

## 示例20：对比两个提交

**用户说：** "对比一下这两个版本有什么不同"

```bash
# 两个提交之间的变更文件
git diff abc1234 def5678 --name-only

# 详细统计
git diff abc1234 def5678 --stat

# 完整 diff
git diff abc1234 def5678
```

---

## 示例21：查看文件完整历史

**用户说：** "这个文件经历了哪些修改"

```bash
# 含重命名追踪的完整历史
git log --oneline --follow -- src/pages/login.dart

# 每次修改的 diff
git log -p -- src/pages/login.dart
```

---

## 示例22：GPG 签名提交

**用户说：** "这个提交需要签名"

```bash
# 单次签名提交
git commit -S -m "feat: 安全模块更新"

# 开启自动签名
git config --global commit.gpgsign true
```

---

## 示例23：SSH 密钥配置

**用户说：** "配一下 SSH key"

```bash
# 生成 SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

# 添加到 ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 查看公钥（复制到 GitHub/GitLab）
cat ~/.ssh/id_ed25519.pub

# 测试连接
ssh -T git@github.com
```
