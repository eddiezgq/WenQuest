"""11.8 节的示意图（数据同程序 11.8.1）。

图 11.8.1：（a）合成的零件表面图像与标注：三类缺陷各一例，右上角是像素级掩码；最后一张是合格品。
（b）代价敏感的阈值：漏检一件缺陷品的代价远高于误判一件合格品时，总代价最小的阈值比“准确率最高”的阈值更靠左——
宁可多几次复检，也别放过一件。
"""
import numpy as np
from scipy import ndimage

from _ch11 import dataset, sample
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig = plt.figure(figsize=(12.4, 4.6))
gs = fig.add_gridspec(2, 5, width_ratios=[1, 1, 1, 1, 2.1], hspace=0.08, wspace=0.08)

# (a) 四个例子：三类缺陷各一 + 合格
picks = []
for kind in ("划痕", "压痕", "锈斑"):
    for seed in range(300, 900):
        s = sample(seed)
        if s["labels"] == [kind] and s["severity"][0] > 0.7:
            picks.append((kind, s))
            break
for seed in range(300, 900):
    s = sample(seed)
    if not s["labels"]:
        picks.append((T("合格", "OK"), s))
        break
names = {"划痕": T("划痕", "scratch"), "压痕": T("压痕", "dent"), "锈斑": T("锈斑", "rust")}
CROP = 110                                            # 截取缺陷附近的一小块，否则在书的尺寸上看不清
for i, (kind, s) in enumerate(picks):
    if s["boxes"]:
        bx = s["boxes"][0]
        cx, cy = (bx[0] + bx[2]) // 2, (bx[1] + bx[3]) // 2
    else:
        cx = cy = s["image"].shape[0] // 2
    x0 = int(np.clip(cx - CROP // 2, 0, s["image"].shape[1] - CROP))
    y0 = int(np.clip(cy - CROP // 2, 0, s["image"].shape[0] - CROP))
    sub = s["image"][y0:y0 + CROP, x0:x0 + CROP]
    ax = fig.add_subplot(gs[0, i])
    ax.imshow(sub, cmap="gray", vmin=float(sub.min()), vmax=float(sub.max()))
    ax.set_title(names.get(kind, kind), fontsize=9)
    ax.axis("off")
    for bx in s["boxes"]:
        ax.add_patch(plt.Rectangle((bx[0] - x0, bx[1] - y0), bx[2] - bx[0], bx[3] - bx[1], fc="none", ec=C["x"], lw=1.2))
    ax2 = fig.add_subplot(gs[1, i])
    ax2.imshow(s["mask"][y0:y0 + CROP, x0:x0 + CROP], cmap="gray_r", vmin=0, vmax=1)
    ax2.axis("off")
    if i == 0:
        ax2.set_title(T("像素级掩码", "pixel mask"), fontsize=8, color=C["muted"])

# (b) 代价曲线
def score(img):
    bg = ndimage.uniform_filter(img, 31)
    d = bg - img
    return float(ndimage.maximum_filter(d, 5).max() / max(d.std(), 1e-6))


test = dataset(200, start=500)
sc = np.array([score(s["image"]) for s in test])
lab = np.array([s["label"] != "无" for s in test])
C_MISS, C_FALSE = 50.0, 1.0
ts = np.linspace(sc.min(), sc.max(), 200)
cost = np.array([((~(sc >= t) & lab).sum() * C_MISS + ((sc >= t) & ~lab).sum() * C_FALSE) for t in ts])
acc = np.array([(((sc >= t) == lab).sum()) / len(test) for t in ts])
ax = fig.add_subplot(gs[:, 4])
ax.plot(ts, cost, color=C["x"], lw=1.8, label=T("总代价（元 / 200 件）", "total cost (per 200 parts)"))
ax.axvline(ts[int(np.argmin(cost))], color=C["x"], ls="--", lw=1.0)
ax2 = ax.twinx()
ax2.plot(ts, acc * 100, color=C["z"], lw=1.4, label=T("准确率（%）", "accuracy (%)"))
ax2.axvline(ts[int(np.argmax(acc))], color=C["z"], ls=":", lw=1.0)
ax.set_xlabel(T("判定阈值", "decision threshold"))
ax.set_ylabel(T("总代价", "total cost"), color=C["x"])
ax2.set_ylabel(T("准确率（%）", "accuracy (%)"), color=C["z"])
ax.set_title(T("(b) 代价最小与准确率最高的阈值不同", "(b) Min-cost and max-accuracy thresholds differ"), fontsize=10)
ax.grid(alpha=0.25, lw=0.5)
figure(fig, "fig11_8_1")
