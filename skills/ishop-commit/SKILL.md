---
name: ishop-commit
description: Generate Conventional Commits-compliant commit messages by analyzing git diffs, perform code quality review, and validate code before committing. Use when the user requests to commit code, generate commit messages, or prepare staged changes for submission.
---

# Git Commit Helper

智能生成符合Conventional Commits规范的提交信息，并在提交前进行代码审查和验证。

## 何时使用

- 用户请求提交代码或生成提交信息
- 用户询问如何描述代码变更
- 用户要求审查即将提交的代码
- 用户提到"提交"、"commit"、"推送"等关键词

## 核心工作流程

### 阶段1：分析变更

1. **检查暂存区状态**
   ```bash
   git status
   git diff --cached
   ```

2. **如果暂存区为空**
   - 提示用户暂存变更：`git add <files>`
   - 询问是否需要帮助选择要暂存的文件

### 阶段2：代码审查（可选）

如果用户启用代码审查功能，检查以下方面：

**关键检查项**
- [ ] 代码逻辑正确性
- [ ] 潜在的空指针或异常处理问题
- [ ] 是否遵循项目代码规范
- [ ] 是否存在硬编码或魔法数字
- [ ] 函数/方法职责是否单一
- [ ] 命名是否清晰易懂

**Dart/Flutter 特定检查**
- [ ] Widget构造函数使用`super.key`而非`Key? key`
- [ ] 多参数构造函数使用末尾逗号
- [ ] 行宽不超过120字符
- [ ] 命名规范：类名大驼峰，变量名小驼峰，常量小写下划线
- [ ] 枚举使用点简写语法（如`.sales`而非`BillType.sales`）
- [ ] 使用`const`修饰不可变Widget

**反馈格式**
- 🔴 **严重问题**：必须修复才能提交
- 🟡 **建议改进**：可考虑优化
- 🟢 **良好实践**：值得保持的优点

### 阶段3：提交前验证（强制）

**⚠️ 重要：此阶段为强制步骤，所有问题必须在提交前解决！**

1. **运行代码格式化检查**
   ```bash
   dart format --set-exit-if-changed .
   ```

2. **运行Lint检查**
   ```bash
   dart analyze
   ```

3. **验证构建是否正常**（可选，大型项目可跳过）
   ```bash
   flutter build apk --debug --no-tree-shake-icons 2>&1 | head -n 50
   ```

#### 问题处理流程

**如果发现任何问题（错误、警告、提醒）：**

1. **列出所有问题**
   - 清晰展示每个问题的类型、位置和描述
   - 按严重程度分类：error > warning > info

2. **自动修复可修复的问题**
   - 格式问题：自动运行 `dart format .`
   - 可自动修复的lint问题：运行 `dart fix --apply`

3. **手动修复剩余问题**
   - 对于无法自动修复的问题，必须手动修改代码
   - 修复后重新运行验证

4. **重新验证**
   - 修复后必须重新运行 `dart analyze` 确认无问题
   - 只有当输出为 `No issues found!` 时才能继续

#### 强制要求

- ❌ **禁止跳过验证**：不允许在有警告或错误的情况下提交
- ❌ **禁止忽略问题**：所有 info 级别的提醒也必须处理
- ✅ **必须零问题**：只有 `dart analyze` 输出 `No issues found!` 才能继续提交流程

#### 问题示例

```
⚠️ 发现以下问题，必须修复后才能提交：

错误 (error): 1个
  - lib/src/example.dart:42:5 - Undefined name 'foo'

警告 (warning): 2个
  - lib/src/example.dart:50:10 - Unused import 'package:flutter/material.dart'
  - lib/src/example.dart:60:3 - Missing return type for function

提醒 (info): 3个
  - lib/src/example.dart:70:5 - Use 'const' with the constructor
  - lib/src/example.dart:80:10 - Unnecessary use of a 'double' literal
  - lib/src/example.dart:90:3 - To-do comment doesn't follow the Flutter style

请修复以上问题后重新运行验证。
```

### 阶段4：生成提交信息

基于变更内容生成符合Conventional Commits的提交信息。

#### 提交信息格式

```
<type>(<scope>): <subject>

<body>
```

