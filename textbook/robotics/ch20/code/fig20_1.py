"""20.1 节的示意图。

图 20.1.1：Go2 左前腿的结构与零位：(a) 侧视，大腿、小腿与两根俯仰轴；(b) 正视，髋外摆轴与侧向偏距 d。
图 20.1.2：逆运动学的两步：(a) 正视，由足端到髋外摆轴的距离定出 z′ 与 θ1（两个分支）；(b) 侧视，平面两连杆的两组解，
          只有膝向后的一组在限位内（算例 20.1.2）。
图 20.1.3：(a) 侧视平面内足端中心能到达的区域（θ1 = 0，按大腿、小腿关节的限位），与站立、行走时足端所在的位置；
          (b) 足端在大腿关节正下方时，机身高度与小腿关节力矩（每只脚承受四分之一体重）。
"""
import math

import numpy as np

from _fig20 import C, angle_arc, arrow, body_side, dim, draw_leg2, ground, leg_side_points, plane
from _leg import AX, AY, DY, L1, L2, TH_REST, hip, leg_fk, leg_ik_all, limits, to_limits, in_limits
from bookout import T, figure, style

plt = style()
lim = limits("FL")

# ---------------------------------------------------------------- 图 20.1.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 5.4), gridspec_kw={"width_ratios": [1.25, 1.0]})
# (a) 侧视：站立姿态
th = TH_REST
pts = leg_side_points("FL", th, base=(0, 0))
body_side(a1, (0, 0))
h, k, f = pts
for p in (h,):
    a1.plot(*p, "x", ms=5.5, mew=1.4, color=C["ink"], zorder=7)      # ⊗：轴 y_b 指向纸内
