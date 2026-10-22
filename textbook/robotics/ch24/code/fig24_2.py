"""24.2 节的示意图。

图 24.2.1：平面两连杆臂的记号：φ₁、φ₂，a₁，质心 (r_i, s_i)，重力。
图 24.2.2：算例 24.2.2：UR5e 用关节 2、3 把毛坯送向卡盘（T = 1 s，装夹爪 + 毛坯）。
          (a) 手臂在 t = 0、0.25、0.5、0.75、1 s 的平面投影；(b)、(c) 关节 2、3 的力矩与三类分量，点为 MuJoCo 的逆动力学。
"""
import math

import numpy as np

from _ch24 import (mj_load, mjcf_text, parse_links, payload_parts, payload_xml, planar_params, quintic, ur_to_planar,
                   ur_weld_xml)
from bookout import COLORS as C, T, figure, style

plt = style()


def arrow(ax, p, q, color, lw=1.5, ms=11, z=5, style_="-|>"):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle=style_, color=color, lw=lw, mutation_scale=ms, shrinkA=0, shrinkB=0),
                zorder=z)


def bar(ax, p, q, w, fc, ec):
    d = np.asarray(q) - np.asarray(p)
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0]])
    pts = np.array([p + n * w, q + n * w, q - n * w, p - n * w])
    ax.add_patch(plt.Polygon(pts, closed=True, fc=fc, ec=ec, lw=1.0, zorder=3))


# ---------------------------------------------------------------- 图 24.2.1
fig, ax = plt.subplots(figsize=(7.6, 5.6))
ax.set_aspect("equal")
ax.axis("off")
p1, p2 = math.radians(35), math.radians(50)
a1, a2 = 1.6, 1.4
O1 = np.zeros(2)
O2 = a1 * np.array([math.cos(p1), math.sin(p1)])
E = O2 + a2 * np.array([math.cos(p1 + p2), math.sin(p1 + p2)])
bar(ax, O1, O2, 0.11, "#c6dbef", C["z"])
bar(ax, O2, E, 0.09, "#fde0c5", C["accent"])
for P in (O1, O2):
    ax.add_patch(plt.Circle(P, 0.09, fc="white", ec=C["ink"], lw=1.3, zorder=5))
ax.plot([-0.4, 0.4], [-0.2, -0.2], color=C["ink"], lw=2)
for k in range(5):
    ax.plot([-0.35 + 0.17 * k, -0.45 + 0.17 * k], [-0.2, -0.32], color=C["ink"], lw=0.8)
