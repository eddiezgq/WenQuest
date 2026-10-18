"""23.1 节的示意图。

图 23.1.1：(a) 刚体绕定点 O 转动：质点 P 的位置 r、速度 v = ω × r、到转轴的距离 d；角动量 L = I_O ω 一般不沿 ω（示意）；
          (b) SH-301 毛坯（侧视）：ω 与轴线成 30° 时 L = I ω 偏向横轴（毛坯的实际惯量），两根主轴方向上 L 与 ω 同向。
图 23.1.2：(a) 常见均匀形体对质心的主惯量；(b) 算例 23.1.3：UR5e 零位，各连杆的“等效圆柱”（半径、长度由主惯量反推）。
图 23.1.3：算例 23.1.4：(a) 夹偏的毛坯绕主轴转动（角度放大画出）；(b) 轴承力矩随夹偏角的变化，点为 MuJoCo。
"""
import math

import numpy as np

from _ch23 import cyl_inertia, link_poses, mj_load, mjcf_text, parse_links, sh301_blank, ur_points, rotx
from bookout import COLORS as C, T, figure, style

plt = style()
m_b, r_b, L_b = sh301_blank()
Ic = cyl_inertia(m_b, r_b, L_b)
I_t, I_a = Ic[0, 0], Ic[2, 2]


def arrow(ax, p, q, color, lw=1.6, ms=11, z=5, ls="-"):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=ms,
                                                    shrinkA=0, shrinkB=0, linestyle=ls), zorder=z)


# ---------------------------------------------------------------- 图 23.1.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 4.8), gridspec_kw=dict(width_ratios=[1.0, 1.15]))
for ax in (a1, a2):
    ax.set_aspect("equal")
    ax.axis("off")
# (a) 一块不规则的刚体（平面示意），O 固定，ω 竖直向上（在纸面内）
t = np.linspace(0, 2 * math.pi, 200)
blob = np.c_[1.25 * np.cos(t) + 0.18 * np.cos(3 * t) + 0.35, 0.95 * np.sin(t) + 0.12 * np.sin(2 * t) + 0.55]
a1.fill(*blob.T, fc="#dbe9f6", ec=C["z"], lw=1.2, alpha=0.8)
O = np.array([0.0, 0.0])
a1.plot(*O, "o", color=C["ink"], ms=5, zorder=6)
a1.text(-0.18, -0.22, "O", fontsize=12, color=C["ink"])
a1.plot([0, 0], [-0.55, 2.15], color=C["muted"], lw=0.9, ls="--", zorder=1)
arrow(a1, O, (0, 1.9), C["z"], lw=2.2)
a1.text(0.07, 1.95, r"$\boldsymbol{\omega}$", fontsize=14, color=C["z"])
P = np.array([1.05, 1.05])
arrow(a1, O, P, C["ink"], lw=1.3)
a1.text(0.42, 0.62, r"$\boldsymbol{r}$", fontsize=13, color=C["ink"])
a1.plot(*P, "o", color=C["x"], ms=6, zorder=6)
a1.text(P[0] + 0.07, P[1] + 0.07, "P", fontsize=12, color=C["x"])
a1.plot([0, P[0]], [P[1], P[1]], color=C["accent"], lw=1.2, ls=":")
a1.text(0.38, P[1] + 0.07, "d", fontsize=13, color=C["accent"], style="italic")
# v = ω × r 垂直于纸面向里：画 ⊗
a1.add_patch(plt.Circle(P + [0.32, -0.28], 0.08, fc="white", ec=C["y"], lw=1.4, zorder=6))
a1.plot([P[0] + 0.32 - 0.055, P[0] + 0.32 + 0.055], [P[1] - 0.28 - 0.055, P[1] - 0.28 + 0.055], color=C["y"], lw=1.4, zorder=7)
a1.plot([P[0] + 0.32 - 0.055, P[0] + 0.32 + 0.055], [P[1] - 0.28 + 0.055, P[1] - 0.28 - 0.055], color=C["y"], lw=1.4, zorder=7)
a1.text(P[0] + 0.45, P[1] - 0.36, T("v = ω × r（垂直纸面向里）", "v = ω × r (into the page)"), fontsize=10, color=C["y"])
arrow(a1, O, (-0.75, 1.62), C["x"], lw=2.2)
a1.text(-1.05, 1.68, r"$\boldsymbol{L}_O = I_O\,\boldsymbol{\omega}$", fontsize=13, color=C["x"])
a1.text(-1.35, -0.62, T("(a) 绕定点 O 转动：L 一般不沿 ω", "(a) rotation about a fixed point O: L is generally not along ω"), fontsize=11)
a1.set_xlim(-1.5, 2.6)
a1.set_ylim(-0.75, 2.3)

