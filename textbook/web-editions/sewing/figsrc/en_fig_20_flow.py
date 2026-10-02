"""English version of fig_20_flow (Fig. 23-1): HTML + inline SVG."""
from en__lib_ch18_23 import page
from en__svg import *

s = []
steps = [('k', 'Design inputs', ['speed, stitch length, fabrics,', 'noise, price, standards']),
         ('b', 'Concept and detailed design', ['mechanism calculations, 3D models,', 'part drawings and tolerances']),
         ('b', 'Design review', ['manufacturability, assemblability,', 'serviceability']),
         ('o', 'Prototypes and testing', ['performance, vibration, noise,', 'life tests']),
         ('g', 'Pilot batch', ['tooling, processes, inspection,', 'yield statistics']),
         ('g', 'Volume production', ['process control,', 'after-sales feedback'])]
for k, (c, t, l) in enumerate(steps):
    x = 47 + k * 324.8
    s.append(box(x, 153, 277, 141, c, t, l, tsize=17, lsize=13.5, ty=33))
    if k < 5:
        s.append(arrow(x + 280, 223, x + 322, 223, '#5a6570', 2.4))
s.append(poly([(1159, 294), (1159, 352), (510, 352), (510, 298)], '#d23b30', 2.2, 'ah', '7 5'))
s.append(text(830, 380, 'Problems found in testing → drawings changed (often several rounds)', 15, '#c4372b', 700, 'middle'))
s.append('<rect x="142" y="436" width="1786" height="363" rx="12" fill="#fff" stroke="#d8dde1" stroke-width="1.6"/>')
s.append(text(165, 463, 'Relative cost of one design change (log scale, illustrative)', 16, INK, 700))
bars = [(1, 6, '#efc3bf', 'Drawing stage'), (5, 89, '#e3a8a0', 'After tooling is made'), (10, 128, '#da8b82', 'Prototype testing'),
        (30, 189, '#d27064', 'Pilot batch'), (100, 256, '#c9574a', 'After market launch')]
for k, (v, h, c, lab) in enumerate(bars):
    cx = 339 + k * 348
    s.append(f'<rect x="{cx-87}" y="{752-h}" width="174" height="{h}" fill="{c}"/>')
    s.append(text(cx, 752 - h - 12, f'×{v}', 18, INK, 700, 'middle'))
    s.append(text(cx, 781, lab, 15.5, MUTED, 400, 'middle'))

body = f'''<p class="title">From drawings to volume production: the earlier a problem is found, the cheaper it is to fix</p>
<p class="sub">Illustrative</p>
{svg(40, 135, 1920, 680, ''.join(s))}
<p class="note" style="color:#1b2430;font-size:13.5px;margin-top:22px">Calculations and reviews in the design stage, and tests in the prototype stage, are all ways of finding problems early, at lower cost.</p>'''
print(page('fig_20_flow', body))
