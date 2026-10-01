# -*- coding: utf-8 -*-
"""厂商产品的外形代用模型（第 5 轮 P3）：按样本上的外形尺寸生成简化外形，不是厂商模型。
engine: proxy:<外形>   strain_wave = 谐波减速器杯型组件（刚轮 + 柔轮杯 + 输出法兰毂）"""
from build123d import Cylinder, Pos


def _ring(r_out, r_in, h):
    return Cylinder(r_out, h) - Cylinder(r_in, h * 1.01)


def strain_wave(row):
    D, L = float(row["OD_mm"]), float(row["L_mm"])
    cs_h = 0.3 * L                                          # 刚轮（外齿圈）宽度
    circular = Pos(0, 0, L - cs_h / 2) * _ring(D / 2, 0.36 * D, cs_h)
    cup_r = 0.35 * D
    cup = Pos(0, 0, L / 2) * _ring(cup_r, cup_r - max(0.6, 0.02 * D), L)          # 柔轮（薄壁杯）
    bottom = Pos(0, 0, 0.04 * L) * Cylinder(cup_r, 0.08 * L)                       # 杯底（膜片）
    hub = Pos(0, 0, -0.06 * L) * _ring(0.2 * D, 0.08 * D, 0.12 * L)               # 输出法兰毂
    return [("circular_spline", circular), ("flexspline", cup + bottom + hub)]


BUILDERS = {"strain_wave": strain_wave}


def build(entry, row):
    return BUILDERS[entry["model"]["engine"].split(":")[1]](row)
