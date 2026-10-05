"""Section 3.5 Assembly drawing and parts list: the assembly drawing of the output shaft assembly SA-300 of WQR-105 (version B, Chapter 33): shaft not sectioned, gear and sleeve sectioned,
bearings in conventional representation (upper half) and general representation (lower half), gear drawn to GB/T 4459.2, item numbers and parts list; the parts list is generated from the digital factory BOM,
plus the changes brought by the engineering change of Chapter 33 (Figure 3.5.1)."""
import math
import re

import numpy as np

import _ch3 as H
import _shaft as S
import mdstd
from bookout import T, figure, out, style

F = H.F
brg = mdstd.bearing(S.BRG)
d_b, D_b, B_b = brg["d"], brg["D"], brg["B"]
kw = H.sh301_keyways()
key_g, key_c = mdstd.key_for(40), mdstd.key_for(30)
L_kg, L_kc = kw[0][1] - kw[0][0], kw[1][1] - kw[1][0]
m, z = F.GEARS["GR-302"]["m"], F.GEARS["GR-302"]["z"]
d_p = m * z
d_a, d_f = d_p + 2 * m, d_p - 2.5 * m
B_RIM, D_HUB = 45.0, 64.0                     # Chapter 33: rim × 45, hub Ø64 × 55
z_hub0, z_hub1 = S.Z_GEAR - S.HUB_GEAR / 2, S.Z_GEAR + S.HUB_GEAR / 2
z_rim0, z_rim1 = z_hub1 - 5 - B_RIM, z_hub1 - 5          # Rim on the right, 5 mm from the collar side (an assumption of this drawing)
SLEEVE_OD = brg["da_min"] + 2                 # Sleeve outer diameter: not less than the bearing abutment dimension da (6207: 42); 44 is taken
z_brgA = (S.Z_BRG_A - B_b / 2, S.Z_BRG_A + B_b / 2)
z_brgB = (S.Z_BRG_B - B_b / 2, S.Z_BRG_B + B_b / 2)
z_sl = (z_brgA[1], z_hub0)


rows = H.sa300_rows()
key_c_code = rows[[r["code"].startswith("KEY-C8") for r in rows].index(True)]["code"]
no_of = {r["code"]: r["no"] for r in rows}
no_sleeve = rows[-1]["no"]

plt = style()
A3 = (420.0, 297.0)
fig, ax = plt.subplots(figsize=(7.4, 7.4 * A3[1] / A3[0]))
sh = H.Sheet(ax)
sh.frame(*A3)
x0, y0 = 60.0, 150.0


def X(zz):
    return x0 + zz


def Y(r):
    return y0 + r


# ---- Shaft (a solid shaft cut lengthwise is drawn unsectioned: outline only; keyways facing the viewer, keys in their slots)
vis, hid = H.project(H.sh301b(), "front")
sh.polys(vis, "thick", x0, y0)
sh.raw_line((X(-8), y0), (X(S.LEN_B + 8), y0), "center")


def rect(z0, z1, r0, r1):
    return [[(z0, r0), (z1, r0), (z1, r1), (z0, r1)]]


def closed(poly):
    return [list(poly) + [poly[0]]]


def part(z0, z1, r0, r1, angle=45, hatch=True, spacing=2.4):
    for k in (1, -1):
        reg = [[(X(a), Y(k * b)) for a, b in rect(z0, z1, r0, r1)[0]]]
        if hatch:
            sh.hatch([reg], angle=angle, spacing=spacing)
        sh.polys(closed(reg[0]), "thick")


# ---- Gear (GB/T 4459.2: teeth are not sectioned in a sectional view; tip and root lines thick continuous, pitch line chain); adjacent parts hatched in opposite directions
for k in (1, -1):
    hub = [(X(z_hub0), Y(k * 20)), (X(z_hub1), Y(k * 20)), (X(z_hub1), Y(k * D_HUB / 2)), (X(z_rim1), Y(k * D_HUB / 2)),
           (X(z_rim1), Y(k * d_f / 2)), (X(z_rim0), Y(k * d_f / 2)), (X(z_rim0), Y(k * D_HUB / 2)), (X(z_hub0), Y(k * D_HUB / 2))]
    sh.hatch([[hub]], angle=-45, spacing=2.4)
    sh.polys([hub + [hub[0]]], "thick")
    tooth = [(X(z_rim0), Y(k * d_f / 2)), (X(z_rim1), Y(k * d_f / 2)), (X(z_rim1), Y(k * d_a / 2)), (X(z_rim0), Y(k * d_a / 2))]
    sh.polys([tooth + [tooth[0]]], "thick")
    sh.raw_line((X(z_rim0) - 3, Y(k * d_p / 2)), (X(z_rim1) + 3, Y(k * d_p / 2)), "center")
