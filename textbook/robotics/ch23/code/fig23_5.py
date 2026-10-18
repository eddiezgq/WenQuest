"""23.5 节的示意图。

图 23.5.1：UR5e 零位（侧视、俯视）：各连杆的质心（圆点面积正比于质量），整臂（不含基座）的质心 ★，
          法兰上装夹爪与 SH-301 毛坯（算例 23.5.3）后的质心 ☆；关节 1 轴、关节 2 轴。
图 23.5.2：(a) 绕关节 1 轴的转动惯量随 θ₂、θ₃ 的变化（θ₄ = −90°，其余为 0）；
          (b) 关节 1 自由转动时把小臂折起（θ₃ 由 0 到 150°，3 s）：MuJoCo 的 θ̇₁ 与式 (23.5.4) 的预测。
"""
import math

import numpy as np

from _ch23 import (GRIP_BOX, GRIP_C, GRIP_M, UR_M, cyl_inertia, link_poses, mj_load, mjcf_text, parse_links, sh301_blank,
                   steiner, ur_fk, ur_points)
from bookout import COLORS as C, T, figure, style

plt = style()
links = parse_links(mjcf_text())
th0 = np.zeros(6)
Tp = link_poses(links, th0)
cs = [(L, Tp[L.name][:3, :3] @ L.ipos + Tp[L.name][:3, 3]) for L in links]
mv = [(L, c) for L, c in cs[1:]]
m_move = sum(L.m for L, _ in mv)
c_move = sum(L.m * c for L, c in mv) / m_move
m_b, r_b, L_b = sh301_blank()
m_p = GRIP_M + m_b
c_p = (GRIP_M * GRIP_C + m_b * (0.15 - 0.04 + L_b / 2)) / m_p
cp_s = UR_M[:3, :3] @ np.array([0, c_p, 0]) + UR_M[:3, 3]
c_load = (m_move * c_move + m_p * cp_s) / (m_move + m_p)
P = ur_points(th0)