# (b) 毛坯（侧视），轴线水平；ω 与轴线成 30°
Lh, rh = 2.6, 0.36                     # 画图用的尺寸（按毛坯的长径比 L/(2r) ≈ 3.6）
a2.add_patch(plt.Rectangle((-Lh / 2, -rh), Lh, 2 * rh, fc="#c9ced3", ec=C["ink"], lw=1.0))
a2.plot([-1.75, 1.75], [0, 0], color=C["muted"], lw=0.9, ls="-.")
a2.plot([0, 0], [-1.25, 1.35], color=C["muted"], lw=0.9, ls="-.")
a2.text(1.78, -0.05, T("轴线（$I_a$）", "axis ($I_a$)"), fontsize=10, color=C["muted"], va="center")
a2.text(0.05, -1.38, T("横轴（$I_t$）", "transverse ($I_t$)"), fontsize=10, color=C["muted"])
phi = math.radians(30)
w = np.array([math.cos(phi), math.sin(phi)])
Lv = np.array([I_a * w[0], I_t * w[1]])
Lv = Lv / np.linalg.norm(Lv)
arrow(a2, (0, 0), 1.35 * w, C["z"], lw=2.2)
a2.text(1.35 * w[0] + 0.04, 1.35 * w[1] - 0.02, r"$\boldsymbol{\omega}$", fontsize=14, color=C["z"])
arrow(a2, (0, 0), 1.25 * Lv, C["x"], lw=2.2)
a2.text(1.25 * Lv[0] + 0.06, 1.25 * Lv[1] - 0.05, r"$\boldsymbol{L} = I\boldsymbol{\omega}$", fontsize=13, color=C["x"])
ang_L = math.degrees(math.atan2(Lv[1], Lv[0]))
a2.text(-1.85, -0.62, T(f"ω 与轴线成 30°，L 与轴线成 {ang_L:.0f}°", f"ω at 30° to the axis, L at {ang_L:.0f}°"), fontsize=10.5, color=C["ink"])
a2.text(-1.85, -0.88, T(f"$I_t/I_a$ = {I_t / I_a:.1f}：L 偏向", f"$I_t/I_a$ = {I_t / I_a:.1f}: L leans towards"), fontsize=10.5, color=C["ink"])
a2.text(-1.85, -1.12, T("转动惯量大的横轴", "the transverse axis"), fontsize=10.5, color=C["ink"])
a2.text(-1.75, -1.7, T("(b) SH-301 毛坯：只有沿主轴转动时 L 才与 ω 同向", "(b) SH-301 blank: L is along ω only about a principal axis"), fontsize=11)
a2.set_xlim(-1.9, 2.75)
a2.set_ylim(-1.85, 1.45)
figure(fig, "fig23_1_1")

