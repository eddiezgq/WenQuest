"""12.6 节的示意图（数值同程序 12.6.1）。

图 12.6.1：（a）同一说话人与不同说话人两段语音的嵌入余弦相似度的分布：两堆分开得越远，越好认；
（b）阈值从低到高时，错误接受率（冒认通过）与错误拒绝率（本人被拒）此消彼长，交点就是等错误率。
"""
import numpy as np

from _ch12 import speaker_scores
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
same, diff = speaker_scores()                                # 与程序 12.6.1 共用同一组嵌入和同一种配对

fig, (a, b) = plt.subplots(1, 2, figsize=(12.0, 4.0))
bins = np.linspace(-0.6, 1.0, 60)
a.hist(diff, bins=bins, color=C["x"], alpha=0.55, density=True, label=T("不同说话人", "different speakers"))
a.hist(same, bins=bins, color=C["z"], alpha=0.55, density=True, label=T("同一说话人", "same speaker"))
a.set_xlabel(T("余弦相似度", "cosine similarity"))
a.set_ylabel(T("密度", "density"))
a.set_title(T("(a) 两类得分的分布", "(a) Score distributions"), fontsize=10)
a.legend(fontsize=9)
a.grid(alpha=0.25, lw=0.5)

ts = np.linspace(-0.4, 0.9, 300)
far = np.array([(diff >= t).mean() for t in ts]) * 100
frr = np.array([(same < t).mean() for t in ts]) * 100
i = int(np.argmin(np.abs(far - frr)))
b.plot(ts, far, color=C["x"], lw=1.8, label=T("错误接受率（冒认通过）", "false accept"))
b.plot(ts, frr, color=C["z"], lw=1.8, label=T("错误拒绝率（本人被拒）", "false reject"))
b.plot([ts[i]], [far[i]], "o", ms=5, color=C["ink"])
b.annotate(T(f"等错误率 {far[i]:.1f}%", f"EER {far[i]:.1f}%"), (ts[i], far[i]), textcoords="offset points",
           xytext=(10, 10), fontsize=9)
b.set_xlabel(T("判定阈值", "threshold"))
b.set_ylabel(T("错误率（%）", "error rate (%)"))
b.set_title(T("(b) 阈值与两种错误", "(b) Threshold and the two errors"), fontsize=10)
b.legend(fontsize=9)
b.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
figure(fig, "fig12_6_1")
