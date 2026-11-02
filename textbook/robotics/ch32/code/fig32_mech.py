"""32.2–32.4 节的结构示意图（配动画 32.2.1、32.3.1、32.4.1）。

图 32.2.1：谐波减速器。(a) 正视：刚轮（内齿，固定）、柔轮（外齿，薄壁，被撑成椭圆）、波发生器（椭圆凸轮 + 柔性轴承）；
          柔轮只在长轴两端与刚轮啮合，短轴处脱开。齿数取 40/42 便于看清（WQ-CR5 用 200/202）。
          (b) 剖视：杯型柔轮的杯底接输出，刚轮接壳体，波发生器接电机。
图 32.3.1：RV 减速器。(a) 第一级：太阳轮 12 齿带动两个行星齿轮 36 齿，行星齿轮装在曲柄轴上；
          (b) 第二级：摆线轮 39 齿（偏心距放大画）与 40 根针齿啮合，曲柄轴转一圈，摆线轮相对针齿转过一个齿。与式 (32.3.1) 的算例同一组齿数。
          摆线轮齿廓按针齿数 N、针齿分布圆半径 R、针齿半径 r、偏心距 e 的标准方程：
          x = R cos t − r cos(t + ψ) − e cos(N t)，y = −R sin t + r sin(t + ψ) + e sin(N t)，ψ = atan2(sin((1 − N) t), R/(eN) − cos((1 − N) t))。
图 32.4.1：行星减速器的三种接法（太阳轮 20 齿、内齿圈 70 齿、3 个行星轮 25 齿，算例 32.4.1）：固定的一件画灰色斜线，标出输入、输出和传动比。
"""
import math

import numpy as np

from bookout import COLORS as C, T, figure, style

plt = style()


def teeth(r, z, h, phase=0.0, inner=False, n=2000, a=None, b=None):
    """齿圈的示意轮廓：半径 r 上叠加 z 个“齿”（截断的正弦）；a、b 给出时为椭圆（柔轮）"""
    t = np.linspace(0, 2 * np.pi, n)
    bump = np.clip(np.sin(z * t + phase) * 1.6, -1, 1) * h / 2
    rr = (r + (-bump if inner else bump))
    if a is not None:
        ex, ey = a / r, b / r
        return rr * np.cos(t) * ex, rr * np.sin(t) * ey
    return rr * np.cos(t), rr * np.sin(t)


# ---------------------------------------------------------------- 图 32.2.1 谐波
fig, axs = plt.subplots(1, 2, figsize=(11.6, 5.0), gridspec_kw={"width_ratios": [1.0, 1.05]})
ax = axs[0]
R, h = 1.0, 0.06
x, y = teeth(R, 42, h, inner=True)
ax.fill(np.r_[1.25 * np.cos(np.linspace(0, 2 * np.pi, 200)), x[::-1]], np.r_[1.25 * np.sin(np.linspace(0, 2 * np.pi, 200)), y[::-1]],
        color=C["muted"], alpha=0.35, lw=0)
ax.plot(x, y, color=C["ink"], lw=1)
a_f, b_f = R - h * 0.5, R - h * 0.5 - 0.11                    # 柔轮：长轴撑到与刚轮啮合，短轴脱开
x, y = teeth(R - h, 40, h, phase=np.pi, a=a_f - h / 2, b=b_f - h / 2)
ax.plot(x, y, color=C["z"], lw=1.2)
t = np.linspace(0, 2 * np.pi, 300)
ax.plot((a_f - 0.13) * np.cos(t), (b_f - 0.13) * np.sin(t), color=C["z"], lw=0.8)
ax.plot((a_f - 0.18) * np.cos(t), (b_f - 0.18) * np.sin(t), color=C["x"], lw=1.0, ls="--")       # 柔性轴承
ax.fill((a_f - 0.24) * np.cos(t), (b_f - 0.24) * np.sin(t), color=C["x"], alpha=0.25)            # 波发生器
ax.plot([0], [0], "o", color=C["ink"], ms=4)
for s in (1, -1):
    ax.annotate(T("啮合", "in mesh"), xy=(s * 0.97, 0), xytext=(s * 1.42, 0.35), fontsize=9, ha="center",
                arrowprops=dict(arrowstyle="->", color=C["ink"], lw=0.8))
ax.annotate(T("脱开", "out of mesh"), xy=(0, b_f), xytext=(0.55, 1.42), fontsize=9, ha="center",
            arrowprops=dict(arrowstyle="->", color=C["ink"], lw=0.8))
