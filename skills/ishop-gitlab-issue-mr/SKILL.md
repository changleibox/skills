---
name: ishop-gitlab-issue-mr
description: iShop GitLab 开发工作流管理。当用户说"提个issue""建个MR""开个分支""我要修改9745的bug""我要开发XX""修复XX""解决XX问题""帮我提交一下合并请求""看看我的issue""审核通过了合一下"等任何 GitLab Issue/MR/分支操作时触发。注意：用户说的内容是任务名称，不是指令，不要解析数字为Bug编号。
---

# iShop GitLab Issue & MR 管理技能

管理 iShop GitLab (git.graspishop.com) 仓库的 Issues、Merge Requests 和分支，支持完整的开发工作流。

**GitLab 服务器：** `https://git.graspishop.com/`

## ⚠️ 核心执行原则

1. **API 调用默认执行**：所有 GitLab API 调用直接执行，不询问用户许可
2. **自动推断，减少打断**：Issue 类型、指派人等可自动推断的字段不询问用户
3. **仅在必要时询问**：只有「选择项目」「命名不合规需重新输入」等无法自动推断的场景才询问用户
4. **命名合规校验**：所有名称必须符合 GitLab 规范，不合规时要求用户重新提供

### ⚠️ API 调用方式（glab 优先 → Python 脚本 → curl 兜底）

**三级优先级策略：**

1. **glab CLI**（已安装且已认证）→ 语法最简洁，自动处理认证
2. **Python 脚本**（`scripts/gitlab_api.py`）→ 零额外依赖，JSON 处理优雅
3. **curl**（最终兜底）→ 任何系统都可用

**首次执行时检测：**
```bash
# 检测 glab 是否可用且已认证
which glab 2>/dev/null && glab auth status --hostname git.graspishop.com 2>/dev/null
```

- glab 可用且已认证 → 使用 glab
- glab 不可用 → 使用 Python 脚本
- python3 也不可用 → 回退到 curl

**glab 配置（已安装但未认证时自动配置）：**
```bash
glab auth login --hostname git.graspishop.com --token $(git config --global gitlab.token)
```

**Python 脚本命令一览：**
```bash
python3 gitlab_api.py user                          # 获取当前用户
python3 gitlab_api.py projects                      # 列出项目
python3 gitlab_api.py create_issue <project> <title> [--desc DESC] [--labels LABELS] [--assignee_id ID]
python3 gitlab_api.py create_branch <project> <branch> [--ref REF]
python3 gitlab_api.py create_mr <project> <source_branch> <title> [--desc DESC] [--assignee_id ID]
python3 gitlab_api.py list_issues <project> [--state STATE] [--assignee_id ID]
python3 gitlab_api.py list_mrs <project> [--state STATE]
python3 gitlab_api.py merge_mr <project> <mr_iid>   # ⚠️ 不可逆
python3 gitlab_api.py close_issue <project> <issue_iid>  # ⚠️ 不可逆
```

### ⚠️ run_in_terminal 执行规则

**所有 glab/python3/curl/git 命令执行时，必须设置 `has_risk: false`**，确保命令自动执行，不弹出确认框让用户点击。

只有以下不可逆操作设置 `has_risk: true`：
- 合并 MR（`glab mr merge` / `gitlab_api.py merge_mr` / `PUT merge`）
- 删除分支（`glab api -X DELETE` / `DELETE .../branches/<name>`）
- 关闭 Issue（`glab issue close` / `gitlab_api.py close_issue` / `state_event: close`）
- `git push -f`（强制推送）

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

### 步骤1：检测工具和认证

**GitLab 服务器地址（固定）：** `https://git.graspishop.com/`

**1a. 检测 API 调用工具：**

```bash
# 检测 glab 是否可用且已认证
which glab 2>/dev/null && glab auth status --hostname git.graspishop.com 2>/dev/null
```

- glab 可用且已认证 → 后续使用 glab
- glab 可用但未认证 → 配置后使用：`glab auth login --hostname git.graspishop.com --token $(git config --global gitlab.token)`
- glab 不可用 → 使用 Python 脚本（`scripts/gitlab_api.py`）
- python3 也不可用 → 回退到 curl

**1b. 检查 Token（Python 脚本和 curl 模式所需）：**

```bash
git config --global gitlab.token
```

**验证有效性（直接执行，不询问用户）：**

