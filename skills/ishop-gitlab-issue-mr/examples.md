# GitLab Issue & MR 管理技能 - 使用示例

本文档提供 `ishop-gitlab-issue-mr` 技能的使用示例，帮助快速上手。

**⚠️ 标准工作流程（全自动执行，无需逐步确认）：**
```
创建 Issue → 创建 Draft MR + 关联分支 → 本地拉取开发 → 推送代码 → Draft 转正式 → 请求审核 → 合并（自动关闭 Issue/MR/删除分支）
```

**核心原则：**
- API 调用三级优先：glab CLI → Python 脚本 → curl 兜底
- 所有 API 调用默认直接执行，不询问用户
- Issue 类型根据名称自动推断
- 指派人自动为当前登录用户
- 仅在必要时询问（选择项目、命名不合规、合并/删除等不可逆操作）

---

## 环境配置

### GitLab 服务器信息

| 配置项 | 值 |
|--------|-----|
| GitLab URL | `https://git.graspishop.com/` |

### 首次配置

**步骤1：创建 Personal Access Token**

```
1. 访问：https://git.graspishop.com/-/profile/personal_access_tokens
2. 点击 "Add new token"
3. 配置：
   - 名称：qoder-agent
   - 权限：勾选 api
   - 过期时间：根据需要设置
4. 点击 "Create personal access token"
5. 复制生成的 Token（glpat-xxxxxxxxxxxxxxxx）
```

**步骤2：配置认证（按优先级选择）**

```bash
# 方式1：glab CLI 认证（最优先）
glab auth login --hostname git.graspishop.com --token glpat-xxxxxxxxxxxxxxxx

# 方式2：Git 全局配置（Python 脚本和 curl 使用）
git config --global gitlab.token "glpat-xxxxxxxxxxxxxxxx"

# 方式3：环境变量
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxx"
```

**步骤3：验证配置**

```bash
# glab 方式
glab auth status --hostname git.graspishop.com

# Python 脚本方式
python3 scripts/gitlab_api.py user

# curl 方式
TOKEN=$(git config --global gitlab.token || echo $GITLAB_TOKEN)
curl -s -H "Private-Token: $TOKEN" https://git.graspishop.com/api/v4/user
```

### 项目识别

**上下文驱动：** 技能通过对话上下文推断要操作的项目，而非检测当前目录

- 如果用户提到了项目名称 → 直接使用
- 如果上下文未提及项目 → 调用 API 列出项目让用户选择

```bash
# glab 方式（优先）
glab api /projects?membership=true\&per_page=100 --hostname git.graspishop.com

# Python 脚本方式
python3 scripts/gitlab_api.py projects

# curl 方式（兜底）
TOKEN=$(git config --global gitlab.token || echo $GITLAB_TOKEN)
curl -s -H "Private-Token: $TOKEN" "https://git.graspishop.com/api/v4/projects?membership=true&per_page=100" \
  | python3 -c "import sys,json; [print(json.dumps({'path': p['path_with_namespace'], 'name': p['name'], 'desc': p.get('description','')}, ensure_ascii=False)) for p in json.loads(sys.stdin.read())]"
```

**选择项目时，必须展示项目路径和描述：**

```json
{
  "question": "请选择要操作的项目：",
  "options": [
    {"label": "1. igroup/ishop", "description": "iShop ERP 主项目 - 进销存管理系统"},
    {"label": "2. igroup/ishop-web", "description": "iShop Web 前端"},
    {"label": "3. igroup/ancestry", "description": "Ancestry 族谱项目"}
  ]
}
```

---

## 示例1：完整功能开发流程

### 用户输入

```
在 igroup/ishop 项目下，我要开发一个用户登录功能
```

### Agent 执行流程（全自动，无需用户逐步确认）

**步骤1：识别意图并确定项目**

```
✅ 识别为：新功能开发
✅ 从上下文识别项目：igroup/ishop
✅ 自动推断 Issue 类型：feature（关键词：开发、功能）
```

