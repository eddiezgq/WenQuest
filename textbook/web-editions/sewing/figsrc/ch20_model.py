# -*- coding: utf-8 -*-
"""Chapter 20 model: WQ-SC/LS prototype trim cycle.
Same models as ch13 (servo.html, solenoid.html) and ch14 (trim.html); the virtual lab
labs/proto-ls.html ports this file line by line.  All values are illustrative (示意)."""
import math, random
D = math.pi/180
# ---------------- servo (ch13 / servo.html) ----------------
B, TMAX, TAUI = 2e-4, 2.5, 0.5e-3
SERVO = dict(Kp=200.0, Kv=0.2, Ti=12e-3, J=6e-4, Tf=0.15, wp=200.0, e0=45.0)
TARGET = 430.0            # needle-up stop target: 70 deg of the next revolution (book angle, 0 = needle-bar TDC)
def stop_sim(n0, p=SERVO, Tf=None, Tl=0.0, dt=2e-5, tend=0.25):
    """Position loop engaged at TARGET-e0 with the spindle running at n0 r/min.
    Returns list of (t, angle_deg_abs, speed_rpm). Tl: extra load torque (thread/fabric drag)."""
    Tf = p['Tf'] if Tf is None else Tf
    J, Kp, Kv, Ti = p['J'], p['Kp'], p['Kv'], p['Ti']
    wpos = p['wp']*2*math.pi/60
    th = -p['e0']*D; w = n0*2*math.pi/60
    Tm = Tf+B*w+Tl; integ = Tm/Kv - (wpos-w)   # speed loop was holding n0
    integ = (Tf+B*w+Tl)/Kv
    res = []; n = int(tend/dt)
    for k in range(n):
        e = -th
        wref = max(-wpos, min(wpos, Kp*e)); ew = wref-w
        integ += ew*dt/Ti
        Tref = Kv*(ew+integ)
        if abs(Tref) > TMAX:
            Tref = math.copysign(TMAX, Tref); integ -= ew*dt/Ti
        Tm += (Tref-Tm)*dt/TAUI
        Td = Tm-B*w-Tl
        if abs(w) < 1e-3 and abs(Td) <= Tf: acc = -w/dt
        else: acc = (Td-Tf*(math.copysign(1, w) if abs(w) >= 1e-3 else math.copysign(1, Td)))/J
        w += acc*dt; th += w*dt
        if k % 5 == 0: res.append((k*dt, TARGET+th/D, w*60/2/math.pi))
    return res
# ---------------- solenoid (ch13 / solenoid.html) ----------------
SOL = dict(L1=0.08, ga=1e-3, xmax=3e-3, m=0.02, k=1000.0, c=4.0, F0=7.0)
def sol_sim(V=24.0, R=8.0, tb=10e-3, Ih=1.0, Vz=48.0, ton=30e-3, dt=2e-6):
    P = SOL
    Lx = lambda x: P['L1']*P['ga']/(P['ga']+P['xmax']-x)
    dLx = lambda x: P['L1']*P['ga']/(P['ga']+P['xmax']-x)**2
    lam = x = v = 0.0; pull = rel = None; t = 0.0; k = 0
    while t < ton+0.04:
        t = k*dt; L = Lx(x); i = lam/L
        if t < ton: u = V if (t < tb or i < Ih) else -0.7
        else:
            if i > 1e-4: u = -Vz
            else: u = 0; lam = 0; i = 0
        lam += (u-i*R)*dt
        F = 0.5*i*i*dLx(x); Fs = P['F0']+P['k']*x
        a = (F-Fs-P['c']*v)/P['m']
        if x <= 0 and a < 0: a = 0; v = 0
        if x >= P['xmax'] and a > 0: a = 0; v = 0
        v += a*dt; x = min(P['xmax'], max(0, x+v*dt))
        if (x == 0 and v < 0) or (x == P['xmax'] and v > 0): v = 0
        if pull is None and x >= 0.999*P['xmax']: pull = t
        if rel is None and t > ton and x <= 0.001*P['xmax']: rel = t-ton; break
        k += 1
    return pull, rel
# ---------------- ch14 windows (trim.html) ----------------
KNIFE = (300.0, 330.0)        # knife must enter the loop here
CUT = (45.0+360, 65.0+360)    # knife return / cut around take-up top 55 deg (+-10, illustrative)
REL = (335.0, 415.0)          # tension released at least over this range
NEEDLE_IN = 360+101.7
# ---------------- one trim cycle on the prototype ----------------
ENGAGE = TARGET-SERVO['e0']           # 385 deg = 25 deg of the next revolution
STD_EVENTS = dict(trim_on=300.0, trim_off=408.0, trel_on=310.0, trel_off=440.0,
                  wipe_on=0.0, wipe_len=40.0, pfl_on=80.0)   # wipe/pfl: ms after 'stopped'
