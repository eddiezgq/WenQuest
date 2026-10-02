# Fig. 16-2 (English): frame motion within one stitch — cycloidal law inside the 204° needle-out window.
import sys, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
WIN, N = 204, 800
T = WIN / (6 * N)                                   # s, time the window occupies
amax = lambda s: 2 * math.pi * s * 1e-3 / T**2      # m/s^2
a3, a7 = amax(3), amax(7)
print(f'T={T*1000:.1f} ms a3={a3:.1f} a7={a7:.1f}')

ch = Chart(720, 470, (0, 360), (0, 100), L=60, T=12, R=40, B=34, frame=False)
ch.bg.append(f'<rect x="{ch.x0-58}" y="{ch.y0-12}" width="{ch.x1-ch.x0+86}" height="{ch.y1-ch.y0+40}" rx="8" fill="#fff" stroke="{C["frame"]}" stroke-width="1.2"/>')
ch.band(0, 100, '#2e9e5b', op=0.09, xa=0, xb=WIN)
ch.band(0, 100, '#c8382a', op=0.07, xa=WIN, xb=360)
ch.text(WIN / 2, 100, 'Needle out of the fabric: frame may move', C['green'], fs=12.5, bold=True, anchor='middle', dy=20)
ch.text((WIN + 360) / 2, 100, 'Needle in the fabric: frame must stop', C['red'], fs=12.5, bold=True, anchor='middle', dy=20)
B0, SC = 50.5, 33.5 / 7          # displacement baseline and % per mm
A0, AS = 11.5, 8.2 / a7          # acceleration zero line and % per m/s^2
ch.hline(A0, '#cfd4d9', w=1, dash='none')
us = [i / 300 for i in range(301)]
for s, a, col in ((7, a7, C['orange']), (3, a3, C['blue'])):
    ch.line([u * WIN for u in us], [B0 + SC * s * (u - math.sin(2 * math.pi * u) / (2 * math.pi)) for u in us], col, w=2.4)
    ch.line([u * WIN for u in us], [A0 + AS * a * math.sin(2 * math.pi * u) for u in us], col, w=2, dash='6 4')
    ch.text(WIN, B0 + SC * s, f'Stitch {s} mm', col, fs=12.5, bold=True, dx=8, dy=5)
for v in (0, 90, 180, 270, 360):
    ch.text(v, 0, f'{v}°', C['muted'], fs=11.5, anchor='middle', dy=22)
ch.text(180, 0, 'Main-shaft angle from the start of the window', C['muted'], fs=12.5, anchor='middle', dy=46)
ch.raw(f'<text x="{ch.x0-52}" y="{ch.Y(84)}" font-size="12.5" font-weight="700" fill="{C["ink"]}">Frame</text>'
       f'<text x="{ch.x0-52}" y="{ch.Y(84)+16}" font-size="12.5" font-weight="700" fill="{C["ink"]}">travel</text>'
       f'<text x="{ch.x0-52}" y="{ch.Y(27)}" font-size="12.5" font-weight="700" fill="{C["ink"]}">Accel.</text>')

side = f'''<div style="border:1.2px solid #e3e6e9;border-radius:8px;background:#fff;padding:18px 20px;font-size:13.5px;line-height:1.75;min-height:470px">
<p style="margin:0 0 14px">At 800 r/min one revolution takes 75 ms;<br>the 204° window lasts only {T*1000:.1f} ms.</p>
<p style="margin:0 0 14px">Stitch 3 mm: peak acceleration {a3:.1f} m/s²<br>Stitch 7 mm: peak acceleration {a7:.1f} m/s²</p>
<p style="margin:0 0 14px">Acceleration is proportional to the stitch length and to the square of the speed:</p>
<p style="margin:0 0 14px">a = 2π s / T², T = 204° / (6n)</p>
<p style="margin:0">The heavier the frame, the less acceleration the same drive force gives. The frame of a 15-head machine has an equivalent mass of about 70 kg (illustrative); with 800 N of drive force it gets only about 10.7 m/s², so a 7&nbsp;mm satin stitch cannot be completed at 800&nbsp;r/min — the machine must slow down.</p></div>'''

body = f'''<p class="title">Frame motion within one stitch: it must be completed in the window while the needle is out of the fabric</p>
<p class="sub">Worked example: needle-out window 204° (borrowed from Chapter 15); the frame moves with a cycloidal motion law, peak acceleration = 2π × stitch length / T², where T is the time the window occupies (illustrative)</p>
<div style="display:flex;gap:26px;align-items:flex-start;margin-top:26px;padding-left:4px">
<div style="padding-left:58px">{ch.svg()}</div><div style="flex:1;margin-top:-12px">{side}</div></div>'''
render('fig_16_window', body, width=1260)
