"""Section 4.8 Dimension chains: axial clearance of the output shaft system of WQR-105. Two 6207 bearings fixed at both ends (each outer ring held by an end cover); the axial clearance is the closing link.
The worst-case, statistical (root-sum-square) and Monte Carlo methods compared; where full interchangeability is impossible, an adjusting shim is used as the compensating link (Examples 4.8.1-4.8.3, Figure 4.8.1).

The shaft dimensions are those of SH-301 version B in Chapter 33 (_shaft.py); the distance W between the two end faces of the housing and the spigot length c of the end covers are set by this book (the housing HSG-001 of the digital factory does not yet have these dimensions)."""
import math

import numpy as np

import _ch4 as H
from bookout import T, figure, out, style

S = H.S
lay = S.LAY_B
B = H.BRG["B"]
B_LO = H.BRG_TOL["B_lo"] / 1000                  # Bearing width deviations 0 / -0.12 (GB/T 307.1)
C_SH = lay[4][0] - lay[2][0]                      # On the shaft: gear locating face (left side of the collar) to the right bearing shoulder, 25 (the functional dimension of Section 3.3)
REQ = (0.20, 0.40)                                # Axial clearance left for deep-groove ball bearings fixed at both ends (common recommended value, see text)
W = 152.0                                         # Distance between the two end faces of the housing (the faces carrying the end covers) (set by this book)


def zone_mm(d, code):
    lo, hi = H.zone(d, code)
    return lo / 1000, hi / 1000


# Component links: (name, nominal, lower deviation, upper deviation, increasing link +1 / decreasing link -1)
def links(c):
    return [
        (T("箱体两端面距离 W", "Housing faces W"), W, *zone_mm(W, "js11"), +1),
        (T("闷盖止口 c₁", "Blind-cap spigot c₁"), c, *zone_mm(c, "js11"), -1),
        (T("透盖止口 c₂", "Through-cap spigot c₂"), c, *zone_mm(c, "js11"), -1),
        (T("左轴承宽 B", "Left bearing B"), B, B_LO, 0.0, -1),
        (T("套筒", "Sleeve"), S.SLEEVE, *zone_mm(S.SLEEVE, "h11"), -1),
        (T("齿轮毂宽", "Gear hub"), S.HUB_GEAR, *zone_mm(S.HUB_GEAR, "h11"), -1),
        (T("轴：定位面到轴肩", "Shaft: face to shoulder"), C_SH, *zone_mm(C_SH, "js11"), -1),
        (T("右轴承宽 B", "Right bearing B"), B, B_LO, 0.0, -1),
    ]


S_NOM = 2 * B + S.SLEEVE + S.HUB_GEAR + C_SH       # Distance between the outer faces of the two bearing outer rings, 132
C_NAIVE = round((W - S_NOM - sum(REQ) / 2) / 2, 3)  # Made up from nominal sizes: nominal clearance 0.3
STEP = 0.05                                          # Smallest step of the shim combinations (combinations of 0.05, 0.1, 0.2 and 0.5 mm)


def worst_case(L):
    nom = sum(k * n for _, n, lo, hi, k in L)
    gmax = nom + sum(hi if k > 0 else -lo for _, n, lo, hi, k in L)
    gmin = nom + sum(lo if k > 0 else -hi for _, n, lo, hi, k in L)
    return nom, gmin, gmax


def rss(L):
    """Statistical method: every link normally distributed, symmetric about the middle of its tolerance zone, σ = T/6"""
    mean = sum(k * (n + (lo + hi) / 2) for _, n, lo, hi, k in L)
    sd = math.sqrt(sum(((hi - lo) / 6) ** 2 for _, n, lo, hi, k in L))
    return mean, sd


def monte_carlo(L, n=200000, seed=48, brg_mean=-0.05, brg_sd=0.015):
    """Monte Carlo: machined dimensions normal (centered in the tolerance zone, σ = T/6); bearing width normal N(-0.05, 0.015): the real distribution from the bearing maker is narrower than the tolerance zone and its center slightly larger than the middle of the zone (-0.06) (set by this book)"""
    rng = np.random.default_rng(seed)
    g = np.zeros(n)
    for name, nom, lo, hi, k in L:
        if hi == 0.0 and lo == B_LO:
            x = nom + rng.normal(brg_mean, brg_sd, n)
        else:
            x = nom + rng.normal((lo + hi) / 2, (hi - lo) / 6, n)
        g += k * x
    return g


