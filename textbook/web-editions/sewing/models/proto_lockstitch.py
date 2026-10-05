"""平缝机虚拟样机的三维模型（第 20 轮）。零件用 build123d 造型，尺寸取《缝纫机设计与制造》第 3–8 章的算例：
针杆曲柄 r = 15.5、连杆 l = 55；挑线四连杆（第 4 章 LK0）；旋梭半径 13.5、旋梭中心在针板面下 xN(206) − 8；送布牙（第 6 章）。
外形是示意的通用工业平缝机，不仿任何品牌。

坐标（与网页 three.js 一致）：mm，y 向上，针板面 y = 0；x 沿上轴，机头（针）在左、手轮在右；z 指向操作者（前方）。
运动零件各自在“局部坐标”里造型，原点放在它的转轴或基准点上，网页按机构库 WQLS 算出的位姿摆放：
  上轴组件绕 (y = HS, z = 0) 的 x 轴转 φ；下轴组件绕 (y = YL, z = 0) 转 φ；旋梭绕 (y = YH, z = 0) 转 2φ；
  针杆组件沿 y 平移；连杆、挑线杆、挑线连杆在 yz 平面里转动；送布牙在 yz 平面里平移。

    python3 models/proto_lockstitch.py src/lib/proto-lockstitch-mesh.js      # 网格化，写成内联用的 JS
"""
from __future__ import annotations

import base64
import json
import math
import sys
from array import array

import build123d as bd

DEG = math.pi / 180
RN, LN = 15.5, 55.0


def xN(f):
    a = f * DEG
    lam = RN / LN
    return RN * (1 - math.cos(a)) - LN * (1 - math.sqrt(1 - (lam * math.sin(a)) ** 2))


# ---- 主要尺寸 ----
XN = -17.0                    # 针杆（机针）所在的 x
TIP_TDC = 18.0                # 针尖在上止点时高出针板
CLAMP_TO_TIP = 38.0           # 针夹到针尖
ROD_TO_CLAMP = 70.0           # 连杆下销到针夹
HS = TIP_TDC + CLAMP_TO_TIP + ROD_TO_CLAMP + (LN - RN)   # 上轴中心高 = 165.5
YH = -(xN(206) - 8)           # 旋梭中心（针板面以下约 21 mm）
YL = YH - 31.0                # 下轴中心（齿轮中心距 31，2:1）
RH = 13.5
X_TK = -34.0                  # 挑线杆所在平面的 x
X_ROD = XN                    # 连杆与针杆同一平面
LK = dict(r=20.7, d=-6.8, Qz=21.5, Qy=-45.5, a=43.4, b=40.9, c=65.7, al=2.8)


def box(x0, x1, y0, y1, z0, z1):
    return bd.Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * bd.Box(x1 - x0, y1 - y0, z1 - z0)


def cyl_x(x0, x1, r, y=0.0, z=0.0):
    """沿 x 的圆柱，x0 → x1。"""
    return bd.Pos(x0, y, z) * bd.Rot(0, 90, 0) * bd.Cylinder(r, x1 - x0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))


def cyl_y(y0, y1, r, x=0.0, z=0.0):
    return bd.Pos(x, y0, z) * bd.Rot(-90, 0, 0) * bd.Cylinder(r, y1 - y0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))


def cyl_z(z0, z1, r, x=0.0, y=0.0):
    return bd.Pos(x, y, z0) * bd.Cylinder(r, z1 - z0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))


def fil(shape, r, sel=None):
    try:
        return bd.fillet((sel or shape.edges()), r) if sel is None else bd.fillet(sel, r)
    except Exception:
        return shape


def rbox(x0, x1, y0, y1, z0, z1, r):
    b = box(x0, x1, y0, y1, z0, z1)
    try:
        return bd.fillet(b.edges(), r)
    except Exception:
        return b


def prism(pts, x0, x1):
    """yz 平面里的多边形（点为 (z, y)）沿 x 从 x0 拉伸到 x1。"""
    w = bd.Polyline(*[(x0, y, z) for z, y in pts], close=True)
    return bd.extrude(bd.make_face(w), amount=x1 - x0, dir=(1, 0, 0))


