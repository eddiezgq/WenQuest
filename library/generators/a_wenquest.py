# -*- coding: utf-8 -*-
"""A 部分自写生成器（第 5 轮 P7）：尺寸取本族规格表（带出处），build123d 造型，返回 [(节点名, 形体)]（毫米，Z 向上）。

engine 写成 wenquest:<造型名>：
    spring_washer  弹簧垫圈 GB/T 93          taper_pin  圆锥销 GB/T 117（A 型，锥度 1:50）
    lip_seal       骨架油封 GB/T 13871.1     hex_plug   外六角带肩螺塞 DIN 910
    ball_screw     滚珠丝杠副 SFU            linear_guide 直线导轨副 HG 型
    timing_pulley  同步带轮 GT2/HTD          jaw_coupling 梅花形弹性联轴器 LM
    compression_spring 圆柱螺旋压缩弹簧 YA 型（第 5 轮第 5 步）
外形是按标准外形尺寸的简化造型（不画螺纹、弹簧垫圈不画扭曲），用于装配、网页预览和课件插图。
"""
import math

from build123d import Axis, Box, Circle, Cone, Cylinder, Pos, RegularPolygon, Rot, extrude


def _ring(r_out, r_in, h):
    return Cylinder(r_out, h, align=None) - Cylinder(r_in, h * 1.01, align=None)


def spring_washer(row):
    """圆环截面 b×s，开一个斜口；高度方向沿 Z，底面在 z=0"""
    d, s = float(row["d_min_mm"]), float(row["s_mm"])
    r_in, r_out = d / 2, d / 2 + s
    ring = Pos(0, 0, s / 2) * _ring(r_out, r_in, s)
    gap = Pos(r_in + s / 2, 0, s / 2) * Rot(0, 0, 0) * Box(s * 1.6, max(0.3, 0.45 * s), s * 1.2)
    gap = gap.rotate(Axis((r_in + s / 2, 0, s / 2), (0, 1, 0)), 25)      # 斜口
    return [("washer", ring - gap)]


def taper_pin(row):
    """小端直径 d，锥度 1:50，长 l；两端倒圆近似为倒角 a"""
    d, l = float(row["d_mm"]), float(row["l_mm"])
    D = d + l / 50
    return [("pin", Pos(0, 0, l / 2) * Cone(D / 2, d / 2, l))]


def lip_seal(row):
    """外骨架环 + 顶部腹板 + 向下收口的唇口，按 d1×D×b"""
    d1, D, b = float(row["d1_mm"]), float(row["D_mm"]), float(row["b_mm"])
    w = (D - d1) / 2
    shell = Pos(0, 0, b / 2) * _ring(D / 2, D / 2 - 0.22 * w, b)
    web = Pos(0, 0, b - 0.12 * b) * _ring(D / 2 - 0.1 * w, d1 / 2 + 0.28 * w, 0.24 * b)
    lip_h = 0.75 * b
    lip = Pos(0, 0, lip_h / 2 + 0.02 * b) * (Cone(d1 / 2 + 0.12 * w, d1 / 2 + 0.3 * w, lip_h)
                                             - Cone(d1 / 2 - 0.001, d1 / 2 + 0.2 * w, lip_h * 1.01))
    spring = Pos(0, 0, 0.35 * b) * _ring(d1 / 2 + 0.26 * w, d1 / 2 + 0.16 * w, 0.14 * b)
    return [("case", shell + web), ("lip", lip), ("spring", spring)]


def hex_plug(row):
    """螺纹段（不画螺纹）+ 肩（密封面）+ 外六角头；螺纹端在 z=0"""
    d, dk, c, i, m, s = (float(row[k]) for k in ("d_mm", "d2_mm", "c_mm", "i_mm", "m_mm", "s_mm"))
    thread = Pos(0, 0, i / 2) * Cylinder(d / 2, i)
    collar = Pos(0, 0, i + c / 2) * Cylinder(dk / 2, c)
    head = Pos(0, 0, i + c) * extrude(RegularPolygon(s / 2, 6, major_radius=False), m)
    return [("plug", thread + collar + head)]


def _f(row, k, default=None):
    v = row.get(k)
    return default if v in (None, "") else float(v)


