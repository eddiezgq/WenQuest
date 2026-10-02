# Fig. 16-1 (English): structure of a multi-head embroidery machine (front view, not to scale)
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
BL, OR, GR = '#2f6fd8', '#e0662f', '#2e9e5b'
W = 1140
s = [f'<svg width="{W}" height="470" viewBox="0 0 {W} 470" style="display:block;overflow:visible">']
s.append(f'<text x="40" y="12" font-size="11" fill="#5a6570">Cross-beam</text>')
s.append(f'<text x="1094" y="12" font-size="11.5" font-weight="700" fill="{BL}" text-anchor="end">Upper shaft (driven by the main motor; drawn below the beam)</text>')
s.append(f'<rect x="28" y="22" width="1068" height="28" rx="3" fill="#e9ecf0" stroke="#5a6570" stroke-width="1.2"/>')
s.append(f'<line x1="28" y1="70" x2="1096" y2="70" stroke="{BL}" stroke-width="3.5"/>')
hx = [84 + i * 169.5 for i in range(6)]
for i, x in enumerate(hx):
    s.append(f'<rect x="{x}" y="50" width="104" height="104" rx="5" fill="#f6f7f9" stroke="#1b2430" stroke-width="1.3"/>')
    s.append(f'<text x="{x+52}" y="69" font-size="11" font-weight="700" fill="#1b2430" text-anchor="middle">Head {i+1}</text>')
    for k in range(6):
        xx = x + 12 + k * 15.3
        s.append(f'<line x1="{xx:.1f}" y1="84" x2="{xx:.1f}" y2="148" stroke="#5a6570" stroke-width="2.6"/>')
    s.append(f'<rect x="{x+76}" y="92" width="21" height="16" rx="3" fill="#fdeee6" stroke="{OR}" stroke-width="1.2"/>')
    s.append(f'<line x1="{x+43}" y1="140" x2="{x+43}" y2="176" stroke="#1b2430" stroke-width="2.6"/>')
    s.append(f'<circle cx="{x+43}" cy="356" r="13" fill="#e9ecf0" stroke="#5a6570" stroke-width="1.2"/>')
s.append(''.join(f'<text x="{hx[0]+109}" y="{96+i*12}" font-size="10" font-weight="700" fill="{OR}">{t}</text>' for i, t in enumerate(('Thread-', 'break', 'detection'))))
s.append(f'<text x="{hx[0]+48}" y="194" font-size="10.5" fill="#5a6570" text-anchor="middle">Needle-bar case (9–15 needle bars;</text><text x="{hx[0]+48}" y="207" font-size="10.5" fill="#5a6570" text-anchor="middle">the whole case shifts at colour change)</text>')
s.append(f'<rect x="48" y="214" width="1042" height="50" rx="4" fill="#2e9e5b" opacity="0.15"/>')
s.append(f'<text x="569" y="244" font-size="13" font-weight="700" fill="{GR}" text-anchor="middle">Embroidery frame (spans all heads; one piece of fabric stretched under each head)</text>')
s.append(f'<line x1="560" y1="280" x2="650" y2="280" stroke="{GR}" stroke-width="2"/><path d="M664 280l-14 -7v14z" fill="#5a6570"/><text x="670" y="285" font-size="11.5" font-weight="700" fill="{GR}">X</text>')
s.append(f'<line x1="1070" y1="248" x2="1070" y2="198" stroke="{GR}" stroke-width="2"/><path d="M1070 184l-7 14h14z" fill="#5a6570"/><text x="1080" y="190" font-size="11.5" font-weight="700" fill="{GR}">Y</text>')
s.append(f'<line x1="28" y1="370" x2="1096" y2="370" stroke="{OR}" stroke-width="3.5"/>')
s.append(f'<text x="1060" y="388" font-size="11.5" font-weight="700" fill="{OR}" text-anchor="end">Hook shaft (drives the rotary hook of every head)</text>')
s.append(f'<line x1="66" y1="70" x2="66" y2="398" stroke="{BL}" stroke-width="1" stroke-dasharray="4 3"/>')
s.append(f'<line x1="1076" y1="264" x2="1076" y2="398" stroke="{BL}" stroke-width="1" stroke-dasharray="4 3"/>')
s.append(f'<rect x="4" y="398" width="124" height="48" rx="6" fill="#e9f0fc" stroke="{BL}" stroke-width="1.4"/><text x="66" y="427" font-size="12" font-weight="700" fill="{BL}" text-anchor="middle">Main-shaft servo</text>')
s.append(f'<rect x="1026" y="398" width="100" height="48" rx="6" fill="#e9f0fc" stroke="{BL}" stroke-width="1.4"/><text x="1076" y="427" font-size="12" font-weight="700" fill="{BL}" text-anchor="middle">X, Y servos</text>')
s.append('</svg>')
ctrl = [('b', 'Main controller', 'Design file, speed control, colour-change order, mending'),
        ('b', 'Motion control', 'Interpolates X, Y within the window of main-shaft angle (Chapter 15)'),
        ('o', 'Head boards', 'Needle-bar jump solenoid, trimming, thread-break detection, indicator lamp'),
        ('o', 'Control panel', 'Design, colours, speed, statistics')]
cb = ''.join(f'<div class="box {c}" style="padding:12px 10px;min-height:66px"><b>{esc(t)}</b><span style="margin-top:4px">{esc(d)}</span></div>' for c, t, d in ctrl)
panel = f'''<div style="margin:22px auto 0;width:780px;border:1.5px solid #1b2430;border-radius:8px;padding:12px 14px 14px;background:#fff">
<p style="font-weight:700;margin:0 0 10px;font-size:14px">Control system</p>
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px">{cb}</div></div>'''
body = f'''<p class="title">Multi-head embroidery machine: one upper shaft, one hook shaft and one frame drive all heads</p>
<p class="sub">Structural schematic (front view, not to scale). The needles and rotary hooks of every head are driven by shared shafts; the frame spans all heads and is moved by the X and Y servos through the same design</p>
<div style="margin-top:30px">{''.join(s)}</div>{panel}
<p class="note" style="color:#1b2430;font-size:12.5px">One manufacturer’s multi-head machines: 2–8 heads, 9, 12 or 15 needles per head, up to 1100 r/min, head spacing 360 or 500 mm; presser-foot pressure follows the fabric thickness within 0.05 s (product literature).</p>'''
render('fig_16_struct', body, width=1200)
