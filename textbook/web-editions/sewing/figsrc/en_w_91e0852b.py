# Fig. 15-6 (English): from outline to stitch points (pocket-flap example).
# Drawn in the original's pixel frame (1344 x 684); geometry in mm, 7.08 px/mm, origin = bottom-left of the stitch line.
import numpy as np, math
from matplotlib.patches import FancyArrowPatch, Rectangle
from en_ch15_style import *

PW, PH = 1344, 684
fig = figure(PH / PW)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, PW); ax.set_ylim(PH, 0); ax.set_axis_off()
K, OX, OY = 7.08, 176, 424
P = lambda x, y: (OX + K * x, OY - K * y)
def txt(x, y, s, **kw):
    kw.setdefault('color', INK); kw.setdefault('fontsize', 10.5); kw.setdefault('va', 'center')
    ax.text(x, y, s, **kw)

txt(42, 42, 'Pattern data is just a string of stitch points plus commands: divide the outline by equal arc length,', fontsize=14.5, fontweight='bold')
txt(42, 70, 'with a stitch at every corner', fontsize=14.5, fontweight='bold')
txt(42, 100, 'Pocket-flap outline 60 × 40 mm, R10 corners, target stitch length 3 mm; each segment divided equally, so the actual stitch length is slightly under 3 mm', color=MUTED, fontsize=10)

# stitch points of the U-shaped outline: left side down, bottom-left arc, bottom, bottom-right arc, right side up
s, R, W, Hh = 3.0, 10.0, 60.0, 40.0
pts, ends = [], []
def line(p0, p1):
    L = math.dist(p0, p1); n = math.ceil(L / s - 1e-9)
    for i in range(n + (0 if pts else 1)) if False else range(1 if pts else 0, n + 1):
        pts.append((p0[0] + (p1[0] - p0[0]) * i / n, p0[1] + (p1[1] - p0[1]) * i / n))
    ends.append(p1)
def arc(c, a0, a1):
    L = R * abs(a1 - a0); n = math.ceil(L / s - 1e-9)
    for i in range(1, n + 1):
        a = a0 + (a1 - a0) * i / n; pts.append((c[0] + R * math.cos(a), c[1] + R * math.sin(a)))
    ends.append(pts[-1])
line((0, Hh), (0, R)); arc((R, R), math.pi, 1.5 * math.pi); line((R, 0), (W - R, 0))
arc((W - R, R), 1.5 * math.pi, 2 * math.pi); line((W, R), (W, Hh))
ends = ends[:-1]                          # last 'end' is the trim point itself
xy = np.array([P(*p) for p in pts])
# sewing area inside the template
ax.add_patch(Rectangle(P(-4, 42.4), K * 68, K * 46.4, fill=False, ec='#bdbdbd', lw=1.3, ls=(0, (4, 3))))
txt(P(-3.2, -4)[0], P(0, -6.3)[1], 'Sewing area inside the template', color=MUTED, fontsize=10)
ax.plot(xy[:, 0], xy[:, 1], color=BLUE, lw=2.0, zorder=2)
ax.plot(xy[1:-1, 0], xy[1:-1, 1], 'o', color=BLUE, ms=4.2, zorder=3)
for e in ends:
    ax.plot(*P(*e), 'o', ms=15, mfc='none', mec=GREEN, mew=2, zorder=4)
ax.plot(*P(W, Hh), 'o', ms=15, mfc='none', mec=GREEN, mew=2, zorder=4)
ax.plot(*P(0, Hh), 'D', color=ORANGE, ms=13, zorder=5)
ax.plot(*P(W, Hh), 's', color=INK, ms=11, zorder=5)
txt(P(0, Hh)[0] - 18, P(0, Hh)[1] - 12, 'Start', ha='right')
txt(P(W, Hh)[0] + 16, P(W, Hh)[1] - 10, 'Trim', ha='left')
# section 2: decorative zigzag, sewn right to left
zx = np.linspace(15.3, 45.1, 11); zy = np.where(np.arange(11) % 2 == 0, 20.5, 24.4)
zz = np.array([P(x, y) for x, y in zip(zx, zy)])
ax.plot(zz[:, 0], zz[:, 1], color=BLUE, lw=2.0, zorder=2)
ax.plot(zz[1:, 0], zz[1:, 1], 'o', color=BLUE, ms=4.2, zorder=3)
ax.plot(*zz[0], 's', color=INK, ms=11, zorder=5)
txt(zz[0][0] - 10, P(0, 15.6)[1], 'Section 2: decorative line', color=MUTED, ha='left')
txt(zz[0][0] - 10, P(0, 15.6)[1] + 22, '(sewn in reverse direction)', color=MUTED, ha='left')
# jump
ax.add_patch(FancyArrowPatch(P(W - 1, Hh - 1), (zz[-1][0] + 2, zz[-1][1] - 8), connectionstyle='arc3,rad=0.28',
                             arrowstyle='-|>,head_length=9,head_width=5', color=ORANGE, lw=2, ls=(0, (3, 2)), zorder=4))
txt(P(47.2, 33)[0] - 6, P(0, 33.3)[1], 'Jump', color=ORANGE, ha='right')
# legend
LX, TX = 742, 768
ax.plot(LX, 162, 'o', color=BLUE, ms=6.5); txt(TX, 162, 'SEW: one stitch; ΔX, ΔY relative to the previous stitch', fontsize=11)
ax.plot(LX, 215, 'D', color=ORANGE, ms=11); txt(TX, 215, 'Start: slow + 2–3 backtack stitches against unravelling', fontsize=11)
ax.plot(LX, 268, 's', color=INK, ms=10); txt(TX, 268, 'TRIM: slow down 1–2 stitches beforehand', fontsize=11)
ax.plot([LX - 12, LX + 12], [328, 328], color=ORANGE, lw=2, ls=(0, (3, 2))); txt(TX, 328, 'JUMP: main shaft parked at needle-up', fontsize=11)
ax.plot(LX, 385, 'o', ms=15, mfc='none', mec=GREEN, mew=2); txt(TX, 385, 'Segment end: a stitch always falls where a line meets an arc', fontsize=11)
txt(725, 457, 'Other commands: PAUSE (pause), PRESS (intermediate-foot height),', color=MUTED)
txt(725, 488, 'TENS (tension), SPEED (speed limit), OUT (valve output), END (end)', color=MUTED)
txt(42, 578, 'For each segment compute the length L, stitches n = ⌈L / 3⌉ and actual stitch length L / n; so a 30 mm straight gets 10 stitches and an R10 corner', color=MUTED)
txt(42, 610, '(arc length 15.7 mm) gets 6 stitches of 2.6 mm each. Schematic drawn to scale', color=MUTED)
print(len(pts), 'points')
save(fig, 'w_91e0852b')