# 角度
ax.plot([0, 1.0], [0, 0], color=C["muted"], lw=0.8, ls="--")
t = np.linspace(0, p1, 30)
ax.plot(0.55 * np.cos(t), 0.55 * np.sin(t), color=C["x"], lw=1.2)
ax.text(0.62, 0.15, r"$\varphi_1$", fontsize=14, color=C["x"])
ext = O2 + 0.9 * np.array([math.cos(p1), math.sin(p1)])
ax.plot([O2[0], ext[0]], [O2[1], ext[1]], color=C["muted"], lw=0.8, ls="--")
t = np.linspace(p1, p1 + p2, 30)
ax.plot(O2[0] + 0.25 * np.cos(t), O2[1] + 0.25 * np.sin(t), color=C["x"], lw=1.2)
ax.text(O2[0] + 0.3, O2[1] + 0.08, r"$\varphi_2$", fontsize=14, color=C["x"])
# a1
nrm = np.array([math.sin(p1), -math.cos(p1)])
arrow(ax, O1 + 0.45 * nrm, O2 + 0.45 * nrm, C["muted"], style_="<|-|>", lw=1.0)
ax.text(*(0.55 * (O1 + O2) + 0.62 * nrm), r"$a_1$", fontsize=13, color=C["ink"])
# 质心
r1, s1 = 0.75, 0.0
c1 = np.array([r1 * math.cos(p1), r1 * math.sin(p1)])
ax.plot(*c1, "o", color=C["x"], ms=7, zorder=6)
ax.text(c1[0] - 0.05, c1[1] + 0.2, r"$c_1$", fontsize=12, color=C["x"])
u2 = np.array([math.cos(p1 + p2), math.sin(p1 + p2)])
n2 = np.array([-u2[1], u2[0]])
r2, s2 = 0.7, 0.18
c2 = O2 + r2 * u2 + s2 * n2
ax.plot(*c2, "o", color=C["x"], ms=7, zorder=6)
ax.text(c2[0] - 0.32, c2[1] - 0.05, r"$c_2$", fontsize=12, color=C["x"])
# 连杆 2 的连杆坐标系
arrow(ax, O2, O2 + 0.45 * u2, C["x"], lw=1.3)
arrow(ax, O2, O2 + 0.4 * n2, C["y"], lw=1.3)
ax.text(*(O2 + 0.42 * u2 + np.array([0.06, -0.08])), "x", fontsize=11, color=C["x"])
ax.text(*(O2 + 0.45 * n2 + np.array([-0.1, 0.02])), "y", fontsize=11, color=C["y"])
foot = O2 + r2 * u2
ax.plot([foot[0], c2[0]], [foot[1], c2[1]], color=C["muted"], lw=0.8, ls=":")
off = -0.3 * n2
arrow(ax, O2 + off, foot + off, C["muted"], style_="<|-|>", lw=1.0)
ax.text(*(O2 + 0.5 * r2 * u2 + off + np.array([0.08, -0.02])), r"$r_2$", fontsize=12, color=C["ink"])
ax.text(*(0.5 * (foot + c2) + 0.12 * u2 + np.array([-0.05, 0.0])), r"$s_2$", fontsize=12, color=C["ink"])
# 重力、坐标
arrow(ax, (2.9, 1.9), (2.9, 1.4), C["ink"])
ax.text(2.97, 1.6, r"$\mathfrak{g}$", fontsize=13)
arrow(ax, (-0.9, 0.0), (-0.4, 0.0), C["ink"], lw=1.0)
arrow(ax, (-0.9, 0.0), (-0.9, 0.5), C["ink"], lw=1.0)
ax.text(-0.42, -0.14, "X", fontsize=11)
ax.text(-1.05, 0.48, "Y", fontsize=11)
ax.text(-0.25, -0.55, T("关节 1", "joint 1"), fontsize=10.5)
ax.text(O2[0] + 0.12, O2[1] - 0.25, T("关节 2", "joint 2"), fontsize=10.5)
ax.text(c1[0] - 0.75, c1[1] + 0.1, T("连杆 1", "link 1"), fontsize=10.5, color=C["z"])
ax.text(E[0] - 0.75, E[1] + 0.12, T("连杆 2", "link 2"), fontsize=10.5, color=C["accent"])
ax.set_xlim(-1.2, 3.3)
ax.set_ylim(-0.7, 3.0)
figure(fig, "fig24_2_1")

# ---------------------------------------------------------------- 图 24.2.2
links = parse_links(mjcf_text())
pl = payload_parts()
P = planar_params(links, payload=pl)
pa, pb = ur_to_planar(*np.radians((-120, 120))), ur_to_planar(*np.radians((-30, 30)))
TT = 1.0
ts = np.linspace(0, TT, 501)
rows = []
for tt in ts:
    q, qd, qdd = quintic(pa, pb, TT, tt)
    rows.append(np.r_[P.M(q) @ qdd, P.c(q, qd), P.g(q)])
R = np.array(rows)
tot = R[:, 0:2] + R[:, 2:4] + R[:, 4:6]
import mujoco                                                           # noqa: E402

