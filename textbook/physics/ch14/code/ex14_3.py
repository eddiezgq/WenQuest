"""14.3 节的计算：

算例 14.3.1  梯子：长 4.0 m、质量 15 kg 的均匀梯子靠在光滑的墙上，与地面成 θ 角；75 kg 的人沿梯子往上爬，离梯脚 s。
            地面要提供多大的静摩擦因数梯子才不滑？θ = 60°、70°、75° 时，人爬到顶端各需要多大的 μ（图 14.3.1）？
算例 14.3.2  夹爪：两指夹爪靠摩擦夹起 2.0 kg 的盒子，指面与盒子之间 μ = 0.40，安全系数取 2。每个手指至少要压多大的力？
            机械臂以 3.0 m/s² 的加速度向上提起时呢？
算例 14.3.3  移动机械臂（算例 11.5.1 的数据）：底盘 120 kg，重心在 x = 0；车轮接地点 x = ±0.40 m；机械臂 25 kg，重心在 x = 0.50 m；
            末端负载 m 在 x = 1.00 m。求前、后轮的支持力随 m 的变化，后轮支持力为零时就要向前倾翻（图 14.3.2）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

L, m, M = 4.0, 15.0, 75.0


def mu_req(th, s):
    P = g * math.cos(th) * (m * L / 2 + M * s) / (L * math.sin(th))   # 对梯脚取矩：墙的支持力 P
    return P / ((m + M) * g)                                            # 地面摩擦 f = P，支持力 N = (m + M) g


for deg in (60, 70, 75):
    th = math.radians(deg)
    out(**{f"mu{deg}": mu_req(th, L), f"mu{deg}_half": mu_req(th, L / 2)})
th70 = math.radians(70)
P70 = mu_req(th70, L) * (m + M) * g
out(P70=P70, N70=(m + M) * g)
# μ = 0.30 时，θ = 70° 能爬多高
s_max = (0.30 * (m + M) * g * L * math.sin(th70) / (g * math.cos(th70)) - m * L / 2) / M
out(s_max=s_max, s_frac=s_max / L)

mb, mu, S, a = 2.0, 0.40, 2.0, 3.0
Ng = S * mb * g / (2 * mu)
Na = S * mb * (g + a) / (2 * mu)
out(mb=mb, mu=mu, S=S, Ng=Ng, Na=Na)

m0, ma, xa, xp, xw = 120.0, 25.0, 0.50, 1.00, 0.40


def wheels(mp):
    W = (m0 + ma + mp) * g
    Nf = (m0 * g * (0 + xw) + ma * g * (xa + xw) + mp * g * (xp + xw)) / (2 * xw)   # 对后轮接地点取矩
    return Nf, W - Nf


mp_max = (m0 * xw - ma * (xa - xw)) / (xp - xw)
assert abs(wheels(mp_max)[1]) < 1e-9
Nf10, Nr10 = wheels(10.0)
out(mp_max=mp_max, Nf0=wheels(0)[0], Nr0=wheels(0)[1], Nf10=Nf10, Nr10=Nr10)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
ss = np.linspace(0, L, 101)
for deg, col in ((60, d.VR), (70, d.VA), (75, d.VB)):
    ax.plot(ss / L, [mu_req(math.radians(deg), s_) for s_ in ss], color=col, lw=2, label=T(f"θ = {deg}°", f"θ = {deg}°"))
ax.axhline(0.30, color=d.MUTED, lw=0.8, ls="--"); ax.text(0.02, 0.31, T("μ = 0.30 的地面", "floor with μ = 0.30"), fontsize=8, color=d.MUTED)
ax.set_xlabel(T("人离梯脚的距离 s / L", "climber position s / L")); ax.set_ylabel(T("需要的静摩擦因数", "static friction needed"))
ax.set_xlim(0, 1); ax.set_ylim(0, 0.6); ax.legend(frameon=False, fontsize=8.5, loc="upper left"); d.spines(ax)
figure(fig, "fig14_3_1")

fig, ax = plt.subplots(figsize=(4.8, 2.9))
mm = np.linspace(0, mp_max, 171)
F = np.array([wheels(x) for x in mm])
ax.plot(mm, F[:, 0], color=d.VR, lw=2, label=T("前轮", "front wheels"))
ax.plot(mm, F[:, 1], color=d.VA, lw=2, label=T("后轮", "rear wheels"))
ax.axhline(0, color=d.MUTED, lw=0.7); ax.axvline(mp_max, color=d.MUTED, lw=0.8, ls=":")
ax.text(mp_max - 2, 1500, T(f"后轮离地：{mp_max:.0f} kg", f"rear wheels lift: {mp_max:.0f} kg"), fontsize=8.5, ha="right")
ax.set_xlabel(T("末端负载 m / kg", "payload m / kg")); ax.set_ylabel(T("支持力 / N", "normal force / N"))
ax.set_xlim(0, 85); ax.set_ylim(0, 2400); ax.legend(frameon=False, fontsize=8.5, loc="center left"); d.spines(ax)
figure(fig, "fig14_3_2")
