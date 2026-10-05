"""11.3 节的示意图（数值同程序 11.3.1）。

图 11.3.1：（a）交并比与非极大值抑制：同一个缺陷上落了三个框，按得分从高到低保留，与已保留的框交并比超过阈值的被丢掉；
（b）阈值分割基线在合成数据上的查准率—查全率曲线（IoU 阈值 0.5），曲线下的面积就是平均精度。
"""
import numpy as np
from scipy import ndimage

from _ch11 import average_precision, dataset, nms
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, (a, b) = plt.subplots(1, 2, figsize=(12.0, 4.3))

# (a) NMS
boxes = [(10, 20, 70, 60), (16, 24, 76, 64), (22, 18, 82, 58), (120, 90, 170, 130)]
scores = [0.92, 0.85, 0.78, 0.66]
keep = set(nms(boxes, scores, 0.5))
gt = (14, 22, 74, 62)
a.add_patch(plt.Rectangle((gt[0], gt[1]), gt[2] - gt[0], gt[3] - gt[1], fc=C["y"], alpha=0.25, ec=C["y"], lw=1.4))
a.text(gt[0], gt[1] - 4, T("真值", "ground truth"), fontsize=8.5, color=C["y"])
for i, (bx, sc) in enumerate(zip(boxes, scores)):
    col = C["z"] if i in keep else C["muted"]
    a.add_patch(plt.Rectangle((bx[0], bx[1]), bx[2] - bx[0], bx[3] - bx[1], fc="none", ec=col,
                              lw=1.6 if i in keep else 1.0, ls="-" if i in keep else ":"))
    a.text(bx[2] + 2, bx[1] + 6, f"{sc:.2f}" + (T("（留）", " keep") if i in keep else T("（抑制）", " drop")),
           fontsize=8, color=col)
a.set_xlim(0, 200)
a.set_ylim(150, 0)
a.set_aspect("equal")
a.axis("off")
a.set_title(T("(a) 非极大值抑制（阈值 0.5）", "(a) Non-maximum suppression (IoU 0.5)"), fontsize=10)

# (b) PR 曲线
def detect(img, k=2.0):
    bg = ndimage.uniform_filter(img, 31)
    d = bg - img
    lab, n = ndimage.label(d > k * d.std())
    bx, sc = [], []
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < 20:
            continue
        ys, xs = np.nonzero(m)
        bx.append((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
        sc.append(float(d[m].mean() * np.sqrt(m.sum())))
    return bx, sc


pb, ps, gb = [], [], []
for s in dataset(120, start=5000):
    bx, sc = detect(s["image"])
    k = nms(bx, sc, 0.3)
    pb += [bx[i] for i in k]
    ps += [sc[i] for i in k]
    gb += s["boxes"]
mx = max(ps)
ap, prec, rec = average_precision(pb, [x / mx for x in ps], gb, 0.5)
b.step(rec, prec, where="post", color=C["z"], lw=1.8)
b.fill_between(rec, prec, step="post", color=C["z"], alpha=0.15)
b.set_xlabel(T("查全率", "recall"))
b.set_ylabel(T("查准率", "precision"))
b.set_xlim(0, 1)
b.set_ylim(0, 1.02)
b.set_title(T(f"(b) 阈值分割基线的 PR 曲线（AP = {ap:.2f}）", f"(b) PR curve of the threshold baseline (AP = {ap:.2f})"), fontsize=10)
b.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
figure(fig, "fig11_3_1")