**步骤2：获取当前用户信息（自动执行）**

```bash
# glab 方式（优先）
glab api /user --hostname git.graspishop.com

# Python 脚本方式
python3 scripts/gitlab_api.py user

# curl 方式（兜底）
TOKEN=$(git config --global gitlab.token || echo $GITLAB_TOKEN)
USER_ID=$(curl -s -H "Private-Token: $TOKEN" "https://git.graspishop.com/api/v4/user" | jq '.id')
```

**步骤3：校验命名合规性**

```
✅ 标题 "用户登录功能" 合规（无特殊字符）
✅ 分支名 "421-用户登录功能" 合规
```

> 如果名称包含 `< > : " / \ | ? * # %` 等特殊字符，会要求用户重新提供合规名称。

**步骤4：创建 Issue（自动执行）**

```bash
# glab 方式（优先）
glab api /projects/igroup%2Fishop/issues --hostname git.graspishop.com -X POST \
  -f title="用户登录功能" \
  -f description="## 描述
实现用户登录功能，支持账号密码登录和第三方登录。" \
  -f labels="feature" -f assignee_ids[]=$USER_ID

# Python 脚本方式
python3 scripts/gitlab_api.py create_issue "igroup/ishop" "用户登录功能" \
  --desc "## 描述\n实现用户登录功能" --labels "feature" --assignee_id $USER_ID

# curl 方式（兜底）
curl -s -X POST -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"title": "用户登录功能", "description": "## 描述\n实现用户登录功能，支持账号密码登录和第三方登录。\n\n## 验收标准\n- [ ] 账号密码登录\n- [ ] 记住密码功能\n- [ ] 登录状态持久化", "labels": "feature", "assignee_ids": ['$USER_ID']}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/issues"
```

**输出：**
```
✅ Issue #421 已创建
   类型: feature（自动推断）
   指派: 当前用户（自动）
   URL: https://git.graspishop.com/igroup/ishop/-/issues/421
```

**步骤5：创建 Draft MR + 关联分支（自动执行）**

```bash
# glab 方式（优先）
glab api /projects/igroup%2Fishop/merge_requests --hostname git.graspishop.com -X POST \
  -f source_branch="421-用户登录功能" -f target_branch="main" \
  -f title='Draft: Resolve "用户登录功能"' \
  -f description="## 变更概述
🚧 开发中...

Closes #421" \
  -f assignee_id=$USER_ID -f remove_source_branch=true

# Python 脚本方式
python3 scripts/gitlab_api.py create_mr "igroup/ishop" "421-用户登录功能" \
  'Draft: Resolve "用户登录功能"' \
  --desc "## 变更概述\n🚧 开发中...\n\nCloses #421" \
  --assignee_id $USER_ID

# curl 方式（兜底）
curl -s -X POST -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"source_branch": "421-用户登录功能", "target_branch": "main", "title": "Draft: Resolve \"用户登录功能\"", "description": "## 变更概述\n🚧 开发中...\n\n## 关联 Issue\nCloses #421", "assignee_id": '$USER_ID', "remove_source_branch": true}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests"
```

**输出：**
```
✅ Draft MR !45 已创建
   分支: 421-用户登录功能
   URL: https://git.graspishop.com/igroup/ishop/-/merge_requests/45

现在可以拉取分支开始开发了。
```

**步骤6：本地拉取分支开发**

```bash
git fetch --all
git checkout 421-用户登录功能

# 开始开发...
```

**步骤7：开发完成，推送代码**

```bash
git add .
git commit -m "实现用户登录功能"
git push origin 421-用户登录功能
```

**步骤8：Draft 转正式状态（自动执行）**

用户说："登录功能开发完成了"

```bash
curl -s -X PUT -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"title": "Resolve \"用户登录功能\""}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests/45"
```

**步骤9：请求审核**

```
✅ MR !45 已准备就绪

@reviewer 您好，MR !45 已准备就绪，请审核。
MR 链接：https://git.graspishop.com/igroup/ishop/-/merge_requests/45
```

