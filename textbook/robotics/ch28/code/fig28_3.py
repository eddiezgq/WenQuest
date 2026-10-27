"""28.3 节的示意图。

图 28.3.1：(a) X2 的俯视与侧视：四个旋翼的位置与转向、质心；后面两个旋翼比前面两个低 3 cm，惯量张量因此有惯量积 I_xz；
          (b) “8”字形轨迹（算例 21.4.1）一个周期内四个旋翼的推力，虚线为悬停值；
          (c) 同一周期内所需的力矩：J ω̇ 与陀螺项 ω × Jω 的大小。
图 28.3.2：(a) 平飞速度与配平俯仰角（MuJoCo 的空气阻力），虚线为 30° 的倾角限制；(b) 10 m/s 平飞时的力（侧视）。
"""
import math

import numpy as np

from _ch28 import G, R2quat, fig8, flat, mj_load, mjcf_text, roty, x2_alloc, x2_params
from bookout import COLORS as C, T, figure, style

plt = style()
P = x2_params()
m, J = P["m"], P["J"]
A, _ = x2_alloc(P)
fig, axs = plt.subplots(1, 3, figsize=(13.4, 4.0), gridspec_kw=dict(width_ratios=[1.15, 1.2, 1.2]))
ax = axs[0]
for i, (ri, si) in enumerate(zip(P["r"], P["sig"])):
    x, y = ri[0], ri[1]
    spin = -si                                   # 反扭矩与旋翼的转向相反：gear 的第 6 个分量为负，旋翼从上看逆时针转
    col = C["x"] if spin > 0 else C["z"]
    ax.add_patch(plt.Circle((y, x), P["R_rot"], fill=False, color=col, lw=1.4))
    ax.plot([0, y], [0, x], color=C["ink"], lw=2)
    # 画面横轴是 y_b 且向左为正：从上看逆时针（绕 z_b 正转）在画面上也是逆时针
    th0, th1 = (0.4, 2.2) if spin > 0 else (2.2, 0.4)
    a0 = np.array([y - 0.075 * math.cos(th0), x + 0.075 * math.sin(th0)])
    a1 = np.array([y - 0.075 * math.cos(th1), x + 0.075 * math.sin(th1)])
    ax.annotate("", xy=a1, xytext=a0, arrowprops=dict(arrowstyle="->", color=col, lw=1.3, connectionstyle=f"arc3,rad={-0.6 if spin > 0 else 0.6}"))
    ax.text(y, x - 0.03, f"$f_{i + 1}$", ha="center", va="top", fontsize=10)
ax.plot([0], [0], "o", color=C["accent"], ms=7)
ax.annotate("", xy=(0, 0.28), xytext=(0, 0.05), arrowprops=dict(arrowstyle="->", lw=1.2))
ax.text(0.01, 0.29, T("机头 x_b", "nose x_b"), fontsize=9)
ax.text(0.36, -0.36, T("红：从上看逆时针转　蓝：顺时针转", "red: counter-clockwise from above; blue: clockwise"), fontsize=8)
ax.set_xlim(0.38, -0.38)
ax.set_ylim(-0.78, 0.38)
# 侧视小图：旋翼的高度（以质心为原点，单位 cm）
ins = ax.inset_axes([0.08, 0.02, 0.84, 0.22])
for ri in P["r"]:
    ins.plot([ri[0] * 100 - 13, ri[0] * 100 + 13], [ri[2] * 100, ri[2] * 100], color=C["muted"], lw=2.5)
ins.plot([0], [0], "o", color=C["accent"], ms=5)
ins.set_xlim(-30, 30)
ins.set_ylim(-2, 4)
ins.set_yticks([0, 2.6])
ins.set_yticklabels(["0", "2.6"], fontsize=7)
ins.set_xticks([])
ins.text(-29, 3.0, T("侧视（cm）：后低前高", "side view (cm): rear rotors lower"), fontsize=7.5)
ins.text(29, 3.0, T("机头 →", "nose →"), fontsize=7.5, ha="right")
ax.set_aspect("equal")
ax.set_xlabel(T("y_b / m（向左为正）", "y_b / m (positive to the left)"))
ax.set_ylabel(T("x_b / m", "x_b / m"))
ax.set_title(T("(a) X2 俯视（旋翼半径 0.13 m）", "(a) X2 from above (rotor radius 0.13 m)"), fontsize=11)
ax.grid(alpha=0.25)
# (b)(c)
ts = np.linspace(0, 2 * math.pi / 0.8, 801)
fis, tj, tg = [], [], []
for t in ts:
    Ft = flat(fig8(t), 0.3 * t, 0.3, 0.0, m)
    gy = np.cross(Ft["w"], J @ Ft["w"])
    tau = J @ Ft["dw"] + gy
    fis.append(np.linalg.solve(A, np.r_[Ft["f"], tau]))
    tj.append(np.linalg.norm(J @ Ft["dw"]))
    tg.append(np.linalg.norm(gy))
fis = np.array(fis)
ax = axs[1]
cols = [C["x"], C["z"], C["y"], C["accent"]]
for i in range(4):
    ax.plot(ts, fis[:, i], color=cols[i], lw=1.5, label=f"$f_{i + 1}$")