WIPE_PULL, WIPE_RET, PFL_T = 12e-3, 15e-3, 40e-3            # illustrative
_grid = None
def sol_grid():
    global _grid
    if _grid is None:
        Vs = [20.0+0.5*i for i in range(17)]; Rs = [7.5+0.25*j for j in range(11)]
        _grid = (Vs, Rs, [[sol_sim(V, R) for R in Rs] for V in Vs])
    return _grid
def sol_delay(V, R):
    Vs, Rs, G = sol_grid()
    fi = (V-Vs[0])/0.5; fj = (R-Rs[0])/0.25
    i = min(len(Vs)-2, max(0, int(fi))); j = min(len(Rs)-2, max(0, int(fj)))
    u = min(1, max(0, fi-i)); w = min(1, max(0, fj-j))
    out = []
    for q in (0, 1):
        a = G[i][j][q]*(1-u)*(1-w)+G[i+1][j][q]*u*(1-w)+G[i][j+1][q]*(1-u)*w+G[i+1][j+1][q]*u*w
        out.append(a)
    return out
class Trace:
    def __init__(s, n, Tf=0.15, Tl=0.0):
        s.n = n; s.tA = (ENGAGE-180.0)/(6*n)
        s.res = stop_sim(n, Tf=Tf, Tl=Tl)
        # stopped flag: |e|<=0.5 deg and |n|<10 r/min for 5 ms
        s.tstop = None; run = 0.0; prev = 0.0
        for (t, a, sp) in s.res:
            if abs(a-TARGET) <= 0.5 and abs(sp) < 10: run += t-prev
            else: run = 0.0
            prev = t
            if run >= 5e-3: s.tstop = s.tA+t; break
        if s.tstop is None: s.tstop = s.tA+s.res[-1][0]
    def ang(s, t):
        if t <= s.tA: return 180.0+6*s.n*t
        k = min(len(s.res)-1, int((t-s.tA)/(5*2e-5)))
        return s.res[k][1]
    def t_of(s, a):
        """time the spindle first reaches angle a; None if it never does"""
        if a <= ENGAGE: return (a-180.0)/(6*s.n)
        for (t, x, sp) in s.res:
            if x >= a: return s.tA+t
        return None
def trial(ev=STD_EVENTS, n=300.0, V=24.0, R=8.0, Tf=0.15, Tl=0.0, calib=0.0, jit=0.0, trace=None):
    """calib: calibration residual (encoder reading - true angle), deg. Firmware fires events on
    the *reading*, so the true angle at command = commanded angle - calib."""
    tr = trace or Trace(n, Tf, Tl)
    tp, trl = sol_delay(V, R); tp += jit
    def cmd_t(a):
        t = tr.t_of(a+calib*0)   # reading == commanded angle; physical spindle angle = reading - calib
        return tr.tstop if t is None or t > tr.tstop else t
    phys = lambda t: tr.ang(t)-calib
    t1 = cmd_t(ev['trim_on']); t2 = cmd_t(ev['trim_off'])
    entry = phys(t1+tp); cut = phys(t2+trl)
    t3 = cmd_t(ev['trel_on']); t4 = cmd_t(ev['trel_off'])
    ropen = phys(t3+tp); rclose = phys(t4+trl) if t4 < tr.tstop else 1e9
    stop = tr.ang(tr.tstop+0.0)-calib
    wipe_end = ev['wipe_on']+ev['wipe_len']+WIPE_RET*1e3
    ok = dict(entry=KNIFE[0] <= entry <= KNIFE[1], cut=CUT[0] <= cut <= CUT[1] and cut < tr.ang(1e9) + 1e-9 or False,
              rel=ropen <= REL[0] and rclose >= REL[1], stop=abs(stop-TARGET) <= 1.0,
              wipe=ev['wipe_len'] >= WIPE_PULL*1e3, pfl=ev['pfl_on'] >= wipe_end)
    ok['cut'] = CUT[0] <= cut <= CUT[1]
    return dict(entry=entry, cut=cut, ropen=ropen, rclose=rclose, stop=stop, tstop=tr.tstop, ok=ok, all=all(ok.values()))
def monte(N=1000, ev=STD_EVENTS, n=300.0, calib=0.0, seed=1, Vmu=24.0):
    rnd = random.Random(seed); out = []
    traces = {}
    for k in range(N):
        V = min(Vmu*1.1, max(Vmu*0.9, rnd.gauss(Vmu, 1.0))); R = rnd.uniform(8.0, 9.5)
        nn = n*(1+max(-0.03, min(0.03, rnd.gauss(0, 0.01)))); Tf = rnd.uniform(0.12, 0.18)
        Tl = rnd.uniform(-0.05, 0.05); jit = rnd.gauss(0, 0.2e-3)
        tr = Trace(nn, Tf, Tl)
        out.append(trial(ev, nn, V, R, Tf, Tl, calib, jit, trace=tr))
    return out
