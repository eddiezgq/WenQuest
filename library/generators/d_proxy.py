# -*- coding: utf-8 -*-
"""厂商产品的外形代用模型（第 5 轮 P3）：按样本上的外形尺寸生成简化外形，不是厂商模型。
engine: proxy:<外形>   strain_wave = 谐波减速器杯型组件（刚轮 + 柔轮杯 + 输出法兰毂）"""
from build123d import Cylinder, Pos


def _ring(r_out, r_in, h):
    return Cylinder(r_out, h) - Cylinder(r_in, h * 1.01)


def _dims(entry, row):
    return {k: float(row[col]) for k, col in (entry["model"].get("dims") or {}).items() if row.get(col) not in (None, "")}


def strain_wave(row, g):
    D, L = g["d"], g["h"]
    cs_h = 0.3 * L                                          # 刚轮（外齿圈）宽度
    circular = Pos(0, 0, L - cs_h / 2) * _ring(D / 2, 0.36 * D, cs_h)
    cup_r = 0.35 * D
    cup = Pos(0, 0, L / 2) * _ring(cup_r, cup_r - max(0.6, 0.02 * D), L)          # 柔轮（薄壁杯）
    bottom = Pos(0, 0, 0.04 * L) * Cylinder(cup_r, 0.08 * L)                       # 杯底（膜片）
    hub = Pos(0, 0, -0.06 * L) * _ring(0.2 * D, 0.08 * D, 0.12 * L)               # 输出法兰毂
    return [("circular_spline", circular), ("flexspline", cup + bottom + hub)]


def box(row, g):
    """长方体：w（宽，X）× d（深，Y）× h（高，Z），底面在 z=0"""
    from build123d import Box
    return [("body", Pos(0, 0, g["h"] / 2) * Box(g["w"], g["d"], g["h"]))]


def cylinder(row, g):
    """圆柱：直径 d × 高 h，底面在 z=0"""
    return [("body", Pos(0, 0, g["h"] / 2) * Cylinder(g["d"] / 2, g["h"]))]


def gripper(row, g):
    """平行夹爪示意：本体 + 两指；w = 张开时总宽，h = 总高（安装面到指尖），d = 厚度（没有时按宽的 0.35）"""
    from build123d import Box
    W, H = g["w"], g["h"]
    D = g.get("d") or 0.35 * W
    body_h = 0.55 * H
    body = Pos(0, 0, body_h / 2) * Box(0.62 * W, D, body_h)
    fw, rail_h = 0.12 * W, 0.08 * H
    rail = Pos(0, 0, body_h + rail_h / 2) * Box(W, 0.7 * D, rail_h)                 # 手指滑轨
    top = body_h + rail_h
    fingers = [Pos(s * (W / 2 - fw / 2), 0, top + (H - top) / 2) * Box(fw, 0.6 * D, H - top) for s in (-1, 1)]
    return [("body", body + rail), ("finger_left", fingers[0]), ("finger_right", fingers[1])]


BUILDERS = {"strain_wave": strain_wave, "box": box, "cylinder": cylinder, "gripper": gripper}


def build(entry, row):
    return BUILDERS[entry["model"]["engine"].split(":")[1]](row, _dims(entry, row))
