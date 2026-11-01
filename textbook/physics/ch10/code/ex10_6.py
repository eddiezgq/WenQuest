"""10.6 节的计算：

算例 10.6.1  立体仓库的堆垛机：载货台 500 kg + 货物 1000 kg，以 1.0 m/s 升高 12 m，再降回原处（加速、减速各 1.0 s）。
            从直流母线看，减速器、电机、变频器的效率分别为 0.95、0.92、0.97，能量双向传递时都按这个效率打折。
            求上升、下降时母线功率随时间的变化，一个循环从母线取用的能量：下降时制动电阻全部烧掉，与回馈给电网相比（图 10.6.1）。
            每天 300 个循环，各耗电多少度。
算例 10.6.2  只靠母线电容吸收下降的能量：C = 4.7 mF，母线 560 V，允许升到 750 V。电容能吸收多少焦耳，
            按算例 10.6.1 的回馈功率，几毫秒就满了？用制动电阻时，750 V 下要消耗这些功率，电阻最大多少欧（第 30 章 P = U²/R）？
估一估      1500 kg 的电动汽车下山，高度下降 300 m，按 60% 回收能多回收多少度电。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 10.6.1
m, H, vmax, ta = 1500.0, 12.0, 1.0, 1.0
eta = 0.95 * 0.92 * 0.97
T_move = H / vmax + ta                                          # 梯形：匀速 H/v − ta，加速、减速各 ta
dt = 1e-3


def profile(direction):                                        # 速度（向上为正）与加速度
    t = np.arange(0, T_move + dt / 2, dt)
    v = np.where(t < ta, t / ta, np.where(t < T_move - ta, 1.0, (T_move - t) / ta)) * vmax
    a = np.where(t < ta, 1.0, np.where(t < T_move - ta, 0.0, -1.0)) * vmax / ta
    return t, direction * v, direction * a


tu, vu, au = profile(+1)
td, vd, ad = profile(-1)
Pm_u = m * (g + au) * vu                                        # 电机轴（减速器之后）给出的机械功率，正为驱动、负为被拖动
Pm_d = m * (g + ad) * vd
bus = lambda P: np.where(P >= 0, P / eta, P * eta)              # 母线功率：正为取用，负为回馈
Pb_u, Pb_d = bus(Pm_u), bus(Pm_d)
integ = lambda P, t: float(np.sum((P[1:] + P[:-1]) / 2 * np.diff(t)))
E_up = integ(Pb_u, tu)
E_down_back = -integ(np.minimum(Pb_d, 0), td)                   # 下降时回馈的能量
E_down_take = integ(np.maximum(Pb_d, 0), td)                    # 下降中取用的部分：|a| < g，电机始终被负载拖动，所以为零
assert E_down_take == 0.0
dU = m * g * H
assert abs(integ(Pm_u, tu) - dU) < 2.0 and abs(integ(Pm_d, td) + dU) < 2.0
E_cycle_res = E_up + E_down_take                                # 制动电阻：回馈的能量全部烧掉
E_cycle_regen = E_up + E_down_take - E_down_back
n_day = 300
out(m=m, H=H, vmax=vmax, eta=eta, dU_kJ=dU / 1e3, P_up=m * g * vmax / eta / 1e3, P_back=m * g * vmax * eta / 1e3,
    E_up_kJ=E_up / 1e3, E_back_kJ=E_down_back / 1e3, back_frac=E_down_back / E_up,
    E_res_kWh=E_cycle_res * n_day / 3.6e6, E_regen_kWh=E_cycle_regen * n_day / 3.6e6, save=1 - E_cycle_regen / E_cycle_res,
    Pk_up=float(Pb_u.max()) / 1e3, Pk_back=float(-Pb_d.min()) / 1e3)

# ---- 算例 10.6.2
C, U0, Umax = 4.7e-3, 560.0, 750.0
Ecap = 0.5 * C * (Umax ** 2 - U0 ** 2)
P_back = m * g * vmax * eta
P_pk = float(-Pb_d.min())
out(C_mF=C * 1e3, U0=U0, Umax=Umax, Ecap=Ecap, t_fill_ms=Ecap / P_back * 1e3, R_max=Umax ** 2 / P_back, Pk_back_kW=P_pk / 1e3, R_pk=Umax ** 2 / P_pk)

# ---- 估一估：电动汽车下山
mc, hc, rc = 1500.0, 300.0, 0.60
Ec = mc * g * hc
out(mc=mc, hc=hc, Ec_MJ=Ec / 1e6, Ec_kWh=Ec / 3.6e6, Erec_kWh=rc * Ec / 3.6e6)

plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.9))
gap = 3.0
t_all = np.concatenate([tu, tu[-1] + gap + td])
P_all = np.concatenate([Pb_u, Pb_d]) / 1e3
k_ = slice(None, None, 25)                                      # 画图只取每 25 个点中的 1 个
a1.plot(tu[k_], Pb_u[k_] / 1e3, color=d.VR, lw=2); a1.plot((tu[-1] + gap + td)[k_], Pb_d[k_] / 1e3, color=d.VB, lw=2)
a1.fill_between((tu[-1] + gap + td)[k_], Pb_d[k_] / 1e3, color=d.VB, alpha=0.2, lw=0)
a1.fill_between(tu[k_], Pb_u[k_] / 1e3, color=d.VR, alpha=0.15, lw=0)
a1.axhline(0, color=d.MUTED, lw=0.7)
a1.text(2.0, Pb_u.max() / 1e3 + 1.0, T("上升：从母线取用", "lifting: drawn from the bus"), fontsize=8.5, color=d.VR)
a1.text(tu[-1] + gap + 1.0, Pb_d.min() / 1e3 - 2.6, T("下降：回馈到母线", "lowering: fed back to the bus"), fontsize=8.5, color=d.VB)
a1.set_xlabel(T("时间 / s", "time / s")); a1.set_ylabel(T("母线功率 / kW", "bus power / kW")); a1.set_ylim(Pb_d.min() / 1e3 - 5, Pb_u.max() / 1e3 + 4); d.spines(a1)
a1.set_title(T("(a) 一个升降循环", "(a) one lift-and-lower cycle"), fontsize=9.5)
names = [T("制动电阻\n（全部烧掉）", "braking resistor\n(all burnt)"), T("回馈\n（送回电网）", "regeneration\n(back to the grid)")]
vals = [E_cycle_res / 1e3, E_cycle_regen / 1e3]
a2.bar(names, vals, color=[d.MUTED, d.VB], width=0.5)
for i, v_ in enumerate(vals):
    a2.text(i, v_ + 4, f"{v_:.0f} kJ", ha="center", fontsize=9)
a2.set_ylabel(T("每循环耗电 / kJ", "grid energy per cycle / kJ")); a2.set_ylim(0, max(vals) * 1.2); d.spines(a2)
a2.set_title(T("(b) 每个循环的耗电", "(b) energy per cycle"), fontsize=9.5)
fig.tight_layout()
figure(fig, "fig10_6_1")
