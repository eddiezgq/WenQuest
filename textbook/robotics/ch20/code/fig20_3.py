"""20.3 节的示意图。

图 20.3.1：五种步态的步态图（希尔德布兰德画法）：横轴为时间（以周期为单位，画两个周期），每条腿一行，深色为支撑相。
图 20.3.2：Go2 小跑（算例 20.3.1）：(a) 左前足端中心在 {b} 中一个周期的轨迹（侧视），支撑段与摆动段；
          (b) 大腿、小腿关节角随时间的变化。
图 20.3.3：Go2 小跑一个周期的八个瞬间（侧视），对角的两条腿同时着地。
"""
import math

import numpy as np

from _fig20 import C, body_side, draw_leg2, ground, leg_side_points, plane
from _leg import AX, AY, DY, GAITS, GO2_FOOT_R, LEGS, TH_REST, in_stance, leg_fk, leg_ik, swing_profile
from bookout import T, figure, style

plt = style()
h_hip = -leg_fk("FL", TH_REST)[2]
NAME = {"walk": T("爬行（静态，β = 0.75）", "crawl (static walk, β = 0.75)"), "trot": T("小跑（对角，β = 0.5）", "trot (diagonal, β = 0.5)"),
        "pace": T("踱步（同侧，β = 0.5）", "pace (lateral, β = 0.5)"), "bound": T("跳跑（前后，β = 0.4）", "bound (fore–hind, β = 0.4)"),
        "gallop": T("奔跑（β = 0.3）", "gallop (β = 0.3)")}
ORDER = ["RL", "FL", "RR", "FR"]

# ---------------------------------------------------------------- 图 20.3.1
fig, axs = plt.subplots(5, 1, figsize=(9.6, 8.4), sharex=True)
for ax, g in zip(axs, ["walk", "trot", "pace", "bound", "gallop"]):
    ph, beta = GAITS[g]
    for row, leg in enumerate(ORDER):
        y = 3 - row
        for k in range(-1, 3):
            s = ph[leg] + k
            for a, b in ((s, s + beta),):
                a0, b0 = max(a, 0), min(b, 2)
                if b0 > a0:
                    ax.add_patch(plt.Rectangle((a0, y - 0.35), b0 - a0, 0.7, facecolor=C["thigh"], edgecolor="none"))
        ax.text(-0.04, y, leg, ha="right", va="center", fontsize=10)
    ts = np.linspace(0, 2, 2001)
    n = [sum(in_stance(ph[l], t, 1.0, beta)[0] for l in LEGS) for t in ts]
    rng_n = ("%d" % min(n)) if min(n) == max(n) else ("%d～%d" % (min(n), max(n)))
    ax.text(2.03, 1.5, T("着地腿数\n" + rng_n, "feet down\n" + rng_n.replace("～", "–")), fontsize=9.5, va="center")
    ax.set_ylim(-0.6, 3.6)
    ax.set_xlim(0, 2)
    ax.set_yticks([])
    for x in (0.5, 1.0, 1.5):
        ax.axvline(x, color=C["light"], lw=0.8, zorder=0)
    ax.set_title(NAME[g], fontsize=10.5, loc="left")
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
axs[-1].set_xlabel(T("时间 t / t_c（两个周期；深色：支撑相）", "time t / t_c (two cycles; dark: stance)"))
fig.tight_layout()
figure(fig, "fig20_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 20.3.2（与程序 20.3.1 相同的轨迹）
v, tc, beta, hs = 0.8, 0.5, 0.5, 0.08
Ls, ell = v * tc, v * beta * tc
x_td, t_sw = ell / 2, (1 - beta) * tc
ph = GAITS["trot"][0]["FL"]
ts = np.linspace(0, tc, 1001)
X, Z, TH, ST = [], [], [], []
for t in ts:
    st, tau = in_stance(ph, t, tc, beta)
    if st:
        xb, zb = x_td - ell * tau, -h_hip
    else:
        s, hz = swing_profile(tau)
        xb, zb = -x_td + Ls * s - v * t_sw * tau, -h_hip + hs * hz
    X.append(xb)
    Z.append(zb)
    ST.append(st)
    TH.append(leg_ik("FL", np.array([AX + xb, AY + DY, zb])))
X, Z, TH, ST = np.array(X), np.array(Z), np.array(TH), np.array(ST)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.2, 4.6), gridspec_kw={"width_ratios": [1.15, 1.0]})
a1.plot(X[~ST], Z[~ST], color=C["orange"], lw=2, label=T("摆动相", "swing"))
a1.plot(X[ST], Z[ST], color=C["thigh"], lw=4, label=T("支撑相", "stance"))
a1.plot(0, 0, "o", ms=7, mfc="white", mec=C["ink"], mew=1.5)
a1.text(0.008, 0.01, T("大腿关节", "thigh joint"), fontsize=9.5)
a1.annotate("", xy=(-0.05, -h_hip - 0.012), xytext=(0.05, -h_hip - 0.012), arrowprops=dict(arrowstyle="-|>", color=C["thigh"], lw=1.2))
a1.text(0, -h_hip - 0.03, T("支撑：足端相对机身后退 ℓ = 0.20 m", "stance: foot moves back ℓ = 0.20 m"), ha="center", fontsize=9.5, color=C["thigh"])
xo = X.max()
a1.plot([x_td, x_td], [-h_hip - 0.005, -h_hip + 0.05], color=C["muted"], lw=0.7, ls="--")
a1.plot([xo, xo], [-h_hip - 0.005, -h_hip + 0.05], color=C["muted"], lw=0.7, ls="--")
a1.text(x_td + 0.012, -h_hip + 0.06, T("先越过落脚点，再收回", "overshoot, then retract"), fontsize=9.5, color=C["muted"])
a1.plot([-0.2, 0.2], [-h_hip - 0.022, -h_hip - 0.022], color=C["dark"], lw=1)
a1.set_xlabel(T("足端在 {b} 中相对大腿关节的 x / m", "foot x relative to the thigh joint in {b} / m"))
a1.set_ylabel("z / m")
a1.set_aspect("equal")
a1.set_xlim(-0.2, 0.2)
a1.set_ylim(-0.31, 0.04)
a1.grid(alpha=0.25)
a1.legend(loc="center left", fontsize=9.5, frameon=False)
a1.set_title(T("(a) 左前足端一个周期的轨迹（侧视）", "(a) front-left foot over one cycle (side view)"), fontsize=11)
a2.plot(ts / tc, np.degrees(TH[:, 1]), color=C["thigh"], lw=2, label=T("大腿 θ₂", "thigh θ₂"))
a2.plot(ts / tc, np.degrees(TH[:, 2]), color=C["purple"], lw=2, label=T("小腿 θ₃", "calf θ₃"))
a2.axvspan(0, 0.5, color=C["orange"], alpha=0.08)
a2.text(0.25, 0, T("摆动", "swing"), ha="center", fontsize=10, color=C["orange"])
a2.text(0.75, 0, T("支撑", "stance"), ha="center", fontsize=10, color=C["thigh"])
a2.set_xlabel(T("t / t_c", "t / t_c"))
a2.set_ylabel(T("关节角 / (°)", "joint angle / (°)"))
a2.set_xlim(0, 1)
a2.set_ylim(-140, 100)
a2.grid(alpha=0.25)
a2.legend(loc="center right", fontsize=9.5, frameon=False)
a2.set_title(T("(b) 左前腿的关节角", "(b) joint angles of the front-left leg"), fontsize=11)
fig.tight_layout()
figure(fig, "fig20_3_2")
plt.close(fig)


