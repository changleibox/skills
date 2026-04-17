---
name: ancestry-i18n
description: 自动化处理ancestry项目国际化任务，将中文字符串替换为S.strings调用并更新ARB文件。用于packages/ancestry/lib/src/pages目录下的文件国际化处理。
---

# Ancestry项目国际化处理Skill

## 概述
专门用于ancestry项目的国际化自动化处理工具，按照进度表批量处理文件中的中文字符串，替换为S.strings国际化调用。

## 项目配置
- **项目根目录**: `/Volumes/Samsung/AndroidStudioWorkspace/ishops/packages/ancestry`
- **源代码目录**: `lib/src/pages/`
- **ARB文件目录**: `lib/src/l10n/`
- **Strings访问**: `S.strings` (来自packages/ancestry/lib/ancestry.dart)

## 核心功能

### 1. 中文字符串识别与替换
- 自动识别Dart文件中的中文字符串字面量
- 将硬编码中文替换为 `S.strings.键名` 调用
- 支持字符串插值和占位符处理

### 2. ARB文件管理
- 自动生成唯一的国际化键名
- **同步更新中文和英文ARB文件**
- **智能中英文翻译映射**
- 自动去重检查避免重复键名

### 3. 批量处理控制
- 每次处理最多5个国际化字段
- 支持按文件处理或按目录递归处理
- 提供进度跟踪和中断恢复功能

## 使用方法

### 基本命令
```
/run ancestry-i18n --path lib/src/pages/specific_file.dart
/run ancestry-i18n --path lib/src/pages/ --recursive
```

### 参数说明
- `--path`: 指定要处理的文件或目录路径
- `--batch-size`: 批处理大小，默认5个字段
- `--dry-run`: 预览模式，显示将要进行的更改但不执行
- `--continue`: 从中断点继续执行
- `--force`: 强制处理，忽略已存在的键名冲突

## 处理规范

### 代码替换规则
1. **基本替换**: `'中文文本'` → `S.strings.chineseText`
2. **字符串插值**: `'你好 ${name}'` → `S.strings.hello(name: name)`
3. **TextSpan处理**: 保持原有结构，仅替换中文部分
4. **保留非中文**: 英文、数字、符号等内容保持不变

### 键名生成规则
1. 使用英文翻译作为基础
2. 采用camelCase命名规范
3. 添加上下文前缀避免冲突
4. 最大长度限制为50个字符

### ARB文件更新
1. 同时更新 `app_zh.arb` 和 `app_en.arb`
2. 中文值使用原始中文文本
3. 英文值使用智能翻译服务自动生成
4. **保持中英文文件字段顺序完全一致**
5. **新增字段总是添加在文件末尾**
6. **元数据字段(`@@`前缀)优先排列**
7. **保持JSON格式正确性和可读性**

## 工作流程

### 完整处理流程
```
1. 扫描指定文件/目录
2. 识别所有中文字符串
3. 按批次分组处理（每批5个）
4. 生成唯一键名
5. 替换代码中的中文字符串
6. 更新ARB文件
7. 验证更改无错误
8. 记录处理进度
```

### 质量检查清单
- [ ] 代码编译无错误
- [ ] 无新的分析警告
- [ ] ARB文件格式正确
- [ ] 国际化键名无冲突
- [ ] 功能逻辑保持不变

## 高级特性

### 上下文感知
- 根据文件路径和组件名称生成更准确的键名
- 考虑业务领域添加适当的前缀

### 智能合并
- 识别相似的字符串进行合并
- 避免创建冗余的国际化条目

### 冲突解决
- 检测现有键名冲突
- 提供手动解决选项
- 支持键名重命名建议

## 故障排除

### 常见问题
1. **键名冲突**: 系统会提示并建议解决方案
2. **编译错误**: 自动回滚更改并报告具体问题
3. **ARB格式错误**: 验证JSON格式并提供修复建议

### 恢复机制
- 保存处理前的文件快照
- 支持单文件或批量回滚
- 提供详细的变更日志

## 最佳实践

### 使用建议
1. 建议先在单个文件上测试
2. 定期提交git以方便回滚
3. 处理前备份重要文件
4. 小批量处理便于质量控制

### 注意事项
- 避免处理正在开发中的文件
- 确保有足够的测试覆盖
- 处理后进行充分的功能测试
- 关注性能影响（大量字符串替换）

## 示例

### 输入代码
```dart
Text('欢迎使用系统')
Text('用户名不能为空')
Text('共找到 ${count} 条记录')
```

### 输出代码
```dart
Text(S.strings.welcomeToSystem)
Text(S.strings.usernameCannotBeEmpty)
Text(S.strings.foundRecords(count))
```

### ARB文件更新
```json
// app_zh.arb
{
  "welcomeToSystem": "欢迎使用系统",
  "usernameCannotBeEmpty": "用户名不能为空", 
  "foundRecords": "共找到 {count} 条记录"
}

// app_en.arb  
{
  "welcomeToSystem": "Welcome to system",
  "usernameCannotBeEmpty": "Username cannot be empty",
  "foundRecords": "Found {count} records"
}
```