# Scheme 1 (full interchangeability): spigot length set from the "mean sizes" of the links (nominal + mean deviation), so that the mean clearance falls in the middle of the requirement
mu_naive = sum(k * (n + (lo + hi) / 2) for _, n, lo, hi, k in links(C_NAIVE))
C1 = round(round((C_NAIVE + (mu_naive - sum(REQ) / 2) / 2) / 0.05) * 0.05, 3)     # Spigot length rounded to 0.05 mm
L1 = links(C1)
nom1, wmin1, wmax1 = worst_case(L1)
T_wc = wmax1 - wmin1
mu1, sd1 = rss(L1)
T_rss = 6 * sd1
p_rss = 0.5 * (math.erf((REQ[1] - mu1) / (sd1 * math.sqrt(2))) - math.erf((REQ[0] - mu1) / (sd1 * math.sqrt(2))))
g1 = monte_carlo(L1)
p_mc = float(np.mean((g1 >= REQ[0]) & (g1 <= REQ[1])))
T_brg = 2 * (-B_LO)                                  # The sum of the tolerances of the two bearing widths already exceeds the required range of clearance
T_req = REQ[1] - REQ[0]

# ---------------------------------------------------------------- Scheme 2: adjusting shims (compensating link)
# Scheme 2 (shim compensation): the spigot is lengthened so that, without shims, the worst-case upper limit of the clearance does not exceed "required upper limit - one step"; shims can only increase the clearance, not reduce it
C2 = round(C1 + math.ceil((wmax1 - (REQ[1] - STEP)) / 2 / 0.05 - 1e-9) * 0.05, 3)
MEAS_SD = 0.01                                       # Measurement error (depth gauge, feeler gauge) σ
TARGET = sum(REQ) / 2
L2 = links(C2)
nom2, wmin2, wmax2 = worst_case(L2)
rng = np.random.default_rng(49)
g0 = monte_carlo(L2, seed=50)                        # "Clearance" without shims (a negative value means it cannot be assembled and needs shims)
meas = g0 + rng.normal(0, MEAS_SD, g0.size)
shim = np.maximum(0, np.round((TARGET - meas) / STEP) * STEP)
g2 = g0 + shim
p_shim = float(np.mean((g2 >= REQ[0]) & (g2 <= REQ[1])))
shim_max = float(shim.max())
shim_wc = TARGET - wmin2                             # Maximum shim thickness needed, by the worst-case method (plus half a step)
shim_wc_min = TARGET - wmax2
# Check of thermal expansion: elongation between the two bearing outer rings when the shaft is ΔT warmer than the housing
ALPHA, DT = 11.5e-6, 20.0
d_thermal = ALPHA * S_NOM * DT
# Full interchangeability without shims: with the bearings removed, only T_req - T_brg is left for the other 6 links (a negative value means it is impossible)
left_for_parts = T_req - T_brg

# ---------------------------------------------------------------- Figure
plt = style()
fig = plt.figure(figsize=(7.6, 4.6))
gs = fig.add_gridspec(2, 2, height_ratios=[0.7, 1.15], hspace=0.45, wspace=0.25)
a0 = fig.add_subplot(gs[0, :])
# (a) Sketch of the dimension chain: top row housing and end covers, bottom row the parts on the shaft
y_top, y_bot = 1.0, 0.0
xs = 0.0
segs_bot = [(T("轴承", "brg"), B), (T("套筒", "sleeve"), S.SLEEVE), (T("齿轮毂", "gear hub"), S.HUB_GEAR), (T("轴", "shaft"), C_SH), (T("轴承", "brg"), B)]
GD = 9.0                                            # The clearance is drawn 9 mm wide in the figure (enlarged)
ks = (W - 2 * C1 - GD) / S_NOM
x = C1
for nm, ln in segs_bot:
    a0.annotate("", xy=(x + ln * ks, y_bot), xytext=(x, y_bot), arrowprops=dict(arrowstyle="<->", lw=0.7, color="#c0392b"))
    a0.text(x + ln * ks / 2, y_bot - 0.18, f"{nm} {ln:g}", ha="center", va="top", fontsize=6.4, color="#c0392b")
    x += ln * ks
a0.annotate("", xy=(W, y_top), xytext=(0, y_top), arrowprops=dict(arrowstyle="<->", lw=0.8, color="#1f77b4"))
a0.text(W / 2, y_top + 0.12, T(f"箱体 W = {W:g}（增环）", f"housing W = {W:g} (increasing)"), ha="center", fontsize=6.8, color="#1f77b4")
for x0, x1, nm in ((0, C1, "c₁"), (W - C1, W, "c₂")):
    a0.annotate("", xy=(x1, 0.5), xytext=(x0, 0.5), arrowprops=dict(arrowstyle="<->", lw=0.7, color="#c0392b"))
    a0.text((x0 + x1) / 2, 0.58, nm, ha="center", fontsize=6.6, color="#c0392b")
