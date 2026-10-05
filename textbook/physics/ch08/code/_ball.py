"""第 8 章：网球发球机器人的模型（与算例 8.1.1 相同），供 8.2–8.4 节的程序共用。"""
import math

import numpy as np

from constants import g
from _ode import STEPS as STEP

m, D, Cd, rho = 0.058, 0.067, 0.55, 1.20
k = 0.5 * rho * Cd * math.pi * D * D / 4 / m
v0, th, y0 = 25.0, math.radians(10.0), 1.0
S0 = np.array([0.0, y0, v0 * math.cos(th), v0 * math.sin(th)])


def f(t, s):
    x, y, vx, vy = s
    v = math.hypot(vx, vy)
    return np.array([vx, vy, -k * v * vx, -g - k * v * vy])


def acc(t, x, v):
    return np.array([-k * np.hypot(*v) * v[0], -g - k * np.hypot(*v) * v[1]])


def landing(h, method="rk4", s0=None):
    """落地点的 x（在落地前后两步之间用三次插值）。一直积分到 y < 0；60 s 内不落地就报错。"""
    s = np.array(S0 if s0 is None else s0, float)
    prev, n = s, 0
    while s[1] >= 0:
        prev = s
        if method == "semi":
            v = s[2:] + h * acc(0, s[:2], s[2:])
            s = np.concatenate([s[:2] + h * v, v])
        else:
            s = STEP[method](f, 0, s, h)
        n += 1
        if n * h > 60:
            raise RuntimeError("60 s 内没有落地")
    return _cross(prev, s, h)


def _herm(p0, d0, p1, d1, s, h):
    """三次埃尔米特插值：两端的值 p 与导数 d（对时间），s ∈ [0, 1]。误差 O(h⁴)，不掩盖 RK4 的四阶。"""
    h00, h10, h01, h11 = 2 * s**3 - 3 * s**2 + 1, s**3 - 2 * s**2 + s, -2 * s**3 + 3 * s**2, s**3 - s**2
    return h00 * p0 + h10 * h * d0 + h01 * p1 + h11 * h * d1


def _cross(a, b, h):
    """在相邻两步 a、b 之间求 y = 0 处的 x（状态为 x, y, vx, vy，用速度作导数）。"""
    lo, hi = 0.0, 1.0                                          # 二分法求插值曲线上 y = 0 的位置
    for _ in range(60):
        mid = (lo + hi) / 2
        if _herm(a[1], a[3], b[1], b[3], mid, h) > 0: lo = mid
        else: hi = mid
    s = (lo + hi) / 2
    return _herm(a[0], a[2], b[0], b[2], s, h)