#### 类型（Type）说明

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| `feat` | 新功能 | 添加新特性、新页面、新组件 |
| `fix` | 修复Bug | 修复已知问题、错误处理 |
| `docs` | 文档变更 | 修改README、注释、文档文件 |
| `style` | 代码格式 | 代码格式化、空格、分号等（不影响逻辑） |
| `refactor` | 代码重构 | 重构代码但不改变功能 |
| `perf` | 性能优化 | 提升性能的修改 |
| `test` | 测试相关 | 添加或修改测试用例 |
| `build` | 构建系统 | 修改构建脚本、依赖配置 |
| `ci` | CI/CD配置 | 修改CI配置文件 |
| `chore` | 其他杂项 | 不属于以上分类的修改 |

#### 范围（Scope）建议

根据项目结构选择合适的scope：

- **页面/模块**：`bills`, `goods`, `customer`, `report`, `auth`, `settings`
- **层级**：`ui`, `model`, `service`, `api`, `storage`, `routing`
- **平台**：`android`, `ios`, `ohos`
- **组件**：`button`, `form`, `table`, `dialog`

#### 主题（Subject）规则

- 使用中文描述（除非项目约定使用英文）
- 简洁明了，不超过50个字符
- 使用动词开头（如：添加、修复、优化、调整）
- 不以句号结尾

#### 正文（Body）

可选，用于详细说明：
- 为什么做这个变更
- 变更的影响范围
- 相关的Issue或需求编号

### 阶段5：执行提交

生成提交信息后：

1. **展示生成的提交信息**
   - 清晰展示type、scope、subject、body

2. **询问用户确认**
   - "是否使用此提交信息？"
   - 如果需要修改，允许用户编辑

3. **执行提交命令**
   ```bash
   git commit -m "<生成的提交信息>"
   ```

4. **确认提交成功**
   ```bash
   git log -1 --oneline
   ```

### 阶段6：推送到远程

提交成功后自动推送到远程仓库：

1. **执行推送**
   ```bash
   git push
   ```

2. **如果推送成功**
   - 显示推送结果
   - 显示相关的合并请求链接（如果有）
   - 提示完成

3. **如果推送失败（远程有新提交）**
   - 检测到冲突提示：`! [rejected] ... (fetch first)`
   - 自动执行rebase操作

#### Rebase冲突处理流程

当推送失败时，自动处理流程：

**步骤1：执行自动rebase**
```bash
git pull --rebase
```

**步骤2：检查rebase结果**

- **情况A：自动rebase成功**
  ```
  ✅ Rebase成功！自动变基已完成。
  现在重新推送到远程...
  ```
  然后自动执行：`git push`

- **情况B：存在冲突需要手动解决**
  ```
  ⚠️ Rebase遇到冲突，需要手动解决

  冲突文件：
  - path/to/file1.dart
  - path/to/file2.dart

  请按以下步骤操作：
  1. 手动解决上述文件中的冲突标记（<<<<<<< HEAD）
  2. 解决后暂存文件：git add <冲突文件>
  3. 继续rebase：git rebase --continue
  4. 如果还有冲突，重复步骤1-3
  5. 完成后推送：git push

  或者放弃rebase：git rebase --abort
  ```

**步骤3：监测用户操作**

如果需要手动解决冲突，skill会：
- 暂停自动流程
- 等待用户手动解决冲突
- 提示用户解决完成后可以说"继续推送"或"重新推送"来完成推送

## 提交信息示例

### 示例1：新增功能
**变更内容**：在销售单列表页面添加了按客户筛选的功能

**生成的提交信息**：
```
feat(bills): 添加销售单列表按客户筛选功能

- 新增客户选择器组件
- 实现按客户ID过滤销售单数据
- 添加清除筛选条件按钮
```

### 示例2：修复Bug
**变更内容**：修复了日期选择器在特定情况下崩溃的问题

**生成的提交信息**：
```
fix(ui): 修复日期选择器空值导致的崩溃问题

当用户未选择日期直接点击确认时，应用会因空指针异常而崩溃。
现在添加了空值检查和默认值处理。
```

### 示例3：代码重构
**变更内容**：重构了数据库查询相关代码，使用Sqlite3静态类替代直接实例化

**生成的提交信息**：
```
refactor(storage): 统一使用Sqlite3静态类进行数据库操作

- 移除直接实例化Sqlite的代码
- 所有数据库查询统一使用Sqlite3静态方法
- 提升代码一致性和可维护性
```

### 示例4：性能优化
**变更内容**：优化了商品列表的加载性能

**生成的提交信息**：
```
perf(goods): 优化商品列表加载性能

- 实现商品数据分页加载
- 添加列表项懒加载
- 减少初始加载时间约60%
```

## 快速模式

如果用户明确表示"快速提交"或"直接提交"：

