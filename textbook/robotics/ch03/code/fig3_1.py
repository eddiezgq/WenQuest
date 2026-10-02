"""3.1 节的示意图。

图 3.1.1：(a) 矢量的加法（三角形法则、平行四边形法则）与数乘，不涉及任何坐标系；
          (b) 取定坐标系后，矢量分解为沿各轴的三段，各段的长度（带正负号）就是分量。
图 3.1.2：同一支箭头 d（算例 3.1.1）在 {a} 和 {b} 中的分量：箭头不变，投影到哪一套轴上，就读出哪一套分量。
"""
import math

import numpy as np

from _vec import C, arc2, arrow2, d
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 3.1.1
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.9))
for ax in (ax1, ax2):
    ax.set_aspect("equal")
    ax.axis("off")

a = np.array([1.6, 0.35])
b = np.array([0.55, 1.05])
O = np.array([0.0, 0.0])
arrow2(ax1, O, a, C["x"], 2.0)
arrow2(ax1, a, a + b, C["y"], 2.0)
arrow2(ax1, O, b, C["y"], 1.2, alpha=0.45)
arrow2(ax1, b, a + b, C["x"], 1.2, alpha=0.45)
arrow2(ax1, O, a + b, C["ink"], 2.2)
ax1.text(*(a / 2 + [0.0, -0.17]), r"$\boldsymbol{a}$", color=C["x"], fontsize=14, ha="center")
ax1.text(*(a + b / 2 + [0.12, -0.05]), r"$\boldsymbol{b}$", color=C["y"], fontsize=14)
ax1.text(*((a + b) / 2 + [-0.33, 0.06]), r"$\boldsymbol{a}+\boldsymbol{b}$", color=C["ink"], fontsize=13)
# 数乘：另取一个较短的矢量 c，画出 c、2c、−c/2
cvec = np.array([0.7, 0.15])
for k_, (y0, kk, lab, col) in enumerate(((-0.45, 1.0, r"$\boldsymbol{c}$", C["x"]), (-0.8, 2.0, r"$2\boldsymbol{c}$", C["accent"]),
                                        (-1.15, -0.5, r"$-\boldsymbol{c}/2$", C["muted"]))):
    p0 = np.array([0.55 if kk < 0 else 0.0, y0])
    arrow2(ax1, p0, p0 + kk * cvec, col, 1.6)
    tip = p0 + kk * cvec
    ax1.text(max(p0[0], tip[0]) + 0.08, y0 + 0.02, lab, color=col, fontsize=12)
ax1.text(-0.05, 1.62, T("(a) 三角形法则与平行四边形法则；数乘", "(a) Triangle and parallelogram rules; scaling"),
         fontsize=10, color=C["ink"])
ax1.set_xlim(-0.2, 2.45)
ax1.set_ylim(-1.35, 1.75)

# (b) 分解为沿坐标轴的三段（画成平面情形的两段，第三段垂直于纸面）
p = np.array([1.5, 1.0])
arrow2(ax2, O, (2.05, 0), C["x"], 1.1)
arrow2(ax2, O, (0, 1.45), C["y"], 1.1)
ax2.text(2.08, -0.06, r"$\hat{\boldsymbol{x}}_a$", color=C["x"], fontsize=13)
ax2.text(-0.2, 1.47, r"$\hat{\boldsymbol{y}}_a$", color=C["y"], fontsize=13)
arrow2(ax2, O, (0.45, 0), C["x"], 2.6)
arrow2(ax2, O, (0, 0.45), C["y"], 2.6)
ax2.text(0.22, -0.16, T("单位长", "unit"), fontsize=8.5, color=C["x"], ha="center")
arrow2(ax2, O, p, C["ink"], 2.2)
ax2.plot([p[0], p[0]], [0, p[1]], ls=":", color=C["muted"], lw=1)
ax2.plot([0, p[0]], [p[1], p[1]], ls=":", color=C["muted"], lw=1)
ax2.text(p[0] + 0.05, p[1] + 0.02, r"$\boldsymbol{p}$", fontsize=14)
ax2.text(p[0] / 2 + 0.25, -0.17, r"$p_1\hat{\boldsymbol{x}}_a$", fontsize=12, color=C["x"], ha="center")
ax2.text(-0.48, p[1] / 2 + 0.2, r"$p_2\hat{\boldsymbol{y}}_a$", fontsize=12, color=C["y"])
arc2(ax2, O, 0.42, 0, math.atan2(p[1], p[0]), C["ink"], 0.9)
ax2.text(0.47, 0.11, r"$\alpha_1$", fontsize=11)
ax2.text(0.03, -0.42, r"$\boldsymbol{p}=p_1\hat{\boldsymbol{x}}_a+p_2\hat{\boldsymbol{y}}_a+p_3\hat{\boldsymbol{z}}_a,\quad "
                       r"p_a=(p_1,p_2,p_3)^{\mathsf{T}}$", fontsize=11.5)