draw_leg2(a1, pts)
dim(a1, h, k, "$l_1$", -0.03, fs=12, toff=(-0.012, 0.0))
dim(a1, k, f, "$l_2$", -0.03, fs=12, toff=(0.0, 0.0))
a1.plot([h[0], h[0]], [h[1], h[1] - 0.19], color=C["muted"], lw=0.7, ls="--", zorder=2)
angle_arc(a1, h, 0.075, -math.pi / 2, -math.pi / 2 - th[1], C["accent"], r"$\theta_2$", tr=1.45)
kd = k - h
a1.plot([k[0], k[0] + 0.07 * kd[0] / 0.213], [k[1], k[1] + 0.07 * kd[1] / 0.213], color=C["muted"], lw=0.7, ls="--", zorder=2)
ang_t = math.atan2(kd[1], kd[0])
angle_arc(a1, k, 0.055, ang_t, ang_t - th[2] * -1 * -1, C["purple"], r"$\theta_3$", tr=1.6)
a1.text(h[0] + 0.015, h[1] + 0.02, T("大腿关节（轴 y，指向纸内）", "thigh joint (axis y, into the page)"), fontsize=9.5)
a1.text(k[0] - 0.13, k[1] - 0.005, T("小腿关节", "calf joint"), fontsize=9.5)
a1.text(f[0] + 0.03, f[1] - 0.012, T("足端中心", "foot centre"), fontsize=9.5)
# 机身坐标系 {b}
o = np.array([0.0, 0.0])
arrow(a1, o, o + [0.08, 0], C["x"], 1.4)
arrow(a1, o, o + [0, 0.08], C["z"], 1.4)
a1.text(0.085, -0.012, "$x_b$", color=C["x"], fontsize=11)
a1.text(-0.025, 0.088, "$z_b$", color=C["z"], fontsize=11)
a1.plot(0, 0, "o", ms=3.5, color=C["ink"], zorder=7)
a1.text(-0.05, -0.04, "{b}", fontsize=11)
ground(a1, -0.32, 0.36, y=-0.2648 - 0.022)
dim(a1, (0.30, 0.0), (0.30, -0.2648), "$h$", 0.0, fs=11, toff=(0.02, 0))
a1.plot([AX, 0.31], [0, 0], color=C["muted"], lw=0.5, ls=":")
a1.plot([f[0], 0.31], [f[1], f[1]], color=C["muted"], lw=0.5, ls=":")
a1.set_title(T("(a) 侧视（从右侧看，x 向前，y 指向纸内）", "(a) side view (from the right; x forward, y into the page)"), fontsize=11)
plane(a1, (-0.32, 0.40), (-0.33, 0.13))
# (b) 正视：从前方看，y 向左画在图的右侧（x 指向读者）
yo = 0.0
c1 = np.array([AY, 0.0])           # 髋外摆轴（x 方向）穿过这一点
c2 = np.array([AY + DY, 0.0])      # 大腿关节
fpt = np.array([AY + DY, -0.2648])
a2.add_patch(plt.Rectangle((-0.12, -0.05), 0.24, 0.10, facecolor=C["body"], edgecolor=C["dark"], lw=1.0, zorder=2))
a2.plot([c1[0], c2[0]], [c1[1], c2[1]], color=C["dark"], lw=6, solid_capstyle="round", zorder=4)
a2.plot([c2[0], fpt[0]], [c2[1], fpt[1]], color=C["thigh"], lw=5, solid_capstyle="round", zorder=4)
import matplotlib.patches as mp
a2.add_patch(mp.Circle(fpt, 0.022, facecolor="#3a3a3a", zorder=5))
a2.add_patch(mp.Circle(c1, 0.013, facecolor="white", edgecolor=C["red"], lw=1.6, zorder=6))
a2.plot(*c1, "o", ms=2.5, color=C["red"], zorder=7)
a2.text(c1[0] - 0.02, c1[1] + 0.07, T("髋外摆轴（沿 x）", "abduction axis (along x)"), fontsize=9.5, color=C["red"], ha="center")
a2.plot([c1[0], c1[0]], [c1[1] + 0.015, c1[1] + 0.06], color=C["red"], lw=0.6)
dim(a2, c1, c2, "$d$", 0.04, fs=12)
dim(a2, (0, -0.10), (AY, -0.10), "$a_y$", 0.0, fs=11, toff=(0, -0.018))
a2.plot([0, 0], [0.06, -0.33], color=C["muted"], lw=0.6, ls="-.")
a2.text(0.005, -0.33, T("机身对称面", "body mid-plane"), fontsize=9, color=C["muted"])
arrow(a2, (-0.09, 0.0), (-0.01, 0.0), C["y"], 1.4)
a2.text(-0.03, 0.012, "$y_b$", color=C["y"], fontsize=11)
angle_arc(a2, c1, 0.032, -math.pi / 2 - 0.6, -math.pi / 2 + 0.9, C["accent"], r"$\theta_1$", tr=1.9)
a2.text(fpt[0] + 0.03, fpt[1], T("足端中心", "foot centre"), fontsize=9.5)
ground(a2, -0.14, 0.30, y=-0.2648 - 0.022)
a2.set_title(T("(b) 正视（从前方看，左腿在右侧）", "(b) front view (from ahead; left leg on the right)"), fontsize=11)
plane(a2, (-0.15, 0.32), (-0.35, 0.13))
fig.tight_layout()
figure(fig, "fig20_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 20.1.2
p_d = np.array([0.28, 0.17, -0.22])
r = p_d - hip("FL")
rho = math.hypot(r[1], r[2])
zp = -math.sqrt(rho ** 2 - DY ** 2)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 5.0))
# (a) 正视：髋外摆轴在原点（y–z 平面中的点），足端在 (r_y, r_z)
O = np.array([0.0, 0.0])
P = np.array([r[1], r[2]])
a1.plot(*O, "o", ms=6, mfc="white", mec=C["red"], mew=1.8, zorder=6)
a1.plot(*P, "o", ms=9, color="#3a3a3a", zorder=6)
a1.text(P[0] + 0.012, P[1] - 0.01, "$(r_y, r_z)$", fontsize=11)
circ = np.linspace(-2.6, -0.2, 200)
a1.plot(rho * np.cos(circ), rho * np.sin(circ), color=C["light"], lw=0.8, zorder=1)
for zs, col in ((-1, C["blue"]), (1, C["orange"])):
    z_ = zs * math.sqrt(rho ** 2 - DY ** 2)
    t1 = math.atan2(r[2], r[1]) - math.atan2(z_, DY)
    R = np.array([[math.cos(t1), -math.sin(t1)], [math.sin(t1), math.cos(t1)]])
    A = R @ np.array([DY, 0.0])           # 大腿关节
    B = R @ np.array([DY, z_])            # 足端
    a1.plot([0, A[0]], [0, A[1]], color=col, lw=4, solid_capstyle="round", zorder=4, alpha=1 if zs < 0 else 0.6)
    a1.plot([A[0], B[0]], [A[1], B[1]], color=col, lw=2.5, ls="-" if zs < 0 else "--", zorder=4, alpha=1 if zs < 0 else 0.7)
    M = (A + B) / 2
    if zs < 0:
        a1.text(M[0] + 0.045, M[1] - 0.06, T("足在下（z′ < 0）", "foot below (z′ < 0)"), color=col, fontsize=9.5, ha="left")
        dim(a1, A, B, "$|z'|$", 0.03, color=col, fs=11, toff=(0.025, 0))
        a1.plot([0, 0.15], [0, 0], color=C["muted"], lw=0.6, ls="--")
        angle_arc(a1, O, 0.12, 0.0, t1, C["accent"], r"$\theta_1$", tr=1.25)
        a1.text(A[0] - 0.01, A[1] + 0.03, "$d$", color=col, fontsize=11)
    else:
        a1.text(M[0] - 0.03, M[1], T("足在上（z′ > 0）", "foot above (z′ > 0)"), color=col, fontsize=9.5, ha="right")
