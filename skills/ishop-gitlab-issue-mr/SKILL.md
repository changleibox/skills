---
name: ishop-gitlab-issue-mr
description: iShop GitLab (git.graspishop.com) 仓库 Issue、Merge Request 和分支全生命周期管理技能。支持创建 Issue、关联创建分支、创建关联 MR 的完整工作流。当用户提到"创建issue"、"提交MR"、"新建分支"、"开发新功能"、"修复bug"、"代码审查"等时智能触发。
---

# iShop GitLab Issue & MR 管理技能

管理 iShop GitLab (git.graspishop.com) 仓库的 Issues、Merge Requests 和分支，支持完整的开发工作流。

**GitLab 服务器：** `https://git.graspishop.com/`

## 何时使用

- 用户说"创建 issue"、"提 issue"、"记录问题"
- 用户说"创建 MR"、"提交合并请求"、"发起 PR"
- 用户说"新建分支"、"创建开发分支"
- 用户描述开发意图："我要开发XX功能"、"修复XX问题"
- 用户询问 Issue/MR 状态或列表
- 用户要求关联 Issue 和 MR

## 前置配置

### 步骤1：检查 GitLab Token 配置

**GitLab 服务器地址（固定）：** `https://git.graspishop.com/`

**检查 Token 配置：**

```bash
# 方式1：检查 Git 全局配置（推荐）
git config --global gitlab.token

# 方式2：检查环境变量
echo $GITLAB_TOKEN
```

**如果 Token 未配置，引导用户选择配置方式：**

使用 `ask_user_question` 工具，提供以下选项：

| 选项 | 说明 |
|------|------|
| 🔧 Git 全局配置（推荐） | 永久保存，所有终端可用 |
| 🌍 环境变量 | 临时配置，仅当前终端有效 |
| ❓ 我还没有 Token | 引导创建 Token |

**配置引导流程：**

```
📋 请按以下步骤创建 Token：

1. 访问 https://git.graspishop.com/-/profile/personal_access_tokens
2. 点击 "Add new token"
3. 配置：
   - 名称：qoder-agent
   - 权限：勾选 api
   - 过期时间：根据需要设置
4. 点击 "Create personal access token"
5. 复制生成的 Token（glpat-xxxxxxxxxxxxxxxx）

请输入您的 Token：
```

### 步骤2：确定操作项目

**自动检测当前项目：**

```bash
# 1. 检查当前目录是否在 Git 仓库内
git rev-parse --is-inside-work-tree

# 2. 获取项目根目录
git rev-parse --show-toplevel

# 3. 获取远程仓库地址
git remote get-url origin
```

**情况A：当前目录在 iShop GitLab 项目内**

自动识别项目路径，并确认：

```
✅ 检测到项目：igroup/ishop

是否在此项目下操作？
```

使用 `ask_user_question` 提供：

| 选项 | 说明 |
|------|------|
| ✅ 是，继续操作 | 使用当前项目 |
| 🔄 切换到其他项目 | 列出所有有权限的项目 |

**情况B：当前目录不在 Git 仓库内**

使用 `ask_user_question` 列出用户有权限的所有项目：

```bash
# 获取用户有权限的项目列表
glab api projects --per-page 100 -f 'membership=true' -f 'simple=true' \
  --jq '.[] | "\(.path_with_namespace)|\(.name)"'
```

显示格式：

```
📋 请选择要操作的项目：

| 选项 | 项目路径 | 项目名称 |
|------|----------|----------|
| 1 | igroup/ishop | iShop 开单系统 |
| 2 | igroup/ishop-web | iShop Web端 |
| 3 | igroup/common | 公共组件库 |
| ... | ... | ... |
```

**情况C：当前项目不在 iShop GitLab**

```
⚠️ 当前项目不在 iShop GitLab (git.graspishop.com)

请选择：
```

| 选项 | 说明 |
|------|------|
| 🔄 切换到其他项目 | 列出 iShop GitLab 上的项目 |
| ❌ 取消操作 | - |

### 配置验证

```bash
# 验证 glab CLI 认证状态
glab auth status

# 或测试 API 访问
curl -H "Private-Token: $(git config --global gitlab.token)" \
  https://git.graspishop.com/api/v4/user
```

