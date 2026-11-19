"""23.3 节的图之二：预测误差的平均与尾巴。

图 23.3.1：（a）3 s 预测的误差分布——平均、95 分位、99 分位、最大值标在同一张图上，
看清“平均值在最左边那一小堆里”；（b）预测时域拉长时，平均、99 分位、最大值各自怎么长，
以及**最坏/平均的比值在短时域上最大**。
"""
import numpy as np

from _ch23 import DT, fit_ls, lead_track, pred_features
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N = 24000
s, v_lead = lead_track(N, DT, seed=9)
F = pred_features(s, v_lead)


def errors(horizon_s: float) -> np.ndarray:
    h = int(horizon_s / DT)
    truth = s[h:]
    X = F[:len(truth)]
    y = truth - s[:len(truth)]
    c = int(len(y) * 0.6)
    w = fit_ls(X[:c], y[:c])
    return np.abs(s[c:len(truth)] + X[c:] @ w - truth[c:])


e3 = errors(3.0)
fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 误差分布与它的尾巴
a.hist(e3, bins=90, color=C["z"], alpha=0.55, log=True)
marks = [(float(e3.mean()), C["x"], T("平均", "mean")),
         (float(np.quantile(e3, 0.95)), C["y"], T("95 分位", "95th pct")),
         (float(np.quantile(e3, 0.99)), C["accent"], T("99 分位", "99th pct")),
         (float(e3.max()), C["ink"], T("最大", "max"))]
a.set_ylim(0.7, 10 ** 4.3)
for i, (x, col, name) in enumerate(marks):
    a.axvline(x, color=col, lw=1.8, ls="--")
    right = i < len(marks) - 1
    a.annotate(f"{name} {x:.2f} m", xy=(x, 10 ** (3.95 - 0.33 * i)),
               xytext=(6 if right else -6, 0), textcoords="offset points",
               ha="left" if right else "right", fontsize=8.5, color=col, va="center")
a.set_xlabel(T("3 s 预测的位移误差（m）", "displacement error of the 3 s prediction (m)"))
a.set_ylabel(T("帧数（对数）", "frames (log scale)"))
a.set_title(T("(a) 平均值落在最左边那一小堆里", "(a) the mean sits in the left-most pile"),
            fontsize=10)
a.annotate(T(f"最坏是平均的 {e3.max() / e3.mean():.0f} 倍——\n"
             f"而规划吃的是最坏那一档",
             f"the worst is {e3.max() / e3.mean():.0f}$\\times$ the mean;\n"
             f"planning eats the worst one"),
           xy=(0.97, 0.47), xycoords="axes fraction", ha="right", va="top",
           fontsize=8.5, color=C["accent"])
a.grid(alpha=0.25, lw=0.5, axis="y")

# ---------------- (b) 时域一拉长
hs = np.array([0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0])
mean_, p99_, max_ = [], [], []
for h in hs:
    e = errors(float(h))
    mean_.append(e.mean())
    p99_.append(np.quantile(e, 0.99))
    max_.append(e.max())
mean_, p99_, max_ = np.array(mean_), np.array(p99_), np.array(max_)

b.plot(hs, max_, "o-", color=C["ink"], lw=2.2, ms=6, label=T("最大值", "max"))
b.plot(hs, p99_, "s-", color=C["accent"], lw=2.0, ms=5.5, label=T("99 分位", "99th pct"))
b.plot(hs, mean_, "^-", color=C["x"], lw=2.2, ms=6, label=T("平均", "mean"))
b.fill_between(hs, mean_, max_, color=C["muted"], alpha=0.12)
b.set_xlabel(T("预测时域（s）", "prediction horizon (s)"))
b.set_ylabel(T("位移误差（m）", "displacement error (m)"))
b.set_title(T("(b) 尾巴先见底，平均值还在长", "(b) the tail saturates while the mean keeps growing"),
            fontsize=10)
b.legend(fontsize=8, loc="center right", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5)

b2 = b.twinx()
ratio = max_ / mean_
b2.plot(hs, ratio, color=C["z"], lw=1.8, ls=":")
b2.set_ylabel(T("最坏 / 平均（虚线）", "worst / mean (dotted)"), color=C["z"])
b2.tick_params(axis="y", labelcolor=C["z"])
b2.set_ylim(0, ratio.max() * 1.25)
for i in (0, len(hs) - 1):
    b2.annotate(f"{ratio[i]:.0f}×", xy=(hs[i], ratio[i]), xytext=(6 if i == 0 else -6, 4),
                textcoords="offset points", ha="left" if i == 0 else "right",
                fontsize=8.5, color=C["z"])
b2.annotate(T("“最坏 / 平均”在短时域上最大——\n而紧急制动用的正是短时域",
              "worst/mean peaks at\nshort horizons — the ones\n"
              "emergency braking uses"),
            xy=(0.95, 0.98), xycoords="axes fraction", ha="right", va="top",
            fontsize=8.5, color=C["z"])

fig.tight_layout()
figure(fig, "fig23_3_1")
