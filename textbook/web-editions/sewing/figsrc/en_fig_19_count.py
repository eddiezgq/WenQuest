"""English version of fig_19_count (Fig. 26-6): counting errors of three methods. Model: src/zh/labs/iot.html."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en__lib_ch26_28 import *
import numpy as np

s = shift()
act = s['pieces']; trim = s['estTrim']; ticket = act * (1 - 0.02); hanger = act

# (a) bars
fig = panel_fig(560, 330); ax = fig.add_axes([0.1, 0.13, 0.88, 0.8])
labs = ['Actual', 'By trims', 'Work tickets', 'Hanger carriers']
vals = [act, trim, ticket, hanger]; cols = [B_DARK, B_ORANGE, B_OCHRE, B_GREEN]
ax.bar(range(4), [v - 520 for v in vals], bottom=520, width=0.55, color=cols, alpha=0.95)
for i, v in enumerate(vals):
    t = f'{v:.0f}' if i == 0 else f'{v:.0f} ({(v / act - 1) * 100:+.1f}%)'
    ax.text(i, v + 2, t, ha='center', va='bottom', fontsize=9.5, fontweight='bold', color=INK)
ax.set_ylim(520, 600); ax.set_yticks([520, 540, 560, 580, 600]); ax.set_xlim(-0.55, 3.55)
ax.set_xticks(range(4)); ax.set_xticklabels(labs); ax.grid(axis='x', visible=False)
ax.set_ylabel('Pieces counted')
ax.set_title('a   One shift, three ways of counting', pad=8)
pa = save_panel(fig, 'count_a.png')

# (b) over-count by trims vs seams per piece
fig = panel_fig(560, 330); ax = fig.add_axes([0.1, 0.17, 0.88, 0.76])
n = np.arange(1, 9)
for p, c, lab in [(0.10, RED, '10%'), (0.05, ORANGE, '5% (worked example)'), (0.02, GREEN, '2%')]:
    e = (p / n + s['nb'] / (n * act)) * 100
    ax.plot(n, e, color=c, lw=2, label=lab)
lg = ax.legend(title='Extra-trim probability', loc='upper right', frameon=True, fontsize=8.5, title_fontsize=8.5, edgecolor=FRAME)
for t, c in zip(lg.get_texts(), [RED, ORANGE, GREEN]): t.set_color(c); t.set_fontweight('bold')
lg.get_title().set_color(MUTED)
ax.axhline(1, color='#6b7785', lw=1, ls=(0, (4, 3)))
ax.text(1.08, 1.12, 'error 1%', color=MUTED, fontsize=8, va='bottom')
ax.set_xlim(1, 8); ax.set_ylim(0, 14); ax.set_xticks(n)
ax.set_xlabel('Seams per piece (trim at the end of each seam)'); ax.set_ylabel('Over-count by trims (%)')
ax.set_title('b   Fewer seams per piece: one extra trim matters more', pad=8)
pb = save_panel(fig, 'count_b.png')

body = f'''<p class="title">Case: counting errors of three methods</p>
<p class="sub">Worked example (illustrative): about 569 pieces actually made; 3 seams per piece; 5% chance of an extra trim from rework, about 11 thread breaks; work tickets per bundle of 20 pieces, 2% missed scans</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px"><img class="pimg" src="{pa}"><img class="pimg" src="{pb}"></div>
<p class="note">Count pieces by hanger carriers or work tickets, and use the trim count and main-shaft running time to check that the figure is plausible; a high trim count shows that rework and thread breaks have increased at this operation.</p>'''
print(page('fig_19_count', body))
