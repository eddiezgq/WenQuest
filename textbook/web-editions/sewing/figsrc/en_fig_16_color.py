# Fig. 16-4 (English): colour-change timing (illustrative), Gantt-style lanes as inline SVG
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
X0, X1, T1 = 150, 1130, 6.0
X = lambda t: X0 + (X1 - X0) * t / T1
lanes = [
    ('Main shaft', '#2f6fd8', '#5f8fe0', [(0, 0.8, 'Slow to trim speed'), (0.8, 1.1, 'Trim stitch'), (4.2, 5.0, 'Slow start'), (5.0, 6.0, 'Accelerate')]),
    ('Trim / wipe', '#e0662f', '#e88a5f', [(0.85, 1.15, 'Trim'), (1.2, 1.45, 'Wipe')]),
    ('Needle-bar case shift', '#8a44b8', '#a670c4', [(1.5, 4.0, 'Move to the needle bar of the next colour (2–3 s)')]),
    ('Needle-bar jump solenoid', '#b07a12', '#c89a50', [(3.98, 4.18, 'Select new needle bar')]),
    ('Embroidery frame', '#2e9e5b', '#5fb47f', [(0, 1.1, 'Follows the stitches'), (4.2, 6.0, 'Follows the stitches')]),
]
sv = [f'<svg width="1170" height="{70+len(lanes)*56}" viewBox="0 0 1170 {70+len(lanes)*56}" style="display:block;overflow:visible">']
for i, (name, tc, fc, bars) in enumerate(lanes):
    y = 20 + i * 56
    sv.append(f'<text x="0" y="{y+14}" font-size="13.5" font-weight="700" fill="{tc}">{esc(name)}</text>')
    sv.append(f'<line x1="{X0}" y1="{y+21}" x2="{X1}" y2="{y+21}" stroke="#d8dde1" stroke-width="1"/>')
    for a, b, lab in bars:
        sv.append(f'<rect x="{X(a):.1f}" y="{y}" width="{X(b)-X(a):.1f}" height="21" rx="3" fill="{fc}"/>')
        sv.append(f'<text x="{(X(a)+X(b))/2:.1f}" y="{y+37}" font-size="11" font-weight="700" fill="{tc}" text-anchor="middle">{esc(lab)}</text>')
yb = 20 + len(lanes) * 56 + 18
for t in range(7):
    sv.append(f'<text x="{X(t):.1f}" y="{yb}" font-size="11" fill="#5a6570" text-anchor="middle">{t:.1f} s</text>')
sv.append('</svg>')
body = f'''<p class="title">Colour change: trim, needle stop, needle-bar case shift, slow start</p>
<p class="sub">Illustrative timing (times are illustrative values). All heads change to the same colour at the same time; the embroidery frame stays still during the change</p>
<div style="margin-top:34px">{''.join(sv)}</div>
<p class="note" style="color:#1b2430;font-size:12.5px;margin-top:10px">The needle-bar case shift takes about 2–3 s; with slowing down, trimming and restarting, one colour change takes about 6 s (illustrative). A design with 10 colours changes colour 9 times; add trims and jumps, and the non-sewing time cannot be ignored.</p>'''
render('fig_16_color', body, width=1200)
