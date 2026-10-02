"""图 18.5.1：极分解 A = QS：先由 S 沿两根互相垂直的轴 v₁、v₂ 伸缩，再由 Q 转动。"""
import numpy as np

from _arm import svd_fixed
from _fig import GREEN, INK, MUTED, RED, T, arrow, axes_box, circle_pts, figure, marker, plt

A = np.array([[3.0, 0.0], [4.0, 5.0]])
U, s, V = svd_fixed(A)
Q = U @ V.T
S = V @ np.diag(s) @ V.T
fig, axs = plt.subplots(1, 3, figsize=(11.5, 3.9))
for k, (ax, M, title) in enumerate(zip(axs, [np.eye(2), S, Q @ S],
                                        [T("单位圆", "unit circle"), T(r"$S\boldsymbol{x}$：沿 $\boldsymbol{v}_1$、$\boldsymbol{v}_2$ 伸缩", r"$S\boldsymbol{x}$: stretch along $\boldsymbol{v}_1$, $\boldsymbol{v}_2$"),
                                         T(r"$QS\boldsymbol{x}=A\boldsymbol{x}$：再转 26.6°", r"$QS\boldsymbol{x}=A\boldsymbol{x}$: then turn 26.6°")])):
    axes_box(ax, 1.6 if k == 0 else 7.2, ticks=k > 0)
    ax.plot(*circle_pts(M), color=INK, lw=1.5)
    F = marker(M, 0.35)
    ax.fill(F[0], F[1], color="#b8860b", alpha=0.75, zorder=3)
    arrow(ax, M @ V[:, 0], RED, None)
    arrow(ax, M @ V[:, 1], GREEN, None)
    ax.set_title(title, fontsize=11.5)
    if k == 1:
        for v in (V[:, 0], V[:, 1]):
            ax.plot([-7 * v[0], 7 * v[0]], [-7 * v[1], 7 * v[1]], color=MUTED, lw=0.8, ls=":")
fig.tight_layout()
figure(fig, "fig18_5_1")