def section(x, w, h, y0, r):
    """横臂、机头用的截面：x 处、宽 w（沿 z）、高 h、底在 y0 的圆角矩形（yz 平面）。"""
    pl = bd.Plane(origin=(x, 0, 0), x_dir=(0, 0, -1), z_dir=(1, 0, 0))
    with bd.BuildSketch(pl) as sk:
        with bd.Locations((0, y0 + h / 2)):
            bd.RectangleRounded(w, h, r)
    return sk.sketch.faces()[0]


def hsection(y, x0, x1, z0, z1, r):
    """水平截面（xz 平面，高度 y）：立柱、底板用。"""
    pl = bd.Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    with bd.BuildSketch(pl) as sk:
        with bd.Locations(((x0 + x1) / 2, -(z0 + z1) / 2)):
            bd.RectangleRounded(x1 - x0, z1 - z0, r)
    return sk.sketch.faces()[0]


# =====================================================================================
# 静止零件
# =====================================================================================
def body(cut_windows=False):
    """铸造机壳：底板（带针板开口）、立柱（下宽上窄）、横臂（机头端细、立柱端粗的圆角截面）、机头，内部掏空。
    cut_windows：A+ 开窗剖切（窗口避开轴套座和立柱根部）。"""
    bed = rbox(-130, 370, -75, 0, -95, 85, 4)
    try:
        bed = bd.fillet(bed.edges().filter_by(bd.Axis.Y), 14)
    except Exception:
        pass
    bed = bed - box(-122, 362, -80, -7, -87, 77)                         # 底板下面是空的
    bed = bed - box(-48, 30, -10, 1, -40, 40)                            # 针板、推板的开口
    pillar = bd.loft([hsection(-4, 244, 352, -62, 50, 22), hsection(150, 252, 344, -52, 44, 20), hsection(222, 254, 342, -48, 42, 20)])
    arm, head = arm_solid(), head_solid()
    b = bed + pillar + arm + head
    # 内腔
    b = b - box(-55, 16, 58, 214, -36, 38)                               # 机头腔
    b = b - box(-55, 262, 156, 208, -30, 30)                             # 横臂腔（上轴）
    b = b - box(258, 337, -2, 214, -50, 38)                              # 立柱腔（同步带）
    # 盖板的开口：机头左侧面板、横臂顶盖、横臂后盖
    b = b - box(-70, -54, 66, 208, -34, 38)
    b = b - box(20, 240, 196, 230, -22, 22)
    b = b - box(40, 230, 162, 202, -50, -26)
    # 挑线杆伸出的槽、针杆和压脚杆的孔
    b = b - box(X_TK - 6, X_TK + 6, 95, 185, 30, 50)
    b = b - cyl_y(40, 62, 6, x=XN, z=0)
    b = b - cyl_y(40, 62, 6, x=XN, z=-24)
    if cut_windows:
        b = b - box(50, 130, 162, 200, 20, 50) - box(150, 228, 162, 200, 20, 50)    # 横臂前面两个窗
        b = b - box(268, 328, 20, 140, 36, 56)                                       # 立柱前面（同步带）
        b = b - box(70, 240, -62, -14, 70, 90)                                       # 底板前面（下轴）
        b = b - box(-46, 8, -62, -14, 70, 90)                                        # 底板前面（旋梭、送布）
    return b


def details():
    """外观细节（静止，并入机壳材质）：针距旋钮、倒缝扳手、抬压脚扳手、油窗、机头前部的针杆导套座。"""
    dial = cyl_z(46, 58, 19, x=300, y=120) - cyl_z(55, 59, 15.5, x=300, y=120) + cyl_z(46, 61, 6, x=300, y=120)
    lever = box(318, 326, 70, 112, 44, 52) + cyl_z(44, 56, 7, x=322, y=70)
    lift = box(-40, -32, 120, 128, -56, -40) + cyl_z(-58, -40, 5, x=-36, y=124)
    oil = cyl_z(40, 44.5, 9, x=150, y=172)
    return dial + lever + lift, oil


def arm_solid():
    return bd.loft([section(-36, 72, 60, 150, 26), section(262, 86, 74, 146, 30)])


def head_solid():
    return rbox(-62, 24, 50, 222, -44, 46, 14)


