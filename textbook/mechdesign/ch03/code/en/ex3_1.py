"""Section 3.1 Orthographic projection and three views: the pillow block (6207) of the palletizing conveyor, with three views projected from the 3D model; first-angle and third-angle projection compared (Figures 3.1.1, 3.1.2)."""
import _ch3 as H
from bookout import T, figure, out, style

p = H.pillow_params("6207")
solid = H.pillow_block(p)
V = {k: H.project(solid, k) for k in ("front", "top", "left", "right", "iso")}
GAP = 22.0


def place(sh, view, dx, dy):
    vis, hid = V[view]
    sh.polys(hid, "hidden", dx, dy)
    sh.polys(vis, "thick", dx, dy)


def centers(sh, view, dx, dy):
    """Center lines: the axis of the bearing bore and the center lines of the anchor-bolt holes and the oil hole (positions from the parameters, extending about 3 mm beyond the outline)"""
    L, Wb, H_, D, Ro = p["L"], p["Wb"], p["H"], p["D"], p["Ro"]
    c = []
    if view == "front":
        c += [((-Ro - 4, H_), (Ro + 4, H_)), ((0, H_ - Ro - 4), (0, H_ + Ro + 4))]
        c += [((x, -3), (x, p["tb"] + 3)) for x in (-p["Lh"] / 2, p["Lh"] / 2)]
    elif view == "top":
        c += [((0, -Wb / 2 - 4), (0, Wb / 2 + 4)), ((-Ro - 4, 0), (Ro + 4, 0))]
        for x in (-p["Lh"] / 2, p["Lh"] / 2):
            c += [((x - p["dh"] / 2 - 3, 0), (x + p["dh"] / 2 + 3, 0)), ((x, -p["dh"] / 2 - 3), (x, p["dh"] / 2 + 3))]
    else:
        c += [((-Wb / 2 - 4, H_), (Wb / 2 + 4, H_))]
    for a, b in c:
        sh.line((dx + a[0], dy + a[1]), (dx + b[0], dy + b[1]), "center")


plt = style()
# ---- Figure 3.1.1: pictorial view + three views in first-angle projection (front view, top view below, left view on the right), with construction lines for "length aligned, height level, width equal"
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.2, 3.9), gridspec_kw={"width_ratios": [0.8, 1.4]})
s0 = H.Sheet(a0)
s0.polys(V["iso"][0], "thick")
a0.set_title(T("轴承座（6207 用）的三维模型", "Pillow block (for a 6207) — 3D model"), fontsize=8.5)
s1 = H.Sheet(a1)
fb, tb_, lb = (H.bbox(V[k][0]) for k in ("front", "top", "left"))
top_dy = fb[1] - GAP - tb_[3]                           # Top view directly below the front view: x aligned (length aligned)
left_dx = fb[2] + GAP - lb[0]                            # Left view directly to the right of the front view: z aligned (height level)
place(s1, "front", 0, 0)
place(s1, "top", 0, top_dy)
place(s1, "left", left_dx, 0)
centers(s1, "front", 0, 0)
centers(s1, "top", 0, top_dy)
centers(s1, "left", left_dx, 0)
blue = "#2c6fbb"
for x in (fb[0], fb[2]):                                 # Length aligned
    s1.raw_line((x, fb[1] - 2), (x, top_dy + tb_[3] + 2), color=blue)
for z in (fb[3], p["H"]):                                # Height level
    s1.raw_line((fb[2] + 2, z), (left_dx + lb[0] - 2, z), color=blue)
# Width equal: the width (Y) in the top view is carried to the left view through the 45° line: horizontal from the top view to the 45° line, then vertically up to the left view (u = -Y in the left view)
kk = left_dx + top_dy                                    # 45° line: x + y = kk (through the intersection of the two corresponding lines at Y = 0)
for yv in (tb_[1], tb_[3]):
    yy, xx = top_dy + yv, left_dx - yv
    s1.raw_line((tb_[2] + 2, yy), (xx, yy), color=blue)
    s1.raw_line((xx, yy), (xx, lb[1] - 2), color=blue)
