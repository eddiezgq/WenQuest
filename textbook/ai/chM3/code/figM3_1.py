"""M3.1 节的示意图。

图 M3.1.1：（a）一万个零件的"自然频率"图：真坏的只有 200 个，检出 180 个，却有 294 个好件被误判——
判为坏的 474 个里真坏的不到四成；（b）后验概率随不合格率变化：基数越低，"判坏"越不可信。
"""
import numpy as np

from _chM3 import P_BAD, SENS, SPEC, bayes
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N = 10000
bad = N * P_BAD
tp, fn = bad * SENS, bad * (1 - SENS)
fp, tn = (N - bad) * (1 - SPEC), (N - bad) * SPEC

fig, (a, b) = plt.subplots(1, 2, figsize=(11.0, 4.0))
labels = [T("真坏·判坏", "bad, flagged"), T("真坏·漏掉", "bad, missed"),
          T("好件·误判", "good, flagged"), T("好件·判好", "good, passed")]
vals = [tp, fn, fp, tn]
cols = [C["x"], C["accent"], C["y"], C["muted"]]
bars = a.barh(labels, vals, color=cols, height=0.6)
for r, val in zip(bars, vals):
    a.text(val + N * 0.012, r.get_y() + r.get_height() / 2, f"{val:.0f}", va="center", fontsize=9, color=C["ink"])
a.set_xscale("log")
a.set_xlim(1, N * 3)
a.set_xlabel(T("件数（一万个零件，对数坐标）", "count out of 10 000 (log scale)"))
a.set_title(T("(a) 判为坏件的 %d 个里，真坏的只有 %d 个" % (tp + fp, tp),
              "(a) Of %d flagged, only %d are really bad" % (tp + fp, tp)), fontsize=10)
a.grid(axis="x", alpha=0.25, lw=0.5)
a.invert_yaxis()

ps = np.logspace(-3.3, -0.3, 400)
post = np.array([bayes(p_bad=p) for p in ps]) * 100
b.semilogx(ps * 100, post, color=C["z"], lw=2)
b.axvline(P_BAD * 100, color=C["muted"], ls="--", lw=1.0)
b.plot([P_BAD * 100], [bayes() * 100], "o", color=C["x"], ms=7)
b.annotate(T(f"本线：{P_BAD*100:.0f}% → {bayes()*100:.0f}%", f"this line: {P_BAD*100:.0f}% → {bayes()*100:.0f}%"),
           (P_BAD * 100, bayes() * 100), textcoords="offset points", xytext=(12, -16), fontsize=9, color=C["x"])
b.axhline(50, color=C["accent"], ls=":", lw=1.2)
b.set_xlabel(T("不合格率（%，对数坐标）", "defect rate (%, log scale)"))
b.set_ylabel(T("判坏之后真坏的概率（%）", "P(bad | flagged) (%)"))
b.set_title(T("(b) 同一台检验机，结论随基数而变", "(b) Same detector, different base rate"), fontsize=10)
b.grid(alpha=0.25, lw=0.5, which="both")
fig.tight_layout()
figure(fig, "figM3_1_1")
