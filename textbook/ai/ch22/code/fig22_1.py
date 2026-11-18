"""22.1 节的图之一：光伏预测与分位数。

图 22.1.1：（a）两天的实际出力、点预测与 10%—90% 区间；
（b）名义覆盖率与实际覆盖率的对照，以及区间宽度——**名义值是你要的，实际值才是你有的**。
"""
import numpy as np

from _ch22 import (STEPS_PER_DAY, cloud_factor, coverage, design_matrix, fit_ls,
                   fit_quantile, interval_width, pv_series)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_DAYS = 60

pv = pv_series(N_DAYS, seed=0)
cl = cloud_factor(N_DAYS, seed=0)
g = np.random.default_rng(5)
X = design_matrix(N_DAYS, np.clip(cl + 0.12 * g.normal(0, 1, len(cl)), 0, 1))
cut = int(len(pv) * 0.7)
tr = np.arange(cut)
te = np.arange(cut, len(pv))
w_mid = fit_ls(X[tr], pv[tr])
QS = (0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95)
pred = {q: np.maximum(X[te] @ fit_quantile(X[tr], pv[tr], q), 0.0) for q in QS}
mid = np.maximum(X[te] @ w_mid, 0.0)
truth = pv[te]
day = truth > 1.0

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 两天的曲线
n_show = 2 * STEPS_PER_DAY
t = np.arange(n_show) / STEPS_PER_DAY * 24
a.fill_between(t, pred[0.1][:n_show], pred[0.9][:n_show], color=C["z"], alpha=0.18,
               label=T("10%—90% 区间", "10th–90th percentile band"))
a.fill_between(t, pred[0.25][:n_show], pred[0.75][:n_show], color=C["z"], alpha=0.28,
               label=T("25%—75% 区间", "25th–75th band"))
a.plot(t, truth[:n_show], color=C["ink"], lw=2.0, label=T("实际出力", "actual output"))
a.plot(t, mid[:n_show], color=C["x"], lw=1.8, ls="--", label=T("点预测", "point forecast"))
a.set_xlabel(T("时间（小时，连续两天）", "time (hours, two consecutive days)"))
a.set_ylabel(T("光伏出力（kW）", "PV output (kW)"))
a.set_title(T("(a) 云一过，点预测就跟着抖；区间把这份不确定装了进去",
              "(a) clouds make the point forecast jitter; the band carries that uncertainty"),
            fontsize=10)
a.legend(fontsize=8, loc="upper left", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 覆盖率
pairs = [(0.05, 0.95, 90.0), (0.1, 0.9, 80.0), (0.25, 0.75, 50.0)]
nom, act, wid = [], [], []
for lo_q, hi_q, nominal in pairs:
    nom.append(nominal)
    act.append(coverage(truth[day], pred[lo_q][day], pred[hi_q][day]))
    wid.append(interval_width(pred[lo_q][day], pred[hi_q][day]))
xs = np.arange(len(pairs))
b.bar(xs - 0.2, nom, 0.38, color=C["muted"], label=T("名义覆盖率", "nominal coverage"))
b.bar(xs + 0.2, act, 0.38, color=C["x"], label=T("实际覆盖率", "observed coverage"))
for i, (nv, av, wv) in enumerate(zip(nom, act, wid)):
    b.annotate(f"{av:.1f}%", xy=(i + 0.2, av), xytext=(0, 4), textcoords="offset points",
               ha="center", fontsize=8.5, color=C["x"])
    b.annotate(T(f"平均宽 {wv:.0f} kW", f"mean width {wv:.0f} kW"),
               xy=(i, max(nv, av)), xytext=(0, 18), textcoords="offset points",
               ha="center", fontsize=8.5, color=C["ink"])
b.set_xticks(xs)
b.set_xticklabels([T(f"{int(n)}% 区间", f"{int(n)}% band") for n in nom], fontsize=9)
b.set_ylabel(T("覆盖率（%）", "coverage (%)"))
b.set_ylim(0, 136)
b.set_title(T("(b) 名义值是你要的，实际值才是你有的",
              "(b) nominal is what you asked for, observed is what you got"), fontsize=10)
b.annotate(T("区间越宽，盖得越住，但对调度越没用——所以覆盖率与宽度要一起报",
             "wider bands cover more but say less; report both"),
           xy=(0.5, 0.965), xycoords="axes fraction", ha="center", va="top",
           fontsize=8.5, color=C["accent"])
b.legend(fontsize=8, loc="upper right", bbox_to_anchor=(1.0, 0.90), framealpha=0.92)
b.grid(alpha=0.25, lw=0.5, axis="y")

fig.tight_layout()
figure(fig, "fig22_1_1")
