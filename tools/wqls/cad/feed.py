"""WQ-LS 送布组零件（第 138 轮 G4.6），由 cad/mech.py 调用：build() 返回 {零件名: (实体, 显示材料, 密度键, 转动类别)}。

位置来自 g4_feed.py 的综合结果（docs/设计/WQ-LS/G4/送布机构.json 的 poses.s3，φ = 0 时的位置；3 mm 正缝）。
所有运动都在垂直于 x 的平面里，x 是层：
  送布偏心、送布连杆 x 327…335；调节器板 x 318…326；滑块和销 x 318…342；水平连杆 L2、送布摆轴曲柄 x 336…342；
  送布摆轴 Ø10（x 22…342），前端摆杆 x 28…32；牙架 x 23.5…27.5，送布牙在针两边；
  抬牙偏心、抬牙连杆 x 108…116，抬牙曲柄 x 116…122；抬牙摆轴 Ø10（x 15…122），叉子 x 19…23。
转动类别：'upper' 随上轴、'lower' 随下轴、'plane' 平面运动（变换由 g4_mech.py 按两点给出）、None 不动。
"""
import json
import math
import os

import FreeCAD as App
import Part

V = App.Vector
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FEED = json.load(open(os.path.join(ROOT, "docs", "设计", "WQ-LS", "G4", "送布机构.json"), encoding="utf-8"))
SET = os.environ.get("WQ_FEED", "s3")
P0 = FEED["poses"][SET]
GEO, PAR = FEED["geo"], FEED["params"]
X = dict(ecc=(327.0, 335.0), reg=(318.0, 326.0), link=(335.6, 341.6), farm=(28.0, 32.0), bar=(23.5, 27.5),
         lecc=(108.0, 116.0), lcrank=(116.0, 122.0), fork=(19.0, 23.0), rock=(22.0, 342.0), lrock=(15.0, 122.0))


def at0(key):
    return P0[key][0]


def xcyl(r, x0, x1, y, z):
    return Part.makeCylinder(r, x1 - x0, V(x0, y, z), V(1, 0, 0))


def bar2d(a, b, w, xr):
    """平面杆：从 a 到 b（(y, z)），宽 w，在 x 层 xr 里；两端圆头"""
    (y0, z0), (y1, z1) = a, b
    L = math.hypot(y1 - y0, z1 - z0)
    ang = math.degrees(math.atan2(z1 - z0, y1 - y0))
    box = Part.makeBox(xr[1] - xr[0], L, w, V(xr[0], 0, -w / 2))
    box.rotate(V(xr[0], 0, 0), V(1, 0, 0), ang)
    box.translate(V(0, y0, z0))
    return box.fuse(xcyl(w / 2, *xr, y0, z0)).fuse(xcyl(w / 2, *xr, y1, z1))


