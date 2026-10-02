"""English version of fig_18_emc (Fig. 18-4). Left: HTML/SVG diagram; right: chart recomputed from the ch18 model."""
import numpy as np
from en__lib_ch18_23 import *

ts = np.arange(80, 1181, 5)
tj = np.array([thermal(Ta=45, tsw=t)['Tjpk'] for t in ts])
icm = np.array([thermal(Ta=45, tsw=t)['icm'] for t in ts])
ok = ts[(tj <= 125) & (icm <= 0.8)]
fig = panel_fig(820, 600)
ax = fig.add_axes([0.10, 0.13, 0.80, 0.80])
ax.set_title('b    The switching-time trade-off (45 °C)', pad=12)
ax.axvspan(ok.min(), ok.max(), color=GREEN, alpha=0.11, lw=0)
ax.text((ok.min() + ok.max()) / 2, 167.5, f'Both met: about {ok.min():.0f}–{ok.max():.0f} ns', color=GREEN,
        fontsize=10.5, weight='bold', ha='center', va='top')
ax.plot(ts, tj, color=RED, lw=2.2)
ax.axhline(125, color=RED, lw=1, ls=(0, (4, 3)))
ax.text(1170, 126.2, 'Junction limit 125 °C', color=RED, fontsize=10.5, weight='bold', ha='right')
ax.text(1185, 132.5, 'Peak junction temperature (left axis)', color=RED, fontsize=10.5, weight='bold', ha='right', va='top')
ax.set_xlim(50, 1210); ax.set_ylim(90, 170); ax.set_yticks(range(90, 171, 20)); ax.set_xticks(range(100, 1101, 200))
ax.set_xlabel('Switching time t_sw (ns, turn-on + turn-off)'); ax.set_ylabel('Peak junction temperature (°C)')
ax2 = ax.twinx(); ax2.set_ylim(0, 2.5); ax2.grid(False)
ax2.set_yticks(np.arange(0, 2.51, 0.5)); ax2.set_yticklabels([f'{v:.1f} A' for v in np.arange(0, 2.51, 0.5)])
ax2.tick_params(colors=BLUE)
for s in ax2.spines.values(): s.set_color(FRAME)
ax2.plot(ts, icm, color=BLUE, lw=2.2)
ax2.axhline(0.8, color=BLUE, lw=1, ls=(0, (4, 3)))
ax2.text(1170, 0.74, 'Common-mode target 0.8 A', color=BLUE, fontsize=10.5, weight='bold', ha='right', va='top')
ax2.text(700, 0.56, 'Peak common-mode current (right axis)', color=BLUE, fontsize=10.5, weight='bold', ha='center')
ax.tick_params(axis='y', colors=MUTED)
pb = save_panel(fig, 'fig_18_emc_b.png')

