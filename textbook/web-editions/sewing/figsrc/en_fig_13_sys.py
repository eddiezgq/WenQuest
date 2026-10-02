import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
# Layout follows the original figure (original display coordinates × 0.6).
S = 0.6
def r(x0, y0, x1, y1): return [(x0 - 47) * S, (y0 - 140) * S, (x1 - x0) * S, (y1 - y0) * S]
def box(rect, cls, title, sub, extra=''):
    x, y, w, h = rect
    return (f'<div class="box {cls}" style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px;'
            f'display:flex;flex-direction:column;justify-content:center;{extra}"><b>{title}</b><span>{sub}</span></div>')
left = [('Main-shaft encoder', 'angle, speed, needle up / down'),
        ('Pedal sensor', 'how far pressed → speed command'),
        ('Thread-break detection', 'check spring not moving / photoelectric'),
        ('Bobbin-thread monitor', 'reflection from the side of the bobbin'),
        ('Fabric thickness / edge', 'presser-foot height, photoelectric'),
        ('Operator panel', 'stitch length, tension, programs')]
right = [('b', 'Main-shaft servo motor', '400 W direct drive, AC PMSM (13.2)'),
         ('b', 'Feed stepper motor', 'electronic stitch length, reverse (13.5, Ch. 14)'),
         ('o', 'Electronic tension assembly', 'needle-thread tension set by magnetic force (Ch. 7, 14)'),
         ('o', 'Trimming solenoid', 'moving knife, thread wiper (13.6, Ch. 14)'),
         ('o', 'Foot-lift solenoid / cylinder', 'automatic foot lift (13.6)'),
         ('o', 'Presser-foot pressure actuator', 'stepper or solenoid (Ch. 14)')]
tops = [153, 300, 447, 594, 741, 888]
h = []
for (t, sub), y in zip(left, tops):
    h.append(box(r(47, y, 435, y + 113), 'g', t, sub))
for (c, t, sub), y in zip(right, tops):
    h.append(box(r(1528, y, 1952, y + 113), c, t, sub))
x, y, w, hh = r(611, 177, 1387, 999)
h.append(f'<div style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{hh:.0f}px;border:2px solid #1b2430;border-radius:12px;background:#f3f5f6"></div>')
h.append(f'<div style="position:absolute;left:{x:.0f}px;top:{y+12:.0f}px;width:{w:.0f}px;text-align:center;font-weight:700;font-size:17px">Control box</div>')
h.append(box(r(658, 259, 1340, 399), 'k', 'Main controller', 'MCU / DSP, or ARM + FPGA (13.8)<br>reads the encoder, computes the speed profile, triggers each action by shaft angle'))
h.append(box(r(658, 435, 988, 587), 'b', 'Servo drive', 'vector control, three loops,<br>inverter (13.2, 13.7)'))
h.append(box(r(1011, 435, 1340, 587), 'b', 'Stepper drive', 'microstepping current (13.5)'))
h.append(box(r(658, 623, 988, 775), 'o', 'Solenoid drive', 'MOSFET, boost,<br>freewheeling (13.6)'))
h.append(box(r(1011, 623, 1340, 775), 'k', 'Communication', 'panel, networking<br>RS-485 / CAN (13.8, Ch. 26)', 'border-color:#5a6570'))
h.append(box(r(658, 811, 1340, 963), 'y', 'Power supply', 'rectifier → DC-link capacitor → braking resistor; plus 24 V, 5 V and other low-voltage supplies (13.7)'))
# arrows (original display coordinates)
L = [(437, 210, 610, 445), (437, 357, 610, 493), (437, 504, 610, 540), (437, 651, 610, 590), (437, 798, 610, 637), (437, 945, 610, 687)]
R = [(1389, 445, 1527, 210, C['blue']), (1389, 493, 1527, 357, C['blue']), (1389, 540, 1527, 504, C['orange']),
     (1389, 590, 1527, 651, C['orange']), (1389, 637, 1527, 798, C['orange']), (1389, 687, 1527, 945, C['orange'])]
sv = [arrow_defs((('ag', '#5a6570'),))]
for a, b, c, d in L:
    sv.append(f'<line x1="{(a-47)*S:.1f}" y1="{(b-140)*S:.1f}" x2="{(c-47)*S:.1f}" y2="{(d-140)*S:.1f}" stroke="{C["green"]}" stroke-width="1.8" marker-end="url(#ag)"/>')
for a, b, c, d, col in R:
    sv.append(f'<line x1="{(a-47)*S:.1f}" y1="{(b-140)*S:.1f}" x2="{(c-47)*S:.1f}" y2="{(d-140)*S:.1f}" stroke="{col}" stroke-width="1.8" marker-end="url(#ag)"/>')
H = (1010 - 140) * S
body = f'''<p class="title">Motors, actuators and sensors in an electronically controlled lockstitch machine</p>
<p class="sub">Illustrative. Left: sensors (inputs); middle: control box; right: actuators (outputs). Section or chapter where each is covered in brackets</p>
<div style="position:relative;height:{H:.0f}px;margin-top:6px">{''.join(h)}
<svg width="1140" height="{H:.0f}" style="position:absolute;left:0;top:0;overflow:visible">{''.join(sv)}</svg></div>
<p class="note" style="color:#1b2430;font-size:13px;margin-top:22px">A manufacturer’s direct-drive lockstitch machine: a 400 W AC servo motor is mounted directly on the main shaft; feed, needle-thread tension and presser-foot pressure are all program-controlled; rated power 520 VA.</p>'''
render('fig_13_sys', body, extra_css='.box b{font-size:14.5px}.box span{font-size:12px;line-height:1.4}')
