---
id: arch
title: 系统设计
lead: 运动程序 → 计算核心 → 校核 → 制造程序 → 测量 → 补偿，绕成一个闭环；凸轮系统再接 CAE。
---
::anim{id=arch}

| 层 | 是什么 | 在哪 |
|---|---|---|
| 计算核心 | 纯 Python，不联网、不调 AI；网页版服务和 FreeCAD 工作台共用 | `services/cam/camkit/` |
| 计算服务 | 网页版的接口：校核、最小基圆、制造、测量、补偿、系统、导出 | `services/cam/app.py`，网址 `/cam/api/` |
| 网页版 | 单个凸轮三页、凸轮系统三页 | `apps/cam/` |
| FreeCAD 工作台 | 精确实体、装配、工作图、程序 | `services/cam/freecad/` |
| 云端、AI、CAE | 账号、企业授权、云端项目、AI 起草（经问渠网关）；CAE 在数字工厂计算服务排队 | `services/gateway/`、数字工厂 |

规矩：判定只由程序做；许用值、机床参数、电机额定值由企业填，不编；示例一律标“虚构”。
