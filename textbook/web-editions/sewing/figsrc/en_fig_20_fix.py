"""English version of fig_20_fix (Fig. 23-7). Recomputed with the single-DOF arm model of ch23 / tol.html page B."""
import math, numpy as np
from en__lib_ch18_23 import *
from en__tolsim import vib, noise

cases = [('Original\n5000 r/min', dict(n=5000)), ('Original\n5500 r/min', dict(n=5500)),
         ('Ribs, walls\nstiffness +30%', dict(n=5500, fn=190 * math.sqrt(1.3))),
         ('Damping\nζ = 0.06', dict(n=5500, z=0.06)), ('Damping\nζ = 0.10', dict(n=5500, z=0.10)),
         ('Recip. mass\n−20%', dict(n=5500, m=0.8)), ('Recip. mass\n−40%', dict(n=5500, m=0.6))]
labs = [c[0] for c in cases]
v = [vib(**c[1])[1] for c in cases]
L = [noise(**c[1]) for c in cases]


def chart(vals, lim, ylim, yt, ylabel, name, limtxt=None):
    fig = panel_fig(820, 470)
    ax = fig.add_axes([0.09, 0.17, 0.89, 0.78])
    x = np.arange(len(vals))
    cols = [BAR_GREEN if round(val, 1) <= lim else BAR_RED for val in vals]
    ax.bar(x, [val - ylim[0] for val in vals], bottom=ylim[0], width=0.6, color=cols)
    for xi, val in zip(x, vals):
        ax.text(xi, val + (ylim[1] - ylim[0]) * 0.015, f'{val:.1f}', ha='center', va='bottom', fontsize=10.5, weight='bold', color=INK)
    ax.axhline(lim, color=RED, lw=1, ls=(0, (4, 3)))
    if limtxt:
        ax.text(-0.45, ylim[1] - (ylim[1] - ylim[0]) * 0.04, limtxt, color=RED, fontsize=10, weight='bold', va='top')
    ax.set_xticks(x); ax.set_xticklabels(labs, fontsize=9.5)
    ax.set_ylim(*ylim); ax.set_yticks(yt); ax.set_xlim(-0.6, len(vals) - 0.4)
    ax.grid(axis='x', visible=False); ax.set_ylabel(ylabel)
    return save_panel(fig, name)


pa = chart(v, 8, (0, 15), range(0, 16, 5), 'Vibration velocity (mm/s)', 'fig_20_fix_a.png')
pb = chart(L, 86, (70, 100), range(70, 101, 10), 'Noise dB(A)', 'fig_20_fix_b.png', 'Dashed line: limit 86 dB(A) (illustrative)')

body = f'''<p class="title">Effect of the three remedies at 5500 r/min</p>
<p class="sub">Worked example (illustrative values); left: RMS vibration velocity; right: estimated workstation noise (about +6 dB for each doubling of vibration)</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px"><img class="pimg" src="{pa}"><img class="pimg" src="{pb}"></div>
<p class="note" style="color:#1b2430;font-size:13.5px;margin-top:20px">Moving the natural frequency out of the working speed range (ribs and thicker walls) works best; damping acts only near resonance, and weight reduction has to be very large to be enough, so both serve as supporting measures.</p>'''
print(page('fig_20_fix', body))