s1.raw_line((left_dx - tb_[3] - 6, top_dy + tb_[3] + 6), (left_dx - tb_[1] + 6, top_dy + tb_[1] - 6), color=blue)
ox, oy = left_dx - tb_[1] + 6, top_dy + tb_[1] - 6
lab = dict(size=7.5, va="top")
s1.text((fb[0] + fb[2]) / 2, fb[1] - 3.5, T("主视图", "Front view"), **lab)
s1.text((tb_[0] + tb_[2]) / 2, top_dy + tb_[1] - 3, T("俯视图", "Top view"), **lab)
s1.text(left_dx + (lb[0] + lb[2]) / 2, lb[1] - 3.5, T("左视图", "Left view"), **lab)
s1.text(fb[0] - 2, (fb[1] + top_dy + tb_[3]) / 2, T("长对正", "length aligned"), size=7, ha="right", va="center", color=blue)
s1.text(fb[2] + GAP / 2, fb[3] + 2, T("高平齐", "height aligned"), size=7, color=blue)
s1.text(ox + 2, oy, T("宽相等", "width equal"), size=7, ha="left", va="center", color=blue)
a1.set_title(T("第一角画法的三视图（GB、ISO 欧洲）", "Three views, first-angle projection (GB, ISO Europe)"), fontsize=8.5)
for a in (a0, a1):
    a.autoscale()
    a.margins(0.04)
fig.tight_layout()
figure(fig, "fig3_1_1")

# ---- Figure 3.1.2: the same part, view positions in first-angle and third-angle projection; projection symbol
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.3))
for k, (ax, mode) in enumerate(zip(axs, ("first", "third"))):
    sh = H.Sheet(ax, scale=1.0)
    place(sh, "front", 0, 0)
    centers(sh, "front", 0, 0)
    if mode == "first":
        place(sh, "top", 0, top_dy)
        centers(sh, "top", 0, top_dy)
        place(sh, "left", left_dx, 0)
        centers(sh, "left", left_dx, 0)
        names = [(0, top_dy + tb_[1] - 3, T("俯视图（在下）", "Top view (below)")), (left_dx + (lb[0] + lb[2]) / 2, lb[1] - 3.5, T("左视图（在右）", "Left view (on the right)"))]
    else:
        up_dy = fb[3] + GAP - tb_[1]
        rb = H.bbox(V["right"][0])
        rdx = fb[2] + GAP - rb[0]
        place(sh, "top", 0, up_dy)
        place(sh, "right", rdx, 0)
        names = [(0, up_dy + tb_[3] + 8, T("俯视图（在上）", "Top view (above)")), (rdx + (rb[0] + rb[2]) / 2, rb[1] - 3.5, T("右视图（在右）", "Right view (on the right)"))]
    sh.text(0, fb[1] - 3.5, T("主视图", "Front view"), size=7.5, va="top")
    for x, y, t in names:
        sh.text(x, y, t, size=7.5, va="top")
    # Projection symbol (GB/T 14692, ISO 128): two views of a truncated cone
    sx, sy = 120, -95 if mode == "first" else -40
    cone_side = [(-8, -2.2), (8, -4), (8, 4), (-8, 2.2), (-8, -2.2)]      # Truncated cone: small end to the left (both concentric circles solid: the view looks at the small end)
    circ = __import__("numpy").linspace(0, 6.2832, 60)
    import numpy as np
    if mode == "first":
        side_x, circ_x = sx, sx + 22
    else:
        side_x, circ_x = sx + 22, sx
    sh.polys([[(side_x + u, sy + v) for u, v in cone_side]], "thick")
    sh.polys([[(circ_x + 4 * np.cos(t), sy + 4 * np.sin(t)) for t in circ], [(circ_x + 2.2 * np.cos(t), sy + 2.2 * np.sin(t)) for t in circ]], "thick")
    sh.line((side_x - 11, sy), (side_x + 11, sy), "center")
    sh.line((circ_x - 7, sy), (circ_x + 7, sy), "center")
    sh.text(sx + 11, sy - 9, T("识别符号", "Projection symbol"), size=7, va="top")
    ax.set_title(T("第一角画法（GB/T 14692、ISO 5456-2）", "First-angle (GB/T 14692, ISO 5456-2)") if mode == "first" else
                 T("第三角画法（ASME Y14.3、JIS）", "Third-angle (ASME Y14.3, JIS)"), fontsize=8.5)
    ax.autoscale()
    ax.margins(0.04)
fig.tight_layout()
figure(fig, "fig3_1_2")

out(L=p["L"], Wb=p["Wb"], W=p["W"], H=p["H"], D=p["D"], D2=p["D2"], Ro=p["Ro"], tb=p["tb"], Lh=p["Lh"], dh=p["dh"], bolt=p["bolt"],
    Htot=p["H"] + p["Ro"], n_vis=len(V["front"][0]), n_hid=len(V["front"][1]), vol=solid.volume / 1000)
