"""English version of fig_18_struct (Fig. 18-1): block diagram, HTML + inline SVG."""
from en__lib_ch18_23 import page
from en__svg import *

s = []
s.append('<rect x="47" y="142" width="1094" height="751" rx="14" fill="#fcebea" stroke="#eaa6a2" stroke-width="2"/>')
s.append(text(70, 176, 'High-voltage section (DC link about 310 V)', 19, '#c4372b', 700))
s.append('<rect x="1153" y="142" width="105" height="751" rx="10" fill="none" stroke="#7d8790" stroke-width="1.8" stroke-dasharray="7 5"/>')
s.append(text(1214, 400, 'Isolation barrier', 19, MUTED, 700, 'middle', 'transform="rotate(-90 1214 400)"'))
s.append('<rect x="1270" y="142" width="682" height="751" rx="14" fill="#e9f0fc" stroke="#a9c3ee" stroke-width="2"/>')
s.append(text(1295, 176, 'Low-voltage section (safety extra-low voltage SELV / PELV)', 19, '#2a5fb8', 700))
# top row
row = [(70, 'r', 'Power input', ['AC 220 V', 'fuse, varistor']), (282, 'r', 'EMI filter', ['common-mode choke', 'X, Y capacitors']),
       (494, 'r', 'Rectifier + DC link', ['about 310 V DC', 'electrolytic capacitors']),
       (706, 'r', 'Power module (IPM)', ['six switching devices', '+ drive + protection']),
       (918, 'k', 'Motor', ['three-phase permanent-', 'magnet synchronous motor'])]
for x, c, t, l in row:
    s.append(box(x, 270, 189, 118, c, t, l))
for x in (259, 471, 683, 895):
    s.append(arrow(x + 1, 329, x + 22, 329))
# PWM and sensing lines
s.append(poly([(1316, 212), (800, 212), (800, 266)], '#8a5cc7', 2.2, 'ahp'))
s.append(text(1135, 203, 'PWM (optocoupler / isolator chip)', 14, '#7444b4', 700, 'end'))
s.append(poly([(870, 270), (870, 241), (1312, 241)], '#8a5cc7', 2.2, 'ahp'))
s.append(text(1135, 264, 'Current and voltage sensing (isolated)', 14, '#7444b4', 700, 'end'))
# heat sink, braking, SMPS, solenoids
s.append('<line x1="588" y1="388" x2="588" y2="518" stroke="#d23b30" stroke-width="1.6" stroke-dasharray="5 4"/>')
s.append('<rect x="494" y="424" width="400" height="39" rx="6" fill="#dde1e5" stroke="#7d8790" stroke-width="1.8"/>')
s.append(text(694, 450, 'Aluminium heat sink (often doubles as the enclosure)', 14.5, INK, 700, 'middle'))
s.append(box(494, 518, 189, 105, 'r', 'Braking circuit', ['dissipates energy fed back', 'in an emergency stop']))
s.append(box(730, 518, 387, 140, 'y', 'Switch-mode supply (with transformer)',
             ['from the DC link → 5 V, 3.3 V (control)', '24–30 V (solenoids, pneumatic valves)', 'the transformer itself is an isolation barrier']))
s.append(box(94, 706, 447, 141, 'y', 'Solenoid drivers',
             ['supplied with 24–30 V from the SMPS secondary', '(isolated from the DC link)',
              'trimming, wiping, backtack, presser-foot lift', 'switching device + freewheeling (Chapter 13)']))
s.append('<line x1="541" y1="775" x2="727" y2="637" stroke="#c48a17" stroke-width="1.6" stroke-dasharray="6 4"/>')
s.append('<line x1="1117" y1="588" x2="1270" y2="588" stroke="#c48a17" stroke-width="2.2"/>')
s.append(text(1206, 610, 'LV supply', 13.5, '#b8791c', 700, 'middle'))
# low-voltage blocks
s.append(box(1317, 259, 283, 152, 'b', 'Main controller chip',
             ['current, velocity and position loops', 'process sequences, fault protection', 'watchdog'], ty=31))
s.append(box(1646, 259, 271, 70, 'b', 'Encoder interface', ty=32))
s.append(box(1646, 341, 271, 70, 'b', 'Pedal, sensors', ty=32))
s.append(box(1317, 471, 283, 105, 'b', 'Control panel', ['parameters, stitch counts, fault codes']))
s.append(box(1646, 471, 271, 105, 'b', 'Communication interface', ['networking (Chapter 26),', 'firmware updates']))
s.append(box(1317, 636, 600, 105, 'b', 'Parameter storage (retained without power)',
             ['user parameters + factory calibration, each set with a checksum']))

body = f'''<p class="title">Structure of a servo control box: high-voltage section, low-voltage section and isolation barrier</p>
<p class="sub">Illustrative block diagram (single-phase 220 V, 550 W lockstitch servo control; not a specific product)</p>
{svg(40, 135, 1920, 765, ''.join(s))}
<p class="note" style="color:#1b2430;font-size:13.5px;margin-top:22px">Creepage distances and clearances are kept between the high- and low-voltage sections; signals cross the isolation barrier through optocouplers or isolator chips, and power crosses it through the transformer. The panel, pedal and communication ports that the operator can touch are all in the low-voltage section.</p>
<p class="note" style="margin-top:8px;font-size:13.5px">Standards: ISO 10821, safety of industrial sewing machines; IEC 60204-31 / GB/T 5226.31-2017, electrical equipment of sewing machines (control circuits use SELV or PELV).</p>'''
print(page('fig_18_struct', body))
