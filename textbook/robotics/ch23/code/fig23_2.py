"""23.2 节的示意图。

图 23.2.1：(a) 平行轴定理：轴 A 与过质心的轴 C 平行、相距 d；(b) 算例 23.2.1：UR5e 大臂（侧视，零位），质心与关节 2 轴，
          对质心与对关节轴的转动惯量（模型的数值）。
图 23.2.2：(a) 米尺（L = 1 m）挂在离中点 d 处的周期，d = k 最短，d 与 k²/d 周期相同；
          (b) 算例 23.2.3：小臂绕关节 3 轴摆动的周期随振幅的变化（椭圆积分），点为 MuJoCo 的仿真。
"""
import math

import numpy as np
from scipy.special import ellipk

from _ch23 import G0, mj_load, mjcf_text, parse_links, sign_changes
from bookout import COLORS as C, T, figure, style

plt = style()


def arrow(ax, p, q, color, lw=1.5, ms=11, z=5, style_="-|>"):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle=style_, color=color, lw=lw, mutation_scale=ms, shrinkA=0, shrinkB=0), zorder=z)


links = {L.name: L for L in parse_links(mjcf_text())}

# ---------------------------------------------------------------- 图 23.2.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.8, 4.4), gridspec_kw=dict(width_ratios=[1.0, 1.35]))
for ax in (a1, a2):
    ax.set_aspect("equal")
    ax.axis("off")
t = np.linspace(0, 2 * math.pi, 200)
blob = np.c_[0.95 * np.cos(t) + 0.12 * np.cos(2 * t), 1.25 * np.sin(t) + 0.1 * np.sin(3 * t)]
a1.fill(*blob.T, fc="#dbe9f6", ec=C["z"], lw=1.2)
a1.plot(0, 0, "o", color=C["x"], ms=6, zorder=6)
a1.text(0.08, -0.22, "C", fontsize=12, color=C["x"])
for x, nm in ((0.0, T("过质心的轴 C", "axis C through the centre of mass")), (1.7, T("轴 A", "axis A"))):
    a1.plot([x, x], [-1.65, 1.75], color=C["ink"] if x else C["x"], lw=1.0, ls="-.")
a1.text(-0.95, 1.85, T("过质心的轴 C", "axis C (through CoM)"), fontsize=10.5, color=C["x"])
a1.text(1.45, 1.85, T("轴 A", "axis A"), fontsize=10.5, color=C["ink"])
arrow(a1, (0.0, -1.45), (1.7, -1.45), C["accent"], style_="<|-|>")
a1.text(0.78, -1.38, "d", fontsize=13, color=C["accent"], style="italic")
a1.text(-1.0, -2.2, r"$I_A = I_C + m\,d^2$", fontsize=14, color=C["ink"])
a1.text(-1.15, -2.75, T("(a) 平行轴定理", "(a) the parallel-axis theorem"), fontsize=11)
a1.set_xlim(-1.3, 2.4)
a1.set_ylim(-2.9, 2.1)

ua = links["upper_arm_link"]
L1 = 0.425
d = float(ua.ipos[2])
J2 = float(ua.diag[1] + ua.m * d * d)
# 侧视（零位：大臂沿 −x 水平），画成水平的杆：关节 2 在右端
x2, x3 = 0.0, -L1
a2.add_patch(plt.Rectangle((x3, -0.06), L1, 0.12, fc="#c6dbef", ec=C["z"], lw=1.0))
for x, nm in ((x2, T("关节 2", "joint 2")), (x3, T("关节 3", "joint 3"))):
    a2.add_patch(plt.Circle((x, 0), 0.045, fc="white", ec=C["ink"], lw=1.3, zorder=5))
    a2.plot(x, 0, "o", color=C["ink"], ms=2.5, zorder=6)
    a2.text(x, 0.1, nm, fontsize=10.5, ha="center", color=C["ink"])
xc = x2 - d
a2.plot(xc, 0, "o", color=C["x"], ms=7, zorder=6)
a2.text(xc, -0.13, T("质心", "CoM"), fontsize=10.5, color=C["x"], ha="center")
arrow(a2, (x2, -0.2), (xc, -0.2), C["accent"], style_="<|-|>")
a2.text((x2 + xc) / 2, -0.28, f"d = {d:.4f} m", fontsize=10.5, color=C["accent"], ha="center")
a2.text(-0.47, 0.50, T(f"m = {ua.m:.3f} kg", f"m = {ua.m:.3f} kg"), fontsize=10.5)
a2.text(-0.47, 0.42, T(f"对质心：$I_C$ = {ua.diag[1]:.4f} kg·m²", f"about the CoM: $I_C$ = {ua.diag[1]:.4f} kg·m²"), fontsize=10.5)
a2.text(-0.47, 0.34, T(f"m d² = {ua.m * d * d:.4f} kg·m²", f"m d² = {ua.m * d * d:.4f} kg·m²"), fontsize=10.5)
a2.text(-0.47, 0.26, T(f"对关节 2 轴：J₂ = {J2:.4f} kg·m²", f"about joint 2: J₂ = {J2:.4f} kg·m²"), fontsize=10.5, color=C["z"])
a2.text(-0.5, -0.42, T("(b) 算例 23.2.1：UR5e 大臂对关节 2 轴（侧视）", "(b) Example 23.2.1: the UR5e upper arm about joint 2 (side view)"), fontsize=11)
a2.set_xlim(-0.52, 0.1)
a2.set_ylim(-0.46, 0.58)
figure(fig, "fig23_2_1")

