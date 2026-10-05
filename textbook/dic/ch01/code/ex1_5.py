"""1.5 节的计算：功耗。

算例 1.5.1  巡线小车控制芯片：N 个门，0→1 翻转率 α（每个时钟一个门输出由 0 变 1 的概率），时钟 f，每门负载 C：
            动态功耗 P = αCV²fN，电压从 1.8 V 降到 Vlow 后的功耗。
算例 1.5.2  降压的代价：FO4 延时随电源电压变化；要求 FO4 不超过 fo4max 时最低能用的电压。
图 1.5.1    动态功耗与 FO4 延时随电源电压的变化。
"""
import numpy as np

from bookout import T, figure, out, style
from mos import P, VDD, dyn_power, fo4_tp, kn, kp, vdd_for_fo4
import _draw as d

q = P["problems"]["p15"]
r = kn / kp
N, alpha, C, f, Vlow, fo4max = q["N"], q["alpha"], q["Cgate"], q["f"], q["Vlow"], q["fo4max"]
P_hi = dyn_power(N, alpha, C, VDD, f)
P_lo = dyn_power(N, alpha, C, Vlow, f)
Vlim = vdd_for_fo4(fo4max, r)
out(N=N, alpha=alpha, C_ff=C * 1e15, f_mhz=f / 1e6, Vlow=Vlow, P_mw=P_hi * 1e3, P_low_mw=P_lo * 1e3,
    save_pct=(1 - P_lo / P_hi) * 100, E_fj=C * VDD ** 2 * 1e15, fo4_hi_ps=fo4_tp(r) * 1e12, fo4_low_ps=fo4_tp(r, Vlow) * 1e12,
    fo4max_ps=fo4max * 1e12, Vlim=Vlim, P_lim_mw=dyn_power(N, alpha, C, Vlim, f) * 1e3)
# 两种“翻转率”的说法：只数 0→1 时 P = αCV²f；数两个方向的翻转（概率 α′ = 2α）时写成 P = ½α′CV²f
assert abs(dyn_power(N, alpha, C, VDD, f) - 0.5 * (2 * alpha) * C * VDD ** 2 * f * N) < 1e-15

plt = style()
fig, ax = plt.subplots(figsize=(5.4, 3.6))
V = np.linspace(1.0, VDD, 161)
ax.plot(V, [dyn_power(N, alpha, C, v, f) * 1e3 for v in V], color=d.NMOS, lw=1.8)
ax.set_xlabel(T("电源电压 VDD / V", "supply voltage VDD / V"))
ax.set_ylabel(T("动态功耗 / mW", "dynamic power / mW"), color=d.NMOS)
ax2 = ax.twinx()
ax2.plot(V, [fo4_tp(r, v) * 1e12 for v in V], color=d.PMOS, lw=1.8)
ax2.axhline(fo4max * 1e12, color=d.LOAD, lw=1.0, ls="--")
ax2.axvline(Vlim, color=d.MUTED, lw=0.8, ls=":")
ax2.set_ylabel(T("FO4 延时 / ps", "FO4 delay / ps"), color=d.PMOS)
ax2.text(Vlim + 0.02, fo4max * 1e12 * 1.6, T(f"{Vlim:.2f} V", f"{Vlim:.2f} V"), color=d.MUTED, fontsize=9)
ax.spines["top"].set_visible(False); ax2.spines["top"].set_visible(False)
figure(fig, "fig1_5_1")
