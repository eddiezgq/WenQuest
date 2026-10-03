"""14.1 节：可解性与多解。

(1) 平面 2R 臂（l1 = 0.425 m、l2 = 0.392 m，UR5e 的大臂、小臂）：四个目标点的解的个数（定理 14.1.1）。
    圆环内的点有两组解，与第 7 章算例 7.3.4 用牛顿法得到的解比较（两种方法一致）。
(2) 引理 14.1.1：A cos θ + B sin θ = C。式 (14.1.4)（两个 atan2）与式 (11.5.3)（arccos）、
    半角代换后的二次方程 (14.1.5) 三种写法在一万组随机系数下互相核对。
(3) 一般 6R 臂（随机 DH 参数）：从 600 个随机初值出发用数值法（阻尼最小二乘）求逆解，统计不同的解有几组；
    每一组都代回正运动学核对。理论上至多 16 组（拉加万与罗思，1990、1993）。
"""
import math

import numpy as np

from _ik import dh_fk_general, distinct, fk2r, ik2r, numeric_ik, pose_err, random6r, trig_solve, wrap
from bookout import out, vec

l1, l2 = 0.425, 0.392

# ---------------------------------------------------------------- (1) 2R 的解的个数
targets = {"A": (0.45, 0.35), "B": (l1 + l2, 0.0), "C": (0.9, 0.3), "D": (0.02, 0.0)}
counts = {k: len(ik2r(x, y, l1, l2)) for k, (x, y) in targets.items()}
assert counts == {"A": 2, "B": 1, "C": 0, "D": 0}
solsA = ik2r(*targets["A"], l1, l2)
for s in solsA:
    assert np.linalg.norm(fk2r(s, l1, l2) - np.array(targets["A"])) < 1e-12
up = [s for s in solsA if s[1] < 0][0]          # θ2 < 0：肘部在基座与目标连线的上方
down = [s for s in solsA if s[1] > 0][0]


def newton2r(th, p, n=50):                       # 第 7 章式 (7.3.8)
    th = np.array(th, float)
    for _ in range(n):
        F = fk2r(th, l1, l2) - p
        if np.linalg.norm(F) < 1e-14:
            break
        s1, s12, c1, c12 = math.sin(th[0]), math.sin(th[0] + th[1]), math.cos(th[0]), math.cos(th[0] + th[1])
        J = np.array([[-l1 * s1 - l2 * s12, -l2 * s12], [l1 * c1 + l2 * c12, l2 * c12]])
        th = th - np.linalg.solve(J, F)
    return np.array([wrap(t) for t in th])


nA = newton2r((0, 1), np.array(targets["A"]))
nB = newton2r((1, -1), np.array(targets["A"]))
assert np.allclose(nA, down, atol=1e-12) and np.allclose(nB, up, atol=1e-12)
r_in = abs(l1 - l2)
# 两组解关于基座与目标的连线对称：θ1 + θ1′ = 2 atan2(y, x) − ...，肘点互为镜像
beta = math.atan2(targets["A"][1], targets["A"][0])
e_up = np.array([l1 * math.cos(up[0]), l1 * math.sin(up[0])])
e_dn = np.array([l1 * math.cos(down[0]), l1 * math.sin(down[0])])
u = np.array([math.cos(beta), math.sin(beta)])
mirror = 2 * (e_dn @ u) * u - e_dn
assert np.allclose(mirror, e_up, atol=1e-12)

# ---------------------------------------------------------------- (2) 引理 14.1.1 的三种写法
rng = np.random.default_rng(141)
worst = 0.0
for _ in range(10000):
    A, B = rng.normal(size=2)
    C = rng.uniform(-1.2, 1.2) * math.hypot(A, B)
    s = trig_solve(A, B, C)
    rho = math.hypot(A, B)
    if abs(C) > rho:
        assert s == []
        continue
    ac = [wrap(math.atan2(B, A) + sg * math.acos(C / rho)) for sg in (1, -1)]          # 式 (11.5.3)
    # 半角代换 t = tan(θ/2)：(C + A) t² − 2B t + (C − A) = 0（式 (14.1.5)）
    qa, qb, qc = C + A, -2 * B, C - A
    disc = qb * qb - 4 * qa * qc
    ts = [(-qb + sg * math.sqrt(max(disc, 0))) / (2 * qa) for sg in (1, -1)]
    hq = [wrap(2 * math.atan(t)) for t in ts]
    for x in s:
        assert abs(A * math.cos(x) + B * math.sin(x) - C) < 1e-12 * rho
        assert min(abs(wrap(x - y)) for y in ac) < 1e-6 and min(abs(wrap(x - y)) for y in hq) < 1e-6
        worst = max(worst, abs(A * math.cos(x) + B * math.sin(x) - C) / rho)

# ---------------------------------------------------------------- (3) 一般 6R 臂的解的个数（数值法清点）
P, Td, found, hits = random6r()
D = distinct(found)
for s in D:
    e = pose_err(dh_fk_general(P, s), Td)
    assert e[0] < 1e-10 and e[1] < 1e-10
assert len(D) <= 16
n_conv = sum(x is not None for x in found)
dh_rows = r" \\ ".join(f"{i} & {a:.3f} & {d:.3f} & {math.degrees(al):.1f}" for i, (a, d, al) in enumerate(P, 1))

out(solA_deg=f"({math.degrees(down[0]):.2f}°, {math.degrees(down[1]):.2f}°)",
    solB_deg=f"({math.degrees(up[0]):.2f}°, {math.degrees(up[1]):.2f}°)",
    nA=counts["A"], nB=counts["B"], nC=counts["C"], nD=counts["D"], r_out=l1 + l2, r_in=r_in,
    rA=math.hypot(*targets["A"]), rC=math.hypot(*targets["C"]), rD=0.02,
    beta_deg=math.degrees(beta), trig_worst=worst,
    n_start=len(found), n_conv=n_conv, n_6r=len(D), hits=hits, hmin=min(hits), hmax=max(hits), dh_rows=dh_rows,
    sol6r=vec(np.degrees(D[0]), 1))
