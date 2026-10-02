"""English version of fig_20_measure (Fig. 23-5). Left: HTML/SVG; right: single-DOF frequency response (fn 190 Hz, zeta 0.03)."""
import numpy as np
from en__lib_ch18_23 import *
from en__svg import *

f = np.linspace(0, 400, 2001); r = f / 190
A = 1 / np.sqrt((1 - r ** 2) ** 2 + (2 * 0.03 * r) ** 2)
fig = panel_fig(820, 560)
ax = fig.add_axes([0.09, 0.13, 0.88, 0.80])
ax.set_title('Frequency response of the arm from a modal test (illustrative)', pad=12, fontsize=12.5)
ax.plot(f, A, color='#b8791c', lw=2)
ax.axvline(190, color=RED, lw=1, ls=(0, (4, 3)))
ax.text(195, 18.6, 'Arm first bending mode 190 Hz (illustrative)', color=RED, fontsize=10.5, weight='bold', va='top')
f5, f55 = 5000 * 2 / 60, 5500 * 2 / 60
ax.plot([f5, f5], [0, 1.7], color=GREEN, lw=2.5); ax.plot([f55, f55], [0, 1.7], color=RED, lw=2.5)
ax.annotate('5000 r/min, 2nd order', (f5, 1.8), xytext=(40, 4.2), color=GREEN, fontsize=10, weight='bold', arrowprops=dict(arrowstyle='-', color=GREEN, lw=0.8))
ax.annotate('5500 r/min, 2nd order', (f55, 1.8), xytext=(228, 6.2), color=RED, fontsize=10, weight='bold', arrowprops=dict(arrowstyle='-', color=RED, lw=0.8))
ax.set_xlim(0, 400); ax.set_ylim(0, 20); ax.set_yticks(range(0, 21, 5)); ax.set_xticks(range(0, 401, 100))
ax.set_xlabel('Frequency (Hz)'); ax.set_ylabel('Amplification factor')
pb = save_panel(fig, 'fig_20_measure_b.png')

O, G, B = '#e0662f', '#b8791c', '#2a6fdb'
s = []
s.append('<rect x="47" y="142" width="1035" height="705" rx="14" fill="#fff" stroke="#d8dde1" stroke-width="1.6"/>')
s.append(text(85, 230, 'Microphone (operator’s ear position)', 15, '#c4531d', 700))
s.append(f'<line x1="176" y1="270" x2="176" y2="352" stroke="{O}" stroke-width="2.4"/><circle cx="176" cy="258" r="17" fill="{O}"/>')
s.append('<polygon points="212,612 212,352 258,305 823,305 823,388 753,388 753,612" fill="#eef1f4" stroke="#1b2430" stroke-width="2.4"/>')
s.append(text(529, 352, 'Arm', 16, INK, 700, 'middle'))
s.append('<rect x="188" y="506" width="94" height="106" rx="8" fill="#eef1f4" stroke="#1b2430" stroke-width="2.4"/>')
s.append('<rect x="141" y="612" width="800" height="46" rx="4" fill="#dacdb1" stroke="#a89a7c" stroke-width="1.6"/>')
s.append('<line x1="235" y1="612" x2="235" y2="660" stroke="#1b2430" stroke-width="2.4"/>')
s.append(text(541, 641, 'Table top', 15, MUTED, 700, 'middle'))
for x, y, lab, lx, ly in [(257, 302, 'Head front end', 270, 293), (516, 281, 'Arm middle', 530, 272), (787, 325, 'Pillar', 800, 317)]:
    s.append(f'<rect x="{x}" y="{y}" width="27" height="22" rx="3" fill="{B}"/>')
    s.append(text(lx, ly, lab, 13.5, '#2a5fb8', 700, 'middle'))
s.append(f'<rect x="300" y="411" width="12" height="12" fill="{B}"/>')
s.append(text(320, 423, 'Accelerometers: measure vibration and spectrum', 15, '#2a5fb8', 700))
s.append(f'<line x1="965" y1="300" x2="893" y2="352" stroke="{G}" stroke-width="4" stroke-linecap="round"/><circle cx="978" cy="291" r="15" fill="{G}"/>')
s.append(arrow(928, 335, 832, 352, '#5a6570', 1.8))
s.append(text(940, 264, 'Impact hammer', 15, G, 700, 'middle'))
for k, l in enumerate(['Vibration: overall level + spectrum (first order, second order …) → identify the source',
                       'Noise: sound pressure level at the workstation (what the worker hears); sound power level',
                       '(radiated by the machine, used for comparison)',
                       'Modal testing: hammer impact + response → natural frequencies and mode shapes; finite elements too']):
    s.append(text(83, 712 + k * 30, l, 15, INK))

body = f'''<p class="title">Vibration, noise and modes: how they are measured</p>
<p class="sub">Illustrative; vibration per QB/T 1178-2006, noise per ISO 10821 / ISO 11204 (emission sound pressure level at the workstation)</p>
<div style="display:grid;grid-template-columns:888px 1fr;gap:24px;align-items:start">
{svg(40, 135, 1050, 720, ''.join(s))}
<img class="pimg" src="{pb}"></div>
<p class="note" style="color:#1b2430;font-size:13.5px;margin-top:10px">In design, the first- and second-order excitation frequencies over the working speed range must be kept away from the natural frequencies of the structure.</p>'''
print(page('fig_20_measure', body))
