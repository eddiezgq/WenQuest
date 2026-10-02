"""English version of fig_19_traffic (Fig. 26-4): message rate and storage of five reporting methods. Model: src/zh/labs/iot.html."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en__lib_ch26_28 import *

modes = ['stitch', 'segment', 'piece', 'minute', 'tenmin']
names = ['Per\nstitch', 'Per start/stop\nand trim', 'Per piece\n+ immediate\nstate', 'Per minute\n+ immediate\nstate', 'Per\n10 min']
tn = ['Per stitch', 'Per pedal start/stop and trim', 'Per-piece summary + immediate state',
      'Per-minute summary + immediate state', '10-minute summary']
ts = [traffic(m) for m in modes]

fig = panel_fig(540, 350); ax = fig.add_axes([0.13, 0.19, 0.85, 0.78])
for i, t in enumerate(ts):
    ax.bar(i, t['rate'] - 0.1, bottom=0.1, width=0.6, color=('#6cbb8c' if t['ok'] else '#d3746a'))
    r = t['rate']; lab = f'{r:.2f}' if r < 1 else (f'{r:.3g}' if r < 10 else f'{r:.0f}')
    ax.text(i, r * 1.12, lab, ha='center', va='bottom', fontsize=9, fontweight='bold', color=INK)
ax.set_yscale('log'); ax.set_ylim(0.1, 10000)
ax.set_yticks([0.1, 1, 10, 100, 1000, 10000]); ax.set_yticklabels(['0.1', '1', '10', '100', '1000', '10000'])
ax.minorticks_off()
ax.axhline(500, color=RED, lw=1.2, ls=(0, (5, 3)))
ax.text(4.5, 600, 'budget 500 msg/s', color=RED, fontsize=8.5, fontweight='bold', ha='right', va='bottom')
ax.set_xticks(range(5)); ax.set_xticklabels(names, fontsize=7.8); ax.set_xlim(-0.55, 4.55); ax.grid(axis='x', visible=False)
ax.set_ylabel('Mean message rate (msg/s, log scale)')
p = save_panel(fig, 'traffic.png')


def stor(gb):
    return f'{gb / 1000:.0f} TB' if gb >= 1000 else f'{gb:.0f} GB'


def lat(v):
    return 'immediate' if v <= 1 else f'{v:.0f} s'


rows = ''.join(f'<tr><td>{n}</td><td>{stor(t["gb"])}</td><td>{lat(t["ls"])}</td><td>{lat(t["lc"])}</td>'
               f'<td style="color:{"#1f8a4c" if t["ok"] else "#c4372b"};font-weight:600">{"meets" if t["ok"] else "fails"}</td></tr>'
               for n, t in zip(tn, ts))
body = f'''<p class="title">The finer the reports, the more data; the coarser the summaries, the slower the dashboard</p>
<p class="sub">Worked example (illustrative): 500 sewing machines, two shifts a day, 250 bytes per message; operating conditions as in this chapter’s worked example</p>
<div style="display:grid;grid-template-columns:540px 1fr;gap:24px;align-items:start">
<img class="pimg" src="{p}">
<div class="card" style="padding:10px 14px 12px;margin-top:4px">
<table style="width:100%;font-size:13px"><tr><th style="border-bottom-color:#d8dde1;color:#5a6570">Method</th><th style="border-bottom-color:#d8dde1;color:#5a6570">Storage / year</th><th style="border-bottom-color:#d8dde1;color:#5a6570">Stop shown</th><th style="border-bottom-color:#d8dde1;color:#5a6570">Count updated</th><th style="border-bottom-color:#d8dde1"></th></tr>
{rows}</table>
<p style="font-size:11.5px;color:#5a6570;margin:12px 0 0">Illustrative criteria: ≤ 500 msg/s, ≤ 100 GB/year, stops shown within 5 s, counts updated within 60&nbsp;s</p></div></div>
<p class="note" style="margin-top:14px">Counts are summarised on the machine or gateway and reported as running totals per piece or per minute; state changes are reported separately as soon as they happen; detailed data stays at the edge and is fetched when needed.</p>'''
print(page('fig_19_traffic', body, extra_css='td{padding:12px 8px}th{padding:8px;white-space:nowrap}td+td{white-space:nowrap}'))
