"""18.6 节的示意图。

图 18.6.1：（a）（b）（c）不校正、恰好校正、校正过度三张降维图；
（d）两个指标此消彼长——只看批次混合度会把一次彻底的失败判成成功。
"""
import numpy as np

from _ch18 import cells, correct_batch, mixing, neighbour_purity, pca
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

x, types, batch = cells(120, 60, seed=0, batch_shift=1.6, batch_p=(0.7, 0.5, 0.3))
MK = ("o", "s", "^")
COLS = (C["x"], C["y"], C["z"])

fig, axes = plt.subplots(1, 4, figsize=(14.6, 3.7))

for ax, n, title in zip(axes[:3], (0, 1, 3),
                        (T("(a) 不校正", "(a) no correction"),
                         T("(b) 恰好去掉批次方向", "(b) remove the batch direction"),
                         T("(c) 去掉三个方向（过度）", "(c) remove three (over-corrected)"))):
    z = pca(correct_batch(x, batch, n), 2)
    for k in range(3):
        for bz, fill in ((0, "full"), (1, "none")):
            sel = (types == k) & (batch == bz)
            ax.plot(z[sel, 0], z[sel, 1], MK[k], color=COLS[k], ms=4, lw=0,
                    mfc=COLS[k] if fill == "full" else "none", mew=0.9, alpha=0.85)
    ax.set_title(f"{title}\n" + T(f"纯度 {neighbour_purity(z, types):.2f}　混合度 {mixing(z, batch):.2f}",
                                  f"purity {neighbour_purity(z, types):.2f}  mixing {mixing(z, batch):.2f}"),
                 fontsize=9)
    ax.set_xticks([]); ax.set_yticks([])
axes[0].set_ylabel(T("实心 = 第 0 批，空心 = 第 1 批；形状/颜色 = 细胞类型",
                     "filled = batch 0, open = batch 1; shape/colour = cell type"), fontsize=7.5)

d = axes[3]
ns = (0, 1, 2, 3, 4)
pur = [neighbour_purity(pca(correct_batch(x, batch, n), 2), types) for n in ns]
mix = [mixing(pca(correct_batch(x, batch, n), 2), batch) for n in ns]
d.plot(ns, pur, "o-", color=C["y"], lw=2.0, ms=6, label=T("类型聚得好不好（纯度）", "cell-type purity"))
d.plot(ns, mix, "s--", color=C["z"], lw=1.8, ms=5, label=T("批次混得匀不匀", "batch mixing"))
d.axhline(1 / 3, color=C["y"], ls=":", lw=1.1)
d.annotate(T("瞎猜", "chance"), xy=(0.06, 0.345), fontsize=8, color=C["y"])
d.axhline(0.5, color=C["z"], ls=":", lw=1.1)
d.annotate(T("理想", "ideal"), xy=(0.06, 0.515), fontsize=8, color=C["z"])
d.set_xlabel(T("去掉了几个方向", "how many directions were removed"))
d.set_ylabel(T("指标值", "metric"))
d.set_xticks(ns)
d.set_ylim(0, 1.05)
d.set_title(T("(d) 只看混合度会把失败判成成功",
              "(d) Mixing alone certifies a total failure"), fontsize=9)
d.legend(fontsize=7.5, loc="upper right")
d.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig18_6_1")