ax2.text(-0.05, 1.62, T("(b) 取定坐标系 {a}：矢量与它的分量", "(b) In frame {a}: the vector and its components"),
         fontsize=10, color=C["ink"])
ax2.set_xlim(-0.55, 2.4)
ax2.set_ylim(-0.6, 1.75)
fig.subplots_adjust(wspace=0.08)
figure(fig, "fig3_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 3.1.2
da = np.array([0.30, 0.20])
beta = d(30)
xb = np.array([math.cos(beta), math.sin(beta)])
yb = np.array([-math.sin(beta), math.cos(beta)])
fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.2))
L = 0.42
for k, ax in enumerate(axs):
    ax.set_aspect("equal")
    ax.axis("off")
    strong = 1.6
    weak = dict(lw=1.0, alpha=0.3)
    # {a}
    if k == 0:
        arrow2(ax, (0, 0), (L, 0), C["x"], strong)
        arrow2(ax, (0, 0), (0, L * 0.8), C["y"], strong)
        arrow2(ax, (0, 0), L * 0.8 * xb, C["x"], **weak)
        arrow2(ax, (0, 0), L * 0.8 * yb, C["y"], **weak)
        ax.text(L + 0.01, -0.02, r"$\hat{\boldsymbol{x}}_a$", color=C["x"], fontsize=13)
        ax.text(-0.045, L * 0.8 + 0.01, r"$\hat{\boldsymbol{y}}_a$", color=C["y"], fontsize=13)
        ax.plot([da[0], da[0]], [0, da[1]], ":", color=C["x"], lw=1.1)
        ax.plot([0, da[0]], [da[1], da[1]], ":", color=C["y"], lw=1.1)
        ax.text(da[0] / 2, -0.035, "0.30", color=C["x"], fontsize=10.5, ha="center")
        ax.text(0.008, da[1] / 2 + 0.01, "0.20", color=C["y"], fontsize=10.5)
        arc2(ax, (0, 0), 0.09, 0, math.atan2(da[1], da[0]), C["ink"], 0.9)
        ax.text(0.1, 0.022, r"$\varphi_a$", fontsize=11)
        ax.text(-0.24, 0.48, T("(a) 在 {a} 中读：", "(a) Read in {a}:"), fontsize=10)
        ax.text(-0.24, 0.445, r"$d_a=(0.30,\ 0.20,\ 0)^{\mathsf{T}}\ \mathrm{m}$", fontsize=11)
    else:
        arrow2(ax, (0, 0), (L * 0.8, 0), C["x"], **weak)
        arrow2(ax, (0, 0), (0, L * 0.8), C["y"], **weak)
        arrow2(ax, (0, 0), L * xb, C["x"], strong)
        arrow2(ax, (0, 0), L * 0.8 * yb, C["y"], strong)
        ax.text(*(L * xb + [0.012, -0.01]), r"$\hat{\boldsymbol{x}}_b$", color=C["x"], fontsize=13)
        ax.text(*(L * 0.8 * yb + [-0.06, 0.0]), r"$\hat{\boldsymbol{y}}_b$", color=C["y"], fontsize=13)
        f1 = (da @ xb) * xb
        f2 = (da @ yb) * yb
        ax.plot([da[0], f1[0]], [da[1], f1[1]], ":", color=C["x"], lw=1.1)
        ax.plot([da[0], f2[0]], [da[1], f2[1]], ":", color=C["y"], lw=1.1)
        arc2(ax, (0, 0), 0.13, 0, beta, C["accent"], 1.0)
        ax.text(0.135, 0.02, r"$30^\circ$", fontsize=10.5, color=C["accent"])
        arc2(ax, (0, 0), 0.2, beta, math.atan2(da[1], da[0]), C["ink"], 0.9)
        ax.text(0.205, 0.105, r"$\varphi_b$", fontsize=11)
        ax.text(-0.24, 0.48, T("(b) 在 {b} 中读：", "(b) Read in {b}:"), fontsize=10)
        ax.text(-0.24, 0.445, rf"$d_b=({da @ xb:.4f},\ {da @ yb:.4f},\ 0)^{{\mathsf{{T}}}}\ \mathrm{{m}}$", fontsize=11)
    arrow2(ax, (0, 0), da, C["ink"], 2.4, z=5)
    ax.text(da[0] + 0.008, da[1] + 0.008, r"$\boldsymbol{d}$", fontsize=15)
    ax.text(-0.05, -0.1, T(f"同一支箭头，长度都是 {np.linalg.norm(da):.4f} m", f"the same arrow; length {np.linalg.norm(da):.4f} m in both"),
            fontsize=9.5, color=C["muted"])
    ax.set_xlim(-0.26, 0.5)
    ax.set_ylim(-0.13, 0.5)
fig.subplots_adjust(wspace=0.05)
figure(fig, "fig3_1_2")
plt.close(fig)
