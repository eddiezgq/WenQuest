# -*- coding: utf-8 -*-
"""A 部分自写生成器（第 5 轮 P7）：尺寸取本族规格表（带出处），build123d 造型，返回 [(节点名, 形体)]（毫米，Z 向上）。

engine 写成 wenquest:<造型名>：
    spring_washer  弹簧垫圈 GB/T 93          taper_pin  圆锥销 GB/T 117（A 型，锥度 1:50）
    lip_seal       骨架油封 GB/T 13871.1     hex_plug   外六角带肩螺塞 DIN 910
外形是按标准外形尺寸的简化造型（不画螺纹、弹簧垫圈不画扭曲），用于装配、网页预览和课件插图。
"""
from build123d import Axis, Box, Cone, Cylinder, Pos, RegularPolygon, Rot, extrude


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


BUILDERS = {"spring_washer": spring_washer, "taper_pin": taper_pin, "lip_seal": lip_seal, "hex_plug": hex_plug}


def build(entry, row):
    return BUILDERS[entry["model"]["engine"].split(":")[1]](row)
