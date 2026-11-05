---
id: kernel
title: 内核：开源软件与参考专著
lead: 数值计算、三维和网页交给成熟的开源软件；算法和判据出自公开的专著，每个模块带标准题对照。
---
### 用到的开源软件

| 开源软件 | 做什么 | 在问渠轴承里用在哪 | 许可证 |
|---|---|---|---|
| **NumPy** | 数组与线性代数 | 全部计算核心 | BSD-3 |
| **SciPy** | 优化、求根、指派与整数规划 | 载荷分布求解、合套选配（匈牙利算法、整数规划） | BSD-3 |
| **FreeCAD** 1.1 | 开源参数化 CAD | “问渠 → 轴承”工作台的宿主，建精确实体、出图 | LGPL-2.0+ |
| **OpenCASCADE**（OCCT） | 三维几何内核 | FreeCAD 建模；验收时读回我们写出的 STEP 检查实体 | LGPL-2.1（带例外） |
| **openpyxl** | Excel 文件 | 产品库表格导入、空表格 | MIT |
| **FastAPI**、**Uvicorn** | 网页接口 | 轴承计算服务 | MIT、BSD-3 |
| **Vue**、**Vite** | 网页界面 | 网页版 | MIT |

STEP 文件由我们自己的程序直接写出（解析几何：回转面、球面），不依赖 CAD 内核，所以网页版不装 CAD 也能下载三维。

### 参考专著

| 书 | 用在哪 |
|---|---|
| T. A. Harris, M. N. Kotzalas, *Rolling Bearing Analysis*, 5th ed., CRC Press, 2006 | 几何、载荷分布、运动学、高速拟静力学、游隙 |
| K. L. Johnson, *Contact Mechanics*, Cambridge University Press, 1985 | 赫兹接触 |
| B. J. Hamrock, D. Dowson, *Ball Bearing Lubrication*, Wiley, 1981 | 点接触油膜 |
| D. Dowson, G. R. Higginson, *Elasto-hydrodynamic Lubrication* | 线接触油膜 |
| A. Palmgren, *Ball and Roller Bearing Engineering* | 线接触变形（经 Harris & Kotzalas 引用） |
| L. S. Nelson, *Journal of Quality Technology*, 1984 | 控制图判异规则 |

### 我们自己做的

- 每类轴承的计算核心（`services/bearing/bearingkit/`，纯 Python）：载荷分布、成对与预紧、温度对游隙、柔性轴承、交叉滚子、薄壁轴承的钢球自由体模型、合套选配、尺寸链、SPC、工艺倒推、零件剖面与 STEP 写出。
- **标准题**：每个模块和闭式解、专著公式或另一个独立模型对照，几百项测试每次改动都跑（`services/bearing/tests/`）。
- 判定全由确定性程序做，不经 AI；没填的数据结果为“未知”，不算合格。