---

## 交互选择规范

**⚠️ 重要：所有需要用户确认的操作，必须使用 `ask_user_question` 工具让用户选择，禁止静默执行或简单确认。**

### 选择项设计原则

1. **项目选择** - 列出所有有权限的项目，让用户选择
2. **Issue 类型** - 提供 feature/bug/improvement 选项
3. **指派人** - 列出项目成员让用户选择
4. **审核人** - 列出项目成员让用户选择
5. **标签** - 列出项目可用标签让用户选择
6. **目标分支** - 列出项目分支让用户选择
7. **关键操作确认** - 合并 MR、删除分支等操作前必须确认

### 选择项示例格式

**项目选择：**
```
📋 请选择要操作的项目：

1. igroup/ishop - iShop 开单系统
2. igroup/ishop-web - iShop Web端
3. igroup/common - 公共组件库
4. 其他项目...

请输入序号：
```

**Issue 类型选择：**
```
📋 请选择 Issue 类型：

1. 🚀 feature - 新功能开发
2. 🐛 bug - Bug 修复
3. ✨ improvement - 优化改进

请输入序号：
```

**指派人选择：**
```
📋 请选择指派人：

1. 张三 (@zhangsan)
2. 李四 (@lisi)
3. 王五 (@wangwu)
4. 不指派

请输入序号：
```

**目标分支选择：**
```
📋 请选择目标分支：

1. main - 主分支
2. develop - 开发分支
3. release/1.0.0 - 发布分支

请输入序号：
```

---

## 核心工作流程

### 完整工作流（Issue → MR → 分支 → 开发 → 合并）

这是团队的标准端到端流程：

```
创建 Issue → 创建关联 MR（Draft） → 创建 MR 关联分支 → 本地开发 → 请求审核合并 → 自动关闭 Issue/MR/删除分支
```

**⚠️ 重要：流程顺序说明**
- **先创建 MR，再创建分支**：MR 创建时会自动创建关联分支
- MR 初始为 Draft/WIP 状态，表示开发中
- 开发完成后转换为正式 MR 并请求审核

**触发时机：**
- 用户说"我要开发一个新功能：XXX"
- 用户说"帮我创建一个 issue 并开始开发"
- 用户描述明确的开发意图

**工作流执行步骤：**

1. **创建 Issue**
   - 分析用户描述，提取标题和描述
   - 选择合适的标签（label）
   - 选择指派人（assignee）

2. **创建关联 MR（Draft）**
   - 基于目标分支（如 main）创建 Draft MR
   - MR 标题关联 Issue：`feat: XXX (#issue-id)`
   - MR 描述中添加 `Closes #<issue-id>` 自动关闭
   - MR 状态为 Draft/WIP

3. **创建 MR 关联分支**
   - MR 创建时自动创建关联分支
   - 或手动创建并关联到 MR
   - 分支名格式：`{type}/{issue-id}-{short-desc}`

4. **本地拉取分支开发**
   - 拉取远程分支到本地
   - 开始开发工作

5. **开发完成，请求审核**
   - 推送代码到远程
   - 将 MR 从 Draft 转为正式状态
   - 通知审核人审核代码

6. **合并 MR**
   - 审核通过后合并 MR
   - 自动触发：关闭 Issue、关闭 MR、删除分支

---

## 操作模块

### 模块1：Issue 管理

#### 创建 Issue

**触发：** "创建一个 issue：XXX" 或 "记录一个问题：XXX"

```bash
# 使用 GitLab CLI (glab) 或 API
glab issue create --title "<title>" --description "<description>" [options]

# 常用选项
--label "bug,feature"          # 标签
--assignee @username           # 指派人
--milestone "Sprint 1"         # 里程碑
--weight 3                     # 权重
```

**Issue 标题规范：**

直接使用中文描述，不带前缀。

| 示例 |
|------|
| `开发iShop开单神器` |
| `974BUG修改` |
| `9750商品性质档案` |
| `国际化` |

**自动生成 Issue 模板：**