ax.text(0, -1.38, T("刚轮 42 齿（内齿，固定）", "circular spline, 42 teeth (fixed)"), ha="center", fontsize=9, color=C["ink"])
ax.text(0, 0.42, T("柔轮 40 齿", "flexspline, 40 teeth"), ha="center", fontsize=9, color=C["z"])
ax.text(0, -0.25, T("波发生器", "wave generator"), ha="center", fontsize=9, color=C["x"])
ax.text(0, -0.43, T("（椭圆凸轮 + 柔性轴承）", "(elliptical cam + flexible bearing)"), ha="center", fontsize=8, color=C["x"])
ax.set_xlim(-1.7, 1.7)
ax.set_ylim(-1.6, 1.6)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title(T("(a) 正视（椭圆度放大画）", "(a) front view (ellipticity exaggerated)"), fontsize=11)
ax = axs[1]
# 剖视：上半剖面
ax.add_patch(plt.Rectangle((2.2, 0.95), 0.9, 0.35, color=C["muted"], alpha=0.5))           # 刚轮
ax.add_patch(plt.Rectangle((0.0, 1.25), 3.4, 0.25, color=C["muted"], alpha=0.25))          # 壳体
ax.plot([0.3, 3.1], [0.9, 0.9], color=C["z"], lw=3)                                          # 柔轮杯壁
ax.plot([0.3, 0.3], [0.9, 0.15], color=C["z"], lw=3)                                         # 杯底
ax.add_patch(plt.Rectangle((-0.9, 0.0), 1.2, 0.15, color=C["z"], alpha=0.6))               # 输出轴
ax.add_patch(plt.Rectangle((2.3, 0.55), 0.8, 0.3, color=C["x"], alpha=0.35))               # 波发生器
ax.add_patch(plt.Rectangle((2.3, 0.0), 2.0, 0.12, color=C["x"], alpha=0.6))                # 输入轴
ax.plot([-1.0, 4.4], [0, 0], color=C["ink"], lw=0.8, ls="-.")
for (xx, yy, z, e, col) in [(2.65, 1.36, "刚轮（固定在壳体上）", "circular spline (in the housing)", C["ink"]),
                            (1.6, 0.98, "柔轮（薄壁杯）", "flexspline (thin cup)", C["z"]),
                            (2.7, 0.45, "波发生器", "wave generator", C["x"]),
                            (4.0, 0.22, "输入：电机", "input: motor", C["x"]),
                            (-0.4, 0.27, "输出", "output", C["z"])]:
    ax.text(xx, yy, T(z, e), fontsize=9, color=col, ha="center", va="bottom")
ax.text(1.6, -0.45, T("杯底变形小，接输出；齿圈端被撑成椭圆", "the cup bottom barely flexes and drives the output;\nthe toothed rim is stretched into an ellipse"),
        ha="center", fontsize=9, color=C["muted"])
ax.set_xlim(-1.1, 4.6)
ax.set_ylim(-0.7, 1.7)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title(T("(b) 杯型组件剖视（上半）", "(b) cup-type set, half section"), fontsize=11)
fig.tight_layout()
figure(fig, "fig32_2_1")

# ---------------------------------------------------------------- 图 32.3.1 RV
ZS, ZPL, NP = 12, 36, 40
fig, axs = plt.subplots(1, 2, figsize=(11.6, 5.0))
ax = axs[0]
m = 0.05
rs, rpl = m * ZS / 2, m * ZPL / 2
x, y = teeth(rs, ZS, 0.04)
ax.fill(x, y, color=C["x"], alpha=0.35)
ax.plot(x, y, color=C["x"], lw=1)
for k in range(2):
    a = math.pi * k
    cx, cy = (rs + rpl) * math.cos(a), (rs + rpl) * math.sin(a)
    x, y = teeth(rpl, ZPL, 0.04, phase=math.pi)
    ax.fill(x + cx, y + cy, color=C["z"], alpha=0.2)
    ax.plot(x + cx, y + cy, color=C["z"], lw=1)
    ax.add_patch(plt.Circle((cx, cy), 0.12, color=C["accent"], alpha=0.8))
    ax.add_patch(plt.Circle((cx + 0.05, cy), 0.07, fill=False, color=C["ink"], lw=1))
ax.text(0, -0.55, T("太阳轮 12 齿（输入）", "sun 12 teeth (input)"), ha="center", fontsize=9, color=C["x"])
ax.text(rs + rpl, -1.15, T("行星齿轮 36 齿", "planet 36 teeth"), ha="center", fontsize=9, color=C["z"])
ax.text(rs + rpl, 0.25, T("曲柄轴（偏心）", "crankshaft (eccentric)"), ha="center", fontsize=9, color=C["accent"])
ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-1.4, 1.4)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title(T("(a) 第一级：减速 36/12 = 3 倍", "(a) stage 1: 36/12 = 3"), fontsize=11)
ax = axs[1]
Rp, rpin, e = 1.0, 0.035, 0.015
t = np.linspace(0, 2 * np.pi, 6000)
psi = np.arctan2(np.sin((1 - NP) * t), Rp / (e * NP) - np.cos((1 - NP) * t))
cxs = Rp * np.cos(t) - rpin * np.cos(t + psi) - e * np.cos(NP * t)
cys = -Rp * np.sin(t) + rpin * np.sin(t + psi) + e * np.sin(NP * t)
ax.fill(cxs + e, cys, color=C["y"], alpha=0.25)                 # 摆线轮：中心偏离 e
ax.plot(cxs + e, cys, color=C["y"], lw=1)
for k in range(NP):
    a = 2 * np.pi * k / NP
    ax.add_patch(plt.Circle((Rp * math.cos(a), Rp * math.sin(a)), rpin, color=C["ink"], alpha=0.7))