**步骤10：合并（需用户确认 - 不可逆操作）**

```bash
# 合并 MR（删除源分支）
curl -s -X PUT -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"should_remove_source_branch": true}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests/45/merge"
```

**输出：**
```
✅ MR !45 已合并
   分支 421-用户登录功能 已删除
   Issue #421 已自动关闭
```

---

## 示例2：Bug 修复流程

### 用户输入

```
需要修复登录页面在输入特殊字符时崩溃的问题
```

### Agent 执行流程（全自动）

**步骤1：识别意图并自动推断**

```
✅ 识别为：Bug 修复（关键词：修复、崩溃）
✅ 自动推断 Issue 类型：bug
✅ 上下文未指定项目 → 询问用户选择项目
```

**步骤2：创建 Issue（自动执行）**

```bash
# glab 方式（优先）
glab api /projects/igroup%2Fishop/issues --hostname git.graspishop.com -X POST \
  -f title="登录页面输入特殊字符时崩溃" \
  -f description="## 问题描述
当用户在登录页面输入特殊字符时，应用发生崩溃。" \
  -f labels="bug,high-priority" -f assignee_ids[]=$USER_ID

# Python 脚本方式
python3 scripts/gitlab_api.py create_issue "igroup/ishop" "登录页面输入特殊字符时崩溃" \
  --desc "## 问题描述\n当用户在登录页面输入特殊字符时崩溃" \
  --labels "bug,high-priority" --assignee_id $USER_ID

# curl 方式（兜底）
TOKEN=$(git config --global gitlab.token || echo $GITLAB_TOKEN)
USER_ID=$(curl -s -H "Private-Token: $TOKEN" "https://git.graspishop.com/api/v4/user" | jq '.id')
curl -s -X POST -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"title": "登录页面输入特殊字符时崩溃", "description": "## 问题描述\n当用户在登录页面输入特殊字符时，应用发生崩溃。", "labels": "bug,high-priority", "assignee_ids": ['$USER_ID']}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/issues"
```

**步骤3：创建 Draft MR + 关联分支（自动执行）**

```bash
# glab 方式（优先）
glab api /projects/igroup%2Fishop/merge_requests --hostname git.graspishop.com -X POST \
  -f source_branch="974-登录页面输入特殊字符时崩溃" -f target_branch="main" \
  -f title='Draft: Resolve "登录页面输入特殊字符时崩溃"' \
  -f description="🚧 修复中...

Fixes #974" \
  -f assignee_id=$USER_ID -f remove_source_branch=true

# Python 脚本方式
python3 scripts/gitlab_api.py create_mr "igroup/ishop" "974-登录页面输入特殊字符时崩溃" \
  'Draft: Resolve "登录页面输入特殊字符时崩溃"' \
  --desc "🚧 修复中...\n\nFixes #974" --assignee_id $USER_ID

# curl 方式（兜底）
curl -s -X POST -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"source_branch": "974-登录页面输入特殊字符时崩溃", "target_branch": "main", "title": "Draft: Resolve \"登录页面输入特殊字符时崩溃\"", "description": "🚧 修复中...\n\nFixes #974", "assignee_id": '$USER_ID', "remove_source_branch": true}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests"
```

**步骤4：本地拉取分支修复**

```bash
git fetch --all
git checkout 974-登录页面输入特殊字符时崩溃

# 修复 bug...
```

**步骤5：修复完成，推送代码**

```bash
git add .
git commit -m "添加输入验证防止特殊字符崩溃"
git push origin 974-登录页面输入特殊字符时崩溃
```

**步骤6：Draft 转正式状态（自动执行）**

```bash
curl -s -X PUT -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"title": "Resolve \"登录页面输入特殊字符时崩溃\""}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests/46"
```

**步骤7：合并（需用户确认）**

```bash
curl -s -X PUT -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"should_remove_source_branch": true}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests/46/merge"

# 自动触发：关闭 Issue #974、删除分支
```