```bash
# glab 方式（优先）
glab api /user --hostname git.graspishop.com

# Python 脚本方式
python3 scripts/gitlab_api.py user

# curl 方式（兜底）
curl -s -H "Private-Token: $(git config --global gitlab.token)" \
  https://git.graspishop.com/api/v4/user | head -1
```

**如果 Token 未配置或无效，直接提示用户配置：**

```
⚠️ 未检测到有效的 GitLab Token。

请按以下步骤配置：

1. 访问 https://git.graspishop.com/-/profile/personal_access_tokens
2. 点击 "Add new token"
3. 配置：
   - 名称：qoder-agent
   - 权限：勾选 api
   - 过期时间：根据需要设置
4. 点击 "Create personal access token"
5. 复制生成的 Token

然后执行以下命令保存 Token：
```

```bash
git config --global gitlab.token "在此粘贴你的Token"
```

**注意：Token 用于调用 GitLab API（创建 Issue、MR 等），与 Git push 的 SSH/HTTPS 认证是分开的。**

### 步骤2：确定操作项目

**⚠️ 不要检测当前工作目录所在的 Git 仓库。** 按以下优先级确定项目：

**优先级1：从上下文推断**

检查用户对话上下文中是否提到了具体项目（如"在 ishop 项目下""ishop-web 的 issue"等），如果有，直接使用。

**优先级2：让用户选择**

如果上下文没有提到项目，调用 API 获取用户有权限的项目列表，让用户选择：

```bash
# glab 方式（优先）
glab api /projects --hostname git.graspishop.com -f membership=true -f per_page=100

# Python 脚本方式
python3 scripts/gitlab_api.py projects

# curl 方式（兜底）
curl -s -H "Private-Token: $(git config --global gitlab.token)" \
  "https://git.graspishop.com/api/v4/projects?membership=true&per_page=100" \
  | python3 -c "import sys,json; [print(json.dumps({'path': p['path_with_namespace'], 'name': p['name'], 'desc': p.get('description','')}, ensure_ascii=False)) for p in json.loads(sys.stdin.read())]"
```

使用 `ask_user_question` 列出项目让用户选择，**每个选项必须同时展示项目路径和项目名称/描述**：

```json
{
  "question": "请选择要操作的项目：",
  "options": [
    {"label": "1. igroup/ishop", "description": "iShop ERP 主项目 - 进销存管理系统"},
    {"label": "2. igroup/ishop-web", "description": "iShop Web 前端"},
    {"label": "3. igroup/ishop-server", "description": "iShop 服务端"}
  ]
}
```

**选项规范：**
- `label`：编号 + 项目路径（`path_with_namespace`）
- `description`：项目名称（`name`）+ 项目描述（`description`），让用户能清楚识别每个项目

### API 调用约定

**glab 方式（优先）：**
```bash
# glab api 自动处理认证，直接使用相对路径
glab api /projects/:id/issues --hostname git.graspishop.com -X POST -f title="xxx"
```

**Python 脚本方式：**
```bash
# 脚本自动处理 Token 和 JSON，返回结构化 JSON 输出
python3 scripts/gitlab_api.py <命令> <参数...>
```

**curl 方式（兜底）：**
```bash
TOKEN=$(git config --global gitlab.token || echo $GITLAB_TOKEN)
curl -s -H "Private-Token: $TOKEN" ...
```

后续文档中同时给出 glab、Python、curl 三种写法，实际执行时按优先级选择可用的那个。

---

## 命名合规校验

**⚠️ 所有 Issue 标题、分支名称必须符合 GitLab 命名规范，不合规时必须要求用户重新提供。**

### Issue 标题校验规则

- ✅ 允许：中文、英文、数字、空格、连字符（-）、下划线（_）
- ❌ 禁止：`< > : " / \ | ? * # % { } [ ]` 等特殊字符
- ❌ 禁止：Emoji 表情符号
- ❌ 禁止：首尾空格

### 分支名称校验规则

