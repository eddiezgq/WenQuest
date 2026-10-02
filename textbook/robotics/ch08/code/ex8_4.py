"""算例 8.4.1～8.4.3：凸优化。

- 8.4.1 凸性的检验：平面 2R 臂逆运动学的目标函数 f(θ) 不是凸函数（找出违反詹森不等式的两点）；
  而 ½‖Ax − b‖² 的黑塞矩阵 AᵀA 半正定，是凸函数；
- 8.4.2 夹爪与障碍物（两个凸多边形）之间的最短距离：二次规划，用障碍函数法求解；
  用“顶点到边”的穷举法核对；由解构造分离直线，验证两个多边形分在两侧；对偶间隙 m/t；
- 8.4.3 AGV 在两段凸走廊中的路径：二次规划，障碍函数法；中心路径；与 scipy（SLSQP）核对；
  验证相邻航点间的线段全部落在可通行区域内。
"""
import math

import numpy as np
from scipy.optimize import minimize

from _opt import L2R, barrier_qp, jac, tip
from bookout import out, vec


def halfplanes(P):
    """逆时针排列的凸多边形顶点 → 不等式 A x ≤ b（每条边一行，法向量朝外，单位长度）。"""
    A, b = [], []
    for i in range(len(P)):
        p, q = np.array(P[i], float), np.array(P[(i + 1) % len(P)], float)
        t = q - p
        n = np.array([t[1], -t[0]]) / np.linalg.norm(t)
        A.append(n)
        b.append(n @ p)
    return np.array(A), np.array(b)


# ---------------------------------------------------------------- 算例 8.4.1：凸与非凸
pd = np.array([0.5, 0.4])


def f_ik(th):
    r = tip(th, L2R) - pd
    return 0.5 * float(r @ r)


ta = np.array([0.0359969, 1.3415703])          # 两个极小点（算例 8.1.3 的两组逆解，取 5 位小数即可说明问题）
tb = np.array([1.3134849, -1.3415703])
mid = (ta + tb) / 2
f_mid = f_ik(mid)
f_avg = (f_ik(ta) + f_ik(tb)) / 2
assert f_mid > f_avg + 0.01                     # 詹森不等式不成立：f 不是凸函数
rng = np.random.default_rng(4)
Aq = rng.normal(size=(5, 3))
bq = rng.normal(size=5)
eig_q = np.linalg.eigvalsh(Aq.T @ Aq)
assert eig_q.min() >= 0                         # AᵀA 半正定（这里正定）
for _ in range(1000):                           # 随机抽查詹森不等式
    x, y, s = rng.normal(size=3), rng.normal(size=3), rng.uniform()
    fq = lambda z: 0.5 * float((Aq @ z - bq) @ (Aq @ z - bq))
    assert fq(s * x + (1 - s) * y) <= s * fq(x) + (1 - s) * fq(y) + 1e-12

# ---------------------------------------------------------------- 算例 8.4.2：两个凸多边形的距离
ang = math.radians(25)
Rg = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
cg = np.array([0.30, 0.20])
G = [cg + Rg @ np.array(v) for v in [(-0.06, -0.03), (0.06, -0.03), (0.06, 0.03), (-0.06, 0.03)]]   # 夹爪投影 12 cm × 6 cm
O = [np.array(v) for v in [(0.42, 0.28), (0.55, 0.25), (0.50, 0.40)]]                                # 障碍物（三角形）
A1, b1 = halfplanes(G)
A2, b2 = halfplanes(O)
A = np.block([[A1, np.zeros((4, 2))], [np.zeros((3, 2)), A2]])
b = np.r_[b1, b2]
Q = np.block([[np.eye(2), -np.eye(2)], [-np.eye(2), np.eye(2)]])     # ½‖u − w‖²
x0 = np.r_[np.mean(G, axis=0), np.mean(O, axis=0)]                   # 两个形心：严格可行
xd, cent_d, mu_d, _, steps_d = barrier_qp(Q, np.zeros(4), A, b, x0, t0=1.0, eps=1e-10)
u, w = xd[:2], xd[2:]
dist = float(np.linalg.norm(u - w))


def seg_dist(p, a, c):
    t = np.clip((p - a) @ (c - a) / ((c - a) @ (c - a)), 0, 1)
    return float(np.linalg.norm(p - a - t * (c - a)))


d_brute = min([seg_dist(p, O[i], O[(i + 1) % 3]) for p in G for i in range(3)] +
              [seg_dist(p, G[i], G[(i + 1) % 4]) for p in O for i in range(4)])
assert abs(dist - d_brute) < 1e-8
n = (w - u) / dist                                                  # 分离直线的法向
cmid = n @ (u + w) / 2
gap_G = max(n @ p for p in G) - cmid                                # 夹爪全在直线一侧（≤ 0）
gap_O = min(n @ p for p in O) - cmid                                # 障碍物全在另一侧（≥ 0）
assert gap_G < 0 < gap_O
m_d = len(b)
gap_bound = m_d / cent_d[-1][0]                                     # 对偶间隙 m/t
fval = 0.5 * dist ** 2
active_d = [i for i in range(m_d) if mu_d[i] > 1e-4]
assert active_d == [1, 4, 6]                                        # 夹爪的第 2 条边；障碍物的顶点 O1（第 1、3 条边的交点）
# KKT：Q x + Aᵀμ ≈ 0
stat_d = float(np.linalg.norm(Q @ xd + A.T @ mu_d))
assert stat_d < 1e-6                                                  # 驻点条件（内层牛顿法的停止精度）

