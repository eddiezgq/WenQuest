"""Section 3.8 Modeling in code: a parametric pillow block (build123d). Input a bearing designation; the design rules give all the dimensions, the 3D solid is generated and exported as STEP;
the same program generates three sizes, 6205, 6207 and 6209 (Program 3.8.1, Figure 3.8.1)."""
import math
import os
import tempfile

import build123d as bd

import _ch3 as H
import mdstd
from bookout import T, figure, out, style

R20 = [10, 11.2, 12.5, 14, 16, 18, 20, 22.4, 25, 28, 31.5, 35.5, 40, 45, 50, 56, 63, 71, 80, 90, 100]   # Preferred number series R20 (Section 2.6)


def params(brg):
    """Design rules: bearing designation -> all dimensions. To change a rule, change it only here; the model and the drawings change together."""
    b = mdstd.bearing(brg)                         # Bearing d, D, B (GB/T 276, the standard tables of this book)
    D, B = b["D"], b["B"]
    wall = math.floor(0.12 * D + 3 + 0.5)                     # Wall thickness around the bearing bore grows with the outer diameter
    Ro = D / 2 + wall                              # Radius of the upper arc
    H = next(v for v in R20 if v >= Ro + 2)        # Center height: an R20 preferred number
    bolt, dh = ("M8", 9.0) if D <= 52 else ("M10", 11.0) if D <= 72 else ("M12", 13.5)   # Anchor bolt and clearance hole (GB/T 5277)
    W = B + 14                                     # Block width = bearing width + end-cover spigot 4 + shoulder 10
    Lh = 2 * (Ro + dh + 2)                         # Anchor-hole spacing: hole center dh + 2 from the upright, hole edge dh/2 + 2 from the upright (room for a washer)
    return dict(brg=brg, D=D, B=B, wall=wall, Ro=Ro, H=H, bolt=bolt, dh=dh, W=W, Wb=W + 12, tb=math.floor(0.25 * H + 0.5),
                Lh=Lh, L=math.ceil(Lh + 3 * dh), D2=D - 8, seat=B + 4, Lr=Lh - 2 * dh - 10, hr=2.0, dg=6.0)


def model(p):
    """The order of the features is the order of machining and design: base -> upright and arc -> stepped bore -> anchor-bolt holes -> base recess -> oil hole"""
    L, W, Wb, H, Ro, tb = p["L"], p["W"], p["Wb"], p["H"], p["Ro"], p["tb"]
    s = bd.Pos(0, 0, tb / 2) * bd.Box(L, Wb, tb)                                              # Base
    s += bd.Pos(0, 0, H / 2) * bd.Box(2 * Ro, W, H)                                            # Upright
    s += bd.Pos(0, 0, H) * bd.Rot(90, 0, 0) * bd.Cylinder(Ro, W)                               # Upper arc
    s -= bd.Pos(0, 0, H) * bd.Rot(90, 0, 0) * bd.Cylinder(p["D2"] / 2, W + 2)                 # Shoulder bore (through)
    y0 = -W / 2 + p["seat"] / 2 - 0.5
    s -= bd.Pos(0, y0, H) * bd.Rot(90, 0, 0) * bd.Cylinder(p["D"] / 2, p["seat"] + 1)          # Bearing bore (from the front face)
    for x in (-p["Lh"] / 2, p["Lh"] / 2):
        s -= bd.Pos(x, 0, tb / 2) * bd.Cylinder(p["dh"] / 2, tb + 2)                           # Anchor-bolt holes
    s -= bd.Pos(0, 0, p["hr"] / 2 - 0.5) * bd.Box(p["Lr"], Wb + 2, p["hr"] + 1)                # Recess in the middle of the base, the two ends rest on the ground
    hg = Ro - p["D"] / 2 + 2
    s -= bd.Pos(0, 0, H + p["D"] / 2 - 1 + hg / 2) * bd.Cylinder(p["dg"] / 2, hg)              # Oil hole
    return s.clean()


rows, solids = [], {}
tmp = tempfile.mkdtemp()
for brg in ("6205", "6207", "6209"):
    p = params(brg)
    s = model(p)
    assert abs(s.volume - H.pillow_block(H.pillow_params(brg)).volume) < 1e-6 * s.volume   # Same as the model used by the other programs of this chapter
    path = os.path.join(tmp, f"pillow_{brg}.step")
    bd.export_step(s, path)                                                                   # The format handed to CAE, CAM and PLM
    rho = 7.2                                                                                 # Gray cast iron HT200, g/cm³
    rows.append({**p, "mass": s.volume * rho / 1e6, "step_kb": os.path.getsize(path) / 1024, "faces": len(s.faces())})
    solids[brg] = s

plt = style()
fig, axs = plt.subplots(1, 3, figsize=(7.4, 2.7), gridspec_kw={"width_ratios": [r["L"] for r in rows]})
for ax, r in zip(axs, rows):
    sh = H.Sheet(ax)
    sh.polys(H.project(solids[r["brg"]], "iso")[0], "thick")
    ax.set_title(T(f"{r['brg']}：D = {r['D']}，H = {r['H']:g}，L = {r['L']:g}\n{r['bolt']} 地脚螺栓，{r['mass']:.1f} kg",
                   f"{r['brg']}: D = {r['D']}, H = {r['H']:g}, L = {r['L']:g}\n{r['bolt']} bolts, {r['mass']:.1f} kg"), fontsize=7.5)
    ax.set_xlim(-rows[-1]["L"] * 0.62, rows[-1]["L"] * 0.62)
    ax.set_ylim(-rows[-1]["L"] * 0.32, rows[-1]["L"] * 0.62)
fig.tight_layout()
figure(fig, "fig3_8_1")

r5, r7, r9 = rows
out(n_lines=sum(1 for ln in open(__file__, encoding="utf-8") if ln.strip() and not ln.strip().startswith("#")),
    L5=r5["L"], L7=r7["L"], L9=r9["L"], H5=r5["H"], H7=r7["H"], H9=r9["H"], m5=r5["mass"], m7=r7["mass"], m9=r9["mass"],
    bolt5=r5["bolt"], bolt9=r9["bolt"], faces7=r7["faces"], step7=r7["step_kb"], wall7=r7["wall"], Ro7=r7["Ro"])