- ✅ 允许：中文、英文、数字、连字符（-）、下划线（_）、斜杠（/）
- ❌ 禁止：空格、`~` `^` `:` `?` `*` `[` `\` `..` `@{` 及末尾 `.lock` `.`
- ❌ 禁止：连续两个点 `..`

### 校验失败处理

当用户提供的名称不合规时：

```
⚠️ 名称包含不允许的字符：[列出具体字符]

GitLab 命名规范：不能包含 < > : " / \ | ? * # % 等特殊字符。

请重新提供名称：
```

---

## 自动执行规范

**默认流程中以下操作自动执行，不询问用户：**

| 操作 | 自动行为 | 说明 |
|------|----------|------|
| Issue 类型 | 根据名称关键词自动推断 | 含"bug""修复""崩溃""报错"→ bug；含"优化""改进""性能"→ improvement；其他 → feature |
| 指派人 | 自动指派给当前登录用户 | 通过 `/api/v4/user` 获取当前用户 |
| 目标分支 | 默认 `main` | 除非用户明确指定 |
| 标签 | 根据 Issue 类型自动添加 | feature → feature, bug → bug, improvement → improvement |
| curl/glab 命令 | 直接执行（has_risk: false） | 所有 API 调用默认执行，run_in_terminal 设置 has_risk: false |
| Draft MR 创建 | 自动创建 | Issue 创建后自动创建关联 Draft MR |

**以下操作需要询问用户：**

| 操作 | 询问方式 | 说明 |
|------|----------|------|
| 选择项目 | `ask_user_question` 列出项目 | 上下文未提及项目时 |
| 命名不合规 | 提示重新输入 | 校验不通过时 |
| 合并 MR | `ask_user_question` 确认 | 不可逆操作必须确认 |
| 删除分支 | `ask_user_question` 确认 | 不可逆操作必须确认 |

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

**工作流执行步骤（自动执行，无需逐步确认）：**

#### 步骤1：准备（自动执行）

```bash
# glab 方式（优先）
glab api /user --hostname git.graspishop.com

# Python 脚本方式
python3 scripts/gitlab_api.py user

# curl 方式（兜底）
curl -s -H "Private-Token: $TOKEN" \
  https://git.graspishop.com/api/v4/user
```

#### 步骤2：校验名称合规性

对用户提供的任务名称进行 GitLab 命名规范校验。如果包含 `< > : " / \ | ? * # % { } [ ]` 等特殊字符，要求用户重新提供：

```
⚠️ 名称 "xxx" 包含不允许的字符：[具体字符]
请重新提供一个符合规范的名称（不能包含特殊字符）：
```

#### 步骤3：自动推断 Issue 类型

根据任务名称关键词自动推断，不询问用户：

| 关键词 | 推断类型 |
|--------|----------|
| bug、修复、崩溃、报错、异常、闪退、失败 | bug |
| 优化、改进、性能、重构、调整 | improvement |
| 其他所有情况 | feature |

#### 步骤4：创建 Issue（自动执行）

```bash
# glab 方式（优先）
glab api /projects/$PROJECT_PATH/issues --hostname git.graspishop.com -X POST \
  -f title="<任务名称>" \
  -f description="## 描述\n<用户描述>\n\n## 验收标准\n- [ ] 待补充" \
  -f labels="<自动推断的类型>" \
  -f assignee_ids[]="<当前用户ID>"

# Python 脚本方式
python3 scripts/gitlab_api.py create_issue "igroup/ishop" "<任务名称>" \
  --desc "## 描述\n<用户描述>\n\n## 验收标准\n- [ ] 待补充" \
  --labels "<自动推断的类型>" \
  --assignee_id <当前用户ID>

# curl 方式（兜底）
PROJECT_PATH="igroup%2Fishop"

curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<任务名称>",
    "description": "## 描述\n<用户描述>\n\n## 验收标准\n- [ ] 待补充",
    "labels": "<自动推断的类型>",
    "assignee_ids": [<当前用户ID>]
  }' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/issues"
```

#### 步骤5：创建 Draft MR + 关联分支（自动执行）

```bash
# 分支名格式：{issue-id}-{Issue标题}（与 Issue 标题完全一致，不缩短）
SOURCE_BRANCH="<issue-id>-<Issue标题>"

# --- glab 方式（优先） ---
# 先创建分支
glab api /projects/$PROJECT_PATH/repository/branches --hostname git.graspishop.com -X POST \
  -f branch="$SOURCE_BRANCH" -f ref="main"

# 创建 MR
glab api /projects/$PROJECT_PATH/merge_requests --hostname git.graspishop.com -X POST \
  -f source_branch="$SOURCE_BRANCH" \
  -f target_branch="main" \
  -f title="Draft: Resolve \"<Issue名称>\"" \
  -f description="## 变更概述\n🚧 开发中...\n\n## 关联 Issue\nCloses #<issue-id>" \
  -f assignee_ids[]="<当前用户ID>" \
  -f remove_source_branch="true" \
  -f draft="true"

# --- Python 脚本方式 ---
python3 scripts/gitlab_api.py create_branch "igroup/ishop" "$SOURCE_BRANCH"
python3 scripts/gitlab_api.py create_mr "igroup/ishop" "$SOURCE_BRANCH" \
  "Draft: Resolve \"<Issue名称>\"" \
  --desc "## 变更概述\n🚧 开发中...\n\n## 关联 Issue\nCloses #<issue-id>" \
  --assignee_id <当前用户ID>

# --- curl 方式（兜底） ---
# 先创建分支
curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"branch": "'$SOURCE_BRANCH'", "ref": "main"}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/repository/branches"

# 创建 MR
curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_branch": "'$SOURCE_BRANCH'",
    "target_branch": "main",
    "title": "Draft: Resolve \"<Issue名称>\"",
    "description": "## 变更概述\n🚧 开发中...\n\n## 关联 Issue\nCloses #<issue-id>",
    "assignee_ids": [<当前用户ID>],
    "remove_source_branch": true,
    "draft": true
  }' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests"
```

#### 步骤6：输出结果

```
✅ 工作流创建完成：

📋 Issue: #<id> - <标题>
   URL: https://git.graspishop.com/<project>/-/issues/<id>

🔀 Draft MR: !<id> - Draft: Resolve "<标题>"
   URL: https://git.graspishop.com/<project>/-/merge_requests/<id>

🌿 分支: <issue-id>-<描述>

现在可以拉取分支开始开发：
  git fetch --all
  git checkout <branch-name>
```

#### 步骤7：本地拉取分支开发

```bash
git fetch --all
git checkout <branch-name>
```

#### 步骤8：开发完成，推送代码

```bash
git add .
git commit -m "实现功能"
git push origin <branch-name>
```

#### 步骤9：Draft 转正式状态（自动执行）

```bash
# 将 Draft MR 转为正式状态
curl -s -X PUT -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Resolve \"<Issue名称>\""}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests/<mr-id>"
```

#### 步骤10：审核、合并（需确认）

**合并是不可逆操作，必须使用 `ask_user_question` 确认：**

```json
{
  "question": "MR 审核已通过，确认合并？",
  "options": [
    {"label": "✅ 合并 MR", "description": "合并后自动删除分支、关闭 Issue"},
    {"label": "⏸️ 暂不合并", "description": "等待进一步确认"}
  ]
}
```

**合并命令：**
```bash
curl -s -X PUT -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"should_remove_source_branch": true}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests/<mr-id>/merge"
```

---

## 操作模块

### 模块1：Issue 管理

#### 创建 Issue

**触发：** "创建一个 issue：XXX" 或 "记录一个问题：XXX"

```bash
curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "<title>",
    "description": "<description>",
    "labels": "bug,feature",
    "assignee_ids": [<user_id>]
  }' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/issues"
```

**Issue 标题规范：**

直接使用中文描述，不带前缀。**必须通过命名合规校验。**

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
curl -s -H "Private-Token: $TOKEN" \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/issues?assignee_username=<current_user>&state=opened"

# 查看项目所有打开的 Issue
curl -s -H "Private-Token: $TOKEN" \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/issues?state=opened"

# 搜索 Issue
curl -s -H "Private-Token: $TOKEN" \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/issues?search=<关键词>"

# 查看 Issue 详情
curl -s -H "Private-Token: $TOKEN" \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/issues/<issue-id>"
```

#### 更新 Issue

**触发：** "更新 issue #X"、"关闭 issue #X"

```bash
# 更新 Issue
curl -s -X PUT -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "<new-title>"}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/issues/<issue-id>"

