"""25.4 节的示意图。

图 25.4.1：(a) 一次逆动力学的乘法次数随关节数 n 的变化：牛顿-欧拉递推（一次式）、拉格朗日-欧拉的 4×4 矩阵写法（四次式；
              n ≤ 10 为数出的次数，更大的 n 按求出的四次式画虚线），以及“n + 1 次递推 + 楚列斯基分解”的正动力学；
          (b) MuJoCo 对 n 连杆链（程序生成的模型）算一次逆动力学（mj_inverse）、正动力学（mj_forward）的用时
              （在构建本书的计算机上测得，不同计算机不同）。
"""
import math
import time

import numpy as np

from _ch25 import G0, Ops, ScalarChain, count_ops, mj_load
from bookout import COLORS as C, T, figure, style

plt = style()
NS = list(range(1, 11))
rn, le = [], []
for n in NS:
    sc = ScalarChain.random(n, np.random.default_rng(1000 + n), wrap=Ops)
    r = np.random.default_rng(1001 + n)
    th = r.uniform(-3, 3, n)
    args = ([Ops(math.cos(x)) for x in th], [Ops(math.sin(x)) for x in th], [Ops(x) for x in r.normal(size=n)],
            [Ops(x) for x in r.normal(size=n)], Ops(G0))
    rn.append(count_ops(lambda: sc.rnea(*args))[0])
    le.append(count_ops(lambda: sc.lagrange_euler(*args))[0])
c4 = np.linalg.solve(np.vander(np.array(NS[:5], float), 5), np.array(le[:5], float))
a, b = rn[1] - rn[0], rn[0] - (rn[1] - rn[0])
nn = np.arange(1, 41)
# 正动力学：(n + 1) 次递推 + 楚列斯基分解与两次回代的乘法 n³/6 + n² + O(n)（近似）
fd = (nn + 1) * (a * nn + b) + nn ** 3 / 6 + nn ** 2


def chain_xml(n):
    s = '<mujoco><option><flag contact="disable"/></option><worldbody>'
    close = ""
    for i in range(n):
        axis = "0 1 0" if i % 2 else "0 0 1"
        s += (f'<body pos="0 0 {0.1 if i else 0}"><joint type="hinge" axis="{axis}"/>'
              f'<geom type="capsule" fromto="0 0 0 0 0 0.1" size="0.02" mass="{1.0 + 0.1 * i}"/>')
        close += "</body>"
    return s + close + "</worldbody></mujoco>"


def timeit(f):
    t0 = time.perf_counter()
    f()
    inner = max(1, int(0.05 / max(time.perf_counter() - t0, 1e-7)))
    res = []
    for _ in range(9):
        t0 = time.perf_counter()
        for _ in range(inner):
            f()
        res.append((time.perf_counter() - t0) / inner)
    return float(np.min(res))


NC = [3, 6, 12, 24, 48, 96, 192]
ti, tf_ = [], []
rng = np.random.default_rng(254)
for n in NC:
    mj, m, d = mj_load(chain_xml(n))
    d.qpos[:] = rng.uniform(-1, 1, n)
    d.qvel[:] = rng.uniform(-1, 1, n)
    d.qacc[:] = rng.uniform(-1, 1, n)
    ti.append(timeit(lambda: mj.mj_inverse(m, d)) * 1e6)
    tf_.append(timeit(lambda: mj.mj_forward(m, d)) * 1e6)

fig, axs = plt.subplots(1, 2, figsize=(11.0, 4.2))
ax = axs[0]
ax.loglog(NS, rn, "o-", color=C["z"], lw=1.6, ms=4, label=T("牛顿-欧拉递推（逆动力学）", "recursive Newton–Euler (inverse)"))
ax.loglog(nn, a * nn + b, "-", color=C["z"], lw=0.8)
ax.loglog(NS, le, "s-", color=C["x"], lw=1.6, ms=4, label=T("拉格朗日-欧拉（逆动力学）", "Lagrange–Euler (inverse)"))
ax.loglog(nn[nn >= 10], np.polyval(c4, nn[nn >= 10]), "--", color=C["x"], lw=1.2)
ax.loglog(nn, fd, ":", color=C["accent"], lw=1.8, label=T("正动力学：n+1 次递推 + 解方程", "forward: n+1 recursions + solve"))
ax.axvline(6, color=C["muted"], lw=0.8, ls="--")
ax.text(6.3, 60, "UR5e", fontsize=9, color=C["muted"])
ax.set_xlabel(T("关节数 n", "number of joints n"))
ax.set_ylabel(T("乘法次数", "multiplications"))
ax.set_title(T("(a) 运算次数", "(a) operation counts"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
ax.grid(alpha=0.25, which="both")
ax = axs[1]
ax.loglog(NC, ti, "o-", color=C["z"], lw=1.6, ms=4, label=T("逆动力学 mj_inverse", "inverse mj_inverse"))
ax.loglog(NC, tf_, "s-", color=C["accent"], lw=1.6, ms=4, label=T("正动力学 mj_forward", "forward mj_forward"))
ax.axhline(2000, color=C["x"], lw=1.0, ls="--")
ax.text(3.2, 1300, T("500 Hz 控制周期 2 ms", "2 ms cycle at 500 Hz"), fontsize=9, color=C["x"])
ax.set_xlabel(T("关节数 n（链）", "number of joints n (chain)"))
ax.set_ylabel(T("用时 / μs", "time / μs"))
ax.set_title(T("(b) MuJoCo 的用时（本书构建时测得）", "(b) MuJoCo timing (measured at build time)"), fontsize=11)
ax.legend(fontsize=9, frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.88))
ax.grid(alpha=0.25, which="both")
fig.tight_layout()
figure(fig, "fig25_4_1")
