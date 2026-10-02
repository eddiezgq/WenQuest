"""English version of fig_18_loss (Fig. 18-2). Left: HTML/SVG thermal network; right: chart recomputed from the ch18 model."""
import numpy as np
from en__lib_ch18_23 import *

f, t = 12e3, 300e-9
I = np.linspace(0.001, 10, 300)
parts = np.array([[6 * sw(i, f, t)[0], 6 * sw(i, f, t)[1], 6 * sw(i, f, t)[2], 2 * 0.9 * 0.6 * i] for i in I]).T
cum = np.cumsum(parts, axis=0)
fig = panel_fig(860, 560)
ax = fig.add_axes([0.10, 0.13, 0.86, 0.80])
ax.set_title('b    Losses grow faster than the current', pad=12)
cols = [('#e8b4b0', '#c4372b', 'Switch conduction'), ('#e9d1a6', '#c48a17', 'Switch switching'),
        ('#d9bde6', '#8a5cc7', 'Diode (incl. reverse recovery)'), ('#c6cbd1', '#6b7580', 'Rectifier bridge')]
lo = np.zeros_like(I)
for k, (fc, ec, lab) in enumerate(cols):
    ax.fill_between(I, lo, cum[k], color=fc, lw=0, label=lab, alpha=0.95)
    ax.plot(I, cum[k], color=ec, lw=0.9)
    lo = cum[k]
for i, dx, dy, ha in [(3, 0.12, 0.8, 'left'), (9, -0.15, 1.0, 'right')]:
    p = inv(i, f, t)
    ax.plot([i], [p], 'o', color=INK, ms=8, zorder=5)
    ax.text(i + dx, p + dy, f'{i} A: about {p:.0f} W', fontsize=10.5, weight='bold', color=INK, ha=ha)
leg = ax.legend(loc='upper left', frameon=False, fontsize=10.5, handlelength=1.2, handleheight=1.0)
for h, (fc, ec, _) in zip(leg.legend_handles, cols): h.set_edgecolor(ec)
ax.set_xlim(0, 10); ax.set_ylim(0, 90); ax.set_yticks(range(0, 91, 15))
ax.set_xlabel('Phase current, RMS (A)'); ax.set_ylabel('Power-stage loss (W)')
pb = save_panel(fig, 'fig_18_loss_b.png')

r = thermal()
K, M = INK, MUTED
nodes = [(93, '#c4372b', 'Junction (chip)', f"peak {r['Tjpk']:.0f} °C"), (258, '#b8791c', 'Heat sink', f"{r['Ths']:.1f} °C"),
         (423, '#2a6fdb', 'Air inside box', f"{r['Tin']:.1f} °C"), (588, '#2e9e5b', 'Shop', '40 °C')]
res = [('Junction to heat sink, per device 3.5 K/W', 'about 8.3 W per device at start/stop'),
       ('Heat sink to box interior 1.5 K/W', f"average loss about {r['Pavg']:.0f} W"),
       ('Box interior to shop 0.6 K/W', f"{r['Pavg']:.0f} W + other circuits 8 W")]
g = []
for k, (y, c, a, b) in enumerate(nodes):
    if k < 3:
        y2 = nodes[k + 1][0]
        g.append(f'<line x1="165" y1="{y}" x2="165" y2="{y2}" stroke="{K}" stroke-width="1.6"/>'
                 f'<rect x="151" y="{y+33}" width="28" height="{y2-y-66}" rx="4" fill="#fff" stroke="{K}" stroke-width="1.6"/>'
                 f'<text x="205" y="{(y+y2)/2-6}" font-size="15" font-weight="700" fill="#5a6570">{res[k][0]}</text>'
                 f'<text x="205" y="{(y+y2)/2+20}" font-size="13" fill="{M}">{res[k][1]}</text>')
for y, c, a, b in nodes:
    g.append(f'<circle cx="165" cy="{y}" r="17" fill="{c}"/>'
             f'<text x="205" y="{y-6}" font-size="17" font-weight="700" fill="{c}">{a}</text>'
             f'<text x="205" y="{y+20}" font-size="15" fill="{K}">{b}</text>')
side = ['The heat sink and the box have', 'large thermal capacity; their', 'temperature is set by the average loss.',
        'The chip has little thermal capacity:', 'at every start and stop the junction', 'jumps above the heat-sink temperature.']
g.append(''.join(f'<text x="548" y="{215+k*30}" font-size="14.5" fill="{K}">{s}</text>' for k, s in enumerate(side)))
svg = f'''<svg viewBox="0 0 823 705" width="100%" style="display:block">
<text x="24" y="38" font-size="20" font-weight="700" fill="{K}">a</text>
<text x="52" y="38" font-size="20" font-weight="700" fill="{K}">Thermal-resistance network (temperature like voltage, heat flow like current)</text>
<g transform="translate(0,40)">
<line x1="82" y1="55" x2="82" y2="565" stroke="#c4372b" stroke-width="2.4"/><path d="M70,568 h24 l-12,24 z" fill="#5a6570"/>
<text x="60" y="318" font-size="15" font-weight="700" fill="#c4372b" text-anchor="middle" transform="rotate(-90 60 318)">Heat flow</text>
{''.join(g)}</g></svg>'''

body = f'''<p class="title">From chip to shop: losses, thermal resistances and temperatures</p>
<p class="sub">Worked example (illustrative values): t_sw = 300 ns, 12 kHz; the left-hand diagram shows temperatures in a 40 °C shop under this chapter’s standard operating conditions</p>
<div style="display:grid;grid-template-columns:700px 1fr;gap:40px;align-items:start">
<div class="card">{svg}</div>
<img class="pimg" src="{pb}" style="margin-top:6px"></div>'''
print(page('fig_18_loss', body))
