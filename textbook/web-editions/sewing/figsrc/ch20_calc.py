# -*- coding: utf-8 -*-
"""Chapter 20 worked-example numbers (all illustrative). Run: python3 ch20_calc.py"""
import math, statistics as st
from ch20_model import *
p = lambda *a: print(*a)
# --- encoder
p('enc res deg', 360/10000)
# --- solenoid delays
for V in (21.6, 24, 26.4):
    for R in (8.0, 9.5):
        tp, tr = sol_delay(V, R); p('sol', V, R, round(tp*1e3, 2), round(tr*1e3, 2))
tpmin, tpmax = sol_delay(26.4, 8.0)[0], sol_delay(21.6, 9.5)[0]
p('R hot 9.5 -> dT K', (9.5/8-1)/0.00393)
for n in (300, 500, 700):
    p('n', n, 'deg/ms', 6*n/1000, 'entry spread deg', 6*n*(tpmax-tpmin), 'mean adv', 6*n*(tpmin+tpmax)/2)
# command angle centre at 300
n = 300; tm = (tpmin+tpmax)/2
p('trim_on centre @300', 315-6*n*tm, '@700', 315-6*700*tm)
p('trel_on latest @300', 335-6*300*tpmax, '@700', 335-6*700*tpmax)
# --- stop
for n in (300, 700):
    tr = Trace(n); r = tr.res
    over = max(q[1] for q in r)-TARGET
    p('stop', n, 'tstop', round(tr.tstop*1e3, 1), 'from engage', round((tr.tstop-tr.tA)*1e3, 1), 'over', round(over, 2), 'ang at flag', round(tr.ang(tr.tstop)-TARGET, 2))
    p('   trim cycle time from 180deg:', tr.tstop)
# --- inertia identification: 1.0 N.m torque, 0 -> 1000 r/min
J = 6e-4; T = 1.0; Tf = 0.15; w = 1000*2*math.pi/60
p('J test time ms', J*w/(T-Tf-2e-4*w/2)*1e3)
# --- velocity loop bandwidth & Kp ratio
p('Kv/J', 0.2/6e-4, 'Kp ratio', 200/(0.2/6e-4))
# --- backtack (ch14): idle angle 211.6, margin 10
for t in (0.018, 0.020, 0.022):
    p('bt nmax', t, (211.6-10)/(6*t))
p('bt 1500 used deg at 22ms', 6*1500*0.022)
# --- speed profile (ch14): 60% of 4417
a = 0.6*(2.5+0.15)/6e-4; p('alpha 60%', a)
for (n1, n2) in ((400, 4000), (4000, 300)):
    dw = abs(n2-n1)*2*math.pi/60; tt = dw/a; revs = (n1+n2)/2/60*tt
    p('ramp', n1, n2, 't', round(tt, 3), 'revs', round(revs, 2))
# --- 24 V budget
# boost current 24/8=3 A for <= pull-in, hold 1 A; trim on 300->408 at 300 r/min = 108 deg = 60 ms
for name, deg in (('trim', 408-300), ('trel', 430-310)):
    p(name, 'on ms @300', deg/1.8)
E_trim = 24*3*0.007 + 1*1*8*(0.060-0.007)  # rough: boost energy + hold
p('energy per trim J (rough)', E_trim)
# --- Monte Carlo acceptance
M = monte(1000, n=300, calib=0.1, seed=7)
ok = sum(m['all'] for m in M); p('MC300 ok', ok)
e = [m['entry'] for m in M]; c = [m['cut'] for m in M]; s = [m['stop']-TARGET for m in M]
p('entry', min(e), max(e), st.mean(e), 'cut', min(c), max(c), 'stop', min(s), max(s), st.mean(s), st.pstdev(s))
p('tstop ms mean', st.mean(m['tstop'] for m in M)*1e3)
M = monte(1000, n=300, calib=0.1, seed=7, Vmu=20.0)
p('MC low V(20V) ok', sum(m['all'] for m in M), min(m['entry'] for m in M), max(m['entry'] for m in M))
M = monte(300, n=700, calib=0.1, seed=8)
p('MC700 std events ok', sum(m['all'] for m in M), {k: sum(m['ok'][k] for m in M) for k in M[0]['ok']})
EV7 = dict(STD_EVENTS, trim_on=285.0, trel_on=290.0)
M = monte(300, ev=EV7, n=700, calib=0.1, seed=8)
p('MC700 tuned ok', sum(m['all'] for m in M), min(m['entry'] for m in M), max(m['entry'] for m in M), min(m['ropen'] for m in M), max(m['ropen'] for m in M), min(m['cut'] for m in M), max(m['cut'] for m in M))