# ---- Sleeve (sectioned, hatching opposite to the gear)
part(z_sl[0], z_sl[1], d_b / 2, SLEEVE_OD / 2, angle=45, spacing=4.0)   # Opposite to the gear; same direction as the bearing inner ring, so the spacing is clearly different
# ---- Bearings: upper half in conventional representation (inner and outer rings hatched in the same direction, rolling elements as circles), lower half in general representation (rectangle + upright cross)
t_ring = (D_b - d_b) / 2 * 0.28
for z0, z1 in (z_brgA, z_brgB):
    zc = (z0 + z1) / 2
    for r0, r1 in ((d_b / 2, d_b / 2 + t_ring), (D_b / 2 - t_ring, D_b / 2)):
        reg = [[(X(z0), Y(r0)), (X(z1), Y(r0)), (X(z1), Y(r1)), (X(z0), Y(r1))]]
        sh.hatch([reg], angle=45, spacing=1.8)
        sh.polys(closed(reg[0]), "thick")
    rb = (D_b - d_b) / 4 * 0.75
    th = np.linspace(0, 2 * math.pi, 60)
    H.ball(sh, X(zc), Y((d_b + D_b) / 4), rb)
    sh.polys([[(X(z0), Y(d_b / 2)), (X(z0), Y(D_b / 2))], [(X(z1), Y(d_b / 2)), (X(z1), Y(D_b / 2))]], "thick")
    box = [(X(z0), Y(-d_b / 2)), (X(z1), Y(-d_b / 2)), (X(z1), Y(-D_b / 2)), (X(z0), Y(-D_b / 2))]
    sh.polys([box + [box[0]]], "thick")
    ym = Y(-(d_b + D_b) / 4)
    sh.raw_line((X(zc) - B_b * 0.3, ym), (X(zc) + B_b * 0.3, ym), "thick")
    sh.raw_line((X(zc), ym - (D_b - d_b) / 2 * 0.3), (X(zc), ym + (D_b - d_b) / 2 * 0.3), "thick")

# ---- Dimensions: fit dimensions, mounting dimensions (distance between bearing centers), overall dimensions
FS = 6.5
xg = X(z_hub1 - 2.5)                                     # Fit dimension at the gear seat: placed between the right end of the keyway and the collar
sh.dim((xg, Y(-20)), (xg, Y(20)), 0.0, "Ø40 H7/r6", size=FS, ext=False, tpos=0.7)
for z0, z1 in (z_brgA, z_brgB):
    xx = X(z0 + 3)
    sh.dim((xx, Y(-d_b / 2)), (xx, Y(d_b / 2)), 0.0, "Ø35k6", size=FS, ext=False, tpos=0.72)
xo = X(-14)                                              # Overall dimension: tip diameter on the left, extension lines drawn from the tip
sh.dim((xo, Y(-d_a / 2)), (xo, Y(d_a / 2)), 0.0, f"Ø{d_a:g}", size=FS, ext=False, tpos=0.75)
for k in (-1, 1):
    sh.raw_line((X(z_rim0) - 1.5, Y(k * d_a / 2)), (xo - 2, Y(k * d_a / 2)))
yt_ = Y(d_a / 2) + 10                                    # Overall length above
sh.dim((X(0), yt_), (X(S.LEN_B), yt_), 0.0, f"{S.LEN_B:g}", size=FS, ext=False)
sh.raw_line((X(0), Y(D_b / 2) + 1.5), (X(0), yt_ + 2))
sh.raw_line((X(S.LEN_B), Y(15) + 1.5), (X(S.LEN_B), yt_ + 2))
xo2 = X(z_brgB[1]) + 6                                   # Mounting dimension: bearing outer diameter (fits the housing bore)
sh.dim((xo2, Y(-D_b / 2)), (xo2, Y(D_b / 2)), 0.0, f"Ø{D_b}", size=FS, ext=False, tpos=0.8)
for k in (-1, 1):
    sh.raw_line((X(z_brgB[1]) + 1.5, Y(k * D_b / 2)), (xo2 + 2, Y(k * D_b / 2)))
yb = Y(-d_a / 2) - 7                                     # Mounting dimension: distance between bearing centers
sh.dim((X(S.Z_BRG_A), yb), (X(S.Z_BRG_B), yb), 0.0, f"{S.SPAN:g}", size=FS, ext=False)
for zz in (S.Z_BRG_A, S.Z_BRG_B):
    sh.raw_line((X(zz), Y(-D_b / 2) - 1.5), (X(zz), yb - 2))

