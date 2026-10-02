"""图 7.7.1：车轮轮缘上一点画出的摆线及几个位置的速度；图 7.7.2：激光雷达扫到一面墙。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

R, v = 0.1, 1.0
phi = np.linspace(0, 4 * math.pi, 600)
fig, ax = plt.subplots(figsize=(10, 3.2))
ax.plot(R * (phi - np.sin(phi)), R * (1 - np.cos(phi)), color=INK, lw=2)
ax.axhline(0, color=MUTED, lw=1)
for p in (math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi + 0.6):
    P = np.array([R * (p - math.sin(p)), R * (1 - math.cos(p))])
    V = np.array([v * (1 - math.cos(p)), v * math.sin(p)])
    ax.annotate("", xy=P + 0.06 * V, xytext=P, arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.8, mutation_scale=12))
    ax.plot(*P, "o", color=RED, ms=4)
c = math.pi / 2
ax.add_patch(plt.Circle((R * c, R), R, fill=False, color=BLUE, lw=1.2, ls="--"))
for k in (0, 2):
    ax.plot([2 * math.pi * R * k / 2 * 2 / 2 * 1], [0], "")
ax.text(2 * math.pi * R + 0.03, -0.035, T("尖点：速度为 0", "cusp: speed 0"), color=MUTED, ha="left")
ax.plot([2 * math.pi * R], [0], "o", color=MUTED, ms=5)
ax.set_aspect("equal")
ax.set_xlim(-0.05, 4 * math.pi * R + 0.05)
ax.set_ylim(-0.05, 0.28)
ax.set_xlabel("x / m")
ax.set_ylabel("y / m")
clean(ax, zero=False)
ax.set_title(T("最高点速度 2v，着地点速度为 0", "Top point moves at 2v, the contact point is at rest"), fontsize=11)
fig.tight_layout()
figure(fig, "fig7_7_1")

d, phi0 = 2.0, math.radians(20)
ph = np.radians(np.arange(-40, 60.01, 2.0))
rr = d / np.cos(ph - phi0)
fig, ax = plt.subplots(figsize=(5.6, 5.0))
for p, r in zip(ph, rr):
    ax.plot([0, r * math.cos(p)], [0, r * math.sin(p)], color=GREEN, lw=0.5, alpha=0.5)
ax.plot(rr * np.cos(ph), rr * np.sin(ph), "o", color=INK, ms=3)
n = np.array([math.cos(phi0), math.sin(phi0)])
ax.annotate("", xy=d * n, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.5))
ax.text(d * n[0] / 2, d * n[1] / 2 + 0.12, "$d$", color=BLUE, fontsize=13)
P0 = np.array([d / math.cos(phi0), 0])
tdir = np.array([math.cos(math.radians(110)), math.sin(math.radians(110))])
ax.annotate("", xy=P0 + 1.2 * tdir, xytext=P0, arrowprops=dict(arrowstyle="-|>", color=RED, lw=2, shrinkA=0, shrinkB=0))
ax.plot(*P0, "o", color=RED, ms=6)
ax.text(P0[0] + 0.08, -0.2, T("φ = 0 处的切线方向", "tangent at φ = 0"), color=RED, fontsize=10)
ax.plot([0], [0], "s", color=INK, ms=8)
ax.text(0.05, -0.25, T("雷达", "lidar"))
ax.set_aspect("equal")
ax.set_xlim(-0.3, 2.9)
ax.set_ylim(-1.6, 3.2)
clean(ax, zero=False)
ax.set_title(T("r = d / cos(φ − φ₀) 的扫描点", "Scan points r = d / cos(φ − φ₀)"), fontsize=11)
fig.tight_layout()
figure(fig, "fig7_7_2")
