"""Section 5.1 Mechanical properties: tensile curves of several materials (model curves fitted to the GB minimum values or to the
material-library values), and the ratio of fatigue limit to tensile strength (digital-factory material library).
Examples 5.1.1 and 5.1.2, Figure 5.1.1.

Model of the tensile curve: elastic part σ = Eε; after yield the true stress hardens by Swift's law σ = K(ε₀ + εp)ⁿ, with ε₀ chosen
so that the curve is continuous at the yield point. n and K follow from two conditions: the maximum engineering stress equals the
tensile strength Rm, and the engineering strain at the maximum (uniform elongation) is taken as 60% of the elongation after
fracture A (set by this book). After necking the engineering stress falls, and the curve ends at the elongation after fracture
(drawn as a straight line, schematic). For the low-carbon steel Q235 a yield plateau of about 1.5% is added."""
import math

import numpy as np
from scipy.optimize import brentq

import _ch5 as H
from bookout import T, figure, out, style

AG_RATIO = 0.6                       # uniform elongation / elongation after fracture (set by this book, for illustration)
# (name, E GPa, ReL, Rm, A%, yield plateau, source)
CURVES = []
for g in H.steel_grades():
    E = H.lib(g["lib_id"])["E"]
    state = {"Q235": T("热轧", "hot rolled"), "45": T("正火", "normalized"), "40Cr": T("调质", "Q&T"), "20CrMnTi": T("淬火回火", "Q&T")}[g["grade"]]
    CURVES.append((T(f"{g['grade']}（{state}）", f"{g['grade']} ({state})"), E, g["ReL"], g["Rm"], g["A"], 0.015 if g["grade"] == "Q235" else 0.0, "GB"))
al = H.lib("6061-T6")
ss = H.lib("304")
CURVES.append(("6061-T6", al["E"], al["sy"], al["sb"], 10, 0.0, T("材料库；A 为典型值", "library; A typical")))
CURVES.append(("304", ss["E"], ss["sy"], ss["sb"], 40, 0.0, T("材料库；A 按 GB/T 1220", "library; A per GB/T 1220")))
CURVES = [c for c in CURVES if not c[0].startswith("20CrMnTi")]   # the test-piece properties of a case-hardening steel do not represent the surface layer of a part; not drawn


def fit(E, sy, Rm, A, plateau):
    eu = AG_RATIO * A / 100                                  # uniform elongation (engineering strain)
    eps_u = math.log(1 + eu)                                 # the corresponding true strain

    def resid(n):
        # necking point: dσ/dε = σ → ε₀ + εp = n; true strain = εp + σ/E + plateau
        K = Rm * math.exp(eps_u) / n ** n
        e0 = (sy / K) ** (1 / n)
        return (n - e0) + Rm * math.exp(eps_u) / (E * 1000) + plateau - eps_u

    n = brentq(resid, 0.02, 0.6)
    K = Rm * math.exp(eps_u) / n ** n
    return n, K, (sy / K) ** (1 / n), eu


def curve(E, sy, Rm, A, plateau):
    n, K, e0, eu = fit(E, sy, Rm, A, plateau)
    Em = E * 1000
    pts = [(0.0, 0.0), (sy / Em, sy)]
    if plateau:
        pts.append((sy / Em + plateau, sy))
    for ep in np.linspace(0, n - e0, 60)[1:]:
        st = K * (e0 + ep) ** n
        et = ep + st / Em + plateau
        e = math.exp(et) - 1
        pts.append((e, st / (1 + e)))
    eA = A / 100
    pts.append((eA, 0.82 * Rm))                              # from necking to fracture (schematic)
    return np.array(pts), n


plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.6, 3.2), gridspec_kw={"width_ratios": [1.35, 1.0]})
cols = ["#7f7f7f", "#1f77b4", "#d62728", "#2ca02c", "#ff7f0e"]
ns = {}
for (name, E, sy, Rm, A, pl, src), c in zip(CURVES, cols):
    p, n = curve(E, sy, Rm, A, pl)
    ns[name] = n
    a0.plot(100 * p[:, 0], p[:, 1], color=c, lw=1.1, label=name)
    a0.plot(100 * p[-1, 0], p[-1, 1], "x", color=c, ms=4)
a0.set_xlabel(T("工程应变 / %", "Engineering strain / %"), fontsize=7.5)
a0.set_ylabel(T("工程应力 / MPa", "Engineering stress / MPa"), fontsize=7.5)
a0.set_xlim(0, 45)
a0.set_ylim(0, 1100)
a0.legend(fontsize=6.5, frameon=False)
a0.tick_params(labelsize=6.5)
a0.set_title(T("(a) 拉伸曲线（模型，按最小值拟合；× 为断裂）", "(a) Tensile curves (model fitted to minimum values; × = fracture)"), fontsize=7.8)

libs = ["Q235", "45-QT", "40Cr-QT", "20CrMnTi-CQ", "HT200", "QT500-7", "304", "6061-T6", "7075-T6", "ABS", "PA66"]
rat = [(H.lib(m)["name"].split("（")[0].split(" ")[0], H.lib(m)["s1"] / H.lib(m)["sb"], m) for m in libs]
y = range(len(rat))
KIND = {"Q235": "#1f77b4", "45-QT": "#1f77b4", "40Cr-QT": "#1f77b4", "20CrMnTi-CQ": "#1f77b4", "304": "#1f77b4",
        "HT200": "#8c564b", "QT500-7": "#8c564b", "6061-T6": "#2ca02c", "7075-T6": "#2ca02c", "ABS": "#ff7f0e", "PA66": "#ff7f0e"}
a1.barh(list(y), [r[1] for r in rat], color=[KIND[r[2]] for r in rat])
a1.set_yticks(list(y))
a1.set_yticklabels([r[0] for r in rat], fontsize=6.4)
a1.invert_yaxis()
a1.set_xlabel("σ₋₁ / σb", fontsize=7.5)
a1.axvline(0.45, color=H.MUTED, lw=0.6, ls="--")
a1.tick_params(labelsize=6.5)
a1.set_title(T("(b) σ₋₁/σb（材料库；蓝 钢，棕 铸铁，绿 铝，橙 塑料）", "(b) σ₋₁/σb (library; blue steel, brown iron,\ngreen Al, orange plastics)"), fontsize=7.4)
fig.tight_layout()
figure(fig, "fig5_1_1")

steel_r = [r[1] for r in rat if r[2] in ("Q235", "45-QT", "40Cr-QT", "20CrMnTi-CQ")]
al_r = [r[1] for r in rat if r[2] in ("6061-T6", "7075-T6")]
g45 = next(g for g in H.steel_grades() if g["grade"] == "45")
out(n_curves=len(CURVES), ag_ratio=AG_RATIO, n45=ns[[k for k in ns if k.startswith("45")][0]], n304=ns["304"], n40=ns[[k for k in ns if k.startswith("40Cr")][0]],
    r_steel_lo=min(steel_r), r_steel_hi=max(steel_r), r_al_lo=min(al_r), r_al_hi=max(al_r),
    r_ht=H.lib("HT200")["s1"] / H.lib("HT200")["sb"], r_pa=H.lib("PA66")["s1"] / H.lib("PA66")["sb"],
    E45=H.lib("45-QT")["E"], E_al=al["E"], E_ratio=H.lib("45-QT")["E"] / al["E"],
    Rm45=g45["Rm"], ReL45=g45["ReL"], A45=g45["A"], Z45=g45["Z"], KU45=g45["KU2"])
