"""3.2 节的示意图。

图 3.2.1：(a) 点积是投影：a·ê = |a| cos θ；(b) 叉积：长度等于平行四边形面积，方向按右手定则垂直于两者。
图 3.2.2：算例 3.2.2：零件的重力对力传感器中心的力矩 m = r × F（侧视与俯视）。
图 3.2.3：(a) 混合积是平行六面体的有向体积；(b) 二重叉积的几何意义：û × (û × v) = −v⊥。
"""
import math

import numpy as np

from _vec import C, arc2, arrow2, arrow3, circle3, sub3d, unit
from bookout import T, figure, style

plt = style()
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

# ---------------------------------------------------------------- 图 3.2.1
fig = plt.figure(figsize=(10.0, 4.3))
ax = fig.add_subplot(121)
ax.set_aspect("equal")
ax.axis("off")
O = np.array([0.0, 0.0])
e = np.array([1.0, 0.0])
a = np.array([1.25, 0.95])
th = math.atan2(a[1], a[0])
arrow2(ax, O, (2.0, 0), C["muted"], 1.0)
ax.text(2.02, -0.07, r"$\hat{\boldsymbol{e}}$" + T(" 的方向", " direction"), fontsize=11, color=C["muted"])
arrow2(ax, O, e * 0.5, C["accent"], 2.6)
ax.text(0.2, -0.17, r"$\hat{\boldsymbol{e}}$", fontsize=13, color=C["accent"])
arrow2(ax, O, a, C["ink"], 2.2)
ax.text(a[0] + 0.04, a[1] + 0.02, r"$\boldsymbol{a}$", fontsize=14)
ax.plot([a[0], a[0]], [0, a[1]], ":", color=C["muted"], lw=1.1)
ax.plot([0, a[0]], [0, 0], color=C["x"], lw=4, alpha=0.6)
ax.text(a[0] / 2 + 0.1, -0.2, r"$|\boldsymbol{a}|\cos\theta=\boldsymbol{a}\cdot\hat{\boldsymbol{e}}$", fontsize=12,
        color=C["x"], ha="center")
arc2(ax, O, 0.36, 0, th, C["ink"], 0.9)
ax.text(0.4, 0.12, r"$\theta$", fontsize=12)
ax.text(-0.05, 1.42, T("(a) 点积：投影的长度", "(a) Dot product: the length of a projection"), fontsize=10)
ax.set_xlim(-0.15, 2.5)
ax.set_ylim(-0.45, 1.55)

ax3 = sub3d(fig, 122, elev=34, azim=-68, lim=0.85, zoom=1.3, center=(0.5, 0.4, 0.35))
A = np.array([1.0, 0.0, 0.0])
B = np.array([0.45, 0.85, 0.0])
N = np.cross(A, B)
ax3.add_collection3d(Poly3DCollection([[np.zeros(3), A, A + B, B]], facecolor="#f3e2b3", edgecolor=C["accent"], alpha=0.6, lw=0.8))
arrow3(ax3, np.zeros(3), A, C["x"], 2.2)
arrow3(ax3, np.zeros(3), B, C["y"], 2.2)
arrow3(ax3, np.zeros(3), N, C["z"], 2.2)
ax3.text(*(A * 1.08 + [0, -0.08, 0]), r"$\boldsymbol{a}$", color=C["x"], fontsize=14)
ax3.text(*(B * 1.1), r"$\boldsymbol{b}$", color=C["y"], fontsize=14)
ax3.text(*(N * 1.05 + [0.05, 0, 0.02]), r"$\boldsymbol{a}\times\boldsymbol{b}$", color=C["z"], fontsize=13)
circle3(ax3, np.zeros(3), unit(A), unit(np.cross(N, A)), 0.32, 0, math.atan2(np.linalg.norm(np.cross(A, B)), A @ B), C["ink"], 1.0)
ax3.text(0.3, 0.13, 0, r"$\theta$", fontsize=12)
ax3.text(*(0.62 * (A + B) + [0.05, 0, 0.0]), T("面积 = |a||b| sin θ", "area = |a||b| sin θ"), fontsize=9.5, color="#8a6d2b", ha="center")
# 右手定则：绕 a×b 的小圆弧，从 a 转向 b
circle3(ax3, N * 0.75, np.array([1, 0, 0]), np.array([0, 1, 0]), 0.16, -0.3, 4.6, C["muted"], 1.0)
ax3.text2D(0.02, 0.94, T("(b) 叉积：长度为面积，方向按右手定则", "(b) Cross product: length = area, direction by the right-hand rule"),
           transform=ax3.transAxes, fontsize=10)
