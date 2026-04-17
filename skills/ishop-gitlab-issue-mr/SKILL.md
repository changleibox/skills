---
name: ishop-gitlab-issue-mr
description: iShop GitLab 开发工作流管理。当用户说"提个issue""建个MR""开个分支""我要修改9745的bug""我要开发XX""修复XX""解决XX问题""帮我提交一下合并请求""看看我的issue""审核通过了合一下"等任何 GitLab Issue/MR/分支操作时触发。注意：用户说的内容是任务名称，不是指令，不要解析数字为Bug编号。
---

# iShop GitLab Issue & MR 管理技能

管理 iShop GitLab (git.graspishop.com) 仓库的 Issues、Merge Requests 和分支，支持完整的开发工作流。

**GitLab 服务器：** `https://git.graspishop.com/`

# 何时使用

- 用户说"提个 issue""建个 issue""记一下这个问题""有个需求要记录"
- 用户说"提个 MR""建个合并请求""帮我提交一下 MR""代码写好了提交审核"
- 用户说"开个分支""建个分支""拉个开发分支"
- 用户说"我要开发XX功能""这个功能我来做""这个 bug 我来修"
- 用户说"看看我的 issue""我有哪些 MR""我提的 MR 怎么样了"
- 用户说"审核通过了合一下""帮我走一下开发流程"
- 用户提到任何 Issue/MR/分支相关的操作

## ⚠️ 意图识别规则（极其重要）

**用户说的话 = 任务名称，不是指令。**

当用户说"我要修改9745的bug"、"修复登录崩溃"、"解决XXX问题"等时：

- ✅ **正确理解**：将整句话作为**任务名称/描述**，走 Issue → Draft MR → 分支 的完整工作流
- ❌ **错误理解**：把其中的数字当成 Bug 编号去查找、或者试图帮用户解决/修复代码

**示例：**

| 用户说 | 正确理解 | 错误理解 |
|--------|----------|----------|
| "我要修改9745的bug" | 创建任务名为"修改9745的bug"的工作流 | 查找编号9745的Bug |
| "修复登录页面崩溃" | 创建任务名为"修复登录页面崩溃"的工作流 | 帮用户调试代码 |
| "解决国际化问题" | 创建任务名为"解决国际化问题"的工作流 | 分析国际化代码 |
| "开发iShop开单神器" | 创建任务名为"开发iShop开单神器"的工作流 | 帮用户写代码 |

**规则：**
1. **永远不要**将用户描述中的数字解析为 Bug/Issue 编号去查找
2. **永远不要**试图帮用户解决具体的技术问题
3. 用户的整句描述就是 Issue 标题和工作流名称
4. 本技能只负责**创建和管理开发工作流**（Issue/MR/分支），不负责写代码

## 前置配置

### 步骤0：检查依赖

**检查 glab CLI 是否安装：**

```bash
which glab && glab version
```

**如果未安装，引导用户安装：**

```bash
# macOS
brew install glab

# Linux
curl -sL https://raw.githubusercontent.com/profclems/glab/trunk/scripts/install.sh | sh
```

### 步骤1：检查 GitLab Token 配置

**GitLab 服务器地址（固定）：** `https://git.graspishop.com/`

**检查 Token 配置（按优先级）：**

```bash
# 方式1：检查 glab CLI 配置（优先）
glab auth status 2>&1 | grep -q "Logged in" && echo "已通过 glab 登录" || echo "未登录"

# 方式2：检查 Git 全局配置
git config --global gitlab.token

# 方式3：检查环境变量
echo $GITLAB_TOKEN
```

**注意：Token 用于调用 GitLab API（创建 Issue、MR 等），与 Git push 的 SSH/HTTPS 认证是分开的。**

**如果 Token 未配置，引导用户选择配置方式：**

使用 `ask_user_question` 工具，提供以下选项：

| 选项 | 说明 |
|------|------|
| 🔧 Git 全局配置（推荐） | 永久保存，所有终端可用 |
| 🌍 环境变量 | 临时配置，仅当前终端有效 |
| 🔑 使用 glab 登录 | 通过 glab auth login 交互式登录 |
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
| ✏️ 手动输入项目路径 | 直接输入项目路径（如 igroup/ishop） |
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
- 用户说"我要修改9745的bug"（→ 任务名：修改9745的bug）
- 用户说"我要开发一个新功能：XXX"（→ 任务名：XXX）
- 用户说"修复登录崩溃"（→ 任务名：修复登录崩溃）
- 用户说任何描述开发/修复/解决意图的话（整句作为任务名）

