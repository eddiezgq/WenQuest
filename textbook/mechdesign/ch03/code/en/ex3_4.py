"""Section 3.4 Part drawing: the part drawing of the roller pillow block (for 6207) of the palletizing conveyor, generated from the 3D model; A3, scale 1:1; front view in half section, top view, left view in full section;
dimensions and tolerance classes, datum and parallelism, surface roughness (machined and cast surfaces), technical requirements, title block (Figure 3.4.1). The dimensions follow from the design rules of Section 3.8."""
import math

import numpy as np

import _ch3 as H
import mdstd
from bookout import T, figure, out, style

p = H.pillow_params("6207")
pb = H.pillow_block(p)
L, Wb, W, tb, Hc, Ro, D, D2, Lh, dh, Lr, hr, seat, dg = (p[k] for k in ("L", "Wb", "W", "tb", "H", "Ro", "D", "D2", "Lh", "dh", "Lr", "hr", "seat", "dg"))
BORE = "H7"                                     # Outer ring stationary, inner ring rotating: the housing bore is H7 (Chapters 4 and 34)
es, ei = mdstd.hole_dev("H", 7, D)                # μm
assert "1:1" in mdstd.drawing_scales()
SHEET = (420.0, 297.0)                          # A3 landscape
FS = 6.4

plt = style()
fig, ax = plt.subplots(figsize=(7.4, 7.4 * SHEET[1] / SHEET[0]))
sh = H.Sheet(ax)
sh.frame(*SHEET)
# Positions of the three views (first-angle projection: top view below the front view, left view on the right)
fx, fy = 150.0, 150.0                           # Front view: midpoint of the base
tx, ty = fx, fy - 30.0 - Wb / 2                 # Top view: center
lx, ly = fx + L / 2 + 42.0 + Wb / 2, fy         # Left view: midpoint of the base (u = -Y, front on the right)

# ---- Front view: right half in section (cutting plane through the bearing-bore axis, parallel to the frontal plane)
v, h_, r = H.section(pb, "front", keep="half")
sh.hatch(r, fx, fy, spacing=2.2)
sh.polys(v, "thick", fx, fy)
sh.raw_line((fx, fy - 4), (fx, fy + Hc + Ro + 4), "center")
sh.raw_line((fx - Ro - 6, fy + Hc), (fx + Ro + 6, fy + Hc), "center")
for s_ in (-1, 1):
    sh.raw_line((fx + s_ * Lh / 2, fy - 3), (fx + s_ * Lh / 2, fy + tb + 3), "center")
# ---- Top view
v, h_ = H.project(pb, "top")
sh.polys(h_, "hidden", tx, ty)
sh.polys(v, "thick", tx, ty)
sh.raw_line((tx, ty - Wb / 2 - 4), (tx, ty + Wb / 2 + 4), "center")
for s_ in (-1, 1):
    sh.raw_line((tx + s_ * Lh / 2 - dh / 2 - 3, ty), (tx + s_ * Lh / 2 + dh / 2 + 3, ty), "center")
    sh.raw_line((tx + s_ * Lh / 2, ty - dh / 2 - 3), (tx + s_ * Lh / 2, ty + dh / 2 + 3), "center")
# ---- Left view: full section (cutting plane through the bearing-bore axis, parallel to the profile plane), showing the stepped bore
v, h_, r = H.section(pb, "left")
sh.hatch(r, lx, ly, spacing=2.2)
sh.polys(v, "thick", lx, ly)
sh.raw_line((lx - Wb / 2 - 5, ly + Hc), (lx + Wb / 2 + 5, ly + Hc), "center")
# Cutting position: short thick strokes and letters at the top and bottom of the front view, A-A above the left view (a section in its projected position needs no arrows)
for y0_, y1_ in ((fy + Hc + Ro + 6, fy + Hc + Ro + 10), (fy - 6, fy - 10)):
    sh.raw_line((fx, y0_), (fx, y1_), "thick")
sh.text(fx - 2.5, fy + Hc + Ro + 8, "A", size=FS, ha="right", va="center")
sh.text(fx - 2.5, fy - 8, "A", size=FS, ha="right", va="center")
sh.text(lx, ly + Hc + Ro + 28, "A–A", size=FS * 1.1)

# ---- Dimensions
# Front view: center height (functional dimension, toleranced individually), base thickness, arc radius, base recess
xd = fx - L / 2 - 8
sh.dim((xd, fy), (xd, fy + Hc), 0.0, f"{Hc:g}±0.05", size=FS, ext=False)
sh.dim((xd - 9, fy), (xd - 9, fy + tb), 0.0, f"{tb:g}", size=FS, ext=False)
for yy in (fy, fy + tb):
    sh.raw_line((fx - L / 2 - 1.5, yy), (xd - 11, yy))
