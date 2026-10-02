import sys, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *

# ---------- circuit (coordinates follow the original drawing; viewBox units) ----------
K, B_, R_, G = C['ink'], C['blue'], C['red'], C['gold']
s = []
a = s.append
a(arrow_defs())
fs = 21
# AC input and rectifier
a(f'<text x="35" y="307" font-size="{fs+1}" font-weight="700" fill="{K}">~220 V</text>')
a(f'<line x1="115" y1="294" x2="165" y2="294" stroke="{K}" stroke-width="2.5"/>')
a(f'<rect x="165" y="200" width="140" height="188" rx="6" fill="#f3f5f6" stroke="{K}" stroke-width="2.5"/>')
a(f'<text x="235" y="290" font-size="{fs}" font-weight="700" fill="{K}" text-anchor="middle">bridge</text><text x="235" y="266" font-size="{fs}" font-weight="700" fill="{K}" text-anchor="middle">Rectifier</text>')
a(f'<text x="235" y="316" font-size="{fs-2}" fill="{C["muted"]}" text-anchor="middle">(diodes)</text>')
# buses
a(f'<polyline points="305,235 340,235 340,118 940,118" fill="none" stroke="{K}" stroke-width="2.5"/>')
a(f'<polyline points="305,353 340,353 340,470 940,470" fill="none" stroke="{K}" stroke-width="2.5"/>')
a(f'<text x="350" y="104" font-size="{fs-1}" font-weight="700" fill="{G}">DC bus + (about 310 V)</text>')
# capacitor
a(f'<line x1="422" y1="118" x2="422" y2="276" stroke="{K}" stroke-width="2.5"/><line x1="422" y1="300" x2="422" y2="470" stroke="{K}" stroke-width="2.5"/>')
a(f'<line x1="390" y1="276" x2="455" y2="276" stroke="{K}" stroke-width="4"/><line x1="390" y1="300" x2="455" y2="300" stroke="{K}" stroke-width="4"/>')
a(f'<text x="463" y="295" font-size="{fs}" font-weight="700" fill="{K}">C</text>')
a(f'<text x="434" y="350" font-size="{fs-3}" fill="{C["muted"]}">DC-link</text>')
a(f'<text x="434" y="372" font-size="{fs-3}" fill="{C["muted"]}">capacitor</text>')
# braking resistor + switch
a(f'<line x1="540" y1="118" x2="540" y2="165" stroke="{K}" stroke-width="2.5"/>')
a(f'<rect x="524" y="165" width="33" height="82" rx="3" fill="{C["red"]}" fill-opacity="0.1" stroke="{R_}" stroke-width="2.2"/>')
a(f'<text x="567" y="200" font-size="{fs-1}" font-weight="700" fill="{R_}">Braking</text>')
a(f'<text x="567" y="224" font-size="{fs-1}" font-weight="700" fill="{R_}">resistor</text>')
a(f'<line x1="540" y1="247" x2="540" y2="306" stroke="{K}" stroke-width="2.5"/>')
a(f'<rect x="518" y="306" width="45" height="45" rx="4" fill="#fff" stroke="{K}" stroke-width="2.2"/>')
a(f'<text x="540" y="336" font-size="{fs-2}" font-weight="700" fill="{K}" text-anchor="middle">S</text>')
a(f'<line x1="540" y1="351" x2="540" y2="470" stroke="{K}" stroke-width="2.5"/>')
a(f'<text x="575" y="366" font-size="{fs-3}" fill="{C["muted"]}">on when</text>')
a(f'<text x="575" y="388" font-size="{fs-3}" fill="{C["muted"]}">overvoltage</text>')
# inverter legs
a(f'<text x="800" y="104" font-size="{fs-1}" font-weight="700" fill="{B_}" text-anchor="middle">Inverter (6 switches)</text>')
legs = [680, 775, 870]
outs = [(715, 595), (810, 520), (905, 595)]
for x in legs:
    a(f'<line x1="{x}" y1="118" x2="{x}" y2="470" stroke="{K}" stroke-width="2.5"/>')
    for y in (155, 260):
        a(f'<rect x="{x-19}" y="{y}" width="38" height="58" rx="4" fill="#e9f0fc" stroke="{B_}" stroke-width="2"/>')