ax.add_patch(plt.Circle((0, 0), 1.12, fill=False, color=C["muted"], lw=6, alpha=0.4))
for k in range(2):
    a = math.pi * k + math.pi / 2
    ax.add_patch(plt.Circle((0.5 * math.cos(a) + e, 0.5 * math.sin(a)), 0.12, fill=False, color=C["accent"], lw=1.5))
ax.plot([0, e], [0, 0], color=C["x"], lw=2)
ax.plot([0], [0], "+", color=C["ink"], ms=10)
ax.text(0, -0.2, T("中心偏 e", "offset e"), ha="center", fontsize=8, color=C["x"])
ax.text(0.0, 0.1, T("摆线轮 39 齿", "cycloid disc 39 lobes"), ha="center", fontsize=9, color=C["y"])
ax.text(0, -1.33, T("针齿 40 根（装在壳体上）", "40 pins (in the housing)"), ha="center", fontsize=9, color=C["ink"])
ax.text(0.95, 0.85, T("曲柄轴孔", "crank holes"), ha="left", fontsize=8, color=C["accent"])
ax.set_xlim(-1.45, 1.45)
ax.set_ylim(-1.45, 1.35)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title(T("(b) 第二级：摆线针轮，再减速 40 倍", "(b) stage 2: cycloid and pins, 40 times more"), fontsize=11)
fig.tight_layout()
figure(fig, "fig32_3_1")

# ---------------------------------------------------------------- 图 32.4.1 行星的三种接法
zs, zr, zp = 20, 70, 25
cases = [("ring", T("内齿圈固定", "ring fixed"), T("太阳轮 → 行星架", "sun → carrier"), f"i = 1 + {zr}/{zs} = {1 + zr / zs:g}"),
         ("carrier", T("行星架固定", "carrier fixed"), T("太阳轮 → 内齿圈", "sun → ring"), f"i = −{zr}/{zs} = −{zr / zs:g}"),
         ("sun", T("太阳轮固定", "sun fixed"), T("内齿圈 → 行星架", "ring → carrier"), f"i = 1 + {zs}/{zr} = {1 + zs / zr:.3f}")]
fig, axs = plt.subplots(1, 3, figsize=(11.6, 4.3))
k = 0.04
for ax, (fixed, title, io, ratio) in zip(axs, cases):
    rs, rp, rr = zs * k / 2, zp * k / 2, zr * k / 2
    hatch = dict(hatch="////", edgecolor=C["muted"])
    if fixed == "ring":
        ax.add_patch(plt.Circle((0, 0), rr + 0.12, facecolor="white", **hatch))
    else:
        ax.add_patch(plt.Circle((0, 0), rr + 0.12, color=C["muted"], alpha=0.15))
    ax.add_patch(plt.Circle((0, 0), rr, color="white"))
    ax.add_patch(plt.Circle((0, 0), rr, fill=False, color=C["ink"], lw=1.2))
    for j in range(3):
        a = 2 * np.pi * j / 3 + np.pi / 2
        px, py = (rs + rp) * math.cos(a), (rs + rp) * math.sin(a)
        ax.plot([0, px], [0, py], color=C["accent"], lw=4 if fixed != "carrier" else 2, ls="-" if fixed != "carrier" else "--")
        ax.add_patch(plt.Circle((px, py), rp, color=C["z"], alpha=0.25))
        ax.add_patch(plt.Circle((px, py), rp, fill=False, color=C["z"], lw=1))
    if fixed == "sun":
        ax.add_patch(plt.Circle((0, 0), rs, facecolor="white", **hatch))
    else:
        ax.add_patch(plt.Circle((0, 0), rs, color=C["x"], alpha=0.5))
    ax.add_patch(plt.Circle((0, 0), rs, fill=False, color=C["x"], lw=1.2))
    if fixed == "carrier":
        ax.text(0, -rr - 0.32, T("行星架固定（虚线）", "carrier held (dashed)"), ha="center", fontsize=8, color=C["accent"])
    ax.text(0, rr + 0.3, title, ha="center", fontsize=11, color=C["ink"])
    ax.text(0, -rr - 0.62, io, ha="center", fontsize=9, color=C["ink"])
    ax.text(0, -rr - 0.9, ratio, ha="center", fontsize=10, color=C["x"])
    ax.set_xlim(-1.75, 1.75)
    ax.set_ylim(-2.45, 1.85)
    ax.set_aspect("equal")
    ax.axis("off")
fig.text(0.5, 0.0, T("红：太阳轮 20　蓝：行星轮 25 × 3　橙：行星架　黑圈：内齿圈 70；斜线 = 固定", "red sun 20, blue planets 25 × 3, orange carrier, black ring 70; hatched = held"),
         fontsize=9, color=C["muted"], ha="center")
fig.tight_layout(rect=(0, 0.04, 1, 1))
figure(fig, "fig32_4_1")