```markdown
## 描述
[用户提供的描述]

## 背景
[为什么需要这个功能/修复]

## 验收标准
- [ ] 标准1
- [ ] 标准2

## 关联
- 关联需求：#XXX
```

#### 查询 Issue

**触发：** "查看我的 issues"、"有什么待处理的 issue"

```bash
# 查看指派给我的 Issue
glab issue list --assignee=@me --state=opened

# 查看项目所有打开的 Issue
glab issue list --state=opened

# 搜索 Issue
glab issue list --search "<关键词>"

# 查看 Issue 详情
glab issue view <issue-id>
```

#### 更新 Issue

**触发：** "更新 issue #X"、"关闭 issue #X"

```bash
# 更新 Issue
glab issue update <issue-id> --title "<new-title>"

# 关闭 Issue
glab issue close <issue-id>

# 重新打开 Issue
glab issue reopen <issue-id>

# 添加评论
glab issue note <issue-id> --message "<comment>"
```

---

### 模块2：分支管理

**⚠️ 重要：分支由 MR 创建**

按照团队工作流，分支是在创建 MR 时自动创建的，流程为：
```
创建 Issue → 创建 MR → MR 自动创建关联分支 → 本地拉取开发
```

#### 拉取 MR 关联分支

**触发：** "拉取分支"、"切换到开发分支"、"开始开发"

```bash
# 查看远程分支
git fetch --all
git branch -r

# 拉取并切换到 MR 关联的分支
git checkout <branch-name>

# 或者从远程跟踪
# 分支名格式：{type}/{issue-id}-{desc}
git checkout -b feature/123-user-login origin/feature/123-user-login
```

**分支命名规范：**

格式：`{issue-id}-{简短描述}`（无类型前缀）

| 示例 |
|------|
| `421-iShop开单神器` |
| `974-BUG修改` |
| `9750-商品性质档案` |

#### 手动创建分支（特殊情况）

如果需要手动创建分支（不通过 MR）：

```bash
# 基于目标分支创建
git checkout -b <branch-name> main

# 推送到远程
git push -u origin <branch-name>
```

#### 查看分支

```bash
# 本地分支
git branch

# 远程分支
git branch -r

# 所有分支
git branch -a

# 查看分支跟踪关系
git branch -vv
```

#### 删除分支

```bash
# 删除本地分支
git branch -d <branch-name>

# 强制删除未合并分支
git branch -D <branch-name>

# 删除远程分支
git push origin --delete <branch-name>
```

---

### 模块3：Merge Request 管理

#### 创建关联 Issue 的 MR（Draft）

**⚠️ 标准流程：先创建 MR，再拉取分支开发**

**触发：** "为 issue #X 创建 MR"、"开始开发 issue #X"

```bash
# 创建 Draft MR 并关联 Issue
# MR 创建时会自动创建关联分支
glab mr create \
  --title "Draft: Resolve "{Issue名称}"" \
  --description "## 变更概述
🚧 开发中...

## 关联 Issue
Closes #<issue-id>" \
  --draft \
  --source-branch <issue-id>-<简短描述> \
  --target-branch main \
  --create-source-branch
```

**关键选项：**
- `--draft`：创建为 Draft 状态（开发中）
- `--create-source-branch`：同时创建源分支
- `--source-branch`：分支名格式 `{issue-id}-{描述}`（无前缀）
- 描述中使用 `Closes #<issue-id>` 自动关闭关联 Issue

#### 创建 MR

**触发：** "创建 MR"、"提交合并请求"、"发起 code review"

```bash
# 创建 MR
glab mr create --title "<title>" --description "<description>" [options]

# 常用选项
--source-branch <branch>      # 源分支（默认当前分支）
--target-branch <branch>      # 目标分支（默认 main/master）
--assignee @username          # 指派审核人
--reviewer @username          # 审核人
--label "feature,review"      # 标签
--draft                       # 草稿 MR（开发中）
--wip                         # WIP 状态
--create-source-branch        # 创建源分支
--fill                        # 自动填充标题和描述（来自提交）
```

**MR 标题规范：**

