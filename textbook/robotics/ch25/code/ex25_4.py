"""25.4 节的计算：计算量对比。

(1) 数运算次数：同一台“通用”串联臂（关节轴是任意单位矢量，连杆参数任意，不利用零元素），
    用 Ops 把数据包起来，程序走一遍就数出乘法、加法次数：
    - 牛顿-欧拉递推（三维矢量写法，25.4.2 节）；
    - 拉格朗日-欧拉方程（尤克、卡恩的 4×4 矩阵写法，式 (25.4.1)）；
    n = 1～10。两种算法对同一组数据算出的力矩相同（数值核对）；递推的次数是 n 的一次式，拉格朗日-欧拉是 n 的四次式（求出系数）。
    书中 UR5e 的数据代进去，n = 6 的次数与通用臂相同（程序不跳过零）。
(2) 正动力学（25.3.4 节）：n + 1 次递推求 M、c + g，再用楚列斯基分解解方程，数运算次数。
(3) 计时（在构建本书的计算机上测得，不同计算机不同）：UR5e 一次逆动力学——本书的 NumPy 递推、三维矢量写法的递推、
    拉格朗日-欧拉写法（都用 Python），MuJoCo 的 mj_inverse；n 连杆链（程序生成的 MJCF）上 MuJoCo 的逆动力学与正动力学用时随 n 的变化。
(4) 习题答案。
"""
import math
import time

import numpy as np

from _ch25 import G0, Ops, ScalarChain, count_ops, mj_load, ur_chain
from bookout import out

rng = np.random.default_rng(254)

# ---------------------------------------------------------------- (1) 数运算次数
NS = list(range(1, 11))
cnt_rn, cnt_le = {}, {}
err_le = 0.0
for n in NS:
    seed = 1000 + n
    sc = ScalarChain.random(n, np.random.default_rng(seed), wrap=Ops)
    r = np.random.default_rng(seed + 1)
    th, thd, thdd = r.uniform(-3, 3, n), r.normal(size=n), r.normal(size=n)
    args = ([Ops(math.cos(x)) for x in th], [Ops(math.sin(x)) for x in th], [Ops(x) for x in thd], [Ops(x) for x in thdd], Ops(G0))
    def run_rn():
        global t_rn
        t_rn = [x.v for x in sc.rnea(*args)]

    def run_le():
        global t_le
        t_le = [x.v for x in sc.lagrange_euler(*args)]
    cnt_rn[n] = count_ops(run_rn)
    cnt_le[n] = count_ops(run_le)
    err_le = max(err_le, float(np.abs(np.array(t_rn) - np.array(t_le)).max()))
assert err_le < 1e-9
# 递推：一次式
a_m = cnt_rn[2][0] - cnt_rn[1][0]
b_m = cnt_rn[1][0] - a_m
a_a = cnt_rn[2][1] - cnt_rn[1][1]
b_a = cnt_rn[1][1] - a_a
assert all(cnt_rn[n] == (a_m * n + b_m, a_a * n + b_a) for n in NS)
# 拉格朗日-欧拉：四次式（用 5 个点求系数，再用其余的点核对）
def poly4(k):
    x = np.array(NS[:5], float)
    y = np.array([cnt_le[n][k] for n in NS[:5]], float)
    c = np.linalg.solve(np.vander(x, 5), y)
    for n in NS:
        assert abs(np.polyval(c, n) - cnt_le[n][k]) < 1e-6
    return c


c4m, c4a = poly4(0), poly4(1)
from fractions import Fraction                                          # noqa: E402
lead_m = Fraction(c4m[0]).limit_denominator(100)
lead_a = Fraction(c4a[0]).limit_denominator(100)
assert abs(float(lead_m) - c4m[0]) < 1e-9 and abs(float(lead_a) - c4a[0]) < 1e-9
# UR5e 的数据
ch = ur_chain()
scu = ScalarChain.from_chain(ch, wrap=Ops)
th = np.radians([115.5, -80.1, 108.7, -103.5, -86.4, 6.8])
argsu = ([Ops(math.cos(x)) for x in th], [Ops(math.sin(x)) for x in th], [Ops(0.3)] * 6, [Ops(0.5)] * 6, Ops(G0))
cnt_ur = count_ops(lambda: scu.rnea(*argsu))
assert cnt_ur == cnt_rn[6]
ratio6 = cnt_le[6][0] / cnt_rn[6][0]

# ---------------------------------------------------------------- (2) 正动力学的运算次数：n + 1 次递推 + 楚列斯基分解与回代


