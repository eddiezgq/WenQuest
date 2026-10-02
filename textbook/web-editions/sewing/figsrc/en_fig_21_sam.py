"""English version of fig_21_sam (Fig. 28-4): time-study example and seam time vs stitch count and max speed.
Seam times from the lab's seamTime() (src/zh/labs/line21.html, speed profile as in Chapter 14)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en__lib_ch26_28 import *

D = load_line()
# left: bars
fig = panel_fig(440, 280); ax = fig.add_axes([0.03, 0.2, 0.94, 0.75])
vals = [0.48, 0.48 * 1.10, 0.48 * 1.10 * 1.14]; cols = ['#7d8995', '#598cde', '#e68559']
ax.bar(range(3), vals, width=0.6, color=cols)
for i, v in enumerate(vals):
    ax.text(i, v + 0.012, f'{v:.3f} min', ha='center', va='bottom', fontsize=10, fontweight='bold', color=INK)
ax.set_ylim(0, 0.66); ax.set_xlim(-0.6, 2.6); ax.axis('off')
for i, t in enumerate(['Observed time\n(mean of 10)', 'Rating 110%\n→ basic time', 'Allowances 14%\n→ standard minute value']):
    fig.text(0.03 + 0.94 * (i + 0.6) / 3.2, 0.16, t, ha='center', va='top', fontsize=8.8, color=INK)
p1 = save_panel(fig, 'sam_bars.png', transparent_white=True)

# right: seam time
fig = panel_fig(560, 330); ax = fig.add_axes([0.1, 0.15, 0.87, 0.82])
sty = {'3000': ('#5a6570', (0, (2, 1.5)), 1.4), '4000': (INK, (0, (5, 3)), 1.6), '5000': ('#2f6fd6', '-', 1.6), '6000': ('#e0662f', '-', 1.6)}
for n, (c, ls, lw) in sty.items():
    xs = [p[0] for p in D['seam'][n]]; ys = [p[1] for p in D['seam'][n]]
    ax.plot(xs, ys, color=c, ls=ls, lw=lw)
    ax.text(590, ys[-1] + (-0.75 if n == '6000' else 0.2), n, color=c, fontsize=8.5, fontweight='bold', ha='right',
            va=('top' if n == '6000' else 'bottom'))
ax.plot([333], [D['s333'][0]], 'o', color=INK, ms=6.5, zorder=5)
ax.plot([333], [D['s333'][1]], 'o', color='#2f6fd6', ms=6.5, zorder=5)
ax.text(20, 12.6, f'333 stitches (dots): 4000 r/min {D["s333"][0]:.2f} s, 5000 r/min {D["s333"][1]:.2f} s', fontsize=8.8, fontweight='bold', color=INK)
ax.text(20, 11.8, f'40-stitch short seam: 4000 and 6000 r/min differ by only {D["s40"][0] - D["s40"][1]:.2f} s', fontsize=8.3, color=MUTED)
ax.set_xlim(0, 600); ax.set_ylim(0, 14); ax.set_yticks(range(0, 15, 2))
ax.set_xlabel('Stitches (100 cm at 3 mm stitch length ≈ 333 stitches)'); ax.set_ylabel('Time for one seam (s)')
p2 = save_panel(fig, 'sam_seam.png')

body = f'''<p class="title">What a standard minute value is made of, and how sewing-machine speed affects it</p>
<p class="sub">Left: time-study worked example for “topstitch side seams”; right: time for one seam from first stitch to trimmed stop (speed profile as in Chapter 14)</p>
<div style="display:grid;grid-template-columns:480px 1fr;gap:30px;align-items:start">
<div class="card" style="padding:14px 18px 10px"><p style="font-size:12.5px;color:#5a6570;margin:4px 0 2px 10px">Allowances = personal 5% + fatigue 4% + machine 5% (common published values)</p><p style="font-size:15px;font-weight:700;color:#e0662f;margin:0 0 6px 10px">Standard minute value ≈ 0.60 min = 36 s</p><img class="pimg" src="{p1}"></div><img class="pimg" src="{p2}"></div>
<p class="note" style="margin-top:12px">Topstitching the side seams means two seams of about 100 cm: raising the maximum speed from 4000 to 5000 r/min saves 1.9 s of machine time, only 5% of the operation’s 36 s; and long seams have to be guided, so the operator does not keep the machine at full speed anyway.</p>'''
print(page('fig_21_sam', body))
