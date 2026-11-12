"""第 138 轮 G5.1 第 7 步、G5.2：机壳的数控程序（数字工厂 cae/cam.py、cam_post.py、cam_sim.py）。

G5.2：上件 O1201、O1202、O1205，下件 O1301、O1302、O1303、O1305，合件 O1401（锥销、测针杆轴线、全部孔系精加工、钻攻）。
镗杆伸进机壳里面的工步（同轴镗杆、阶梯镗杆，kind = linebar）不做高度图仿真，它们能不能进去由 cad/access_check.py 在三维里查。

    python3 tools/wqls/g5_cam.py <毛坯与零件网格目录> <输出目录>

按工艺规程（g5_process.py）的工序、工步编程：卧加 HMC-01（转台 B 分度）、立加 VMC-01，后处理成 FANUC 风格 G 代码。
然后每个程序用数字工厂的读程序器独立读一遍（机床行程、转速、B 范围），算加工时间，并按“面”做切削仿真：
从主轴方向看，毛坯（铸件）的高度图是起始材料，零件（成品）的高度图是目标，查快移撞工件、过切（切到成品面以下）和精加工面的残留。

每个装夹面的工件坐标系（右手，Z 指向主轴）：Z = n·p − Z0，X、Y 在面内。卧加托盘上工件立放（接合面 C 朝下），转台 B 绕竖直轴：
  B 0°：机头端面朝主轴（n = −x）；B 180°：电机端（n = +x）；B 270°：正面（n = −y）；
  直角铣头：从机头下方朝上（n = −z）、从上面朝下（n = +z）。立加：工件倒放时 n = −z，正放时 n = +z。
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "factory" / "digital"), str(HERE)]
from cae import cam, cam_post, cam_sim  # noqa: E402
from cae import casting as CST  # noqa: E402

ZU = 200.0
FRAMES = {   # 名称: (n, X 方向, Y 方向, 原点 p0（整机坐标，成品面上）)
    "B0": ((-1, 0, 0), (0, -1, 0), (0, 0, 1), (-62.0, 0.0, ZU)),
    "B180": ((1, 0, 0), (0, 1, 0), (0, 0, 1), (408.0, 0.0, ZU)),
    "B270": ((0, -1, 0), (1, 0, 0), (0, 0, 1), (0.0, -48.0, ZU)),
    "UP": ((0, 0, 1), (1, 0, 0), (0, 1, 0), (0.0, 0.0, 0.0)),
    "DOWN_HEAD": ((0, 0, -1), (1, 0, 0), (0, -1, 0), (0.0, 0.0, 45.0)),
    "C_UP": ((0, 0, -1), (1, 0, 0), (0, -1, 0), (348.0, 27.0, 0.0)),      # 上件倒放在立加上，接合面 C 朝上
    "A_UP": ((0, 0, -1), (1, 0, 0), (0, -1, 0), (153.0, 34.0, -62.0)),    # 下件倒放，底面 A 朝上
    "TOP": ((0, 0, 1), (1, 0, 0), (0, 1, 0), (153.0, 34.0, 0.0)),         # 下件正放，顶面朝上
    "TOPARM": ((0, 0, 1), (1, 0, 0), (0, 1, 0), (185.0, 12.0, 259.0)),    # G5.2 合件：直角铣头从上面钻攻顶盖螺孔（机臂顶面 z 259）
    "UNDER": ((0, 0, -1), (1, 0, 0), (0, -1, 0), (348.0, 36.5, -16.0)),   # G5.2 合件：直角铣头在机座底下向上（销孔凸台下端 z −16）
    "LB0": ((-1, 0, 0), (0, -1, 0), (0, 0, 1), (-105.0, 0.0, 0.0)),       # G5.2 下件 / 合件：机座左端壁外面（x −105），B 0°
}
WCS = {"B0": "G54", "B180": "G55", "B270": "G56", "UP": "G57", "DOWN_HEAD": "G58", "C_UP": "G54", "A_UP": "G54", "TOP": "G54",
       "TOPARM": "G57", "UNDER": "G58", "LB0": "G59"}
BVAL = {"B0": 0, "B180": 180, "B270": 270, "UP": 0, "DOWN_HEAD": 0, "TOPARM": 0, "UNDER": 0, "LB0": 0}
PINS = ((315.8, 7.0), (380.2, 66.0))          # 工艺孔 / 锥销孔（G5.2 第二个由 y 47 移到 66）
YL, ZL, ZH = 27.791774943072237, -35.36485983577417, -21.5
FEED = json.loads((Path(__file__).resolve().parents[2] / "docs" / "设计" / "WQ-LS" / "G4" / "送布机构.json").read_text(encoding="utf-8"))["geo"]   # G4.6


def to_frame(frame, p):
    n, ex, ey, p0 = (np.asarray(v, float) for v in FRAMES[frame])
    d = np.asarray(p, float) - p0
    return float(d @ ex), float(d @ ey), float(d @ n)


def heightmap(tris, frame, xs, ys):
    """三角网格从主轴方向看的高度图（Z 最大值），没有材料处为 NaN"""
    n, ex, ey, p0 = (np.asarray(v, float) for v in FRAMES[frame])
    P = tris - p0
    U, V, W = P @ ex, P @ ey, P @ n
    H = np.full((len(xs), len(ys)), np.nan)
    h = xs[1] - xs[0]
    for u, v, w in zip(U, V, W):
        i0, i1 = np.searchsorted(xs, u.min()), np.searchsorted(xs, u.max())
        j0, j1 = np.searchsorted(ys, v.min()), np.searchsorted(ys, v.max())
        if i1 <= i0 or j1 <= j0:
            continue
        X, Y = np.meshgrid(xs[i0:i1], ys[j0:j1], indexing="ij")
        den = (v[1] - v[2]) * (u[0] - u[2]) + (u[2] - u[1]) * (v[0] - v[2])
        if abs(den) < 1e-12:
            continue
        l0 = ((v[1] - v[2]) * (X - u[2]) + (u[2] - u[1]) * (Y - v[2])) / den
        l1 = ((v[2] - v[0]) * (X - u[2]) + (u[0] - u[2]) * (Y - v[2])) / den
        l2 = 1 - l0 - l1
        e = -1e-9
        inside = (l0 >= e) & (l1 >= e) & (l2 >= e)
        if not inside.any():
            continue
        z = l0 * w[0] + l1 * w[1] + l2 * w[2]
        sub = H[i0:i1, j0:j1]
        sub[inside] = np.fmax(sub[inside], z[inside])
    del h
    return H


def circle(cx, cy, r, z, f, n=72):
    pts = [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]
    mv = [{"t": "rapid", "x": pts[0][0], "y": pts[0][1], "z": 5.0}, {"t": "rapid", "x": pts[0][0], "y": pts[0][1], "z": 2.0},
          {"t": "feed", "x": pts[0][0], "y": pts[0][1], "z": z, "f": f / 2}]
    mv += [{"t": "feed", "x": x, "y": y, "z": z, "f": f} for x, y in pts[1:]]
    mv += [{"t": "rapid", "x": pts[-1][0], "y": pts[-1][1], "z": 5.0}]
    return mv


def face_rows(x0, x1, y0, y1, D, z, f, stock_top=5.0):
    """端铣：沿 X 来回走，行距 0.75D；从工件外切入、切出"""
    rows = max(1, math.ceil((y1 - y0) / (0.75 * D)))
    ys = [y0 + (y1 - y0) * (k + 0.5) / rows for k in range(rows)]
    mv = [{"t": "comment", "text": "端铣 Face milling：{} 行，Z{:g}".format(rows, z)}]
    for k, y in enumerate(ys):
        a, b = (x0 - D / 2 - 3, x1 + D / 2 + 3) if k % 2 == 0 else (x1 + D / 2 + 3, x0 - D / 2 - 3)
        mv += [{"t": "rapid", "x": a, "y": y, "z": stock_top}, {"t": "feed", "x": a, "y": y, "z": z, "f": f},
               {"t": "feed", "x": b, "y": y, "z": z, "f": f}, {"t": "rapid", "x": b, "y": y, "z": stock_top}]
    return mv


def rpm(vc, d, m="HMC-01"):
    return cam.spindle_rpm(vc, d, cam_post.MACHINES[m]["max_rpm"])


def op(title, frame, n_tool, name, d, vc, moves, kind="endmill", machine="HMC-01"):
    r = rpm(vc, d, machine)
    tp = next((m for m in moves if m.get("cycle") == "G84"), None)
    if tp:
        r = tp["f"] / tp["pitch"]                # 刚性攻丝：转速必须等于 F / 螺距
    o = dict(title=title, tool={"n": n_tool, "name": name, "d": d}, spindle={"rpm": r}, moves=moves, wcs=WCS[frame], frame=frame,
             kind=kind)
    if machine == "HMC-01":
        o["b"] = BVAL[frame]
    return o


# ---------------------------------------------------------------- 程序
def pair_hmc():
    """合件工序 70（锥销、测针杆轴线、精加工）、80（钻攻）——卧加，下件 A ＋ 两工艺孔"""
    ops = []
    pu = [to_frame("UNDER", (x, y, -16.0))[:2] for x, y in PINS]
    r = rpm(60, 8.5)
    ops.append(op("直角铣头（机座底下向上）钻锥销底孔 Ø8.5，穿过下件凸台进上件工艺孔", "UNDER", 21, "钻头 Ø8.5", 8.5, 60, cam.drill(pu, 28, 0, 0.15 * r, r_plane=2, safe=55),
                  kind="drill"))
    ops.append(op("直角铣头 粗铰、精铰 1:50 锥销孔（仿真按小端 Ø10）", "UNDER", 22, "锥度铰刀 1:50", 10, 8, cam.bore(pu, 28, 0.15 * rpm(8, 10), r_plane=2, safe=55)))
    # 测针杆轴线：测头 B 0°，下塞规 z 30、上塞规 z 190，各 3 点（−x、−y、+y 三个方向接近）
    mv = [{"t": "comment", "text": "测针杆轴线：针杆上、下孔已插液压涨紧测量塞规 Ø12；测头 B 0°，每个塞规 3 点定圆心"},
          {"t": "comment", "text": "两个圆心连线外推到 z -21.5、z 200，结果写入 G54 / G58 的 Y 偏置（宏程序 O9811 / O9812）"}]
    for zt in (30.0, 190.0):
        X0, Y0, Z0 = to_frame("B0", (0.0, 0.0, zt))
        for dx, dy in ((0.0, -1.0), (1.0, 0.0), (-1.0, 0.0)):      # 帧内：X = −y（零件），Z = −(x + 62)
            ax, ay = X0 + dx * (6 + 1.5 + 4), Y0
            az = (Z0 + 62 - 6 - 1.5 - 4) if dy < 0 else Z0
            mv += [{"t": "rapid", "x": ax, "y": ay, "z": 70.0}, {"t": "rapid", "x": ax, "y": ay, "z": az},
                   {"t": "feed", "x": X0 + dx * 7.5, "y": ay, "z": (Z0 + 62 - 7.5) if dy < 0 else az, "f": 100},
                   {"t": "rapid", "x": ax, "y": ay, "z": az}, {"t": "rapid", "x": ax, "y": ay, "z": 70.0}]
    ops.append(op("B0 测头测两个塞规（针杆轴线）", "B0", 30, "测头（测针 Ø3）", 3, 1, mv, kind="probe"))
    r = rpm(200, 63)
    ops.append(op("B0 精铣面板口端面", "B0", 2, "面铣刀 Ø63", 63, 200, face_rows(-72, 50, -82, 60, 63, 0.0, 0.08 * 5 * r)))
    hx, hy, _ = to_frame("LB0", (-105.0, 0.0, ZH))
    r = rpm(120, 13.7)
    ops.append(op("B0 阶梯镗杆半精镗旋梭轴孔 Ø13.7（从左端壁 Ø20 孔伸进去，孔在 x 30…66；G4.6 轴座左端由 24 缩到 30）", "LB0", 23, "阶梯镗杆 Ø13.7", 13.7, 120,
                  cam.bore([(hx, hy)], 66 + 105, 0.10 * r, r_plane=-(30 + 105 - 2)), kind="linebar"))
    r = rpm(140, 14)
    ops.append(op("B0 精镗旋梭轴孔 Ø14 H7", "LB0", 24, "阶梯精镗杆 Ø14", 14, 140, cam.bore([(hx, hy)], 66 + 105, 0.05 * r, r_plane=-(30 + 105 - 2)),
                  kind="linebar"))
    # G4.6 送布组的孔（B 0°：从左端壁的工艺孔伸进去）
    fx, fy_, _ = to_frame("LB0", (-105.0, *FEED["Fr"]))
    gx, gy_, _ = to_frame("LB0", (-105.0, *FEED["Lr"]))
    for d_, vc_, fz_, tno in ((13.7, 120, 0.10, 33), (14.0, 140, 0.05, 34)):
        r = rpm(vc_, d_)
        ops.append(op(f"B0 摆轴镗杆 Ø{d_:g} 镗送布摆轴前孔（x 33…47，左端壁 Ø16 工艺孔进）", "LB0", tno, f"摆轴镗杆 Ø{d_:g}", d_, vc_,
                      cam.bore([(fx, fy_)], 47 + 105 + 1, fz_ * r, r_plane=-(33 + 105 - 2)), kind="linebar"))
        ops.append(op(f"B0 摆轴镗杆 Ø{d_:g} 镗抬牙摆轴后孔（x 95…107，穿过前孔铸出的 Ø15）", "LB0", tno, f"摆轴镗杆 Ø{d_:g}", d_, vc_,
                      cam.bore([(gx, gy_)], 107 + 105 + 1, fz_ * r, r_plane=-(95 + 105 - 2)), kind="linebar"))
    for d_, vc_, fz_, tno in ((15.7, 120, 0.10, 35), (16.0, 140, 0.05, 36)):
        r = rpm(vc_, d_)
        ops.append(op(f"B0 摆轴镗杆 Ø{d_:g} 镗抬牙摆轴前孔（x 24…38，左端壁 Ø18 工艺孔进）", "LB0", tno, f"摆轴镗杆 Ø{d_:g}", d_, vc_,
                      cam.bore([(gx, gy_)], 38 + 105 + 1, fz_ * r, r_plane=-(24 + 105 - 2)), kind="linebar"))
    r = rpm(140, 34.7)
    ops.append(op("B0 同轴半精镗上轴两孔 Ø34.7 / Ø31.7（程序按前刀编）", "B0", 25, "同轴半精镗杆", 31.7, 140,
                  [{"t": "comment", "text": "右导向套支架翻上；压板油压降到 40%（M 代码由夹具 PLC 处理）"}]
                  + cam.bore([(0.0, 0.0)], 62 + 44 + 1, 0.12 * r, r_plane=-(62 + 31 - 2)), kind="linebar"))
    r = rpm(150, 35)
    ops.append(op("B0 同轴精镗上轴两孔 Ø35 H7 / Ø32 H7（前刀走完 6202 孔时后刀正好走完 6201 孔）", "B0", 13, "同轴精镗杆", 32, 150,
                  cam.bore([(0.0, 0.0)], 62 + 44 + 1, 0.06 * r, r_plane=-(62 + 31 - 2)), kind="linebar"))
    r = rpm(120, 20)
    ops.append(op("B180 镗轴过孔 Ø20 H11", "B180", 4, "精镗刀 Ø20", 20, 120, cam.bore([(0.0, 0.0)], 36, 0.12 * r, r_plane=2)))
    r = rpm(200, 63)
    ops.append(op("B180 精铣电机法兰端面", "B180", 2, "面铣刀 Ø63", 63, 200, face_rows(-1, 1, -1, 1, 63, 0.0, 0.08 * 5 * r)))
    r = rpm(180, 20)
    ops.append(op("B180 圆弧插补精铣止口 Ø52 h7", "B180", 5, "立铣刀 Ø20", 20, 180, circle(0, 0, 26 - 0.015 + 10, -8, 0.05 * 4 * r)))
    lx, ly, lz = to_frame("B180", (412.0, YL, ZL))
    r = rpm(140, 31.7)
    ops.append(op("B180 下轴同轴半精镗 Ø31.7（两刀相距 276，程序按前刀编：前刀在左孔 x 88…104）", "B180", 26, "下轴半精镗杆", 31.7, 140,
                  [{"t": "comment", "text": "左导向套支架翻上；压板油压降到 40%"}]
                  + cam.bore([(lx, ly)], 408 - 88 + 1, 0.12 * r, r_plane=-(408 - 106), safe=10), kind="linebar"))
    r = rpm(150, 32)
    ops.append(op("B180 下轴同轴精镗两孔 Ø32 H7", "B180", 27, "下轴精镗杆", 32, 150,
                  cam.bore([(lx, ly)], 408 - 88 + 1, 0.06 * r, r_plane=-(408 - 106), safe=10), kind="linebar"))
    # G4.6 B 180°：送布摆轴后孔、调节器孔（从右端壁、右横筋的工艺孔伸进去）
    bx, by, _ = to_frame("B180", (412.0, *FEED["Fr"]))
    for d_, vc_, fz_, tno in ((13.7, 120, 0.10, 33), (14.0, 140, 0.05, 34)):
        r = rpm(vc_, d_)
        ops.append(op(f"B180 摆轴镗杆 Ø{d_:g} 镗送布摆轴后孔（x 296…311，右端壁、右横筋 Ø16 工艺孔进）", "B180", tno, f"摆轴镗杆 Ø{d_:g}", d_, vc_,
                      cam.bore([(bx, by)], 408 - 296 + 1, fz_ * r, r_plane=-(408 - 313), safe=10), kind="linebar"))
    cx, cy, _ = to_frame("B180", (412.0, *FEED["G"]))
    r = rpm(70, 9.7)
    ops.append(op("B180 加长钻 Ø9.7 调节器轴孔（x 296…311，Ø14 工艺孔进）", "B180", 37, "加长钻头 Ø9.7", 9.7, 70,
                  cam.drill([(cx, cy)], 408 - 296 + 1, 0, 0.12 * r, r_plane=-(408 - 313), safe=10), kind="linebar"))
    r = rpm(12, 10)
    ops.append(op("B180 加长铰刀 Ø10 H7 铰调节器轴孔", "B180", 38, "加长铰刀 Ø10 H7", 10, 12,
                  cam.bore([(cx, cy)], 408 - 296 + 1, 0.2 * r, r_plane=-(408 - 313), safe=10), kind="linebar"))
    # 工序 80：螺纹孔
    r = rpm(60, 4.2)
    mh = [to_frame("B180", p)[:2] for p in [(408.0, 14.142, 214.142), (408.0, -14.142, 214.142), (408.0, -14.142, 185.858), (408.0, 14.142, 185.858)]]
    ops.append(op("B180 钻 M5 底孔 Ø4.2", "B180", 10, "钻头 Ø4.2", 4.2, 60, cam.drill(mh, 11, 0, 0.1 * r), kind="drill"))
    ops.append(op("B180 攻 M5", "B180", 15, "丝锥 M5（仿真按底孔 Ø4.2）", 4.2, 8, cam.tap(mh, 9, 0.8, rpm(8, 5)), kind="drill"))
    fh = [to_frame("B0", p)[:2] for p in [(-62.0, -33.5, 143.36), (-62.0, -33.5, 203.36), (-62.0, 55.5, 143.36), (-62.0, 55.5, 203.36)]]
    ops.append(op("B0 钻面板口 M4 底孔", "B0", 11, "钻头 Ø3.3", 3.3, 60, cam.drill(fh, 9, 0, 0.08 * rpm(60, 3.3)), kind="drill"))
    ops.append(op("B0 攻 M4", "B0", 16, "丝锥 M4（仿真按底孔 Ø3.3）", 3.3, 8, cam.tap(fh, 7, 0.7, rpm(8, 4)), kind="drill"))
    wh = [to_frame("B270", p)[:2] for p in [(-42, -48, 132), (-42, -48, 169), (-42, -48, 220), (32, -48, 132), (32, -48, 169), (32, -48, 220)]]
    ops.append(op("B270 钻前窗口 M4 底孔", "B270", 11, "钻头 Ø3.3", 3.3, 60, cam.drill(wh, 9, 0, 0.08 * rpm(60, 3.3)), kind="drill"))
    ops.append(op("B270 攻 M4", "B270", 16, "丝锥 M4（仿真按底孔 Ø3.3）", 3.3, 8, cam.tap(wh, 7, 0.7, rpm(8, 4)), kind="drill"))
    th = [to_frame("TOPARM", (x, y, 259.0))[:2] for x in (118.0, 252.0) for y in (-6.0, 30.0)]
    ops.append(op("直角铣头（从上面）钻顶盖 M4 底孔", "TOPARM", 31, "钻头 Ø3.3（直角铣头）", 3.3, 60, cam.drill(th, 5, 0, 0.08 * rpm(60, 3.3)), kind="drill"))
    ops.append(op("直角铣头 攻顶盖 M4", "TOPARM", 32, "丝锥 M4（直角铣头，仿真按底孔 Ø3.3）", 3.3, 8, cam.tap(th, 3.5, 0.7, rpm(8, 4)), kind="drill"))
    return ops


def upper_hmc_rough():
    """上件工序 20（粗加工）"""
    ops = []
    r = rpm(110, 18)
    ops.append(op("B180 粗镗轴过孔 Ø16 → Ø18", "B180", 14, "粗镗刀 Ø18", 18, 110, cam.bore([(0.0, 0.0)], 40, 0.2 * r)))
    r = rpm(160, 63)
    ops.append(op("B180 粗铣电机座端面（留 0.5）", "B180", 2, "面铣刀 Ø63", 63, 160, face_rows(-1, 1, -1, 1, 63, 0.5, 0.15 * 5 * r, stock_top=8)))
    r = rpm(150, 20)
    ops.append(op("B180 圆弧插补粗铣止口 Ø57 → Ø53", "B180", 5, "立铣刀 Ø20", 20, 150,
                  circle(0, 0, 27.5 + 10, -8, 0.1 * 4 * r) + circle(0, 0, 26.5 + 10, -8, 0.1 * 4 * r)))
    r = rpm(160, 63)
    ops.append(op("B0 粗铣面板口端面（留 0.5）", "B0", 2, "面铣刀 Ø63", 63, 160, face_rows(-72, 50, -82, 60, 63, 0.5, 0.15 * 5 * r, stock_top=8)))
    r = rpm(110, 34)
    ops.append(op("B0 同轴粗镗两轴承孔 Ø34 / Ø31（程序按前刀编）", "B0", 3, "同轴粗镗杆", 31, 110,
                  cam.bore([(0.0, 0.0)], 62 + 44 + 1, 0.25 * r, r_plane=-(62 + 31 - 2)), kind="linebar"))
    r = rpm(60, 14)
    ops.append(op("直角铣头 锪针杆孔下端沉孔 Ø14 深 4", "DOWN_HEAD", 18, "锪钻 Ø14", 14, 60, cam.bore([(0.0, 0.0)], 5, 0.08 * r, r_plane=8, safe=15),
                  kind="drill"))
    r = rpm(60, 11.5)
    ops.append(op("直角铣头 钻针杆孔 Ø11.5（钻通上下两个导套座）", "DOWN_HEAD", 7, "钻头 Ø11.5", 11.5, 60, cam.drill([(0.0, 0.0)], 150, 10, 0.15 * r, r_plane=8, safe=15),
                  kind="drill"))
    return ops


def upper_vmc(finish):
    """上件工序 10（粗、半精铣 C、钻工艺孔）/ 40（精铣 C、铰工艺孔、攻 M10）——立加，工件倒放"""
    ops = []
    pins = [to_frame("C_UP", (x, y, 0.0))[:2] for x, y in PINS]
    bolts = [to_frame("C_UP", (x, y, 0.0))[:2] for x, y in ((319.8, -42.2), (376.2, -42.2), (319.8, 96.2), (376.2, 96.2))]
    if not finish:
        r = rpm(160, 80, "VMC-01")
        ops.append(op("粗铣接合面 C（留 1.0）", "C_UP", 1, "面铣刀 Ø80", 80, 160, face_rows(-56, 56, -98, 98, 80, 1.0, 0.18 * 8 * r, 10), machine="VMC-01"))
        r = rpm(200, 80, "VMC-01")
        ops.append(op("半精铣接合面 C（留 0.5）", "C_UP", 1, "面铣刀 Ø80", 80, 200, face_rows(-56, 56, -98, 98, 80, 0.5, 0.10 * 8 * r, 10), machine="VMC-01"))
        r = rpm(70, 8.5, "VMC-01")
        ops.append(op("钻两个工艺孔 Ø8.5", "C_UP", 8, "钻头 Ø8.5", 8.5, 70, cam.drill(pins, 12, 0, 0.2 * r), machine="VMC-01", kind="drill"))
        ops.append(op("扩工艺孔 Ø8.85", "C_UP", 19, "扩孔钻 Ø8.85", 8.85, 60, cam.bore(pins, 12, 0.15 * rpm(60, 8.85, "VMC-01")), machine="VMC-01"))
        ops.append(op("铰工艺孔 Ø9 H7", "C_UP", 9, "铰刀 Ø9 H7", 9, 12, cam.bore(pins, 12, 0.3 * rpm(12, 9, "VMC-01")), machine="VMC-01"))
        ops.append(op("钻 M10 底孔 Ø8.5", "C_UP", 12, "钻头 Ø8.5", 8.5, 70, cam.drill(bolts, 22, 0, 0.18 * rpm(70, 8.5, "VMC-01")), machine="VMC-01",
                      kind="drill"))
        ops.append(op("攻 M10（卧加夹具的拉杆也拧在这里）", "C_UP", 17, "丝锥 M10（仿真按底孔 Ø8.5）", 8.5, 10, cam.tap(bolts, 18, 1.5, rpm(10, 10, "VMC-01")),
                      machine="VMC-01", kind="drill"))
    else:
        r = rpm(220, 80, "VMC-01")
        ops.append(op("精铣接合面 C（平面度 0.02）", "C_UP", 1, "面铣刀 Ø80", 80, 220, face_rows(-56, 56, -98, 98, 80, 0.0, 0.06 * 8 * r, 10), machine="VMC-01"))
        nd = [to_frame("C_UP", (0.0, 0.0, 0.0))[:2]]
        # 机头底面比 C 低 46（倒放时在 C 下面）：快移到 R 点 −30（机头底面前 16，空当里），铰到 z 182（上导套座顶面）
        ops.append(op("扩针杆孔 Ø11.85（上、下两孔一次扩通）", "C_UP", 20, "扩孔钻 Ø11.85（加长）", 11.85, 60,
                      cam.bore(nd, 182, 0.12 * rpm(60, 11.85, "VMC-01"), r_plane=-30, safe=5), machine="VMC-01", kind="drill"))
        ops.append(op("铰针杆孔 Ø12 H7（一次铰通）", "C_UP", 7, "铰刀 Ø12 H7（加长）", 12, 12, cam.bore(nd, 182, 0.25 * rpm(12, 12, "VMC-01"), r_plane=-30, safe=5),
                      machine="VMC-01", kind="drill"))
    return ops


def lower_vmc(stage):
    ops = []
    if stage == 10:
        r = rpm(160, 100, "VMC-01")
        ops.append(op("粗铣底面 A（留 0.8）", "A_UP", 1, "面铣刀 Ø100", 100, 160, face_rows(-262, 262, -100, 100, 100, 0.8, 0.18 * 10 * r, 10), machine="VMC-01"))
        r = rpm(200, 100, "VMC-01")
        ops.append(op("半精铣底面 A（留 0.3）", "A_UP", 1, "面铣刀 Ø100", 100, 200, face_rows(-262, 262, -100, 100, 100, 0.3, 0.10 * 10 * r, 10), machine="VMC-01"))
        ph = [to_frame("A_UP", (x, y, -62.0))[:2] for x, y in ((-94.4, -30.0), (401.4, 80.0))]
        ops.append(op("钻、铰两个工艺孔 Ø10 H7（底边法兰）", "A_UP", 3, "铰刀 Ø10 H7", 10, 12, cam.bore(ph, 6, 0.3 * rpm(12, 10, "VMC-01")), machine="VMC-01"))
    elif stage == 20:
        r = rpm(160, 100, "VMC-01")
        ops.append(op("粗铣机座顶面（4 → 0.5，两刀）", "TOP", 1, "面铣刀 Ø100", 100, 160,
                      face_rows(-262, 262, -100, 100, 100, 2.25, 0.18 * 10 * r, 10) + face_rows(-262, 262, -100, 100, 100, 0.5, 0.18 * 10 * r, 10),
                      machine="VMC-01"))
        bh = [to_frame("TOP", (x, y, 0.0))[:2] for x, y in ((319.8, -42.2), (376.2, -42.2), (319.8, 96.2), (376.2, 96.2))]
        ops.append(op("钻 4 × Ø11 通孔", "TOP", 4, "钻头 Ø11", 11, 70, cam.drill(bh, 30, 0, 0.2 * rpm(70, 11, "VMC-01")), machine="VMC-01", kind="drill"))
    elif stage == 30:
        # 下件单独装在 FX-HSG-P-70 上（卧加）：左端壁两个 Ø20 过孔、粗镗旋梭轴孔、粗镗下轴两孔
        for (yy, zz) in ((0.0, ZH), (YL, ZL)):
            cx, cy, _ = to_frame("LB0", (-105.0, yy, zz))
            r = rpm(150, 16)
            mv = []
            for k, zc in enumerate((-2.0, -4.0, -6.5)):
                mv += circle(cx, cy, 10 - 8, zc, 0.05 * 4 * r)[2 if k else 0:]
            ops.append(op("B0 螺旋插补铣左端壁 Ø20 过孔", "LB0", 2, "立铣刀 Ø16", 16, 150, mv, machine="HMC-01"))
        hx, hy, _ = to_frame("LB0", (-105.0, 0.0, ZH))
        r = rpm(100, 13)
        ops.append(op("B0 阶梯粗镗杆粗镗旋梭轴孔 Ø9 → Ø13", "LB0", 10, "阶梯粗镗杆 Ø13", 13, 100,
                      cam.bore([(hx, hy)], 66 + 105, 0.12 * r, r_plane=-(30 + 105 - 2)), machine="HMC-01", kind="linebar"))
        lx, ly, lz = to_frame("B180", (412.0, YL, ZL))
        r = rpm(110, 31)
        ops.append(op("B180 下轴粗镗杆两孔一刀粗镗 Ø27 → Ø31", "B180", 9, "下轴粗镗杆", 31, 110,
                      [{"t": "comment", "text": "左导向套支架翻上；进刀时主轴定向、刀尖朝上，抬高 1 mm 穿过右端壁、横筋 Ø34 孔"}]
                      + cam.bore([(lx, ly)], 408 - 88 + 1, 0.25 * r, r_plane=-(408 - 106), safe=10), machine="HMC-01", kind="linebar"))
    else:
        r = rpm(220, 100, "VMC-01")
        ops.append(op("（第一次装夹：翻面，顶面定位）精铣底面 A（平面度 0.05）", "A_UP", 1, "面铣刀 Ø100", 100, 220,
                      face_rows(-262, 262, -100, 100, 100, 0.0, 0.06 * 10 * r, 10), machine="VMC-01"))
        ops.append(op("（第二次装夹：A ＋ 两工艺孔）精铣机座顶面（高 62 ± 0.05）", "TOP", 1, "面铣刀 Ø100", 100, 220, face_rows(-262, 262, -100, 100, 100, 0.0, 0.06 * 10 * r, 10),
                      machine="VMC-01"))
        r = rpm(180, 16, "VMC-01")
        pk = cam.mill_pocket([(-32 - 153, -22 - 34), (32 - 153, -22 - 34), (32 - 153, 22 - 34), (-32 - 153, 22 - 34)], 2.5, 16, 0.45, 1.25,
                             0.05 * 4 * r, 0.02 * 4 * r)
        ops.append(op("铣针板座（深 2.5）", "TOP", 2, "立铣刀 Ø16", 16, 180, pk, machine="VMC-01"))
        ps = cam.mill_pocket([(-23 - 153, -58 - 34), (23 - 153, -58 - 34), (23 - 153, -22 - 34), (-23 - 153, -22 - 34)], 1.5, 16, 0.45, 1.5,
                             0.05 * 4 * r, 0.02 * 4 * r)
        ops.append(op("铣滑板座（深 1.5）", "TOP", 2, "立铣刀 Ø16", 16, 180, ps, machine="VMC-01"))
        nh = [to_frame("TOP", (x, y, -2.5))[:2] for x, y in ((-27, -19.5), (27, -19.5), (-27, 19.5), (27, 19.5))]      # G4.6：针板螺孔 y ±17 → ±19.5（cad/housing.py）
        ops.append(op("钻 M3 底孔 Ø2.5", "TOP", 6, "钻头 Ø2.5", 2.5, 50, cam.drill(nh, 9.5, 0, 0.06 * rpm(50, 2.5, "VMC-01")), machine="VMC-01",
                      kind="drill"))
        ops.append(op("攻 M3", "TOP", 18, "丝锥 M3（仿真按底孔 Ø2.5）", 2.5, 6, cam.tap(nh, 8.0, 0.5, rpm(6, 3, "VMC-01")), machine="VMC-01", kind="drill"))
    return ops


PROGRAMS = {   # 程序号: (标题, 零件, 工序, 机床, 生成函数)（G5.2：上件粗、下件粗、合件精）
    1201: ("上件 工序 10 粗、半精铣接合面、钻铰工艺孔、攻 M10", "upper", 10, "VMC-01", lambda: upper_vmc(False)),
    1202: ("上件 工序 20 卧加粗加工", "upper", 20, "HMC-01", upper_hmc_rough),
    1205: ("上件 工序 50 精铣接合面、扩铰针杆孔", "upper", 50, "VMC-01", lambda: upper_vmc(True)),
    1301: ("下件 工序 10 铣底面 A、工艺孔", "lower", 10, "VMC-01", lambda: lower_vmc(10)),
    1302: ("下件 工序 20 粗铣顶面、过孔", "lower", 20, "VMC-01", lambda: lower_vmc(20)),
    1303: ("下件 工序 30 卧加粗镗（左端壁过孔、旋梭轴孔、下轴两孔）", "lower", 30, "HMC-01", lambda: lower_vmc(30)),
    1305: ("下件 工序 50 精铣底面、顶面、针板座、M3", "lower", 50, "VMC-01", lambda: lower_vmc(50)),
    1401: ("合件 工序 70、80 锥销、测针杆轴线、精加工、钻攻", "pair", 70, "HMC-01", pair_hmc),
}


def simulate(ops, text, machine, tris_blank, tris_part, frames, tol=0.02):
    """按面仿真：每个面单独解析（只含这个面的工步），毛坯高度图作起始，成品高度图比对"""
    out = []
    for fr in frames:
        sub = [o for o in ops if o["frame"] == fr and o.get("kind") not in ("linebar", "probe")]
        if not sub:
            continue
        prog = dict(machine=machine, title=fr, number=1, ops=[{k: v for k, v in o.items() if k not in ("frame", "kind", "b")} for o in sub])
        p = cam_sim.parse(cam_post.post(prog), machine)
        xs_all = [mv["b"][0] for mv in p["moves"]]
        ys_all = [mv["b"][1] for mv in p["moves"]]
        pad = 40
        x0, x1, y0, y1 = min(xs_all) - pad, max(xs_all) + pad, min(ys_all) - pad, max(ys_all) + pad
        h = 1.0
        xs = np.arange(x0, x1, h) + h / 2
        ys = np.arange(y0, y1, h) + h / 2
        HP = heightmap(tris_part, fr, xs, ys)
        # 毛坯一定包住零件：毛坯与零件的三角网格在圆柱面的轮廓边上各自取弦，会差零点几毫米，起始材料取两者的较高者；
        # 比对过切时，目标取 3 × 3 格（±1 mm）里最低的，免得把轮廓边上的取弦差当成过切
        HB = np.fmax(heightmap(tris_blank, fr, xs, ys), HP)
        from scipy import ndimage
        HPm = ndimage.minimum_filter(np.where(np.isnan(HP), np.inf, HP), size=3)
        HP = np.where(np.isnan(HP), np.nan, HPm)

        def hb(X, Y):
            ix = np.clip(((X - xs[0]) / h).round().astype(int), 0, len(xs) - 1)
            iy = np.clip(((Y - ys[0]) / h).round().astype(int), 0, len(ys) - 1)
            return HB[ix, iy]

        def hp(X, Y):
            ix = np.clip(((X - xs[0]) / h).round().astype(int), 0, len(xs) - 1)
            iy = np.clip(((Y - ys[0]) / h).round().astype(int), 0, len(ys) - 1)
            return HP[ix, iy]
        tools = {o["tool"]["n"]: {"kind": "drill" if o.get("kind") == "drill" else "endmill", "d": o["tool"]["d"]} for o in sub}
        sim = cam_sim.simulate_mill(p, {"box": (x0 + pad / 2, y0 + pad / 2, x1 - pad / 2, y1 - pad / 2), "top": 0.0, "height": hb}, tools,
                                    target=hp, h=h, tol=tol)
        out.append(dict(frame=fr, steps=len(sub), issues=[i["text"] for i in sim["issues"]], over_cells=sim.get("over", 0),
                        dev_min=round(sim.get("dev_min", 0.0), 3), ap_max=round(sim["ap_max"], 2)))
    return out


def linebar_clearance(tris_part):
    """同轴镗杆的通过检查：镗杆 Ø28、刀 Ø35（前）/ Ø32（后）、尾部导向柱 Ø17，沿上轴轴线从机头端伸到电机端，
    每 2 mm 取一个截面，算轴线周围最近的零件材料（成品）半径，比较镗杆在这一段的半径"""
    import trimesh
    m = trimesh.Trimesh(vertices=tris_part.reshape(-1, 3), faces=np.arange(len(tris_part) * 3).reshape(-1, 3), process=True)
    xs = np.arange(-60.0, 406.0, 2.0)
    pts = np.c_[xs, np.zeros_like(xs), np.full_like(xs, ZU)]
    _, dist, _ = trimesh.proximity.closest_point(m, pts)

    def need(x):
        if x < 31 or (44 < x < 375):
            return 14.0                     # 镗杆 Ø28 穿过
        if x <= 44:
            return 17.5 - 0.05              # 前刀在 6202 孔里切削（孔本身）
        if x <= 385:
            return 16.0 - 0.05
        return 8.5                          # 尾部导向柱 Ø17 穿过 Ø20 轴过孔
    worst = min(((float(d) - need(x)), float(x)) for x, d in zip(xs, dist) if not (31 <= x <= 44 or 375 <= x <= 385))
    return dict(min_clearance_mm=round(worst[0], 2), at_x=worst[1])


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    tri = {k: CST.read_stl(src / f"{k}.stl") for k in ("blank_upper", "blank_lower", "part_upper", "part_lower")}
    tri["blank_pair"] = np.concatenate([tri["blank_upper"], tri["blank_lower"]])
    tri["part_pair"] = np.concatenate([tri["part_upper"], tri["part_lower"]])
    report = {}
    for num, (title, part, seq, machine, fn) in PROGRAMS.items():
        ops = fn()
        prog = dict(machine=machine, title=title, number=num, header=dict(item={"upper": "HSG-LS-U", "lower": "HSG-LS-L", "pair": "HSG-LS-P"}[part],
                                                                          operation=str(seq), author="问渠数字工厂（AI 编程，人工审核）", date="2026-11-11"),
                    ops=[{k: v for k, v in o.items() if k not in ("frame", "kind")} for o in ops])
        text = cam_post.post(prog)
        (out / f"O{num}.nc").write_text(text, encoding="utf-8")
        parsed = cam_sim.parse(text, machine)
        checks = cam_sim.machine_checks(parsed, machine)
        tm = cam_sim.timing(parsed, machine)
        frames = sorted({o["frame"] for o in ops if o.get("kind") != "probe"})
        sim = simulate(ops, text, machine, tri[f"blank_{part}"], tri[f"part_{part}"], frames)
        report[f"O{num}"] = dict(title=title, machine=machine, lines=len(text.splitlines()), tools=parsed["tools"],
                                 b_indexes=tm.get("b_indexes", 0), time_min=round(tm["total_s"] / 60, 2), cut_min=round(tm["cut_s"] / 60, 2),
                                 checks=[c["text"] for c in checks if c["level"] == "error"], sim=sim)
        print(f"O{num} {title}: {len(text.splitlines())} 行，{tm['total_s'] / 60:.1f} min；检查 {len(report[f'O{num}']['checks'])} 个问题")
        for s in sim:
            print("    ", s)
    report["linebar"] = linebar_clearance(tri["part_upper"])
    print("同轴镗杆通过检查", report["linebar"])
    (out / "数控程序_核对.json").write_text(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
