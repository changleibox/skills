# Git Commit Skill 使用示例

## 基本使用

### 示例 1：标准提交流程

用户将修改后的代码暂存后，执行：

```bash
git add .
/run commit
```

**AI 响应流程**：

```
📋 分析暂存区变更...

已暂存的文件：
- lib/src/pages/bills/sales_bills_page.dart
- lib/src/models/bills/sales_bills_model.dart

变更摘要：
- 添加了按客户筛选销售单的功能
- 新增客户选择器组件

🔍 运行提交前验证...

$ dart format --set-exit-if-changed .
✓ 格式检查通过

$ dart analyze
✓ No issues found!

📝 生成提交信息：

feat(bills): 添加销售单列表按客户筛选功能

- 新增客户选择器组件
- 实现按客户ID过滤销售单数据
- 添加清除筛选条件按钮

是否使用此提交信息？
[确认] [修改]
```

### 示例 2：快速提交模式

```bash
/run commit --quick
```

AI 将跳过代码审查步骤，但仍会执行强制验证。

### 示例 3：仅提交不推送

```bash
/run commit --no-push
```

提交成功后不会自动推送到远程仓库。

## 实际场景示例

### 场景 1：修复 Bug

**变更内容**：
```dart
// 修复前
if (date == null) {
  return formatDate(date);  // 空指针异常
}

// 修复后
if (date == null) {
  return '';
}
return formatDate(date);
```

**生成的提交信息**：
```
fix(ui): 修复日期选择器空值导致的崩溃问题

当用户未选择日期直接点击确认时，应用会因空指针异常而崩溃。
现在添加了空值检查和默认值处理。
```

### 场景 2：代码重构

**变更内容**：
- 重构了数据库查询相关代码
- 使用 Sqlite3 静态类替代直接实例化
- 移除了重复的连接管理代码

**生成的提交信息**：
```
refactor(storage): 统一使用Sqlite3静态类进行数据库操作

- 移除直接实例化Sqlite的代码
- 所有数据库查询统一使用Sqlite3静态方法
- 提升代码一致性和可维护性
```

### 场景 3：性能优化

**变更内容**：
- 商品列表实现分页加载
- 添加列表项懒加载
- 减少初始加载时间

**生成的提交信息**：
```
perf(goods): 优化商品列表加载性能

- 实现商品数据分页加载
- 添加列表项懒加载
- 减少初始加载时间约60%
```

### 场景 4：新增功能

**变更内容**：
- 新增批量审核功能入口
- 实现批量审核弹窗组件
- 添加批量操作逻辑

**生成的提交信息**：
```
feat(review): 新增批量审核功能

- 添加批量审核按钮入口
- 实现批量审核弹窗组件
- 支持批量选择和审核操作
```

## 验证失败处理

### 示例：格式问题

```
$ dart format --set-exit-if-changed .
5个文件格式不符合规范

正在自动修复：dart format .
✓ 格式问题已修复

$ dart analyze
1个错误, 2个警告, 3个提醒

⚠️ 发现以下问题，必须修复后才能提交：

错误 (error): 1个
  - lib/src/example.dart:42:5 - Undefined name 'foo'

警告 (warning): 2个
  - lib/src/example.dart:50:10 - Unused import
  - lib/src/example.dart:60:3 - Missing return type

提醒 (info): 3个
  - lib/src/example.dart:70:5 - Use 'const' with the constructor

请修复以上问题后重新运行验证。
```

## 推送失败处理

### 示例：远程有新提交

```
$ git push
! [rejected] main -> main (fetch first)

⚠️ 推送失败：远程分支有新的提交

正在自动执行 git pull --rebase...
✅ Rebase成功！自动变基已完成。

重新推送到远程...
$ git push
✓ 推送成功！
```

### 示例：Rebase 冲突

```
$ git pull --rebase
CONFLICT (content): Merge conflict in lib/src/example.dart

⚠️ Rebase遇到冲突，需要手动解决

冲突文件：
- lib/src/example.dart

解决步骤：
1. 打开冲突文件，查找冲突标记：
   <<<<<<< HEAD (当前变更)
   >>>>>>> commit-hash (远程变更)

2. 手动编辑文件，保留正确的代码

3. 解决完成后：
   git add lib/src/example.dart
   git rebase --continue

4. 完成后推送：
   git push

或取消rebase：git rebase --abort
```

## 配置偏好示例

### 设置语言偏好

```
用户：以后用英文写提交信息
AI：好的，后续提交信息将使用英文。

用户：改回中文
AI：好的，提交信息将使用中文。
```

### 设置推送偏好

```
用户：不要自动推送
AI：好的，提交后不会自动推送到远程。

用户：恢复自动推送
AI：好的，提交后会自动推送到远程。
```

## 最佳实践

1. **小步提交**：每次只提交相关的修改，避免一次提交过多内容
2. **先验证后提交**：确保 `dart analyze` 无问题
3. **写清楚意图**：如果 AI 生成的提交信息不准确，主动修改
4. **及时推送**：提交后尽快推送，减少冲突概率
