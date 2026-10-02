"""18.7 节的四张图：齿轮图像的低秩重建；奇异值与相对误差；两连杆的速度椭圆；UR5e 最小奇异值与可操作度。"""
import math

import numpy as np

from _arm import planar2, ur5e, ur5e_links
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from _img import gear_image

G = gear_image()
m, n = G.shape
U, s, Vt = np.linalg.svd(G, full_matrices=False)
fig, axs = plt.subplots(1, 4, figsize=(13.5, 2.9))
for ax, k in zip(axs, (1, 5, 20, None)):
    M = G if k is None else (U[:, :k] * s[:k]) @ Vt[:k]
    ax.imshow(M, cmap="gray", vmin=0, vmax=1, interpolation="nearest")
    ax.set_xticks([])
    ax.set_yticks([])
    if k is None:
        ax.set_title(T("原图（19200 个数）", "original (19200 numbers)"), fontsize=11)
    else:
        ax.set_title(T(f"k = {k}（{k * (m + n + 1)} 个数）", f"k = {k} ({k * (m + n + 1)} numbers)"), fontsize=11)
fig.tight_layout()
figure(fig, "fig18_7_1")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6))
a1.semilogy(np.arange(1, len(s) + 1), s, ".", color=BLUE, ms=4)
a1.set_xlabel("i")
a1.set_ylabel(r"$\sigma_i$")
a1.set_title(T("奇异值（对数坐标）", "singular values (log scale)"), fontsize=11)
ks = np.arange(1, 81)
rel = [math.sqrt(np.sum(s[k:] ** 2) / np.sum(s ** 2)) for k in ks]
a2.plot(ks, np.array(rel) * 100, color=RED)
a2.plot(ks, ks * (m + n + 1) / (m * n) * 100, color=MUTED, ls="--")
a2.text(52, 52, T("存储量 / 原图", "storage / original"), color=MUTED)
a2.text(22, 12, T(r"相对误差 $\Vert A-A_k\Vert_F\,/\,\Vert A\Vert_F$", r"relative error $\Vert A-A_k\Vert_F\,/\,\Vert A\Vert_F$"), color=RED)
a2.set_xlabel("k")
a2.set_ylabel("%")
a2.set_ylim(0, 100)
for ax in (a1, a2):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig18_7_2")

l1, l2 = ur5e_links()
fig, axs = plt.subplots(1, 3, figsize=(12, 4.0))
for ax, deg in zip(axs, (90, 45, 10)):
    t1, t2 = math.radians(30), math.radians(deg)
    p, J = planar2(t1, t2, l1, l2)
    j = np.array([l1 * math.cos(t1), l1 * math.sin(t1)])
    ax.plot([0, j[0], p[0]], [0, j[1], p[1]], color=BLUE, lw=5, alpha=0.55, solid_capstyle="round")
    ax.plot([0, j[0]], [0, j[1]], "o", color="white", mec=INK, ms=7)
    th = np.linspace(0, 2 * math.pi, 361)
    E = 0.35 * (J @ np.vstack([np.cos(th), np.sin(th)])) + p[:, None]
    ax.plot(E[0], E[1], color=RED, lw=1.8)
    sv = np.linalg.svd(J, compute_uv=False)
    ax.set_title(T(f"θ₂ = {deg}°：σ₂ = {sv[1]:.3f} m/s", f"θ₂ = {deg}°: σ₂ = {sv[1]:.3f} m/s"), fontsize=11)
    ax.set_aspect("equal")
    ax.set_xlim(-0.25, 1.05)
    ax.set_ylim(-0.15, 0.95)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig18_7_3")

R = ur5e()
base = np.radians([0, -60, 90, -120, -90, 0])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6))
for ax, idx, rng_, name in ((a1, 2, np.linspace(0, 150, 301), T("肘关节角 θ₃ / °", "elbow angle θ₃ / °")),
                            (a2, 4, np.linspace(-150, 0, 301), T("腕关节角 θ₅ / °", "wrist angle θ₅ / °"))):
    smin, w = [], []
    for d in rng_:
        q = base.copy()
        q[idx] = math.radians(d)
        sv = np.linalg.svd(R.jacobian(q), compute_uv=False)
        smin.append(sv[-1])
        w.append(np.prod(sv))
    ax.plot(rng_, smin, color=RED, label=T("最小奇异值 σ₆", "smallest singular value σ₆"))
    ax.plot(rng_, w, color=BLUE, ls="--", label=T("可操作度 w = σ₁⋯σ₆", "manipulability w = σ₁⋯σ₆"))
    ax.set_xlabel(name)
    ax.legend(frameon=False, fontsize=9.5)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig18_7_4")
