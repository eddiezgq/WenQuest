# -*- coding: utf-8 -*-
"""Chapter 20: overlock prototype WQ-SC/OL numbers (illustrative)."""
import math
Jm, Js, Tpk, Tf = 1.2e-4, 4.0e-4, 2.5, 0.15     # motor rotor, spindle side (reflected mechanisms), peak torque, friction at spindle
def opt(i, nmax_s=7000):
    """i = spindle speed / motor speed (belt speed-up ratio)"""
    Jeq = Jm + Js*i*i            # at motor shaft
    nm = nmax_s/i
    wm = nm*2*math.pi/60
    a_acc = 0.6*Tpk/Jeq          # 60% of peak (ch14 practice), friction ignored for accel margin
    a_dec = 0.6*(Tpk+Tf*i)/Jeq
    t_acc = wm/a_acc; t_dec = wm/a_dec
    revs_dec = (nmax_s/60)*t_dec/2   # spindle revolutions during a linear decel
    return dict(i=i, Jeq=Jeq, nm=nm, t_acc=t_acc, t_dec=t_dec, revs_dec=revs_dec)
if __name__ == '__main__':
    for i in (1.0, 1.4, 2.0):
        print({k: round(v, 5) for k, v in opt(i).items()})
    o = opt(1.4)
    for n in (3000, 5000, 7000):
        f = n/7000; print('n', n, 'decel stitches', round(o['revs_dec']*f*f, 1), 'time', round(o['t_dec']*f, 3))
    # edge sensor
    s = 3.0; ds = 25.0; Lc = 40.0
    for n in (3000, 7000):
        v = s*n/60; print('fabric speed mm/s', v, '1 ms ->', v/1000, 'mm; 20 ms debounce ->', v*0.02, 'mm')
    print('N1', ds/s, 'N2', Lc/s)
    # differential: l_m = 20 mm, D 0.7..2.0
    lm = 20; travel = (2.0-0.7)*lm; lead = 1.0; steps = 200*8
    print('travel', travel, 'mm/microstep', lead/steps, 'time@10mm/s', travel/10)
    # belt: encoder counts per spindle rev, i = 1.4 -> motor turns 1/1.4 per spindle rev
    print('counts per spindle rev', 10000/1.4, 'motor revs per 5 spindle revs', 5/1.4)
