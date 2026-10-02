# Fig. 15-3 (English): needle-point height and the template movement window.
import numpy as np
from scipy.optimize import brentq
from en_ch15_style import *

r, l = 15.5, 55.0; lam = r / l
def h(deg):
    p = np.radians(deg)
    return 18 - (r * (1 - np.cos(p)) - l * (1 - np.sqrt(1 - lam**2 * np.sin(p)**2)))
def entry(t): return brentq(lambda d: h(d) - t, 0, 180)
e15, e6 = entry(1.5), entry(6)      # 101.7, 85.2
x15, x6 = 360 - e15, 360 - e6       # 258.3, 274.8

fig = figure(844 / 1344)
header(fig, 'The template may move only while the needle is out of the fabric: 203° at 1.5 mm, only 170° at 6 mm',
       'Height of the needle point above the throat plate; Chapter 3 worked example r = 15.5 mm, l = 55 mm; the needle point is 18 mm above the throat plate at TDC')
ax = fig.add_axes([0.145, 0.184, 0.802, 0.669])
clean(ax, bottom=False)
ax.set_xlim(0, 360); ax.set_ylim(-14, 22)
ax.axvspan(0, e15, color=WIN, lw=0, zorder=0.2); ax.axvspan(x15, 360, color=WIN, lw=0, zorder=0.2)
ax.axvspan(e15, x15, color=STILL, lw=0, zorder=0.2)
ax.axhspan(0, 1.5, color=FABRIC, alpha=0.85, lw=0, zorder=0.3)
ax.axhline(0, color=AXIS, lw=1)
phi = np.linspace(0, 360, 721)
ax.plot(phi, h(phi), color=INK, lw=2.2)
pts = np.arange(0, 361, 10); ax.plot(pts, h(pts), 'o', color=INK, ms=3.5)
ax.axhline(6, color=ORANGE, lw=1.8, ls=(0, (5, 3)))
ax.text(355, 6.4, 'Fabric surface t = 6 mm', color=ORANGE, ha='right', va='bottom', fontsize=10.5)
ax.text(355, 1.9, 'Fabric surface t = 1.5 mm', color=INK, ha='right', va='bottom', fontsize=10.5)
ax.text(355, -0.7, 'Throat-plate surface', color=MUTED, ha='right', va='top', fontsize=10.5)
ax.text(e15 / 2, 21.0, 'Template may move', color=BLUE, ha='center', va='center', fontweight='bold', fontsize=11)
ax.text((x15 + 360) / 2, 21.0, 'Template may move', color=BLUE, ha='center', va='center', fontweight='bold', fontsize=11)
ax.text(180, 21.0, 'Needle in fabric: template must be stationary', color=MUTED, ha='center', va='center', fontsize=11)
ax.set_yticks([-10, 0, 10, 20])
ax.set_xticks([0, 90, 180, 270, 360]); ax.set_xticklabels(['0°', '90°', '180°', '270°', '360°'])
ax.tick_params(axis='x', pad=50)
for xv, yv, c in [(e6, 6, ORANGE), (x6, 6, ORANGE), (e15, 1.5, BLUE), (x15, 1.5, BLUE)]:
    ax.plot([xv, xv], [-14, yv], color=c, lw=1, ls=(0, (2, 2)), clip_on=False)
    ax.plot([xv, xv], [-14, -15.6], color=c, lw=1, ls=(0, (2, 2)), clip_on=False)
ax.text(e6 - 2, -16.3, f'{e6:.1f}°', color=ORANGE, ha='right', va='center')
ax.text(e15 + 2, -16.3, f'{e15:.1f}° entry', color=BLUE, ha='left', va='center')
ax.text(x15 - 2, -16.3, f'{x15:.1f}° exit', color=BLUE, ha='right', va='center')
ax.text(x6 + 2, -16.3, f'{x6:.1f}°', color=ORANGE, ha='left', va='center')
ylabel(fig, ax, 'Needle-point\nheight', 'mm', yfrac=0.55)
fig.text(0.032, 0.093, 'Main-shaft angle φ', fontsize=10.5, color=MUTED, va='center')
foot(fig, ['The window spans top dead centre (360° = 0°): it runs from the exit angle to the entry angle of the next stitch'], 0.05)
save(fig, 'w_85b283fd')
