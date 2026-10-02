"""English version of fig_18_test (Fig. 18-6): test flow + schematic bathtub curve, HTML + inline SVG."""
import math
from en__lib_ch18_23 import page
from en__svg import *

s = []
steps = [('k', 'SMT soldering', []), ('b', 'AOI', ['wrong or skewed parts,', 'bridges, too little solder']),
         ('b', 'In-circuit test ICT', ['bed of nails, one by one:', 'values, polarity']), ('k', 'Program flashing', []),
         ('b', 'Functional test FCT', ['simulated motor, encoder,', 'pedal, solenoids']),
         ('r', 'Hot burn-in', ['under load, power cycling,', 'screens early failures']),
         ('p', 'Retest + safety', ['functional retest, earth,', 'insulation, withstand']),
         ('g', 'Machine running-in', ['fitted to a sewing machine,', 'real sewing']), ('k', 'Shipment', [])]
for k, (c, t, l) in enumerate(steps):
    x = 35 + k * 216.5
    s.append(box(x, 142, 190, 128, c, t, l, tsize=16, lsize=13, ty=32))
    if k < 8:
        s.append(arrow(x + 192, 206, x + 215, 206, '#5a6570', 2.4))
# bathtub card
s.append('<rect x="142" y="318" width="1763" height="610" rx="12" fill="#fff" stroke="#d8dde1" stroke-width="1.6"/>')
s.append('<rect x="165" y="352" width="223" height="541" fill="#fbecec"/>')
s.append('<rect x="388" y="352" width="1012" height="541" fill="#f1f7f4"/>')
s.append('<rect x="1400" y="352" width="482" height="541" fill="#f8f2ec"/>')
pts = []
for i in range(0, 1715, 4):
    x = 168 + i
    y = 850 - 392 * math.exp(-(x - 168) / 85) - (488 * ((x - 1400) / 482) ** 3 if x > 1400 else 0)
    pts.append((round(x, 1), round(y, 1)))
s.append(poly(pts, '#2a6fdb', 3))
s.append('<line x1="250" y1="528" x2="250" y2="893" stroke="#d23b30" stroke-width="1.8" stroke-dasharray="7 5"/>')
s.append('<polyline points="165,352 165,893 1882,893" fill="none" stroke="#1b2430" stroke-width="2"/>')
for k, l in enumerate(['Early failures', 'poor solder joints,', 'component defects,', 'assembly damage;', 'rate falls with time']):
    s.append(text(186, 388 + k * 26, l, 14.5, '#c4372b', 700))
for k, l in enumerate(['Burn-in “uses up”', 'this stretch in', 'the factory']):
    s.append(text(272, 647 + k * 24, l, 14.5, '#c4372b', 700))
s.append(text(886, 388, 'Random failures', 15, '#1f8a4c', 700, 'middle'))
s.append(text(886, 414, 'low, roughly constant failure rate', 15, '#1f8a4c', 700, 'middle'))
for k, l in enumerate(['Wear-out failures', 'capacitors drying out,', 'solder-joint fatigue']):
    s.append(text(1641, 388 + k * 26, l, 15, '#b8791c', 700, 'middle'))
s.append(text(130, 625, 'Failure rate', 15, MUTED, 400, 'middle', 'transform="rotate(-90 130 625)"'))
s.append(text(1023, 922, 'Time in service', 15, MUTED, 400, 'middle'))

body = f'''<p class="title">Production test flow and the bathtub curve</p>
<p class="sub">Illustrative; every circuit board carries a barcode, and the test data are archived by barcode</p>
{svg(30, 135, 1935, 800, ''.join(s))}
<p class="note" style="color:#1b2430;font-size:13.5px;margin-top:20px">Burn-in is done at elevated temperature to make defects show up faster; the acceleration factor is estimated with the Arrhenius relation. The temperature must not exceed the components’ ratings; the longer the burn-in, the more thorough the screening and the higher the cost (Virtual lab 18-1, page ②).</p>'''
print(page('fig_18_test', body))