def cholesky_solve(M, b):
    n = len(b)
    Lm = [[None] * n for _ in range(n)]
    for j in range(n):
        s = M[j][j]
        for k in range(j):
            s = s - Lm[j][k] * Lm[j][k]
        Lm[j][j] = Ops(math.sqrt(s.v))                    # 开方单独计（n 次）
        inv_d = Ops(1.0 / Lm[j][j].v)                      # 倒数单独计（n 次）
        for i in range(j + 1, n):
            s = M[i][j]
            for k in range(j):
                s = s - Lm[i][k] * Lm[j][k]
            Lm[i][j] = s * inv_d
    y = [None] * n
    for i in range(n):
        s = b[i]
        for k in range(i):
            s = s - Lm[i][k] * y[k]
        y[i] = s * Ops(1.0 / Lm[i][i].v)
    x = [None] * n
    for i in reversed(range(n)):
        s = y[i]
        for k in range(i + 1, n):
            s = s - Lm[k][i] * x[k]
        x[i] = s * Ops(1.0 / Lm[i][i].v)
    return x


def fd_count(n):
    rn = cnt_rn[n]
    A = rng.normal(size=(n, n))
    M = [[Ops(v) for v in row] for row in (A @ A.T + n * np.eye(n))]
    b = [Ops(v) for v in rng.normal(size=n)]
    ch_m, ch_a = count_ops(lambda: cholesky_solve(M, b))
    return (n + 1) * rn[0] + ch_m, (n + 1) * rn[1] + ch_a + n   # 加上 τ − (c + g) 的 n 次减法


fd6 = fd_count(6)

# ---------------------------------------------------------------- (3) 计时


def timeit(f, reps=5, inner=None):
    if inner is None:                                   # 先估计一次用时，使每次测量约 0.1 s
        t0 = time.perf_counter()
        f()
        dt = time.perf_counter() - t0
        inner = max(1, int(0.1 / max(dt, 1e-7)))
    best = []
    for _ in range(reps):
        t0 = time.perf_counter()
        for _ in range(inner):
            f()
        best.append((time.perf_counter() - t0) / inner)
    return float(np.min(best))


q = th
qd = np.full(6, 0.3)
qdd = np.full(6, 0.5)
t_np = timeit(lambda: ch.rnea(q, qd, qdd))
scf = ScalarChain.from_chain(ch)
cs, ss = [math.cos(x) for x in q], [math.sin(x) for x in q]
t_sc = timeit(lambda: scf.rnea(cs, ss, qd, qdd, G0))
t_le6 = timeit(lambda: scf.lagrange_euler(cs, ss, qd, qdd, G0), reps=3)
from _ch25 import ur_mj                                                 # noqa: E402
mj, m, d = ur_mj()
d.qpos[:], d.qvel[:], d.qacc[:] = q, qd, qdd


def mj_inv():
    mj.mj_inverse(m, d)


t_mj = timeit(mj_inv)
BUDGET = 2e-3                                           # UR e 系列：500 Hz，每 2 ms 一次
# n 连杆链


def chain_xml(n):
    s = '<mujoco><option><flag contact="disable"/></option><worldbody>'
    close = ""
    for i in range(n):
        axis = "0 1 0" if i % 2 else "0 0 1"
        s += (f'<body pos="0 0 {0.1 if i else 0}"><joint type="hinge" axis="{axis}"/>'
              f'<geom type="capsule" fromto="0 0 0 0 0 0.1" size="0.02" mass="{1.0 + 0.1 * i}"/>')
        close += "</body>"
    return s + close + "</worldbody></mujoco>"


NC = [6, 12, 24, 48, 96]
t_inv, t_fwd = [], []
for n in NC:
    mjc, mc, dc = mj_load(chain_xml(n))
    dc.qpos[:] = rng.uniform(-1, 1, n)
    dc.qvel[:] = rng.uniform(-1, 1, n)
    dc.qacc[:] = rng.uniform(-1, 1, n)
    t_inv.append(timeit(lambda: mjc.mj_inverse(mc, dc)))
    t_fwd.append(timeit(lambda: mjc.mj_forward(mc, dc)))

# ---------------------------------------------------------------- (4) 习题答案
# 习题 25.4.2：n = 30（类人机器人量级）时两种写法的乘法次数
m30_rn = a_m * 30 + b_m
m30_le = int(round(np.polyval(c4m, 30)))

tab = {}
for n in (1, 2, 3, 6, 10):
    tab[f"rm{n}"], tab[f"ra{n}"] = cnt_rn[n]
    tab[f"lm{n}"], tab[f"la{n}"] = cnt_le[n]
out(err_le=err_le, a_m=a_m, nb_m=-b_m, a_a=a_a, nb_a=-b_a, lead_m=str(lead_m), lead_a=str(lead_a), ratio6=ratio6,
    fd6_m=fd6[0], fd6_a=fd6[1], t_np=t_np * 1e6, t_sc=t_sc * 1e6, t_le6=t_le6 * 1e3, t_mj=t_mj * 1e6,
    n_np=BUDGET / t_np, n_le=BUDGET / t_le6, t_inv6=t_inv[0] * 1e6, t_inv96=t_inv[-1] * 1e6, t_fwd6=t_fwd[0] * 1e6,
    t_fwd96=t_fwd[-1] * 1e6, m30_rn=m30_rn, m30_le=m30_le, **tab)