a1.plot([0, P[0]], [0, P[1]], color=C["muted"], lw=0.8, ls=":")
a1.text(P[0] * 0.45 - 0.035, P[1] * 0.45, r"$\rho$", color=C["muted"], fontsize=12)
a1.text(-0.025, 0.03, T("髋外摆轴", "abduction axis"), fontsize=9.5, color=C["red"], ha="center")
a1.text(-0.30, -0.33, r"$\rho^2 = r_y^2 + r_z^2 = d^2 + z'^2$", fontsize=11)
a1.set_title(T("(a) 正视：先定 z′ 与 θ₁", "(a) front view: z′ and θ₁ first"), fontsize=11)
plane(a1, (-0.32, 0.30), (-0.35, 0.10))
# (b) 侧视平面：大腿关节在原点，足端在 (x′, z′)
F = np.array([r[0], zp])
D = math.hypot(*F)
sols = [s for s, zs, ks in leg_ik_all("FL", p_d) if zs < 0]
for s in sols:
    t2, t3 = s[1], s[2]
    K = L1 * np.array([-math.sin(t2), -math.cos(t2)])
    ok = in_limits("FL", to_limits("FL", s))
    col = C["blue"] if ok else C["orange"]
    a2.plot([0, K[0]], [0, K[1]], color=col, lw=5 if ok else 3, solid_capstyle="round", alpha=1 if ok else 0.6, zorder=4)
    a2.plot([K[0], F[0]], [K[1], F[1]], color=col, lw=4 if ok else 2.5, ls="-" if ok else "--", alpha=1 if ok else 0.7, zorder=4)
    a2.add_patch(mp.Circle(K, 0.009, facecolor="white", edgecolor=col, lw=1.4, zorder=6))
    a3 = abs(math.degrees(t3))
    txt = (T("膝向后：θ₃ = −%.1f°\n在限位内" % a3, "knee back: θ₃ = −%.1f°\nwithin limits" % a3) if ok
           else T("膝向前：θ₃ = +%.1f°\n超出限位" % a3, "knee forward: θ₃ = +%.1f°\nout of range" % a3))
    a2.text(K[0] + (-0.02 if ok else 0.02), K[1] + 0.012, txt, color=col, fontsize=9.5, ha="right" if ok else "left")
a2.plot(0, 0, "o", ms=6, mfc="white", mec=C["ink"], mew=1.5, zorder=7)
a2.add_patch(mp.Circle(F, 0.022, facecolor="#3a3a3a", zorder=7))
a2.text(F[0] + 0.03, F[1] - 0.01, "$(x', z')$", fontsize=11)
a2.plot([0, F[0]], [0, F[1]], color=C["muted"], lw=0.8, ls=":")
a2.text(F[0] * 0.55 + 0.012, F[1] * 0.55, "$D$", color=C["muted"], fontsize=11)
arrow(a2, (-0.25, -0.30), (-0.17, -0.30), C["x"], 1.2, 9)
arrow(a2, (-0.25, -0.30), (-0.25, -0.22), C["z"], 1.2, 9)
a2.text(-0.165, -0.31, "$x$", color=C["x"], fontsize=10)
a2.text(-0.26, -0.21, "$z'$", color=C["z"], fontsize=10)
a2.set_title(T("(b) 侧视平面：再解两连杆", "(b) sagittal plane: then the two-link leg"), fontsize=11)
plane(a2, (-0.30, 0.36), (-0.33, 0.08))
fig.tight_layout()
figure(fig, "fig20_1_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 20.1.3
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.8), gridspec_kw={"width_ratios": [1.0, 1.05]})
rng = np.random.default_rng(2)
t2s = rng.uniform(lim[1, 0], lim[1, 1], 60000)
t3s = rng.uniform(lim[2, 0], lim[2, 1], 60000)
X = -L1 * np.sin(t2s) - L2 * np.sin(t2s + t3s)
Z = -L1 * np.cos(t2s) - L2 * np.cos(t2s + t3s)
a1.scatter(X, Z, s=0.4, color=C["blue"], alpha=0.12, lw=0, zorder=1, rasterized=True)
a1.plot(0, 0, "o", ms=6, mfc="white", mec=C["ink"], mew=1.5, zorder=6)
h = 0.2648
a1.plot([-0.33, 0.33], [-h, -h], color=C["dark"], lw=0.8, ls="--", zorder=2)
a1.text(0.31, -h + 0.012, T("站立高度", "standing height"), fontsize=9, ha="right", color=C["dark"])
xr = math.sqrt(0.38917 ** 2 - h ** 2)
a1.plot([-xr, xr], [-h, -h], color=C["accent"], lw=3, zorder=4)
a1.text(0, -h - 0.04, T("这一高度上足端前后可达 ±%.3f m" % xr, "reach ±%.3f m fore and aft at this height" % xr), fontsize=9.5,
        color=C["accent"], ha="center")
