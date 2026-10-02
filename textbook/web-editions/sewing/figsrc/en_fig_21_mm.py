"""English version of fig_21_mm (Fig. 28-6): operator-machine charts and cost per piece. Model: src/zh/labs/line21.html."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en__lib_ch26_28 import *

a, w, WAGE, MR = 0.3, 0.05, 0.5, 0.08


def mm(n, t):
    C = max(n * (a + w), a + t)
    return C, n * (a + w) / C, (a + t) / C, (WAGE + n * MR) * C / n


fig = panel_fig(640, 345)
SPAN = 2.8
for p, (n, top) in enumerate([(3, 0.95), (4, 0.47)]):
    t = 0.9; C, uo, um, _ = mm(n, t)
    h = 0.06 * (n + 1)
    ax = fig.add_axes([0.1, top - h - 0.06, 0.88, h])
    for cy in range(-1, 4):
        base = cy * C
        for i in range(n):
            s = base + i * (a + w)
            for row, t0, t1, col in [(0, s, s + a, '#2f6fd6'), (0, s + a, s + a + w, '#d3d9df'),
                                     (i + 1, s, s + a, '#2f6fd6'), (i + 1, s + a, s + a + t, '#e57d4e')]:
                t0c, t1c = max(0, t0), min(SPAN, t1)
                if t1c > t0c:
                    ax.add_patch(plt.Rectangle((t0c, row + 0.15), t1c - t0c, 0.7, color=col, lw=0))
    ax.set_xlim(0, SPAN); ax.set_ylim(n + 1, 0)
    ax.set_yticks([k + 0.5 for k in range(n + 1)]); ax.set_yticklabels(['Operator'] + [f'M{k}' for k in range(1, n + 1)])
    ax.set_xticks([0, 0.5, 1, 1.5, 2, 2.5]); ax.set_xticklabels(['0', '0.5', '1', '1.5', '2', '2.5'])
    ax.grid(False); ax.set_facecolor('white')
    for s_ in ax.spines.values(): s_.set_visible(False)
    ax.tick_params(axis='y', colors=MUTED, labelsize=8.5)
    fig.text(0.1, top - 0.035, f'Tending {n} machines: cycle {C:.2f} min, operator {uo * 100:.0f}%, machines {um * 100:.0f}%',
             fontsize=9.5, fontweight='bold', color=INK, va='bottom')
p1 = save_panel(fig, 'mm_gantt.png', transparent_white=True)

fig = panel_fig(420, 300); ax = fig.add_axes([0.15, 0.15, 0.82, 0.82])
for t, c, dy in [(0.9, '#2f6fd6', 0), (0.6, '#e0662f', 0)]:
    ns = list(range(1, 7)); cs = [mm(n, t)[3] for n in ns]; best = ns[cs.index(min(cs))]
    ax.plot(ns, cs, color=c, lw=1.6, marker='o', ms=4.5, zorder=3)
    ax.plot([best], [min(cs)], 'o', color=c, ms=10, zorder=4)
ax.text(1.2, 0.715, 't = 0.9 min (lowest at 4)', color='#2f6fd6', fontsize=8.5, fontweight='bold', va='bottom')
ax.text(1.75, 0.15, 't = 0.6 min (lowest at 3)', color='#e0662f', fontsize=8.5, fontweight='bold', va='bottom')
ax.set_xlim(0.6, 6.5); ax.set_ylim(0, 0.8); ax.set_xticks(range(1, 7)); ax.set_yticks([0, .2, .4, .6, .8])
ax.set_yticklabels(['0.0', '0.2', '0.4', '0.6', '0.8'])
ax.set_xlabel('Machines tended'); ax.set_ylabel('Cost per piece (yuan)')
p2 = save_panel(fig, 'mm_cost.png')

body = f'''<p class="title">One operator, several machines: operator–machine chart and cost per piece</p>
<p class="sub">Worked-example values: loading/unloading per machine a = 0.3 min, walking w = 0.05 min, automatic sewing t = 0.9 min; wage 0.5 yuan/min, equipment 0.08 yuan/min per machine</p>
<div style="display:grid;grid-template-columns:660px 1fr;gap:24px;align-items:start">
<div class="card" style="padding:6px 8px 12px"><img class="pimg" src="{p1}"><p style="font-size:12px;color:#5a6570;margin:4px 0 0 64px">Blue: operator loading/unloading; light grey: walking; orange: automatic sewing; blank: waiting; time in min</p></div>
<div><img class="pimg" src="{p2}"><p style="font-size:13px;margin:6px 0 0 10px">Machines at which neither operator nor machine waits ≈ (a+t)/(a+w):<br>3.43 for t = 0.9, 2.57 for t = 0.6; for n ≥ 4 the two curves coincide</p></div></div>'''
print(page('fig_21_mm', body))
