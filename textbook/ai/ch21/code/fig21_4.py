"""21.3 节的图之二：划分口径第四次露面。

图 21.3.2：（a）三种划分下的准确率（中位与全距）；
（b）按时间划分为什么更难——故障是长出来的，后面那一段的故障更多、也更重。
"""
import numpy as np

from _ch21 import (features, logistic_acc, logistic_fit, make_runs, split_runs,
                   standardize)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_MACH, PER_MACH, SECONDS = 8, 8, 0.5
SEEDS = range(8)
runs = make_runs(N_MACH, PER_MACH, seconds=SECONDS, seed=0)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 三种划分
labels = {"random": T("按采集随机", "random by run"),
          "machine": T("按机床", "by machine"),
          "time": T("按时间（过去训、未来测）", "by time (past → future)")}
cols = {"random": C["muted"], "machine": C["z"], "time": C["x"]}
xs, meds, los, his = [], [], [], []
for i, how in enumerate(("random", "machine", "time")):
    accs = []
    for sd in SEEDS:
        tr, te = split_runs(runs, how, seed=sd)
        if not te or len({r["fault"] for r in tr}) < 2 or len({r["fault"] for r in te}) < 2:
            continue
        Xtr = np.array([features(r) for r in tr])
        Xte = np.array([features(r) for r in te])
        ytr = np.array([r["fault"] for r in tr], dtype=float)
        yte = np.array([r["fault"] for r in te], dtype=float)
        Xtr, Xte = standardize(Xtr, Xte)
        accs.append(logistic_acc(logistic_fit(Xtr, ytr), Xte, yte) * 100)
    xs.append(i)
    meds.append(float(np.median(accs)))
    los.append(float(np.min(accs)))
    his.append(float(np.max(accs)))
a.bar(xs, meds, 0.5, color=[cols[h] for h in ("random", "machine", "time")],
      yerr=[np.array(meds) - np.array(los), np.array(his) - np.array(meds)],
      capsize=4, ecolor=C["ink"])
for i, (m, lo, hi) in enumerate(zip(meds, los, his)):
    a.annotate(T(f"{m:.1f}%\n（{lo:.0f}—{hi:.0f}%）", f"{m:.1f}%\n({lo:.0f}–{hi:.0f}%)"),
               xy=(i, m), xytext=(0, 6), textcoords="offset points",
               ha="center", fontsize=8.5, color=C["ink"])
a.set_xticks(xs)
a.set_xticklabels([labels[h] for h in ("random", "machine", "time")], fontsize=9)
a.set_ylabel(T("测试准确率（%）", "test accuracy (%)"))
a.set_ylim(50, 112)
a.axhline(100, color=C["muted"], ls=":", lw=1.0)
a.set_title(T("(a) 同一个模型、同一批数据，换个划分就换个结论",
              "(a) one model, one dataset, three different verdicts"), fontsize=10)
a.annotate(T("竖线是 8 折的全距；按时间划分不含随机性，所以没有竖线",
             "bars show the range over 8 folds; the time split is deterministic"),
           xy=(0.5, -0.13), xycoords="axes fraction", ha="center",
           fontsize=8, color=C["muted"])
a.grid(alpha=0.25, lw=0.5, axis="y")

# ---------------- (b) 故障是长出来的
share = []
for k in range(PER_MACH):
    rs = [r for r in runs if r["t"] == k]
    share.append(float(np.mean([r["fault"] for r in rs])) * 100)
b.step(np.arange(PER_MACH), share, where="mid", color=C["x"], lw=2.4,
       label=T("这一轮采集里有故障的比例", "share of runs with a fault"))
b.fill_between(np.arange(PER_MACH), 0, share, step="mid", color=C["x"], alpha=0.14)
tr, te = split_runs(runs, "time", seed=0)
cut = min(r["t"] for r in te)
b.axvline(cut - 0.5, color=C["ink"], ls="--", lw=1.6)
b.annotate(T(f"训练 / 测试的分界\n训练段 {np.mean([r['fault'] for r in tr]) * 100:.0f}% 有故障，"
             f"测试段 {np.mean([r['fault'] for r in te]) * 100:.0f}%",
             "train/test cut"),
           xy=(0.2, 88), xytext=(0, 0), textcoords="offset points",
           ha="left", fontsize=8.5, color=C["ink"])
b.set_xlabel(T("第几轮采集（时间先后）", "run index (in time order)"))
b.set_ylabel(T("有故障的比例（%）", "share with a fault (%)"))
b.set_title(T("(b) 故障是长出来的：未来那一段更多、也更重",
              "(b) faults grow in: the later window has more, and worse"), fontsize=10)
b.set_ylim(-4, 104)
b.legend(fontsize=8, loc="upper left", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig21_3_2")
