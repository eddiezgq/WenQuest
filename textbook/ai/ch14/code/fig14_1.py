"""14.1 节的示意图。

图 14.1.1：（a）对齐之前，"图 × 文"的相似度矩阵上几乎没有结构；（b）学了两个投影之后，
配对的那一格（对角线）亮起来，说的是同一件事的图与文靠在一起；
（c）温度决定梯度压在"最像的那个负样本"上有多少：温度越低越集中。
"""
import numpy as np

from _ch14 import KINDS, l2, labels_of, pairs, train
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

NOISE = 0.8
xi, xt, a = pairs(6000, 0, noise=NOISE)
xi_t, xt_t, a_t = pairs(400, 9, noise=NOISE)
Wi, Wt, _ = train(xi, xt, dim=16, batch=256, steps=1800, temp=0.07, lr=0.9)

fig, (ax, bx, cx) = plt.subplots(1, 3, figsize=(13.2, 4.0))


# (a)(b) 同一批样本的"图 × 文"相似度矩阵：对齐之前几乎没有结构，对齐之后对角线亮起来
sel = np.lexsort((a_t[:, 1], a_t[:, 0]))[:40]            # 取 40 个样本，按零件、缺陷排好序
lab_sel = labels_of(a_t[sel])
zi_raw = l2(xi_t[sel][:, :16])
zt_raw = l2(xt_t[sel] @ np.eye(xt_t.shape[1], 16))       # 没学过的"同一个空间"：直接截断
s_before = zi_raw @ zt_raw.T
s_after = l2(xi_t[sel] @ Wi) @ l2(xt_t[sel] @ Wt).T
for axis, m, ttl in ((ax, s_before, T("(a) 对齐之前：图与文各说各话", "(a) Before: image and text are unrelated")),
                     (bx, s_after, T("(b) 对齐之后：配对的那一格亮起来", "(b) After: the matching cell lights up"))):
    im = axis.imshow(m, cmap="RdYlBu_r", vmin=-1, vmax=1)
    axis.set_title(ttl, fontsize=10)
    axis.set_xlabel(T("文本（按零件、缺陷排序）", "text (sorted by part, defect)"))
    axis.set_ylabel(T("图像", "image"))
    axis.set_xticks([])
    axis.set_yticks([])
fig.colorbar(im, ax=bx, fraction=0.046, pad=0.04, label=T("余弦相似度", "cosine similarity"))

# (c) 温度
zi, zt = l2(xi_t @ Wi), l2(xt_t @ Wt)
temps = np.logspace(-2, 0, 25)
top, eff = [], []
for t in temps:
    s = (zi @ zt.T) / t
    p = np.exp(s - s.max(1, keepdims=True))
    p /= p.sum(1, keepdims=True)
    np.fill_diagonal(p, 0.0)
    p = p / np.maximum(p.sum(1, keepdims=True), 1e-12)
    top.append(np.sort(p, axis=1)[:, -1].mean() * 100)
    eff.append(np.exp(-(p * np.log(np.maximum(p, 1e-12))).sum(1)).mean())
cx.semilogx(temps, top, color=C["x"], lw=1.8, label=T("最像的那个负样本占的梯度权重（%）", "weight on hardest negative (%)"))
cx.axvline(0.07, color=C["muted"], lw=1.0, ls="--")
cx.text(0.075, 60, T("CLIP 的初值 0.07", "CLIP init 0.07"), fontsize=8, color=C["muted"])
cx.set_xlabel(T("温度", "temperature"))
cx.set_ylabel(T("梯度权重（%）", "gradient weight (%)"), color=C["x"])
cx2 = cx.twinx()
cx2.semilogx(temps, eff, color=C["z"], lw=1.8)
cx2.set_yscale("log")
cx2.set_ylabel(T("等效上有几个负样本在起作用（右轴）", "effective negatives (right axis)"), color=C["z"])
cx.set_title(T("(c) 温度越低，梯度越集中在最难的那个上", "(c) Lower temperature concentrates the gradient"), fontsize=10)
cx.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig14_1_1")