def covers():
    """盖板：机头面板（左侧）、横臂顶盖、后盖。取机壳在开口处的那一块壳体，和机壳外形齐平。
    透明版（套件 A）用同样的形状、换成聚碳酸酯材质。"""
    arm, head = arm_solid(), head_solid()
    face = (head & box(-70, -58, 66, 208, -34, 38)) - box(-58.5, 16, 58, 214, -36, 38)
    top = (arm & box(20, 240, 196, 240, -22, 22)) - box(-55, 262, 156, 208.5, -30, 30)
    rear = (arm & box(40, 230, 162, 202, -60, -26)) - box(-55, 262, 156, 208, -30.5, 30)
    return face, top, rear


def window_panes():
    """A+ 开窗处嵌的透明板（聚碳酸酯）。"""
    p = []
    p.append(box(46, 134, 154, 202, 39, 41.5))
    p.append(box(146, 239, 154, 202, 39, 41.5))
    p.append(box(264, 332, 16, 144, 45, 47.5))
    p.append(box(66, 244, -70, -10, 84, 86.5))
    p.append(box(-50, 12, -70, -10, 84, 86.5))
    return p


def plates():
    """针板（带针孔和送布牙槽）、推板。"""
    np_ = box(-48, 14, -3, 0, -40, 40)
    np_ = np_ - cyl_y(-4, 1, 1.0, x=XN, z=0)
    for dx in (-3.5, 3.5):
        np_ = np_ - box(XN + dx - 1.0, XN + dx + 1.0, -4, 1, -9, 9)
    slide = box(14, 30, -3, 0, -40, 40)
    return np_, slide


def presser():
    """压脚杆与压脚（静止；抬压脚不做）。"""
    bar = cyl_y(1.6, 230, 3.2, x=XN, z=-24)
    foot = box(XN - 12, XN + 12, 0.15, 2.4, -14, 10)
    foot = foot - box(XN - 1.6, XN + 1.6, 0, 3, -2, 12)
    shank = box(XN - 4, XN + 4, 2.4, 14, -28, -18)
    return bar + foot + shank


def tension_unit():
    """夹线器（面线张力）与过线件，装在机头正面。"""
    base = cyl_z(44, 50, 9, x=-36, y=192)
    d1 = cyl_z(50, 53, 7.5, x=-36, y=192)
    d2 = cyl_z(53.4, 56.4, 7.5, x=-36, y=192)
    stud = cyl_z(44, 66, 1.6, x=-36, y=192)
    nut = cyl_z(60, 66, 5.0, x=-36, y=192)
    guide = cyl_z(44, 54, 1.4, x=-58, y=203) + cyl_z(44, 54, 1.4, x=-18, y=110)
    return base + d1 + d2 + stud + nut, guide


def bushings():
    s = None
    for x0, x1 in ((-14, -2), (8, 20), (238, 252), (322, 336)):
        c = cyl_x(x0, x1, 9, y=HS) - cyl_x(x0 - 1, x1 + 1, 6.2, y=HS)
        s = c if s is None else s + c
    for x0, x1 in ((24, 34), (240, 252)):
        s = s + (cyl_x(x0, x1, 9, y=YL) - cyl_x(x0 - 1, x1 + 1, 6.2, y=YL))
    s = s + (cyl_y(48, 60, 6.5, x=XN, z=0) - cyl_y(47, 61, 4.4, x=XN, z=0))
    return s


