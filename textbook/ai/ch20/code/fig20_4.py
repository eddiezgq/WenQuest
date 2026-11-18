"""20.3—20.4 节的图：能量准不等于性质准，以及真正决定性质准不准的是什么。

图 20.4.1：（a）同一个拟合好的势，误差一级一级放大——能量（函数值）、力（一阶导）、
声子（二阶导）；（b）同一个性质（平衡间距与曲率），训练集覆盖到那条形变路径与没覆盖到，
差的不是一点点。**决定性的不是导数阶数，是覆盖范围。**
"""
import numpy as np

from _ch20 import (BASIS, basis_centers, featurize, featurize_forces, fit_potential,
                   lj_energy_forces, phonon_omega, predict_forces, sample_configs,
                   strained_configs)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
L, N = 12.0, 10
CENTERS, WIDTH = basis_centers(), BASIS["width"]

train = sample_configs(80, N, L, amp=0.12, seed=0)
frames = [(x, lj_energy_forces(x, L)[0]) for x in train]
fdata = [lj_energy_forces(x, L)[1] for x in train]
w = fit_potential(frames, L, CENTERS, WIDTH, force_weight=0.1, force_data=fdata)

# 第二个势：训练集里补上均匀应变的构型（与算例 20.4 同一套做法）
A_, b_ = [], []
for x, e in frames:
    A_.append(featurize(x, L, CENTERS, WIDTH)[None, :]); b_.append([e])
    A_.append(0.1 * featurize_forces(x, L, CENTERS, WIDTH)); b_.append(0.1 * lj_energy_forces(x, L)[1])
for x, box in strained_configs(80, N, 1.05, 1.35, amp=0.06, seed=3):
    e, f = lj_energy_forces(x, box)
    A_.append(featurize(x, box, CENTERS, WIDTH)[None, :]); b_.append([e])
    A_.append(0.1 * featurize_forces(x, box, CENTERS, WIDTH)); b_.append(0.1 * f)
A_ = np.vstack(A_); b_ = np.concatenate([np.atleast_1d(t) for t in b_])
w_strain = np.linalg.solve(A_.T @ A_ + 1e-8 * np.eye(A_.shape[1]), A_.T @ b_)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 误差阶梯
test = sample_configs(40, N, L, amp=0.12, seed=99)
e_mae = float(np.mean([abs(float(featurize(x, L, CENTERS, WIDTH) @ w)
                           - lj_energy_forces(x, L)[0]) / N for x in test]))
e_scale = float(np.mean([abs(lj_energy_forces(x, L)[0]) / N for x in test]))
f_mae = float(np.mean([np.abs(predict_forces(w, x, L, CENTERS, WIDTH)
                              - lj_energy_forces(x, L)[1]).mean() for x in test]))
f_scale = float(np.mean([np.abs(lj_energy_forces(x, L)[1]).mean() for x in test]))

# 平衡间距在覆盖到的那一段里搜（与算例 20.4 同一套做法，不写死数值）
_g = np.linspace(1.08, 1.32, 801)
a0 = float(_g[int(np.argmin([lj_energy_forces(np.arange(N) * s_, N * s_)[0] for s_ in _g]))])
x_eq = np.arange(N) * a0
box_eq = N * a0
om_exact = phonon_omega(lambda x: lj_energy_forces(x, box_eq)[0], x_eq, box_eq)
om_fit = phonon_omega(lambda x: float(featurize(x, box_eq, CENTERS, WIDTH) @ w_strain),
                      x_eq, box_eq)
keep = om_exact > 1e-6
ph_rel = float((np.abs(om_fit[keep] - om_exact[keep]) / om_exact[keep] * 100).mean())

vals = [e_mae / e_scale * 100, f_mae / f_scale * 100, ph_rel]
names = [T("能量\n（函数值）", "energy\n(value)"), T("力\n（一阶导）", "forces\n(1st deriv.)"),
         T("声子频率\n（二阶导）", "phonons\n(2nd deriv.)")]
cols = [C["z"], C["y"], C["x"]]
a.bar(np.arange(3), vals, 0.52, color=cols)
for i, t in enumerate(vals):
    a.annotate(f"{t:.4g}%", xy=(i, t), xytext=(0, 5), textcoords="offset points",
               ha="center", fontsize=8.5, color=cols[i])
a.set_yscale("log")
a.set_xticks(np.arange(3))
a.set_xticklabels(names, fontsize=9)
a.set_ylabel(T("相对误差（对数轴）", "relative error (log scale)"))
a.set_title(T("(a) 覆盖范围内：误差一级一级放大，但三级都还能用",
              "(a) inside coverage: a ladder, all three usable"), fontsize=10)
a.annotate(T("注意三者都很小——“二阶导一定不能用”并不成立",
             "all three are small: 'second derivatives are hopeless' is false"),
           xy=(0.03, 0.93), xycoords="axes fraction", ha="left",
           fontsize=8.5, color=C["accent"])
a.grid(alpha=0.25, lw=0.5, axis="y")

# ---------------- (b) 覆盖与不覆盖
grid = np.linspace(1.08, 1.32, 401)


def e_chain(coef, s):
    x = np.arange(N) * s
    return float(featurize(x, N * s, CENTERS, WIDTH) @ coef)


e_ex = np.array([lj_energy_forces(np.arange(N) * s, N * s)[0] for s in grid]) / N
e_no = np.array([e_chain(w, s) for s in grid]) / N
e_st = np.array([e_chain(w_strain, s) for s in grid]) / N
for ys, col, ls, name in ((e_ex, C["ink"], "-", T("精确", "exact")),
                          (e_st, C["z"], "--", T("训练集里有应变构型", "trained with strain")),
                          (e_no, C["x"], ":", T("训练集里没有应变构型", "no strain in training"))):
    b.plot(grid, ys - ys.min(), color=col, lw=2.0, ls=ls, label=name)
    i = int(np.argmin(ys))
    b.plot([grid[i]], [0.0], "o", color=col, ms=7, zorder=3)
b.set_xlabel(T("均匀伸缩的间距", "uniform spacing"))
b.set_ylim(0, 0.085)
b.set_ylabel(T("每个原子的能量（各自减去自己的最小值）",
               "energy per atom (each minus its own minimum)"))
b.set_title(T("(b) 同一个性质，差别全在训练集覆盖了哪条路径",
              "(b) same property: coverage is what decides"), fontsize=10)
i_ex, i_no, i_st = (int(np.argmin(z)) for z in (e_ex, e_no, e_st))
err_no = abs(grid[i_no] - grid[i_ex]) / grid[i_ex] * 100
err_st = abs(grid[i_st] - grid[i_ex]) / grid[i_ex] * 100
b.annotate(T(f"平衡间距误差：有应变 {err_st:.3f}%，没有 {err_no:.2f}%"
             f"（后者的最小值还跑到了搜索区间的边上）",
             f"spacing error: {err_st:.3f}% with strain, {err_no:.2f}% without"),
           xy=(0.5, 0.055), xycoords="axes fraction", ha="center",
           fontsize=8.5, color=C["accent"])
b.annotate(T("虚线（没有应变构型）一路冲出图外——它在这条路径上根本没有被约束过",
             "the dotted curve runs off the top: unconstrained along this path"),
           xy=(0.97, 0.62), xycoords="axes fraction", ha="right",
           fontsize=8.5, color=C["x"])
b.legend(fontsize=8, loc="upper left", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig20_4_1")
