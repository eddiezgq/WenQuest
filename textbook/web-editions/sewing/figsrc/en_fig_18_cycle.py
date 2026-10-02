"""English version of fig_18_cycle (Fig. 18-3). Recomputed from the ch18 model (ebox lab)."""
import math, numpy as np
from en__lib_ch18_23 import *

r = thermal()
# ---- panel a: first hour (heat sink first-order, time constant ~12 min, illustrative) ----
tm = np.linspace(0, 60, 601)
ths = 40 + (r['Ths'] - 40) * (1 - np.exp(-tm / 12))
tj = ths + (r['Tjpk'] - r['Ths'])
fig = panel_fig(820, 470)
ax = fig.add_axes([0.10, 0.13, 0.87, 0.78])
ax.set_title('a    First hour after switch-on (band: junction jump at each start/stop)', pad=12, fontsize=12)
ax.fill_between(tm, ths, tj, color=RED, alpha=0.12, lw=0)
ax.plot(tm, tj, color=RED, lw=1.4)
ax.plot(tm, ths, color=BLUE, lw=2.2)
ax.plot([60, 60], [ths[-1], tj[-1]], color=RED, lw=1.4)
ax.axhline(125, color=RED, lw=1, ls=(0, (4, 3)))
ax.axhline(100, color=GOLD, lw=1, ls=(0, (4, 3)))
ax.text(1, 126.5, 'Junction design limit 125 °C', color=RED, fontsize=10.5, weight='bold')
ax.text(1, 101.5, 'Overheat alarm 100 °C', color=GOLD, fontsize=10.5, weight='bold')
ax.text(40, 112.5, f"Peak junction → {r['Tjpk']:.0f} °C", color=RED, fontsize=10.5, weight='bold', ha='center')
ax.text(59, 73, f"Heat sink → {r['Ths']:.0f} °C\n(time constant ten-odd minutes, illustrative)",
        color=BLUE, fontsize=10.5, weight='bold', ha='right', va='top')
ax.set_xlim(0, 60); ax.set_ylim(30, 130); ax.set_yticks(range(30, 131, 20))
ax.set_xlabel('Time after switch-on (min)'); ax.set_ylabel('Temperature (°C)')
pa = save_panel(fig, 'fig_18_cycle_a.png')

# ---- panel b: two sewing cycles ----
f = 12e3; t = 300e-9; tc = 2.0; ta = 0.15; tr = 0.5 * tc - 2 * ta
def Iof(u):
    k = u % tc
    return 9 if k < ta else 3 if k < ta + tr else 9 if k < 2 * ta + tr else 0
def pof(I):
    if I <= 0: return 0
    pc, ps, _ = sw(I, f, t); return pc + ps
T = 2 * tc; N = 4000; dt = T / N; z = 0
for _ in range(3):
    us, tjs, Is = [], [], []
    for i in range(N + 1):
        u = i * dt; I = Iof(u)
        z += (pof(I) * RTH - z) * (1 - math.exp(-dt / TAU))
        us.append(u); tjs.append(r['Ths'] + z); Is.append(I)
us = np.array(us); Is = np.array(Is)
fig = panel_fig(860, 470)
ax = fig.add_axes([0.08, 0.13, 0.84, 0.78])
ax.set_title('b    Two sewing cycles enlarged (grey: phase current, right-hand scale)', pad=12, fontsize=12)
YI = lambda i: 70 + 70 * i / 14  # current scale mapped onto 70–140 °C axis
ax.fill_between(us, 70, YI(Is), step=None, color='#d5d9de', alpha=0.7, lw=0)
ax.plot(us, YI(Is), color='#8a949e', lw=0.8)
ax.axhline(125, color=RED, lw=1, ls=(0, (4, 3)))
ax.plot(us, [r['Ths']] * len(us), color=BLUE, lw=2)
ax.plot(us, tjs, color=RED, lw=1.8)
ax.text(3.97, 126.2, '125 °C', color=RED, fontsize=10, weight='bold', ha='right')
ax.text(0.02, 119.5, 'Accelerate 9 A', color=RED, fontsize=10, weight='bold')
ax.text(0.93, YI(9) + 1.2, 'Decelerate/brake 9 A', color=RED, fontsize=10, weight='bold', ha='center')
ax.text(0.5, YI(3) + 1.0, 'Sew 3 A', color=RED, fontsize=10, weight='bold', ha='center')
ax.text(1.52, 72.5, 'Stopped (handling fabric)', color=MUTED, fontsize=9.5, weight='bold', ha='center')
ax.text(3.0, r['Ths'] - 1.4, 'Heat sink (almost constant)', color=BLUE, fontsize=10, weight='bold', ha='center', va='top')
ax.set_xlim(0, 4); ax.set_ylim(70, 140); ax.set_xticks(range(5)); ax.set_yticks(range(70, 141, 10))
ax2 = ax.twinx(); ax2.set_ylim(0, 14); ax2.set_yticks([0, 3, 6, 9]); ax2.set_yticklabels(['0 A', '3 A', '6 A', '9 A'])
ax2.grid(False)
for s in ax2.spines.values(): s.set_color(FRAME)
ax.set_xlabel('Time (s)'); ax.set_ylabel('Temperature (°C)')
pb = save_panel(fig, 'fig_18_cycle_b.png')

share = r['facc'] * r['Pk'] / r['Pavg'] * 100
body = f'''<p class="title">Intermittent sewing: the heat sink creeps up with the average loss, the junction jumps at every start and stop</p>
<p class="sub">Worked example (illustrative values): 40 °C shop; 30 starts and stops per minute, sewing half of the time; acceleration and deceleration 0.15 s each at 9 A, the rest of the sewing at 3 A</p>
<div style="display:grid;grid-template-columns:820fr 860fr;gap:0">
<img class="pimg" src="{pa}"><img class="pimg" src="{pb}"></div>
<p class="note" style="color:#1b2430;font-size:13.5px">Starts and stops take only {r['facc']*100:.0f}% of the time but contribute about {share:.0f}% of the heat. Operations with many short seams start and stop often and run hotter than long-seam operations; running continuously at 9 A would take the heat sink above 200 °C.</p>'''
print(page('fig_18_cycle', body))