a0.annotate("", xy=(W - C1, y_bot), xytext=(x, y_bot), arrowprops=dict(arrowstyle="<->", lw=0.9, color="#2ca02c"))
a0.text(W - C1 - GD / 2, y_bot - 0.18, T("游隙\n（封闭环）", "end play\n(closing link)"), fontsize=6.4, color="#2ca02c", ha="center", va="top")
for xx in (0, W):
    a0.plot([xx, xx], [-0.3, 1.2], color=H.MUTED, lw=0.6)
a0.set_xlim(-5, W + 5)
a0.set_ylim(-0.8, 1.35)
a0.axis("off")
a0.set_title(T("(a) 轴向尺寸链：蓝色增环，红色减环（下排是轴上的零件，示意，游隙放大）",
               "(a) Axial chain: blue increasing, red decreasing links (shaft parts below; schematic, play enlarged)"), fontsize=7.8)
a1 = fig.add_subplot(gs[1, 0])
bins = np.linspace(-0.4, 1.0, 120)
a1.hist(g1, bins=bins, color="#9ecae1", density=True)
for v, ls, lab in ((wmin1, "-", T("极值", "worst case")), (wmax1, "-", None), (mu1 - 3 * sd1, "--", T("方和根 ±3σ", "RSS ±3σ")), (mu1 + 3 * sd1, "--", None)):
    a1.axvline(v, color=H.INK, lw=0.8, ls=ls, label=lab)
a1.axvspan(*REQ, color="#2ca02c", alpha=0.15, label=T("要求 0.2–0.4", "required 0.2–0.4"))
a1.set_xlabel(T("游隙 / mm", "End play / mm"), fontsize=7.5)
a1.set_yticks([])
a1.tick_params(labelsize=6.5)
a1.legend(fontsize=6.2, frameon=False, loc="upper right")
a1.set_title(T(f"(b) 方案一 完全互换：合格 {100 * p_mc:.0f}%", f"(b) Option 1, full interchange: {100 * p_mc:.0f}% OK"), fontsize=7.8)
a2 = fig.add_subplot(gs[1, 1])
a2.hist(g0, bins=bins, color="#fdd0a2", density=True, label=T("不加垫片", "no shims"))
a2.hist(g2, bins=bins, color="#74c476", density=True, label=T("按测量值加垫片", "shimmed to measurement"))
a2.axvspan(*REQ, color="#2ca02c", alpha=0.15)
a2.set_xlabel(T("游隙 / mm", "End play / mm"), fontsize=7.5)
a2.set_yticks([])
a2.tick_params(labelsize=6.5)
a2.legend(fontsize=6.2, frameon=False, loc="upper left")
a2.set_title(T(f"(c) 方案二 调整垫片：合格 {100 * p_shim:.1f}%", f"(c) Option 2, shims: {100 * p_shim:.1f}% OK"), fontsize=7.8)
figure(fig, "fig4_8_1")

rows = [(nm, n, lo, hi, k) for nm, n, lo, hi, k in L1]
out(W=W, S_nom=S_NOM, c_naive=C_NAIVE, mu_naive=mu_naive, c1=C1, c2=C2, B=B, B_lo=B_LO, sleeve=S.SLEEVE, hub=S.HUB_GEAR, C_sh=C_SH, req_lo=REQ[0], req_hi=REQ[1],
    tol_W=zone_mm(W, "js11")[1], tol_c=zone_mm(C1, "js11")[1], tol_sl=-zone_mm(S.SLEEVE, "h11")[0], tol_hub=-zone_mm(S.HUB_GEAR, "h11")[0],
    tol_C=zone_mm(C_SH, "js11")[1],
    nom1=nom1, wmin1=wmin1, wmax1=wmax1, T_wc=T_wc, mu1=mu1, sd1=sd1, T_rss=T_rss, p_rss=100 * p_rss, p_mc=100 * p_mc,
    mc_mean=float(g1.mean()), mc_sd=float(g1.std()), T_brg=T_brg, T_req=T_req, left_for_parts=left_for_parts,
    nom2=nom2, wmin2=wmin2, wmax2=wmax2, step=STEP, meas_sd=MEAS_SD, p_shim=100 * p_shim, shim_max=shim_max,
    shim_mean=float(shim.mean()), shim_wc=shim_wc, shim_wc_min=shim_wc_min, d_thermal=d_thermal, dT=DT, n_mc=g1.size,
    n_links=len(L1), tol_c2=zone_mm(C2, "js11")[1])
