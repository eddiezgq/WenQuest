"""19.5 节的示意图：遥感的划分口径。

图 19.5.1：（a）同一张"卫星图"的两种划分，白色是测试集；
（b）地物越成片，按像素随机划分高估得越厉害。
"""
import numpy as np

from _ch19 import knn_classify, satellite_tile, split_blocks, split_pixels
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N, PATCH = 96, 8
feat, cls, bid = satellite_tile(N, seed=0, patch=PATCH)

fig = plt.figure(figsize=(11.4, 4.6))
gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.45], wspace=0.3)
ax1, ax2, ax3 = (fig.add_subplot(gs[0, i]) for i in range(3))

# ---------------- (a)(b) 两种划分长什么样
cmap = plt.matplotlib.colors.ListedColormap([C["z"], C["y"], C["accent"]])
for ax, (name, tr_te, tag) in zip(
        (ax1, ax2),
        ((T("(a) 按像素随机划分", "(a) random pixel split"), split_pixels(len(cls), seed=0), "px"),
         (T("(b) 按区块划分", "(b) block split"), split_blocks(bid, seed=0), "bk"))):
    pic = cls.reshape(N, N).astype(float).copy()
    mask = np.zeros(len(cls), bool); mask[tr_te[1]] = True
    ax.imshow(pic, cmap=cmap, vmin=-0.5, vmax=2.5, interpolation="nearest")
    ax.imshow(np.where(mask.reshape(N, N), 1.0, np.nan), cmap="gray", vmin=0, vmax=1,
              alpha=0.85, interpolation="nearest")
    pred = knn_classify(feat[tr_te[0]], cls[tr_te[0]], feat[tr_te[1]])
    acc = float((pred == cls[tr_te[1]]).mean())
    ax.set_title(f"{name}\n{T('准确率', 'accuracy')} {acc:.3f}", fontsize=9.5)
    ax.set_xticks([]); ax.set_yticks([])
for ax in (ax1, ax2):
    ax.set_xlabel(T("颜色 = 地物类别，发白的是测试集",
                    "colour = class, washed-out = test set"), fontsize=8.5)
ax1.annotate(T("测试像素的旁边\n就是训练像素", "a training pixel sits\nright next to each test one"),
             xy=(0.52, 0.5), xycoords="axes fraction", fontsize=8.5, color=C["x"],
             ha="center", bbox=dict(fc="white", ec=C["x"], lw=0.8, alpha=0.9, pad=2.5))
ax2.annotate(T("整片扣出来\n这条路就断了", "whole patches held out\ncuts that path"),
             xy=(0.52, 0.5), xycoords="axes fraction", fontsize=8.5, color=C["z"],
             ha="center", bbox=dict(fc="white", ec=C["z"], lw=0.8, alpha=0.9, pad=2.5))

# ---------------- (c) 地物越成片，高估得越厉害
patches, px, bk = [], [], []
for patch in (2, 4, 8, 16):
    f2, c2, b2 = satellite_tile(N, seed=1, patch=patch)
    tr, te = split_pixels(len(c2), seed=0)
    px.append(float((knn_classify(f2[tr], c2[tr], f2[te]) == c2[te]).mean()))
    tr, te = split_blocks(b2, seed=0)
    bk.append(float((knn_classify(f2[tr], c2[tr], f2[te]) == c2[te]).mean()))
    patches.append(patch)
xi = np.arange(len(patches))
ax3.bar(xi - 0.19, px, 0.36, color=C["x"], label=T("按像素随机划分", "random pixel split"))
ax3.bar(xi + 0.19, bk, 0.36, color=C["z"], label=T("按区块划分", "block split"))
for i, (p, b_) in enumerate(zip(px, bk)):
    ax3.annotate(T(f"差 {(p - b_) * 100:.1f} 分", f"{(p - b_) * 100:.1f} pts"),
                 xy=(i, max(p, b_) + 0.03), fontsize=8.5, color=C["ink"], ha="center")
ax3.axhline(1 / 3, color=C["muted"], ls="--", lw=1.2)
ax3.annotate(T("瞎猜的水平", "chance level"), xy=(len(patches) - 0.6, 1 / 3 + 0.015),
             fontsize=8, color=C["muted"])
ax3.set_xticks(xi)
ax3.set_xticklabels([str(p) for p in patches])
ax3.set_xlabel(T("地物成片的尺度（像素）", "size of a land-cover patch (pixels)"))
ax3.set_ylabel(T("测试集上的准确率", "accuracy on the test set"))
ax3.set_ylim(0, 1.08)
ax3.set_title(T("(c) 地物越成片，随机划分高估得越厉害",
                "(c) The patchier the ground, the bigger the overestimate"), fontsize=10)
ax3.legend(fontsize=8.5, loc="upper left")
ax3.grid(alpha=0.25, lw=0.5, axis="y")

figure(fig, "fig19_5_1")
