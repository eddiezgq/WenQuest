"""Calculations of Section 1.5: power.

Example 1.5.1  Control chip of the line-following cart: N gates, 0→1 activity factor α (the probability that the output of a gate
               goes from 0 to 1 in a clock cycle), clock f, load C per gate:
               dynamic power P = αCV²fN, and the power after lowering the voltage from 1.8 V to Vlow.
Example 1.5.2  The price of lowering the voltage: FO4 delay against the supply voltage; the lowest usable voltage when FO4 must not
               exceed fo4max.
Figure 1.5.1   Dynamic power and FO4 delay against the supply voltage.
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
# two conventions for the activity factor: counting only 0→1, P = αCV²f; counting transitions in both directions
# (probability α′ = 2α), P = ½α′CV²f
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
