"""English version of fig_19_events (Fig. 26-2). The 15-minute event stream is one random draw of the lab's
model (src/zh/labs/iot.html); the tick positions are digitised from the original image so the English figure
shows the same events."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en__lib_ch26_28 import *
from PIL import Image

im = Image.open('/home/claude/book/img/fig_19_events.png').convert('RGB')
X0, X15 = 299, 3278
T = lambda x: (x - X0) / (X15 - X0) * 15


def runs(y, test):
    r = []; inb = False
    for x in range(250, 3330):
        t = test(im.getpixel((x, y)))
        if t and not inb: inb = True; a = x
        if not t and inb: inb = False; r.append((T(a), T(x)))
    return r


blue = runs(357, lambda c: c[2] > 180 and c[0] < 150)
org = runs(561, lambda c: c[0] > 180 and c[1] < 150 and c[2] < 100)
brk = runs(760, lambda c: c[0] > 180 and 90 < c[1] < 140 and 80 < c[2] < 130)
brk = [r for r in brk if r[1] - r[0] > 0.3]
wait = runs(940, lambda c: abs(c[0] - 187) < 12 and abs(c[2] - 197) < 12)

fig = panel_fig(1120, 300)
ax = fig.add_axes([0.105, 0.1, 0.875, 0.88])
ax.set_xlim(-0.05, 15.05); ax.set_ylim(-0.3, 4.15); ax.axis('off')
rows = {'run': 3.3, 'trim': 2.3, 'brk': 1.3, 'wait': 0.3}
for y in rows.values():
    ax.plot([0, 15], [y, y], color=FRAME, lw=0.8, zorder=0)
for a, b in blue:
    ax.add_patch(plt.Rectangle((a, rows['run']), max(b - a, 0.02), 0.45, color='#4e84db', lw=0))
for a, b in org:
    ax.plot([(a + b) / 2] * 2, [rows['trim'] + 0.02, rows['trim'] + 0.47], color=ORANGE, lw=1.4)
for a, b in brk:
    ax.add_patch(plt.Rectangle((a, rows['brk']), b - a, 0.45, color='#d27368', lw=0))
    ax.text(b + 0.08, rows['brk'] + 0.22, 'Thread break: 1 min stop; one extra trim when sewing restarts',
            color=RED, fontsize=8, fontweight='bold', va='center')
for a, b in wait:
    ax.add_patch(plt.Rectangle((a, rows['wait']), b - a, 0.45, color='#bbc1c5', lw=0))
    ax.text(b + 0.08, rows['wait'] + 0.22, 'Waiting: previous operation\nhas not delivered',
            color='#5d6b7a', fontsize=8, fontweight='bold', va='center')
for lab, key, c in [('Main shaft\nrunning', 'run', '#2f6fd6'), ('Trimming', 'trim', ORANGE),
                    ('Thread break', 'brk', RED), ('Waiting for\nwork', 'wait', '#5d6b7a')]:
    ax.text(-0.15, rows[key] + 0.22, lab, color=c, fontsize=9, fontweight='bold', ha='right', va='center')
for m in range(0, 16, 3):
    ax.text(m, -0.22, f'{m} min', color=MUTED, fontsize=8.5, ha='center', va='center')
p = save_panel(fig, 'events.png')

s = shift()
body = f'''<p class="title">A quarter of an hour on one lockstitch machine: the events the controller “sees”</p>
<p class="sub">Worked example (illustrative): standard minute value 0.6 min, 3 seams per piece, each with one stop part-way, efficiency 85%; one thread break at about 5 min, waiting for work from about 9 min</p>
<img class="pimg" src="{p}">
<p class="note" style="margin-top:6px">In this quarter of an hour: main shaft running about 3.2 min (22%), 47 trims, i.e. 15.7 pieces counted by trims.<br>
The controller knows every start, stop and trim, but not which piece is being sewn or why the machine stopped — that comes from work tickets, hanger-carrier IDs and the operator choosing a stop reason on the terminal.</p>'''
print(page('fig_19_events', body))
