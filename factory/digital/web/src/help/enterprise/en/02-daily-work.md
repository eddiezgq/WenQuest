# Daily work for each role

> Planning, production, quality, cost: each role has a workbench; documents live in ERPNext and data on the unified data bus.

## Planner: orders and planning

```anim
name: mrp
```

Take the order → MRP → submit → confirm → release to the shop. MRP uses ERPNext stock, items on order and what other orders have reserved.

```goto
tour: planner-order
label: Help me take an order
```

```goto
tour: planner-release
label: Help me release a work order to the shop
```

## Operator: dispatch and start

```anim
name: workorder
```

After release the work order is dispatched operation by operation to machines along the routing; the operator clicks “Start” on the shop terminal for a dispatched operation, and “Reset” after a stop is handled.

```goto
tour: operator-start
label: Help me start on the shop terminal
```

## Inspector: inspection and 8D

Look at control charts and measurements; for nonconforming parts choose rework, scrap or concession; when you find a problem open a quality issue and work through D1–D8.

```goto
tour: quality-chart
label: Show me the control charts
```

## Plant manager: metrics and cost

```live
kind: kpi
```

“Production cost” in the left sidebar shows each machine's OEE today, deliveries this month and work order cost breakdowns; cost uses the workstations' hourly rates (from the plant manifest).

```goto
tour: cost-tour
label: Show me production cost
```

```ask
q: Which work order went furthest over cost this month, and why?
```