# 关闭 Issue
curl -s -X PUT -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"state_event": "close"}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/issues/<issue-id>"

# 添加评论
curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"body": "<comment>"}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/issues/<issue-id>/notes"
```

---

### 模块2：分支管理

**⚠️ 重要：分支通过 API 创建**

按照团队工作流，分支是通过 API 在创建 MR 之前创建的，流程为：
```
创建 Issue → 创建分支 → 创建 Draft MR → 本地拉取开发
```

#### 拉取 MR 关联分支

**触发：** "拉取分支"、"切换到开发分支"、"开始开发"

```bash
# 查看远程分支
git fetch --all
git branch -r

# 拉取并切换到 MR 关联的分支
git checkout <branch-name>
```

**分支命名规范：**

格式：`{issue-id}-{Issue标题}`（与 Issue 标题完全一致，无类型前缀，不缩短）

| 示例 |
|------|
| `421-iShop开单神器` |
| `974-BUG修改` |
| `9750-商品性质档案` |

**⚠️ 分支名必须与 Issue 标题完全一致，禁止自行缩写或简化。**

#### 通过 API 创建分支

```bash
curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"branch": "<branch-name>", "ref": "main"}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/repository/branches"
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

# 删除远程分支（通过 API）
curl -s -X DELETE -H "Private-Token: $TOKEN" \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/repository/branches/<branch-name>"
```

---

### 模块3：Merge Request 管理

#### 创建关联 Issue 的 MR（Draft）

**⚠️ 标准流程：先创建分支，再创建 Draft MR**

**触发：** "为 issue #X 创建 MR"、"开始开发 issue #X"

```bash
# 1. 先创建分支
curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"branch": "<issue-id>-<Issue标题>", "ref": "main"}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/repository/branches"

