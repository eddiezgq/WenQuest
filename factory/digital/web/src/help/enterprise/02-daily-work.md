# 各岗位的日常

> 计划、生产、质量、成本：每个岗位一个工作台，单据都在 ERPNext 里，数据都在统一数据总线上。

## 计划员：接单与计划

```anim
name: mrp
```

接单 → 算料 → 提交 → 确认 → 下达车间。算料用 ERPNext 的库存、在途和其他订单的占用。

```goto
tour: planner-order
label: 带我接一张订单
```

```goto
tour: planner-release
label: 带我把工单下达车间
```

## 操作工：派工与开工

```anim
name: workorder
```

工单下达后按工艺路线逐道派给设备，操作工在车间终端对派来的工序点“开工”，停机处理完点“复位”。

```goto
tour: operator-start
label: 带我在车间终端开工
```

## 质检员：检验与 8D

看控制图和测量值；对不合格品选返修、报废或让步接收；发现异常开质量异常单，按 D1–D8 处理。

```goto
tour: quality-chart
label: 带我看控制图
```

## 厂长：指标与成本

```live
kind: kpi
```

左栏“生产成本”里看各设备今日的设备综合效率（OEE）、本月交付、工单成本分解；成本按工作站的每小时费率（工厂清单里填的）算。

```goto
tour: cost-tour
label: 带我看生产成本
```

```ask
q: 这个月哪张工单的成本超得最多，为什么？
```
