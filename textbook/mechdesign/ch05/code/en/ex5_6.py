"""Section 5.6 Additive manufacturing: the 3D-printed finger of an electric gripper for a collaborative robot. The print orientation reduces
the strength when the layers are pulled apart; gripping is a pulsating load from 0 to maximum, so fatigue is checked with the Goodman line.
Example 5.6.1, Figure 5.6.1. Materials: ABS from the digital-factory material library (its σ₋₁ is estimated in the library as 0.3σs;
for the interlayer strength reduction of 0.5–0.8 see the library note) and PA12 from the table of this book (values for selective-laser-sintered parts)."""
import math

import _ch5 as H
from bookout import T, figure, out, style

L, B, HH = 60.0, 12.0, 8.0          # finger: cantilever length, width, thickness, mm (set by this book)
F = 40.0                            # fingertip gripping force, N (half the rated gripping force of the gripper, set by this book)
S_REQ = 1.5                         # required fatigue safety factor
abs_ = H.lib("ABS")
pa12 = H.by_id("pa12")              # the 48 MPa in the table is the tensile strength of sintered parts (no distinct yield); not reduced further
K_INPLANE = 0.9                     # tension along the print path (printed flat): 0.9 of the solid value (set by this book)
K_LAYER = (0.5, 0.8)                # tension normal to the layers (printed upright): library note 0.5–0.8; the lower limit is taken, on the safe side
FAT_RATIO = abs_["s1"] / abs_["sb"]  # no fatigue data for PA12: estimated with the σ₋₁/σb of ABS (set by this book)


def sigma(h):
    return 6 * F * L / (B * h * h)


def goodman_S(s_max, s1, sb):
    """Pulsating cycle (0 → s_max): σa = σm = s_max/2, 1/S = σa/σ₋₁ + σm/σb"""
    return 1 / (s_max / 2 / s1 + s_max / 2 / sb)


s0 = sigma(HH)
# (name, static strength (yield or tensile), σ₋₁, σb)
opts = [
    (T("ABS，平放打印", "ABS, printed flat"), abs_["sy"] * K_INPLANE, abs_["s1"] * K_INPLANE, abs_["sb"] * K_INPLANE),
    (T("ABS，竖放打印", "ABS, printed upright"), abs_["sy"] * K_LAYER[0], abs_["s1"] * K_LAYER[0], abs_["sb"] * K_LAYER[0]),
    (T("PA12，激光烧结", "PA12, laser sintered"), pa12["sy"], pa12["sy"] * FAT_RATIO, pa12["sy"]),
]
res = []
for name, sst, s1, sb in opts:
    s_allow = 2 / (S_REQ * (1 / s1 + 1 / sb))                  # largest bending stress allowed for a Goodman safety factor of S_REQ
    h_req = math.sqrt(6 * F * L / (B * s_allow))
    res.append((name, sst / s0, goodman_S(s0, s1, sb), h_req))

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.2, 2.8))
x = range(len(res))
a0.bar([i - 0.18 for i in x], [r[1] for r in res], 0.36, color="#1f77b4", label=T("静强度", "static"))
a0.bar([i + 0.18 for i in x], [r[2] for r in res], 0.36, color="#d62728", label=T("疲劳（Goodman，脉动循环）", "fatigue (Goodman, 0 → max)"))
a0.axhline(S_REQ, color=H.MUTED, lw=0.7, ls="--")
a0.axhline(1.0, color=H.INK, lw=0.6)
a0.set_xticks(list(x))
a0.set_xticklabels([r[0] for r in res], fontsize=6.4)
a0.set_ylabel(T("安全系数", "Safety factor"), fontsize=7.5)
a0.tick_params(labelsize=6.5)
a0.legend(fontsize=6.4, frameon=False)
a0.set_title(T(f"(a) 厚 {HH:.0f} mm 时的安全系数", f"(a) Safety factors at {HH:.0f} mm thickness"), fontsize=7.8)
a1.bar(list(x), [r[3] for r in res], 0.5, color="#2ca02c")
a1.axhline(HH, color=H.MUTED, lw=0.7, ls="--")
a1.set_xticks(list(x))
a1.set_xticklabels([r[0] for r in res], fontsize=6.4)
a1.set_ylabel(T("所需厚度 / mm", "Required thickness / mm"), fontsize=7.5)
a1.tick_params(labelsize=6.5)
a1.set_title(T(f"(b) 疲劳安全系数 {S_REQ} 所需的厚度", f"(b) Thickness for fatigue safety factor {S_REQ}"), fontsize=7.8)
fig.tight_layout()
figure(fig, "fig5_6_1")

out(L=L, B=B, h=HH, F=F, sigma=s0, S_req=S_REQ, abs_sy=abs_["sy"], abs_s1=abs_["s1"], abs_sb=abs_["sb"], pa12_sb=pa12["sy"],
    k_in=K_INPLANE, k_lay_lo=K_LAYER[0], k_lay_hi=K_LAYER[1], fat_ratio=FAT_RATIO,
    S_flat=res[0][1], Sf_flat=res[0][2], h_flat=res[0][3], S_up=res[1][1], Sf_up=res[1][2], h_up=res[1][3],
    S_pa=res[2][1], Sf_pa=res[2][2], h_pa=res[2][3])
