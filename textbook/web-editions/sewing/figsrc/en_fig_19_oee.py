"""English version of fig_19_oee (Fig. 26-5): OEE waterfall. Model: src/zh/labs/iot.html."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en__lib_ch26_28 import *

s = shift(); L = s['loss']
items = [('Planned time', s['planned'], 'base'), ('Waiting for work', -L['wait'], None), ('Equipment failure', -L['fault'], None),
         ('Thread breaks', -L['brk'], None), ('Operating time', s['oper'], 'sub'), ('Speed loss', -L['speed'], None),
         ('Rework', -L['quality'], None), ('Good-piece time', s['good'] * s['p']['sam'], 'sub')]
fig = panel_fig(1120, 330); ax = fig.add_axes([0.06, 0.1, 0.93, 0.86])
lvl = 0
for i, (lab, v, k) in enumerate(items):
    if k:
        top, bot = v, 0; lvl = v; col = '#6393e0' if k == 'base' else '#62b684'
    else:
        top, bot = lvl, lvl + v; lvl = bot; col = '#d06b60'
    ax.bar(i, top - bot, bottom=bot, width=0.6, color=col)
    ax.text(i, top + 5, f'{abs(v):.0f}', ha='center', va='bottom', fontsize=9.5, fontweight='bold', color=INK)
ax.text(4, 472, f'A = {s["oper"]:.0f} / {s["planned"]:.0f}', ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2f6fd6')
ax.set_xticks(range(len(items))); ax.set_xticklabels([x[0] for x in items])
ax.set_ylim(0, 480); ax.set_yticks(range(0, 481, 120)); ax.set_xlim(-0.6, 7.6); ax.grid(axis='x', visible=False)
ax.set_ylabel('Time (min)')
p = save_panel(fig, 'oee.png')

body = f'''<p class="title">Where the time of one shift goes: OEE = {s['A']*100:.1f}% × {s['P']*100:.1f}% × {s['Q']*100:.1f}% ≈ {s['OEE']*100:.1f}%</p>
<p class="sub">Worked example (illustrative values): planned 450 min; waiting for work 25 min, equipment failure 12 min, about 11 thread breaks × 1 min; efficiency 85%; rework 3%; standard minute value 0.6 min</p>
<img class="pimg" src="{p}">
<p class="note">The main shaft actually runs for only about 120 min (27% of planned time) — the rest goes on picking up, aligning and turning the fabric, which is already included in the standard minute value and must not be read as “the machine standing idle”.<br>
The largest loss is speed loss, followed by waiting for work and equipment failure; thread breaks and rework are about 10 min each. Only after this breakdown is it clear where to start.</p>'''
print(page('fig_19_oee', body))
