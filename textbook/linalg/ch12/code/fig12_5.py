"""图 12.5.1：柔性关节的两个振型。(a) 示意：电机（转动惯量 J_m = 2 kg·m²）经扭转刚度 k 的减速器带动连杆（J_l = 1 kg·m²），
位置控制器相当于把电机拉向目标的弹簧 k_p；(b) 振型 v₁ = (1, 2)（19.5 Hz，电机与连杆同向）与 v₂ = (1, −1)（39.0 Hz，反向）；
(c) 电机侧初始偏转 1 mrad 后的自由振动：q = ⅓ v₁ cos ω₁t + ⅔ v₂ cos ω₂t。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

Jm, Jl, k, kp = 2.0, 1.0, 3.0e4, 6.0e4
w1, w2 = np.sqrt(15000.0), np.sqrt(60000.0)
v1, v2 = np.array([1.0, 2.0]), np.array([1.0, -1.0])
fig = plt.figure(figsize=(11.0, 3.9))
gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 0.8, 1.5])
a0, a1, a2 = fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2])
# (a) 示意：两个转盘、弹簧
a0.set_xlim(0, 10); a0.set_ylim(0, 6); a0.axis("off"); a0.set_aspect("equal")
a0.add_patch(plt.Rectangle((0.2, 1.5), 0.4, 3, color=MUTED))
def spring(x0, x1, y, n=6):
    xs = np.linspace(x0, x1, 2 * n + 1)
    ys = y + 0.35 * np.array([0] + [(-1) ** i for i in range(2 * n - 1)] + [0])
    a0.plot(xs, ys, color=INK, lw=1.4)
spring(0.6, 2.8, 3.0)
a0.add_patch(plt.Circle((3.8, 3.0), 1.0, fc=BLUE, alpha=0.35, ec=BLUE, lw=2))
spring(4.8, 7.0, 3.0)
a0.add_patch(plt.Circle((8.0, 3.0), 0.8, fc=ACC, alpha=0.35, ec=ACC, lw=2))
a0.text(1.7, 3.7, "$k_p$", ha="center", fontsize=11); a0.text(5.9, 3.7, "$k$", ha="center", fontsize=11)
a0.text(3.8, 1.4, T("电机 $J_m$", "motor $J_m$"), ha="center", fontsize=9)
a0.text(8.0, 1.6, T("连杆 $J_l$", "link $J_l$"), ha="center", fontsize=9)
a0.text(3.8, 4.4, "$q_1$", ha="center", fontsize=10); a0.text(8.0, 4.2, "$q_2$", ha="center", fontsize=10)
a0.set_title(T("(a) 柔性关节模型", "(a) Flexible joint model"), fontsize=11)
# (b) 振型
x = np.array([0, 1])
a1.bar(x - 0.18, v1, 0.34, color=GREEN, label=T("v₁：19.5 Hz", "v₁: 19.5 Hz"))
a1.bar(x + 0.18, v2, 0.34, color=RED, label=T("v₂：39.0 Hz", "v₂: 39.0 Hz"))
a1.axhline(0, color=MUTED, lw=0.6)
a1.set_xticks(x); a1.set_xticklabels([T("电机 q₁", "motor q₁"), T("连杆 q₂", "link q₂")])
a1.set_ylim(-1.4, 2.6); a1.legend(frameon=False, fontsize=9, loc="upper left")
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.set_title(T("(b) 两个振型", "(b) The two modes"), fontsize=11)
# (c) 自由振动
t = np.linspace(0, 0.2, 2001)
q = np.outer(v1 / 3, np.cos(w1 * t)) + np.outer(2 * v2 / 3, np.cos(w2 * t))
a2.plot(t * 1000, q[0], color=BLUE, lw=1.5, label=T("电机 q₁", "motor q₁"))
a2.plot(t * 1000, q[1], color=ACC, lw=1.5, label=T("连杆 q₂", "link q₂"))
a2.axhline(0, color=MUTED, lw=0.6)
a2.set_xlabel(T("时间 / ms", "time / ms")); a2.set_ylabel(T("转角 / mrad", "angle / mrad"))
a2.set_xlim(0, 200); a2.legend(frameon=False, fontsize=9, ncol=2, loc="upper right")
a2.set_ylim(-1.3, 1.6)
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
a2.set_title(T("(c) 电机侧初始偏转 1 mrad 后的自由振动", "(c) Free vibration after a 1 mrad motor offset"), fontsize=11)
fig.tight_layout()
figure(fig, "fig12_5_1")