# ---------------------------------------------------------------- 图 20.3.3：小跑一个周期的八个瞬间
def foot_body(leg, t):
    st, tau = in_stance(GAITS["trot"][0][leg], t, tc, beta)
    if st:
        return np.array([x_td - ell * tau, -h_hip])
    s, hz = swing_profile(tau)
    return np.array([-x_td + Ls * s - v * t_sw * tau, -h_hip + hs * hz])


fig, axs = plt.subplots(2, 4, figsize=(13.0, 4.6))
gz = h_hip + GO2_FOOT_R
for k, ax in enumerate(axs.flat):
    t = tc * k / 8
    xb = v * t
    ground(ax, xb - 0.52, xb + 0.44, y=0)
    body_side(ax, (xb, gz))
    for leg, far in (("RL", True), ("FL", True), ("RR", False), ("FR", False)):
        fb = foot_body(leg, t)
        sx = 1 if leg[0] == "F" else -1
        th = leg_ik(leg, np.array([sx * AX + fb[0], (1 if leg[1] == "L" else -1) * (AY + DY), fb[1]]))
        pts = leg_side_points(leg, th, base=(xb, gz))
        st = in_stance(GAITS["trot"][0][leg], t, tc, beta)[0]
        col = C["thigh"] if leg in ("FL", "RR") else C["orange"]
        draw_leg2(ax, pts, color_t=col, color_c=col, lw=3.2, alpha=0.4 if far else 1.0, joints=False)
    ax.text(xb - 0.48, 0.43, f"t = {k}/8 t_c", fontsize=9.5)
    plane(ax, (xb - 0.52, xb + 0.44), (-0.04, 0.47))
fig.text(0.5, 0.01, T("蓝：左前、右后一组；橙：右前、左后一组；淡色为远侧（左侧）的腿。机身每个周期前进 L_s = 0.40 m",
                     "blue: front-left and rear-right; orange: front-right and rear-left; faint: legs on the far (left) side. The body advances L_s = 0.40 m per cycle"),
         ha="center", fontsize=9.5, color=C["muted"])
fig.tight_layout(rect=(0, 0.04, 1, 1))
figure(fig, "fig20_3_3")
plt.close(fig)
