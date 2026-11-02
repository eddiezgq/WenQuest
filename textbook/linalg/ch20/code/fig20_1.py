"""图 20.1.1：(a) 平面上 p = 1、1.5、2、4、∞ 的单位球 ‖x‖ₚ = 1；(b) 两种控制器下 AGV 的横向偏差：
A 的均方根小但有一个尖峰，B 没有尖峰但整体摆动大——用 2-范数评 A 好，用 ∞-范数评 B 好。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, axes_box, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.6), gridspec_kw={"width_ratios": [1, 1.6]})
t = np.linspace(0, 2 * math.pi, 721)
for p, col in ((1, RED), (1.5, ACC), (2, BLUE), (4, GREEN), (np.inf, INK)):
    c, s = np.cos(t), np.sin(t)
    if p == np.inf:
        r = 1 / np.maximum(np.abs(c), np.abs(s))
    else:
        r = 1 / (np.abs(c) ** p + np.abs(s) ** p) ** (1 / p)
    a1.plot(r * c, r * s, color=col, lw=2, label="p = ∞" if p == np.inf else f"p = {p:g}")
axes_box(a1, 1.35)
a1.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(1.0, 1.0))
a1.set_title(T("(a) 单位球 ‖x‖ₚ = 1", "(a) Unit balls ‖x‖ₚ = 1"), fontsize=11)
n = 1000
s_ = np.arange(n) * 0.05
rng = np.random.default_rng(2001)
eA = 4.0 * rng.standard_normal(n) + 26.0 * np.exp(-((s_ - 31.0) / 0.25) ** 2)
eB = 8.0 * np.sin(2 * math.pi * s_ / 7.0) + 1.0 * rng.standard_normal(n)
a2.plot(s_, eA, color=RED, lw=0.8, label=T(f"控制器 A：均方根 {np.sqrt(np.mean(eA**2)):.1f} mm，最大 {np.max(np.abs(eA)):.1f} mm",
                                             f"controller A: RMS {np.sqrt(np.mean(eA**2)):.1f} mm, max {np.max(np.abs(eA)):.1f} mm"))
a2.plot(s_, eB, color=BLUE, lw=1.0, label=T(f"控制器 B：均方根 {np.sqrt(np.mean(eB**2)):.1f} mm，最大 {np.max(np.abs(eB)):.1f} mm",
                                             f"controller B: RMS {np.sqrt(np.mean(eB**2)):.1f} mm, max {np.max(np.abs(eB)):.1f} mm"))
for y in (20, -20):
    a2.axhline(y, color=MUTED, lw=1, ls="--")
a2.text(0.5, 21.5, T("货架间隙 ±20 mm", "shelf clearance ±20 mm"), color=MUTED, fontsize=9)
a2.set_xlabel(T("沿路径的距离 / m", "distance along the path / m"))
a2.set_ylabel(T("横向偏差 / mm", "lateral error / mm"))
a2.set_ylim(-25, 38)
a2.legend(frameon=False, fontsize=8.5, loc="upper left")
a2.set_title(T("(b) 两种控制器的跟踪误差", "(b) Tracking errors of two controllers"), fontsize=11)
for sp in ("top", "right"):
    a2.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig20_1_1")
