import sys, math; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *

# solenoid model (same as src/zh/labs/solenoid.html = model13.py)
P = dict(R=8, L1=0.08, ga=1e-3, xmax=3e-3, m=0.02, k=1000, c=4)
TON, TEND, DT = 0.06, 0.1, 2e-6
STD = dict(V=24, tb=20, Ih=1, Vz=0.7, F0=7)
Lx = lambda x: P['L1'] * P['ga'] / (P['ga'] + P['xmax'] - x)
dLx = lambda x: P['L1'] * P['ga'] / (P['ga'] + P['xmax'] - x) ** 2

def sim(p):
    tb = p['tb'] / 1000; lam = x = v = 0.0; res = []
    for k in range(round(TEND / DT)):
        t = k * DT; L = Lx(x); i = lam / L
        if t < TON: u = p['V'] if (t < tb or i < p['Ih']) else -0.7
        else:
            if i > 1e-4: u = -p['Vz']
            else: u = 0; lam = 0; i = 0
        lam += (u - i * P['R']) * DT
        F = 0.5 * i * i * dLx(x); Fs = p['F0'] + P['k'] * x
        a = (F - Fs - P['c'] * v) / P['m']
        if x <= 0 and a < 0: a = 0; v = 0
        if x >= P['xmax'] and a > 0: a = 0; v = 0
        v += a * DT; x = min(P['xmax'], max(0, x + v * DT))
        if (x == 0 and v < 0) or (x == P['xmax'] and v > 0): v = 0
        if k % 25 == 0: res.append((t, i, x * 1e3))
    return res

def metrics(r):
    pull = rel = None
    for q in r:
        if pull is None and q[2] >= 0.999 * 3: pull = q[0]
        if rel is None and q[0] > TON and q[2] <= 0.003: rel = q[0] - TON
    return pull, rel

rd = sim(dict(STD)); rz = sim(dict(STD, Vz=48))
pd, reld = metrics(rd); pz, relz = metrics(rz)
print('diode', pd, reld, 'zener', pz, relz)

W = 1230 - 0
ci = Chart(780, 290, (0, 100), (0, 3.4), L=70, T=16, R=12, B=14)
ci.grid([0, 20, 40, 60, 80, 100], [0, 1, 2, 3], xfmt=lambda v: '', ylab='Current (A)', ylab_dx=10)
cx = Chart(780, 320, (0, 100), (0, 3.15), L=70, T=16, R=12, B=48)
cx.grid([0, 20, 40, 60, 80, 100], [0, 1, 2, 3], xlab='Time (ms)', ylab='Armature stroke (mm)', ylab_dx=10)
for ch, idx in ((ci, 1), (cx, 2)):
    td = [q[0] * 1000 for q in rd]
    ch.line(td, [q[idx] for q in rd], C['blue'])
    ch.line([q[0] * 1000 for q in rz], [q[idx] for q in rz], C['orange'])
for ch in (ci, cx):
    for v in (0, 20, 60): ch.vline(v, C['gold'], w=1.4, dash='6 4', y1=ch.ylim[1])
# event markers (drawn through both panels in the HTML via overlay svg)
ci.text(0, 3.2, 'Power on', C['gold'], fs=12, dx=6)
ci.text(20, 3.2, 'Boost ends', C['gold'], fs=12, dx=6)
ci.text(60, 3.2, 'Power off', C['gold'], fs=12, dx=6)
ci.text(8.5, 0.72, '↑ dip in current: back-EMF of the moving armature', C['muted'], fs=12, halo=True)
cx.text(7.5, 2.62, f'Pulled in at {pd*1000:.1f} ms', C['ink'], fs=13, bold=True, dx=4, halo=True)
cx.text(60 + relz * 1000, 0.22, f'{relz*1000:.1f} ms', C['orange'], fs=12, bold=True, dx=5)
cx.text(60 + reld * 1000, 1.4, f'{reld*1000:.1f} ms', C['blue'], fs=13, bold=True, dx=8)

# dashed event lines spanning both charts: overlay svg positioned absolutely
H1, H2, gap = 290, 320, 64
xs = [ci.X(v) for v in (0, 20, 60)]
ov = ''.join(f'<line x1="{x:.1f}" y1="{H1-2}" x2="{x:.1f}" y2="{H1+gap+cx.y0-4}" stroke="{C["gold"]}" stroke-width="1.4" stroke-dasharray="6 4"/>' for x in xs)

side = '''<div style="border:1.2px solid #e3e6e9;border-radius:8px;background:#fff;padding:18px 20px;font-size:13px;line-height:1.7;color:#1b2430">
<p style="margin:0 0 14px">Key points</p>
<p style="margin:0 0 14px">• <b style="font-weight:500">Pull-in</b>: the coil current rises with time constant L/R, and the armature moves only once the magnetic force exceeds the spring force. The 1 A hold current alone gives too little force to pull it in; 3 A continuously would pull it in but heat the coil by about 70 W. So the full voltage is applied first (“boost”), and once the armature is home the current is chopped to a 1 A hold (8 W).</p>
<p style="margin:0 0 14px">• <b style="font-weight:500">Release</b>: after switch-off the current must decay through the freewheeling path. A diode puts only 0.7 V across the coil, so the current falls slowly; a Zener diode puts several tens of volts of reverse voltage on the coil, and the current quickly drops below the release current. The price: the power transistor must withstand “supply + Zener” voltage.</p>
<p style="margin:0">• In shaft angle: at 400 r/min, 1 ms = 2.4°.</p></div>'''

body = f'''<p class="title">Trimming solenoid: boost for fast pull-in, Zener for fast release</p>
<p class="sub">Simulation (illustrative parameters): coil 8 Ω, inductance 20–80 mH, stroke 3 mm; 24 V boost for 20 ms, then 1 A hold; power off at 60 ms</p>
<div style="display:flex;gap:34px;margin-top:30px;align-items:flex-start">
<div style="position:relative;width:780px;flex:none">{ci.svg()}<div style="height:{gap}px"></div>{cx.svg()}
<svg width="780" height="{H1+gap+H2}" style="position:absolute;left:0;top:0;pointer-events:none">{ov}</svg></div>
<div style="flex:1;margin-top:4px">{side}</div></div>
<p class="note" style="margin-left:70px;font-size:13px;color:#1b2430">Blue: diode freewheeling, release {reld*1000:.1f} ms; orange: 48 V Zener, release {relz*1000:.1f} ms. Pull-in is the same for both, {pd*1000:.1f} ms.</p>'''
render('fig_13_sol', body)
