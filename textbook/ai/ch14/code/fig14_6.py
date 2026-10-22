"""14.6 节的示意图。

图 14.6.1：（a）按置信度拒答：阈值一提高，自动放行的少了，放行出去的那些却更可靠；
（b）总代价随阈值的变化：放行一条错记录的代价越高，最省的那个阈值越严。
两张图用的是同一批合成检验报告（`_ch14.reports`），与算例 14.6.3、14.6.4 同一组数。
"""
import numpy as np

from _ch14 import read_fields, reports
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

N = 4000
recs, qual = reports(N, seed=0)
correct, conf = read_fields(recs, qual, seed=0)
rep_conf = conf.prod(1)
rep_ok = correct.all(1)
ths = np.linspace(0, 0.98, 200)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.2, 4.0))

cov = np.array([(rep_conf >= t).mean() * 100 for t in ths])
acc = np.array([rep_ok[rep_conf >= t].mean() * 100 if (rep_conf >= t).any() else np.nan for t in ths])
a.plot(ths, cov, color=C["z"], lw=1.8, label=T("自动放行的比例（覆盖率）", "auto-accepted share"))
a.plot(ths, acc, color=C["x"], lw=1.8, label=T("放行的那些里七个字段全对的比例", "accuracy among accepted"))
a.axhline(rep_ok.mean() * 100, color=C["muted"], lw=1.0, ls=":")
a.text(0.02, rep_ok.mean() * 100 + 1.5, T("全部放行时：全对的只有这么多", "accept everything"), fontsize=8, color=C["muted"])
a.set_xlabel(T("拒答阈值（一份报告的把握）", "reject threshold (report confidence)"))
a.set_ylabel("%")
a.set_title(T("(a) 拒答：放行得少，放行得准", "(a) Reject more, trust what passes"), fontsize=10)
a.legend(fontsize=8, loc="center left")
a.grid(alpha=0.25, lw=0.5)

C_REVIEW = 3.0
for ce, col in ((10.0, C["y"]), (20.0, C["z"]), (40.0, C["x"])):
    cost = np.array([((rep_conf >= t) & ~rep_ok).sum() * ce + (rep_conf < t).sum() * C_REVIEW for t in ths]) / 60
    b.plot(ths, cost, color=col, lw=1.8, label=T(f"放行一条错记录 = {ce:.0f} 分钟", f"error costs {ce:.0f} min"))
    i = int(np.argmin(cost))
    b.plot(ths[i], cost[i], "o", color=col, ms=7)
b.axhline(N * C_REVIEW / 60, color=C["muted"], lw=1.0, ls="--")
b.text(0.02, N * C_REVIEW / 60 + 4, T("全部人工复核", "review everything"), fontsize=8, color=C["muted"])
b.set_xlabel(T("拒答阈值", "reject threshold"))
b.set_ylabel(T("总工时（小时 / 4000 份）", "total hours per 4000 reports"))
b.set_title(T("(b) 错一条越贵，阈值定得越严", "(b) The costlier a mistake, the stricter the threshold"), fontsize=10)
b.legend(fontsize=8)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig14_6_1")
