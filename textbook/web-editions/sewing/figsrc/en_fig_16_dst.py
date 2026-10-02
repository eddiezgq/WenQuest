# Fig. 16-5 (English): three basic stitch types (left) and records of a DST file (right)
import sys, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
B, O, G = '#2f6fd8', '#e0662f', '#2e9e5b'
sv = ['<svg width="640" height="600" viewBox="0 0 640 600" style="display:block">']
def lab(y, t, c): sv.append(f'<text x="0" y="{y}" font-size="13.5" font-weight="700" fill="{c}">{esc(t)}</text>')
lab(18, 'Running stitch: 2–4 mm per stitch, for outlines', B)
pts = [(14 + i * 27.5, 70 - 22 * math.sin(i * 0.38 + 0.4)) for i in range(20)]
sv.append('<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + f'" fill="none" stroke="{B}" stroke-width="1.8"/>')
sv += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="{B}"/>' for x, y in pts]
lab(205, 'Satin: back and forth across a column; stitch length = column width (a few mm to 10+ mm)', O)
zz = []
for i in range(36):
    x = 14 + i * 16.3; h = 6 * i / 35
    zz += [(x, 250 - h * 1.0), (x + 8, 300 - 0)]
zz = [(14 + i * 8.15, (238 - 6 * i / 71) if i % 2 == 0 else 302) for i in range(72)]
sv.append('<polyline points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in zz) + f'" fill="none" stroke="{O}" stroke-width="1.5"/>')
lab(405, 'Fill (tatami): rows of short parallel stitches, staggered, to cover large areas', G)
for r in range(8):
    y = 440 + r * 21; off = (r % 3) * 9.5
    xs = [14 + off + k * 28.5 for k in range(18)]
    sv.append(f'<line x1="{xs[0]}" y1="{y}" x2="{xs[-1]}" y2="{y}" stroke="{G}" stroke-width="1.6"/>')
    sv += [f'<circle cx="{x:.1f}" cy="{y}" r="3" fill="{G}"/>' for x in xs]
sv.append('</svg>')

rows = [('Stitch', '+2.5', '+0.4', 'normal stitch'), ('Stitch', '+2.6', '−0.3', 'normal stitch'), ('…', '', '', ''),
        ('Jump', '+12.1', '+5.0', 'jump (no needle drop)'), ('Colour', '0', '0', 'colour change'),
        ('Stitch', '−7.0', '+1.2', 'one satin stitch'), ('End', '0', '0', 'end of design')]
tb = ''.join(f'<tr><td style="font-weight:700">{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in rows)
right = f'''<div style="border:1.2px solid #e3e6e9;border-radius:10px;background:#fff;padding:18px 20px;height:100%">
<p style="font-size:16px;font-weight:700;margin:0 0 12px">DST file</p>
<ul style="margin:0 0 16px;padding-left:16px;font-size:13px;line-height:1.75">
<li>512-byte header (design name, stitch count, number of colours, extents)</li>
<li>then one 3-byte record per stitch: the displacement Δx, Δy from the previous stitch, in units of 0.1 mm</li>
<li>at most ±121 in each coordinate direction, i.e. 12.1 mm</li>
<li>flag bits distinguish normal stitch / jump / colour change, etc.</li>
<li>no trim command: several consecutive jumps mean a trim</li>
<li>an end record marks the end of the design</li>
<li>the file holds no colour values, only “colour change” commands; which needle bar each colour uses is set on the machine</li></ul>
<table style="width:100%;font-size:13px"><tr><th style="color:#5a6570;border-bottom-color:#d8dde1">Type</th><th style="color:#5a6570;border-bottom-color:#d8dde1">Δx (mm)</th><th style="color:#5a6570;border-bottom-color:#d8dde1">Δy (mm)</th><th style="color:#5a6570;border-bottom-color:#d8dde1">Meaning</th></tr>{tb}</table>
<p style="font-size:12.5px;color:#5a6570;margin:22px 0 0">The controller reads the records one by one and sets the speed from each stitch’s displacement (Fig. 16-3).</p></div>'''
left = f'''<div style="border:1.2px solid #e3e6e9;border-radius:10px;background:#fff;padding:20px 20px 16px">{''.join(sv)}
<p style="font-size:12.5px;color:#5a6570;margin:8px 0 0">Satin is usually laid over a layer of “underlay” stitches; fill needs “pull compensation” for the fabric: the stitches pull the fabric inwards, so shapes are digitised a little wider than the finished size.</p></div>'''
body = f'''<p class="title">Embroidery stitches and embroidery files</p>
<p class="sub">Left: three basic stitch types (schematic); right: records of a DST file (from the public format description)</p>
<div style="display:grid;grid-template-columns:690px 1fr;gap:26px;margin-top:22px">{left}{right}</div>'''
render('fig_16_dst', body, width=1200)
