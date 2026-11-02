"""20.1 节：向量范数。AGV 沿 50 m 的路径行驶，每 5 cm 记录一次横向偏差（1000 个数）：两种控制器的 1-、2-、∞-范数；
范数的等价不等式；1-范数不满足平行四边形法则；位姿误差的加权范数。"""
import math

import numpy as np

from bookout import out, vec

n = 1000
s = np.arange(n) * 0.05                          # 路程，m
rng = np.random.default_rng(2001)
# 控制器 A：跟踪紧，随机偏差约 4 mm，但在地面接缝（s = 31 m）处被颠出一个 26 mm 的尖峰
eA = 4.0 * rng.standard_normal(n) + 26.0 * np.exp(-((s - 31.0) / 0.25) ** 2)
# 控制器 B：比较“软”，偏差是幅度 8 mm 的缓慢摆动，没有尖峰
eB = 8.0 * np.sin(2 * math.pi * s / 7.0) + 1.0 * rng.standard_normal(n)


def norms(e):
    return np.sum(np.abs(e)), np.linalg.norm(e), np.max(np.abs(e))


n1A, n2A, niA = norms(eA)
n1B, n2B, niB = norms(eB)
out(n=n, n1A=float(n1A), n2A=float(n2A), niA=float(niA), n1B=float(n1B), n2B=float(n2B), niB=float(niB),
    meanA=float(n1A / n), rmsA=float(n2A / math.sqrt(n)), meanB=float(n1B / n), rmsB=float(n2B / math.sqrt(n)),
    sqn=math.sqrt(n))
# 等价不等式：‖x‖∞ ≤ ‖x‖₂ ≤ ‖x‖₁ ≤ √n‖x‖₂ ≤ n‖x‖∞
for e in (eA, eB):
    a1, a2, ai = norms(e)
    assert ai <= a2 <= a1 <= math.sqrt(n) * a2 <= n * ai
# 平行四边形法则：2-范数满足，1-范数不满足
u, v = np.array([1.0, 0.0]), np.array([0.0, 1.0])
for p, name in ((1, "1"), (2, "2"), (np.inf, "inf")):
    lhs = np.linalg.norm(u + v, p) ** 2 + np.linalg.norm(u - v, p) ** 2
    rhs = 2 * np.linalg.norm(u, p) ** 2 + 2 * np.linalg.norm(v, p) ** 2
    out(**{f"pl_{name}": float(lhs), f"pr_{name}": float(rhs)})
# 位姿误差：位置 (mm) 与姿态 (mrad) 单位不同；取特征长度 L = 0.5 m，把角度误差换成末端 0.5 m 处的位移
dp = np.array([0.8, -0.3, 0.5])                  # mm
dth = np.array([1.2, 0.4, -2.0])                 # mrad
Lc = 500.0                                       # mm
w = np.concatenate([dp, Lc * dth / 1000])        # mm
out(dp=vec(dp, 1), dth=vec(dth, 1), w=vec(w, 2), wn=float(np.linalg.norm(w)), raw=float(np.linalg.norm(np.concatenate([dp, dth]))),
    pn=float(np.linalg.norm(dp)), tn=float(Lc * np.linalg.norm(dth) / 1000))