sh.raw_line((fx - Ro - 1.5, fy + Hc), (xd - 2, fy + Hc))
ang = math.radians(135)
pe = (fx + Ro * math.cos(ang), fy + Hc + Ro * math.sin(ang))
sh.raw_line((fx, fy + Hc), pe)
sh.arrow((fx, fy + Hc), pe, size=2.4)
sh.text(fx + Ro * 0.6 * math.cos(ang) - 1.5, fy + Hc + Ro * 0.6 * math.sin(ang) + 1.5, f"R{Ro:g}", size=FS, rot=-45,
        bbox=dict(boxstyle="square,pad=0.08", fc="white", ec="none"))
sh.dim((fx - Lr / 2, fy - 13), (fx + Lr / 2, fy - 13), 0.0, f"{Lr:g}", size=FS, ext=False, tside=-1, tpos=0.3)
for xx in (fx - Lr / 2, fx + Lr / 2):
    sh.raw_line((xx, fy + hr - 1), (xx, fy - 15))
# Top view: base length, hole spacing, base width, anchor-bolt holes, oil hole
yb = ty - Wb / 2 - 8
sh.dim((tx - Lh / 2, yb), (tx + Lh / 2, yb), 0.0, f"{Lh:g}", size=FS, ext=False)
sh.dim((tx - L / 2, yb - 9), (tx + L / 2, yb - 9), 0.0, f"{L:g}", size=FS, ext=False)
for xx in (tx - Lh / 2, tx + Lh / 2):
    sh.raw_line((xx, ty - dh / 2 - 4), (xx, yb - 2))
for xx in (tx - L / 2, tx + L / 2):
    sh.raw_line((xx, ty - Wb / 2 - 1.5), (xx, yb - 11))
xr = tx + L / 2 + 8
sh.dim((xr, ty - Wb / 2), (xr, ty + Wb / 2), 0.0, f"{Wb:g}", size=FS, ext=False)
for yy in (ty - Wb / 2, ty + Wb / 2):
    sh.raw_line((tx + L / 2 + 1.5, yy), (xr + 2, yy))
q = (tx + Lh / 2 + dh / 2 * math.cos(math.radians(45)), ty + dh / 2 * math.sin(math.radians(45)))
ax.annotate(f"2×Ø{dh:g}", xy=q, xytext=(q[0] + 8, ty + Wb / 2 + 7), fontsize=FS, ha="left",
            arrowprops=dict(arrowstyle="-|>", lw=0.45, color=H.INK, shrinkA=0, shrinkB=0, mutation_scale=7))
q = (tx + dg / 2 * math.cos(math.radians(45)), ty + dg / 2 * math.sin(math.radians(45)))
ax.annotate(T(f"Ø{dg:g}（注油孔）", f"Ø{dg:g} (oil hole)"), xy=q, xytext=(q[0] + 14, ty + Wb / 2 + 7), fontsize=FS, ha="left",
            arrowprops=dict(arrowstyle="-|>", lw=0.45, color=H.INK, shrinkA=0, shrinkB=0, mutation_scale=7))
# Left view: bearing bore Ø72H7 and shoulder bore, bore depth, block width (in the left view the front is on the right, and the bearing bore opens from the right end)
xs1 = lx + W / 2 - seat / 2
sh.dim((xs1, ly + Hc - D / 2), (xs1, ly + Hc + D / 2), 0.0, f"Ø{D}{BORE}", size=FS, ext=False, tpos=0.78)
xs2 = lx - W / 2 + (W - seat) / 2
sh.dim((xs2, ly + Hc - D2 / 2), (xs2, ly + Hc + D2 / 2), 0.0, f"Ø{D2}", size=FS, ext=False, tpos=0.22)
yt = ly + Hc + Ro + 8
sh.dim((lx + W / 2 - seat, yt), (lx + W / 2, yt), 0.0, f"{seat:g}", size=FS, ext=False)
sh.dim((lx - W / 2, yt + 9), (lx + W / 2, yt + 9), 0.0, f"{W:g}", size=FS, ext=False)
sh.raw_line((lx + W / 2 - seat, ly + Hc + D / 2 + 1.5), (lx + W / 2 - seat, yt + 2))
for xx in (lx + W / 2, lx - W / 2):
    sh.raw_line((xx, ly + Hc + Ro + 1.5), (xx, yt + 11))

