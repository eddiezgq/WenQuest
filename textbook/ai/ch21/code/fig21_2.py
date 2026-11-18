"""21.2 节的图：不良率与代价。

图 21.2.1：（a）同一个检测器，不良率一变查准率就塌——查全率与误判率一个没动；
（b）漏检与误判的代价比一变，最优阈值就跟着移；按“准确率最高”定的阈值在代价不对称时要多花多少。
"""
import numpy as np

from _ch21 import confusion, cost_of, metrics, sample_scores
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N, SEP, THR = 200000, 2.2, 1.1

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 不良率扫一遍
rates = np.array([0.20, 0.10, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 0.0005])
prec, rec, fpr = [], [], []
for r in rates:
    good, bad = sample_scores(N, float(r), sep=SEP, seed=1)
    m = metrics(confusion(good, bad, THR))
    prec.append(m["precision"] * 100)
    rec.append(m["recall"] * 100)
    fpr.append(m["fpr"] * 100)
a.semilogx(rates * 100, prec, "o-", color=C["x"], lw=2.2, ms=5,
           label=T("查准率", "precision"))
a.semilogx(rates * 100, rec, "s--", color=C["z"], lw=2.0, ms=4,
           label=T("查全率", "recall"))
a.semilogx(rates * 100, fpr, "^:", color=C["muted"], lw=1.8, ms=4,
           label=T("误判率", "false-positive rate"))
a.set_xlabel(T("不良率（%，对数轴）", "defect rate (%, log scale)"))
a.set_ylabel(T("百分比", "percent"))
a.set_title(T("(a) 检测器一个参数都没动，变的只是不良率",
              "(a) the detector never changed; only the defect rate did"), fontsize=10)
a.annotate(T(f"不良率从 20% 到 0.05%：\n查准率 {prec[0]:.0f}% → {prec[-1]:.1f}%，"
             f"而查全率与误判率几乎是平的",
             f"precision {prec[0]:.0f}% → {prec[-1]:.1f}%"),
           xy=(0.04, 0.55), xycoords="axes fraction", ha="left",
           fontsize=8.5, color=C["accent"])
a.legend(fontsize=8, loc="center right", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 代价与阈值
good, bad = sample_scores(N, 0.004, sep=SEP, seed=11)
grid = np.linspace(-1.0, 5.0, 301)
styles = ((1.0, C["muted"], "-"), (10.0, C["z"], "--"), (100.0, C["accent"], "-."),
          (1000.0, C["x"], ":"))
for miss, col, ls in styles:
    costs = np.array([cost_of(confusion(good, bad, float(t)), miss, 1.0) for t in grid])
    b.semilogy(grid, costs / costs.min(), ls, color=col, lw=2.0,
               label=T(f"漏检:误判 = {miss:.0f}:1", f"miss:false = {miss:.0f}:1"))
    i = int(np.argmin(costs))
    b.plot([grid[i]], [1.0], "o", color=col, ms=8, zorder=3)
# 按"准确率最高"定的阈值
accs = [metrics(confusion(good, bad, float(t)))["accuracy"] for t in grid]
acc_thr = float(grid[int(np.argmax(accs))])
b.axvline(acc_thr, color=C["y"], lw=1.6, ls="-")
c100 = np.array([cost_of(confusion(good, bad, float(t)), 100.0, 1.0) for t in grid])
pen = c100[int(np.argmin(np.abs(grid - acc_thr)))] / c100.min()
b.annotate(T(f"按“准确率最高”定的阈值 {acc_thr:+.2f}：\n"
             f"在 100:1 的车间里要多花 {pen:.1f} 倍",
             f"accuracy-optimal threshold costs {pen:.1f}× more at 100:1"),
           xy=(acc_thr, pen), xytext=(-10, 30), textcoords="offset points",
           ha="right", fontsize=8.5, color=C["y"],
           arrowprops=dict(arrowstyle="->", color=C["y"], lw=1.0))
b.set_xlabel(T("判定阈值", "decision threshold"))
b.set_ylabel(T("总代价 ÷ 该代价比下的最小代价", "total cost ÷ its own minimum"))
b.set_title(T("(b) 阈值是经济决策，不是统计决策",
              "(b) the threshold is an economic decision"), fontsize=10)
b.legend(fontsize=8, loc="upper center", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig21_2_1")
