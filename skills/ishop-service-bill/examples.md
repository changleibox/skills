# Service Bill Skill 使用示例

## 基本使用

### 示例 1：创建销售单据

用户请求：
```
创建一个销售退货单功能
```

AI 响应：
```
📋 正在为"销售退货单"生成代码...

单据类型：sales_return_bill
单据名称：销售退货单
分类：sales（销售类）

将生成以下文件：
1. Entry: lib/src/entries/sales_return_bill.dart
2. Model: lib/src/models/bills/lists/sales_return_bills_model.dart
3. Model: lib/src/models/bills/edits/sales_return_bill_model.dart
4. Presenter: lib/src/presenters/bills/lists/sales_return_bills_presenter.dart
5. Presenter: lib/src/presenters/bills/edits/sales_return_bill_presenter.dart
6. Page: lib/src/pages/bills/lists/sales_return_bills_page.dart
7. Page: lib/src/pages/bills/edits/sales_return_bill_page.dart
8. Cell: lib/src/pages/widgets/bills/lists/sales_return_bills_cell.dart

是否继续？
```

### 示例 2：创建采购订单

用户请求：
```
创建采购订单功能
```

AI 响应：
```
📋 正在为"采购订单"生成代码...

单据类型：purchase_order
单据名称：采购订单
分类：purchase（进货类）
是否为订单：是

注意：订单类型使用复数形式的页面命名：
- 列表页：PurchaseOrdersPage
- 编辑页：PurchaseOrderPage
```

## 完整代码示例

### 示例 1：销售订单 Entry 类

```dart
// packages/ancestry/lib/src/entries/sales_order.dart
import 'package:ancestry/ancestry.dart';

part 'sales_order.g.dart';

@JsonSerializable()
final class SalesOrder implements Bill {
  const SalesOrder({
    required this.billId,
    required this.billNumber,
    required this.serviceDate,
    this.customerId,
    this.customerName,
    this.totalAmount,
    this.remarks,
  });

  factory SalesOrder.fromJson(Map<String, dynamic> json) => 
      _$SalesOrderFromJson(json);

  Map<String, dynamic> toJson() => _$SalesOrderToJson(this);

  @JsonKey(name: 'billid')
  @override
  final int billId;

  @JsonKey(name: 'billno')
  @override
  final String billNumber;

  @JsonKey(name: 'billdate', fromJson: parseDate)
  @override
  final DateTime? serviceDate;

  @JsonKey(name: 'customerid')
  final int? customerId;

  @JsonKey(name: 'customername')
  final String? customerName;

  @JsonKey(name: 'totalamount', fromJson: parseDouble)
  final double? totalAmount;

  @JsonKey(name: 'remarks')
  final String? remarks;
}
```

### 示例 2：销售订单列表 Model

```dart
// packages/ancestry/lib/src/models/bills/lists/sales_orders_model.dart
import 'package:ancestry/ancestry.dart';

/// 销售订单列表Model
final class SalesOrdersModel extends BillsModel<SalesOrder> {
  SalesOrdersModel(super.filterArguments);

  @override
  BillType get billType => BillType.salesOrder;

  @override
  List<Sortable<EnumStorage>> get sorts => salesOrderSortFields;

  @override
  List<BillFilterField> get filters {
    return BillFilterField.append([
      BillFilterField.customer,
      BillFilterField.businessStore,
      BillFilterField.clerk,
      BillFilterField.storehouse,
    ]);
  }

  @override
  List<MarkableNamedValue> sectionTotalsItemsOf(BillGroup group) {
    final list = List.of(objects);
    return [
      ('日订单金额', Fn.amount.format(group.sub(list).map((e) => e.totalAmount).sum, symbols: true), false),
    ];
  }

  @override
  List<MarkableNamedValue>? get summaryTotalsItems {
    return [
      (billType.totalName, Fn.amount.format(parseDouble(summaryTotals['total']), symbols: true), true),
    ];
  }

  @override
  List<SalesOrder>? fromJson(List<Map<String, dynamic>> src) {
    return src.map(SalesOrder.fromJson).toList();
  }
}
```

### 示例 3：销售订单编辑 Model

```dart
// packages/ancestry/lib/src/models/bills/edits/sales_order_model.dart
import 'package:ancestry/ancestry.dart';

/// 销售订单编辑Model
final class SalesOrderModel extends EditSalesBillModel<SalesOrderDetail>
    with EditSalesBillModelMixin<SalesOrderDetail> {
  SalesOrderModel({
    int? billId,
    BillingMode mode = BillingMode.normal,
  }) : super(
         billId: billId,
         mode: mode,
       );

  @override
  BillType get billType => BillType.salesOrder;

  @override
  bool get isMergeSameGoods => billConfigs.isMergeSameGoods;

  @override
  Future<void> onSetup() async {
    await super.onSetup();
    // 订单特定初始化逻辑
  }

  @override
  Map<String, dynamic>? get postingParams => <String, dynamic>{
    ...?super.postingParams,
    // 订单特定参数
  };
}
```

### 示例 4：销售订单列表 Presenter

