"""图 18.4.1：最好的秩 1 逼近把椭圆压成沿 u₁ 的线段；图 18.4.2：齿轮图像的前三层 σᵢuᵢvᵢᵀ 与它们的和。"""
import numpy as np

from _arm import svd_fixed
from _fig import GREEN, INK, MUTED, RED, T, arrow, axes_box, circle_pts, figure, plt
from _img import gear_image

A = np.array([[3.0, 0.0], [4.0, 5.0]])
U, s, V = svd_fixed(A)
A1 = s[0] * np.outer(U[:, 0], V[:, 0])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.0, 4.4))
for ax in (a1, a2):
    axes_box(ax, 7.2)
    ax.plot(*circle_pts(A), color=MUTED, lw=1.2, ls="--")
a1.plot(*circle_pts(A), color=INK, lw=1.6)
arrow(a1, s[0] * U[:, 0], RED, r"$\sigma_1\boldsymbol{u}_1$", (0.2, 0))
arrow(a1, s[1] * U[:, 1], GREEN, r"$\sigma_2\boldsymbol{u}_2$", (0.2, -0.6))
a1.set_title(T(r"$A$：单位圆的像是椭圆", r"$A$: the image is an ellipse"), fontsize=12)
P = circle_pts(A1)
a2.plot(P[0], P[1], color=RED, lw=3)
arrow(a2, s[0] * U[:, 0], RED, r"$\sigma_1\boldsymbol{u}_1$", (0.2, 0))
arrow(a2, s[1] * U[:, 1], GREEN, T(r"误差 $\sigma_2\boldsymbol{u}_2$", r"error $\sigma_2\boldsymbol{u}_2$"), (0.2, -0.6), lw=1.4)
a2.set_title(T(r"$A_1=\sigma_1\boldsymbol{u}_1\boldsymbol{v}_1^{\mathrm{T}}$：压成线段", r"$A_1=\sigma_1\boldsymbol{u}_1\boldsymbol{v}_1^{\mathrm{T}}$: flattened to a segment"), fontsize=12)
fig.tight_layout()
figure(fig, "fig18_4_1")

G = gear_image()
Ug, sg, Vgt = np.linalg.svd(G, full_matrices=False)
layers = [sg[i] * np.outer(Ug[:, i], Vgt[i]) for i in range(3)]
fig, axs = plt.subplots(1, 5, figsize=(13.5, 2.6))
items = [(layers[0], r"$\sigma_1\boldsymbol{u}_1\boldsymbol{v}_1^{\mathrm{T}}$"), (layers[1], r"$\sigma_2\boldsymbol{u}_2\boldsymbol{v}_2^{\mathrm{T}}$"),
         (layers[2], r"$\sigma_3\boldsymbol{u}_3\boldsymbol{v}_3^{\mathrm{T}}$"), (sum(layers), r"$A_3$"), (G, r"$A$")]
for ax, (M, name) in zip(axs, items):
    if name.startswith(r"$\sigma_1") or name in (r"$A_3$", r"$A$"):
        ax.imshow(M, cmap="gray", vmin=0, vmax=1, interpolation="nearest")
    else:
        m = np.abs(M).max()
        ax.imshow(M, cmap="RdBu_r", vmin=-m, vmax=m, interpolation="nearest")
    ax.set_title(name, fontsize=12)
    ax.set_xticks([])
    ax.set_yticks([])
fig.text(0.5, -0.04, T("第 2、3 层有正有负（红正蓝负），只能叠加在前面的层上使用", "Layers 2 and 3 have both signs (red +, blue −): they only correct the layers before them"),
         ha="center", fontsize=10.5, color=MUTED)
fig.tight_layout()
figure(fig, "fig18_4_2")
