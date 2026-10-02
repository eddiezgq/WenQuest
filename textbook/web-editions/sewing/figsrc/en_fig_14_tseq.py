import sys, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
D = math.pi / 180
# needle-bar model of the book (model14 / labs/trim.html)
Rr, Ll, T = 15.5, 55, 1.5; lam = Rr / Ll
Xn = lambda f: Rr * (1 - math.cos(f * D)) - Ll * (1 - math.sqrt(1 - (lam * math.sin(f * D)) ** 2))
HT = T + Xn(101.7)
ztip = lambda f: HT - Xn(f % 360)
ALPHA = (2.5 + 0.15) / 6e-4
n, pc, t1, t2 = 300, 290, 0.006, 0.010
e1, e2 = pc + 6 * n * t1, pc + 6 * n * t2
CUT = 415
stop = CUT + (n * 2 * math.pi / 60) ** 2 / (2 * ALPHA) / D
f10 = next(f / 10 for f in range(2500, 3300) if ztip(f / 10) >= 10)
print('entry', e1, e2, 'stop', stop - 360, 'tip 10 mm at', f10)

W = 1140; x0, x1 = 110, 1128
X = lambda f: x0 + (x1 - x0) * (f - 180) / 300
s = [arrow_defs()]
a = s.append
H = 604
for f in range(180, 481, 30):
    a(f'<line x1="{X(f):.1f}" y1="0" x2="{X(f):.1f}" y2="{H-30}" stroke="{C["grid"]}" stroke-width="1"/>')
    a(f'<text x="{X(f):.1f}" y="{H-8}" font-size="12" fill="{C["muted"]}" text-anchor="middle">{f % 360}°</text>')
# row labels
rows = {'needle': 34, 'knife': 186, 'cut': 244, 'rel': 302, 'stop': 360, 'wipe': 420}
labs = [('needle', 'Needle-point height'), ('knife', 'Knife entry'), ('cut', 'Cut'), ('rel', 'Tension release'), ('stop', 'Needle stop'), ('wipe', 'Thread wiping')]
for k, t in labs:
    a(f'<text x="0" y="{rows[k] + (0 if k == "needle" else 0)}" font-size="13" font-weight="700" fill="{C["ink"]}">{t}</text>')
# shift rows: needle panel is rows y 20..140
Yn = lambda z: 112 - 72 * (z + 2) / 34 + 14
fs = [180 + k for k in range(301)]
a(f'<line x1="{x0}" y1="{Yn(0):.1f}" x2="{x1}" y2="{Yn(0):.1f}" stroke="{C["muted"]}" stroke-width="1" stroke-dasharray="5 4"/>')
a(f'<text x="{x0+4}" y="{Yn(0)-5:.1f}" font-size="11" fill="{C["muted"]}">throat-plate surface</text>')
a('<polyline points="' + ' '.join(f'{X(f):.1f},{Yn(ztip(f)):.1f}' for f in fs) + f'" fill="none" stroke="{C["ink"]}" stroke-width="2"/>')
a(f'<circle cx="{X(f10):.1f}" cy="{Yn(ztip(f10)):.1f}" r="5" fill="{C["gold"]}" stroke="{C["ink"]}" stroke-width="1"/>')
a(f'<text x="{X(f10)-10:.1f}" y="{Yn(ztip(f10))-12:.1f}" font-size="11.5" font-weight="700" fill="{C["gold"]}" text-anchor="end">needle point 10 mm above the plate ({f10:.0f}°; solenoid energised in the patent)</text>')
ev = [(206, 'hook catches loop'), (258.3, 'needle leaves fabric'), (293, 'take-up gives most thread'), (341, 'loop sheds'), (415, 'take-up lever top'), (461.7, 'needle enters fabric')]
for f, l in ev:
    a(f'<line x1="{X(f):.1f}" y1="150" x2="{X(f):.1f}" y2="164" stroke="{C["ink"]}" stroke-width="2"/>')
    a(f'<text x="{X(f):.1f}" y="{196 if f == 293 else 180}" font-size="11.5" font-weight="700" fill="{C["ink"]}" text-anchor="middle">{l}</text>')
# move other rows down
R = {'knife': 228, 'cut': 290, 'rel': 378, 'stop': 448, 'wipe': 512}
s = [x for x in s if not any(f'>{t}</text>' in x and 'x="0"' in x for _, t in labs)]
a = s.append
a(f'<text x="0" y="40" font-size="13" font-weight="700" fill="{C["ink"]}">Needle-point</text><text x="0" y="56" font-size="13" font-weight="700" fill="{C["ink"]}">height</text>')
for k, t in labs[1:]:
    a(f'<text x="0" y="{R[k]+5}" font-size="13" font-weight="700" fill="{C["ink"]}">{t}</text>')
