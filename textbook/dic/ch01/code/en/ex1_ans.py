"""Numbers in the answers to selected exercises of Chapter 1 (cited in "Answers and hints to selected exercises" of 01-99.md).

Uses the same model as the example programs of the text (conventions/mos.py); when the parameters change, the answers follow.
"""
import math

from bookout import out
from mos import (Cd, Cg, L, VDD, VTn, VTp, Wmin, chain_delay, cin, delays, dyn_power, fo4_tp, fopt, idn, idsat_n, kn, kp,
                 noise_margins, req_n, req_p, vdd_for_fo4, vm, wn_for_vol)

r = kn / kp

# 1.1.1  saturation currents at VGS = 1.2 V and 1.8 V
i12, i18 = idn(1.2, VDD, Wmin), idn(VDD, VDD, Wmin)
out(a111_i12_ua=i12 * 1e6, a111_i18_ua=i18 * 1e6, a111_ratio=i12 / i18)

# 1.1.2  PMOS sourcing 1 mA with VSD ≤ 0.2 V (VOH ≥ 1.6 V)
I, dv = 1e-3, VDD - 1.6
wp = I * L / (kp * ((VDD - VTp) * dv - dv * dv / 2))
wn = wn_for_vol(I, 0.2)
out(a112_wp=wp, a112_ratio=wp / wn)


def vol(W, Iload):
    lo, hi = 0.0, VDD - VTn
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if idn(VDD, mid, W) > Iload else (mid, hi)
    return (lo + hi) / 2


# 1.1.3  VOL for width wn and a 1.5 mA load
out(a113_vol=vol(wn, 1.5e-3))

# 1.1.5  load current at which VOL and "on-resistance times current" differ by 10 %
ron = 1 / (kn * wn / L * (VDD - VTn))
lo, hi = 1e-6, idsat_n(wn) * 0.999
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if vol(wn, mid) / (ron * mid) < 1.1 else (lo, mid)
out(a115_i_ma=lo * 1e3)

# 1.2.1  size ratio for VM = 0.8 V
x = (0.8 - VTn) / (VDD - VTp - 0.8)
out(a121_ratio=x * x * r)

# 1.2.3  VDD = 1.2 V、Wp/Wn = r
nm = noise_margins(Wmin, r * Wmin, vdd=1.2)
nm18 = noise_margins(Wmin, r * Wmin)
out(a123_vm=vm(Wmin, r * Wmin, vdd=1.2), a123_nml=nm["NML"], a123_nmh=nm["NMH"],
    a123_frac=min(nm["NML"], nm["NMH"]) / 1.2 * 100, a123_frac18=min(nm18["NML"], nm18["NMH"]) / VDD * 100)

# 1.2.5  size ratio for NML = NMH (sweep from 0.5 to 5)
best, gap = 0.5, 9.0
for k in range(0, 451):
    ratio = 0.5 + k * 0.01
    q = noise_margins(Wmin, ratio * Wmin, step=0.002)
    if abs(q["NML"] - q["NMH"]) < gap:
        best, gap = ratio, abs(q["NML"] - q["NMH"])
out(a125_ratio=best)

# 1.3.1  equivalent resistances of the minimum NMOS and the minimum PMOS
out(a131_rn_k=req_n(Wmin) / 1e3, a131_rp_k=req_p(Wmin) / 1e3)

# 1.3.3  r = 3: β = √3 versus β = 3 (drain capacitance neglected, tp ∝ 1 + r + β + r/β)
r3 = 3.0
tp = lambda b: 1 + r3 + b + r3 / b  # noqa: E731
out(a133_slower=(tp(r3) / tp(math.sqrt(r3)) - 1) * 100, a133_area=(1 - math.sqrt(r3) / r3) * 100)

# 1.3.5  Wp/Wn = 1, 500 MHz: duty cycle after one stage (FO4); duty cycle after two stages (second stage FO4 or FO8)
def skew(fo):
    a, b = delays(Wmin, Wmin, fo * cin(Wmin, Wmin))
    return b - a                                       # tPLH − tPHL


T = 1 / 500e6
out(a135_duty1=50 - skew(4) / T * 100, a135_duty2=50 + (skew(4) - skew(4)) / T * 100,
    a135_duty2b=50 + (skew(4) - skew(8)) / T * 100)

# 1.4.2, 1.4.4  inverter chains


def best_n(CL):
    t = {N: chain_delay(N, CL, r) for N in range(1, 11)}
    return min(t, key=t.get), t


C1 = cin(Wmin, r * Wmin)
n2, _ = best_n(2e-12)
n20, _ = best_n(20e-12)
n10, t10 = best_n(10e-12)
even = min((N for N in t10 if N % 2 == 0), key=t10.get)
out(a142_n2=n2, a142_n20=n20, a142_l2=math.log(2e-12 / C1) / math.log(4), a142_l20=math.log(20e-12 / C1) / math.log(4),
    a144_n=even, a144_t_ps=t10[even] * 1e12)

# 1.4.3  γ = 0.67
f67 = fopt(0.67)
out(a143_f=f67, a143_n=math.log(10e-12 / C1) / math.log(f67), a143_gamma=Cd / Cg)

# 1.5.1
P1 = dyn_power(1e6, 0.05, 3e-15, 1.8, 200e6)
P2 = dyn_power(1e6, 0.05, 3e-15, 1.2, 200e6)
out(a151_p1_mw=P1 * 1e3, a151_p2_mw=P2 * 1e3)

# 1.5.4  lowest voltage for FO4 ≤ 80 ps (lab step 0.01 V, rounded up) and the power (conditions of the cart chip)
v80 = vdd_for_fo4(80e-12, r)
v80_lab = math.ceil(v80 * 100 - 1e-9) / 100
out(a154_v=v80_lab, a154_p_mw=dyn_power(1e4, 0.1, 5e-15, v80_lab, 100e6) * 1e3, a154_fo4_ps=fo4_tp(r, v80_lab) * 1e12)
