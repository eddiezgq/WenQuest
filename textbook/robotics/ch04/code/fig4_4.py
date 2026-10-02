"""4.4 节的示意图。

图 4.4.1：罗德里格斯公式的几何推导——v = v∥ + v⊥；v⊥ 在 v⊥ 与 ω̂×v 张成的平面内转过 θ。
图 4.4.2：级数 (4.4.7) 的误差随项数变化（数据与程序 4.4.1 相同）。
"""
import math

import numpy as np

from _rot import C, axes3d, circle_arc, rot_axis, skew
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 4.4.1
w = np.array([0.0, 0.0, 1.0])
v = np.array([0.75, 0.15, 0.55])
t = math.radians(125)
vpar = (w @ v) * w
vperp = v - vpar
wxv = np.cross(w, v)
v2 = rot_axis(w, t) @ v
r = np.linalg.norm(vperp)

fig, ax = axes3d(plt, size=(4.8, 3.8), elev=22, azim=-62, lim=0.6, zoom=1.1, center=(0.05, 0.05, 0.35))
ax.plot([0, 0], [0, 0], [-0.1, 0.85], color=C["ink"], lw=1.3)
ax.text(0, 0, 0.9, r"$\hat\omega$", fontsize=13)


def arrow(p, q, col, lw=2.0, ls="-"):
    p, q = np.asarray(p), np.asarray(q)
    ax.quiver(*p, *(q - p), color=col, lw=lw, arrow_length_ratio=0.1, linestyle=ls)


arrow((0, 0, 0), v, C["ink"])
arrow((0, 0, 0), v2, C["accent"])
arrow((0, 0, 0), vpar, C["z"], 1.6)
arrow(vpar, vpar + vperp, C["x"], 1.6)
arrow(vpar, vpar + wxv, C["y"], 1.6)
circle_arc(ax, vpar, vperp / r, wxv / np.linalg.norm(wxv), r, 0, 2 * math.pi, C["muted"], 0.6, ":")
circle_arc(ax, vpar, vperp / r, wxv / np.linalg.norm(wxv), r * 0.35, 0, t, C["accent"], 1.2)
ax.text(*(v * 1.06), "$v$", fontsize=13)
ax.text(*(v2 * 1.08), r"$v'$", fontsize=13, color=C["accent"])
ax.text(*(vpar * 0.5 + np.array([0.05, -0.05, 0])), r"$v_\parallel$", fontsize=12, color=C["z"])
ax.text(*(vpar + vperp * 0.55 + np.array([0, -0.08, -0.04])), r"$v_\perp$", fontsize=12, color=C["x"])
ax.text(*(vpar + wxv * 1.1), r"$\hat\omega\times v$", fontsize=12, color=C["y"])
m = vpar + 0.42 * r * (math.cos(t / 2) * vperp / r + math.sin(t / 2) * wxv / np.linalg.norm(wxv))
ax.text(*m, r"$\theta$", fontsize=12, color=C["accent"])
figure(fig, "fig4_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 4.4.2
w1 = np.ones(3) / math.sqrt(3)
A = skew(w1) * math.radians(120)
R1 = rot_axis(w1, math.radians(120))
S, term, errs = np.eye(3), np.eye(3), [float(np.abs(np.eye(3) - R1).max())]
for k in range(1, 30):
    term = term @ A / k
    S = S + term
    errs.append(float(np.abs(S - R1).max()))
fig, ax = plt.subplots(figsize=(5.2, 3.2))
n = np.arange(1, 31)
ax.semilogy(n, np.maximum(errs, 1e-17), "o-", color=C["z"], ms=3.5, lw=1.2)
ax.axhline(1e-12, color=C["muted"], lw=0.8, ls="--")
ax.text(29.6, 2.5e-12, "$10^{-12}$", ha="right", fontsize=10, color=C["muted"])
ax.set_xlabel(T("所取的项数 n", "number of terms n"))
ax.set_ylabel(T("最大误差", "largest error"))
ax.grid(True, which="major", lw=0.3, alpha=0.5)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
figure(fig, "fig4_4_2")
plt.close(fig)