| 状态 | 格式 | 示例 |
|------|------|------|
| Draft（草稿） | `Draft: Resolve "{Issue名称}"` | `Draft: Resolve "开发iShop开单神器"` |
| 正式（非草稿） | `Resolve "{Issue名称}"` | `Resolve "开发iShop开单神器"` |

**MR 描述模板：**

```markdown
## 变更概述
[简要描述本次变更的内容]

## 变更详情
- 变更点1
- 变更点2

## 测试说明
- [ ] 单元测试已通过
- [ ] 集成测试已通过
- [ ] 手动测试场景

## 关联 Issue
Closes #<issue-id>

## Checklist
- [ ] 代码已自测
- [ ] 已添加必要注释
- [ ] 已更新相关文档
```

#### 开发完成：Draft 转正式状态

**触发：** "开发完成了"、"准备好审核了"、"转换 MR 状态"

```bash
# 将 Draft MR 转换为正式状态
glab mr ready <mr-id>

# MR 标题自动从 "Draft: Resolve ..." 变为 "Resolve ..."
```

#### 请求审核

**触发：** "请审核 MR"、"通知审核人"、"提交审核"

```bash
# 查看当前审核状态
glab mr view <mr-id>

# 添加审核人
# 通过 MR URL 通知审核人
```

**自动通知示例：**
```
@reviewer 您好，MR !<id> 已准备就绪，请审核。
MR 链接：https://gitlab.xxx.com/project/-/merge_requests/<id>
```

#### 查询 MR

**触发：** "查看我的 MR"、"有哪些待审核的 MR"

```bash
# 查看我创建的 MR
glab mr list --author=@me --state=opened

# 查看待我审核的 MR
glab mr list --reviewer=@me --state=opened

# 查看所有打开的 MR
glab mr list --state=opened

# 查看 MR 详情
glab mr view <mr-id>

# MR diff
glab mr diff <mr-id>
```

#### 审核 MR

**触发：** "审核 MR #X"、"审查代码"

```bash
# 查看 MR 变更
glab mr diff <mr-id>

# 添加评论
glab mr note <mr-id> --message "<comment>"

# 批准 MR
glab mr approve <mr-id>

# 取消批准
glab mr unapprove <mr-id>

# 请求修改
glab mr review <mr-id> --request-changes --message "<comment>"
```

#### 合并 MR

**触发：** "合并 MR #X"

```bash
# 合并 MR
glab mr merge <mr-id>

# 合并并删除源分支
glab mr merge <mr-id> --delete-branch

# Squash 合并
glab mr merge <mr-id> --squash

# 检查合并状态
glab mr view <mr-id>
```

---

## 智能识别场景

### 场景1：用户描述开发意图

**用户说：** "我要开发一个用户登录功能"

**智能处理：**
1. 识别为"新功能"类型
2. 询问是否创建 Issue 记录
3. 如用户确认：
   - 创建 Issue（标题：`用户登录功能`）
   - 询问是否创建 Draft MR 开始开发
   - 如确认，创建 Draft MR（标题：`Draft: Resolve "用户登录功能"`）+ 关联分支
   - 提示用户拉取分支开始开发

### 场景2：用户描述修复意图

**用户说：** "需要修复登录页面的崩溃问题"

**智能处理：**
1. 识别为"Bug 修复"类型
2. 询问是否创建 Issue 记录
3. 如用户确认：
   - 创建 Issue（标题：`登录页面崩溃问题`）
   - 询问是否创建 Draft MR 开始修复
   - 如确认，创建 Draft MR + 关联分支
   - 提示用户拉取分支开始修复

### 场景3：用户完成开发

**用户说：** "登录功能开发完成了"、"准备好了，请审核"

**智能处理：**
1. 检查当前分支对应的 MR 状态
2. 将 Draft MR 转换为正式状态
3. 更新 MR 标题（去掉 Draft: 前缀）
4. 通知审核人审核代码

### 场景4：用户查看工作状态

**用户说：** "我有什么待处理的工作？"

**智能处理：**
1. 查询指派给用户的打开的 Issues
2. 查询用户创建的打开的 MRs
3. 查询待用户审核的 MRs
4. 汇总展示工作状态

---

## 配置参数

通过 Git 配置或环境变量配置：