R, G, K, M = RED, GREEN, INK, MUTED
svg = f'''<svg viewBox="0 0 893 465" width="100%" style="display:block">
<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#5a6570"/></marker>
<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#5a6570"/></marker></defs>
<text x="24" y="38" font-size="20" font-weight="700" fill="{K}">a</text><text x="52" y="38" font-size="20" font-weight="700" fill="{K}">Common-mode current i = C dv/dt: the path it takes</text>
<rect x="35" y="93" width="177" height="107" rx="9" fill="#fff" stroke="{K}" stroke-width="2.4"/>
<text x="123" y="127" text-anchor="middle" font-size="17" font-weight="700" fill="{K}">Mains</text>
<text x="123" y="152" text-anchor="middle" font-size="13.5" fill="{M}">L, N, PE</text>
<rect x="258" y="93" width="177" height="107" rx="9" fill="#fff" stroke="{G}" stroke-width="2.4"/>
<text x="347" y="127" text-anchor="middle" font-size="17" font-weight="700" fill="#1f8a4c">EMI filter</text>
<text x="347" y="152" text-anchor="middle" font-size="13.5" fill="{M}">common-mode choke</text>
<text x="347" y="171" text-anchor="middle" font-size="13.5" fill="{M}">Y capacitors to earth</text>
<rect x="482" y="93" width="177" height="107" rx="9" fill="#fff" stroke="{R}" stroke-width="2.4"/>
<text x="570" y="127" text-anchor="middle" font-size="17" font-weight="700" fill="{R}">Inverter bridge</text>
<text x="570" y="152" text-anchor="middle" font-size="13.5" fill="{M}">310 V transitions</text>
<text x="570" y="171" text-anchor="middle" font-size="13.5" fill="{M}">in 0.15 µs inside</text>
<rect x="705" y="82" width="153" height="128" rx="56" fill="#eef1f4" stroke="#5a6570" stroke-width="2.4"/>
<text x="782" y="140" text-anchor="middle" font-size="17" font-weight="700" fill="{K}">Motor</text>
<text x="782" y="165" text-anchor="middle" font-size="13.5" fill="{M}">windings</text>
<g stroke="#5a6570" stroke-width="2.4" marker-end="url(#ah)"><line x1="214" y1="146" x2="256" y2="146"/><line x1="437" y1="146" x2="480" y2="146"/><line x1="661" y1="146" x2="703" y2="146"/></g>
<text x="690" y="234" text-anchor="end" font-size="13" fill="{M}">Motor cable</text>
<line x1="123" y1="200" x2="123" y2="375" stroke="{R}" stroke-width="1.8" stroke-dasharray="5 4"/>
<line x1="347" y1="200" x2="347" y2="375" stroke="{G}" stroke-width="1.8" stroke-dasharray="5 4"/>
<text x="358" y="305" font-size="14" font-weight="700" fill="#1f8a4c">Y capacitors return it locally</text>
<line x1="782" y1="210" x2="782" y2="281" stroke="{R}" stroke-width="2.4"/>
<line x1="755" y1="281" x2="812" y2="281" stroke="{R}" stroke-width="4"/><line x1="755" y1="295" x2="812" y2="295" stroke="{R}" stroke-width="4"/>
<line x1="782" y1="295" x2="782" y2="375" stroke="{R}" stroke-width="2.4"/>
<text x="745" y="294" text-anchor="end" font-size="15" font-weight="700" fill="{R}">Parasitic capacitance C</text>
<line x1="45" y1="375" x2="848" y2="375" stroke="#5a6570" stroke-width="3.2"/>
<g stroke="{R}" stroke-width="2.4"><line x1="540" y1="390" x2="382" y2="390"/><line x1="765" y1="390" x2="567" y2="390"/></g>
<path d="M372,390 l20,-9 v18 z" fill="#5a6570"/><path d="M557,390 l20,-9 v18 z" fill="#5a6570"/>
<text x="60" y="406" font-size="14.5" font-weight="700" fill="{M}">Protective earth / housing</text>
<text x="455" y="436" text-anchor="middle" font-size="14.5" font-weight="700" fill="{R}">Common-mode current → (through the earth wire and the mains back to the inverter bridge)</text>
</svg>'''

body = f'''<p class="title">Faster switching: less heat, more interference</p>
<p class="sub">Left: path of the common-mode current (illustrative); right: effect of switching time in a 45 °C shop under this chapter’s standard operating conditions (worked example, illustrative values)</p>
<div style="display:grid;grid-template-columns:760px 1fr;gap:20px;align-items:start">
<div class="card" style="padding:4px 0 18px;height:600px">{svg}
<ul style="margin:6px 0 0;padding:0 24px 0 40px;font-size:13.5px;line-height:1.85;color:#1b2430">
<li>Worked example: C = 300 pF, 310 V rising in 150 ns, peak about 0.6 A</li>
<li>Long path, large loop area: it radiates like an antenna</li>
<li>Flowing through the earth conductors, it makes the low-voltage “ground” bounce, disturbing the encoder and communications</li>
<li>Countermeasures: filter, shielded cable (shield earthed over a large area), small loop areas, slower switching (lower dv/dt)</li></ul></div>
<img class="pimg" src="{pb}"></div>
<p class="note" style="color:#1b2430;font-size:13.5px">Doubling the switching time halves the peak common-mode current (low-frequency conducted interference improves little and still relies on the filter) but doubles the switching loss; lowering the switching frequency also cuts losses, but the motor noise becomes more shrill. Thermal design and EMC must be considered together.</p>'''
print(page('fig_18_emc', body))