# knife entry
y = R['knife']
a(f'<rect x="{X(300):.1f}" y="{y-16}" width="{X(330)-X(300):.1f}" height="32" rx="3" fill="{C["green"]}" opacity="0.2"/>')
a(f'<text x="{X(300):.1f}" y="{y+32}" font-size="11.5" font-weight="700" fill="{C["green"]}">allowed entry window 300°–330°</text>')
a(f'<circle cx="{X(pc):.1f}" cy="{y}" r="6" fill="{C["red"]}"/>')
a(f'<text x="{X(pc)-10:.1f}" y="{y+4}" font-size="11.5" font-weight="700" fill="{C["red"]}" text-anchor="end">command {pc}°</text>')
a(f'<rect x="{X(e1):.1f}" y="{y-9}" width="{X(e2)-X(e1):.1f}" height="18" rx="2" fill="{C["red"]}" opacity="0.75"/>')
a(f'<text x="{X(e2)+8:.1f}" y="{y+4}" font-size="11.5" font-weight="700" fill="{C["red"]}">actual entry {e1:.0f}°–{e2:.0f}° (delay 6–10 ms)</text>')
# cut
y = R['cut']
a(f'<polyline points="{X(e2):.1f},{y+10} {X(340):.1f},{y+10} {X(CUT):.1f},{y-4}" fill="none" stroke="{C["red"]}" stroke-width="2.6"/>')
a(f'<circle cx="{X(CUT):.1f}" cy="{y-4}" r="6" fill="{C["gold"]}" stroke="{C["ink"]}" stroke-width="1"/>')
a(f'<text x="{X(CUT)-6:.1f}" y="{y+27}" font-size="11.5" font-weight="700" fill="{C["gold"]}" text-anchor="end">cut against the fixed knife (415° = 55° of the next revolution)</text>')
# tension release
y = R['rel']
a(f'<line x1="{X(335):.1f}" y1="{y-24}" x2="{X(415):.1f}" y2="{y-24}" stroke="{C["ink"]}" stroke-width="1.5"/>')
a(f'<text x="{X(335):.1f}" y="{y-30}" font-size="11" fill="{C["ink"]}">must cover at least 335°–415°</text>')
a(f'<rect x="{X(330):.1f}" y="{y-16}" width="{X(420)-X(330):.1f}" height="32" rx="3" fill="{C["orange"]}" opacity="0.45"/>')
a(f'<text x="{(X(330)+X(420))/2:.1f}" y="{y+34}" font-size="11.5" font-weight="700" fill="{C["orange"]}" text-anchor="middle">tension discs open: thread drawn by the take-up lever comes from the supply side, leaving a long end at the eye</text>')
# needle stop
y = R['stop']
a(f'<rect x="{X(415):.1f}" y="{y-16}" width="{X(456.7)-X(415):.1f}" height="32" rx="3" fill="{C["blue"]}" opacity="0.2"/>')
a(f'<circle cx="{X(stop):.1f}" cy="{y}" r="7" fill="{C["blue"]}" stroke="{C["ink"]}" stroke-width="1"/>')
a(f'<text x="{X(stop)+11:.1f}" y="{y+4}" font-size="11.5" font-weight="700" fill="{C["blue"]}">stops at {stop-360:.0f}°</text>')
a(f'<text x="{X(stop)+11:.1f}" y="{y+19}" font-size="11" fill="{C["blue"]}">(after the cut, before entry: 55°–96.7°)</text>')
# wipe
y = R['wipe']
a(f'<circle cx="{X(stop):.1f}" cy="{y}" r="7" fill="{C["grey"]}" stroke="{C["ink"]}" stroke-width="1"/>')
a(f'<text x="{X(stop)+11:.1f}" y="{y+4}" font-size="11.5" font-weight="700" fill="{C["grey"]}">wiper sweeps once the shaft</text>')
a(f'<text x="{X(stop)+11:.1f}" y="{y+19}" font-size="11.5" font-weight="700" fill="{C["grey"]}">has stopped (angle no longer changes)</text>')
svg = f'<svg width="{W}" height="{H}" style="display:block;overflow:visible">{"".join(s)}</svg>'

body = f'''<p class="title">Trimming sequence: every action lined up with the timing chart of Chapter 8</p>
<p class="sub">Worked example: trimming speed 300 r/min, trimming-solenoid delay 6–10 ms; horizontal axis from 180° (bottom dead centre of the last stitch) to 120° of the next revolution; windows are illustrative values</p>
<div style="margin-top:18px">{svg}</div>
<p class="note" style="color:#1b2430;font-size:13px;line-height:1.7;margin-top:14px">If the knife enters too early, the loop has not yet been carried round the bobbin case into the knife’s path, and the knife cannot catch the needle thread running to the fabric; too late, and the loop has already shed and been pulled away by the take-up lever — again no cut. Without tension release the needle-thread end is too short, and the next seam easily unthreads at the start.</p>'''
render('fig_14_tseq', body)
