"""M1.6 节的示意图。

图 M1.6.1：奇异值分解的几何意义——任何矩阵作用在单位圆上，都得到一个椭圆：先转（Vᵀ）、
再沿两个主轴拉伸（Σ）、再转（U）。椭圆的两个半轴长就是两个奇异值。
图 M1.6.2：（a）零件表面图的奇异值谱（对数坐标）：前 3 个是结构，后面一长串是噪声；
（b）用前 k 个奇异值重建的相对误差，以及要存多少数。
"""
import numpy as np

from _chM1 import surface
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

# ---------------------------------------------------------------- 图 M1.6.1
A = np.array([[1.6, 0.9], [0.2, 1.1]])
U, S, Vt = np.linalg.svd(A)
t = np.linspace(0, 2 * np.pi, 241)
circle = np.c_[np.cos(t), np.sin(t)].T
# 每一步都画出同两个标记向量（V 的两列）的去向，否则"转了一下"在圆上看不出来
V = Vt.T
mats = [np.eye(2), Vt, np.diag(S) @ Vt, A]
names = [T("单位圆与两个标记方向", "unit circle, two marked directions"),
         T("$V^{T}$：转到坐标轴上", "$V^{T}$: rotate onto the axes"),
         T("$\\Sigma$：沿两轴各拉伸一次", "$\\Sigma$: stretch along the axes"),
         T("$U$：再转一下，得到椭圆", "$U$: rotate again — an ellipse")]
fig, axes = plt.subplots(1, 4, figsize=(13.0, 3.4))
for ax, Mk, ttl in zip(axes, mats, names):
    pts = Mk @ circle
    ax.plot(pts[0], pts[1], color=C["z"], lw=1.8)
    for k, col in ((0, C["x"]), (1, C["accent"])):
        q = Mk @ V[:, k]
        ax.annotate("", xy=tuple(q), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.8))
    ax.set_title(ttl, fontsize=9.5)
    ax.set_aspect("equal")
    ax.set_xlim(-2.4, 2.4)
    ax.set_ylim(-2.4, 2.4)
    ax.grid(alpha=0.25, lw=0.5)
    ax.axhline(0, color=C["muted"], lw=0.6)
    ax.axvline(0, color=C["muted"], lw=0.6)
# 在最后一幅上标出两个奇异值（椭圆的半轴）
ax = axes[-1]
for k, col in ((0, C["x"]), (1, C["accent"])):
    vlen = A @ V[:, k]
    ax.annotate("", xy=tuple(vlen), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.8))
    ax.text(vlen[0] * 1.08, vlen[1] * 1.08, f"$\\sigma_{k + 1}={S[k]:.2f}$", color=col, fontsize=9)
fig.tight_layout()
figure(fig, "figM1_6_1")

# ---------------------------------------------------------------- 图 M1.6.2
img = surface(96)
s = np.linalg.svd(img, compute_uv=False)
fro = np.linalg.norm(img, "fro")
ks = np.arange(1, 25)
err = [float(np.sqrt((s[k:] ** 2).sum()) / fro * 100) for k in ks]
keep = [k * (img.shape[0] + img.shape[1] + 1) / img.size * 100 for k in ks]
noise = np.linalg.norm(img - surface(96, noise=0), "fro") / fro * 100

fig, (a, b) = plt.subplots(1, 2, figsize=(11.0, 3.8))
a.semilogy(range(1, 21), s[:20], "o-", color=C["z"], lw=1.6, ms=5)
a.axvline(3.5, color=C["muted"], ls="--", lw=1.0)
a.text(3.8, s[0] / 3, T("左边 3 个是结构，右边是噪声", "3 structural values; the rest is noise"),
       fontsize=9, color=C["ink"])
a.set_xlabel(T("第几个奇异值", "index"))
a.set_ylabel(T("奇异值", "singular value"))
a.set_title(T("(a) 奇异值谱", "(a) Singular values"), fontsize=10)
a.grid(alpha=0.25, lw=0.5)

b.plot(ks, err, "o-", color=C["z"], lw=1.6, ms=4, label=T("重建的相对误差", "relative error"))
b.axhline(noise, color=C["x"], ls="--", lw=1.2, label=T("图里噪声本身的大小", "the noise itself"))
b.plot(ks, keep, "s-", color=C["accent"], lw=1.4, ms=4, label=T("要存的数（占原来的 %）", "numbers kept (% of original)"))
b.set_xlabel(T("保留前 k 个奇异值", "rank k"))
b.set_ylabel("%")
b.set_title(T("(b) 误差与存储", "(b) Error and storage"), fontsize=10)
b.legend(fontsize=9)
b.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
figure(fig, "figM1_6_2")
