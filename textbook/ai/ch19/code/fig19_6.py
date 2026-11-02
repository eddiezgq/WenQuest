"""19.6 节的示意图：风电场明天发多少电。

图 19.6.1：（a）风功率曲线与"同样 1 m/s 的风速误差在不同风速上差多少"；
（b）确定性预报答不了"低于切入风速的概率"，集合能答。
"""
import numpy as np

from _ch19 import WIND, power_curve, power_error, wind_cases
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.4))

# ---------------- (a) 功率曲线 + 误差放大
vs = np.linspace(0, 27, 600)
a.plot(vs, power_curve(vs) * 100, "-", color=C["ink"], lw=2.4,
       label=T("风功率曲线", "power curve"))
a.axvline(WIND["cut_in"], color=C["muted"], ls=":", lw=1.2)
a.axvline(WIND["rated"], color=C["muted"], ls=":", lw=1.2)
a.axvline(WIND["cut_out"], color=C["muted"], ls=":", lw=1.2)
for xv, lab in ((WIND["cut_in"], T("切入", "cut-in")),
                (WIND["rated"], T("额定", "rated")),
                (WIND["cut_out"], T("切出", "cut-out"))):
    a.annotate(f"{lab} {xv:g} m/s", xy=(xv, 104), fontsize=8, color=C["muted"],
               ha="center")
a2 = a.twinx()
dv = np.linspace(0.01, 23.9, 600)   # 到切出为止：越过切出是停机，那是另一回事，正文里说
a2.plot(dv, power_error(dv, 1.0) * 100, "-", color=C["x"], lw=2.0,
        label=T("风速多报 1 m/s 造成的发电量误差",
                "power error from a 1 m/s speed error"))
worst = dv[int(np.argmax(power_error(dv, 1.0)))]
a2.plot([worst], [power_error(np.array([worst]), 1.0)[0] * 100], "o", color=C["x"],
        ms=7, mec="white", mew=1.0, zorder=5)
a2.annotate(T(f"最吃亏在 {worst:.0f} m/s 附近：\n差 {power_error(np.array([worst]), 1.0)[0] * 100:.0f} 个百分点",
              f"worst near {worst:.0f} m/s:\n{power_error(np.array([worst]), 1.0)[0] * 100:.0f} points"),
            xy=(worst, power_error(np.array([worst]), 1.0)[0] * 100),
            xytext=(13.0, 20), fontsize=8.5, color=C["x"],
            arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.0))
a2.annotate(T("额定以上再多刮风\n也不多发电", "above rated, more wind\nbuys nothing"),
            xy=(16, 1), xytext=(14.5, 7.5), fontsize=8.5, color=C["muted"],
            arrowprops=dict(arrowstyle="->", color=C["muted"], lw=1.0))
a.set_xlabel(T("风速（米每秒）", "wind speed (m/s)"))
a.set_ylabel(T("发电量（占额定功率 %）", "power (% of rated)"))
a2.set_ylabel(T("发电量误差（百分点）", "power error (percentage points)"), color=C["x"])
a2.tick_params(axis="y", colors=C["x"])
a.set_ylim(0, 112); a2.set_ylim(0, 32)
a.set_title(T("(a) 三次方关系：同样的风速误差，在中段最吃亏",
              "(a) A cubic law: the same speed error hurts most mid-curve"), fontsize=10)
a.legend(fontsize=8.5, loc="center left")
a2.legend(fontsize=8.5, loc="upper left", bbox_to_anchor=(0.0, 0.88))
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 电网真正要问的那个问题
N, M, TRUE_SD = 20000, 50, 1.6
g = np.random.default_rng(0)
sig = g.normal(0, 2.0, N) + 8.0
truth = sig + g.normal(0, TRUE_SD, N)
det = sig
ens = sig[None, :] + g.normal(0, TRUE_SD, (M, N))
occ = truth < WIND["cut_in"]
p_ens = (ens < WIND["cut_in"]).mean(0)
p_det = (det < WIND["cut_in"]).astype(float)
bq = lambda p: float(((p - occ) ** 2).mean())
names = [T("确定性预报\n（只能答是/否）", "deterministic\n(yes/no only)"),
         T("每次都报气候概率", "climatology every time"),
         T("集合给的概率", "probability from the ensemble")]
vals = [bq(p_det), bq(np.full(N, occ.mean())), bq(p_ens)]
cols = [C["x"], C["muted"], C["z"]]
b.bar(np.arange(3), vals, 0.56, color=cols)
for i, val in enumerate(vals):
    b.annotate(f"{val:.4f}", xy=(i, val + 0.0008), fontsize=9.5, color=C["ink"], ha="center")
b.set_xticks(np.arange(3)); b.set_xticklabels(names, fontsize=8.5)
b.set_ylabel(T("Brier 分数（越小越好）", "Brier score (lower is better)"))
b.set_ylim(0, max(vals) * 1.28)
b.annotate(T(f"确定性预报与集合均值的 RMSE 几乎一样"
             f"（{np.sqrt(((det - truth) ** 2).mean()):.2f} 对 "
             f"{np.sqrt(((ens.mean(0) - truth) ** 2).mean()):.2f}）——\n"
             f"光看 RMSE 看不出集合的价值",
             "deterministic and ensemble-mean RMSE are nearly identical — "
             "RMSE cannot show the ensemble's value"),
           xy=(0.03, 0.80), xycoords="axes fraction", fontsize=8.5, color=C["ink"])
b.annotate(T(f"问题：明天风速低于切入（{WIND['cut_in']:g} m/s）的概率是多少？"
             f"实际发生 {occ.mean() * 100:.2f}%",
             f"question: probability of falling below cut-in? it happens {occ.mean() * 100:.2f}% "
             f"of the time"),
           xy=(0.03, 0.93), xycoords="axes fraction", fontsize=9, color=C["ink"])
b.set_title(T("(b) 电网要的是概率，不是一个数",
              "(b) The grid needs a probability, not a single number"), fontsize=10)
b.grid(alpha=0.25, lw=0.5, axis="y")

fig.tight_layout()
figure(fig, "fig19_6_1")