# phase wires to motor (from mid-point of each leg)
mx, my, mr = 870, 595, 47
a(f'<polyline points="680,236 715,236 715,595 {mx-mr},595" fill="none" stroke="{B_}" stroke-width="2"/>')
a(f'<polyline points="775,236 810,236 810,520 870,520 870,{my-mr}" fill="none" stroke="{B_}" stroke-width="2"/>')
a(f'<polyline points="870,236 905,236 905,{my-mr+12}" fill="none" stroke="{B_}" stroke-width="2"/>')
a(f'<circle cx="{mx}" cy="{my}" r="{mr}" fill="#e9f0fc" stroke="{B_}" stroke-width="2.4"/>')
a(f'<text x="{mx}" y="{my+9}" font-size="{fs+3}" font-weight="700" fill="{B_}" text-anchor="middle">M</text>')
a(f'<text x="930" y="640" font-size="{fs-3}" fill="{C["muted"]}">Servo</text><text x="930" y="662" font-size="{fs-3}" fill="{C["muted"]}">motor</text>')
circ = f'<svg viewBox="0 0 1000 680" width="600" height="408" style="display:block">{"".join(s)}</svg>'

# ---------- chart: DC-link voltage without braking ----------
J, C_, V0, eta = 6e-4, 470e-6, 310, 0.7
V = lambda n: math.sqrt(V0 ** 2 + 2 * eta * 0.5 * J * (n * 2 * math.pi / 60) ** 2 / C_)
ns = list(range(0, 6001, 50))
n400 = math.sqrt((400 ** 2 - V0 ** 2) * C_ / (2 * eta * 0.5 * J)) * 60 / (2 * math.pi)
print('V(5000)=', V(5000), 'n at 400 V =', n400)
ch = Chart(480, 420, (0, 6000), (300, 700), L=66, T=16, R=14, B=48)
ch.grid([0, 1000, 2000, 3000, 4000, 5000, 6000], [300, 400, 500, 600, 700], xlab='Speed before the emergency stop (r/min)', ylab='DC-link voltage without braking (V)', ylab_dx=-2)
ch.hline(400, C['red'], w=1.6, dash='7 5')
ch.vline(n400, C['grey'], w=1.3, dash='5 4')
ch.line(ns, [V(n) for n in ns], C['blue'], w=2.4)
ch.text(2700, 400, 'Overvoltage protection', C['red'], fs=12.5, bold=True, dy=22)
ch.text(2700, 400, '400 V (illustrative)', C['red'], fs=12.5, bold=True, dy=39)
ch.text(n400, 300, f'≈ {n400:.0f} r/min', C['muted'], fs=12, dx=6, dy=-14)
ch.dot(5000, V(5000), C['blue'], r=5, stroke='#fff')
ch.text(5000, V(5000), f'5000 r/min: ≈ {V(5000):.0f} V', C['blue'], fs=13, bold=True, anchor='end', dx=-12, dy=-8)

body = f'''<p class="title">Power circuit: rectifier, DC-link capacitor, inverter bridge and braking resistor</p>
<p class="sub">Illustrative. In an emergency stop the motor acts as a generator and returns kinetic energy to the DC-link capacitor; if the voltage rises too far, the energy must be burned in the braking resistor</p>
<div style="display:flex;gap:22px;align-items:flex-start;margin-top:4px">
<div style="border:1.2px solid #e3e6e9;border-radius:8px;background:#fff;padding:14px 6px 10px">{circ}</div>
<div style="margin-top:6px">{ch.svg()}</div></div>
<p class="note" style="color:#1b2430;font-size:13px;line-height:1.7;margin-top:14px">Worked example (illustrative values): equivalent inertia J = 6×10⁻⁴ kg·m²; kinetic energy at 5000 r/min ½Jω² ≈ 82 J; assuming 70% is returned to the DC link (the rest is lost in friction and the windings), about 58 J.<br>
DC-link capacitor 470 μF, initially at 310 V: absorbing all of it would raise the voltage to √(310² + 2E/C) ≈ 584 V, far beyond the rating of the capacitor and power switches. So an emergency stop needs either a braking resistor or a slower deceleration that lets friction absorb more of the energy.</p>'''
render('fig_13_inv', body)