---

## 示例3：查询工作状态

### 用户输入

```
我有什么待处理的工作？
```

### Agent 执行流程（自动执行）

```bash
# === glab 方式（优先） ===
glab api "/projects/igroup%2Fishop/issues?assignee_username=$USERNAME&state=opened" --hostname git.graspishop.com
glab api "/projects/igroup%2Fishop/merge_requests?author_username=$USERNAME&state=opened" --hostname git.graspishop.com
glab api "/projects/igroup%2Fishop/merge_requests?reviewer_username=$USERNAME&state=opened" --hostname git.graspishop.com

# === Python 脚本方式 ===
python3 scripts/gitlab_api.py list_issues "igroup/ishop" --assignee $USERNAME --state opened
python3 scripts/gitlab_api.py list_mrs "igroup/ishop" --author $USERNAME --state opened

# === curl 方式（兜底） ===
TOKEN=$(git config --global gitlab.token || echo $GITLAB_TOKEN)
USERNAME=$(curl -s -H "Private-Token: $TOKEN" "https://git.graspishop.com/api/v4/user" | jq -r '.username')
curl -s -H "Private-Token: $TOKEN" "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/issues?assignee_username=$USERNAME&state=opened"
curl -s -H "Private-Token: $TOKEN" "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests?author_username=$USERNAME&state=opened"
curl -s -H "Private-Token: $TOKEN" "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests?reviewer_username=$USERNAME&state=opened"
```

### 输出示例

```
📋 您的工作状态汇总

🔴 待处理的 Issues (3个)
   #126 商品搜索功能 [feature]
   #125 列表加载性能问题 [bug]
   #124 登录页面特殊字符导致崩溃 [bug]

🟡 待审核的 MRs (2个)
   !48 订单导出功能
   !47 修复支付金额计算错误

🟢 我创建的 MRs (1个)
   !45 实现用户登录功能 [待审核]
```

---

## 示例4：仅创建 Issue

### 用户输入

```
创建一个 issue：优化商品列表的加载性能
```

### Agent 执行流程（自动执行）

```
✅ 自动推断 Issue 类型：improvement（关键词：优化）
✅ 标题 "优化商品列表的加载性能" 合规
```

```bash
# glab 方式（优先）
glab api /projects/igroup%2Fishop/issues --hostname git.graspishop.com -X POST \
  -f title="优化商品列表的加载性能" \
  -f description="## 当前问题
商品列表在数据量大时加载缓慢" \
  -f labels="improvement,performance" -f assignee_ids[]=$USER_ID

# Python 脚本方式
python3 scripts/gitlab_api.py create_issue "igroup/ishop" "优化商品列表的加载性能" \
  --desc "## 当前问题\n商品列表在数据量大时加载缓慢" \
  --labels "improvement,performance" --assignee_id $USER_ID

# curl 方式（兜底）
TOKEN=$(git config --global gitlab.token || echo $GITLAB_TOKEN)
USER_ID=$(curl -s -H "Private-Token: $TOKEN" "https://git.graspishop.com/api/v4/user" | jq '.id')
curl -s -X POST -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"title": "优化商品列表的加载性能", "description": "## 当前问题\n商品列表在数据量大时加载缓慢", "labels": "improvement,performance", "assignee_ids": ['$USER_ID']}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/issues"
```

---

## 示例5：审核 MR

### 用户输入

```
审核 MR !48
```

### Agent 执行流程（自动执行查询，审核操作需确认）

**步骤1：查看 MR 详情（自动执行）**

```bash
# glab 方式（优先）
glab api /projects/igroup%2Fishop/merge_requests/48 --hostname git.graspishop.com
glab api /projects/igroup%2Fishop/merge_requests/48/changes --hostname git.graspishop.com

# Python 脚本方式
python3 scripts/gitlab_api.py list_mrs "igroup/ishop" --iid 48

# curl 方式（兜底）
TOKEN=$(git config --global gitlab.token || echo $GITLAB_TOKEN)
curl -s -H "Private-Token: $TOKEN" "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests/48"
curl -s -H "Private-Token: $TOKEN" "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests/48/changes"
```