a1.plot(0, -h, "o", ms=6, color="#3a3a3a", zorder=6)
for Rr, ls in ((0.38917, "-"), (0.08857, "-")):
    t = np.linspace(0, 2 * math.pi, 300)
    a1.plot(Rr * np.cos(t), Rr * np.sin(t), color=C["red"], lw=0.8, ls=ls, zorder=3, alpha=0.7)
a1.text(0.21, 0.30, "$D_{\\max}$", color=C["red"], fontsize=11)
a1.text(0.03, 0.09, "$D_{\\min}$", color=C["red"], fontsize=11)
a1.text(-0.39, 0.33, T("θ₁ = 0；蓝点：限位内足端中心可到之处", "θ₁ = 0; blue: where the foot centre can go"), fontsize=9.5)
a1.set_xlabel(T("x′ / m（向前）", "x′ / m (forward)"))
a1.set_ylabel(T("z′ / m（向上）", "z′ / m (up)"))
a1.set_aspect("equal")
a1.set_xlim(-0.42, 0.42)
a1.set_ylim(-0.42, 0.38)
a1.grid(alpha=0.25)
a1.set_title(T("(a) 侧视平面内的工作空间", "(a) workspace in the sagittal plane"), fontsize=11)
import json, os
from pathlib import Path
# 小腿关节力矩随机身高度：由程序 20.1.1 的同一公式重算（足端在大腿关节正下方，每只脚 m𝔤/4）
from _leg import G, GO2_FOOT_R, MASS_GO2, TH_REST, leg_fk, leg_ik, leg_jac
F = MASS_GO2 * G / 4
hs = np.arange(0.10, 0.4001, 0.0025)
tq = []
for hh in hs:
    s = leg_ik("FL", np.array([AX, AY + DY, -hh]))
    tq.append(np.nan if s is None else (leg_jac("FL", s).T @ np.array([0, 0, -F]))[2])
tq = np.array(tq)
a2.plot(hs + GO2_FOOT_R, tq, color=C["purple"], lw=2)
a2.axvline(-leg_fk("FL", TH_REST)[2] + GO2_FOOT_R, color=C["dark"], lw=0.8, ls="--")
a2.text(-leg_fk("FL", TH_REST)[2] + GO2_FOOT_R + 0.004, np.nanmin(tq) + 0.15, T("站立", "standing"), fontsize=9.5, color=C["dark"])
a2.axhline(F * L2, color=C["muted"], lw=0.8, ls=":")
a2.text(0.135, F * L2 + 0.08, T("上限 F·l₂（小腿水平）", "bound F·l₂ (calf horizontal)"), fontsize=9.5, color=C["muted"])
a2.set_xlabel(T("机身离地高度 / m", "body height above ground / m"))
a2.set_ylabel(T("小腿关节力矩 τ₃ / (N·m)", "calf-joint torque τ₃ / (N·m)"))
a2.set_ylim(0, F * L2 * 1.15)
a2.grid(alpha=0.25)
a2.set_title(T(r"(b) 站立时小腿关节的力矩（每只脚 $m\mathfrak{g}/4$）", r"(b) calf-joint torque when standing ($m\mathfrak{g}/4$ per foot)"), fontsize=11)
fig.tight_layout()
figure(fig, "fig20_1_3")
plt.close(fig)