# ---------------------------------------------------------------- 图 23.1.2
fig = plt.figure(figsize=(12.4, 5.2))
ax = fig.add_axes([0.0, 0.0, 0.44, 1.0])
ax.axis("off")
ax.set_xlim(0, 10)
ax.set_ylim(0, 10.6)
shapes = [
    (T("长方体 a×b×c", "box a×b×c"), r"$I_{xx} = \frac{m}{12}(b^2 + c^2)$" + "\n" + T("（另两个轮换）", "(cyclic for the others)")),
    (T("实心圆柱 r, L", "solid cylinder r, L"), r"$I_{zz} = \frac{1}{2} mr^2$" + "\n" + r"$I_{xx} = \frac{m}{12}(3r^2 + L^2)$"),
    (T("细杆 L", "slender rod L"), r"$I = \frac{1}{12}mL^2$"),
    (T("薄圆盘 r", "thin disc r"), r"$I_{zz} = \frac{1}{2} mr^2,\ \ I_{xx} = \frac{1}{4} mr^2$"),
    (T("实心球 r", "solid sphere r"), r"$I = \frac{2}{5} mr^2$"),
]
for k, (nm, fm) in enumerate(shapes):
    y = 9.4 - 2.0 * k
    cx = 1.3
    if k == 0:
        ax.add_patch(plt.Polygon([[cx - 0.8, y - 0.45], [cx + 0.5, y - 0.45], [cx + 0.5, y + 0.25], [cx - 0.8, y + 0.25]], fc="#dbe9f6", ec=C["z"]))
        ax.add_patch(plt.Polygon([[cx - 0.8, y + 0.25], [cx - 0.5, y + 0.55], [cx + 0.8, y + 0.55], [cx + 0.5, y + 0.25]], fc="#eef4fa", ec=C["z"]))
        ax.add_patch(plt.Polygon([[cx + 0.5, y - 0.45], [cx + 0.8, y - 0.15], [cx + 0.8, y + 0.55], [cx + 0.5, y + 0.25]], fc="#c6dbef", ec=C["z"]))
    elif k == 1:
        ax.add_patch(plt.Rectangle((cx - 0.9, y - 0.3), 1.8, 0.6, fc="#dbe9f6", ec=C["z"]))
        ax.add_patch(plt.matplotlib.patches.Ellipse((cx + 0.9, y), 0.25, 0.6, fc="#c6dbef", ec=C["z"]))
        ax.plot([cx - 1.15, cx + 1.25], [y, y], color=C["muted"], lw=0.8, ls="-.")
        ax.text(cx + 1.28, y - 0.12, "z", fontsize=10, color=C["muted"])
    elif k == 2:
        ax.plot([cx - 1.0, cx + 1.0], [y, y], color=C["z"], lw=4, solid_capstyle="round")
        ax.plot([cx, cx], [y - 0.5, y + 0.5], color=C["muted"], lw=0.8, ls="-.")
    elif k == 3:
        ax.add_patch(plt.matplotlib.patches.Ellipse((cx, y), 1.7, 0.55, fc="#dbe9f6", ec=C["z"]))
        ax.plot([cx, cx], [y - 0.55, y + 0.6], color=C["muted"], lw=0.8, ls="-.")
        ax.text(cx + 0.06, y + 0.5, "z", fontsize=10, color=C["muted"])
    else:
        ax.add_patch(plt.Circle((cx, y), 0.48, fc="#dbe9f6", ec=C["z"]))
    ax.text(3.0, y + 0.22, nm, fontsize=11, color=C["ink"], va="center")
    ax.text(3.0, y - 0.42, fm, fontsize=11, color=C["ink"], va="center")
ax.text(0.2, 0.1, T("(a) 常见均匀形体对质心的主惯量", "(a) principal moments of common uniform bodies about the centre of mass"), fontsize=11)

