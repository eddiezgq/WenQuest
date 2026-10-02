"""English version of fig_18_case (Fig. 18-7). Recomputed from the ch18 model."""
import numpy as np
from en__lib_ch18_23 import *

# ---- panel a: temperatures vs blockage at 38 °C ----
c = np.linspace(0, 1, 101)
tj = [thermal(Ta=38, clog=x)['Tjpk'] for x in c]
hs = [thermal(Ta=38, clog=x)['Ths'] for x in c]
hs2 = [thermal(Ta=38, clog=x, rhs=1.0)['Ths'] for x in c]
fig = panel_fig(820, 470)
ax = fig.add_axes([0.105, 0.13, 0.87, 0.78])
ax.set_title('a    Temperatures rise with the degree of blockage', pad=12)
ax.plot(c, tj, color=RED, lw=2)
ax.plot(c, hs, color=BLUE, lw=2)
ax.plot(c, hs2, color=BLUE, lw=2, ls=(0, (4, 2)))
ax.axhline(125, color=RED, lw=1, ls=(0, (4, 3)))
ax.axhline(100, color=GOLD, lw=1, ls=(0, (4, 3)))
r = thermal(Ta=38, clog=0.5)
ax.plot([0.5], [r['Tjpk']], 'o', color=RED, ms=8)
ax.plot([0.5], [r['Ths']], 'o', color=BLUE, ms=8)
ax.text(0.49, r['Tjpk'] + 2.5, f"{r['Tjpk']:.0f} °C", color=RED, ha='right', fontsize=10.5, weight='bold')
ax.text(0.52, 104.3, f"{r['Ths']:.0f} °C", color=BLUE, ha='left', va='center', fontsize=10.5, weight='bold')
ax.text(0.98, 160, 'Peak junction temperature', color=RED, ha='right', va='top', fontsize=10.5, weight='bold')
ax.text(0.79, 130, 'Heat sink', color=BLUE, ha='right', va='bottom', fontsize=10.5, weight='bold')
ax.text(0.98, 116.5, 'Improved heat sink', color=BLUE, ha='right', va='bottom', fontsize=10.5, weight='bold')
ax.text(0.015, 126.5, 'Junction limit 125 °C', color=RED, fontsize=10.5, weight='bold')
ax.text(0.015, 101.5, 'Overheat alarm 100 °C', color=GOLD, fontsize=10.5, weight='bold')
ax.set_xlim(0, 1); ax.set_ylim(60, 170)
ax.set_yticks(range(60, 161, 20)); ax.set_xticks(np.arange(0, 1.01, 0.2))
ax.set_xlabel('Degree of blockage'); ax.set_ylabel('Temperature (°C)')
pa = save_panel(fig, 'fig_18_case_a.png')

# ---- panel b: capacitor life vs core temperature ----
T = np.linspace(40, 90, 401)
life = lambda L0, t: np.minimum(L0 * 2 ** ((105 - t) / 10) / 4800, 30)
fig = panel_fig(860, 470)
ax = fig.add_axes([0.09, 0.13, 0.86, 0.78])
ax.set_title('b    Electrolytic-capacitor life halves for every 10 °C hotter (10-degree rule)', pad=12)
ax.plot(T, life(5000, T), color=GREEN, lw=2)
ax.plot(T, life(2000, T), color=ORANGE, lw=2)
ax.axhline(5, color=MUTED, lw=1, ls=(0, (4, 3)))
ax.text(40.6, 5.4, 'Design target 5 years', color=INK, fontsize=10, weight='bold')
ax.text(67.5, 14.6, '105 °C, 5000 h', color=GREEN, fontsize=10.5, weight='bold')
ax.text(83.0, 0.5, '105 °C, 2000 h', color=ORANGE, fontsize=10.5, weight='bold', ha='center')
for clog, dx, dy, ha, lab in [(0, 0.8, 0.5, 'left', 'Clean'), (0.5, None, None, None, 'Blockage 0.5'),
                              (0.8, -0.8, -1.3, 'right', 'Blockage 0.8')]:
    r = thermal(Ta=38, clog=clog)
    ax.plot([r['Tcap']], [r['lifeY']], 'o', color=ORANGE, ms=8, zorder=5)
    txt = f"{lab}: {r['Tcap']:.0f} °C, {r['lifeY']:.1f} years"
    if dx is None:  # leader line, label in the free area to the left
        ax.annotate(txt, (r['Tcap'], r['lifeY']), xytext=(44.2, 7.3), fontsize=10, weight='bold', color=INK,
                    arrowprops=dict(arrowstyle='-', color=MUTED, lw=0.8, shrinkB=5))
    else:
        ax.text(r['Tcap'] + dx, r['lifeY'] + dy, txt, fontsize=10, weight='bold', color=INK, ha=ha)
ax.set_xlim(40, 90); ax.set_ylim(0, 30)
ax.set_xlabel('Capacitor core temperature (°C)'); ax.set_ylabel('Life (years, 4800 h per year)')
pb = save_panel(fig, 'fig_18_case_b.png')

body = f'''<p class="title">Case study: after lint blocks the cooling path</p>
<p class="sub">Worked example (illustrative values): 38 °C shop, this chapter’s standard operating conditions; blockage 0 = clean, 1 = severe</p>
<div style="display:grid;grid-template-columns:820fr 860fr;gap:0">
<img class="pimg" src="{pa}"><img class="pimg" src="{pb}"></div>
<p class="note" style="color:#1b2430;font-size:13.5px">The overheat alarm is the protection doing its job correctly. The real remedy is cooling that lint cannot defeat: a sealed box, an external heat sink with widely spaced fins and regular cleaning, combined with overtemperature derating and long-life capacitors.</p>'''
print(page('fig_18_case', body))