**步骤2：审核决策**

**情况A：通过审核**
```bash
# glab 方式
glab api /projects/igroup%2Fishop/merge_requests/48/approve --hostname git.graspishop.com -X POST
glab api /projects/igroup%2Fishop/merge_requests/48/notes --hostname git.graspishop.com -X POST \
  -f body="LGTM! 代码质量良好，测试覆盖充分。"

# curl 方式
curl -s -X POST -H "Private-Token: $TOKEN" \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests/48/approve"
curl -s -X POST -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"body": "LGTM! 代码质量良好，测试覆盖充分。"}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests/48/notes"
```

**情况B：请求修改**
```bash
# glab 方式
glab api /projects/igroup%2Fishop/merge_requests/48/notes --hostname git.graspishop.com -X POST \
  -f body="请处理以下问题：
1. 缺少单元测试
2. 命名不够清晰"

# curl 方式
curl -s -X POST -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"body": "请处理以下问题：\n1. 缺少单元测试\n2. 命名不够清晰\n3. 注释建议统一使用英文"}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests/48/notes"
```

---

## 示例6：合并 MR

### 用户输入

```
合并 MR !45
```

### Agent 执行流程（合并为不可逆操作，需用户确认）

```bash
# === 检查 MR 状态（自动执行） ===
# glab 方式
glab api /projects/igroup%2Fishop/merge_requests/45 --hostname git.graspishop.com

# Python 脚本方式
python3 scripts/gitlab_api.py list_mrs "igroup/ishop" --iid 45

# curl 方式
TOKEN=$(git config --global gitlab.token || echo $GITLAB_TOKEN)
curl -s -H "Private-Token: $TOKEN" "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests/45"

# === 执行合并（用户确认后执行，has_risk: true） ===
# glab 方式
glab api /projects/igroup%2Fishop/merge_requests/45/merge --hostname git.graspishop.com -X PUT \
  -f should_remove_source_branch=true

# Python 脚本方式
python3 scripts/gitlab_api.py merge_mr "igroup/ishop" 45

# curl 方式
curl -s -X PUT -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"should_remove_source_branch": true}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests/45/merge"
```

**输出：**
```
✅ MR !45 已合并
   分支 421-用户登录功能 已删除
   Issue #421 已自动关闭
```

---

## 示例7：分支管理

### 创建发布分支

```bash
# 用户输入：创建 v1.2.0 发布分支

git checkout main
git pull
git checkout -b release/v1.2.0
git push -u origin release/v1.2.0
```

### 查看分支状态

```bash
# 用户输入：查看当前有哪些分支

git branch -a
```

**输出示例：**
```
本地分支：
  * main
    feature/126-product-search
    fix/125-list-performance

远程分支：
  origin/main
  origin/feature/126-product-search
  origin/fix/125-list-performance
  origin/release/v1.1.0
```

---

## 示例8：Draft MR

### 用户输入

```
创建一个草稿 MR，先保存当前进度
```

### Agent 执行流程（自动执行）

```bash
# glab 方式（优先）
glab api /projects/igroup%2Fishop/merge_requests --hostname git.graspishop.com -X POST \
  -f source_branch="126-商品搜索功能" -f target_branch="main" \
  -f title="Draft: 商品搜索功能" \
  -f description="🚧 WIP: 功能开发中

Relates to #126" \
  -f assignee_id=$USER_ID -f remove_source_branch=true

# Python 脚本方式
python3 scripts/gitlab_api.py create_mr "igroup/ishop" "126-商品搜索功能" \
  "Draft: 商品搜索功能" \
  --desc "🚧 WIP: 功能开发中\n\nRelates to #126" --assignee_id $USER_ID

# curl 方式（兜底）
TOKEN=$(git config --global gitlab.token || echo $GITLAB_TOKEN)
USER_ID=$(curl -s -H "Private-Token: $TOKEN" "https://git.graspishop.com/api/v4/user" | jq '.id')
curl -s -X POST -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"source_branch": "126-商品搜索功能", "target_branch": "main", "title": "Draft: 商品搜索功能", "description": "🚧 WIP: 功能开发中\n\nRelates to #126", "assignee_id": '$USER_ID', "remove_source_branch": true}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests"
```

