"""图 17.4.1：由秩确定若尔当块（程序 17.4.1）。(a) 特征值 2 的“点图”：第 k 行的点数 = 大小 ≥ k 的块数 = r_{k−1} − r_k，
r_k = rank(A − 2I)^k = 6, 4, 3, 2, 2；每一列是一个若尔当块（大小 3 和 1）；(b) 加加速度轴三个闭环极点都在 −10（一个 3 阶若尔当块）时，
1 mm 位置误差的衰减 (1 + 10t + 50t²)e^{−10t}，与单个极点 e^{−10t} 比较。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.0), gridspec_kw={"width_ratios": [1, 1.3]})
r = [6, 4, 3, 2, 2]
for k in range(1, 4):
    nk = r[k - 1] - r[k]
    for j in range(nk):
        a1.plot(j, -k, "o", color=BLUE, ms=18)
    a1.text(-0.9, -k, f"k = {k}：{r[k - 1]} − {r[k]} = {nk}", ha="right", va="center", fontsize=10, color=INK)
for j, sz in enumerate((3, 1)):
    a1.text(j, -4, T(f"J{'₃₁'[j]}(2)", f"J{'₃₁'[j]}(2)"), ha="center", fontsize=11, color=RED)
a1.set_xlim(-4.2, 2); a1.set_ylim(-4.6, -0.3); a1.axis("off")
a1.set_title(T("(a) 特征值 2 的点图：每列一个块", "(a) Dot diagram for λ = 2: one block per column"), fontsize=11)
t = np.linspace(0, 1, 500)
a2.plot(t, (1 + 10 * t + 50 * t ** 2) * np.exp(-10 * t), color=RED, lw=2, label=T("三重极点 −10（若尔当块 J₃）", "triple pole −10 (block J₃)"))
a2.plot(t, np.exp(-10 * t), color=BLUE, lw=1.6, ls="--", label=T("单个极点 e^(−10t)", "single pole e^(−10t)"))
a2.axhline(0.01, color=ACC, lw=0.8, ls=":")
a2.text(0.62, 0.03, "1%", color=ACC, fontsize=9)
a2.set_xlabel(T("t / s", "t / s")); a2.set_ylabel(T("位置误差 / mm", "position error / mm"))
a2.legend(frameon=False, fontsize=9)
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
a2.set_title(T("(b) 重极点使响应变慢", "(b) A repeated pole slows the response"), fontsize=11)
fig.tight_layout()
figure(fig, "fig17_4_1")
