---
id: kernel
title: 内核：开源软件与参考书
lead: 数值、几何和网页交给成熟的开源软件；公式和判据出自公开的教材和专著，每个模块带标准题。
---
### 用到的开源软件

| 开源软件 | 做什么 | 在问渠凸轮里用在哪 | 许可证 |
|---|---|---|---|
| **NumPy**、**SciPy** | 数值计算 | 全部计算核心：运动程序、廓线、样条、最小基圆、谐波分析 | BSD-3 |
| **Shapely** | 平面几何 | 加工仿真（刀具扫过毛坯） | BSD-3 |
| **manifold3d** | 网格布尔运算 | 圆柱凸轮、弧面凸轮按加工方法生成的 STL | Apache-2.0 |
| **FreeCAD** 1.1、**OpenCASCADE** | 参数化 CAD、几何内核 | “问渠 → 凸轮”工作台；精确实体与工作图 | LGPL-2.0+、LGPL-2.1（带例外） |
| **three.js** | 网页三维 | 凸轮系统三维、圆柱凸轮三维 | MIT |
| **FastAPI**、**Uvicorn**、**Vue** | 接口与网页 | 凸轮计算服务、网页版 | MIT、BSD-3、MIT |
| **Gmsh**、**CalculiX**、**pyLife**、**MuJoCo** | 网格、有限元、疲劳、多体动力学 | 凸轮系统的 CAE（在数字工厂计算服务上跑） | GPL-2.0+、GPL-2.0、Apache-2.0、Apache-2.0 |

### 参考书

R. L. Norton, *Cam Design and Manufacturing Handbook*（运动规律、压力角、曲率、动力学与残余振动）；H. A. Rothbart, *Cam Design Handbook*（滚子齿轮凸轮 / 弧面凸轮）；J. Angeles, C. López-Cajún, *Optimization of Cam Mechanisms*（最小基圆）；孙桓《机械原理》（廓线曲率）。另外和开源的 `mechanism` 包做过交叉对照。

### 我们自己做的

计算核心 `services/cam/camkit/`（纯 Python）：运动程序、盘形与圆柱与弧面凸轮、制造程序与读回仿真、测量与补偿、凸轮系统与设计搜索、STEP 写出；标准题与闭式解对照（`services/cam/tests/`）。判定全由程序做，不经 AI；没填的数据结果为“未知”。