fig.subplots_adjust(wspace=0.02)
figure(fig, "fig3_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 3.2.2
r = np.array([0.08, 0.03, -0.10])
fig, (axs, axt) = plt.subplots(1, 2, figsize=(9.6, 4.2), gridspec_kw={"width_ratios": [1.15, 1]})
for axx in (axs, axt):
    axx.set_aspect("equal")
    axx.axis("off")
# 侧视（x 向右，z 向上）
S = np.array([0.0, 0.0])
axs.add_patch(plt.Rectangle((-0.035, 0.0), 0.07, 0.03, fc="#d9dee2", ec=C["muted"]))     # 传感器
axs.add_patch(plt.Rectangle((-0.02, 0.03), 0.04, 0.05, fc="#eef1f3", ec=C["muted"]))     # 法兰
axs.text(0.045, 0.012, T("力传感器", "F/T sensor"), fontsize=9.5, color=C["muted"])
axs.add_patch(plt.Rectangle((-0.025, -0.06), 0.05, 0.06, fc="#cfd6db", ec=C["muted"]))   # 夹爪
part = plt.Polygon([[-0.03, -0.06], [0.14, -0.06], [0.14, -0.14], [-0.03, -0.14]], fc="#f3e2b3", ec=C["accent"])
axs.add_patch(part)
G = np.array([r[0], r[2]])
axs.plot(*S, "o", color=C["ink"], ms=4, zorder=6)
axs.text(-0.03, 0.012, "O", fontsize=11, ha="right")
arrow2(axs, S, G, C["ink"], 1.8, z=6)
axs.text(0.052, -0.035, r"$\boldsymbol{r}$", fontsize=14)
axs.plot(*G, "o", color=C["x"], ms=5, zorder=6)
arrow2(axs, G, G + [0, -0.09], C["x"], 2.2, z=6)
axs.text(G[0] + 0.008, G[1] - 0.085, r"$\boldsymbol{F}=m\boldsymbol{g}$", fontsize=12, color=C["x"])
axs.plot([0, 0], [0.0, -0.24], "--", color=C["muted"], lw=0.9)
axs.annotate("", xy=(G[0], -0.205), xytext=(0, -0.205), arrowprops=dict(arrowstyle="<->", color=C["accent"], lw=1))
axs.text(G[0] / 2, -0.228, T("力臂 ρ（俯视中量）", "lever arm ρ (see top view)"), fontsize=9.5, color=C["accent"], ha="center")
axs.text(-0.16, 0.1, T("(a) 侧视：x 向右，z 向上", "(a) Side view: x right, z up"), fontsize=10)
axs.set_xlim(-0.17, 0.25)
axs.set_ylim(-0.25, 0.12)
# 俯视（x 向右，y 向上）：力矩矢量在水平面内，垂直于力臂
arrow2(axt, (0, 0), (0.13, 0), C["x"], 1.0)
arrow2(axt, (0, 0), (0, 0.11), C["y"], 1.0)
axt.text(0.133, -0.006, "$x$", color=C["x"], fontsize=12)
axt.text(0.004, 0.112, "$y$", color=C["y"], fontsize=12)
Gt = np.array([r[0], r[1]])
axt.plot(*Gt, "o", color=C["x"], ms=5)
axt.plot([0, Gt[0]], [0, Gt[1]], color=C["accent"], lw=2)
axt.text(Gt[0] / 2 + 0.003, Gt[1] / 2 + 0.012, r"$\rho$", fontsize=12, color=C["accent"])
axt.text(Gt[0] + 0.006, Gt[1] - 0.012, T("质心（重力向下，垂直纸面）", "centre of mass (weight into the page)"), fontsize=9)
mvec = np.cross(r, [0, 0, -14.715])
ms = mvec[:2] / np.linalg.norm(mvec) * 0.09
arrow2(axt, (0, 0), ms, C["z"], 2.4)
axt.text(ms[0] - 0.05, ms[1] + 0.006, r"$\boldsymbol{m}=\boldsymbol{r}\times\boldsymbol{F}$", fontsize=12, color=C["z"])
axt.plot(0, 0, "o", color=C["ink"], ms=4)
axt.text(-0.012, -0.016, "O", fontsize=11)
axt.text(-0.1, 0.15, T("(b) 俯视：m 在水平面内，垂直于力臂", "(b) Top view: m is horizontal, perpendicular to the lever arm"), fontsize=10)
axt.set_xlim(-0.11, 0.2)
axt.set_ylim(-0.05, 0.16)
fig.subplots_adjust(wspace=0.12)
figure(fig, "fig3_2_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 3.2.3
fig = plt.figure(figsize=(10.0, 4.4))
ax = sub3d(fig, 121, elev=18, azim=-55, lim=0.95, zoom=1.25, center=(0.55, 0.45, 0.4))
a = np.array([1.0, 0.0, 0.0])
b = np.array([0.3, 0.8, 0.0])
c = np.array([0.25, 0.2, 0.75])
V = [np.zeros(3), a, b, a + b]
faces = []
for base in (np.zeros(3), c):
    faces.append([base, base + a, base + a + b, base + b])
for p0, p1 in ((np.zeros(3), a), (a, a + b), (a + b, b), (b, np.zeros(3))):
    faces.append([p0, p1, p1 + c, p0 + c])
ax.add_collection3d(Poly3DCollection(faces, facecolor="#dbe7f3", edgecolor=C["muted"], alpha=0.16, lw=0.6))
ax.add_collection3d(Poly3DCollection([faces[0]], facecolor="#f3e2b3", edgecolor=C["accent"], alpha=0.8, lw=0.8))
arrow3(ax, np.zeros(3), a, C["x"], 2.2)
arrow3(ax, np.zeros(3), b, C["y"], 2.2)
arrow3(ax, np.zeros(3), c, C["ink"], 2.2)
n = np.cross(a, b)
arrow3(ax, np.zeros(3), n * 0.95, C["z"], 1.6)
ax.text(*(a * 1.06 + [0, -0.12, 0]), r"$\boldsymbol{a}$", color=C["x"], fontsize=14)
ax.text(*(b * 1.12), r"$\boldsymbol{b}$", color=C["y"], fontsize=14)
ax.text(*(c + [0.02, -0.12, 0.03]), r"$\boldsymbol{c}$", color=C["ink"], fontsize=14)
ax.text(*(n * 0.95 + [-0.05, -0.05, 0.06]), r"$\boldsymbol{a}\times\boldsymbol{b}$", color=C["z"], fontsize=12)
ax.plot([c[0], c[0]], [c[1], c[1]], [0, c[2]], ":", color=C["accent"], lw=1.4)
ax.text(c[0] + 0.03, c[1], c[2] / 2, r"$h$", color="#8a6d2b", fontsize=14)
ax.text2D(0.02, 0.95, T("(a) 混合积 (a×b)·c = 底面积 × 高", "(a) (a×b)·c = base area × height"), transform=ax.transAxes, fontsize=10)

ax = sub3d(fig, 122, elev=20, azim=-60, lim=0.95, zoom=1.25, center=(0.3, 0.2, 0.45))
uh = np.array([0.0, 0.0, 1.0])
v = np.array([0.8, 0.15, 0.6])
vpar = (uh @ v) * uh
vperp = v - vpar
uxv = np.cross(uh, v)
uuxv = np.cross(uh, uxv)
arrow3(ax, np.zeros(3), uh * 1.05, C["ink"], 2.0)
ax.text(0, 0, 1.12, r"$\hat{\boldsymbol{u}}$", fontsize=14)
arrow3(ax, np.zeros(3), v, C["accent"], 2.2)
ax.text(*(v + [0.03, 0, 0.04]), r"$\boldsymbol{v}$", color=C["accent"], fontsize=14)
arrow3(ax, vpar, vperp, C["x"], 2.0)
ax.text(*(vpar + 0.55 * vperp + [0, 0, 0.06]), r"$\boldsymbol{v}_\perp$", color=C["x"], fontsize=13)
arrow3(ax, vpar, uxv, C["y"], 2.0)
ax.text(*(vpar + uxv + [-0.05, 0.05, 0.05]), r"$\hat{\boldsymbol{u}}\times\boldsymbol{v}$", color=C["y"], fontsize=12)
arrow3(ax, vpar, uuxv, C["z"], 2.0)
ax.text(*(vpar + uuxv + [-0.02, -0.05, -0.12]), r"$\hat{\boldsymbol{u}}\times(\hat{\boldsymbol{u}}\times\boldsymbol{v})=-\boldsymbol{v}_\perp$",
        color=C["z"], fontsize=11.5, ha="center")
circle3(ax, vpar, unit(vperp), unit(uxv), np.linalg.norm(vperp), 0, 2 * math.pi, C["muted"], 0.8, ":")
ax.plot([0, vpar[0]], [0, vpar[1]], [0, vpar[2]], color=C["ink"], lw=3, alpha=0.5)
ax.text(-0.3, 0, vpar[2] / 2, r"$(\hat{\boldsymbol{u}}\cdot\boldsymbol{v})\hat{\boldsymbol{u}}$", fontsize=11, ha="right")
ax.text2D(0.02, 0.95, T("(b) 二重叉积：每叉乘一次 û，在垂直平面内转 90°", "(b) Each cross product with û turns 90° in the plane across û"),
          transform=ax.transAxes, fontsize=10)
fig.subplots_adjust(wspace=0.02)
figure(fig, "fig3_2_3")
plt.close(fig)