# ---- Item numbers: leaders start inside the part (small dot), numbers one size larger than dimension figures, arranged clockwise
balloon = {                                               # (leader start x, y, number position x, y)
    "GR-302": (X(z_rim0 + 25), Y(80), X(z_rim1 + 22), Y(96)),
    "SH-301": (X(225), Y(8), X(232), Y(60)),
    key_c_code: (X(S.Z_CPL + 12), Y(-2), X(232), Y(-60)),
    "BRG-6207": (X(S.Z_BRG_B + 4), Y(-26), X(170), Y(-80)),
    "KEY-12x8x45": (X(S.Z_GEAR + 8), Y(-2), X(z_rim1 + 22), Y(-96)),
    "sleeve": (X((z_sl[0] + z_sl[1]) / 2), Y(-19.5), X(-10), Y(-80)),
}
for code, (px, py, tx, ty) in balloon.items():
    n = no_sleeve if code == "sleeve" else no_of[code]
    ax.plot([px], [py], "o", ms=1.6, color=H.INK)
    sh.raw_line((px, py), (tx, ty))
    sh.raw_line((tx, ty), (tx + 9 * (1 if tx >= px else -1), ty))
    sh.text(tx + 4.5 * (1 if tx >= px else -1), ty + 0.6, str(n), size=FS * 1.3)

# ---- Parts list (above the title block, item numbers from bottom to top)
x1, yt = 415.0, 5.0 + 32.0
cols = [("no", T("序号", "No."), 9), ("code", T("代号", "Code"), 27), ("name", T("名称", "Name"), 36), ("qty", T("数量", "Qty"), 9),
        ("mat", T("材料", "Material"), 20), ("std", T("标准", "Standard"), 21), ("chg", T("备注", "Note"), 18)]
wsum = sum(c[2] for c in cols)
xs0 = x1 - wsum
rh = 7.0
allrows = [None] + rows                        # Row 0 is the header (at the bottom)
for i, r in enumerate(allrows):
    y = yt + i * rh
    ax.add_patch(H.Polygon([(xs0, y), (x1, y), (x1, y + rh), (xs0, y + rh)], closed=True, fill=False, lw=0.45, ec=H.INK))
    xx = xs0
    for key, head, w in cols:
        if r is None:
            val = head
        elif key == "name":
            val = T(r["name"][0], re.sub(r"\d+×\d+×\d+ (?=\d{4})", "", (r["name"][1] or r["name"][0]).replace("Parallel key", "Key")))
        elif key == "chg":
            val = {T("改", "chg."): T("B 版改", "changed"), T("新", "new"): T("B 版新增", "added")}.get(r.get("chg"), "")
        else:
            val = str(r.get(key, ""))
        sh.text(xx + w / 2, y + rh / 2, val, size=FS * T(0.78, 0.7), va="center", color=H.MUTED if r is None else H.INK)
        sh.raw_line((xx + w, y), (xx + w, y + rh))
        xx += w
sh.title_block(415, 5, {"name": T("输出轴组件", "Shaft assembly"), "material": "—", "drawn": T("问渠教材", "WenQuest"), "checked": "—",
                        "scale": "1:1", "qty": "1", "date": "2026-10", "rev": "B", "no": "SA-300", "org": T("问渠数字工厂", "WenQuest factory"),
                        "title": "SA-300"})
notes = [T("技术要求", "Technical requirements"),
         T("1. 齿轮与轴为过盈配合，热装（加热齿轮），不得锤击。", "1. Gear on shaft with interference: shrink fit (heat the gear), no hammering."),
         T("2. 轴承内圈靠紧轴肩和套筒，不得有间隙。", "2. Bearing inner rings tight against shoulder and sleeve, no gap."),
         T("3. 装配后用手转动输出轴，转动灵活、无卡滞；出厂时在跑合试验台上检查空载温升和噪声。", "3. Shaft turns freely by hand; no-load heat and noise checked on the run-in bench.")]
for i, t in enumerate(notes):
    sh.text(30, 29 - i * 6.5, t, size=FS * (1.05 if i == 0 else 0.95), ha="left", va="center", weight="bold" if i == 0 else "normal")
fig.subplots_adjust(0, 0, 1, 1)
figure(fig, "fig3_5_1")

out(L=S.LEN_B, n_rows=len(rows), n_bom=len(F.BOMS["SA-300"][1]), key_c=key_c_code, L_kc=L_kc, L_kg=L_kg, span=S.SPAN, d_a=d_a, d_f=d_f, d_p=d_p,
    sleeve_od=SLEEVE_OD, sleeve_L=z_sl[1] - z_sl[0], da_min=brg["da_min"], no_sleeve=no_sleeve, no_brg=no_of["BRG-6207"])
