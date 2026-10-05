"""2.4 节：有比逻辑与传输管逻辑。

算例 2.4.1  十六路故障信号的伪 NMOS 或非门：PMOS 负载取最小宽度，下拉 NMOS 取它的 1、2、4 倍时的输出低电平
            （手算与仿真）、有故障时的静态电流与功耗；与静态 CMOS 十六输入或非门比较输入电容。
算例 2.4.2  传感器四选一：NMOS 传输管只能把输出充到 VDD − VT；传输门（NMOS 与 PMOS 并联）能充满。
            传输管输出的“弱 1”接到下一级反相器，反相器里有多大的静态电流。
图 2.4.1    10 fF 负载经 NMOS 传输管与传输门充电的波形（手算模型），标出仿真的终值。
"""
import numpy as np

from bookout import T, figure, out, style
from mos import (Cd, Cg, P, VDD, VTn, VTp, Wmin, cin, idn, idp, idsat_n, idsat_p, kn, kp, le_g, r_ratio, req_p, vout)
import _draw as d

r = r_ratio()
Cinv = cin(Wmin, r * Wmin)
sim = P["gates_sim"]

# ---------------------------------------------------------------- 算例 2.4.1 伪 NMOS
def vol_pseudo(ratio):
    """PMOS 负载（最小宽度，VSG = VDD，饱和）与一个导通的下拉 NMOS（线性区）电流相等时的输出电压。"""
    ip = idsat_p(Wmin)
    lo, hi = 0.0, VDD - VTn
    for _ in range(60):
        mid = (lo + hi) / 2
        if idn(VDD, mid, ratio * Wmin) > ip:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


for k, ratio in enumerate((1, 2, 4)):
    out(**{f"vol{ratio}": vol_pseudo(ratio), f"vol{ratio}_sim": sim["pseudo_nmos"][k]["VOL"]})
I_model, I_sim = idsat_p(Wmin), sim["pseudo_nmos"][2]["I"]
out(I_model_ua=I_model * 1e6, I_sim_ua=I_sim * 1e6, P_fault_mw=I_sim * VDD * 1e3)
ratio = 4
Wn = ratio * Wmin
cin_pseudo = Wn * Cg / Cinv                             # 每个输入只接一个 NMOS
g_nor16 = le_g("nor", 16)
out(cin_pseudo=cin_pseudo, g_nor16=g_nor16, nor16_wp=16 * r * Wmin)
# 十六路或非门输出节点：16 个下拉漏极 + 负载 PMOS；输出接 4 个参考反相器
c_out = (16 * Wn + Wmin) * Cd + 4 * Cinv
t_rise = 0.69 * req_p(Wmin) * c_out
i_fall = idsat_n(Wn) - idsat_p(Wmin)                   # 下拉电流要先抵掉常通的负载电流
t_fall = 0.69 * 0.75 * VDD / i_fall * c_out
out(c_out_ff=c_out * 1e15, t_rise_ps=t_rise * 1e12, t_fall_ps=t_fall * 1e12)

# ---------------------------------------------------------------- 算例 2.4.2 传输管
v_pass_model = VDD - VTn
v_pass_sim = sim["pass"]["nmos"]
out(v_pass_model=v_pass_model, v_pass_sim=v_pass_sim, v_tg_sim=sim["pass"]["tgate"], body_drop=v_pass_model - v_pass_sim)
# “弱 1”接到最小对称反相器：PMOS 的 VSG = VDD − Vin
vin = v_pass_sim
vo = vout(vin, Wmin, r * Wmin)
i_static = idn(vin, vo, Wmin)
out(vsg_weak=VDD - vin, vo_weak=vo, i_static_ua=i_static * 1e6, p_static_uw=i_static * VDD * 1e6)


# 图 2.4.1：手算模型的充电波形
def charge(tg, C=10e-15, t_end=2e-9, n=4000):
    dt, v, ts, vs = t_end / n, 0.0, [], []
    for i in range(n + 1):
        ts.append(i * dt); vs.append(v)
        i_n = idn(VDD - v, VDD - v, Wmin)               # 栅 = VDD，漏 = 输入 VDD，源 = 输出 v
        i_p = idp(VDD, VDD - v, r * Wmin) if tg else 0.0   # PMOS：源 = 输入 VDD，栅 = 0
        v += (i_n + i_p) / C * dt
    return np.array(ts), np.array(vs)


plt = style()
fig, ax = plt.subplots(figsize=(5.6, 3.4))
t1, v1 = charge(False)
t2, v2 = charge(True)
ax.plot(t1 * 1e9, v1, color=d.NMOS, lw=1.8, label=T("NMOS 传输管（手算）", "NMOS pass transistor (model)"))
ax.plot(t2 * 1e9, v2, color=d.MEAN, lw=1.8, label=T("传输门（手算）", "transmission gate (model)"))
ax.axhline(VDD - VTn, color=d.NMOS, lw=0.8, ls=":")
ax.text(1.98, VDD - VTn + 0.03, T("VDD − VT", "VDD − VT"), color=d.NMOS, fontsize=8.5, ha="right")
ax.axhline(v_pass_sim, color=d.PMOS, lw=1.0, ls="--")
ax.text(1.98, v_pass_sim - 0.1, T(f"仿真终值 {v_pass_sim:.2f} V（体效应）", f"SPICE final {v_pass_sim:.2f} V (body effect)"), color=d.PMOS, fontsize=8.5, ha="right")
ax.set_xlim(0, 2); ax.set_ylim(0, 1.95)
ax.set_xlabel(T("时间 / ns", "time / ns")); ax.set_ylabel(T("输出电压 / V", "output voltage / V"))
ax.legend(fontsize=8.5, frameon=False, loc="lower right")
d.spines(ax)
figure(fig, "fig2_4_1")
