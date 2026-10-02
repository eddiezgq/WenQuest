"""图 18.2.1：A = UΣVᵀ 的几何——先转（Vᵀ），再沿坐标轴伸缩（Σ），再转（U）。取 U、V 都是旋转的那组符号。"""
import numpy as np

from _arm import svd_fixed
from _fig import GREEN, INK, MUTED, RED, T, arrow, axes_box, circle_pts, figure, marker, plt

A = np.array([[3.0, 0.0], [4.0, 5.0]])
U, s, V = svd_fixed(A)
U[:, 1] *= -1
V[:, 1] *= -1
S = np.diag(s)
steps = [(np.eye(2), r"$\boldsymbol{x}$", T("单位圆与 v₁、v₂", "unit circle, v₁, v₂")),
         (V.T, r"$V^{\mathrm{T}}\boldsymbol{x}$", T("① 转：vᵢ 转到坐标轴 eᵢ", "① rotate: vᵢ to the axes eᵢ")),
         (S @ V.T, r"$\Sigma V^{\mathrm{T}}\boldsymbol{x}$", T("② 沿坐标轴伸缩 σᵢ 倍", "② stretch the axes by σᵢ")),
         (U @ S @ V.T, r"$U\Sigma V^{\mathrm{T}}\boldsymbol{x}=A\boldsymbol{x}$", T("③ 转：eᵢ 方向转到 uᵢ", "③ rotate: eᵢ to uᵢ"))]
fig, axs = plt.subplots(2, 2, figsize=(9.0, 8.4))
for k, (ax, (M, name, title)) in enumerate(zip(axs.flat, steps)):
    lim = 1.6 if k < 2 else 7.2
    axes_box(ax, lim, ticks=k >= 2)
    ax.plot(*circle_pts(M), color=INK, lw=1.5)
    F = marker(M, 0.35 if k < 2 else 0.35)
    ax.fill(F[0], F[1], color="#b8860b", alpha=0.75, zorder=3)
    arrow(ax, M @ V[:, 0], RED, None)
    arrow(ax, M @ V[:, 1], GREEN, None)
    ax.set_title(title, fontsize=11)
    ax.text(0.02, 0.02, name, transform=ax.transAxes, fontsize=12, color=MUTED)
fig.tight_layout()
figure(fig, "fig18_2_1")
