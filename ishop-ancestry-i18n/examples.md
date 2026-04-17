# Ancestry国际化Skill使用示例

## 基本使用

### 1. 处理单个文件
```bash
/run ancestry-i18n --path lib/src/pages/account/new_account.dart
```

### 2. 递归处理整个目录
```bash
/run ancestry-i18n --path lib/src/pages/ --recursive
```

### 3. 预览模式（不实际修改文件）
```bash
/run ancestry-i18n --path lib/src/pages/main/main_page.dart --dry-run
```

### 4. 指定批处理大小
```bash
/run ancestry-i18n --path lib/src/pages/ --batch-size 3
```

## 实际处理示例

### 输入文件示例
```dart
// lib/src/pages/account/new_account.dart
class LoginPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('登录'),
      ),
      body: Column(
        children: [
          TextField(
            decoration: InputDecoration(
              labelText: '请输入用户名',
              hintText: '用户名',
            ),
          ),
          TextField(
            decoration: InputDecoration(
              labelText: '请输入密码',
              hintText: '密码',
            ),
          ),
          ElevatedButton(
            onPressed: () {
              // 登录逻辑
            },
            child: Text('登录'),
          ),
          Text('还没有账户？'),
          TextButton(
            onPressed: () {
              // 跳转到注册页面
            },
            child: Text('立即注册'),
          ),
        ],
      ),
    );
  }
}
```

### 处理后的输出
```dart
// lib/src/pages/account/new_account.dart
class LoginPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(S.strings.login),
      ),
      body: Column(
        children: [
          TextField(
            decoration: InputDecoration(
              labelText: S.strings.pleaseEnterUsername,
              hintText: S.strings.username,
            ),
          ),
          TextField(
            decoration: InputDecoration(
              labelText: S.strings.pleaseEnterPassword,
              hintText: S.strings.password,
            ),
          ),
          ElevatedButton(
            onPressed: () {
              // 登录逻辑
            },
            child: Text(S.strings.login),
          ),
          Text(S.strings.noAccountYet),
          TextButton(
            onPressed: () {
              // 跳转到注册页面
            },
            child: Text(S.strings.registerNow),
          ),
        ],
      ),
    );
  }
}
```

### 更新的ARB文件
```json
// app_zh.arb - 中文资源文件
{
  "@@locale": "zh",
  "appName": "管家婆手机版",
  "login": "登录",
  "pleaseEnterUsername": "请输入用户名",
  "username": "用户名",
  "pleaseEnterPassword": "请输入密码",
  "password": "密码",
  "noAccountYet": "还没有账户？",
  "registerNow": "立即注册"
}

// app_en.arb - 英文资源文件（自动生成翻译）
{
  "@@locale": "en",
  "appName": "管家婆手机版",
  "login": "Login",
  "pleaseEnterUsername": "Please enter username",
  "username": "Username",
  "pleaseEnterPassword": "Please enter password",
  "password": "Password",
  "noAccountYet": "No account yet?",
  "registerNow": "Register now"
}
```

## 高级使用场景

### 1. 处理带参数的字符串
```dart
// 输入
Text('共找到 ${resultCount} 条记录')

// 输出
Text(S.strings.foundRecords(resultCount))
```

### 2. 处理TextSpan
```dart
// 输入
Text.rich(
  TextSpan(
    children: [
      TextSpan(text: '欢迎'),
      TextSpan(text: userName, style: boldStyle),
      TextSpan(text: '使用系统'),
    ],
  ),
)

// 输出
Text.rich(
  TextSpan(
    children: [
      TextSpan(text: S.strings.welcome),
      TextSpan(text: userName, style: boldStyle),
      TextSpan(text: S.strings.useSystem),
    ],
  ),
)
```

### 3. 处理复杂上下文
```dart
// 根据文件路径和组件名称生成更准确的键名
// 文件: lib/src/pages/bills/sales_bills_page.dart
// 组件: SalesBillsPage
Text('新增销售单据')  // → S.strings.billNewSalesBill
```

## 进度管理和恢复

### 查看处理进度
```bash
/run ancestry-i18n --status
```

### 从中断点继续
```bash
/run ancestry-i18n --continue
```

### 重置进度
```bash
/run ancestry-i18n --reset-progress
```

## 质量检查

### 处理后验证
```bash
/run ancestry-i18n --validate
```

### 生成处理报告
```bash
/run ancestry-i18n --report
```

## 故障排除

### 常见问题及解决方案

1. **键名冲突**
   ```bash
   # 系统会自动提示并建议解决方案
   # 或者手动指定键名
   /run ancestry-i18n --resolve-conflict old_key=new_key
   ```

2. **编译错误**
   ```bash
   # 自动回滚到处理前状态
   /run ancestry-i18n --rollback
   ```

3. **ARB文件格式错误**
   ```bash
   # 验证并修复ARB文件
   /run ancestry-i18n --fix-arb
   ```

## 最佳实践工作流

### 推荐的工作流程
1. **准备工作**
   ```bash
   git add .  # 提交当前更改
   git commit -m "Before i18n processing"
   ```

2. **预览处理**
   ```bash
   /run ancestry-i18n --path lib/src/pages/target_page.dart --dry-run
   ```

3. **小批量处理**
   ```bash
   /run ancestry-i18n --path lib/src/pages/target_page.dart --batch-size 3
   ```

4. **质量验证**
   ```bash
   flutter analyze
   flutter test
   ```

5. **提交更改**
   ```bash
   git add .
   git commit -m "i18n: Process target_page.dart"
   ```

### 团队协作建议
- 每人负责不同的文件/目录
- 定期同步ARB文件变更
- 建立键名命名规范
- 维护翻译记忆库