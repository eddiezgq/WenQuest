"""24.3 节的示意图。

图 24.3.1：书中 UR5e 的质量矩阵。(a) 初始姿态 θ = (−90°, −90°, 90°, −90°, −90°, 0) 下 |M_ij|（对数色标，不含转子惯量）；
          (b) 10⁴ 个随机姿态（关节 2～6 在 ±180° 内均匀分布，关节 1 不影响 M）下各关节推动的连杆惯量 M_ii 的范围，
              空心点为初始姿态；虚线为转子等效惯量 armature = 0.1 kg·m²；
          (c) 平面 n 连杆臂运动方程展开后的项数（与程序 24.3.1 同样的写法；n = 2、3、4）。
"""
import math

import numpy as np
import sympy as sp

from _ch24 import mass_matrix, mj_load, mjcf_text, parse_links
from bookout import COLORS as C, T, figure, style

plt = style()
import mujoco                                                           # noqa: E402

links = parse_links(mjcf_text())
HOME = np.radians([-90, -90, 90, -90, -90, 0])
M_home = mass_matrix(links, HOME)
mj, m, d = mj_load(mjcf_text(option='<option><flag contact="disable"/></option>'))
ARM = np.array(m.dof_armature)
rng = np.random.default_rng(243)
lo, hi = np.full(6, np.inf), np.zeros(6)
for _ in range(10000):
    d.qpos[:] = np.r_[0.0, rng.uniform(-math.pi, math.pi, 5)]
    mujoco.mj_forward(m, d)
    Mf = np.zeros((6, 6))
    mujoco.mj_fullM(m, d, Mf)
    dg = np.diag(Mf) - ARM
    lo, hi = np.minimum(lo, dg), np.maximum(hi, dg)


def n_terms(n):
    q = sp.symbols(f"q1:{n + 1}")
    qd = sp.symbols(f"w1:{n + 1}")
    qdd = sp.symbols(f"u1:{n + 1}")
    a, mm, r, I = (sp.symbols(f"{s}1:{n + 1}") for s in ("a", "m", "r", "I"))
    g = sp.symbols("g")
    M = sp.zeros(n, n)
    U = 0
    base, ang = sp.Matrix([0, 0]), 0
    for i in range(n):
        ang = ang + q[i]
        c = base + r[i] * sp.Matrix([sp.cos(ang), sp.sin(ang)])
        Jv = c.jacobian(q)
        Jw = sp.Matrix([[1 if k <= i else 0 for k in range(n)]])
        M += mm[i] * Jv.T * Jv + I[i] * Jw.T * Jw
        U += mm[i] * g * c[1]
        base = base + a[i] * sp.Matrix([sp.cos(ang), sp.sin(ang)])
    M = M.applyfunc(lambda e: sp.trigsimp(sp.expand(e)))
    tot = 0
    for i in range(n):
        e = sum(M[i, j] * qdd[j] for j in range(n)) + sp.diff(U, q[i])
        for j in range(n):
            for k in range(n):
                e += sp.Rational(1, 2) * (sp.diff(M[i, j], q[k]) + sp.diff(M[i, k], q[j]) - sp.diff(M[j, k], q[i])) * qd[j] * qd[k]
        tot += len(sp.Add.make_args(sp.expand(e)))
    return tot


counts = [n_terms(n) for n in (2, 3, 4)]

fig = plt.figure(figsize=(13.2, 4.3))
gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.15, 0.8], wspace=0.5)
a1, a2, a3 = (fig.add_subplot(gs[0, k]) for k in range(3))
A = np.log10(np.maximum(np.abs(M_home), 1e-6))
im = a1.imshow(A, cmap="Blues", vmin=-6, vmax=0.5)
for i in range(6):
    for j in range(6):
        v = M_home[i, j]
        txt = "0" if abs(v) < 5e-7 else (f"{v:.2f}" if abs(v) >= 0.01 else f"{v:.0e}".replace("e-0", "e-"))
        a1.text(j, i, txt, ha="center", va="center", fontsize=7.5, color="white" if A[i, j] > -0.6 else C["ink"])
a1.set_xticks(range(6), [str(k) for k in range(1, 7)])
a1.set_yticks(range(6), [str(k) for k in range(1, 7)])
a1.set_xlabel(T("列（关节）", "column (joint)"))
a1.set_ylabel(T("行（关节）", "row (joint)"))
cb = fig.colorbar(im, ax=a1, fraction=0.046, pad=0.04)
cb.set_label(r"$\log_{10}|M_{ij}|$")
a1.set_title(T("(a) 初始姿态的 M（kg·m²）", "(a) M at the initial pose (kg·m²)"), fontsize=11, loc="left")

x = np.arange(1, 7)
a2.vlines(x, lo, hi, color=C["z"], lw=6, alpha=0.6, label=T("随机姿态的范围", "range over random poses"))
a2.plot(x, lo, "_", color=C["z"], ms=16, mew=2)
a2.plot(x, hi, "_", color=C["z"], ms=16, mew=2)
a2.plot(x, np.diag(M_home), "o", color=C["x"], mfc="white", ms=7, label=T("初始姿态", "initial pose"))
a2.axhline(ARM[0], color=C["accent"], ls="--", lw=1.2, label=T("转子等效惯量 0.1", "rotor (armature) 0.1"))
a2.set_yscale("log")
a2.set_xticks(x)
a2.set_xlabel(T("关节", "joint"))
a2.set_ylabel(r"$M_{ii}$ / (kg·m²)")
a2.legend(frameon=False, fontsize=9, loc="lower left")
a2.set_title(T("(b) 各关节推动的连杆惯量", "(b) link inertia seen by each joint"), fontsize=11, loc="left")
for s_ in ("top", "right"):
    a2.spines[s_].set_visible(False)

a3.bar([2, 3, 4], counts, color=C["z"], width=0.6)
for n_, c_ in zip((2, 3, 4), counts):
    a3.text(n_, c_ * 1.03, str(c_), ha="center", fontsize=10)
a3.set_xticks([2, 3, 4])
a3.set_xlabel(T("连杆数 n", "number of links n"))
a3.set_ylabel(T("展开后的项数", "terms after expansion"))
a3.set_ylim(0, max(counts) * 1.15)
a3.set_title(T("(c) 平面 n 连杆臂的方程规模", "(c) size of planar n-link equations"), fontsize=11, loc="left")
for s_ in ("top", "right"):
    a3.spines[s_].set_visible(False)
figure(fig, "fig24_3_1")
