"""22.1 节的图之二：时间序列的两种泄漏。

图 22.1.2：（a）特征里藏着答案——换哪种划分都看不出来，两边一起变好看；
（b）划分把近亲分到两边——只有按时间划分才看得出来，而且模型越能记差得越多。
"""
import numpy as np

from _ch22 import (STEPS_PER_DAY, cloud_factor, design_matrix, fit_ls, pv_series,
                   split_random, split_time)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_DAYS, WIN = 60, 8

pv = pv_series(N_DAYS, seed=0)
cl = cloud_factor(N_DAYS, seed=0)
g = np.random.default_rng(5)
X0 = design_matrix(N_DAYS, np.clip(cl + 0.12 * g.normal(0, 1, len(cl)), 0, 1))
n = len(pv)
day = pv > 1.0


def causal_roll(x, k):
    past = np.concatenate([np.zeros(1), x[:-1]])
    return np.convolve(past, np.ones(k) / k, mode="full")[:len(x)]


X_causal = np.column_stack([X0, causal_roll(pv, WIN), causal_roll(pv, WIN * 3)])
X_center = np.column_stack([X0,
                            np.convolve(pv, np.ones(WIN) / WIN, mode="same"),
                            np.convolve(pv, np.ones(WIN * 3) / (WIN * 3), mode="same")])


def rmse_ls(X, tr, te):
    w = fit_ls(X[tr], pv[tr])
    p = np.maximum(X[te] @ w, 0.0)
    m = day[te]
    return float(np.sqrt(np.mean((p[m] - pv[te][m]) ** 2)))


def rmse_nn(X, tr, te):
    Xt = X[tr]
    mu, sd = Xt.mean(0), Xt.std(0) + 1e-9
    A, B = (Xt - mu) / sd, (X[te] - mu) / sd
    pred = np.array([pv[tr][int(np.argmin(((A - b) ** 2).sum(axis=1)))] for b in B])
    m = day[te]
    return float(np.sqrt(np.mean((pred[m] - pv[te][m]) ** 2)))


tr_t, te_t = split_time(n, 0.25, gap=0)
vals = {
    "causal": (float(np.median([rmse_ls(X_causal, *split_random(n, 0.25, seed=s))
                                for s in range(5)])), rmse_ls(X_causal, tr_t, te_t)),
    "center": (float(np.median([rmse_ls(X_center, *split_random(n, 0.25, seed=s))
                                for s in range(5)])), rmse_ls(X_center, tr_t, te_t)),
}
nn = (float(np.median([rmse_nn(X_causal, *split_random(n, 0.25, seed=s)) for s in range(3)])),
      rmse_nn(X_causal, tr_t, te_t))

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 第一种泄漏
xs = np.arange(2)
rand = [vals["causal"][0], vals["center"][0]]
timed = [vals["causal"][1], vals["center"][1]]
a.bar(xs - 0.19, rand, 0.36, color=C["muted"], label=T("随机划分", "random split"))
a.bar(xs + 0.19, timed, 0.36, color=C["x"], label=T("按时间划分", "time-ordered split"))
for i in range(2):
    a.annotate(f"{rand[i]:.1f}", xy=(i - 0.19, rand[i]), xytext=(0, 4),
               textcoords="offset points", ha="center", fontsize=8.5, color=C["ink"])
    a.annotate(f"{timed[i]:.1f}", xy=(i + 0.19, timed[i]), xytext=(0, 4),
               textcoords="offset points", ha="center", fontsize=8.5, color=C["x"])
a.set_xticks(xs)
a.set_xticklabels([T("滑动特征只用过去\n（因果，上线时拿得到）",
                     "causal window\n(available at run time)"),
                   T("滑动特征取居中窗口\n（含当前点，上线时拿不到）",
                     "centred window\n(not available at run time)")], fontsize=9)