# 2. 创建 Draft MR 并关联 Issue
curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_branch": "<issue-id>-<Issue标题>",
    "target_branch": "main",
    "title": "Draft: Resolve \"<Issue名称>\"",
    "description": "## 变更概述\n🚧 开发中...\n\n## 关联 Issue\nCloses #<issue-id>",
    "assignee_ids": [<当前用户ID>],
    "remove_source_branch": true,
    "draft": true
  }' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests"
```

**关键说明：**
- `draft: true`：创建为 Draft 状态（开发中）
- `remove_source_branch: true`：合并后自动删除源分支
- 分支名格式 `{issue-id}-{Issue标题}`（无前缀，不缩短）
- 描述中使用 `Closes #<issue-id>` 自动关闭关联 Issue
- `assignee_ids`：自动指派给当前登录用户

#### 创建 MR

**触发：** "创建 MR"、"提交合并请求"、"发起 code review"

```bash
curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source_branch": "<source-branch>",
    "target_branch": "main",
    "title": "<title>",
    "description": "<description>",
    "assignee_ids": [<user_id>],
    "remove_source_branch": true,
    "labels": "feature,review",
    "draft": false
  }' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests"
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
# 将 Draft MR 转换为正式状态（更新标题去掉 Draft: 前缀）
curl -s -X PUT -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Resolve \"<Issue名称>\""}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests/<mr-id>"
```

#### 查询 MR

**触发：** "查看我的 MR"、"有哪些待审核的 MR"

```bash
# 查看我创建的 MR
curl -s -H "Private-Token: $TOKEN" \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests?author_username=<current_user>&state=opened"

# 查看所有打开的 MR
curl -s -H "Private-Token: $TOKEN" \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests?state=opened"

# 查看 MR 详情
curl -s -H "Private-Token: $TOKEN" \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests/<mr-id>"

# MR 变更
curl -s -H "Private-Token: $TOKEN" \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests/<mr-id>/changes"
```

#### 审核 MR

**触发：** "审核 MR #X"、"审查代码"

```bash
# 批准 MR
curl -s -X POST -H "Private-Token: $TOKEN" \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests/<mr-id>/approve"

# 添加评论
curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"body": "<comment>"}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests/<mr-id>/notes"
```

#### 合并 MR（需确认）

**触发：** "合并 MR #X"

**⚠️ 合并是不可逆操作，必须先确认。**

```bash
# 合并 MR 并删除源分支
curl -s -X PUT -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"should_remove_source_branch": true}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests/<mr-id>/merge"
```

---

## 智能识别场景

### 场景1：用户描述开发意图

**用户说：** "我要开发一个用户登录功能"

**自动处理（不询问用户）：**
1. 自动推断为 feature 类型
2. 校验名称合规性
3. 确定项目（从上下文或让用户选择）
4. 获取当前用户信息
5. 创建 Issue（标题：`用户登录功能`，标签：feature，指派：当前用户）
6. 创建分支 + Draft MR
7. 输出完整结果，提示拉取分支开发

### 场景2：用户描述修复意图

**用户说：** "需要修复登录页面的崩溃问题"

**自动处理（不询问用户）：**
1. 自动推断为 bug 类型（包含"修复""崩溃"关键词）
2. 校验名称合规性
3. 确定项目 → 获取当前用户 → 创建 Issue → 创建分支 + Draft MR
4. 输出完整结果

### 场景3：用户完成开发

**用户说：** "登录功能开发完成了"、"准备好了，请审核"

**自动处理：**
1. 查找当前分支对应的 MR
2. 自动将 Draft MR 转换为正式状态（curl 直接执行）
3. 输出 MR 链接

