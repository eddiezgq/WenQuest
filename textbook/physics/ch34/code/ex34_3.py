"""34.3 节的计算：

算例 34.3.1  导轨上匀速滑动的导体棒：动生电动势、电流、安培力和功率的平衡；
算例 34.3.2  恒力拉动导体棒：速度趋于末速度 v_t = F R/(B L)²，时间常数 τ = m R/(B L)²（图 34.3.2），
             并用数值积分核对解析解。
"""
import numpy as np

from bookout import T, figure, out, style
import _draw as d

B, L, R = 0.8, 0.5, 0.2          # T, m, Ω
v = 2.0                          # m/s
emf = B * L * v
I = emf / R
F_amp = B * I * L
P_mech = F_amp * v
P_elec = emf * I
assert abs(P_mech - P_elec) < 1e-12

F, m = 2.0, 0.5                  # 恒定拉力 N、导体棒质量 kg
v_t = F * R / (B * L) ** 2
tau = m * R / (B * L) ** 2
tt = np.linspace(0, 4 * tau, 801)
v_an = v_t * (1 - np.exp(-tt / tau))
# 数值积分（半隐式欧拉，第 8 章）核对
vn, dt, vs = 0.0, tt[1] - tt[0], [0.0]
for _ in tt[1:]:
    vn += (F - (B * L) ** 2 * vn / R) / m * dt
    vs.append(vn)
assert np.max(np.abs(np.array(vs) - v_an)) < 5e-3
v_3tau = v_t * (1 - np.exp(-3))

out(B=B, L=L, R=R, v=v, emf=emf, I=I, F_amp=F_amp, P=P_mech, F=F, m=m, v_t=v_t, tau=tau, v_3tau=v_3tau,
    frac_3tau=100 * (1 - np.exp(-3)))

plt = style()
# ---- 图 34.3.1：导轨与导体棒
fig, ax = plt.subplots(figsize=(5.8, 3.0))
ax.plot([0, 4.2], [0, 0], color=d.INK, lw=3); ax.plot([0, 4.2], [2, 2], color=d.INK, lw=3)
ax.plot([0, 0], [0, 2], color=d.INK, lw=3)
ax.add_patch(plt.Rectangle((-0.12, 0.7), 0.24, 0.6, fc="white", ec=d.INK, lw=1.5, zorder=4))
ax.text(-0.35, 1.0, r"$R$", fontsize=12, color=d.INK, ha="center", va="center")
ax.plot([2.6, 2.6], [-0.15, 2.15], color="#8a6508", lw=6, solid_capstyle="round", zorder=4)
for x in (0.5, 1.2, 1.9, 3.7):
    for y in np.arange(0.35, 2.0, 0.6):
        if x > 3 and abs(y - 0.95) < 0.1:
            continue                   # leave room for the v arrow
        d.dot_or_cross(ax, x, y, out=False, r=0.07)
d.arrow(ax, 2.75, 1.0, 0.7, 0, d.INK, r"$\boldsymbol{v}$", off=(0.15, 0))
d.arrow(ax, 2.45, 0.6, -0.6, 0, d.FORCE, r"$\boldsymbol{F}_\mathrm{A}$", off=(-0.25, 0))
d.arrow(ax, 2.38, 1.25, 0, 0.6, d.CURR, r"$I$", off=(-0.18, -0.3))
ax.text(2.6, 2.35, T("导体棒，长 $L$", "rod, length $L$"), ha="center", fontsize=10, color=d.INK)
ax.text(4.2, -0.3, r"$\boldsymbol{B}$" + T("（垂直纸面向里）", " (into the page)"), ha="right", fontsize=10, color=d.FIELD)
ax.set_xlim(-0.7, 4.4); ax.set_ylim(-0.5, 2.6); d.clean(ax)
figure(fig, "fig34_3_1")
# ---- 图 34.3.2：v(t)
fig, ax = plt.subplots(figsize=(5.4, 3.0))
ax.plot(tt, v_an, color=d.INK, lw=2)
ax.axhline(v_t, color=d.MUTED, lw=1, ls="--")
ax.axvline(tau, color=d.MUTED, lw=0.8, ls=":")
ax.text(tau * 1.05, 0.2, r"$\tau$", fontsize=11, color=d.MUTED)
ax.text(tt[-1] * 0.55, v_t * 1.05, r"$v_\mathrm{t} = FR/(BL)^2$", fontsize=11, color=d.INK)
ax.set_xlabel(T("时间 $t$ / s", "time $t$ / s")); ax.set_ylabel(T("速度 $v$ / (m/s)", "speed $v$ / (m/s)"))
ax.set_xlim(0, tt[-1]); ax.set_ylim(0, v_t * 1.15); d.spines(ax)
figure(fig, "fig34_3_2")