# ---------------------------------------------------------------- 图 23.5.1
fig, (a1, a2) = plt.subplots(2, 1, figsize=(9.6, 7.8), gridspec_kw=dict(height_ratios=[1, 1.15]))
for ax, (i, j), ttl in ((a1, (0, 2), T("(a) 侧视（x–z 平面）", "(a) side view (x–z plane)")), (a2, (0, 1), T("(b) 俯视（x–y 平面）", "(b) top view (x–y plane)"))):
    ax.set_aspect("equal")
    ax.plot(P[:, i], P[:, j], color=C["muted"], lw=6, alpha=0.45, solid_capstyle="round", zorder=2)
    for L, c in cs:
        ax.scatter(c[i], c[j], s=22 * L.m, color="#6baed6", edgecolor=C["z"], zorder=4, alpha=0.9)
    yb = UR_M[:3, 1]
    fl = UR_M[:3, 3]
    g = np.array([fl, fl + 0.10 * yb])
    bl = np.array([fl + 0.11 * yb, fl + (0.11 + L_b) * yb])
    ax.plot(g[:, i], g[:, j], color="#5d6b73", lw=7, solid_capstyle="butt", zorder=3)
    ax.plot(bl[:, i], bl[:, j], color="#8c6d1f", lw=5, solid_capstyle="butt", zorder=3)
    ax.plot(c_move[i], c_move[j], "*", color=C["x"], ms=17, zorder=6, mec="white")
    ax.plot(c_load[i], c_load[j], "*", color="white", mec=C["x"], ms=17, zorder=6)
    ax.set_title(ttl, fontsize=11, loc="left")
    ax.grid(True, color="#ececec", lw=0.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
a1.axvline(0, color=C["z"], lw=1.0, ls="-.")
a1.text(0.012, 0.36, T("关节 1 轴", "joint 1 axis"), fontsize=10, color=C["z"])
a1.plot(0, 0.163, "o", color="white", mec=C["ink"], ms=8, zorder=7)
a1.text(0.015, 0.175, T("关节 2 轴（垂直纸面）", "joint 2 axis (normal to page)"), fontsize=10)
a1.annotate(T(f"整臂质心 ★ x = {c_move[0]:.3f} m", f"arm CoM ★ x = {c_move[0]:.3f} m").replace("-", "−"), xy=(c_move[0], c_move[2]), xytext=(-0.42, 0.33), fontsize=10,
            color=C["x"], arrowprops=dict(arrowstyle="-", color=C["x"], lw=0.8))
a1.annotate(T(f"加负载后 ☆ x = {c_load[0]:.3f} m", f"with payload ☆ x = {c_load[0]:.3f} m").replace("-", "−"), xy=(c_load[0], c_load[2]), xytext=(-0.80, 0.33), fontsize=10,
            color=C["x"], arrowprops=dict(arrowstyle="-", color=C["x"], lw=0.8))
a1.annotate(T("大臂质心（8.4 kg）", "upper-arm CoM (8.4 kg)"), xy=(-0.2125, 0.163), xytext=(-0.33, 0.02), fontsize=10, color=C["z"],
            arrowprops=dict(arrowstyle="-", color=C["z"], lw=0.8))
a1.set_xlim(-0.95, 0.12)
a1.set_ylim(-0.05, 0.42)
a1.set_xlabel("x / m")
a1.set_ylabel("z / m")
a2.plot(0, 0, "o", color=C["z"], ms=7)
a2.text(0.012, 0.02, T("关节 1 轴", "joint 1 axis"), fontsize=10, color=C["z"])
a2.plot([0.05, -0.05], [-0.138, -0.138], color=C["ink"], lw=1.0, ls="-.")
a2.text(0.02, -0.17, T("关节 2 轴", "joint 2 axis"), fontsize=10)
rc = math.hypot(c_move[0], c_move[1])
a2.plot([0, c_move[0]], [0, c_move[1]], color=C["x"], lw=0.8, ls=":")
a2.text(c_move[0] / 2, c_move[1] / 2 + 0.03, f"{rc:.3f} m", fontsize=10, color=C["x"])
a2.text(-0.76, -0.47, T("圆点：各连杆的质心，面积正比于质量；灰、棕：夹爪与毛坯", "dots: link centres of mass (area ∝ mass); grey, brown: gripper and blank"),
        fontsize=10)
a2.set_xlim(-0.95, 0.12)
a2.set_ylim(-0.56, 0.08)
a2.set_xlabel("x / m")
a2.set_ylabel("y / m")
fig.tight_layout()
figure(fig, "fig23_5_1")

# ---------------------------------------------------------------- 图 23.5.2
def izz(theta):
    T_ = link_poses(links, theta)
    s = 0.0
    for L in links[1:]:
        R, p = T_[L.name][:3, :3], T_[L.name][:3, 3]
        c = R @ L.ipos + p
        s += (R @ L.I_link_c @ R.T)[2, 2] + L.m * (c[0] ** 2 + c[1] ** 2)
    return s


fig, (b1, b2) = plt.subplots(1, 2, figsize=(12.4, 4.4))
t3 = np.linspace(-150, 150, 301)
for t2, col in ((0, C["x"]), (-45, C["accent"]), (-90, C["z"])):
    b1.plot(t3, [izz(np.radians([0, t2, a, -90, 0, 0])) for a in t3], color=col, lw=1.8,
            label=T(f"θ₂ = {t2}°", f"θ₂ = {t2}°").replace("-", "−"))
b1.set_xlabel(T("θ₃ / (°)", "θ₃ / (°)"))
b1.set_ylabel(T("绕关节 1 轴的转动惯量 / (kg·m²)", "inertia about joint 1 / (kg·m²)"))
b1.set_xlim(-150, 150)
b1.set_xticks([-150, -100, -50, 0, 50, 100, 150])
b1.set_ylim(0, 4.0)
b1.grid(True, color="#ececec", lw=0.6)
for sp in ("top", "right"):
    b1.spines[sp].set_visible(False)
b1.legend(loc="upper right", frameon=False, fontsize=10)
b1.set_title(T("(a) 姿态与转动惯量（θ₄ = −90°）", "(a) pose and inertia (θ₄ = −90°)"), fontsize=11, loc="left")

xs = mjcf_text(option='<option timestep="0.002"/>')
xs = xs.replace('<joint name="shoulder_pan_joint" class="size3" axis="0 0 1" />',
                '<joint name="shoulder_pan_joint" class="size3" axis="0 0 1" armature="0" limited="false" />')
xs = xs.replace('<general class="size3" name="shoulder_pan" joint="shoulder_pan_joint" />',
                '<general class="size3" name="shoulder_pan" joint="shoulder_pan_joint" gainprm="0" biasprm="0 0 0" />')
mj, mm, dd = mj_load(xs)
qa = np.radians([0, 0, 0, -90, 0, 0])
qb = np.radians([0, 0, 150, -90, 0, 0])
dd.qpos[:] = qa
dd.ctrl[1:] = qa[1:]
dd.qvel[0] = 1.0
tt, w1, q3 = [], [], []
while dd.time < 6.0 - 1e-9:
    u = min(1.0, max(0.0, (dd.time - 1.0) / 3.0))
    sm = u * u * (3 - 2 * u)
    dd.ctrl[1:] = (qa + (qb - qa) * sm)[1:]
    mj.mj_step(mm, dd)
    tt.append(dd.time)
    w1.append(dd.qvel[0])
    q3.append(math.degrees(dd.qpos[2]))
pred = izz(qa) / izz(dd.qpos.copy())
b2.plot(tt, w1, color=C["z"], lw=1.8, label=T(r"MuJoCo：$\dot\theta_1$", r"MuJoCo: $\dot\theta_1$"))
b2.axhline(pred, color=C["x"], lw=1.2, ls="--", label=T(f"式 (23.5.4) 的预测 {pred:.3f}", f"Eq. (23.5.4) {pred:.3f}"))
b2.set_xlabel("t / s")
b2.set_ylabel(T(r"关节 1 的角速度 $\dot\theta_1$ / (rad/s)", r"joint 1 speed $\dot\theta_1$ / (rad/s)"))
b2.set_xlim(0, 6)
b2.set_ylim(0, 4.5)
bb = b2.twinx()
bb.plot(tt, q3, color=C["muted"], lw=1.0, ls=":")
bb.set_ylabel(T("θ₃ / (°)（点线）", "θ₃ / (°) (dotted)"), color=C["muted"])
bb.set_ylim(0, 180)
b2.grid(True, color="#ececec", lw=0.6)
b2.legend(loc="lower right", frameon=False, fontsize=10)
b2.set_title(T("(b) 关节 1 不出力时折起小臂", "(b) folding the forearm with joint 1 free"), fontsize=11, loc="left")
fig.tight_layout()
figure(fig, "fig23_5_2")
