"""9.4 节的计算：

算例 9.4.1  满载 AGV（M = 800 kg）以 1.0 m/s 匀速爬 3° 的坡，C_rr = 0.015：驱动轮要提供多大的力和功率？平地上呢？
算例 9.4.2  机械臂竖直提起 20 kg 的箱子，提高 1.2 m，用时 1.5 s，速度曲线为梯形（加速、减速各 0.3 s）。
            求各段的提升力、功率随时间的变化、峰值功率与平均功率；用时缩短到 1.0 s 时峰值功率变成多少（图 9.4.1）。
            功率对时间积分，验证总功等于 mgh。
电池        AGV 电池 48 V、100 A·h 储存多少能量；平均消耗 300 W 时能用多久。
马力        1 hp = 550 ft·lbf/s；公制马力 = 75 kgf·m/s。
估一估      60 kg 的人 10 s 登上一层楼（3.0 m）的功率。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 9.4.1
M, v, th, Crr = 800.0, 1.0, math.radians(3.0), 0.015
F_ramp = M * g * (math.sin(th) + Crr * math.cos(th))
F_flat = Crr * M * g
out(M=M, v=v, th_deg=3.0, Crr=Crr, F_grade=M * g * math.sin(th), F_roll=Crr * M * g * math.cos(th), F_ramp=F_ramp,
    P_ramp=F_ramp * v, F_flat=F_flat, P_flat=F_flat * v, ratio_rf=F_ramp / F_flat)


# ---- 算例 9.4.2：梯形速度曲线提升
def lift(m, h, Tm, ta, n=30001):
    vmax = h / (Tm - ta)
    a = vmax / ta
    t = np.linspace(0, Tm, n)
    vv = np.where(t < ta, a * t, np.where(t < Tm - ta, vmax, a * (Tm - t)))
    aa = np.where(t < ta, a, np.where(t < Tm - ta, 0.0, -a))
    F = m * (g + aa)
    P = F * vv
    return t, vv, F, P, vmax, a


mb, hb, T1, ta = 20.0, 1.2, 1.5, 0.3
t, vv, Fl, P, vmax, a = lift(mb, hb, T1, ta)
W = float(np.sum((P[1:] + P[:-1]) / 2 * np.diff(t)))
assert abs(W - mb * g * hb) < 1e-2                            # 功率在加速段末尾有跳变，梯形求和的误差约为步长 × 跳变
Ppk = mb * (g + a) * vmax                                       # 加速段末尾：力最大、速度也最大
assert abs(P.max() - Ppk) < 1e-3 * Ppk                     # 网格点不一定正好落在加速段末尾
t2, vv2, F2, P2, vmax2, a2 = lift(mb, hb, 1.0, 0.2)
out(mb=mb, hb=hb, T1=T1, ta=ta, vmax=vmax, a=a, F_acc=mb * (g + a), F_cru=mb * g, F_dec=mb * (g - a), Ppk=Ppk,
    P_cru=mb * g * vmax, Pavg=W / T1, W=W, mgh=mb * g * hb, pk_avg=Ppk / (W / T1), vmax2=vmax2, a2=a2,
    Ppk2=mb * (g + a2) * vmax2, Pavg2=mb * g * hb / 1.0, P_dec_end=mb * (g - a) * vmax)

# ---- 电池
U, Ah, Pavg_agv = 48.0, 100.0, 300.0
E_kWh = U * Ah / 1000
out(U=U, Ah=Ah, E_kWh=E_kWh, E_MJ=U * Ah * 3600 / 1e6, Pavg_agv=Pavg_agv, hours=E_kWh * 1000 / Pavg_agv)

# ---- 马力
ft, lbf, kgf = 0.3048, 4.4482216152605, 9.80665
out(hp=550 * ft * lbf, hp_metric=75 * kgf)

# ---- 估一估：登楼
mp, hs, ts_ = 60.0, 3.0, 10.0
out(mp=mp, hs=hs, ts=ts_, P_stair=mp * g * hs / ts_)

plt = style()
# ---- 图 9.4.1（画图只取每 20 个点中的 1 个，跳变处仍然陡直）
k_ = slice(None, None, 20)
fig, axs = plt.subplots(3, 1, figsize=(4.8, 4.6), sharex=True)
axs[0].plot(t[k_], vv[k_], color=d.VA, lw=2); axs[0].set_ylabel(T("速度 / (m/s)", "speed / (m/s)")); axs[0].set_ylim(0, 1.25)
axs[1].plot(t[k_], Fl[k_], color=d.VB, lw=2); axs[1].axhline(mb * g, color=d.MUTED, lw=0.8, ls="--")
axs[1].text(1.53, mb * g + 22, "mg", fontsize=9, va="center", color=d.MUTED)
axs[1].set_ylabel(T("提升力 / N", "lifting force / N")); axs[1].set_ylim(0, 300)
axs[2].fill_between(t[k_], P[k_], color=d.VR, alpha=0.15, lw=0)
axs[2].plot(t[k_], P[k_], color=d.VR, lw=2)
axs[2].axhline(W / T1, color=d.MUTED, lw=0.8, ls="--")
axs[2].text(0.62, W / T1 - 34, T(f"平均 {W / T1:.0f} W", f"average {W / T1:.0f} W"), fontsize=8.5, color=d.MUTED)
axs[2].annotate(T(f"峰值 {Ppk:.0f} W", f"peak {Ppk:.0f} W"), xy=(ta, Ppk), xytext=(0.5, Ppk + 15), fontsize=8.5,
                arrowprops=dict(arrowstyle="->", color=d.MUTED, lw=0.8))
axs[2].text(0.45, 55, T(f"面积 = mgh = {W:.0f} J", f"area = mgh = {W:.0f} J"), fontsize=8.5, color=d.VR)
axs[2].set_ylabel(T("功率 / W", "power / W")); axs[2].set_ylim(0, 320); axs[2].set_xlabel(T("时间 t / s", "time t / s"))
for x in (ta, T1 - ta):
    for a_ in axs:
        a_.axvline(x, color=d.MUTED, lw=0.5, ls=":")
for a_ in axs:
    d.spines(a_)
axs[2].set_xlim(0, 1.6)
fig.align_ylabels(axs)
fig.tight_layout()
figure(fig, "fig9_4_1")
