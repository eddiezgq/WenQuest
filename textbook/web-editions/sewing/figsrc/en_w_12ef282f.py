# Fig. 15-7 (English): stitch breakdown of a bartack, a sewn-on button and a straight-end buttonhole.
# Drawn in the original's pixel frame (1344 x 720), 25 px/mm.
import numpy as np
from matplotlib.patches import Circle
from en_ch15_style import *

PW, PH = 1344, 720
fig = figure(PH / PW)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, PW); ax.set_ylim(PH, 0); ax.set_axis_off()
def txt(x, y, s, **kw):
    kw.setdefault('color', INK); kw.setdefault('fontsize', 10.5); kw.setdefault('va', 'center'); ax.text(x, y, s, **kw)
DARK = '#3a3936'
txt(42, 42, 'Bartacks, buttons and buttonholes are all “fixed patterns”: few parameters, few stitches, the same job repeated',
    fontsize=14, fontweight='bold')
txt(42, 77, 'Drawn to scale; the figures are typical settings and can be adjusted in practice', color=MUTED)
K = 25.0
# --- bartack: L = 10 mm, W = 2 mm, N1 = 6 underlay, N2 = 28 cover (parametric formulas of Section 15.7)
L, Wb, N1, N2 = 10, 2, 6, 28; X0, YC = 105, 193
j = np.arange(N1 + 1); ux = X0 + K * j * L / N1; uy = YC + K * np.where(j % 2 == 0, -0.3, 0.3) * Wb
k = np.arange(N2 + 1); cx = X0 + K * (L - k * L / N2); cy = YC + K * np.where(k % 2 == 0, -0.5, 0.5) * Wb
ax.plot(ux, uy, color=ORANGE, lw=2.2, zorder=2)
ax.plot(cx, cy, '-o', color=BLUE, lw=1.6, ms=3.6, zorder=3)
txt(230, 127, 'Bartack (reinforcing)', ha='center', fontweight='bold', fontsize=11)
txt(106, 276, '① Underlay: 6 stitches along the length', color=ORANGE)
txt(106, 308, '② Cover: dense zigzag of 28 stitches back', color=BLUE)
txt(106, 340, 'Length 10 mm, width 2 mm, about 36 stitches', color=DARK)
txt(106, 372, 'Motion: X–Y stepper table moves the clamp', color=DARK)
# --- button, four holes, parallel; hole spacing 3.6 mm
BC = (636, 195); d = 3.6 * K / 2
ax.add_patch(Circle(BC, 90, fill=False, ec='#c8c6bc', lw=2.5))
holes = [(BC[0] - d, BC[1] - d), (BC[0] + d, BC[1] - d), (BC[0] - d, BC[1] + d), (BC[0] + d, BC[1] + d)]
for h in holes: ax.add_patch(Circle(h, 13, fill=False, ec='#c8c6bc', lw=1.6))
ax.plot([holes[0][0], holes[1][0]], [holes[0][1] - 2, holes[1][1] - 2], color=BLUE, lw=2.6)
ax.plot([holes[2][0], holes[3][0]], [holes[2][1] - 2, holes[3][1] - 2], color=BLUE, lw=2.6)
ax.plot([holes[1][0], holes[2][0]], [holes[1][1], holes[2][1]], color=GREEN, lw=1.8, ls=(0, (3, 3)))
txt(BC[0], 127, 'Button (four holes, parallel)', ha='center', fontweight='bold', fontsize=11,
    bbox=dict(boxstyle='square,pad=0.15', fc=BG, ec='none'))
txt(512, 322, '8 stitches back and forth between each pair of holes', color=BLUE)
txt(512, 354, 'Dashed: move across to the other pair (needle up)', color=GREEN)
txt(512, 386, 'Hole spacing 3.6 mm; the clamp holds the button', color=DARK)
txt(512, 418, 'Motion: X–Y table moves the button clamp', color=DARK)
# --- straight-end buttonhole: eye length 12 mm
HX, Y1, Y2 = 990, 125, 425
txt(HX, 63, 'Straight-end buttonhole', ha='center', fontweight='bold', fontsize=11)
yy = np.arange(Y1, Y2 + 0.1, 10)
lx = np.where(np.arange(len(yy)) % 2 == 0, HX - 42, HX - 4); rx = np.where(np.arange(len(yy)) % 2 == 0, HX + 42, HX + 4)
ax.plot(lx, yy, color=BLUE, lw=1.4); ax.plot(rx, yy, color=BLUE, lw=1.4)
ax.plot([HX, HX], [Y1 + 5, Y2 - 13], color=GREEN, lw=3)
bx = np.linspace(HX - 40, HX + 40, 9)
ax.plot(bx, np.where(np.arange(9) % 2 == 0, 108, 96), color=ORANGE, lw=1.8)
ax.plot(bx, np.where(np.arange(9) % 2 == 0, 434, 446), color=ORANGE, lw=1.8)
for i, (s_, c) in enumerate([('① Left row: zigzag, downwards', BLUE), ('② Bottom bartack', ORANGE),
                             ('③ Right row: zigzag, upwards', BLUE), ('④ Top bartack', ORANGE),
                             ('⑤ Knife cuts it open (centre line)', GREEN)]):
    txt(1078, 170 + 32 * i, s_, color=c)
txt(1078, 350, 'Eye length 12 mm', color=DARK)
txt(1078, 382, 'Motion: needle-bar swing + feed', color=DARK)
# --- common points
txt(42, 524, 'Common ground: each is “sewing head + relative motion in two directions + one on/off action”; the out-of-fabric window of Section 15.3 applies too',
    color=INK, fontsize=10.5)
txt(42, 560, 'Bartacks and buttons move the fabric (X–Y table); buttonholes move the needle in one direction (needle-bar swing) and the fabric in the other (feed)', color=MUTED)
txt(42, 596, 'Each zigzag stitch moves sideways by the zigzag width (1.5–2.5 mm) but advances only 0.3–0.5 mm; the speed limit is set by the sideways travel', color=MUTED)
txt(42, 628, 'and the mass of the parts that move sideways', color=MUTED)
save(fig, 'w_12ef282f')