mjw, mw, dw = mj_load(ur_weld_xml(tool=payload_xml(*pl)))
tm, tau_mj = [], []
for tt in np.linspace(0, TT, 21):
    q, qd, qdd = quintic(pa, pb, TT, tt)
    dw.qpos[:], dw.qvel[:], dw.qacc[:] = -q, -qd, -qdd
    mujoco.mj_inverse(mw, dw)
    tm.append(tt)
    tau_mj.append(-dw.qfrc_inverse.copy())
tau_mj = np.array(tau_mj)

fig = plt.figure(figsize=(12.6, 4.6))
gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.0, 1.0], wspace=0.3)
ax0, ax1, ax2 = (fig.add_subplot(gs[0, k]) for k in range(3))
ax0.set_aspect("equal")
a2len = P.r2 * 2 * 0 + 0.392 + 0.1 + 0.15 + 0.04 + 0.12      # 画图用：小臂 + 腕 + 夹爪 + 毛坯（示意长度）
for k, tt in enumerate(np.linspace(0, TT, 5)):
    q, _, _ = quintic(pa, pb, TT, tt)
    O2 = P.a1 * np.array([math.cos(q[0]), math.sin(q[0])])
    E = O2 + a2len * np.array([math.cos(q[0] + q[1]), math.sin(q[0] + q[1])])
    al = 0.3 + 0.7 * k / 4
    ax0.plot([0, O2[0]], [0, O2[1]], color=C["z"], lw=5, alpha=al, solid_capstyle="round")
    ax0.plot([O2[0], E[0]], [O2[1], E[1]], color=C["accent"], lw=4, alpha=al, solid_capstyle="round")
    ax0.plot(*O2, "o", color="white", mec=C["ink"], ms=6, alpha=al)
    if k in (0, 4):
        ax0.text(E[0] + 0.03, E[1] - 0.01, f"t = {tt:.0f} s", fontsize=9.5, color=C["ink"])
ax0.plot(0, 0, "o", color="white", mec=C["ink"], ms=7)
ax0.plot([-0.12, 0.12], [-0.06, -0.06], color=C["ink"], lw=2)
ax0.set_xlim(-0.4, 1.4)
ax0.set_ylim(-0.35, 0.75)
ax0.set_xlabel("X / m")
ax0.set_ylabel("Y / m")
ax0.set_title(T("(a) 小臂始终水平，毛坯平着送出", "(a) forearm stays level, blank moves out flat"), fontsize=11, loc="left")
labels = (T("惯性项", "inertial") + r" $M\ddot\varphi$", T("速度项", "velocity") + " $c$", T("重力项", "gravity") + " $g$", T("总力矩", "total"))
cols = (C["z"], C["y"], C["muted"], C["x"])
for ax, j, ttl in ((ax1, 0, T("(b) 关节 2（肩）", "(b) joint 2 (shoulder)")), (ax2, 1, T("(c) 关节 3（肘）", "(c) joint 3 (elbow)"))):
    for k, (lab, col) in enumerate(zip(labels, cols)):
        y = tot[:, j] if k == 3 else R[:, 2 * k + j]
        ax.plot(ts, y, color=col, lw=2.0 if k == 3 else 1.3, ls="-" if k in (0, 3) else ("--" if k == 1 else "-."), label=lab)
    ax.plot(tm, tau_mj[:, j], "o", color=C["x"], ms=4, mfc="white", label=T("MuJoCo 逆动力学", "MuJoCo inverse dynamics"))
    ax.axhline(0, color=C["ink"], lw=0.6)
    ax.set_xlabel(T("时间 t / s", "time t / s"))
    ax.set_ylabel(T("力矩 / (N·m)", "torque / (N·m)"))
    ax.set_title(ttl, fontsize=11, loc="left")
    ax.set_xlim(0, TT)
    for s_ in ("top", "right"):
        ax.spines[s_].set_visible(False)
ax1.legend(frameon=False, fontsize=8.8, loc="upper left")
figure(fig, "fig24_2_2")