def ball_screw(row):
    """丝杠（光轴示意，不画滚道）+ 法兰螺母（DIN 69051 B 型：圆柱本体、带两切边的法兰、法兰孔）；法兰端面 z=0，螺母向 +Z"""
    d0, D, L, D1, L1 = (_f(row, k) for k in ("d0_mm", "D_mm", "L_mm", "D1_mm", "L1_mm"))
    D5, X, W = _f(row, "D5_mm"), _f(row, "X_mm"), _f(row, "W_mm")
    n = int(_f(row, "n_holes", 6))
    shaft_len = 3 * L + 2 * d0
    screw = Pos(0, 0, L / 2) * Cylinder(d0 / 2, shaft_len)
    body = Pos(0, 0, L / 2) * Cylinder(D / 2, L)
    flange = Pos(0, 0, L1 / 2) * Cylinder(D1 / 2, L1)
    if W and W < D1:                                     # 两侧切边
        for sgn in (-1, 1):
            flange -= Pos(0, sgn * (W / 2 + D1 / 2), L1 / 2) * Box(D1 * 1.2, D1, L1 * 1.1)
    if D5 and X:
        for i in range(n):
            a = math.radians(360 / n * i + 90 / n * (n % 2 == 0))
            flange -= Pos(D5 / 2 * math.cos(a), D5 / 2 * math.sin(a), L1 / 2) * Cylinder(X / 2, L1 * 1.2)
    nut = (body + flange) - Pos(0, 0, L / 2) * Cylinder(d0 / 2 * 1.02, L * 1.1)
    return [("screw", screw), ("nut", nut)]


def linear_guide(row):
    """导轨（矩形截面 + 沉头孔）+ 滑块（本体开槽跨在导轨上，两端端盖）；导轨底面 z=0，沿 X"""
    WR, HR, P, E = (_f(row, k) for k in ("rail_W_mm", "rail_H_mm", "rail_pitch_mm", "rail_E_mm"))
    H, H1, W, L1, L = (_f(row, k) for k in ("H_mm", "H1_mm", "W_mm", "L1_mm", "L_mm"))
    d, Dc, hc = _f(row, "rail_d_mm"), _f(row, "rail_D_mm"), _f(row, "rail_h_mm")
    nh = max(3, math.ceil((2.5 * L) / P))
    rail_len = (nh - 1) * P + 2 * E
    rail = Pos(0, 0, HR / 2) * Box(rail_len, WR, HR)
    for i in range(nh):
        x = -rail_len / 2 + E + i * P
        if d:
            rail -= Pos(x, 0, HR / 2) * Cylinder(d / 2, HR * 1.1)
        if Dc and hc:
            rail -= Pos(x, 0, HR - hc / 2 + 0.01) * Cylinder(Dc / 2, hc + 0.02)
    bh = H - H1
    body = Pos(0, 0, H1 + bh / 2) * Box(L1, W, bh)
    slot_h = HR - H1 + 0.3
    body -= Pos(0, 0, H1 + slot_h / 2 - 0.01) * Box(L1 * 1.1, WR + 0.6, slot_h + 0.02)
    caps = None
    cap_len = (L - L1) / 2
    if cap_len > 0.1:
        for sgn in (-1, 1):
            c = Pos(sgn * (L1 / 2 + cap_len / 2), 0, H1 + bh / 2 - 0.05 * bh) * Box(cap_len, W * 0.96, bh * 0.9)
            c -= Pos(sgn * (L1 / 2 + cap_len / 2), 0, H1 + slot_h / 2 - 0.01) * Box(cap_len * 1.1, WR + 0.6, slot_h + 0.02)
            caps = c if caps is None else caps + c
    return [("rail", rail), ("block", body + caps if caps is not None else body)]


def timing_pulley(row):
    """齿圈（齿顶圆 OD，z 个圆弧轮槽）+ 两侧挡边 + 一侧轮毂 + 轴孔；轮毂端面 z=0"""
    z, b, OD = int(_f(row, "z")), _f(row, "b_mm"), _f(row, "OD_mm")
    gd, gr = _f(row, "groove_depth_mm"), _f(row, "groove_r_mm")
    flange_t = max(1.0, 0.08 * b)
    flange_r = OD / 2 + max(1.5, 0.6 * gd + 1)
    hub_d = max(8.0, min(0.75 * (OD - 2 * gd), OD - 2 * gd - 2))
    hub_l = max(6.0, 0.8 * b)
    bore = max(3.0, round(0.35 * hub_d))
    prof = Circle(OD / 2)
    rc = OD / 2 - gd + gr                                # 轮槽圆弧中心半径：槽底在 OD/2 − 槽深
    for i in range(z):
        a = 2 * math.pi * i / z
        prof -= Pos(rc * math.cos(a), rc * math.sin(a)) * Circle(gr)
    z0 = hub_l
    teeth = Pos(0, 0, z0 + flange_t) * extrude(prof, b)
    f1 = Pos(0, 0, z0 + flange_t / 2) * Cylinder(flange_r, flange_t)
    f2 = Pos(0, 0, z0 + flange_t + b + flange_t / 2) * Cylinder(flange_r, flange_t)
    hub = Pos(0, 0, hub_l / 2) * Cylinder(hub_d / 2, hub_l)
    total = hub_l + 2 * flange_t + b
    body = (teeth + f1 + f2 + hub) - Pos(0, 0, total / 2) * Cylinder(bore / 2, total * 1.1)
    return [("pulley", body)]