ax.axhline(P["hover"], color=C["muted"], lw=1, ls="--")
ax.set_xlabel(T("时间 / s", "time / s"))
ax.set_ylabel(T("旋翼推力 / N", "rotor thrust / N"))
ax.set_title(T("(b) “8”字形一周的四个推力", "(b) the four thrusts around the figure eight"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, ncol=4, loc="upper center")
ax.grid(alpha=0.25)
ax = axs[2]
ax.plot(ts, np.array(tj) * 1000, color=C["z"], lw=1.6, label=T(r"$|I_b\dot\omega_b|$", r"$|I_b\dot\omega_b|$"))
ax.plot(ts, np.array(tg) * 1000, color=C["x"], lw=1.6, label=T(r"陀螺项 $|\omega_b\times I_b\omega_b|$", r"gyroscopic $|\omega_b\times I_b\omega_b|$"))
ax.set_xlabel(T("时间 / s", "time / s"))
ax.set_ylabel(T("力矩 / (mN·m)", "torque / (mN·m)"))
ax.set_title(T("(c) 所需力矩的两部分", "(c) the two parts of the required torque"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False)
ax.grid(alpha=0.25)
fig.tight_layout()
figure(fig, "fig28_3_1")

# ---------------------------------------------------------------- 图 28.3.2
import mujoco  # noqa: E402

mm, d = mj_load(mjcf_text("x2"))
W = m * G


def mj_drag(v, R):
    d.qpos[:] = np.r_[0, 0, 5, R2quat(R)]
    d.qvel[:] = np.r_[v, 0, 0, 0]
    mujoco.mj_forward(mm, d)
    return d.qfrc_passive[:3].copy()


def trim(v):
    th = 0.0
    for _ in range(100):
        Fd = mj_drag(np.array([v, 0, 0]), roty(th))
        th = math.atan2(-Fd[0], W - Fd[2])
    Fd = mj_drag(np.array([v, 0, 0]), roty(th))
    return th, math.hypot(-Fd[0], W - Fd[2]), Fd


fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.9))
ax = axs[0]
vs = np.linspace(0, 22, 45)
ths = [math.degrees(trim(v)[0]) for v in vs]
ax.plot(vs, ths, color=C["z"], lw=1.8, label=T("MuJoCo 的空气阻力", "MuJoCo air drag"))
ax.axhline(30, color=C["x"], lw=1.2, ls="--", label=T("倾角限制 30°", "tilt limit 30°"))
ax.axhline(0, color=C["muted"], lw=1.2, ls=":", label=T("不计阻力（21.2 节）", "no drag (Section 21.2)"))
ax.set_xlabel(T("平飞速度 / (m/s)", "level-flight speed / (m/s)"))
ax.set_ylabel(T("配平俯仰角 θ / (°)", "trim pitch θ / (°)"))
ax.set_title(T("(a) 飞得越快，机身越低头", "(a) the faster it flies, the more it pitches down"), fontsize=11)
ax.legend(fontsize=8.5, frameon=False, loc="upper left")
ax.grid(alpha=0.25)
ax = axs[1]
th, f, Fd = trim(10.0)
sc = 0.1
o = np.array([0.0, 0.0])
zb = np.array([math.sin(th), math.cos(th)])
xb = np.array([math.cos(th), -math.sin(th)])
ax.plot([-0.25 * xb[0], 0.25 * xb[0]], [-0.25 * xb[1], 0.25 * xb[1]], color=C["muted"], lw=3, solid_capstyle="round", zorder=1)
for vec, col, lab, off in ((f * zb, C["z"], T(f"推力 {f:.1f} N", f"thrust {f:.1f} N"), (0.03, 0.0)),
                           (np.array([0, -W]), C["ink"], T(f"重力 {W:.1f} N", f"weight {W:.1f} N"), (0.03, -0.1)),
                           (np.array([Fd[0], Fd[2]]), C["x"], T(f"阻力 {-Fd[0]:.2f} N", f"drag {-Fd[0]:.2f} N"), (-0.35, 0.08))):
    ax.annotate("", xy=o + sc * vec, xytext=o, arrowprops=dict(arrowstyle="-|>", color=col, lw=2))
    ax.text(*(o + sc * vec + np.array(off)), lab, color=col, fontsize=9)
ax.annotate("", xy=(0.55, -0.9), xytext=(0.25, -0.9), arrowprops=dict(arrowstyle="->", lw=1.2, color=C["muted"]))
ax.text(0.25, -0.85, T("飞行方向 10 m/s", "flight 10 m/s"), fontsize=8.5, color=C["muted"])
ax.text(-0.6, 1.25, T(f"θ = {math.degrees(th):.1f}°", f"θ = {math.degrees(th):.1f}°"), fontsize=10)
ax.set_xlim(-0.7, 0.7)
ax.set_ylim(-1.45, 1.45)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title(T("(b) 10 m/s 平飞时的力（侧视）", "(b) forces in level flight at 10 m/s (side view)"), fontsize=11)
fig.tight_layout()
figure(fig, "fig28_3_2")