# ---------------------------------------------------------------- 算例 8.4.3：凸走廊中的 AGV 路径
R1 = [(0, 0), (6, 0), (6, 1.2), (0, 1.8)]                        # 下方走廊（上边是倾斜的货架边缘），m
R2 = [(4.6, 0), (6, 0), (6, 4), (4.6, 4)]                        # 右侧走廊
Ar1, br1 = halfplanes(R1)
Ar2, br2 = halfplanes(R2)
start, goal = np.array([0.5, 0.9]), np.array([5.3, 3.5])
Nw, kx = 10, 5                                                   # 10 段，航点 x1…x5 在 R1，x5…x9 在 R2
nv = 2 * (Nw - 1)
rows, rhs = [], []
for i in range(1, Nw):
    regs = ([(Ar1, br1)] if i <= kx else []) + ([(Ar2, br2)] if i >= kx else [])
    for Aa, bb in regs:
        for a_, b_ in zip(Aa, bb):
            r = np.zeros(nv)
            r[2 * (i - 1):2 * i] = a_
            rows.append(r)
            rhs.append(b_)
Ac, bc = np.array(rows), np.array(rhs)
Dm, dv = np.zeros((2 * Nw, nv)), np.zeros(2 * Nw)                # 第 i 段 x_{i+1} − x_i = Dm x + dv
for i in range(Nw):
    for k in range(2):
        if i + 1 <= Nw - 1:
            Dm[2 * i + k, 2 * i + k] += 1
        else:
            dv[2 * i + k] += goal[k]
        if i >= 1:
            Dm[2 * i + k, 2 * (i - 1) + k] -= 1
        else:
            dv[2 * i + k] -= start[k]
Qc, cc = 2 * Dm.T @ Dm, 2 * Dm.T @ dv                            # Σ‖x_{i+1} − x_i‖² = xᵀ(DᵀD)x + 2(Dᵀd)ᵀx + 常数
x0c = np.array([start + (np.array([5.3, 0.9]) - start) * i / kx if i <= kx else
                np.array([5.3, 0.9 + (goal[1] - 0.9) * (i - kx) / (Nw - kx)]) for i in range(1, Nw)]).ravel()
assert (bc - Ac @ x0c).min() > 0                                  # 起点严格可行
xc, cent_c, mu_c, _, steps_c = barrier_qp(Qc, cc, Ac, bc, x0c, t0=1.0, eps=1e-9)
P = np.vstack([start, xc.reshape(-1, 2), goal])
corner = P[kx]
assert abs(corner[0] - 4.6) < 1e-6 and abs(corner[1] - (1.8 - 0.6 * 4.6 / 6)) < 1e-6   # 拐点在两走廊交界的角上
# 线段全在区域内：每个线段的两个端点在同一个凸区域里，用 50 个中间点抽查
for i in range(Nw):
    regs = [(Ar1, br1)] if i < kx else [(Ar2, br2)]
    for s in np.linspace(0, 1, 50):
        q = (1 - s) * P[i] + s * P[i + 1]
        assert all((Aa @ q <= bb + 1e-9).all() for Aa, bb in regs)
sc = minimize(lambda z: 0.5 * z @ Qc @ z + cc @ z, x0c, jac=lambda z: Qc @ z + cc, method="SLSQP",
              constraints=[dict(type="ineq", fun=lambda z: bc - Ac @ z, jac=lambda z: -Ac)],
              options={"ftol": 1e-15, "maxiter": 500})
assert np.abs(sc.x - xc).max() < 1e-6
length = float(np.sum(np.linalg.norm(np.diff(P, axis=0), axis=1)))
straight = float(np.linalg.norm(start - corner) + np.linalg.norm(corner - goal))
assert abs(length - straight) < 1e-6                              # 最优路径是“起点—拐角—终点”两段直线
# 中心路径：几个 t 时拐角航点的位置
cp = {round(t): xx.reshape(-1, 2)[kx - 1] for t, xx in cent_c}
mc = len(bc)

out(
    f_mid=f_mid, f_avg=f_avg, eig_q=vec(eig_q, 3),
    u=vec(u, 4), w=vec(w, 4), dist=dist, dist_mm=dist * 1000, d_brute=d_brute, n=vec(n, 4), gap_G=-gap_G, gap_O=gap_O,
    mu1=float(mu_d[1]), mu4=float(mu_d[4]), mu6=float(mu_d[6]), steps_d=steps_d, outer_d=len(cent_d), m_d=m_d, gap_d=gap_bound,
    stat_d=stat_d, fval=fval,
    corner=vec(corner, 3), steps_c=steps_c, outer_c=len(cent_c), mc=mc, nvar=nv, length=length,
    cp1=vec(cp[1], 3), cp10=vec(cp[10], 3), cp100=vec(cp[100], 3), cp1000=vec(cp[1000], 3),
    sc_err=float(np.abs(sc.x - xc).max()), gap_c=mc / cent_c[-1][0],
)