# =====================================================================================
# 运动零件（局部坐标）
# =====================================================================================
def upper_shaft():
    """上轴组件（局部原点在上轴轴线上、x 与世界相同；绕 x 转 φ）：轴、针杆曲柄盘与平衡块、挑线曲柄、同步带轮、手轮。
    φ = 0 时针杆曲柄销朝上（+y），挑线曲柄销朝向按第 4 章（相位 d）。"""
    shaft = cyl_x(-30, 372, 6)
    # 针杆曲柄：曲柄盘在针杆平面右侧，曲柄销伸到 x = XN
    disc = cyl_x(XN + 4, XN + 13, 22)
    cw = cyl_x(XN + 4, XN + 13, 27) - cyl_x(XN + 3, XN + 14, 12)
    cw = cw - box(XN, XN + 20, -40, 40, -40, 0)            # 平衡块在销的对面
    cw = cw.rotate(bd.Axis.X, 0)
    # 平衡块：半圆环，放在 −y（销在 +y）
    cw = cyl_x(XN + 4, XN + 13, 30) - cyl_x(XN + 3, XN + 14, 13) - box(XN, XN + 20, 0, 40, -40, 40)
    pin = cyl_x(XN - 4, XN + 5, 3.2, y=RN)
    # 挑线曲柄：在挑线杆平面 X_TK，曲柄销在 (z, y) = (−r sin(d), −r cos(d))（第 4 章）
    q = LK["d"] * DEG
    pz, py = -LK["r"] * math.sin(q), -LK["r"] * math.cos(q)
    tk_disc = cyl_x(X_TK + 3, X_TK + 9, 26)
    tk_pin = cyl_x(X_TK - 5, X_TK + 4, 3.0, y=py, z=pz)
    pulley = cyl_x(296, 316, 22) - cyl_x(299, 313, 24.5) + cyl_x(299, 313, 21)
    wheel = cyl_x(350, 368, 40) - cyl_x(349, 369, 33) + cyl_x(352, 366, 12)
    for k in range(5):
        a = k * 72 * DEG
        spoke = box(353, 365, -3, 3, 0, 34).rotate(bd.Axis.X, k * 72)
        wheel = wheel + spoke
    wheel = wheel + cyl_x(367, 371, 39)
    return shaft + disc + cw + pin + tk_disc + tk_pin + pulley + wheel


def needle_rod():
    """针杆连杆（局部原点在上端销孔，杆沿 −y，长 LN；网页按曲柄销与下销的连线转动）。"""
    L = LN
    prof = [(-7, 0), (7, 0), (4, -L), (-4, -L)]
    s = prism(prof, XN - 3, XN + 3)
    s = s + cyl_x(XN - 3, XN + 3, 8) + cyl_x(XN - 3, XN + 3, 5.5, y=-L)
    s = s - cyl_x(XN - 4, XN + 4, 3.3) - cyl_x(XN - 4, XN + 4, 2.4, y=-L)
    return s


