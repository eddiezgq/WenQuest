"""4.5 节：电感与传输线效应（专题）。

算例 4.5.1  第 1 章 1.4 节的采样时钟经 10 cm 的电路板走线送到电流采样 ADC。走线是特性阻抗 50 Ω 的微带线，
            有效介电常数取 3.3（FR4 板，示意值）。求信号在走线上的传播时间，判断要不要当作传输线；
            输出级的输出电阻（第 1 章反相器链最后一级）与 50 Ω 不匹配时，接收端的波形；串联端接后的波形。
算例 4.5.2  芯片上 3 mm 长、最小线宽的 met5 线：单位长度电感取 0.5 nH/mm（示意值），电感效应要不要考虑。
图 4.5.1    接收端波形：不端接与源端串联端接（反射图法数值计算）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from mos import P, VDD, Wmin, cin, r_ratio, req_n, req_p, wire_c, wire_r, WIRES
import _draw as d

c0 = 3e8
eps = 3.3                     # 示意值
Z0 = 50.0
Lt = 0.10                     # m
v = c0 / math.sqrt(eps)
td = Lt / v
# 第 1 章：驱动 10 pF 的最快反相器链 6 级，每级扇出 f = F^(1/6)，最后一级是第一级的 f^5 倍
r = r_ratio()
R0 = (req_n(Wmin) + req_p(r * Wmin)) / 2
C0 = cin(Wmin, r * Wmin)
F = P["problems"]["p14"]["CL"] / C0
N = 6
size_last = F ** ((N - 1) / N)
Rout = R0 / size_last
tr = 100e-12                  # 输出边沿（示意值，约两个 FO4 延时）
out(v_cm_ns=v * 1e-9 * 100, td_ns=td * 1e9, tr_ps=tr * 1e12, Rout=Rout, size_last=size_last, Rseries=Z0 - Rout,
    crit_ns=2 * td * 1e9)


def receiver(Rs, t_end=6e-9, dt=1e-12):
    """理想斜坡源（0 → VDD，上升时间 tr）经 Rs 驱动长度 td 的无损线，末端开路（接收端输入电容忽略）。"""
    n = int(t_end / dt)
    k = int(round(td / dt))
    gs = (Rs - Z0) / (Rs + Z0)
    t = np.arange(n) * dt
    vs = np.clip(t / tr, 0, 1) * VDD
    a = np.zeros(n)                                   # 源端向右的入射波
    for i in range(n):
        back = a[i - 2 * k] if i >= 2 * k else 0.0    # 末端全反射（ΓL = 1）后回到源端的波
        a[i] = vs[i] * Z0 / (Z0 + Rs) + gs * back
    vr = np.zeros(n)
    vr[k:] = 2 * a[:n - k]                            # 末端电压 = 入射 + 反射 = 2a
    return t, vr


t1, v1 = receiver(Rout)
t2, v2 = receiver(Z0)
out(overshoot_v=v1.max() - VDD, undershoot_v=VDD - v1[int(len(v1) * 0.3):].min(), v2_max=v2.max())

# 算例 4.5.2：芯片上的 met5
Lp = 0.5e-9 / 1e-3            # H/m，示意值
w5 = WIRES["met5"]["wmin"]
Rpm = wire_r("met5", w5) * 1e6                        # Ω/m
Cpm = wire_c("met5", w5) * 1e6                        # F/m
Z5 = math.sqrt(Lp / Cpm)
len5 = 3e-3
tf5 = len5 * math.sqrt(Lp * Cpm)
out(z5=Z5, tf5_ps=tf5 * 1e12, R5=Rpm * len5, twoZ=2 * Z5, R5m=wire_r("met1", 0.14) * 3000)

# 图 4.5.1
plt = style()
fig, ax = plt.subplots(figsize=(5.8, 3.4))
ax.plot(t1 * 1e9, v1, color=d.PMOS, lw=1.6, label=T(f"不端接（输出电阻约 {Rout:.0f} Ω）", f"unterminated (output resistance ≈ {Rout:.0f} Ω)"))
ax.plot(t2 * 1e9, v2, color=d.NMOS, lw=1.8, label=T("源端串联电阻，总电阻 = Z0", "series-terminated, total = Z0"))
ax.axhline(VDD, color=d.MUTED, lw=0.8, ls=":")
ax.set_xlabel(T("时间 / ns", "time / ns")); ax.set_ylabel(T("ADC 时钟输入端电压 / V", "voltage at the ADC clock pin / V"))
ax.set_xlim(0, 6)
ax.legend(fontsize=8.5, frameon=False, loc="lower right")
d.spines(ax)
figure(fig, "fig4_5_1")