**⚠️ 注意：用户说的内容就是任务名称，不要解析其中的数字为编号！**

**工作流执行步骤：**

#### 步骤1：创建 Issue

**1.1 选择 Issue 类型**

使用 `ask_user_question` 提供：

```json
{
  "question": "📋 请选择 Issue 类型：",
  "options": [
    {"label": "🚀 feature", "description": "新功能开发"},
    {"label": "🐛 bug", "description": "Bug 修复"},
    {"label": "✨ improvement", "description": "优化改进"}
  ]
}
```

**1.2 确认 Issue 标题**

根据用户描述生成建议标题，让用户确认或修改：

```json
{
  "question": "📋 Issue 标题：",
  "options": [
    {"label": "✅ 使用建议标题", "description": "[显示建议的标题]"},
    {"label": "✏️ 修改标题", "description": "手动输入新标题"}
  ]
}
```

**1.3 选择指派人**

```bash
# 获取项目成员列表
glab api projects/:id/members --jq '.[] | "\(.id)|\(.name)|\(.username)"'
```

使用 `ask_user_question` 列出成员：

```json
{
  "question": "📋 请选择指派人：",
  "options": [
    {"label": "张三 (@zhangsan)", "description": ""},
    {"label": "李四 (@lisi)", "description": ""},
    {"label": "👤 不指派", "description": "稍后指定"}
  ]
}
```

**1.4 选择标签**

```bash
# 获取项目标签
glab api projects/:id/labels --jq '.[] | "\(.name)"'
```

使用 `ask_user_question` 列出标签（多选）：

```json
{
  "question": "📋 请选择标签（可多选）：",
  "options": [
    {"label": "🏷️ feature", "description": "新功能"},
    {"label": "🏷️ bug", "description": "Bug"},
    {"label": "🏷️ priority::high", "description": "高优先级"},
    {"label": "⏭️ 跳过", "description": "不添加标签"}
  ],
  "multiSelect": true
}
```

#### 步骤2：创建 Draft MR + 关联分支

**2.1 选择目标分支**

```bash
# 获取项目分支列表
glab api projects/:id/repository/branches --jq '.[] | "\(.name)"'
```

使用 `ask_user_question` 列出分支：

```json
{
  "question": "📋 请选择目标分支：",
  "options": [
    {"label": "main", "description": "主分支"},
    {"label": "develop", "description": "开发分支"},
    {"label": "release/x.x.x", "description": "发布分支"}
  ]
}
```

**2.2 确认分支名称**

根据 Issue ID 和标题生成建议分支名，让用户确认：

```json
{
  "question": "📋 分支名称：",
  "options": [
    {"label": "✅ 使用建议名称", "description": "[显示建议的分支名，如：421-用户登录功能]"},
    {"label": "✏️ 修改分支名", "description": "手动输入新名称"}
  ]
}
```

**2.3 确认创建 Draft MR**

```json
{
  "question": "📋 确认创建 Draft MR？",
  "options": [
    {"label": "✅ 创建 Draft MR", "description": "创建并关联分支"},
    {"label": "⏸️ 暂不创建 MR", "description": "仅创建 Issue"}
  ]
}
```

#### 步骤3：本地拉取分支开发

```bash
git fetch --all
git checkout <branch-name>
```

#### 步骤4：开发完成，推送代码

```bash
git add .
git commit -m "实现功能"
git push origin <branch-name>
```

#### 步骤5：Draft 转正式状态

**5.1 选择审核人**

使用 `ask_user_question` 列出项目成员：

```json
{
  "question": "📋 请选择审核人：",
  "options": [
    {"label": "张三 (@zhangsan)", "description": ""},
    {"label": "李四 (@lisi)", "description": ""},
    {"label": "👤 不指定", "description": "稍后指定"}
  ]
}
```

**5.2 确认转为正式 MR**

```json
{
  "question": "📋 确认将 Draft MR 转为正式状态？",
  "options": [
    {"label": "✅ 转为正式 MR", "description": "并请求审核"},
    {"label": "⏸️ 保持 Draft 状态", "description": "继续开发"}
  ]
}
```

#### 步骤6：审核、合并

**6.1 审核通过后确认合并**

```json
{
  "question": "📋 MR 审核已通过，确认合并？",
  "options": [
    {"label": "✅ 合并 MR", "description": "合并后自动删除分支、关闭 Issue"},
    {"label": "⏸️ 暂不合合并", "description": "等待进一步确认"}
  ]
}
```

**合并命令：**
```bash
glab mr merge <mr-id> --delete-branch
# 自动触发：关闭 Issue、关闭 MR、删除分支
```

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