a.set_ylabel(T("白天的均方根误差（kW）", "daylight RMSE (kW)"))
a.set_ylim(0, max(rand + timed) * 1.42)
a.set_title(T("(a) 特征里藏着答案：两种划分一起变好看",
              "(a) the answer hides in the features: both splits look better"), fontsize=10)
a.annotate(T("↓ 两根都矮了一截——换划分口径查不出这一种",
             "↓ both bars drop — changing the split cannot catch this one"),
           xy=(1, max(rand + timed) * 1.26), ha="center", fontsize=8.5, color=C["accent"])
a.legend(fontsize=8, loc="upper left", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5, axis="y")

# ---------------- (b) 第二种泄漏：测试点的“最像的那条”离它多远
def neighbour_lag(X, tr, te):
    """每个白天的测试点，在训练集里最像的那条**在时间上离它多远**（小时）。"""
    Xt = X[tr]
    mu, sd = Xt.mean(0), Xt.std(0) + 1e-9
    A, B = (Xt - mu) / sd, (X[te] - mu) / sd
    out = []
    for k, bvec in enumerate(B):
        if not day[te][k]:
            continue
        j = int(np.argmin(((A - bvec) ** 2).sum(axis=1)))
        out.append(abs(int(tr[j]) - int(te[k])) / STEPS_PER_DAY * 24.0)
    return np.array(out)


lag_rand = neighbour_lag(X_causal, *split_random(n, 0.25, seed=0))
lag_time = neighbour_lag(X_causal, tr_t, te_t)
bins = np.array([0, 0.5, 2, 6, 12, 24, 48, 24 * 7, 24 * 60])
centers = np.arange(len(bins) - 1)
h_r = np.histogram(lag_rand, bins=bins)[0] / len(lag_rand) * 100
h_t = np.histogram(lag_time, bins=bins)[0] / len(lag_time) * 100
b.bar(centers - 0.19, h_r, 0.36, color=C["muted"],
      label=T(f"随机划分（{nn[0]:.1f} kW）", f"random split ({nn[0]:.1f} kW)"))
b.bar(centers + 0.19, h_t, 0.36, color=C["x"],
      label=T(f"按时间划分（{nn[1]:.1f} kW）", f"time split ({nn[1]:.1f} kW)"))
b.set_xticks(centers)
b.set_xticklabels(["<0.5", "0.5–2", "2–6", "6–12", "12–24", "1–2", "2–7", ">7"], fontsize=8.5)
b.set_xlabel(T("最像的那条训练样本，在时间上离测试点多远（小时 / 天）",
                "time distance to the nearest training sample (hours / days)"))
b.set_ylabel(T("占白天测试点的比例（%）", "share of daylight test points (%)"))
b.set_ylim(0, 108)
b.set_title(T("(b) 近亲分到两边：随机划分时，最像的那条就在隔壁",
              "(b) near-duplicates: under a random split the twin sits next door"),
            fontsize=10)
b.annotate(T(f"随机划分有 {h_r[0]:.0f}% 的测试点，双胞胎就在半小时之内；按时间划分一个也没有。\n"
             f"可误差只差 {nn[1] / nn[0]:.1f} 倍——因为日变化天天重复，昨天的同一时刻\n"
             f"本来就是个像样的替身。没有这种重复形状的序列（慢漂移、工况切换），\n"
             f"同样的泄漏会要命。",
             f"{h_r[0]:.0f}% of test points have a twin within 30 min under a random split, "
             f"none under a time split;\nerror still differs only {nn[1] / nn[0]:.1f}× because "
             f"the daily shape repeats. On series without\nthat repetition the same leak bites "
             f"hard."),
           xy=(0.03, 0.62), xycoords="axes fraction", ha="left", va="top",
           fontsize=8.2, color=C["accent"])
b.legend(fontsize=8, loc="upper left", bbox_to_anchor=(0.02, 0.98), framealpha=0.92)
b.grid(alpha=0.25, lw=0.5, axis="y")

fig.tight_layout()
figure(fig, "fig22_1_2")
