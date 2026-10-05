"""Section 4.1 Interchangeability: the Ø12 locating pin and locating bush of the tool changer at the end of a palletizing robot. Required clearance 4-14 μm (repeatability).
The pins are ground; their size distribution follows the grinding-machine model of the digital factory (part-to-part drift from wheel wear + repeatability, sim/errors.py, sim/engine.py);
the bushes are honed, with a distribution set by this book. Compares the yield of full interchangeability (random pairing) and of selective assembly (2-5 groups), and the parts left unmatched (Example 4.1.1, Figure 4.1.1)."""
import numpy as np

import _ch4 as H
from bookout import T, figure, out, style

N = 2000
REQ = (4.0, 14.0)                      # Clearance requirement, μm
rng = np.random.default_rng(41)
# Pin: wheel wear goes from 0 to 0.9 over a dressing cycle of 28 parts, diameter drift 0.0125 mm × wear; repeatability σ = 1.2 μm (the same grinding machine as the bearing seats of SH-301)
wear = np.array(H.wear_sequence(N))
d_pin = 1000 * (H.SLOPE * wear) + rng.normal(0, 1000 * H.SD_D35, N)          # Deviation from nominal, μm
# Bush: honed; stone wear makes the bore smaller part by part by about 6 μm (stones changed every 40 parts), repeatability σ = 1.5 μm (set by this book)
k = np.arange(N) % 40
d_hole = -6.0 * k / 39 + rng.normal(0, 1.5, N)
# Nominal clearance: puts the mean clearance in the middle of the requirement
c0 = (REQ[0] + REQ[1]) / 2 - (d_hole.mean() - d_pin.mean())
d_hole = d_hole + c0                     # Deviation of the hole (relative to the nominal pin diameter)
perm = rng.permutation(N)
clr = d_hole[perm] - d_pin                # Random pairing: the bushes are shuffled and then assembled with the pins one by one (both parts have periodic wear trends, so they cannot be paired directly by serial number)
p_random = float(np.mean((clr >= REQ[0]) & (clr <= REQ[1])))
spread_pin = float(np.percentile(d_pin, 99.865) - np.percentile(d_pin, 0.135))
spread_hole = float(np.percentile(d_hole, 99.865) - np.percentile(d_hole, 0.135))
T_need = REQ[1] - REQ[0]                 # Full interchangeability: the sum of the pin and bush tolerances must not exceed the range of variation of the clearance
it5_12 = H.mdstd.it(5, 12)
MEAS = 0.5                               # Measurement error σ when sorting, μm


def selective(n):
    """Sort pins and bushes by measured size into n groups each (size bands of equal width), and pair parts with the same group number"""
    mp = d_pin + rng.normal(0, MEAS, N)
    mh = d_hole + rng.normal(0, MEAS, N)
    ep = np.linspace(mp.min(), mp.max() + 1e-9, n + 1)
    eh = np.linspace(mh.min(), mh.max() + 1e-9, n + 1)
    gp = np.digitize(mp, ep) - 1
    gh = np.digitize(mh, eh) - 1
    ok = paired = 0
    for g in range(n):
        ip = np.where(gp == g)[0]
        ih = np.where(gh == g)[0]
        m = min(ip.size, ih.size)
        c = d_hole[ih[:m]] - d_pin[ip[:m]]
        ok += int(np.sum((c >= REQ[0]) & (c <= REQ[1])))
        paired += m
    return ok / paired, N - paired, ok / N


sel = {n: selective(n) for n in (2, 3, 4, 5)}

# ---------------------------------------------------------------- Figure
plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 2.9), gridspec_kw={"width_ratios": [1.2, 1.0]})
bins = np.linspace(-15, 35, 101)
a0.hist(d_pin, bins=bins, color="#c0392b", alpha=0.5, density=True, label=T("销（数字工厂磨床）", "pins (factory grinder)"))
a0.hist(d_hole, bins=bins, color="#2c6fbb", alpha=0.5, density=True, label=T("套（珩磨）", "bushes (honed)"))
a0.hist(clr, bins=bins, histtype="step", color=H.INK, lw=0.9, density=True, label=T("随机配对的间隙", "clearance, random pairs"))
a0.axvspan(*REQ, color="#2ca02c", alpha=0.15, label=T("要求的间隙", "required clearance"))
a0.set_xlabel(T("相对销的名义直径 / μm", "Relative to pin nominal / μm"), fontsize=7.5)
a0.set_yticks([])
a0.tick_params(labelsize=6.5)
a0.legend(fontsize=6.2, frameon=False, loc="upper right")
a0.set_title(T("(a) 尺寸分布与间隙", "(a) Size distributions and clearance"), fontsize=8)
ns = [1, 2, 3, 4, 5]
a1.bar(ns, [100 * p_random] + [100 * sel[n][0] for n in (2, 3, 4, 5)], color=["#999"] + ["#2ca02c"] * 4, width=0.6)
for n in (2, 3, 4, 5):
    a1.text(n, 100 * sel[n][0] + 1.5, T(f"剩 {sel[n][1]}", f"{sel[n][1]} left"), ha="center", fontsize=6.4)
a1.text(1, 100 * p_random + 1.5, f"{100 * p_random:.0f}%", ha="center", fontsize=6.4)
a1.set_xticks(ns)
a1.set_xticklabels([T("随机", "random"), "2", "3", "4", "5"], fontsize=6.8)
a1.set_xlabel(T("分组数", "Number of groups"), fontsize=7.5)
a1.set_ylabel(T("配上的对中合格的比例 / %", "Good among matched pairs / %"), fontsize=7.2)
a1.set_ylim(0, 110)
a1.tick_params(labelsize=6.5)
a1.set_title(T("(b) 分组装配", "(b) Selective assembly"), fontsize=8)
fig.tight_layout()
figure(fig, "fig4_1_1")

out(N=N, req_lo=REQ[0], req_hi=REQ[1], p_random=100 * p_random, spread_pin=spread_pin, spread_hole=spread_hole, T_need=T_need,
    it5_12=it5_12, drift_pin=1000 * H.SLOPE * wear.max(), meas=MEAS,
    p2=100 * sel[2][0], p3=100 * sel[3][0], p4=100 * sel[4][0], p5=100 * sel[5][0],
    left2=sel[2][1], left3=sel[3][1], left4=sel[4][1], left5=sel[5][1],
    y2=100 * sel[2][2], y3=100 * sel[3][2], y4=100 * sel[4][2], y5=100 * sel[5][2])
