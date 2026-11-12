# -*- coding: utf-8 -*-
"""平面连杆机构的位置、速度、加速度（第 138 轮 G4.6，缝纫机送布、抬牙机构用）。

做法：按杆组（Assur 组）逐个求位置——
  crank(O, r, θ)                 曲柄（或偏心）端点；
  rrr(A, la, B, lb, near)        RRR 组：已知两端铰点 A、B 和两杆长，求中间铰点（两圆交点，取靠近 near 的那一个，保证一转里连续）；
  rrp(A, la, G, u, near)         RRP 组：中间铰点在过 G、方向 u 的导路（滑槽）上，到 A 的距离为 la；
  rotate_about(P, O, ang)        刚体上点绕 O 转动。
一转按等间隔角度逐点求解，速度、加速度用周期中心差分（角速度 ω 给定时乘 ω、ω²）。
单位：mm、rad；平面坐标 (u, v) 用元组或 numpy 数组。
"""
from __future__ import annotations

import math

import numpy as np


def crank(O, r, theta):
    return (O[0] + r * math.cos(theta), O[1] + r * math.sin(theta))


def _circles(A, ra, B, rb):
    dx, dy = B[0] - A[0], B[1] - A[1]
    d = math.hypot(dx, dy)
    if d < 1e-12 or d > ra + rb + 1e-9 or d < abs(ra - rb) - 1e-9:
        raise ValueError(f"装不上：两铰点相距 {d:.4f}，杆长 {ra:.4f}、{rb:.4f}")
    a = (ra * ra - rb * rb + d * d) / (2 * d)
    h = math.sqrt(max(ra * ra - a * a, 0.0))
    mx, my = A[0] + a * dx / d, A[1] + a * dy / d
    return (mx + h * dy / d, my - h * dx / d), (mx - h * dy / d, my + h * dx / d)


def rrr(A, la, B, lb, near):
    """两圆交点里靠近 near 的那一个"""
    p1, p2 = _circles(A, la, B, lb)
    return p1 if math.dist(p1, near) <= math.dist(p2, near) else p2


def rrp(A, la, G, u, near):
    """导路 G + s·u（u 为单位向量）上、到 A 距离为 la 的点，取靠近 near 的那一个；同时返回 s"""
    ux, uy = u
    wx, wy = G[0] - A[0], G[1] - A[1]
    b = 2 * (wx * ux + wy * uy)
    c = wx * wx + wy * wy - la * la
    disc = b * b - 4 * c
    if disc < -1e-9:
        raise ValueError("装不上：导路离铰点太远")
    sq = math.sqrt(max(disc, 0.0))
    best = None
    for s in ((-b + sq) / 2, (-b - sq) / 2):
        P = (G[0] + s * ux, G[1] + s * uy)
        if best is None or math.dist(P, near) < math.dist(best[0], near):
            best = (P, s)
    return best


def angle(O, P):
    return math.atan2(P[1] - O[1], P[0] - O[0])


def rotate_about(P, O, ang):
    c, s = math.cos(ang), math.sin(ang)
    x, y = P[0] - O[0], P[1] - O[1]
    return (O[0] + c * x - s * y, O[1] + s * x + c * y)


def unwrap_angle(a):
    return np.unwrap(np.asarray(a, float))


def derivatives(y, dphi, omega=1.0):
    """一转等间隔采样（周期）的一阶、二阶中心差分，对时间：乘 ω、ω²（ω 单位 rad/s 时得 mm/s、mm/s²）"""
    y = np.asarray(y, float)
    v = (np.roll(y, -1, axis=0) - np.roll(y, 1, axis=0)) / (2 * dphi) * omega
    a = (np.roll(y, -1, axis=0) - 2 * y + np.roll(y, 1, axis=0)) / dphi ** 2 * omega ** 2
    return v, a


def slider_crank_x(r, l, theta, e=0.0):
    """对心 / 偏置曲柄滑块的滑块位置（解析解，测试用）：x = r cosθ + √(l² − (r sinθ − e)²)"""
    return r * np.cos(theta) + np.sqrt(l * l - (r * np.sin(theta) - e) ** 2)


def fourbar_output(a, b, c, d, theta2, cross=False):
    """四连杆（机架 d、曲柄 a、连杆 b、摇杆 c）摇杆转角的 Freudenstein 解析解（测试用）"""
    K1, K2, K3 = d / a, d / c, (a * a - b * b + c * c + d * d) / (2 * a * c)
    A = math.cos(theta2) - K1 - K2 * math.cos(theta2) + K3
    B = -2 * math.sin(theta2)
    C = K1 - (K2 + 1) * math.cos(theta2) + K3
    disc = math.sqrt(B * B - 4 * A * C)
    return 2 * math.atan2(-B + (disc if cross else -disc), 2 * A)
