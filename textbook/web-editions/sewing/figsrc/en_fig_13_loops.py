import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
K, M, G, Bc, R = C['ink'], C['muted'], C['green'], C['blue'], C['red']
s = [arrow_defs((('ak', '#5a6570'), ('ab', C['blue']), ('ag2', C['green']), ('ar', C['red'])))]
a = s.append
Y = 131
def arr(x1, x2, y=Y): a(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#5a6570" stroke-width="2" marker-end="url(#ak)"/>')
def bx(x1, x2, y1, y2, stroke, fill='#fff', t='', sub=(), tc=None, tfs=17, sw=2):
    a(f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    n = len(sub); cy = (y1 + y2) / 2 - 8 * n + 6
    a(f'<text x="{(x1+x2)/2}" y="{cy}" font-size="{tfs}" font-weight="700" fill="{tc or stroke}" text-anchor="middle">{t}</text>')
    for i, l in enumerate(sub):
        a(f'<text x="{(x1+x2)/2}" y="{cy+(24 if n==1 else 20)+i*17}" font-size="11.5" fill="{M}" text-anchor="middle">{l}</text>')
def sm(cx):
    a(f'<circle cx="{cx}" cy="{Y}" r="14" fill="#fff" stroke="{K}" stroke-width="2"/><text x="{cx}" y="{Y+6}" font-size="16" font-weight="700" fill="{K}" text-anchor="middle">Σ</text>')
    a(f'<text x="{cx-20}" y="{Y+32}" font-size="16" font-weight="700" fill="{K}">−</text>')
a(f'<text x="40" y="{Y-4}" font-size="13.5" font-weight="700" fill="{K}" text-anchor="middle">Target angle θ*</text>')
a(f'<text x="40" y="{Y+14}" font-size="12" fill="{M}" text-anchor="middle">(needle-up)</text>')
arr(90, 119); sm(135); arr(149, 172)
bx(172, 272, 100, 162, G, t='K<tspan baseline-shift="sub" font-size="12">p</tspan>', sub=('position loop (P)',), tfs=19)
arr(272, 288)
bx(288, 410, 100, 162, '#5a6570', t='Limit', sub=('≤ positioning speed',), tc=K, tfs=15)
a(f'<text x="428" y="{Y-10}" font-size="15" font-weight="700" fill="{K}" text-anchor="middle">ω*</text>')
arr(410, 446); sm(462); arr(476, 496)
bx(496, 626, 100, 162, Bc, t='K<tspan baseline-shift="sub" font-size="11">v</tspan> (1 + 1/(T<tspan baseline-shift="sub" font-size="11">i</tspan> s))', sub=('velocity loop (PI)',), tfs=16)
a(f'<text x="644" y="{Y-10}" font-size="15" font-weight="700" fill="{K}" text-anchor="middle">T*</text>')
arr(626, 662)
bx(662, 912, 82, 182, Bc, fill='#e9f0fc', t='Current loop + inverter',
   sub=('turns the current command into three-phase', 'voltages by rotor angle (vector control)', 'torque T = k<tspan baseline-shift="sub" font-size="9">t</tspan> × i<tspan baseline-shift="sub" font-size="9">q</tspan>'), tfs=15)
arr(912, 936)
bx(936, 1046, 100, 162, K, t='1 / (J s)', sub=('motor + main shaft',), tfs=17)
a(f'<line x1="991" y1="198" x2="991" y2="164" stroke="{R}" stroke-width="1.6" marker-end="url(#ar)"/>')
a(f'<text x="1046" y="212" font-size="12" fill="{R}" text-anchor="end">Load: friction, inertia torque</text>')
a(f'<text x="1046" y="227" font-size="12" fill="{R}" text-anchor="end">of the needle-bar mechanism</text>')
a(f'<text x="1057" y="{Y-10}" font-size="15" font-weight="700" fill="{K}" text-anchor="middle">ω</text>')
arr(1046, 1068)
bx(1068, 1106, 108, 154, K, t='1/s', tfs=15)
arr(1106, 1128)
a(f'<text x="1134" y="{Y+5}" font-size="15" font-weight="700" fill="{K}">θ</text>')
# feedback paths
a(f'<polyline points="1057,{Y} 1057,250 462,250 462,{Y+15}" fill="none" stroke="{Bc}" stroke-width="1.8" marker-end="url(#ab)"/>')
a(f'<text x="757" y="244" font-size="12.5" font-weight="700" fill="{Bc}" text-anchor="middle">speed from angle differences (velocity feedback)</text>')
a(f'<polyline points="1117,{Y} 1117,292 135,292 135,{Y+15}" fill="none" stroke="{G}" stroke-width="1.8" marker-end="url(#ag2)"/>')
a(f'<text x="627" y="286" font-size="12.5" font-weight="700" fill="{G}" text-anchor="middle">angle measured by the encoder (position feedback)</text>')
svg = f'<svg width="1145" height="235" viewBox="0 70 1145 235" style="display:block;overflow:visible">{"".join(s)}</svg>'

body = f'''<p class="title">The three control loops of the main-shaft servo: position loop around velocity loop around current loop</p>
<p class="sub">Illustrative. The inner the loop, the faster it runs: the current loop is computed about every 0.1 ms, the velocity and position loops more slowly; the output of each outer loop is the command for the loop inside it</p>
<div style="margin-top:20px">{svg}</div>
<p class="note" style="color:#1b2430;font-size:13px;line-height:1.75;margin:30px 12px 0">Worked example in this chapter (illustrative values): J = 6×10⁻⁴ kg·m², K<sub>v</sub> = 0.2 N·m·s/rad → velocity-loop bandwidth about K<sub>v</sub>/J ≈ 330 rad/s; K<sub>p</sub> = 200 s⁻¹; current loop modelled as a 0.5 ms first-order lag.<br>
Tuning order: first make the current and velocity loops stiff, then add the position loop; the position gain must not be too large compared with the velocity-loop bandwidth, or the shaft overshoots (Fig. 13-3).</p>'''
render('fig_13_loops', body)
