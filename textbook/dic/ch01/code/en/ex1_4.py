"""Calculations of Section 1.4: propagation delay and inverter chains.

Example 1.4.1  The chip sends the sampling clock out through a pin to drive the clock input of the current-sampling ADC on the board
               and the trace, a load of about 10 pF. The first stage is a minimum symmetric inverter: input capacitance, total fan-out F,
               and the delay with a single stage.
Example 1.4.2  Total delay of a tapered chain of N inverters, t(N) = N·0.69·R·C1·(γ + F^(1/N)), for N = 1 to 10; the fastest number
               of stages compared with the rule of thumb ln F / ln 4;
               the optimum fan-out per stage for the self-loading ratio γ = Cd/Cg (f(ln f − 1) = γ).
Example 1.4.3  The timing budget requires an output delay below tmax: the fewest stages that meet it, and the total gate width saved
               compared with the fastest number of stages.
Figure 1.4.1   Total delay against the number of stages (logarithmic scale), marking tmax.
"""
import math

import numpy as np

from bookout import T, figure, out, style
from mos import Cd, Cg, P, Wmin, chain_delay, cin, fopt, kn, kp
import _draw as d

r = kn / kp
CL = P["problems"]["p14"]["CL"]
tmax = P["problems"]["p14"]["tmax"]
C1 = cin(Wmin, r * Wmin)
F = CL / C1
t = {N: chain_delay(N, CL, r) for N in range(1, 11)}
best = min(t, key=t.get)
few = next(N for N in range(1, 11) if t[N] < tmax)
gamma = Cd / Cg
f_opt = fopt(gamma)
out(CL_pf=CL * 1e12, C1_ff=C1 * 1e15, F=F, t1_ns=t[1] * 1e9, Nopt4=math.log(F) / math.log(4),
    best=best, t_best_ps=t[best] * 1e12, f_best=F ** (1 / best), t_m1_ps=t[best - 1] * 1e12, t_p1_ps=t[best + 1] * 1e12,
    gamma=gamma, fopt=f_opt, N_from_fopt=math.log(F) / math.log(f_opt),
    tmax_ns=tmax * 1e9, few=few, t_few_ps=t[few] * 1e12, t4_ps=t[4] * 1e12, f6=F ** (1 / 6))
val = lambda N: f"{t[N] * 1e9:.3g} ns" if t[N] >= 1e-9 else f"{t[N] * 1e12:.0f} ps"  # noqa: E731
out(table=T("；".join(f"{N} 级 {val(N)}" for N in range(1, 11)), "; ".join(f"N = {N}: {val(N)}" for N in range(1, 11))))
width = lambda N: sum((F ** (1 / N)) ** i for i in range(N))  # noqa: E731  sum of the stage widths (first stage = 1)
out(best_m1=best - 1, best_p1=best + 1, few_m1=few - 1, t_fewm1_ps=t[few - 1] * 1e12,
    w_best=width(best), w_few=width(few), w_save_pct=(1 - width(few) / width(best)) * 100)

plt = style()
fig, ax = plt.subplots(figsize=(5.4, 3.6))
Ns = list(range(1, 11))
ax.semilogy(Ns, [t[N] * 1e9 for N in Ns], "o-", color=d.NMOS, lw=1.6, ms=4)
ax.axhline(tmax * 1e9, color=d.LOAD, lw=1.2, ls="--")
ax.text(7.6, tmax * 1e9 * 1.45, T(f"要求 {tmax * 1e9:g} ns", f"limit {tmax * 1e9:g} ns"), color=d.LOAD, fontsize=9)
ax.plot([best], [t[best] * 1e9], "o", color=d.MEAN, ms=8, mfc="none", mew=1.6)
ax.text(best - 0.5, t[best] * 1e9 * 2.2, T(f"最快 {best} 级", f"fastest: {best}"), color=d.MEAN, fontsize=9)
ax.set_xticks(Ns)
ax.set_xlabel(T("级数 N", "number of stages N"))
ax.set_ylabel(T("总延时 / ns", "total delay / ns"))
d.spines(ax)
figure(fig, "fig1_4_1")