def jaw_coupling(row):
    """两个半联轴器（轮毂 + 三个凸爪）+ 梅花弹性件；外径 D、总长 L0、轴孔长 L"""
    D, L0, L = _f(row, "D_mm"), _f(row, "L0_mm"), _f(row, "L_mm")
    dmin = _f(row, "d_min_mm", 0.25 * D)
    gap = L0 - 2 * L                                     # 两轮毂端面之间：凸爪与弹性件
    jaw_h = 0.85 * gap
    bore = dmin
    hub_r = D / 2
    lower = Pos(0, 0, L / 2) * Cylinder(hub_r, L)
    upper = Pos(0, 0, L0 - L / 2) * Cylinder(hub_r, L)
    for i in range(3):
        lower += Pos(0, 0, L + jaw_h / 2) * Rot(0, 0, 120 * i) * Pos(0.3 * D, 0, 0) * Box(0.3 * D, 0.34 * D, jaw_h)
        upper += Pos(0, 0, L0 - L - jaw_h / 2) * Rot(0, 0, 120 * i + 60) * Pos(0.3 * D, 0, 0) * Box(0.3 * D, 0.34 * D, jaw_h)
    clip = Pos(0, 0, L0 / 2) * Cylinder(hub_r, L0)
    lower, upper = lower & clip, upper & clip
    lower -= Pos(0, 0, L / 2) * Cylinder(bore / 2, L * 1.1)
    upper -= Pos(0, 0, L0 - L / 2) * Cylinder(bore / 2, L * 1.1)
    spider = Pos(0, 0, L0 / 2) * Cylinder(0.43 * D, gap * 0.9)          # 比外径小一圈，凸爪与弹性件交替看得见
    spider -= lower
    spider -= upper
    spider -= Pos(0, 0, L0 / 2) * Cylinder(0.16 * D, gap)
    return [("hub_1", lower), ("hub_2", upper), ("spider", spider)]


def compression_spring(row):
    """螺旋线扫掠圆截面：两端各一圈并紧（节距 = d），中间 n 圈等节距；两端磨平到 z=0 与 z=H0"""
    from build123d import Helix, Plane, Wire, sweep
    d, D, H0, n = (_f(row, k) for k in ("d_mm", "D_mm", "H0_mm", "n"))
    r = D / 2
    p_act = max(d * 1.05, (H0 - 2 * d) / n)              # 中间圈节距（两端并紧圈各占约 d）
    end = Helix(d, d, r)
    mid = Pos(0, 0, d) * Helix(p_act, p_act * n, r)
    top = Pos(0, 0, d + p_act * n) * Helix(d, d, r)
    # 三段螺旋线首尾相接（各段起点都在 +X 方向；中间段圈数取整到半圈时旋转对齐）
    turns_mid = n
    top = top.rotate(Axis.Z, 360 * (turns_mid % 1))
    path = Wire([end, mid, top])
    start = path @ 0
    tangent = path % 0
    sec = Plane(origin=start, z_dir=tangent) * Circle(d / 2)
    coil = sweep(sec, path)
    total = d + p_act * n + d
    keep = Pos(0, 0, total / 2) * Box(D + 2 * d, D + 2 * d, total - 0.5 * d)      # 两端磨平各磨去约 d/4
    coil = coil & keep
    return [("spring", Pos(0, 0, -0.25 * d) * coil)]


BUILDERS = {"spring_washer": spring_washer, "taper_pin": taper_pin, "lip_seal": lip_seal, "hex_plug": hex_plug,
            "ball_screw": ball_screw, "linear_guide": linear_guide, "timing_pulley": timing_pulley,
            "jaw_coupling": jaw_coupling, "compression_spring": compression_spring}


def build(entry, row):
    return BUILDERS[entry["model"]["engine"].split(":")[1]](row)
