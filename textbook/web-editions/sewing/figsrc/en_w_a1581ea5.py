# Fig. 15-4 (English): stitch length versus upper speed limit.
import numpy as np
from scipy.optimize import brentq
from en_ch15_style import *

r, l = 15.5, 55.0; lam = r / l
def h(deg):
    p = np.radians(deg)
    return 18 - (r * (1 - np.cos(p)) - l * (1 - np.sqrt(1 - lam**2 * np.sin(p)**2)))
def window(t):
    e = brentq(lambda d: h(d) - t, 0, 180); return 360 - (360 - 2 * e)
a, v = 50.0, 1.0
def tmove(s_mm):
    s = s_mm / 1000
    return np.where(s <= v * v / a, 2 * np.sqrt(s / a), s / v + v / a)
def nmax(s_mm, t, diag=False):
    return window(t) / (6 * tmove(s_mm / np.sqrt(2) if diag else s_mm))
S = np.array([1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12])

fig = figure(826 / 1344)
header(fig, 'Stitch length from 3 mm to 12 mm: the speed limit falls from about 2200 to about 1100 r/min',
       'Per-axis acceleration 50 m/s², maximum velocity 1 m/s, triangular velocity profile; n_max = W / (6 t_move), W = out-of-fabric window (°)')
ax = fig.add_axes([0.132, 0.186, 0.684, 0.618])
clean(ax)
ax.set_xlim(0, 12); ax.set_ylim(0, 4600)
ax.set_yticks([0, 1000, 2000, 3000, 4000]); ax.set_xticks(range(0, 13, 2))
ax.axhline(2800, color=INK, lw=1.4, ls=(0, (1.5, 2.5)))
ax.text(11.8, 2860, 'Head’s mechanical maximum 2800 (example value)', color=INK, ha='right', va='bottom')
nd = nmax(S, 1.5, True); n15 = nmax(S, 1.5); n6 = nmax(S, 6)
ax.plot(S, nd, '--o', color=GREEN, lw=1.8, ms=4.5, clip_on=False)
ax.plot(S, n15, '-o', color=BLUE, lw=2.6, ms=4.5, clip_on=False)
ax.plot(S, n6, '-o', color=ORANGE, lw=2.2, ms=4.5, clip_on=False)
ax.text(12.2, nd[-1], f'45° diagonal {nd[-1]:.0f}', color=GREEN, va='center')
ax.text(12.2, n15[-1] - 40, f't = 1.5 mm {n15[-1]:.0f}', color=BLUE, va='center')
ax.text(12.2, n6[-1] - 70, f't = 6 mm {n6[-1]:.0f}', color=ORANGE, va='center')
ax.text(3.1, 2330, f'3 mm → {n15[3]:.0f}', color=BLUE, ha='left', va='center', fontweight='bold', fontsize=11)
ax.set_xlabel('Stitch length s (mm)', color=MUTED, labelpad=12, fontsize=10.5)
ylabel(fig, ax, 'Speed limit', 'r/min', yfrac=0.70)
foot(fig, ['Solid lines: one stitch along the X or Y axis alone; dashed line: one stitch at 45°, each axis travelling s/√2, which is actually faster (t = 1.5 mm)'], 0.07)
print(np.round(n15), np.round(n6), np.round(nd))
save(fig, 'w_a1581ea5')