```dart
// packages/ancestry/lib/src/presenters/bills/lists/sales_orders_presenter.dart
import 'package:ancestry/ancestry.dart';

/// 销售订单列表Presenter
final class SalesOrdersPresenter extends BillsPresenter<SalesOrdersPage, SalesOrdersModel> {
  @override
  late final model = SalesOrdersModel(filters);

  /// 从订单生成销售单
  Future<void> onGenerateBill() async {
    final selectedOrders = model.selectedElements;
    if (selectedOrders.isEmpty) {
      showToast('请选择要生成单据的订单');
      return;
    }

    await navigator.push(
      R.salesBill.push(
        context,
        arguments: {
          'fromOrders': selectedOrders,
          'mode': BillingMode.fromOrder,
        },
      ),
    );
  }
}
```

### 示例 5：销售订单列表 Page

```dart
// packages/ancestry/lib/src/pages/bills/lists/sales_orders_page.dart
import 'package:ancestry/ancestry.dart';
import 'package:flutter/material.dart';

/// 销售订单列表页面
class SalesOrdersPage extends StatefulWidget with HostProvider {
  const SalesOrdersPage({super.key});

  @override
  _SalesOrdersPageState createState() => _SalesOrdersPageState();

  @override
  SalesOrdersPresenter createPresenter() => SalesOrdersPresenter();
}

class _SalesOrdersPageState extends HostState<SalesOrdersPage, SalesOrdersPresenter> {
  @override
  Widget build(BuildContext context) {
    return BillsMainstay<SalesOrdersModel>(
      model: presenter.model,
      title: const Text('销售订单'),
      placeholder: (() {
        final joined = [
          '单据编号',
          '客户名称',
          '商品',
          Settings.extendInfo1Name,
        ].join('、');
        return '请输入$joined';
      })(),
      onPrinting: presenter.onPrinting,
      onPosting: presenter.onPosting,
      onDownload: presenter.onDownload,
      onBatching: presenter.onBatching,
      actions: (model) {
        return [
          if (model.mode case EditingMode.normal)
            AppBarAction(
              onPressed: presenter.onGenerateBill,
              child: const Text('生成单据'),
            ),
          BillsEllipsis(
            mode: model.mode,
            onMode: (value) => model.mode = value,
            onReviewProcess: presenter.onReviewProcess,
            configuratorsOptions: model.configuratorsOptions,
            onSaveConfigurators: model.saveConfigurators,
            onResetConfigurators: model.resetConfigurators,
          ),
        ];
      },
      itemBuilder: (context, model, index) {
        return SalesOrdersCell(
          model: model,
          index: index,
        );
      },
      separatorBuilder: (context, index) {
        return const SizedBox(height: 9);
      },
    );
  }
}
```

### 示例 6：支持 AI 开单的 Model

```dart
/// 支持 AI 开单的销售单编辑Model
final class SalesBillModel extends EditSalesBillModel<SalesBillDetail>
    with EditFlexibleBillModelMixin<SalesBillDetail> {
  
  @override
  Future<void> onFlexibleResult(Map<String, dynamic> value) async {
    // 处理 AI 返回的数据
    final headerInfo = value['headerInfo'] as Map<String, dynamic>?;
    
    if (headerInfo?['billDate'] case final int billDate when billDate > 0) {
      serviceDate = parseDate(billDate ~/ 1000);
    }
    
    if (headerInfo?['customerId'] case final int customerId when customerId > 0) {
      await selectCustomer(customerId);
    }
    
    // 处理商品明细
    final items = value['items'] as List<dynamic>?;
    if (items != null) {
      await addGoodsFromAI(items);
    }
  }
}
```

## 命名规范对照表

| 单据类型 | 单据实体 | 列表Page | 编辑Page | 详情Page |
|---------|---------|----------|----------|----------|
| 销售单 | `SalesBill` | `SalesBillsPage` | `SalesBillPage` | `SalesBillDetailPage` |
| 销售订单 | `SalesOrder` | `SalesOrdersPage` | `SalesOrderPage` | `SalesOrderDetailPage` |
| 采购单 | `PurchaseBill` | `PurchaseBillsPage` | `PurchaseBillPage` | `PurchaseBillDetailPage` |
| 采购订单 | `PurchaseOrder` | `PurchaseOrdersPage` | `PurchaseOrderPage` | `PurchaseOrderDetailPage` |
| 销售退货单 | `SalesReturnBill` | `SalesReturnBillsPage` | `SalesReturnBillPage` | `SalesReturnBillDetailPage` |
| 调拨单 | `TransBill` | `TransBillsPage` | `TransBillPage` | `TransBillDetailPage` |

## 销售类 vs 进货类差异

| 特性 | 销售类 | 进货类 |
|------|--------|--------|
| 基类 | `EditSalesBillModel` | `EditPurchasesBillModel` |
| 往来单位 | `customer` (客户) | `supplier` (供应商) |
| 金额方向 | 应收 | 应付 |
| 特有功能 | 积分、物流信息 | - |
| Mixin | `EditSalesBillModelMixin` | `EditPurchasesBillModelMixin` |
| 筛选字段 | `BillFilterField.customer` | `BillFilterField.supplier` |