# (b) UR5e 零位，“等效圆柱”
links = parse_links(mjcf_text())
Tp = link_poses(links, np.zeros(6))
ax3 = fig.add_axes([0.42, 0.04, 0.54, 0.96], projection="3d")
ax3.view_init(elev=18, azim=-62)
ax3.set_axis_off()
P = ur_points(np.zeros(6))
ax3.plot(*P.T, color=C["muted"], lw=1.0, ls="--")
cols = ["#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b", "#d9730d"]
for k, L in enumerate(links):
    vals, cnt = np.unique(np.round(L.diag, 12), return_counts=True)
    I_ax = float(vals[cnt == 1][0])
    I_tr = float(vals[cnt == 2][0])
    r = math.sqrt(2 * I_ax / L.m)
    ln = math.sqrt(12 * I_tr / L.m - 3 * r * r)
    j = int(np.where(np.isclose(L.diag, I_ax))[0][0])
    Ti = Tp[L.name]
    R = Ti[:3, :3] @ L.R_ic
    axis = R[:, j]
    c = Ti[:3, :3] @ L.ipos + Ti[:3, 3]
    e1 = np.cross(axis, [0, 0, 1.0]) if abs(axis[2]) < 0.9 else np.cross(axis, [1.0, 0, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(axis, e1)
    u = np.linspace(0, 2 * math.pi, 28)
    s = np.array([-ln / 2, ln / 2])
    U, S = np.meshgrid(u, s)
    X = c[0] + S * axis[0] + r * (np.cos(U) * e1[0] + np.sin(U) * e2[0])
    Y = c[1] + S * axis[1] + r * (np.cos(U) * e1[1] + np.sin(U) * e2[1])
    Z = c[2] + S * axis[2] + r * (np.cos(U) * e1[2] + np.sin(U) * e2[2])
    ax3.plot_surface(X, Y, Z, color=cols[k], alpha=0.45, linewidth=0, shade=True)
    ax3.scatter(*c, s=18 + 6 * L.m, color=C["x"], depthshade=False, zorder=6)
lab = {"upper_arm_link": (T("大臂 ℓ = 0.425", "upper arm ℓ = 0.425"), (0.0, -0.05, -0.15)),
       "forearm_link": (T("小臂 ℓ = 0.392", "forearm ℓ = 0.392"), (0.0, -0.05, 0.12)),
       "shoulder_link": (T("肩 ℓ = 0.15", "shoulder ℓ = 0.15"), (-0.02, 0.0, 0.15)),
       "base": (T("基座 ℓ = 0.05", "base ℓ = 0.05"), (-0.02, 0.0, -0.085)),
       "wrist_1_link": (T("腕 1、2 ℓ = 0.12", "wrists 1, 2 ℓ = 0.12"), (0.02, -0.02, 0.17))}
for nm, (txt, off) in lab.items():
    L = [x for x in links if x.name == nm][0]
    c = Tp[nm][:3, :3] @ L.ipos + Tp[nm][:3, 3]
    ax3.text(c[0] + off[0], c[1] + off[1], c[2] + off[2], txt, fontsize=10, color=C["ink"], ha="center")
ax3.text2D(0.04, 0.86, T("半径都是 0.06 m（腕 3 除外），长度单位 m；红点为质心", "radius 0.06 m for all but wrist 3; lengths in m; red dots: centres of mass"),
           transform=ax3.transAxes, fontsize=10, color=C["ink"])
ax3.text2D(0.04, 0.08, T("(b) 算例 23.1.3：UR5e 各连杆的“等效均匀圆柱”（零位）", "(b) Example 23.1.3: the UR5e links as uniform cylinders (zero position)"),
           transform=ax3.transAxes, fontsize=11)
xl, yl, zl = (-0.95, 0.12), (-0.32, 0.10), (-0.06, 0.30)
ax3.set_xlim(*xl)
ax3.set_ylim(*yl)
ax3.set_zlim(*zl)
ax3.set_box_aspect((xl[1] - xl[0], yl[1] - yl[0], zl[1] - zl[0]), zoom=1.15)
figure(fig, "fig23_1_2")

# ---------------------------------------------------------------- 图 23.1.3
fig, (b1, b2) = plt.subplots(1, 2, figsize=(11.6, 4.6), gridspec_kw=dict(width_ratios=[1.0, 1.2]))
b1.set_aspect("equal")
b1.axis("off")
al = math.radians(14)                  # 画图时放大的夹偏角
R2 = np.array([[math.cos(al), math.sin(al)], [-math.sin(al), math.cos(al)]])    # 毛坯上端偏向右（−y_s 方向）
box = np.array([[-0.38, -1.25], [0.38, -1.25], [0.38, 1.25], [-0.38, 1.25]])     # 毛坯（竖直放，轴线沿 z）
b1.fill(*(R2 @ box.T), fc="#c9ced3", ec=C["ink"], lw=1.0)
b1.plot([0, 0], [-1.9, 2.3], color=C["muted"], lw=0.9, ls="-.")
ax_b = R2 @ np.array([0, 1.0])
b1.plot([-1.7 * ax_b[0], 1.7 * ax_b[0]], [-1.7 * ax_b[1], 1.7 * ax_b[1]], color=C["ink"], lw=0.8, ls=":")
b1.text(1.75 * ax_b[0] + 0.05, 1.75 * ax_b[1] - 0.1, T("毛坯轴线", "blank axis"), fontsize=10)
b1.text(0.06, 2.22, T("主轴 z", "spindle z"), fontsize=10, color=C["muted"])
arrow(b1, (0, 0), (0, 1.75), C["z"], lw=2.2)
b1.text(0.1, 1.55, r"$\boldsymbol{\omega}$", fontsize=14, color=C["z"])
Is = rotx(al) @ Ic @ rotx(al).T
Lw = Is @ np.array([0, 0, 1.0])
Ld = np.array([-Lw[1], Lw[2]])
Ld = Ld / np.linalg.norm(Ld) * 1.6
arrow(b1, (0, 0), Ld, C["x"], lw=2.2)
b1.text(Ld[0] - 0.55, Ld[1] + 0.05, r"$\boldsymbol{L}$", fontsize=14, color=C["x"])
th = np.linspace(math.pi / 2, math.atan2(Ld[1], Ld[0]), 30)
b1.plot(0.7 * np.cos(th), 0.7 * np.sin(th), color=C["x"], lw=0.9)
b1.text(-0.62, 0.78, "β", fontsize=12, color=C["x"])
b1.add_patch(plt.Circle((1.25, -0.55), 0.11, fc="white", ec=C["accent"], lw=1.5, zorder=6))
b1.plot(1.25, -0.55, "o", color=C["accent"], ms=3, zorder=7)
b1.text(1.43, -0.63, T("M = ω × L\n（指向纸外，\n随毛坯转）", "M = ω × L\n(out of the page,\nturns with the blank)"), fontsize=10, color=C["accent"])
th2 = np.linspace(-0.4, 3.6, 60)
b1.plot(0.5 * np.cos(th2), -1.65 + 0.12 * np.sin(th2), color=C["z"], lw=1.0)
b1.text(-1.95, -2.25, T("(a) 夹偏的毛坯（角度放大画出）", "(a) the tilted blank (angle exaggerated)"), fontsize=11)
b1.set_xlim(-2.0, 2.4)
b1.set_ylim(-2.35, 2.45)

w = 1200 * 2 * math.pi / 60
aa = np.linspace(0, 90, 361)
Mf = w * w * abs(I_t - I_a) * np.sin(np.radians(aa)) * np.cos(np.radians(aa))
b2.plot(aa, Mf, color=C["z"], lw=1.8, label=T("式 (23.1.16)", "Eq. (23.1.16)"))
pts_a, pts_m = [5, 15, 30, 45, 60, 75], []
for a_ in pts_a:
    q = (math.cos(math.radians(a_) / 2), math.sin(math.radians(a_) / 2), 0, 0)
    xml = (f'<mujoco><option timestep="0.0002" integrator="RK4"/><worldbody><body pos="0 0 0.5"><joint type="hinge" axis="0 0 1"/>'
           f'<site name="s"/><geom type="sphere" size="0.005" mass="1e-9" contype="0" conaffinity="0"/>'
           f'<body quat="{q[0]} {q[1]} 0 0"><geom type="cylinder" size="{r_b} {L_b / 2}" mass="{m_b}" contype="0" conaffinity="0"/></body>'
           f'</body></worldbody><sensor><torque site="s"/></sensor></mujoco>')
    mj, mm, dd = mj_load(xml)
    dd.qvel[0] = w
    for _ in range(50):
        mj.mj_step(mm, dd)
    pts_m.append(float(np.linalg.norm(dd.sensordata[:3])))
b2.plot(pts_a, pts_m, "o", color=C["x"], ms=6, label=T("MuJoCo 的约束力矩", "MuJoCo constraint torque"))
b2.plot([1], [w * w * abs(I_t - I_a) * math.sin(math.radians(1)) * math.cos(math.radians(1))], "s", color=C["accent"], ms=6)
b2.annotate(T("算例 23.1.4：α = 1°，2.0 N·m", "Example 23.1.4: α = 1°, 2.0 N·m"), xy=(1, 2.0), xytext=(9, 4),
            fontsize=10, color=C["accent"], arrowprops=dict(arrowstyle="-", color=C["accent"], lw=0.8))
b2.set_xlabel(T("夹偏角 α / (°)", "tilt α / (°)"))
b2.set_ylabel(T("轴承力矩 |M| / (N·m)", "bearing moment |M| / (N·m)"))
b2.set_xlim(0, 90)
b2.set_ylim(0, 65)
b2.set_xticks([0, 15, 30, 45, 60, 75, 90])
b2.grid(True, color="#ececec", lw=0.6)
for sp in ("top", "right"):
    b2.spines[sp].set_visible(False)
b2.legend(loc="upper right", frameon=False, fontsize=10)
b2.set_title(T("(b) 1200 r/min 时轴承力矩与夹偏角", "(b) bearing moment against tilt at 1200 r/min"), fontsize=11, loc="left")
figure(fig, "fig23_1_3")
