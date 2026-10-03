"""图 2.7.1–2.7.3：取整与符号函数、梯形速度曲线；摆线；激光雷达扫描。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a0, a2) = plt.subplots(1, 3, figsize=(13, 3.8), gridspec_kw={"width_ratios": [1, 0.8, 1.3]})
for k in range(-3, 3):
    a1.plot([k, k + 1], [k, k], color=BLUE, lw=2)
    a1.plot([k], [k], "o", color=BLUE, ms=4)
    a1.plot([k + 1], [k], "o", mfc="white", mec=BLUE, ms=4)
a1.set_title(T("取整函数 ⌊x⌋：在每个整数处跳跃", "Floor ⌊x⌋: a jump at every integer"), fontsize=10)
clean(a1)
a1.axvline(0, color=MUTED, lw=0.6)
a0.plot([-2, 0], [-1, -1], color=RED, lw=2)
a0.plot([0, 2], [1, 1], color=RED, lw=2)
a0.plot([0], [0], "o", color=RED, ms=5)
a0.plot([0, 0], [-1, 1], "o", mfc="white", mec=RED, ms=5)
a0.set_ylim(-1.6, 1.6)
a0.set_title(T("符号函数 sgn x", "Sign function sgn x"), fontsize=10)
clean(a0)
a0.axvline(0, color=MUTED, lw=0.6)
t = np.linspace(0, 7, 701)
v = np.where(t < 2, 0.5 * t, np.where(t <= 5, 1.0, 0.5 * (7 - t)))
x = np.where(t < 2, 0.25 * t**2, np.where(t <= 5, 1 + (t - 2), 5 - 0.25 * (7 - t) ** 2))
a2.plot(t, v, color=RED, lw=2, label=T("速度 v / (m/s)", "speed v / (m/s)"))
a2.fill_between(t, 0, v, color=RED, alpha=0.08)
a2b = a2.twinx()
a2b.plot(t, x, color=BLUE, lw=2, label=T("位置 x / m", "position x / m"))
for tj in (2, 5):
    a2.axvline(tj, color=MUTED, lw=0.6, ls=":")
a2.set_ylim(0, 1.6)
a2b.set_ylim(0, 6)
a2.set_xlabel("t / s")
a2.set_ylabel(T("v / (m/s)", "v / (m/s)"), color=RED)
a2b.set_ylabel("x / m", color=BLUE)
a2.set_title(T("AGV 的梯形速度曲线与位置", "AGV trapezoidal speed and position"), fontsize=10)
for s in ("top",):
    a2.spines[s].set_visible(False)
    a2b.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig2_7_1")

r = 0.075
fig, ax = plt.subplots(figsize=(10, 2.8))
th = np.linspace(0, 4 * np.pi, 1000)
ax.plot(r * (th - np.sin(th)), r * (1 - np.cos(th)), color=RED, lw=2)
for k, th0 in enumerate((0.0, 2.2, 4.4)):
    cx = r * th0
    c = np.linspace(0, 2 * np.pi, 200)
    ax.plot(cx + r * np.cos(c), r + r * np.sin(c), color=MUTED, lw=1)
    ax.plot([cx], [r], "+", color=MUTED)
    px, py = r * (th0 - math.sin(th0)), r * (1 - math.cos(th0))
    ax.plot([cx, px], [r, py], color=INK, lw=1)
    ax.plot([px], [py], "o", color=RED, ms=5)
ax.axhline(0, color=INK, lw=1)
ax.text(2 * np.pi * r, -0.02, T("尖点：着地时速度为零", "cusp: zero speed at contact"), ha="center", va="top", fontsize=9)
ax.set_aspect("equal")
ax.set_ylim(-0.04, 0.17)
ax.axis("off")
ax.set_title(T("车轮滚动时轮缘上一点画出的摆线", "The cycloid traced by a point on a rolling wheel"), fontsize=10)
fig.tight_layout()
figure(fig, "fig2_7_2")

W, H, px, py = 4.0, 3.0, 1.0, 1.0
rng = np.random.default_rng(3)
phi = np.radians(np.arange(0, 360, 1.0))
dist = []
for p in phi:
    c, s = math.cos(p), math.sin(p)
    cand = [d for d in ((W - px) / c if c > 1e-12 else None, -px / c if c < -1e-12 else None,
                        (H - py) / s if s > 1e-12 else None, -py / s if s < -1e-12 else None) if d is not None]
    dist.append(min(cand))
dist = np.array(dist) + rng.normal(0, 0.01, phi.size)
fig = plt.figure(figsize=(10, 4.2))
a1 = fig.add_subplot(1, 2, 1)
a1.plot(np.degrees(phi), dist, ".", color=BLUE, ms=3)
a1.set_xlabel(T("方向 φ / (°)", "direction φ / (°)"))
a1.set_ylabel(T("距离 r / m", "range r / m"))
a1.set_xticks([0, 90, 180, 270, 360])
a1.set_title(T("原始数据：距离 r 随方向 φ 的变化", "Raw data: range r against direction φ"), fontsize=10)
clean(a1, zero=False)
a2 = fig.add_subplot(1, 2, 2)
X, Y = px + dist * np.cos(phi), py + dist * np.sin(phi)
a2.plot(X, Y, ".", color=BLUE, ms=3)
a2.plot([0, W, W, 0, 0], [0, 0, H, H, 0], color=MUTED, lw=0.8, ls="--")
a2.plot([px], [py], "s", color=RED, ms=8)
a2.text(px + 0.1, py - 0.25, T("雷达", "lidar"), color=RED)
a2.set_aspect("equal")
a2.set_xlabel("x / m")
a2.set_ylabel("y / m")
a2.set_title(T("换算到房间的直角坐标", "Converted to room coordinates"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig2_7_3")