def needle_bar():
    """针杆组件（局部原点在连杆下销处，上止点时；网页沿 y 平移 −xN(φ)）：针杆、连杆销座、针夹、机针。"""
    top = 22.0
    bar = cyl_y(-ROD_TO_CLAMP, top + 40, 3.6, x=XN)
    stud = box(XN - 4, XN + 4, -5, 5, -6, 6) + cyl_x(XN - 3, XN + 3, 2.4)
    clamp = cyl_y(-ROD_TO_CLAMP - 7, -ROD_TO_CLAMP + 4, 4.6, x=XN) + cyl_z(0, 7, 1.8, x=XN, y=-ROD_TO_CLAMP - 2)
    shank = cyl_y(-ROD_TO_CLAMP - 22, -ROD_TO_CLAMP - 6, 1.0, x=XN)
    blade = cyl_y(-ROD_TO_CLAMP - CLAMP_TO_TIP + 2.0, -ROD_TO_CLAMP - 21, 0.45, x=XN)
    point = bd.Pos(XN, -ROD_TO_CLAMP - CLAMP_TO_TIP, 0) * bd.Rot(-90, 0, 0) * bd.Cone(0.0, 0.45, 2.0, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    eye = box(XN - 1, XN + 1, -ROD_TO_CLAMP - CLAMP_TO_TIP + 2.0, -ROD_TO_CLAMP - CLAMP_TO_TIP + 3.2, -0.12, 0.12)
    needle = shank + blade + point - eye
    return bar + stud + clamp + needle


def takeup_lever():
    """挑线杆（四连杆的连杆；局部原点在曲柄销 P，局部 +z 指向 P→M；穿线孔 E 在离 P 为 c、偏 al 角处）。"""
    a, c, al = LK["a"], LK["c"], LK["al"] * DEG
    ez, ey = c * math.cos(al), c * math.sin(al)
    prof = [(-5, -6), (a, -5), (ez - 3, ey - 3.5), (ez + 2, ey - 2), (ez + 3, ey + 3), (ez - 4, ey + 3.5), (a, 5), (-5, 6)]
    s = prism(prof, X_TK - 2, X_TK + 2)
    s = s + cyl_x(X_TK - 2, X_TK + 2, 7) + cyl_x(X_TK - 2, X_TK + 2, 5, z=a)
    s = s - cyl_x(X_TK - 3, X_TK + 3, 3.1) - cyl_x(X_TK - 3, X_TK + 3, 2.2, z=a) - cyl_x(X_TK - 3, X_TK + 3, 1.3, y=ey, z=ez)
    return s


def takeup_link():
    """挑线连杆（四连杆的摇杆 Q–M；局部原点在机壳上的铰点 Q，局部 +z 指向 Q→M）。"""
    b = LK["b"]
    prof = [(-4, -4), (b, -3), (b, 3), (-4, 4)]
    s = prism(prof, X_TK + 2, X_TK + 6)
    s = s + cyl_x(X_TK + 2, X_TK + 6, 6) + cyl_x(X_TK + 2, X_TK + 6, 4.5, z=b)
    return s


def lower_shaft():
    """下轴组件（局部原点在下轴轴线上；绕 x 转 φ）：下轴、大齿轮（驱动旋梭轴）、同步带轮。"""
    s = cyl_x(20, 322, 6)
    gear = cyl_x(30, 40, 20.7)
    for k in range(36):
        gear = gear + box(30, 40, 20.2, 22.4, -1.1, 1.1).rotate(bd.Axis.X, k * 10)
    pulley = cyl_x(296, 316, 22) - cyl_x(299, 313, 24.5) + cyl_x(299, 313, 21)
    return s + gear + pulley


def hook():
    """旋梭组件（局部原点在旋梭轴线上；绕 x 转 2φ）：旋梭体、梭尖、梭轴、小齿轮。φ = 钩线时刻时梭尖在最上面（+y）。"""
    body_ = cyl_x(XN + 3.5, XN + 16, RH) - cyl_x(XN + 2.5, XN + 13, RH - 1.6)
    # 梭尖：一段沿外圆的楔形（梭尖在 +y，向“来”的方向伸出）
    tip = bd.Pos(XN + 2.2, 0, 0) * slab_tip()
    shaft = cyl_x(XN + 16, 40, 4)
    gear = cyl_x(30, 38, 10.3)
    for k in range(18):
        gear = gear + box(30, 38, 9.8, 11.9, -1.0, 1.0).rotate(bd.Axis.X, k * 20)
    return body_ + tip + shaft + gear


def slab_tip():
    """梭尖：沿外圆的一段楔形，尖端在角度 90°（+y），楔体在尖端后面（角度 > 90°）；旋梭顺时针转（从左端看），尖端在前。"""
    pts = [(0.0, RH + 0.25)]
    for k in range(2, 45):
        a = (90 + k) * DEG
        pts.append((RH * math.cos(a), RH * math.sin(a)))
    for k in range(44, 5, -1):
        a = (90 + k) * DEG
        r = RH - 2.4 + max(0, 6 - k) * 0.3
        pts.append((r * math.cos(a), r * math.sin(a)))
    return prism(pts, 0, 1.6)


def bobbin_case():
    """梭壳与梭芯（不转；被定位钩挡住）。局部原点在旋梭轴线上。"""
    case = cyl_x(XN + 3.2, XN + 13.5, 10.6) - cyl_x(XN + 2.5, XN + 12, 9.4)
    face = cyl_x(XN + 2.4, XN + 3.4, 10.6) + cyl_x(XN + 1.2, XN + 2.4, 3)
    latch = box(XN + 1.0, XN + 2.0, -1.5, 1.5, 3, 9)
    bob = cyl_x(XN + 4.5, XN + 12, 9.0) - cyl_x(XN + 5.5, XN + 11, 8.0) + cyl_x(XN + 5.5, XN + 11, 3.5)
    stop = box(XN + 6, XN + 10, RH + 0.5, RH + 3.5, -2, 2)
    return case + face + latch + bob, stop


def feed_dog():
    """送布牙与牙架（局部原点在牙齿尖平均高度、针前后中点；网页按第 6 章 X、Y 平移，X 沿 −z 为送布方向）。"""
    teeth = None
    for dx in (-3.5, 3.5):
        row = box(XN + dx - 0.9, XN + dx + 0.9, -2.2, -0.6, -8, 8)
        for k in range(7):
            z0 = -7 + k * 2.2
            t = prism([(z0, -0.6), (z0 + 2.2, -0.6), (z0 + 0.4, 0.0)], XN + dx - 0.9, XN + dx + 0.9)
            row = row + t
        teeth = row if teeth is None else teeth + row
    carrier = box(XN - 6, XN + 6, -9, -2.2, -10, 10) + box(XN - 6, 60, -12, -6, 18, 26) + box(XN - 6, XN + 6, -12, -6, 8, 26)
    return teeth + carrier


def belt():
    """同步带（静止画出，网页让它的纹理移动）。"""
    r = 22.5
    pts_out, pts_in = [], []
    s = None
    for y0, y1 in ((YL, HS),):
        left = box(304, 308, y0, y1, -r - 1.5, -r)
        right = box(304, 308, y0, y1, r, r + 1.5)
        s = left + right
    for yc in (HS, YL):
        ring = cyl_x(304, 308, r + 1.5) - cyl_x(303, 309, r)
        half = ring - (box(300, 312, yc - 40 if yc == HS else yc, yc if yc == HS else yc + 40, -40, 40))
        s = s + bd.Pos(0, yc, 0) * (ring - box(300, 312, -40 if yc == HS else 0, 0 if yc == HS else 40, -40, 40))
    return s


def table():
    """台板（木质）：机壳底板嵌在台板的开口里，底板顶面与台板面齐平。"""
    t = box(-330, 560, -38, 0, -300, 230)
    t = t - box(-133, 373, -40, 1, -98, 88)
    try:
        t = bd.fillet(t.edges().filter_by(bd.Axis.Y), 30)
    except Exception:
        pass
    return t


def thread_stand():
    """线架与线团（装在台板后部）。线从线团上方的导线钩引出（见网页的穿线路线）。"""
    pole = cyl_y(0, 340, 4, x=330, z=-200)
    base = cyl_y(0, 8, 22, x=330, z=-200)
    arm = cyl_z(-200, -70, 3, x=330, y=332)
    hookp = cyl_y(322, 340, 3, x=330, z=-70)
    pin = cyl_y(0, 60, 3, x=330, z=-160)
    return pole + base + arm + hookp + pin


def spool():
    core = cyl_y(6, 66, 13, x=330, z=-160)
    flange = cyl_y(4, 8, 22, x=330, z=-160) + cyl_y(64, 68, 16, x=330, z=-160)
    return core + flange


# =====================================================================================
# 编号表（虚拟样机、拆装手册、透明件印字共用）
# =====================================================================================
PARTS = [
    # code, key, zh, en, group, material, moving-kind
    ("F-01", "body", "机壳（底板、立柱、横臂、机头）", "Machine frame (bed, pillar, arm, head)", "frame", "paint", "static"),
    ("F-02", "face", "面板", "Face plate", "frame", "paint", "cover"),
    ("F-03", "top", "顶盖", "Top cover", "frame", "paint", "cover"),
    ("F-04", "rear", "后盖", "Rear cover", "frame", "paint", "cover"),
    ("F-05", "plate", "针板", "Needle plate", "frame", "plate", "static"),
    ("F-06", "slide", "推板", "Slide plate", "frame", "plate", "static"),
    ("F-07", "bush", "轴套", "Bushings", "frame", "brass", "static"),
    ("F-08", "panes", "开窗透明板", "Window panes", "frame", "pc", "window"),
    ("F-09", "details", "针距调节器、倒缝扳手、抬压脚扳手", "Stitch-length dial, reverse lever, presser lifter", "frame", "steel", "static"),
    ("F-10", "oil", "油窗", "Oil sight window", "frame", "glass", "static"),
    ("N-01", "upper", "上轴、针杆曲柄与平衡块", "Main shaft, needle-bar crank and counterweight", "needle", "steel", "upper"),
    ("N-02", "rod", "针杆连杆", "Needle-bar connecting rod", "needle", "steel", "rod"),
    ("N-03", "nbar", "针杆、针夹与机针", "Needle bar, clamp and needle", "needle", "chrome", "nbar"),
    ("N-04", "presser", "压脚杆与压脚", "Presser bar and foot", "needle", "chrome", "static"),
    ("T-01", "tklever", "挑线杆", "Thread take-up lever", "takeup", "chrome", "tklever"),
    ("T-02", "tklink", "挑线连杆", "Take-up link", "takeup", "steel", "tklink"),
    ("T-03", "tension", "夹线器", "Thread tension assembly", "takeup", "chrome", "static"),
    ("T-04", "guide", "过线件", "Thread guides", "takeup", "chrome", "static"),
    ("H-01", "lower", "下轴与大齿轮", "Lower shaft and gear", "hook", "steel", "lower"),
    ("H-02", "hook", "旋梭（含梭尖、梭轴、小齿轮）", "Rotary hook (point, shaft, pinion)", "hook", "hook", "hook"),
    ("H-03", "bcase", "梭壳与梭芯", "Bobbin case and bobbin", "hook", "dark", "bcase"),
    ("H-04", "bstop", "梭壳定位钩", "Bobbin-case stop", "hook", "steel", "bcase"),
    ("D-01", "dog", "送布牙与牙架", "Feed dog and carrier", "feed", "dark", "dog"),
    ("S-01", "belt", "同步带", "Timing belt", "drive", "rubber", "static"),
    ("X-01", "table", "台板", "Table top", "frame", "wood", "static"),
    ("X-02", "stand", "线架", "Thread stand", "frame", "steel", "static"),
    ("X-03", "spool", "面线线团", "Upper-thread spool", "frame", "spool", "static"),
]


def build():
    out = {}
    out["body"] = body(False)
    out["body_cut"] = body(True)
    out["face"], out["top"], out["rear"] = covers()
    out["details"], out["oil"] = details()
    out["table"] = table()
    out["stand"] = thread_stand()
    out["spool"] = spool()
    p = window_panes()
    panes = p[0]
    for q in p[1:]:
        panes = panes + q
    out["panes"] = panes
    out["plate"], out["slide"] = plates()
    out["bush"] = bushings()
    out["presser"] = presser()
    out["tension"], out["guide"] = tension_unit()
    out["upper"] = upper_shaft()
    out["rod"] = needle_rod()
    out["nbar"] = needle_bar()
    out["tklever"] = takeup_lever()
    out["tklink"] = takeup_link()
    out["lower"] = lower_shaft()
    out["hook"] = hook()
    out["bcase"], out["bstop"] = bobbin_case()
    out["dog"] = feed_dog()
    out["belt"] = belt()
    return out


def mesh(shape, tol, ang):
    vs, ts = [], []
    for face in shape.faces():
        try:
            v, t = face.tessellate(tol, ang)
        except Exception:
            continue
        base = len(vs)
        vs.extend((p.X, p.Y, p.Z) for p in v)
        ts.extend((base + a, base + b, base + c) for a, b, c in t)
    return vs, ts


def pack(shapes, tol=0.25, ang=0.35):
    res = {}
    for key, shp in shapes.items():
        if shp is None:
            continue
        fine = key in ("nbar", "hook", "dog", "bcase", "tklever", "rod")
        vs, ts = mesh(shp, 0.05 if fine else tol, 0.25 if fine else ang)
        va = array("f", [c for v in vs for c in v])
        ia = array("I" if len(vs) > 65535 else "H", [i for t in ts for i in t])
        res[key] = {"v": base64.b64encode(va.tobytes()).decode(), "i": base64.b64encode(ia.tobytes()).decode(),
                    "i32": len(vs) > 65535, "nv": len(vs), "nt": len(ts)}
    return res


if __name__ == "__main__":
    shapes = build()
    data = {"meta": {"HS": HS, "YH": YH, "YL": YL, "XN": XN, "X_TK": X_TK, "RH": RH, "TIP_TDC": TIP_TDC,
                     "ROD_TO_CLAMP": ROD_TO_CLAMP, "CLAMP_TO_TIP": CLAMP_TO_TIP, "LK": LK},
            "parts": [dict(zip(("code", "key", "zh", "en", "group", "mat", "kind"), p)) for p in PARTS],
            "mesh": pack(shapes)}
    js = "/* 平缝机虚拟样机的网格（models/proto_lockstitch.py 生成，勿手改） */\nwindow.WQLS_MESH=" + json.dumps(data, separators=(",", ":")) + ";\n"
    open(sys.argv[1], "w").write(js)
    tot = sum(m["nt"] for m in data["mesh"].values())
    print("triangles", tot, "bytes", len(js), {k: m["nt"] for k, m in data["mesh"].items()})
