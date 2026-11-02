"""图 24.5.1：左：单位圆上的 e^{iθ}，实部为 cos θ、虚部为 sin θ；右：差速机器人里程计 60 s（准确轨迹是单位圆），
欧拉法更新航向使 |z| 增大、轨迹外旋；乘单位复数 e^{iωΔt} 保持 |z| = 1。"""
import cmath
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.6))
th = np.linspace(0, 2 * np.pi, 400)
a1.plot(np.cos(th), np.sin(th), color=MUTED, lw=1.2)
t0 = 0.9
a1.plot([0, math.cos(t0)], [0, math.sin(t0)], color=INK, lw=2)
a1.plot([math.cos(t0)], [math.sin(t0)], "o", color=RED, ms=7)
a1.plot([0, math.cos(t0)], [0, 0], color=BLUE, lw=3, label="cos θ = Re e^{iθ}".replace("e^{iθ}", "$e^{i\\theta}$"))
a1.plot([math.cos(t0), math.cos(t0)], [0, math.sin(t0)], color=GREEN, lw=3, label="sin θ = Im e^{iθ}".replace("e^{iθ}", "$e^{i\\theta}$"))
arc = np.linspace(0, t0, 50)
a1.plot(0.25 * np.cos(arc), 0.25 * np.sin(arc), color=ACC, lw=1.5)
a1.text(0.28, 0.1, "θ", fontsize=12, color=ACC)
a1.text(math.cos(t0) + 0.05, math.sin(t0) + 0.05, "$e^{i\\theta}$", fontsize=13, color=RED)
a1.plot([-1], [0], "s", color=INK, ms=5); a1.text(-1.25, 0.1, "$e^{i\\pi}=-1$", fontsize=10)
a1.axhline(0, color=MUTED, lw=0.6); a1.axvline(0, color=MUTED, lw=0.6)
a1.set_aspect("equal"); a1.set_xlim(-1.4, 1.4); a1.set_ylim(-1.3, 1.3)
a1.set_title(T("欧拉公式：e^{iθ} = cos θ + i sin θ", "Euler's formula: e^{iθ} = cos θ + i sin θ").replace("e^{iθ}", "$e^{i\\theta}$"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="lower left")
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
v, w, dt, Tt = 0.5, 0.5, 0.01, 60.0
N = round(Tt / dt)
r = cmath.exp(1j * w * dt)
paths = {}
for kind in ("eu", "rot"):
    z, p, pts = 1 + 0j, 0j, [0j]
    for _ in range(N):
        p += v * dt * z
        z = z + 1j * w * dt * z if kind == "eu" else z * r
        pts.append(p)
    paths[kind] = np.array(pts)
tt = np.linspace(0, Tt, 2000)
ex = v / (1j * w) * (np.exp(1j * w * tt) - 1)
a2.plot(ex.real, ex.imag, color=INK, lw=3, alpha=0.4, label=T("准确轨迹（半径 1 m 的圆）", "exact path (circle, radius 1 m)"))
a2.plot(paths["eu"].real, paths["eu"].imag, color=RED, lw=1.2, label=T("欧拉法更新航向（|z| 漂移）", "Euler update of heading (|z| drifts)"))
a2.plot(paths["rot"].real, paths["rot"].imag, color=BLUE, lw=1.2, ls="--", label=T("乘以单位复数 e^{iωΔt}", "multiply by e^{iωΔt}").replace("e^{iωΔt}", "$e^{i\\omega\\Delta t}$"))
a2.set_aspect("equal"); a2.set_xlabel("x / m"); a2.set_ylabel("y / m")
a2.set_title(T("差速机器人里程计 60 s（Δt = 10 ms）", "Differential-drive odometry, 60 s (Δt = 10 ms)"), fontsize=10)
a2.legend(fontsize=8.5, frameon=False, loc="lower center", bbox_to_anchor=(0.5, -0.02)); clean(a2, zero=False)
a2.set_ylim(-1.05, 2.2)
fig.tight_layout()
figure(fig, "fig24_5_1")
