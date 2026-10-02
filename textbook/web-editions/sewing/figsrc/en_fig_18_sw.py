"""English version of fig_18_sw (Fig. 18-5): HTML + inline SVG."""
from en__lib_ch18_23 import page
from en__svg import *

s = []
layers = [(165, 'p', 'User-interface and communication layer', 'every few tens of ms', 'control panel, parameters, networking, firmware updates'),
          (306, 'g', 'Process layer', 'by main-shaft angle / ms', 'start backtack, trimming, wiping, colour change, pattern interpolation (Chapters 14–17)'),
          (447, 'b', 'Motion-control layer', 'current loop about 0.1 ms', 'current, velocity and position loops (Chapter 13)'),
          (588, 'k', 'Driver layer', 'interrupt-driven', 'PWM, A/D conversion, encoder interface, serial ports, memory')]
for y, c, t, per, l in layers:
    st, tc = C[c]
    s.append(f'<rect x="70" y="{y}" width="730" height="117" rx="10" fill="#fff" stroke="{st}" stroke-width="2.6"/>')
    s.append(text(94, y + 40, t, 19, tc, 700))
    s.append(text(776, y + 40, per, 14.5, MUTED, 700, 'end'))
    s.append(text(94, y + 77, l, 14.5, INK))
s.append(arrow(822, 705, 822, 187, '#5a6570', 2.4))
for k, l in enumerate(['Higher up:', 'slower,', 'more', 'flexible']):
    s.append(text(834, 400 + k * 23, l, 14.5, MUTED))
s.append(arrow(929, 188, 929, 706, '#d23b30', 2.4))
s.append('<path d="M920,697 l9,12 l9,-12 z" fill="#5a6570"/>')
for k, l in enumerate(['Lower down:', 'faster,', 'stricter', 'timing']):
    s.append(text(940, 547 + k * 23, l, 14.5, '#c4372b'))
for k, l in enumerate(['Protection runs through every layer: overvoltage, undervoltage, overcurrent, stall, encoder loss,',
                       'overtemperature → limit speed or switch off the outputs, show a fault code; at power-up check that the pedal',
                       'is in neutral and the head is not tilted back, to prevent unexpected start-up; the watchdog resets a runaway',
                       'program and first switches off PWM.']):
    s.append(text(70, 747 + k * 26, l, 14.5, INK))
# right card
s.append('<rect x="1083" y="153" width="869" height="658" rx="14" fill="#fff" stroke="#d8dde1" stroke-width="1.8"/>')
s.append(text(1106, 190, 'Dual-bank firmware update', 19, INK, 700))
s.append('<rect x="1117" y="224" width="188" height="352" rx="8" fill="#f3f5f6" stroke="#1b2430" stroke-width="2"/>')
s.append(box(1129, 236, 165, 57, 'k', 'Bootloader', fill='#e3e7ea', tsize=15.5, ty=35, sw=1.6, rx=5))
s.append(f'<rect x="1129" y="306" width="165" height="117" rx="5" fill="#eaf6ee" stroke="#2e9e5b" stroke-width="1.6"/>')
s.append(text(1211, 355, 'Program bank A', 15.5, '#1f8a4c', 700, 'middle') + text(1211, 380, '(running)', 15, '#1f8a4c', 700, 'middle'))
s.append(f'<rect x="1129" y="435" width="165" height="117" rx="5" fill="#fcefe8" stroke="#e0662f" stroke-width="1.6"/>')
s.append(text(1211, 484, 'Program bank B', 15.5, '#c4531d', 700, 'middle') + text(1211, 509, '(new version', 15, '#c4531d', 700, 'middle')
         + text(1211, 530, 'being written)', 15, '#c4531d', 700, 'middle'))
s.append(text(1211, 602, 'Memory', 14, MUTED, 400, 'middle'))
steps = [('y', '① Write the new firmware completely into bank B'), ('y', '② Verify bank B (checksum, signature)'),
         ('b', '③ Only if it passes, switch the boot flag to B'), ('b', '④ Restart: the bootloader checks bank B'),
         ('g', '⑤ OK → run B; fault → fall back to A')]
for k, (c, t) in enumerate(steps):
    y = 247 + k * 73
    s.append(box(1364, y, 553, 54, c, t, tsize=16, ty=34, align='start'))
    if k < 4:
        s.append(arrow(1640, y + 54, 1640, y + 71, '#5a6570', 1.8))
s.append(text(1117, 659, 'Power failure at any step: the boot flag still points to A and the machine', 15, INK))
s.append(text(1117, 687, 'starts on the old version as usual; the bootloader is very small and is', 15, INK))
s.append(text(1117, 715, 'never changed after the unit leaves the factory.', 15, INK))

body = f'''<p class="title">Control software: four layers and a firmware update that survives a power failure</p>
<p class="sub">Illustrative; the periods of the layers are typical orders of magnitude</p>
{svg(40, 135, 1920, 720, ''.join(s))}'''
print(page('fig_18_sw', body))
