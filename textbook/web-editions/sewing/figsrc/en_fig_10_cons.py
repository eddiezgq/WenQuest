"""English version of fig_10_cons: thread consumption ratios (data from Section 10.6)."""
import sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
plt.rcParams['font.family'] = ['DejaVu Sans']
BG, INK, MUT, GRID = '#fbfaf7', '#1f2a36', '#5d6b7a', '#dde1e6'
BLUE, ORANGE, GREY = '#2f6fd6', '#e0662f', '#9aa4ae'
# (code, name, total, needle share or None, model value or None)
rows = [('301', 'Lockstitch', 2.5, 0.5, 2.7), ('101', 'Single-thread chain', 4, None, None), ('401', 'Two-thread chain', 5.5, 0.25, 6.1),
        ('504', 'Three-thread overedge', 14, None, None), ('516', 'Five-thread safety', 20, None, None),
        ('406', '2-needle 3-thread cover', 18, 0.30, 16.8), ('602', '2-needle 4-thread cover', 25, 0.20, 23.2),
        ('605', '3-needle 5-thread cover', 28, 0.30, 31.0)]
W, H = 3400, 1920
fig = plt.figure(figsize=(W / 200, H / 200), dpi=200, facecolor=BG)
ax = fig.add_axes([388 * 1.7 / W, 1 - 885 * 1.7 / H, (1763 - 388) * 1.7 / W, (885 - 165) * 1.7 / H], facecolor=BG)
ax.set_xlim(0, 35); ax.set_ylim(len(rows) - 0.5, -0.5)
for s in ax.spines.values(): s.set_visible(False)
ax.set_xticks(range(0, 36, 5)); ax.grid(axis='x', color=GRID, lw=1); ax.set_axisbelow(True)
ax.tick_params(axis='x', length=0, labelsize=8.5, colors=MUT, pad=10); ax.set_yticks([])
bh = 0.44
for i, (code, name, tot, sh, mod) in enumerate(rows):
    if sh is None:
        ax.add_patch(Rectangle((0, i - bh / 2), tot, bh, color=GREY, lw=0))
    else:
        ax.add_patch(Rectangle((0, i - bh / 2), tot * sh, bh, color=BLUE, lw=0))
        ax.add_patch(Rectangle((tot * sh, i - bh / 2), tot * (1 - sh), bh, color=ORANGE, lw=0))
    lab = f'{tot:g}'
    if mod is not None:
        ax.plot(mod, i, marker='d', ms=15, mfc='white', mec=INK, mew=1.4, zorder=5)
        xt = max(tot, mod) if mod <= tot + 0.6 else tot
        ax.text(xt + (0.5 if mod <= tot else 0.3), i, lab, va='center', fontsize=10, fontweight='bold', color=INK) if False else None
    # value label after bar (or after diamond when the diamond is just past the bar)
    vx = (mod + 0.55) if (mod is not None and tot < mod < tot + 1.5) else tot + 0.3
    ax.text(vx, i + 0.02, lab, va='center', fontsize=10, fontweight='bold', color=INK)
    if mod is not None:
        mx = max(vx + 1.6, mod + 2.1)
        ax.text(mx, i + 0.02, f'(model {mod:.1f})', va='center', fontsize=9, color=MUT)
    ax.text(-0.45, i, code, va='center', ha='right', fontsize=12.5, fontweight='bold', color=INK, transform=ax.transData)
    ax.text(-2.15, i, name, va='center', ha='right', fontsize=9, color=MUT)
ax.set_xlabel('Consumption ratio (cm thread / cm seam)', fontsize=9.5, color=MUT, labelpad=8)
fx = lambda x: x * 1.7 / W; fy = lambda y: 1 - y * 1.7 / H
fig.text(fx(47), fy(50), 'Thread consumption ratio of each stitch: centimetres of thread per 1 cm of seam', fontsize=15.5, fontweight='bold', color=INK, va='center')
fig.text(fx(47), fy(91), 'Bars: a thread maker’s consumption guide (7 stitches/cm, minimum under stated conditions, plus 10–15% wastage); open diamonds: this chapter’s illustrative geometric model (fabric 0.5 mm)',
         fontsize=9.6, color=MUT, va='center')
for x, y, c, t in [(1470, 146, BLUE, 'Needle thread'), (1470, 172, ORANGE, 'Looper / bobbin / cover thread'), (1470, 198, GREY, 'Split not given in the source')]:
    fig.patches.append(Rectangle((fx(x), fy(y) - 0.0045), fx(22), 0.009 * 1.0, transform=fig.transFigure, color=c, lw=0))
    fig.text(fx(x + 30), fy(y), t, fontsize=9, color=INK, va='center')
fig.text(fx(47), fy(1028), 'Chainstitches use more than twice as much thread as lockstitch, coverstitches nearly ten times as much: most of the thread is in the “net” on the back. A T-shirt hem plus cuffs is',
         fontsize=9.6, color=INK, va='center')
fig.text(fx(47), fy(1056), 'about 1.7 m; in 406 that takes about 31 m of thread (without wastage). The ratio also varies with stitch density, fabric thickness and tension; model and source differ by up to ±12%, so such figures are estimates only.',
         fontsize=9.6, color=INK, va='center')
fig.savefig(sys.argv[1] if len(sys.argv) > 1 else 'img/en/fig_10_cons.png', facecolor=BG)
