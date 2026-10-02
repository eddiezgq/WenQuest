"""算例 7.7.2、7.7.3：AGV 车轮轮缘上一点的轨迹（摆线）；激光雷达的极坐标扫描点求墙面方向。"""
import math

import numpy as np

from bookout import out

# 算例 7.7.2：轮半径 R = 0.1 m，车速 v = 1 m/s，轮转角 φ = vt/R
R, v = 0.1, 1.0
phi = math.pi / 2
dxdt = v * (1 - math.cos(phi))
dydt = v * math.sin(phi)
out(dxdt=dxdt, dydt=dydt, speed=math.hypot(dxdt, dydt), slope=dydt / dxdt, rpm=v / R * 60 / (2 * math.pi), omega=v / R)

# 算例 7.7.3：一面直墙，到雷达的距离 d = 2 m，墙的法线方向 φ0 = 20°；极坐标方程 r = d / cos(φ − φ0)
d, phi0 = 2.0, math.radians(20)
r = lambda p: d / math.cos(p - phi0)
dr = lambda p: d * math.sin(p - phi0) / math.cos(p - phi0) ** 2
p = 0.0
slope = (dr(p) * math.sin(p) + r(p) * math.cos(p)) / (dr(p) * math.cos(p) - r(p) * math.sin(p))
ang = math.degrees(math.atan2(dr(p) * math.sin(p) + r(p) * math.cos(p), dr(p) * math.cos(p) - r(p) * math.sin(p)))
# 用扫描点估计墙的方向。测距误差假设在 ±10 mm 以内（均匀分布）；比较相隔 1、20、40 束激光的两点
rng = np.random.default_rng(7)
res = math.radians(0.5)
def estimate(k):
    p1, p2 = -k * res / 2, k * res / 2
    r1, r2 = r(p1) + rng.uniform(-0.01, 0.01), r(p2) + rng.uniform(-0.01, 0.01)
    P1 = np.array([r1 * math.cos(p1), r1 * math.sin(p1)])
    P2 = np.array([r2 * math.cos(p2), r2 * math.sin(p2)])
    gap = math.hypot(*(np.array([r(p2) * math.cos(p2), r(p2) * math.sin(p2)]) - np.array([r(p1) * math.cos(p1), r(p1) * math.sin(p1)])))
    return math.degrees(math.atan2(*(P2 - P1)[::-1])), gap
e1, g1 = estimate(1)
e20, g20 = estimate(20)
e40, g40 = estimate(40)
out(r0=r(0), dr0=dr(0), wall_slope=slope, wall_deg=ang, est_adj=e1, est_20=e20, est_40=e40,
    gap1_mm=g1 * 1000, gap20_mm=g20 * 1000, gap40_mm=g40 * 1000)
