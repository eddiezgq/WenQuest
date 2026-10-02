import sys; sys.path.insert(0, '/home/claude/sm/figsrc'); from en_relabel_lib import Fig
import numpy as np
f = Fig('/home/claude/book/img/fig_12_dispatch.png')
f.label((45, 30, 540, 72), 'Dispatching in a hanger system: rules and the WIP limit', bold=True)
f.label((45, 78, 1168, 106), 'Simulation example: T-shirt with 6 operations (260 s standard time in total), 10 operators of differing skills, 4 h, average of 5 runs; times, skills and efficiencies are illustrative')
# legend: move the second swatch right to make room for the longer first entry
S = f.S; x0, y0, x1, y1 = [int(v * S) for v in (328, 196, 350, 218)]
sw = f.a[y0:y1, x0:x1].copy()
f.erase((211, 196, 284, 218)); f.erase((326, 195, 526, 219), full=True)
f.text((214.1, 206.5), 'All operators present', 14.5, color=(31, 42, 54))
f.text((425.9, 206.5), 'Operator 5 absent for 1 h', 14.5, color=(31, 42, 54))
nx = int(398 * S); f.a[y0:y1, nx:nx + (x1 - x0)] = sw
for x, t in ((321.5, 'Fixed work centre'), (556.5, 'Shortest queue'), (791.5, 'Earliest finish')):
    f.label((x - 40, 837, x + 40, 859), t, bold=True, anchor='c', size=15)
f.label((78, 458, 102, 567), 'Output (pieces/h)', rot=90, size=14.5)
f.label((973, 458, 997, 567), 'Output (pieces/h)', rot=90, size=14.5)
f.label((1733, 241, 1830, 263), 'Output (left axis)', bold=True, anchor='c', size=14.5, fix=[('v', 1764.4, 239, 265, 380, 0.3)])
f.label((1686, 475, 1888, 497), ['Average throughput time', '(right axis, 0–2000 s)'], bold=True, anchor='r', size=14.5, lh=21, fix=[('v', 1764.4, 473, 499, 380, 0.3)], dy=8)
f.label((1393, 863, 1562, 885), 'WIP limit (number of carriers)', anchor='c', size=15)
f.label((43, 911, 1152, 963), [
    'Dynamic dispatching (shortest queue, earliest finish) produces about 13% more than fixed work centres; the gap widens when someone is absent, because the system passes the work to others who can do that operation.',
    'Beyond a WIP limit of about 20–25 carriers output no longer rises, while throughput time grows in proportion to WIP (Little’s law): set the limit where the output curve just levels off.'],
    size=14, lh=27, wrap=1900, ytop=True)
f.save('/home/claude/sm/img/en/fig_12_dispatch.png')
