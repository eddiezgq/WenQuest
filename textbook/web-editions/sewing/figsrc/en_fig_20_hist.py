"""English version of fig_20_hist (Fig. 23-4). Monte Carlo re-run with the tol.html model
(seed 7 reproduces panels a and b exactly; seed 20 reproduces the needle-change statistics of panel c)."""
import numpy as np
from en__lib_ch18_23 import *
from en__tolsim import sim

cases = [('a', 'Full interchangeability (no adjustment)', 0, 0, 7),
         ('b', 'Adjusted during assembly', 1, 0, 7),
         ('c', 'Needle changed on the shop floor after adjustment', 1, 1, 20)]
cards, sds = [], []
edges = np.arange(-0.05, 0.19 + 1e-9, 0.0025)
for key, title, adj, swap, seed in cases:
    gs, ok, sd = sim(adj, swap, seed)
    sds.append(sd)
    cnt, _ = np.histogram(gs, edges)
    mids = (edges[:-1] + edges[1:]) / 2
    fig = panel_fig(480, 270)
    ax = fig.add_axes([0.02, 0.12, 0.96, 0.86])
    ax.axvspan(0.04, 0.10, color=GREEN, alpha=0.10, lw=0)
    col = np.where((mids >= 0.04) & (mids <= 0.10), '#3a78d8', '#c9574a')
    ax.bar(mids, cnt, width=0.0025 * 0.94, color=col, lw=0)
    ax.set_xlim(-0.015, 0.155); ax.set_ylim(0, cnt.max() * 1.0)
    ax.set_xticks([0, 0.04, 0.07, 0.10, 0.14]); ax.set_xticklabels(['0.00', '0.04', '0.07', '0.10', '0.14'])
    ax.set_yticks([]); ax.grid(False); ax.set_facecolor('white')
    for sp in ax.spines.values(): sp.set_visible(False)
    fig.set_facecolor('white')
    fig.savefig(os.path.join(PANELS, f'fig_20_hist_{key}.png'), dpi=200, facecolor='white'); plt.close(fig)
    yc = '#1f8a4c' if ok >= 0.99 else '#c4372b'
    cards.append(f'''<div class="card" style="padding:14px 10px 12px;text-align:center">
<div style="font-weight:700;font-size:15.5px;margin-bottom:6px"><span style="margin-right:12px">{key}</span>{title}</div>
<img class="pimg" src="en_panels/fig_20_hist_{key}.png">
<div style="font-weight:700;font-size:15px;color:{yc};margin-top:2px">Yield {ok*100:.1f}%</div></div>''')

body = f'''<p class="title">Same parts, three situations: the distribution of the hook-point clearance</p>
<p class="sub">Monte Carlo simulation of 4000 machines (illustrative values); horizontal axis: clearance (mm); the green band is 0.04–0.10 mm</p>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:48px;padding:0 10px">{''.join(cards)}</div>
<p class="note" style="color:#1b2430;font-size:13.5px;margin-top:60px">σ: interchangeable {sds[0]:.4f} mm; adjusted {sds[1]:.4f} mm; after a needle change {sds[2]:.4f} mm. Interchangeability reaches 99% only if every tolerance is tightened uniformly to 60%, raising cost by about two-thirds; adjustment adds only a few yuan per machine, and the absorbable links can then be relaxed.</p>'''
print(page('fig_20_hist', body))