### 场景4：用户查看工作状态

**用户说：** "我有什么待处理的工作？"

**自动处理（直接查询）：**
1. 查询指派给用户的打开的 Issues
2. 查询用户创建的打开的 MRs
3. 汇总展示工作状态

---

## 配置参数

通过 Git 配置或环境变量配置：

| 参数 | 配置方式 | 说明 |
|------|----------|------|
| GitLab URL | 固定值 | `https://git.graspishop.com/` |
| GitLab Token | `git config --global gitlab.token` | Personal Access Token |
| 默认目标分支 | - | MR 默认目标分支，默认 `main` |
| 自动删除分支 | - | MR 合并后自动删除分支，默认 `true` |

**注意：** 项目通过对话上下文推断，或让用户从项目列表中选择。不检测当前工作目录。

---

## 工作流模板

### 模板1：新功能开发完整流程

```bash
# ====== 准备：获取当前用户 ======
TOKEN=$(git config --global gitlab.token)
USER=$(curl -s -H "Private-Token: $TOKEN" https://git.graspishop.com/api/v4/user)
# 从返回 JSON 中提取 id 和 username

PROJECT_PATH="igroup%2Fishop"

# ====== 步骤1：创建 Issue（自动推断 feature 类型） ======
curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "用户登录功能", "labels": "feature", "assignee_ids": [USER_ID]}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/issues"
# 输出：Issue #421 已创建

# ====== 步骤2：创建分支 ======
curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"branch": "421-用户登录功能", "ref": "main"}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/repository/branches"

# ====== 步骤3：创建 Draft MR ======
curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source_branch": "421-用户登录功能", "target_branch": "main", "title": "Draft: Resolve \"用户登录功能\"", "description": "## 变更概述\n🚧 开发中...\n\nCloses #421", "assignee_ids": [USER_ID], "remove_source_branch": true, "draft": true}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests"
# 输出：MR !45 已创建

# ====== 步骤4：本地拉取分支开发 ======
git fetch --all
git checkout 421-用户登录功能
# 开始开发...

# ====== 步骤5：开发完成，推送代码 ======
git add .
git commit -m "实现用户登录功能"
git push origin 421-用户登录功能

# ====== 步骤6：Draft 转正式状态 ======
curl -s -X PUT -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Resolve \"用户登录功能\""}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests/45"

# ====== 步骤7：合并（需用户确认） ======
curl -s -X PUT -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"should_remove_source_branch": true}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests/45/merge"
# 自动触发：关闭 Issue #421、删除分支
```

### 模板2：Bug 修复完整流程

```bash
# ====== 准备 ======
TOKEN=$(git config --global gitlab.token)
PROJECT_PATH="igroup%2Fishop"

# ====== 步骤1：创建 Issue（自动推断 bug 类型） ======
curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "974BUG修改", "labels": "bug", "assignee_ids": [USER_ID]}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/issues"
# 输出：Issue #974 已创建

# ====== 步骤2：创建分支 + Draft MR ======
curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"branch": "974-BUG修改", "ref": "main"}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/repository/branches"

curl -s -X POST -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source_branch": "974-BUG修改", "target_branch": "main", "title": "Draft: Resolve \"974BUG修改\"", "description": "## 问题\n[问题描述]\n\nFixes #974", "assignee_ids": [USER_ID], "remove_source_branch": true, "draft": true}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests"

# ====== 步骤3：本地拉取分支修复 ======
git fetch --all
git checkout 974-BUG修改
# 修复 bug...

# ====== 步骤4：修复完成，推送代码 ======
git add .
git commit -m "修复问题"
git push origin 974-BUG修改

# ====== 步骤5：Draft 转正式状态 ======
curl -s -X PUT -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Resolve \"974BUG修改\""}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests/<mr-id>"

# ====== 步骤6：合并（需用户确认） ======
curl -s -X PUT -H "Private-Token: $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"should_remove_source_branch": true}' \
  "https://git.graspishop.com/api/v4/projects/$PROJECT_PATH/merge_requests/<mr-id>/merge"
```

---

## 错误处理

### 认证失败

```
{"message":"401 Unauthorized"}
```

**解决：**
1. 检查 Token 是否正确配置：`git config --global gitlab.token`
2. 确认 Token 有 `api` 权限
3. 确认 Token 未过期
4. 访问 https://git.graspishop.com/-/profile/personal_access_tokens 重新生成

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
- GitLab API 文档：`https://git.graspishop.com/help/api/README.md`

