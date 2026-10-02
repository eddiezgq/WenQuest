"""English version of fig_20_sweep (Fig. 23-6). Recomputed with the single-DOF arm model of ch23 / tol.html page B."""
import numpy as np
from en__lib_ch18_23 import *
from en__tolsim import vib, noise

n = np.arange(2000, 6501, 5)
tot = np.array([vib(x)[1] for x in n]); o1 = np.array([vib(x)[0][0]['v'] for x in n]); o2 = np.array([vib(x)[0][1]['v'] for x in n])
npk = n[np.argmax(tot)]
fig = panel_fig(1000, 480)
ax = fig.add_axes([0.085, 0.13, 0.90, 0.80])
ax.set_title('a    Speed sweep', pad=10)
ax.plot(n, o1, color=BLUE, lw=1.4, ls=(0, (5, 3)))
ax.plot(n, o2, color=ORANGE, lw=1.4, ls=(0, (2, 1.5)))
ax.plot(n, tot, color=INK, lw=2.2)
ax.axhline(8, color=RED, lw=1, ls=(0, (4, 3)))
ax.text(2050, 8.4, 'Limit 8 mm/s (illustrative)', color=RED, fontsize=10.5, weight='bold')
ax.text(2300, 22.2, 'Solid: total    dashed: first order    dotted: second order', color=MUTED, fontsize=10)
ax.text(npk, 23.4, f'Second-order resonance {round(npk, -2):.0f} r/min', color=ORANGE, fontsize=10.5, weight='bold', ha='center')
for sp, col, dx, dy in [(5000, GREEN, -60, 0.4), (5500, RED, -60, 0.6)]:
    vv = vib(sp)[1]
    ax.plot([sp], [vv], 'o', color=col, ms=9, zorder=5)
    ax.text(sp + dx, vv + dy, f'{sp}: {vv:.1f} mm/s, {noise(sp):.1f} dB(A)', color=col, fontsize=10.5, weight='bold', ha='right')
ax.set_xlim(2000, 6500); ax.set_ylim(0, 25); ax.set_xticks(range(2000, 6001, 1000))
ax.set_xlabel('Speed (r/min)'); ax.set_ylabel('RMS vibration velocity of the head (mm/s)')
pa = save_panel(fig, 'fig_20_sweep_a.png')

fig = panel_fig(700, 480)
ax = fig.add_axes([0.10, 0.13, 0.86, 0.80])
ax.set_title('b    Spectrum: the second-order component is what grew', pad=10)
for sp, col, lab in [(5000, BAR_GREEN, False), (5500, BAR_RED, True)]:
    for o in vib(sp)[0]:
        ax.bar(o['f'], o['v'], width=8, color=col)
    o = vib(sp)[0][1]
    ax.text(o['f'] + (3 if lab else 0), o['v'] + 0.25, f"{o['v']:.1f}", ha='right' if lab else 'center', fontsize=10.5, weight='bold', color=RED if lab else GREEN)
ax.axvline(190, color=GOLD, lw=1.2, ls=(0, (4, 3)))
ax.text(194, 14.6, 'Arm natural\nfrequency 190 Hz', color=GOLD, fontsize=10.5, weight='bold', va='top')
ax.text(20, 14.3, 'Green: 5000 r/min\nRed: 5500 r/min', color=MUTED, fontsize=10, va='top')
ax.set_xlim(0, 300); ax.set_ylim(0, 15); ax.set_yticks(range(0, 16, 5))
ax.set_xlabel('Frequency (Hz)'); ax.set_ylabel('Vibration velocity (mm/s)')
pb = save_panel(fig, 'fig_20_sweep_b.png')

body = f'''<p class="title">Case study: at 5500 r/min the second-order excitation runs into the arm’s natural frequency</p>
<p class="sub">Worked example (illustrative values): arm natural frequency 190 Hz, damping ratio 0.03; at 5000 r/min the first-order residual force is 300 N and the second-order force 120 N, both proportional to the square of the speed</p>
<div style="display:grid;grid-template-columns:1000fr 700fr;gap:0"><img class="pimg" src="{pa}"><img class="pimg" src="{pb}"></div>
<p class="note" style="color:#1b2430;font-size:13.5px;margin-top:14px">The speed rose by only 10% and the inertia forces by only 21%, yet the second-order amplification rose from about 4.2 to about 11 times: this is what happens near resonance.</p>'''
print(page('fig_20_sweep', body))
