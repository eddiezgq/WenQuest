"""13.5 节的示意图。

图 13.5.1：相邻两轴接近平行（侧视，偏转角为看清起见放大到 12°）。按 DH，公垂线退化为两轴的交点，
          {i} 的原点跑到远处，d 很大、a 突然变为 0；按哈亚蒂，取轴 i+1 与 {i−1} 的 xy 平面的交点，a 不变，多出一个绕 y 的转角 β。
图 13.5.2：偏转角 ε 与参数的关系（对数坐标）：面内偏转时 |d| ≈ a/ε，面外偏转时 d = 0；哈亚蒂的 β = ε；旋量轴的变化量与 ε 成正比。
数据与程序 13.5.1 相同（a = 0.425 m）。
"""
import math

import numpy as np

from _fig13 import C, plane
from bookout import T, figure, style

plt = style()
A = 0.425

# ---------------------------------------------------------------- 图 13.5.1
eps = math.radians(12)
zc = -A / math.tan(eps)                       # 交点高度
fig, axs = plt.subplots(1, 2, figsize=(10.0, 5.0), gridspec_kw={"width_ratios": [1.0, 1.0]})
for k, ax in enumerate(axs):
    plane(ax, (-0.55, 0.95), (zc - 0.35, 0.75) if k == 0 else (-0.45, 0.75))
    ax.plot([0, 0], [zc - 0.25 if k == 0 else -0.4, 0.7], color="#5b6670", lw=2.2)
    t = np.array([zc / math.cos(eps) - 0.2, 0.7 / math.cos(eps)]) if k == 0 else np.array([-0.4, 0.7])
    ax.plot(A + t * math.sin(eps), t * math.cos(eps), color="#5b6670", lw=2.2)
    ax.plot([A, A], [-0.4 if k else zc, 0.7], color=C["muted"], lw=1.0, ls=":")
    ax.text(0.02, 0.62, T("轴 $i$", "axis $i$"), fontsize=10, color="#5b6670")
    ax.text(A + 0.7 * math.sin(eps) + 0.03, 0.62, T("轴 $i+1$", "axis $i+1$"), fontsize=10, color="#5b6670")
    ax.text(A + 0.03, 0.42, T("名义位置", "nominal"), fontsize=9, color=C["muted"])
    ax.annotate("", xy=(0.0, 0.0), xytext=(0.0, 0.001))
    # {i−1}
    ax.annotate("", xy=(0.12, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=1.4))
    ax.annotate("", xy=(0, 0.12), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=C["z"], lw=1.4))
    ax.text(-0.3, 0.02, "{i-1}", fontsize=10)
    if k == 0:
        ax.plot([0], [zc], "o", color=C["accent"], ms=7)
        ax.annotate(T("两轴相交：{i} 的原点在这里\n$a_i = 0$，$d_i = -a\\cot\\varepsilon$", "axes meet: origin of {i} is here\n$a_i = 0$, $d_i = -a\\cot\\varepsilon$"),
                    xy=(0, zc), xytext=(0.22, zc + 0.3), fontsize=9.5, color=C["accent"],
                    arrowprops=dict(arrowstyle="->", color=C["accent"], lw=0.9))
        ax.annotate("", xy=(-0.12, zc), xytext=(-0.12, 0), arrowprops=dict(arrowstyle="<->", color=C["z"], lw=1.2))
        ax.text(-0.4, zc / 2, "$d_i$", fontsize=13, color=C["z"])
        ax.text(0.03, zc + 0.75, r"$\varepsilon$", fontsize=12, color=C["ink"])
        ax.set_title(T("(a) DH：公垂线退化为交点，参数突变", "(a) DH: the normal collapses to an intersection; parameters jump"), fontsize=10, pad=14)
    else:
        ax.plot([0, A], [0, 0], color=C["accent"], lw=1.8, ls="--")
        ax.plot([A], [0], "o", color=C["accent"], ms=7)
        ax.text(A / 2 - 0.04, -0.09, "$a$", fontsize=12, color=C["accent"])
        tt = np.linspace(math.pi / 2, math.pi / 2 - eps, 20)
        ax.plot(A + 0.35 * np.cos(tt), 0.35 * np.sin(tt), color=C["y"], lw=1.6)
        ax.text(A + 0.1, 0.36, r"$\beta = \varepsilon$", fontsize=11, color=C["y"])
        ax.text(0.05, -0.3, T("与 {i−1} 的 xy 平面相交处：$a$ 不变，\n多出绕 $y$ 的转角 $\\beta$，随 ε 连续变化",
                              "where it crosses the xy plane of {i-1}: $a$ unchanged,\nan extra turn $\\beta$ about $y$, continuous in ε"), fontsize=9.5, color=C["ink"])
        ax.set_title(T("(b) 哈亚蒂：参数连续", "(b) Hayati: parameters stay continuous"), fontsize=10, pad=14)
fig.text(0.5, 0.01, T("轴 $i+1$ 在两轴所在的平面内偏转 ε（图中放大为 12°；a = 0.425 m）", "Axis $i+1$ tilted by ε in the plane of the two axes (drawn at 12°; a = 0.425 m)"),
         ha="center", fontsize=9.5)
figure(fig, "fig13_5_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 13.5.2
e = np.logspace(-4, 1, 60)                    # 度
er = np.radians(e)
fig, ax = plt.subplots(figsize=(7.0, 4.2))
ax.loglog(e, A / np.tan(er), color=C["accent"], lw=2.0, label=T("DH 的 |d|（面内偏转），m", "DH |d| (in-plane tilt), m"))
ax.loglog(e, er, color=C["y"], lw=2.0, ls="--", label=T("哈亚蒂的 β，rad", "Hayati β, rad"))
ax.loglog(e, np.sqrt(np.sin(er) ** 2 + (1 + A ** 2) * (1 - np.cos(er)) ** 2),     # S = (u, −u × p)，p = (a, 0, 0)
          color=C["z"], lw=1.4, ls=":", label=T("旋量轴的变化量 |ΔS|", "change of the screw axis |ΔS|"))
for x in (0.01,):
    y = A / math.tan(math.radians(x))
    ax.plot([x], [y], "o", color=C["accent"])
    ax.annotate(T(f"ε = 0.01° 时 |d| ≈ {y:.0f} m", f"ε = 0.01°: |d| ≈ {y:.0f} m"), xy=(x, y), xytext=(0.05, 3e4), fontsize=9.5,
                arrowprops=dict(arrowstyle="->", color=C["muted"], lw=0.8))
ax.set_xlabel(T("偏转角 ε / (°)", "tilt ε / (°)"))
ax.set_ylim(1e-7, 1e6)
ax.grid(True, which="major", color="#e3e7ea", lw=0.6)
ax.legend(fontsize=9, loc="center left", frameon=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.text(1.2e-4, 3e-7, T("面外偏转时 DH 的 d 恒为 0，a 不变（不在对数坐标中画出）", "out-of-plane tilt: DH d stays 0 and a is unchanged (not drawn on log axes)"),
        fontsize=8.5, color=C["muted"])
figure(fig, "fig13_5_2")
plt.close(fig)
