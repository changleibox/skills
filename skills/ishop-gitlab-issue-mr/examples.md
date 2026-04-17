# GitLab Issue & MR 管理技能 - 使用示例

本文档提供 `ishop-gitlab-issue-mr` 技能的使用示例，帮助快速上手。

**⚠️ 标准工作流程：**
```
创建 Issue → 创建 Draft MR + 关联分支 → 本地拉取开发 → 推送代码 → Draft 转正式 → 请求审核 → 合并（自动关闭 Issue/MR/删除分支）
```

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

**步骤2：配置 Token（二选一）**

```bash
# 方式1：Git 全局配置（推荐）
git config --global gitlab.token "glpat-xxxxxxxxxxxxxxxx"

# 方式2：环境变量
export GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxx"
```

**步骤3：验证配置**

```bash
# 验证 glab CLI 认证状态
glab auth status

# 或测试 API 访问
curl -H "Private-Token: $(git config --global gitlab.token)" \
  https://git.graspishop.com/api/v4/user
```

### 项目识别

**自动检测：** 技能通过当前目录的 Git 配置自动识别项目

```bash
# 确保在 Git 仓库目录内操作
cd /path/to/your/project

# 验证项目识别
git remote get-url origin
# 输出示例：git@git.graspishop.com:igroup/ishop.git
```

**项目解析规则：**
- `git@git.graspishop.com:igroup/ishop.git` → 项目 `igroup/ishop`

---

## 示例1：完整功能开发流程

### 用户输入

```
我要开发一个用户登录功能
```

### Agent 执行流程

**步骤1：识别意图**
```
✅ 识别为：新功能开发
📝 建议创建 Issue 记录此需求
```

**步骤2：创建 Issue**

```bash
glab issue create \
  --title "用户登录功能" \
  --description "## 描述
实现用户登录功能，支持账号密码登录和第三方登录。

## 验收标准
- [ ] 账号密码登录
- [ ] 记住密码功能
- [ ] 登录状态持久化"
```

**输出：**
```
✅ Issue 创建成功
   ID: #421
   URL: https://git.graspishop.com/team/project/-/issues/421

是否创建 Draft MR 并开始开发？
```

**步骤3：创建 Draft MR + 关联分支**

```bash
# 用户确认后
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
```

**输出：**
```
✅ Draft MR 创建成功
   MR: !45
   分支: 421-用户登录功能
   URL: https://git.graspishop.com/team/project/-/merge_requests/45

现在可以拉取分支开始开发了。
```

**步骤4：本地拉取分支开发**

```bash
git fetch --all
git checkout 421-用户登录功能

# 开始开发...
```

**步骤5：开发完成，推送代码**

```bash
# 开发完成后
git add .
git commit -m "实现用户登录功能"
git push origin 421-用户登录功能
```

**步骤6：Draft 转正式状态**

用户说："登录功能开发完成了"

```bash
# 将 Draft MR 转为正式状态
glab mr ready 45

# MR 标题自动变为：Resolve "用户登录功能"
```

**步骤7：请求审核**

```
✅ MR !45 已准备就绪

@reviewer 您好，MR !45 已准备就绪，请审核。
MR 链接：https://git.graspishop.com/team/project/-/merge_requests/45
```

**步骤8：审核、合并**

```bash
# 审核人审核通过
glab mr approve 45

# 合并 MR
glab mr merge 45 --delete-branch
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

### Agent 执行流程

**步骤1：识别意图**

```
✅ 识别为：Bug 修复
📝 创建 Issue 记录此问题
```

**步骤2：创建 Issue**

```bash
glab issue create \
  --title "[Bug] 登录页面输入特殊字符时崩溃" \
  --description "## 问题描述
当用户在登录页面输入特殊字符（如 emoji 或特殊符号）时，应用发生崩溃。

## 复现步骤
1. 打开登录页面
2. 在用户名输入框输入特殊字符
3. 点击登录按钮
4. 应用崩溃

## 预期行为
应正确处理特殊字符，给出友好的错误提示。

## 影响范围
- 登录页面
- 输入验证模块" \
  --label "bug,high-priority"
```

**步骤3：创建 Draft MR + 关联分支**

```bash
glab mr create \
  --title "Draft: Resolve \"登录页面输入特殊字符时崩溃\"" \
  --description "## 问题
登录页面在输入特殊字符时发生崩溃。

🚧 修复中...

Fixes #974" \
  --draft \
  --source-branch 974-登录特殊字符崩溃 \
  --target-branch main \
  --create-source-branch
```

**步骤4：本地拉取分支修复**

```bash
git fetch --all
git checkout 974-登录特殊字符崩溃

# 修复 bug...
```

**步骤5：修复完成，推送代码**

```bash
git add .
git commit -m "添加输入验证防止特殊字符崩溃"
git push origin 974-登录特殊字符崩溃
```

**步骤6：Draft 转正式状态并请求审核**

```bash
glab mr ready 46
```

**步骤7：合并**

```bash
glab mr merge 46 --delete-branch

