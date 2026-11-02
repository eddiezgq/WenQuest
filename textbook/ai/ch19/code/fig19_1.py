"""19.1 节的示意图。

图 19.1.1：（a）显式格式过了库朗数 1 就炸，而半拉格朗日格式库朗数 5 照样稳；
（b）误差指数增长——初值精度提高十倍，只多买回一个多翻倍时间。
"""
import numpy as np

from _ch19 import advect_semilagrangian, advect_upwind, lorenz_run, useful_lead
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

NX, NSTEP = 200, 200
x = np.arange(NX) / NX * 2 * np.pi
u0 = np.exp(-((x - np.pi) ** 2) / 0.08)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 两种格式对库朗数的反应
cs = np.arange(0.2, 5.01, 0.1)
up = [min(np.max(np.abs(advect_upwind(u0, c, NSTEP))), 1e12) for c in cs]
sl = [np.max(np.abs(advect_semilagrangian(u0, c, NSTEP))) for c in cs]
a.semilogy(cs, up, "-", color=C["x"], lw=2.2, label=T("显式迎风格式", "explicit upwind"))
a.semilogy(cs, sl, "-", color=C["z"], lw=2.2, label=T("半拉格朗日格式", "semi-Lagrangian"))
a.axvline(1.0, color=C["ink"], ls=":", lw=1.4)
a.axhline(u0.max(), color=C["muted"], ls="--", lw=1.0)
a.annotate(T("库朗数 = 1", "Courant = 1"), xy=(1.0, 1e6), xytext=(1.25, 1e7),
           fontsize=9, color=C["ink"])
a.annotate(T("过了这条线就炸", "past this line it blows up"), xy=(1.5, 1e8),
           xytext=(2.2, 1e9), fontsize=8.5, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.0))
a.annotate(T("业务模式用的这一种\n库朗数 5 照样有界",
             "the kind operational models use\nstays bounded at Courant 5"),
           xy=(4.4, sl[-6]), xytext=(2.4, 1e-4), fontsize=8.5, color=C["z"],
           arrowprops=dict(arrowstyle="->", color=C["z"], lw=1.0))
a.set_xlabel(T("库朗数 C = uΔt/Δx", "Courant number C = uΔt/Δx"))
a.set_ylabel(T("走 200 步之后的峰值", "peak after 200 steps"))
a.set_ylim(1e-6, 1e12)
a.set_title(T("(a) 只有显式格式受 CFL 约束", "(a) Only explicit schemes obey CFL"),
            fontsize=10)
a.legend(fontsize=8.5, loc="lower left")
a.grid(alpha=0.25, lw=0.5, which="both")

# ---------------- (b) 误差指数增长
DT, N = 0.01, 1500
t = np.arange(N + 1) * DT
TOL = 2.0
for eps, col in ((1e-2, C["x"]), (1e-3, C["accent"]), (1e-4, C["y"]), (1e-5, C["z"])):
    logs = []
    for k in range(60):
        g = np.random.default_rng(1000 + k)
        s0 = lorenz_run(g.normal(0, 5, 3) + np.array([0.0, 0.0, 25.0]), DT, 2000)[-1]
        d = g.normal(size=3); d = d / np.linalg.norm(d) * eps
        err = np.linalg.norm(lorenz_run(s0, DT, N) - lorenz_run(s0 + d, DT, N), axis=-1)
        logs.append(np.log(np.maximum(err, 1e-16)))
    curve = np.exp(np.mean(logs, 0))          # 几何平均：指数增长在对数上才是直线
    b.semilogy(t, curve, "-", color=col, lw=1.9,
               label=T(f"初值误差 {eps:g}", f"initial error {eps:g}"))
    lead = useful_lead(DT, 3000, eps, TOL, seed=1)   # 与算例 19.1 同一口径
    b.plot([lead], [TOL], "o", color=col, ms=6, mec="white", mew=1.0, zorder=5)
    b.annotate(f"{lead:.1f}", xy=(lead, TOL), xytext=(lead - 0.35, TOL * 2.4),
               fontsize=8.5, color=col)
b.axhline(TOL, color=C["ink"], ls="--", lw=1.2)
b.annotate(T("误差涨到这里就不能用了", "forecast is no longer usable here"),
           xy=(0.3, TOL), xytext=(0.3, TOL * 6), fontsize=8.5, color=C["ink"])
b.set_xlabel(T("时间（无量纲）", "time (dimensionless)"))
b.set_ylabel(T("两条轨迹的距离", "distance between the two trajectories"))
b.set_xlim(0, 15)
b.set_ylim(1e-6, 1e2)
b.set_title(T("(b) 初值精度提高十倍，只多买回两个多时间单位",
              "(b) Ten times better initial data buys only ~2 more time units"), fontsize=10)
b.legend(fontsize=8, loc="lower right")
b.grid(alpha=0.25, lw=0.5, which="both")

fig.tight_layout()
figure(fig, "fig19_1_1")
