# WBS 拆分工具使用示例

## 示例 1：蓝湖需求导出

### 场景
从蓝湖原型图提取需求模块和任务，生成 WBS Excel 文件。

### 操作步骤

```bash
# 步骤 1：运行工具获取指引
/run ishop-wbs-split --url "https://lanhuapp.com/web/#/item/project/product?tid=xxx&pid=yyy&docId=zzz"

# 步骤 2：按照提示让 AI 获取数据
# AI 会调用 lanhu_get_ai_analyze_page_result 工具获取蓝湖表格数据

# 步骤 3：使用数据文件完成拆分（默认只生成APP端）
/run ishop-wbs-split \
  --url "https://lanhuapp.com/web/#/item/project/product?tid=xxx&pid=yyy&docId=zzz" \
  --data-file lanhu_table_data.json \
  --output "需求_WBS.xlsx"
```

### 输出示例

```
==============================================================
📋 WBS拆分结果摘要
==============================================================

📌 审核中心
  📂 审核中心主页
    ✓ TabBar框架搭建
    ✓ 单据列表数据加载
    ✓ 搜索框实现
    └─ 3 个任务
  📂 单据列表
    ✓ 列表组件开发
    ✓ 筛选功能
    └─ 2 个任务
    └─ 共 5 个任务

==============================================================
📊 总计: 5 个任务
==============================================================

✅ 完成！输出文件: /path/to/需求_WBS.xlsx
```

## 示例 2：按模块筛选

### 场景
只导出特定模块的需求任务。

### 操作步骤

```bash
/run ishop-wbs-split \
  --url "https://lanhuapp.com/..." \
  --data-file lanhu_data.json \
  --keep-modules "审核中心,批量审核" \
  --output "筛选后_WBS.xlsx"
```

## 示例 3：带需求名称映射

### 场景
自动填充需求名称列。

### 操作步骤

```bash
/run ishop-wbs-split \
  --url "https://lanhuapp.com/..." \
  --data-file lanhu_data.json \
  --demand-map "审核中心主页:审核中心,批量审核模块:批量审核" \
  --output "带需求名称_WBS.xlsx"
```

## 示例 4：生成 PC 端需求

### 场景
只生成 PC 端（后台管理）的需求任务。

### 操作步骤

```bash
/run ishop-wbs-split \
  --url "https://lanhuapp.com/..." \
  --data-file lanhu_data.json \
  --target-platform pc \
  --output "PC端_WBS.xlsx"
```

## 示例 5：细粒度任务拆分

### 场景
控制任务粒度在 2 小时以内，确保任务更细粒度。

### 操作步骤

```bash
/run ishop-wbs-split \
  --url "https://lanhuapp.com/..." \
  --data-file lanhu_data.json \
  --max-task-hours 2 \
  --output "细粒度_WBS.xlsx"
```

### 粒度验证警告

如果任务超过设定的最大工时，工具会输出警告：

```
⚠️ 任务粒度验证警告
以下任务超过 2 小时，建议拆分：

  - "列表组件开发" (3h) → 建议拆分为：
    1. 列表基础组件 (1.5h)
    2. 列表交互逻辑 (1.5h)
```

## 示例 6：Jira 任务表格

### 场景
从 Jira 任务页面提取任务列表。

### 操作步骤

```bash
# 步骤 1：运行工具
/run ishop-wbs-split --url "https://your-company.atlassian.net/browse/PROJECT-123"

# 步骤 2：让 AI 读取数据
"请使用 fetch_content 工具读取这个网页的表格数据"

# 步骤 3：使用数据文件
/run ishop-wbs-split \
  --data-file jira_data.json \
  --output "Jira_Tasks.xlsx"
```

## JSON 数据文件格式

### 标准格式

```json
{
  "headers": ["需求名称", "模块", "任务", "时间", "剩余时间"],
  "data": [
    {
      "需求名称": "",
      "模块": "审核中心主页",
      "任务": "TabBar框架搭建",
      "时间": "2",
      "剩余时间": "2"
    },
    {
      "需求名称": "",
      "模块": "审核中心主页",
      "任务": "列表数据加载",
      "时间": "3",
      "剩余时间": "3"
    }
  ]
}
```

### 重要约定

1. **模块名称**：使用原始文档中的名称，不添加编号前缀
2. **任务名称**：使用原始文档中的名称，不添加编号前缀
3. **时间字段**：只填写纯数字（单位：小时），如 `"2"`、`"3"`、`"1.5"`
4. **需求名称**：可为空，后续通过 `--demand-map` 参数填充

## 常见问题

### Q: AI 无法访问蓝湖页面？

**解决方案**：
1. 确保蓝湖 URL 完整且可访问
2. 检查是否需要登录权限
3. 尝试手动导出蓝湖表格为 Excel，再让 AI 读取

### Q: 任务粒度验证失败？

**解决方案**：
- 使用 `--max-task-hours` 调整粒度阈值
- 手动拆分超限任务后重新运行
- 或忽略警告直接使用生成的 Excel

### Q: 输出的 Excel 格式不符合预期？

**解决方案**：
- 检查 JSON 数据文件格式是否正确
- 确保 `--demand-map` 参数格式正确：`模块1:需求1,模块2:需求2`
- 检查 `--keep-modules` 和 `--exclude-modules` 参数是否冲突