# 自动触发：关闭 Issue #974、删除分支
```

---

## 示例3：查询工作状态

### 用户输入

```
我有什么待处理的工作？
```

### Agent 执行流程

```bash
# 查询指派给我的 Issues
glab issue list --assignee=@me --state=opened

# 查询我创建的 MR
glab mr list --author=@me --state=opened

# 查询待我审核的 MR
glab mr list --reviewer=@me --state=opened
```

### 输出示例

```
📋 您的工作状态汇总

🔴 待处理的 Issues (3个)
   #126 [Feature] 商品搜索功能
   #125 [Bug] 列表加载性能问题
   #124 [Bug] 登录页面特殊字符导致崩溃

🟡 待审核的 MRs (2个)
   !48 feat: 订单导出功能
   !47 fix: 修复支付金额计算错误

🟢 我创建的 MRs (1个)
   !45 feat(auth): 实现用户登录功能 [待审核]
```

---

## 示例4：仅创建 Issue

### 用户输入

```
创建一个 issue：优化商品列表的加载性能
```

### Agent 执行流程

```bash
glab issue create \
  --title "[Improvement] 优化商品列表加载性能" \
  --description "## 当前问题
商品列表在数据量大时加载缓慢，影响用户体验。

## 优化建议
- 实现分页加载
- 添加列表懒加载
- 优化数据查询

## 验收标准
- [ ] 列表加载时间 < 1秒
- [ ] 内存占用优化 50%
- [ ] 滚动流畅度提升" \
  --label "improvement,performance"
```

---

## 示例5：审核 MR

### 用户输入

```
审核 MR !48
```

### Agent 执行流程

**步骤1：查看 MR 详情**

```bash
glab mr view 48
glab mr diff 48
```

**步骤2：审核决策**

**情况A：通过审核**
```bash
glab mr approve 48
glab mr note 48 --message "LGTM! 代码质量良好，测试覆盖充分。"
```

**情况B：请求修改**
```bash
glab mr review 48 --request-changes --message "请处理以下问题：
1. 缺少单元测试
2. 命名不够清晰，建议使用更具描述性的变量名
3. 注释使用中文，建议统一使用英文"
```

---

## 示例6：合并 MR

### 用户输入

```
合并 MR !45
```

### Agent 执行流程

```bash
# 检查 MR 状态
glab mr view 45

# 执行合并
glab mr merge 45 --delete-branch
```

**输出：**
```
✅ MR !45 已合并
   分支 feature/123-user-login 已删除
   Issue #123 已自动关闭
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

### Agent 执行流程

```bash
glab mr create \
  --title "Draft: feat: 商品搜索功能" \
  --description "🚧 WIP: 功能开发中

## 当前进度
- [x] 搜索 UI
- [ ] 搜索逻辑
- [ ] 性能优化

Relates to #126" \
  --draft
```

**输出：**
```
✅ Draft MR 创建成功
   ID: !50
   状态: Draft (草稿)

开发完成后，可以转换为正式 MR：
   glab mr ready 50
```

---

## 常见场景速查

| 场景 | 用户输入 | Agent 操作 |
|------|----------|------------|
| 开始新功能 | "我要开发XX功能" | 创建 Issue → 创建 Draft MR + 分支 |
| 报告Bug | "发现一个bug：XX" | 创建 Issue |
| 开始修复 | "开始修复 issue #X" | 创建 Draft MR + 分支 |
| 拉取分支开发 | "拉取分支"、"开始开发" | git checkout 远程分支 |
| 开发完成 | "开发完成了"、"准备好了" | Draft MR 转正式 → 请求审核 |
| 查看工作 | "我有什么工作" | 查询 Issues 和 MRs |
| 审核代码 | "审核 MR !XX" | 查看 MR → 批准/请求修改 |
| 合并代码 | "合并 MR !XX" | 合并 → 自动关闭 Issue/删除分支 |

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
$ glab issue list
Error: authentication failed

# 解决
export GITLAB_TOKEN="glpat-xxxxxxxx"
glab auth login
```

### 分支已存在

```bash
$ git push -u origin feature/123-user-login
! [remote rejected] feature/123-user-login -> feature/123-user-login (branch already exists)

# 解决
# 方案1：切换到已存在的分支
git checkout feature/123-user-login

# 方案2：使用新分支名
git checkout -b feature/123-user-login-v2
```

### MR 冲突

```bash
$ glab mr merge 45
Error: merge conflict detected

# 解决
# 1. 拉取目标分支最新代码
git checkout main
git pull

# 2. 切换到开发分支并 rebase
git checkout feature/123-user-login
git rebase main

# 3. 解决冲突后推送
git push -f origin feature/123-user-login

# 4. 再次尝试合并
glab mr merge 45
```