**输出：**
```
✅ Draft MR 创建成功
   ID: !50
   状态: Draft (草稿)

开发完成后，使用以下命令转为正式 MR：
curl -s -X PUT -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"title": "商品搜索功能"}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests/50"
```

---

## 常见场景速查

| 场景 | 用户输入 | Agent 操作 | 是否自动 |
|------|----------|------------|----------|
| 开始新功能 | "我要开发XX功能" | 创建 Issue → 创建 Draft MR + 分支 | ✅ 全自动 |
| 报告Bug | "发现一个bug：XX" | 创建 Issue（类型自动推断为 bug） | ✅ 全自动 |
| 开始修复 | "开始修复 issue #X" | 创建 Draft MR + 分支 | ✅ 全自动 |
| 拉取分支开发 | "拉取分支"、"开始开发" | git checkout 远程分支 | ✅ 全自动 |
| 开发完成 | "开发完成了" | Draft MR 转正式 → 请求审核 | ✅ 全自动 |
| 查看工作 | "我有什么工作" | 查询 Issues 和 MRs | ✅ 全自动 |
| 审核代码 | "审核 MR !XX" | 查看 MR → 批准/请求修改 | ✅ 查询自动 |
| 合并代码 | "合并 MR !XX" | 合并 → 自动关闭 Issue/删除分支 | ⚠️ 需确认 |

## 命名规范速查

| 项目 | 格式 | 示例 |
|------|------|------|
| Issue 名称 | 中文描述（无前缀） | `开发iShop开单神器` |
| Draft MR | `Draft: Resolve "{Issue名称}"` | `Draft: Resolve "开发iShop开单神器"` |
| 正式 MR | `Resolve "{Issue名称}"` | `Resolve "开发iShop开单神器"` |
| 分支名称 | `{issue-id}-{描述}` | `421-iShop开单神器` |

---

## 错误处理示例

### 认证失败

```bash
# glab 认证失败
$ glab auth status --hostname git.graspishop.com
error: failed to authenticate

# 解决：重新登录
glab auth login --hostname git.graspishop.com --token glpat-xxxxxxxxxxxxxxxx

# curl/Python 认证失败
$ curl -s -H "Private-Token: $TOKEN" "https://git.graspishop.com/api/v4/user"
{"message":"401 Unauthorized"}

# 解决：配置 Token
git config --global gitlab.token "glpat-xxxxxxxxxxxxxxxx"
# 或
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxx"
```

### 命名不合规

```
用户输入：创建 issue：修复 #bug <紧急>

❌ 标题包含特殊字符：# < >
请提供合规的 Issue 标题（禁止使用 < > : " / \ | ? * # % { } [ ] 等字符）
```

### 分支已存在

```bash
# API 返回分支已存在
{"message":"Branch already exists"}

# 解决
# 方案1：切换到已存在的分支
git checkout 421-用户登录功能

# 方案2：使用新分支名
git checkout -b 421-用户登录功能-v2
```

### MR 冲突

```bash
# API 返回冲突
{"message":"Branch cannot be merged"}

# 解决
# 1. 拉取目标分支最新代码
git checkout main
git pull

# 2. 切换到开发分支并 rebase
git checkout 421-用户登录功能
git rebase main

# 3. 解决冲突后推送
git push -f origin 421-用户登录功能

# 4. 再次尝试合并
curl -s -X PUT -H "Private-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"should_remove_source_branch": true}' \
  "https://git.graspishop.com/api/v4/projects/igroup%2Fishop/merge_requests/45/merge"
```