def build():
    P = {}
    O1, O2 = GEO["O1"], GEO["O2"]
    E, Pp, C, T, D, K, EL, dog = (at0(k) for k in ("E", "P", "C", "T", "D", "K", "EL", "dog"))
    Fr, Lr, G = GEO["Fr"], GEO["Lr"], GEO["G"]
    # ---- 送布偏心（上轴上，孔 Ø16）
    ecc = xcyl(11.0, *X["ecc"], *E).cut(xcyl(8.0, X["ecc"][0] - 1, X["ecc"][1] + 1, *O1))
    P["feed_ecc"] = (ecc, "metal", "steel", "upper")
    # ---- 送布连杆：大头套在偏心上（外 r15、内 r11.05），杆身 8 宽，小头 r6 带 Ø6 销孔
    rod = bar2d(E, Pp, 8.0, X["ecc"]).fuse(xcyl(15.0, *X["ecc"], *E)).fuse(xcyl(6.0, *X["ecc"], *Pp))
    rod = rod.cut(xcyl(11.05, X["ecc"][0] - 1, X["ecc"][1] + 1, *E)).cut(xcyl(3.0, X["ecc"][0] - 1, X["ecc"][1] + 1, *Pp))
    P["feed_rod"] = (rod, "metal", "alu", "plane")          # 铝合金压铸（ADC12），杆长 250，钢的 141 g 惯性力太大
    # ---- 调节器板：绕 G 转到调节器角（这一档），中间滑槽沿 u；板 20 × 16，槽 7 宽
    u = P0["u"]
    ang = math.degrees(math.atan2(u[1], u[0]))
    plate = Part.makeBox(X["reg"][1] - X["reg"][0], 22.0, 16.0, V(X["reg"][0], -11.0, -8.0))
    slot = Part.makeBox(X["reg"][1] - X["reg"][0] + 2, 15.0, 7.0, V(X["reg"][0] - 1, -7.5, -3.5))
    plate = plate.cut(slot)
    plate.rotate(V(0, 0, 0), V(1, 0, 0), ang)
    plate.translate(V(0, *G))
    plate = plate.fuse(xcyl(4.0, 298.0, X["reg"][0], *G))            # 调节器轴 Ø8（装在立柱下左横筋的座里，x 297…310）
    P["regulator"] = (plate, "metal", "steel", None)
    # ---- 滑块（在调节器槽里）＋ 销（穿过送布连杆小头、L2 一端）
    blk = Part.makeBox(X["reg"][1] - X["reg"][0], 9.0, 6.6, V(X["reg"][0], -4.5, -3.3))
    blk.rotate(V(0, 0, 0), V(1, 0, 0), ang)
    blk.translate(V(0, *Pp))
    blk = blk.fuse(xcyl(2.95, X["reg"][0], X["link"][1], *Pp))
    P["reg_slider"] = (blk, "metal", "steel", "plane")
    # ---- 水平连杆 L2（P → C）
    l2 = bar2d(Pp, C, 8.0, X["link"]).cut(xcyl(3.0, X["link"][0] - 1, X["link"][1] + 1, *Pp)).cut(
        xcyl(3.0, X["link"][0] - 1, X["link"][1] + 1, *C))
    P["feed_link"] = (l2, "metal", "steel", "plane")
    # ---- 送布摆轴：轴 Ø10、曲柄（朝下到 C）、前端摆杆（朝上到 T）
    rock = xcyl(5.0, *X["rock"], *Fr)
    rock = rock.fuse(bar2d(Fr, C, 9.0, (X["link"][0] - 7.0, X["link"][0] - 1.0))).fuse(xcyl(2.95, X["link"][0] - 7.0, X["link"][1], *C))
    rock = rock.fuse(bar2d(Fr, T, 8.0, X["farm"])).fuse(xcyl(2.45, X["bar"][0], X["farm"][1], *T))
    P["feed_rock"] = (rock, "metal", "steel", "plane")
    # ---- 牙架：从 T 到叉子处的滑块 K，宽 5（z），在 x 23.5…27.5；前端滑块销伸到叉子层
    bar = bar2d(T, (K[0], T[1] + (K[1] - T[1])), 5.0, X["bar"])
    bar = bar.cut(xcyl(2.5, X["bar"][0] - 1, X["bar"][1] + 1, *T))
    bar = bar.fuse(xcyl(2.45, X["fork"][0], X["bar"][0], K[0], T[1] + (K[1] - T[1])))
    # ---- 送布牙（框式）：三排牙在针两边（x −6.5…−3.5、3.5…6.5、9…12），y −12…12，高 2.5；两端往下接侧梁
    zt, yd = dog[1], dog[0]
    rows = None
    for x0, x1 in ((-6.5, -3.5), (3.5, 6.5), (9.0, 12.0)):
        r_ = Part.makeBox(x1 - x0, 24.0, 2.5, V(x0, yd - 12.0, zt - 2.5))
        rows = r_ if rows is None else rows.fuse(r_)
    # 侧梁：在旋梭和针板之间，y ±(11.3…14.3)（送布行程 ±2.7 后最里到 8.6、最外到 17，针板下开口 ±18），
    # 高 2.5：平均位置顶 −4.6、底 −7.1（最高时离针板底 1.1，最低时离旋梭 1.1）；牙顶平均 −0.3 → 侧梁顶 = 牙顶 − 4.3
    zb1, zb0 = zt - 4.3, zt - 6.8
    for s_ in (-1, 1):
        y0 = yd + (11.3 if s_ > 0 else -14.3)
        rows = rows.fuse(Part.makeBox(X["bar"][1] + 6.5, 3.0, zb1 - zb0, V(-6.5, y0, zb0)))
        yl_ = yd + (11.3 if s_ > 0 else -12.0)                     # 牙排两端往下接侧梁的“腿”（y 11.3…12）
        rows = rows.fuse(Part.makeBox(X["bar"][1] + 6.5, 0.7, (zt - 2.5) - zb1 + 0.1, V(-6.5, yl_, zb1)).common(
            Part.makeBox(19.0, 1.0, 10.0, V(-6.5, yl_ - 0.1, zb1 - 1))))
    # 侧梁接到牙架：牙架在 y −14.3…14.3 处往上加高到侧梁顶
    rows = rows.fuse(Part.makeBox(X["bar"][1] - X["bar"][0], 28.6, zb1 - (T[1] - 2.5), V(X["bar"][0], yd - 14.3, T[1] - 2.5)))
    P["feed_bar"] = (bar.fuse(rows), "chrome", "steel", "plane")
    # ---- 抬牙偏心（下轴上，孔 Ø12）
    lec = xcyl(10.0, *X["lecc"], *EL).cut(xcyl(6.0, X["lecc"][0] - 1, X["lecc"][1] + 1, *O2))
    P["lift_ecc"] = (lec, "metal", "steel", "lower")
    # ---- 抬牙连杆 L3（EL → D）：大头套偏心（外 r13.5、内 r10.05）
    l3 = bar2d(EL, D, 7.0, X["lecc"]).fuse(xcyl(13.5, *X["lecc"], *EL)).fuse(xcyl(5.5, *X["lecc"], *D))
    l3 = l3.cut(xcyl(10.05, X["lecc"][0] - 1, X["lecc"][1] + 1, *EL)).cut(xcyl(2.5, X["lecc"][0] - 1, X["lecc"][1] + 1, *D))
    P["lift_link"] = (l3, "metal", "alu", "plane")
    # ---- 抬牙摆轴：轴 Ø10、曲柄（到 D）、叉子（到 K，槽沿牙架方向）
    lr = xcyl(5.0, *X["lrock"], *Lr)
    lr = lr.fuse(bar2d(Lr, D, 8.0, X["lcrank"])).fuse(xcyl(2.45, X["lecc"][0], X["lcrank"][1], *D))
    Kp = (K[0], T[1] + (K[1] - T[1]))
    # 叉子：头部高 10（滑块销 Ø4.9 在 5 宽的槽里沿牙架方向滑），顶离机座顶板 ≥ 1
    fork = bar2d(Lr, (Kp[0] - 4.0, Kp[1]), 8.0, X["fork"]).fuse(Part.makeBox(X["fork"][1] - X["fork"][0], 14.0, 10.0, V(X["fork"][0], Kp[0] - 7.0, Kp[1] - 5.0)))
    fork = fork.cut(Part.makeBox(X["fork"][1] - X["fork"][0] + 2, 16.0, 5.0, V(X["fork"][0] - 1, Kp[0] - 8.0, Kp[1] - 2.5)))
    P["lift_rock"] = (lr.fuse(fork), "metal", "steel", "plane")
    return P


RHO = dict(steel=7.85e-6, alu=2.75e-6)


def inertia_x(s, rho, yc, zc):
    """绕 (yc, zc) 的 x 轴的转动惯量 kg·m²（同 cad/hook.py）"""
    s = s.Solids if s.ShapeType == "Compound" else [s]
    J = 0.0
    for so in s:
        I = so.MatrixOfInertia
        c = so.CenterOfMass
        J += (I.A11 + so.Volume * ((c.y - yc) ** 2 + (c.z - zc) ** 2)) * rho
    return J * 1e-6