| 参数 | 配置方式 | 说明 |
|------|----------|------|
| GitLab URL | 固定值 | `https://git.graspishop.com/` |
| GitLab Token | `git config --global gitlab.token` | Personal Access Token |
| 默认目标分支 | - | MR 默认目标分支，默认 `main` |
| 自动删除分支 | - | MR 合并后自动删除分支，默认 `true` |

**注意：** 项目通过当前目录的 Git 远程仓库地址自动识别，无需手动配置。

---

## 工作流模板

### 模板1：新功能开发完整流程

```bash
# ====== 步骤1：创建 Issue ======
glab issue create --title "用户登录功能"
# 输出：Issue #421 已创建

# ====== 步骤2：创建 Draft MR + 关联分支 ======
glab mr create \
  --title "Draft: Resolve \"用户登录功能\"" \
  --description "## 变更概述
🚧 开发中...

## 关联 Issue
Closes #421" \
  --draft \
  --source-branch 421-用户登录功能 \
  --target-branch main \
  --create-source-branch
# 输出：MR !45 已创建，分支 421-用户登录功能 已创建

# ====== 步骤3：本地拉取分支开发 ======
git fetch --all
git checkout 421-用户登录功能
# 开始开发...

# ====== 步骤4：开发完成，推送代码 ======
git add .
git commit -m "实现用户登录功能"
git push origin 421-用户登录功能

# ====== 步骤5：Draft 转正式状态 ======
glab mr ready 45
# MR 标题自动从 "Draft: Resolve ..." 变为 "Resolve ..."

# ====== 步骤6：审核、合并 ======
glab mr approve 45
glab mr merge 45 --delete-branch
# 自动触发：关闭 Issue #421、关闭 MR、删除分支
```

### 模板2：Bug 修复完整流程

```bash
# ====== 步骤1：创建 Issue ======
glab issue create --title "974BUG修改"
# 输出：Issue #974 已创建

# ====== 步骤2：创建 Draft MR + 关联分支 ======
glab mr create \
  --title "Draft: Resolve \"974BUG修改\"" \
  --description "## 问题
[问题描述]

## 解决方案
[方案]

Fixes #974" \
  --draft \
  --source-branch 974-BUG修改 \
  --target-branch main \
  --create-source-branch

# ====== 步骤3：本地拉取分支修复 ======
git checkout 974-BUG修改
# 修复 bug...

# ====== 步骤4：修复完成，推送代码 ======
git add .
git commit -m "修复问题"
git push origin 974-BUG修改

# ====== 步骤5：Draft 转正式状态 ======
glab mr ready 46

# ====== 步骤6：审核、合并 ======
glab mr merge 46 --delete-branch
# 自动触发：关闭 Issue #974、关闭 MR、删除分支
```

---

## 错误处理

### 认证失败

```
Error: authentication failed
```

**解决：**
1. 检查 Token 是否正确配置：`git config --global gitlab.token`
2. 确认 Token 有 `api` 权限
3. 确认 Token 未过期
4. 访问 https://git.graspishop.com/-/profile/personal_access_tokens 重新生成

### 不在 Git 仓库内

```
fatal: not a git repository
```

**解决：**
```
cd /path/to/your/project
```

### 项目不在 iShop GitLab

```
git remote get-url origin
# 输出：git@github.com:user/repo.git
```

**说明：** 当前项目不在 iShop GitLab 服务器上，此技能仅适用于 `git.graspishop.com` 上的项目。

### 权限不足

```
Error: 403 Forbidden
```

**解决：**
1. 检查用户对项目的权限
2. 确认 Token 的 scope 包含所需权限

### 分支已存在

```
Error: branch already exists
```

**解决：**
1. 切换到已存在的分支
2. 或使用新分支名

### MR 冲突

```
Error: merge conflict
```

**解决：**
1. 查看冲突文件
2. 本地解决冲突后重新推送
3. 或请求 MR 作者解决

---

## 相关文档

- [使用示例](examples.md)
- GitLab API 文档：`https://{gitlab-url}/help/api/README.md`
- glab CLI 文档：`https://gitlab.com/gitlab-org/cli`

