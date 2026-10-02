import sys, math, json; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
D = math.pi / 180
HERE = __file__.rsplit('/', 1)[0]

# ---- left: 16-microstep phase currents (exact) ----
cl = Chart(560, 470, (0, 360), (-1.18, 1.25), L=56, T=16, R=14, B=48)
cl.grid([0, 90, 180, 270, 360], [-1, -0.5, 0, 0.5, 1], xfmt=lambda v: f'{v:g}',
        xlab='Electrical angle (°); one electrical cycle = 4 full steps = 7.2° mechanical', ylab='Phase current (× rated)', ylab_dx=2)
st = 90 / 16
def stairs(fn):
    xs, ys = [], []
    for k in range(64):
        v = fn(k * st * D)
        xs += [k * st, (k + 1) * st]; ys += [v, v]
    return xs, ys
# full-step drive, phase A (dashed)
cl.line([0, 90, 90, 270, 270, 360], [1, 1, -1, -1, 1, 1], C['grey'], w=1.6, dash='6 4')
cl.line(*stairs(math.cos), C['blue'])
cl.line(*stairs(math.sin), C['orange'])
cl.text(4, 1.1, 'Phase A (16 microsteps)', C['blue'], fs=12, bold=True)
cl.text(122, 1.1, 'Phase B (16 microsteps)', C['orange'], fs=12, bold=True)
cl.text(98, -1.0, 'Phase A current with full-step drive (dashed)', C['muted'], fs=12, dy=22)

# ---- right: torque vs step frequency (shape digitised from the original figure; illustrative) ----
dig = json.load(open(f'{HERE}/en_fig_13_step_digitised.json'))
def curve(pts, start, depth):
    pts = [p for p in pts if p[0] >= 240]
    # light smoothing
    sm = []
    for i in range(len(pts)):
        w = pts[max(0, i - 2):i + 3]; sm.append((pts[i][0], sum(q[1] for q in w) / len(w)))
    f240 = sm[0][1]
    fs, ts = [], []
    for k in range(0, 240, 4):
        f = float(k); base = start + (f240 - start) * f / 240 if f > 60 else start
        ts.append(base * (1 - depth * math.exp(-((f - 150) / 28) ** 2))); fs.append(f)
    for f, t in sm: fs.append(f); ts.append(t)
    return fs, ts
cr = Chart(560, 470, (0, 5000), (0, 1.2), L=56, T=16, R=14, B=48)
cr.grid([0, 1000, 2000, 3000, 4000, 5000], [0, 0.3, 0.6, 0.9, 1.2], xlab='Step frequency (full steps / s)', ylab='Torque (N·m)', ylab_dx=2)
cr.hline(0.25, C['red'], w=1.6, dash='7 5')
cr.line(*curve(dig['b'], 1.0, 0.24), C['blue'])
cr.line(*curve(dig['o'], 1.0, 0.25), C['orange'])
cr.text(2550, 0.25, 'Load torque', C['red'], fs=13, bold=True, dy=-7)
cr.text(140, 0.2, '↖ low-frequency resonance', C['muted'], fs=12)
cr.text(4300, 0.07, '24 V drive', C['orange'], fs=13, bold=True)
cr.text(3000, 0.42, '48 V drive', C['blue'], fs=13, bold=True)

body = f'''<p class="title">Stepper motor: microstepping makes each step smaller; torque falls as speed rises</p>
<p class="sub">Illustrative. Two-phase hybrid stepper, step angle 1.8° (200 steps per revolution); torque curves show the shape only</p>
<div style="display:flex;justify-content:space-between;margin-top:30px;padding-left:10px">{cl.svg()}{cr.svg()}</div>
<p class="note" style="color:#1b2430;font-size:13px;line-height:1.7;margin:16px 14px 0">Left: with microstepping the currents in phases A and B follow a sine and cosine in small increments, the rotor stops between two full steps, and the steps become smaller and the motion smoother. Microstepping does not raise positioning accuracy in the same proportion, though: under heavy load the actual angle of each microstep becomes uneven. Right: the windings have inductance, so the higher the frequency, the less time the current has to build up and the lower the torque; once the curve drops below the load torque the motor loses steps. A higher drive voltage pushes the curve to the right.</p>'''
render('fig_13_step', body)