# ---------------------------------------------------------------- 图 23.2.2
fig, (b1, b2) = plt.subplots(1, 2, figsize=(11.8, 4.4))
k = 1 / math.sqrt(12)
dd = np.linspace(0.04, 0.5, 600)
Tp = 2 * math.pi * np.sqrt((k * k + dd * dd) / (G0 * dd))
b1.plot(dd, Tp, color=C["z"], lw=1.8)
Tmin = 2 * math.pi * math.sqrt(2 * k / G0)
b1.plot([k], [Tmin], "o", color=C["x"], ms=6)
b1.annotate(T(f"d = k = {k:.3f} m\nT = {Tmin:.3f} s（最短）", f"d = k = {k:.3f} m\nT = {Tmin:.3f} s (shortest)"), xy=(k, Tmin), xytext=(0.26, 1.33),
            fontsize=10, color=C["x"], ha="center", arrowprops=dict(arrowstyle="-", color=C["x"], lw=0.8))
d1, d2 = 0.2, k * k / 0.2
T12 = 2 * math.pi * math.sqrt((k * k + d1 * d1) / (G0 * d1))
b1.plot([d1, d2], [T12, T12], "s", color=C["accent"], ms=6)
b1.plot([d1, d2], [T12, T12], color=C["accent"], lw=0.9, ls="--")
b1.text((d1 + d2) / 2 + 0.03, T12 + 0.06, T(f"d = 0.2 与 k²/d = {d2:.3f}：周期相同", f"d = 0.2 and k²/d = {d2:.3f}: same period"), fontsize=10,
        color=C["accent"], ha="center", va="bottom")
Tend = 2 * math.pi * math.sqrt(2 / (3 * G0))
b1.plot([0.5], [Tend], "^", color=C["y"], ms=7)
b1.text(0.49, Tend + 0.04, T("挂在一端", "hung at the end"), fontsize=10, color=C["y"], ha="right")
b1.set_xlabel(T("悬挂点离中点的距离 d / m", "distance d of the pivot from the centre / m"))
b1.set_ylabel(T("周期 T / s", "period T / s"))
b1.set_xlim(0, 0.52)
b1.set_ylim(1.3, 2.4)
b1.grid(True, color="#ececec", lw=0.6)
for sp in ("top", "right"):
    b1.spines[sp].set_visible(False)
b1.set_title(T("(a) 米尺（1 m）的复摆", "(a) a metre stick as a physical pendulum"), fontsize=11, loc="left")

fa = links["forearm_link"]
dfa = float(fa.ipos[2])
Jo = float(fa.diag[0] + fa.m * dfa * dfa)
T0 = 2 * math.pi * math.sqrt(Jo / (fa.m * G0 * dfa))
amp = np.linspace(0, 60, 241)
ratio = 2 / math.pi * ellipk(np.sin(np.radians(amp) / 2) ** 2)
b2.plot(amp, ratio * T0, color=C["z"], lw=1.8, label=T("精确公式（椭圆积分）", "exact (elliptic integral)"))
b2.axhline(T0, color=C["muted"], lw=1.0, ls="--", label=T(f"小幅近似 {T0:.4f} s", f"small-angle {T0:.4f} s"))
mj_a, mj_T = [2, 10, 20, 30, 45, 60], []
for a0 in mj_a:
    xml = (f'<mujoco><option timestep="0.0005" integrator="RK4" gravity="0 0 -{G0}"/><worldbody>'
           f'<body pos="0 0 1"><joint type="hinge" axis="0 1 0"/><inertial pos="0 0 {-dfa}" mass="{fa.m}" diaginertia="{fa.diag[0]} {fa.diag[0]} {fa.diag[0]}"/>'
           f'</body></worldbody></mujoco>')
    mj, mm, dd_ = mj_load(xml)
    dd_.qpos[0] = math.radians(a0)
    tt, ww = [], []
    for _ in range(8000):
        mj.mj_step(mm, dd_)
        tt.append(dd_.time)
        ww.append(dd_.qvel[0])
    sc = sign_changes(np.array(tt), np.array(ww))
    mj_T.append(2 * float(np.mean(np.diff(sc))))
b2.plot(mj_a, mj_T, "o", color=C["x"], ms=6, label="MuJoCo")
b2.set_xlabel(T("释放角 θ₀ / (°)", "release angle θ₀ / (°)"))
b2.set_ylabel(T("周期 T / s", "period T / s"))
b2.set_xlim(0, 62)
b2.grid(True, color="#ececec", lw=0.6)
for sp in ("top", "right"):
    b2.spines[sp].set_visible(False)
b2.legend(loc="upper left", frameon=False, fontsize=10)
b2.set_title(T("(b) 算例 23.2.3：UR5e 小臂绕关节 3 轴摆动", "(b) Example 23.2.3: UR5e forearm swinging about joint 3"), fontsize=11, loc="left")
figure(fig, "fig23_2_2")
