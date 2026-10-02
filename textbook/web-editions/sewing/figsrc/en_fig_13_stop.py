import sys, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *

# servo model (same as src/zh/labs/servo.html = model13.py)
D = math.pi / 180
B, TMAX, TAUI, TEND, DT = 2e-4, 2.5, 0.5e-3, 0.25, 2e-5
STD = dict(Kp=200, Kv=0.2, Ti=12, wp=200, e0=45, J=6, Tf=0.15)

def sim(p):
    J = p['J'] * 1e-4; Tf = p['Tf']; Ti = p['Ti'] / 1000; wpos = p['wp'] * 2 * math.pi / 60
    th = -p['e0'] * D; w = wpos; Tm = Tf + B * w; integ = Tm / p['Kv'] if Ti > 0 else 0
    res = []
    for k in range(round(TEND / DT)):
        t = k * DT; e = -th
        wref = max(-wpos, min(wpos, p['Kp'] * e)); ew = wref - w
        if Ti > 0: integ += ew * DT / Ti
        Tref = p['Kv'] * (ew + integ)
        if abs(Tref) > TMAX:
            Tref = math.copysign(TMAX, Tref)
            if Ti > 0: integ -= ew * DT / Ti
        Tm += (Tref - Tm) * DT / TAUI
        Td = Tm - B * w
        if abs(w) < 1e-3 and abs(Td) <= Tf: acc = -w / DT
        else: acc = (Td - Tf * (math.copysign(1, w) if abs(w) >= 1e-3 else math.copysign(1, Td))) / J
        w += acc * DT; th += w * DT
        if k % 10 == 0: res.append((t, th / D, w * 60 / 2 / math.pi))
    return res

def metrics(r):
    over = max(q[1] for q in r); ts = 0
    for q in r:
        if abs(q[1]) > 0.5: ts = q[0]
    return over, ts * 1000, r[-1][1]

cases = [
    (dict(STD), C['blue'], 'Standard (K_p = 200, K_v = 0.2, T_i = 12 ms)'),
    (dict(STD, Kp=500), C['orange'], 'Position gain too high (K_p = 500)'),
    (dict(STD, J=12), C['purple'], 'Inertia doubled, same gains (J = 12×10⁻⁴)'),
    (dict(STD, Ti=0), C['green'], 'Integral removed (T_i = 0)'),
]
runs = []
for p, col, lab in cases:
    r = sim(p); m = metrics(r); runs.append((r, col, lab, m)); print(lab, m)

ce = Chart(560, 470, (0, 120), (-2, 3), L=56, T=16, R=14, B=48)
ce.grid([0, 20, 40, 60, 80, 100, 120], [-2, -1, -0.5, 0, 0.5, 1, 2, 3], xlab='Time (ms)', ylab='Position error (°)', ylab_dx=4)
ce.band(-0.5, 0.5, C['green'], 0.10)
ce.text(2, 0.62, '±0.5° tolerance band', C['green'], fs=12)
cs = Chart(560, 470, (0, 120), (-55, 240), L=56, T=16, R=14, B=48)
cs.grid([0, 20, 40, 60, 80, 100, 120], [-50, 0, 50, 100, 150, 200], xlab='Time (ms)', ylab='Speed (r/min)', ylab_dx=4)
for r, col, lab, m in runs:
    t = [q[0] * 1000 for q in r if q[0] <= 0.1205]
    n = len(t)
    ce.line(t, [q[1] for q in r[:n]], col)
    cs.line(t, [q[2] for q in r[:n]], col, clip=False)

leg = ''
for r, col, lab, (ov, ts, fin) in runs:
    leg += (f'<div style="display:flex;align-items:center;gap:10px"><span style="flex:none;width:28px;height:3px;background:{col}"></span>'
            f'<span>{esc(lab).replace("K_p","K<sub>p</sub>").replace("K_v","K<sub>v</sub>").replace("T_i","T<sub>i</sub>")}: overshoot {ov:.1f}°, inside ±0.5° in {ts:.0f} ms, stops at {(fin if abs(fin)>=0.005 else 0.0):+.2f}°</span></div>')

body = f'''<p class="title">Needle positioning: one machine, four parameter sets</p>
<p class="sub">Simulation: shaft turning at 200 r/min, position loop engaged 45° before needle-up; friction 0.15 N·m; illustrative parameters (model13.py)</p>
<div style="display:flex;justify-content:space-between;margin-top:30px;padding-left:10px">{ce.svg()}{cs.svg()}</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px 24px;font-size:12.5px;margin:26px 0 6px 12px">{leg}</div>'''
render('fig_13_stop', body)