1. 跳过代码审查步骤
2. **仍需运行验证（format + analyze）- 此步骤不可跳过**
3. **如果有任何问题，仍需修复后才能继续**
4. 生成提交信息
5. 直接执行提交（仍需用户最终确认）

**注意：快速模式只是跳过代码审查，验证步骤仍然强制执行！**

## 错误处理

### 情况1：暂存区为空
```
提示：暂存区没有变更。
建议：
1. 查看未暂存的文件：git status
2. 暂存文件：git add <files>
3. 或暂存所有变更：git add .
```

### 情况2：代码验证发现问题
```
⚠️ 发现以下问题，必须修复后才能继续：

格式问题：
- 5个文件格式不符合规范
- 正在自动修复：dart format .

静态分析问题：
- dart analyze: 1个错误, 2个警告, 3个提醒

必须修复的问题：
- [错误] lib/src/example.dart:42:5 - Undefined name 'foo'
- [警告] lib/src/example.dart:50:10 - Unused import
- [提醒] lib/src/example.dart:70:5 - Use 'const' with the constructor

请修复以上问题后，我会重新运行验证。
只有验证通过（No issues found!）才能继续提交流程。
```

### 情况3：未安装必要工具
```
⚠️ 检测到Flutter环境未配置
请确保已安装：
- Flutter SDK
- Dart SDK

或跳过验证步骤直接提交？
```

### 情况4：推送失败（远程有更新）
```
⚠️ 推送失败：远程分支有新的提交

正在自动执行 git pull --rebase...
```

**自动处理**：执行`git pull --rebase`

**如果自动rebase成功**：
- 显示"✅ 自动变基完成"
- 自动重新推送

**如果需要手动解决冲突**：
- 列出冲突文件
- 显示详细的解决步骤
- 等待用户解决后继续

### 情况5：Rebase过程中的冲突

检测rebase状态的方法：
```bash
git status
```

如果输出包含`rebase in progress`，说明正在rebase且有冲突。

**识别冲突文件**：
```bash
git diff --name-only --diff-filter=U
```

**提示用户解决冲突的完整流程**：
```
⚠️ 检测到rebase冲突

冲突文件列表：
[列出所有冲突文件]

解决步骤：
1. 打开冲突文件，查找冲突标记：
   <<<<<<< HEAD (当前变更)
   >>>>>>> commit-hash (远程变更)

2. 手动编辑文件，保留正确的代码，删除冲突标记

3. 解决完成后：
   git add <已解决的文件>
   git rebase --continue

4. 如果继续出现冲突，重复步骤1-3

5. 完成所有冲突解决后，执行推送：
   git push

取消rebase：git rebase --abort
```

## 配置选项

用户可以通过对话指定偏好：

- **是否启用代码审查**："跳过代码审查"或"需要审查"
- **是否运行测试**："运行测试"或"跳过测试"
- **提交信息语言**："使用中文"或"使用英文"
- **是否显示详细diff**："显示完整差异"或"仅显示摘要"
- **是否自动推送**："自动推送"（默认）或"只提交不推送"

## 完整流程总结

### 标准流程（自动推送模式）
1. 分析暂存区变更
2. 代码审查（可选）
3. **提交前验证（强制）- 必须零问题才能继续**
4. 生成并确认提交信息
5. 执行本地提交
6. **自动推送到远程**
7. **如果推送失败，自动rebase**
8. **如果rebase成功，自动重新推送**
9. **如果有冲突，提示手动解决**

### 仅提交模式
如果用户说"只提交不推送"或"不要push"：
- 执行步骤1-5（包括强制验证）
- 跳过步骤6-9
- 完成后提示："提交成功，未推送到远程"

## 注意事项

1. **强制验证**：提交前必须通过 `dart analyze` 验证，零问题才能提交
2. **禁止跳过**：不允许跳过验证步骤，即使快速模式也必须验证
3. **自动推送**：提交成功后默认自动推送到远程（可通过配置关闭）
4. **智能rebase**：推送失败时自动执行`git pull --rebase`解决冲突
5. **冲突提示**：如果rebase需要手动解决，会暂停并提供详细指导
6. **尊重用户选择**：生成的提交信息仅作为建议，用户可以修改
7. **保持简洁**：提交信息应简洁明了，避免冗长描述
8. **遵循项目规范**：优先遵循项目中已有的commit message约定

## 相关文档

- [Conventional Commits规范](https://www.conventionalcommits.org/zh-hans/)
- 项目代码规范：参见`.qoder/rules/`目录
