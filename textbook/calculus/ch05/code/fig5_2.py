"""图 5.2.1：四类间断点；图 5.2.2：关节库仑摩擦的跳跃间断与光滑化，以及仿真中的抖振。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, axs = plt.subplots(1, 4, figsize=(13, 3.2))
x = np.linspace(-8, 8, 801)
x = x[np.abs(x) > 1e-9]
axs[0].plot(x, np.sin(x) / x, color=BLUE, lw=2)
axs[0].plot([0], [1], "o", mfc="white", mec=BLUE, ms=6, zorder=5)
axs[0].set_title(T("可去间断：sin x / x", "removable: sin x / x"), fontsize=10)
for k in range(-2, 3):
    axs[1].plot([k, k + 1], [k, k], color=BLUE, lw=2)
    axs[1].plot([k], [k], "o", color=BLUE, ms=4)
    axs[1].plot([k + 1], [k], "o", mfc="white", mec=BLUE, ms=4)
axs[1].set_title(T("跳跃间断：⌊x⌋", "jump: ⌊x⌋"), fontsize=10)
for s in (-1, 1):
    xx = s * np.linspace(0.18, 3, 200)
    axs[2].plot(xx, 1 / xx ** 2, color=BLUE, lw=2)
axs[2].set_ylim(0, 30)
axs[2].set_title(T("无穷间断：1/x²", "infinite: 1/x²"), fontsize=10)
xx = 1 / np.linspace(1 / 0.5, 300, 30000)
for s in (-1, 1):
    axs[3].plot(s * xx, np.sin(1 / (s * xx)), color=BLUE, lw=0.7)
axs[3].set_title(T("振荡间断：sin(1/x)", "oscillating: sin(1/x)"), fontsize=10)
for ax in axs:
    clean(ax)
fig.tight_layout()
figure(fig, "fig5_2_1")

J, Fc, b, tau, dt = 0.5, 2.0, 0.1, 1.0, 1e-3


def sim(fric, n=300):
    v, vs = 0.2, []
    for _ in range(n):
        v += dt * (tau - fric(v) - b * v) / J
        vs.append(v)
    return np.array(vs)


fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
v = np.linspace(-0.1, 0.1, 2001)
a1.plot(v[v < 0], -Fc + b * v[v < 0], color=RED, lw=2, label=T("库仑 + 黏性（v = 0 处跳跃）", "Coulomb + viscous (jump at v = 0)"))
a1.plot(v[v > 0], Fc + b * v[v > 0], color=RED, lw=2)
a1.plot(v, Fc * np.tanh(v / 0.01) + b * v, color=GREEN, lw=1.5, ls="--", label=T("tanh 光滑化，$v_s$ = 0.01 rad/s", "tanh smoothing, $v_s$ = 0.01 rad/s"))
a1.set_xlabel(T("关节角速度 v / (rad/s)", "joint speed v / (rad/s)"))
a1.set_ylabel(T("摩擦力矩 / (N·m)", "friction torque / (N·m)"))
a1.legend(fontsize=8.5, frameon=False, loc="upper left")
clean(a1)
t = np.arange(1, 301) * dt * 1000
a2.plot(t, sim(lambda v: Fc * np.sign(v)), color=RED, lw=1.2, label=T("跳跃模型：在 0 附近来回跳", "jump model: chatters around 0"))
a2.plot(t, sim(lambda v: Fc * math.tanh(v / 0.01)), color=GREEN, lw=1.5, ls="--", label=T("光滑模型：停在一个小的蠕动速度", "smooth model: settles at a small creep"))
a2.set_xlabel(T("时间 / ms", "time / ms"))
a2.set_ylabel(T("v / (rad/s)", "v / (rad/s)"))
a2.set_xlim(60, 140)
a2.set_ylim(-0.012, 0.03)
a2.legend(fontsize=8.5, frameon=False)
clean(a2)
fig.tight_layout()
figure(fig, "fig5_2_2")
