"""图 19.4.1：降维与可视化。(a) 机器人手 120 个抓取姿态的方差解释比：前两个主成分（协同）约占 86%；
(b) 200 件减速器在前两个主成分平面上的得分，叠加第 2 章的八份检测记录和六个项目的载荷箭头（双标图）；
(c) 方差大不等于有用：两类零件沿 x 方向散得很开，区分它们的却是方差小的 y 方向。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from _hand import postures
from _num import fix_sign
from _qc import N_I, RECORDS2, SHORT, SHORT_EN, X_I

fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(13.5, 4.5), gridspec_kw={"width_ratios": [0.9, 1.2, 1]})
Hc = postures()
Hc = Hc - Hc.mean(axis=0)
sh = np.linalg.svd(Hc, compute_uv=False)
r = sh ** 2 / np.sum(sh ** 2)
k = np.arange(1, 16)
a1.bar(k, 100 * r, color=BLUE, width=0.7)
a1.plot(k, 100 * np.cumsum(r), "o-", color=RED, ms=4, lw=1.4)
for i in (0, 1, 2):
    a1.text(k[i] + 0.4, 100 * np.cumsum(r)[i] - 7, f"{100 * np.cumsum(r)[i]:.0f}%", color=RED, fontsize=9)
a1.set_xlabel(T("主成分序号", "component"))
a1.set_ylabel(T("方差解释比 / %（折线为累计）", "explained variance / % (line: cumulative)"))
a1.set_xticks([1, 3, 5, 7, 9, 11, 13, 15])
a1.set_ylim(0, 105)
a1.set_title(T("(a) 15 个关节的机器人手", "(a) A 15-joint robot hand"), fontsize=11)

Xc = X_I - X_I.mean(axis=0)
s = Xc.std(axis=0, ddof=1)
Z = Xc / s
w, V = np.linalg.eigh(Z.T @ Z / (N_I - 1))
w, V = w[::-1], fix_sign(V[:, ::-1])
Tsc = Z @ V[:, :2]
a2.scatter(Tsc[:, 0], Tsc[:, 1], s=8, color=MUTED, alpha=0.5, lw=0, label=T("200 件受控产品", "200 in-control units"))
Tr = ((RECORDS2 - X_I.mean(axis=0)) / s) @ V[:, :2]
groups = [((0, 4), INK, T("正常（记录 1、5）", "normal (1, 5)")), ((1, 5), RED, T("轴承磨损（2、6）", "bearing wear (2, 6)")),
          ((2, 6), GREEN, T("齿轮偏心（3、7）", "gear eccentricity (3, 7)")), ((3, 7), BLUE, T("装配过紧（4、8）", "tight assembly (4, 8)"))]
for idx, col, lab in groups:
    a2.plot(Tr[list(idx), 0], Tr[list(idx), 1], "D", color=col, ms=7, label=lab)
    for i in idx:
        a2.text(Tr[i, 0] + 0.15, Tr[i, 1] + 0.12, str(i + 1), color=col, fontsize=9)
names = T(SHORT, SHORT_EN)
for j in range(6):
    v = 3.0 * V[j, :2]
    a2.annotate("", xy=v, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=ACC, lw=1.2))
    dy = {2: 0.22, 4: -0.3}.get(j, 0.05)
    a2.text(v[0] * 1.1 + 0.15, v[1] * 1.08 + dy, names[j], color=ACC, fontsize=8.5, ha="center")
a2.axhline(0, color=MUTED, lw=0.5)
a2.axvline(0, color=MUTED, lw=0.5)
a2.set_aspect("equal")
a2.set_xlabel(T(f"第一主成分得分 t₁（{100 * w[0] / 6:.0f}%）", f"score t₁ ({100 * w[0] / 6:.0f}%)"))
a2.set_ylabel(T(f"第二主成分得分 t₂（{100 * w[1] / 6:.0f}%）", f"score t₂ ({100 * w[1] / 6:.0f}%)"))
a2.legend(frameon=False, fontsize=7.8, loc="lower right")
a2.set_xlim(-4.5, 6.2)
a2.set_ylim(-4.6, 3.6)
a2.set_title(T("(b) 得分图与载荷箭头", "(b) Scores and loading arrows"), fontsize=11)

rng = np.random.default_rng(42)
A = np.c_[rng.normal(0, 1.5, 150), rng.normal(-0.5, 0.25, 150)]
B = np.c_[rng.normal(0, 1.5, 150), rng.normal(0.5, 0.25, 150)]
a3.plot(A[:, 0], A[:, 1], "o", color=BLUE, ms=3, alpha=0.7, label=T("合格件", "good parts"))
a3.plot(B[:, 0], B[:, 1], "o", color=RED, ms=3, alpha=0.7, label=T("偏心件", "eccentric parts"))
a3.annotate("", xy=(4.2, 0), xytext=(-4.2, 0), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.4))
a3.text(2.0, -1.55, T("第一主成分：两类混在一起", "PC 1: classes overlap"), fontsize=9, color=INK)
a3.annotate("", xy=(-3.6, 1.3), xytext=(-3.6, -1.3), arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.4))
a3.text(-3.4, 1.2, T("第二主成分：分得开", "PC 2: separates them"), fontsize=9, color=GREEN)
a3.set_xlim(-5, 5)
a3.set_ylim(-2, 2.8)
a3.set_aspect("equal")
a3.legend(frameon=False, fontsize=8.5, loc="upper right", ncol=2)
a3.set_title(T("(c) 方差大不等于有用", "(c) Large variance ≠ useful"), fontsize=11)
for a in (a1, a2, a3):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig19_4_1")