# ---- Datum and geometrical tolerance: the base is datum A; parallelism of the bearing-bore axis to A
xa = fx - L / 2 + 12
ax.add_patch(H.Polygon([(xa - 2.2, fy - 0.2), (xa + 2.2, fy - 0.2), (xa, fy - 3.4)], closed=True, fc=H.INK, ec=H.INK, lw=0.3))
sh.raw_line((xa, fy - 3.4), (xa, fy - 8))
ax.add_patch(H.Polygon([(xa - 3.5, fy - 8), (xa + 3.5, fy - 8), (xa + 3.5, fy - 15), (xa - 3.5, fy - 15)], closed=True, fill=False, lw=0.45, ec=H.INK))
sh.text(xa, fy - 11.5, "A", size=FS, va="center")


def fcf(x, y, cells):
    xs = np.cumsum([x, 8, 13, 8])
    ax.add_patch(H.Polygon([(xs[0], y), (xs[-1], y), (xs[-1], y + 7), (xs[0], y + 7)], closed=True, fill=False, lw=0.45, ec=H.INK))
    for xx in xs[1:-1]:
        sh.raw_line((xx, y), (xx, y + 7))
    for a_, b_, t_ in zip(xs, xs[1:], cells):
        sh.text((a_ + b_) / 2, y + 3.5, t_, size=FS, va="center")
    return xs


yf = ly + Hc + D / 2 + 3                                                # The leader arrow of the frame is aligned with the dimension line of Ø72H7: the toleranced feature is the axis of the bore
xs = fcf(lx - W / 2 - 52, yf, ["∥", "0.03", "A"])
sh.raw_line((xs[-1], yf + 3.5), (xs1 - 6, yf + 3.5))
sh.raw_line((xs1 - 6, yf + 3.5), (xs1 - 6, ly + Hc + D / 2))
sh.raw_line((xs1 - 6, ly + Hc + D / 2), (xs1, ly + Hc + D / 2))

# ---- Surface roughness: machined surfaces indicated individually, the rest are cast surfaces (material removal not permitted)
sh.ra_leader((lx + W / 2 - seat * 0.5, ly + Hc - D / 2), (lx + W / 2 + 14, ly + Hc - D / 2 - 18), "1.6")    # Bearing bore
sh.ra_leader((fx + L / 2 - 8, fy), (fx + L / 2 + 4, fy - 16), "6.3")                                     # Base (mounting face)
sh.ra_leader((lx + W / 2, ly + Hc + Ro - 10), (lx + W / 2 + 14, ly + Hc + Ro - 2), "3.2")             # Both end faces
sh.ra_cast(338, 50)
sh.text(346, 50, "( √ )", size=FS * 1.05, ha="left", va="bottom")

# ---- Technical requirements, title block
notes = [T("技术要求", "Technical requirements"),
         T("1. 铸件不得有砂眼、气孔、裂纹等缺陷。", "1. No sand holes, blowholes or cracks."),
         T("2. 铸件经时效处理。", "2. Casting stress-relieved (aged)."),
         T("3. 未注铸造圆角 R3–R5。", "3. Unspecified casting radii R3–R5."),
         T("4. 未注尺寸公差：加工面按 GB/T 1804-m，", "4. General tolerances: machined GB/T 1804-m,"),
         T("   铸造面按 GB/T 6414。", "   as-cast GB/T 6414."),
         T("5. 非加工面涂底漆。", "5. Prime-paint unmachined surfaces.")]
for i, t in enumerate(notes):
    sh.text(318, 125 - i * 8, t, size=FS * (1.1 if i == 0 else 0.95), ha="left", va="center", weight="bold" if i == 0 else "normal")
sh.title_block(415, 5, {"name": T("轴承座", "Pillow block"), "material": "HT200", "drawn": T("问渠教材", "WenQuest"), "checked": "—",
                        "scale": "1:1", "qty": "2", "date": "2026-10", "rev": "1", "no": "PB-6207", "org": T("教材示例", "Textbook"),
                        "title": "PB-6207"})
fig.subplots_adjust(0, 0, 1, 1)
figure(fig, "fig3_4_1")

out(scale="1:1", sheet="A3", L=L, Wb=Wb, W=W, tb=tb, H=Hc, Ro=Ro, D=D, D2=D2, Lh=Lh, dh=dh, Lr=Lr, seat=seat, dg=dg, bore_fit=BORE,
    bore_lo=D + ei / 1000, bore_hi=D + es / 1000)
