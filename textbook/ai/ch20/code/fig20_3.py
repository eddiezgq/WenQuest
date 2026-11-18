"""20.3 节的图：拟出来的势像不像，以及长时间模拟会怎样。

图 20.3.1：（a）在训练覆盖到的那一类构型上，拟合的势给出的能量与精确值几乎落在同一条
直线上——**静态指标好看**；（b）可是拿同一个势去跑分子动力学，总能量守不住：精确势几乎
不漂，拟合的势一路累积。**静态误差小，不等于长时间模拟能用。**
"""
import numpy as np

from _ch20 import (BASIS, basis_centers, featurize, fit_potential, lj_energy_forces,
                   predict_forces, sample_configs, verlet)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
L, N = 12.0, 10
CENTERS, WIDTH = basis_centers(), BASIS["width"]

train = sample_configs(80, N, L, amp=0.12, seed=0)
frames = [(x, lj_energy_forces(x, L)[0]) for x in train]
fdata = [lj_energy_forces(x, L)[1] for x in train]
w = fit_potential(frames, L, CENTERS, WIDTH, force_weight=0.1, force_data=fdata)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 拟合得像不像：预测对精确的对照
test = sample_configs(60, N, L, amp=0.12, seed=99)
e_true = np.array([lj_energy_forces(x, L)[0] for x in test]) / N
e_pred = np.array([float(featurize(x, L, CENTERS, WIDTH) @ w) for x in test]) / N
f_true = np.concatenate([lj_energy_forces(x, L)[1] for x in test])
f_pred = np.concatenate([predict_forces(w, x, L, CENTERS, WIDTH) for x in test])

a.plot(e_true, e_pred, "o", color=C["z"], ms=5, alpha=0.85,
       label=T("每个构型的能量/原子", "energy per atom, one dot per config"))
lim = (min(e_true.min(), e_pred.min()), max(e_true.max(), e_pred.max()))
pad = 0.04 * (lim[1] - lim[0])
a.plot([lim[0] - pad, lim[1] + pad], [lim[0] - pad, lim[1] + pad],
       color=C["ink"], lw=1.4, ls="--", label=T("完全一致的那条线", "perfect agreement"))
a.set_xlim(lim[0] - pad, lim[1] + pad)
a.set_ylim(lim[0] - pad, lim[1] + pad)
e_mae = float(np.abs(e_pred - e_true).mean())
f_mae = float(np.abs(f_pred - f_true).mean())
f_scale = float(np.abs(f_true).mean())
a.annotate(T(f"能量误差/原子 {e_mae:.2e}（相对 "
             f"{e_mae / float(np.abs(e_true).mean()) * 100:.4f}%）\n"
             f"力的平均误差 {f_mae:.2e}（相对 {f_mae / f_scale * 100:.3f}%）\n"
             f"训练构型：{len(train)} 个扰动晶格，能量与力一起拟合",
             f"energy MAE/atom {e_mae:.2e}; force MAE {f_mae:.2e}"),
           xy=(0.04, 0.72), xycoords="axes fraction", ha="left",
           fontsize=8.5, color=C["accent"])
a.set_xlabel(T("精确对势给的能量/原子", "exact energy per atom"))
a.set_ylabel(T("拟合的势预测的能量/原子", "predicted energy per atom"))
a.set_title(T("(a) 在训练覆盖到的构型上，拟得很紧",
              "(a) tight on configurations the training set covers"), fontsize=10)
a.legend(fontsize=8, loc="lower right", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 分子动力学的总能量漂移
x0 = np.sort(np.arange(N) * (L / N) + np.array([0.06, -0.04, 0.03, -0.05, 0.02,
                                                0.05, -0.03, 0.04, -0.02, 0.01]))
v0 = np.zeros(N)
DT, STEPS = 2e-3, 20000


def run(force_fn):
    _, _, hist = verlet(x0, v0, L, DT, STEPS, force_fn)
    return np.asarray(hist)[::200]


h_exact = run(lambda x: lj_energy_forces(x, L))
h_fit = run(lambda x: (float(featurize(x, L, CENTERS, WIDTH) @ w),
                       predict_forces(w, x, L, CENTERS, WIDTH)))
steps = np.arange(len(h_exact)) * 200 * DT
for h, col, name in ((h_exact, C["ink"], T("精确势", "exact potential")),
                     (h_fit, C["x"], T("拟合的势", "fitted potential"))):
    drift = (h - h[0]) / N
    b.plot(steps, drift, color=col, lw=2.0, label=name)
b.axhline(0.0, color=C["muted"], ls=":", lw=1.0)
b.set_xlabel(T("模拟时间", "simulated time"))
b.set_ylabel(T("每个原子的总能量相对初值的漂移",
               "drift of total energy per atom"))
b.set_title(T("(b) 长时间模拟里误差不是抹平，是累积",
              "(b) errors accumulate, they do not average out"), fontsize=10)
d_exact = float(np.abs((h_exact - h_exact[0]) / N).max())
d_fit = float(np.abs((h_fit - h_fit[0]) / N).max())
b.annotate(T(f"最大漂移：精确势 {d_exact:.1e}，拟合的势 {d_fit:.1e}",
             f"max drift: exact {d_exact:.1e}, fitted {d_fit:.1e}"),
           xy=(0.5, 0.06), xycoords="axes fraction", ha="center",
           fontsize=8.5, color=C["accent"])
b.legend(fontsize=8, loc="best", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig20_3_1")
