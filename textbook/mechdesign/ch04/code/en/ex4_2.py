"""Section 4.2 Size tolerances: IT5-IT11 calculated from the formula for the standard tolerance factor and compared with the standard table (GB/T 1800.1, Table 1);
positions of the tolerance zones of a set of fundamental deviations for Ø40 (shafts f...s, hole H) (Examples 4.2.1, 4.2.2, Figure 4.2.1)."""
import math

import _ch4 as H
from bookout import T, figure, out, style

mdstd = H.mdstd
K = {5: 7, 6: 10, 7: 16, 8: 25, 9: 40, 10: 64, 11: 100}          # IT = K · i (multiples from IT5 on, following the R5 preferred number series)
tab = mdstd.table("iso286_it")


def i_factor(D):
    """Standard tolerance factor i (μm); D is the geometric mean of the size range (mm); valid for ≤ 500 mm"""
    return 0.45 * D ** (1 / 3) + 0.001 * D


rows = []
for r in tab["rows"]:
    lo, hi = r[0], r[1]
    Dm = math.sqrt(max(lo, 1) * hi)                         # The first range 0-3 mm takes the geometric mean of 1-3 mm
    for g in range(5, 12):
        f = K[g] * i_factor(Dm)
        t = r[2 + g - 5]
        rows.append((lo, hi, g, f, t, (t - f) / f))
rows = [x for x in rows if x[0] >= 3]                      # The formula applies above 3 mm (the range ≤ 3 mm has its own rounding rules)
n_cells = len(rows)
max_rel = max(abs(x[5]) for x in rows)
n_within5 = sum(1 for x in rows if abs(x[5]) <= 0.05)
worst = max(rows, key=lambda x: abs(x[5]))

# Example 4.2.1: IT6 for Ø35
D35 = math.sqrt(30 * 50)
i35 = i_factor(D35)
it6_35_f = 10 * i35
it6_35 = mdstd.it(6, 35)
it7_35 = mdstd.it(7, 35)

# Example 4.2.2: several tolerance classes of SH-301
k6 = H.zone(35, "k6")
f9 = H.zone(35, "f9")
r6 = H.zone(40, "r6")
k6_30 = H.zone(30, "k6")

# ---------------------------------------------------------------- Figure
plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.2), gridspec_kw={"width_ratios": [1.0, 1.25]})
# (a) Formula and standard table
sizes = [math.sqrt(max(r[0], 1) * r[1]) for r in tab["rows"]]
cols = {6: "#1f77b4", 7: "#2ca02c", 9: "#ff7f0e", 11: "#9467bd"}
xs = [1 + k * 0.5 for k in range(0, 999)]
for g, c in cols.items():
    a0.plot(xs, [K[g] * i_factor(x) for x in xs], color=c, lw=0.9)
    a0.plot(sizes, [r[2 + g - 5] for r in tab["rows"]], "o", ms=2.6, color=c)
    a0.text(520, K[g] * i_factor(500), f"IT{g}", fontsize=7, color=c, va="center")
a0.set_xscale("log")
a0.set_yscale("log")
a0.set_xlim(1, 800)
a0.set_xlabel(T("公称尺寸 / mm", "Nominal size / mm"), fontsize=8)
a0.set_ylabel(T("标准公差 / μm", "Standard tolerance / μm"), fontsize=8)
a0.tick_params(labelsize=7)
a0.set_title(T("(a) 线：公式 K·i；点：标准表", "(a) Lines: formula K·i; dots: table"), fontsize=8)
a0.grid(True, which="both", lw=0.3, alpha=0.4)
# (b) Positions of the tolerance zones for Ø40
a1.axhline(0, color=H.INK, lw=1.0)
a1.text(9.3, 1.5, T("零线", "zero line"), fontsize=7, ha="right", va="bottom")
letters = ["f", "g", "h", "js", "k", "m", "n", "p", "r", "s"]
for k, L in enumerate(letters):
    lo, hi = H.zone(40, L + "6")
    H.draw_zone(a1, 1.0 + k * 0.82, 0.6, lo, hi, H.C_SHAFT, L + "6")
lo, hi = H.zone(40, "H7")
H.draw_zone(a1, 0.0, 0.7, lo, hi, H.C_HOLE, "H7")
a1.set_xlim(-0.6, 9.4)
a1.set_ylim(-62, 82)
a1.set_xticks([])
a1.set_ylabel(T("偏差 / μm", "Deviation / μm"), fontsize=8)
a1.tick_params(labelsize=7)
a1.set_title(T("(b) Ø40：孔 H7 与轴 f6…s6 的公差带", "(b) Ø40: hole H7 and shafts f6…s6"), fontsize=8)
for s in ("top", "right", "bottom"):
    a1.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig4_2_1")

out(n_cells=n_cells, max_rel=100 * max_rel, n_within5=n_within5, worst_g=worst[2], worst_lo=worst[0], worst_hi=worst[1],
    worst_tab=worst[4], worst_f=worst[3],
    D35=D35, i35=i35, it6_35_f=it6_35_f, it6_35=it6_35, it7_35=it7_35, it7_35_f=16 * i35,
    k6_lo=k6[0], k6_hi=k6[1], f9_lo=f9[0], f9_hi=f9[1], r6_lo=r6[0], r6_hi=r6[1], k630_lo=k6_30[0], k630_hi=k6_30[1],
    it6_40=mdstd.it(6, 40), it11_40=mdstd.it(11, 40),
    k6_max=35 + k6[1] / 1000, k6_min=35 + k6[0] / 1000, r6_max=40 + r6[1] / 1000, r6_min=40 + r6[0] / 1000,
    f9_max=35 + f9[1] / 1000, f9_min=35 + f9[0] / 1000, k630_max=30 + k6_30[1] / 1000, k630_min=30 + k6_30[0] / 1000)
