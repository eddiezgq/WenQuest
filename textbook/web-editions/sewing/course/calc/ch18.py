"""Ch18 numbers: the thermal / EMC / burn-in model of Chapter 18 (same as Virtual lab 18-1, illustrative values)."""
from math import sqrt, pi, exp

VDC, VCE0, RCE, VF0, RF, MCOS, RRF = 310, 1.0, 0.10, 0.9, 0.08, 0.6, 0.3
RTH, TAU, RBOX, PAUX, TACC, CDT, HY, CPAR = 3.5, 0.05, 0.6, 8, 0.15, 5, 4800, 300e-12

def sw(I, f, t):
    Ip = sqrt(2) * I
    pc = VCE0 * Ip * (1 / (2 * pi) + MCOS / 8) + RCE * Ip**2 * (1 / 8 + MCOS / (3 * pi))
    pd = VF0 * Ip * (1 / (2 * pi) - MCOS / 8) + RF * Ip**2 * (1 / 8 - MCOS / (3 * pi))
    ps = 0.5 * VDC * (Ip / pi) * t * f
    return pc, ps, pd + RRF * ps

def inv(I, f, t):
    pc, ps, pd = sw(I, f, t)
    return 6 * (pc + ps + pd) + 2 * 0.9 * 0.6 * I

def thermal(Ta=40, starts=30, duty=0.5, Irun=3, Ipk=9, fsw=12, tsw=300, rhs=1.5, clog=0, L0=2000):
    f, t, tc = fsw * 1e3, tsw * 1e-9, 60 / starts
    facc = min(TACC * 2 / tc, duty); frun = max(duty - facc, 0)
    Pk, Pr = inv(Ipk, f, t), inv(Irun, f, t)
    Pavg = facc * Pk + frun * Pr
    rh = rhs * (1 + 1.5 * clog)
    Tin = Ta + RBOX * (1 + clog) * (Pavg + PAUX)
    Ths = Tin + rh * Pavg
    pc, ps, _ = sw(Ipk, f, t)
    Tjpk = Ths + (pc + ps) * RTH * (1 - exp(-TACC / TAU))
    Tcap = Tin + CDT
    life = min(L0 * 2 ** ((105 - Tcap) / 10), 30 * HY)
    return dict(Pk=Pk, Pr=Pr, Pavg=Pavg, facc=facc, heat_share=facc * Pk / Pavg, Tin=Tin, Ths=Ths, Tjpk=Tjpk,
                Tcap=Tcap, life_h=life, life_y=life / HY, icm=CPAR * VDC / (t / 2))

EA, KB, BETA, ETA, LAM, TUSE, RISE = 0.7, 8.617e-5, 0.5, 100, 1e-6, 55, 15
def af(Tbox): return exp(EA / KB * (1 / (TUSE + 273.15) - 1 / (Tbox + RISE + 273.15)))
def Fw(t): return 1 - exp(-(t / ETA) ** BETA) if t > 0 else 0
def burn(p, Tbox, h):
    te = af(Tbox) * h; sc = p * Fw(te); esc = p * (Fw(te + HY) - Fw(te)); rnd = (1 - p) * (1 - exp(-LAM * HY))
    ret = esc + rnd
    return dict(AF=af(Tbox), te=te, screened=sc, escaped=esc, random=rnd, ret=ret, cost=0.3 * h + 600 * ret + 50 * sc)

def tsw_window(**kw):
    ok = [t for t in range(50, 1201, 5) if (r := thermal(tsw=t, **kw))['Tjpk'] <= 125 and r['icm'] <= 0.8 and r['Ths'] <= 100]
    return (min(ok), max(ok)) if ok else None

R = {}
R['P_3A'] = inv(3, 12e3, 300e-9); R['P_9A'] = inv(9, 12e3, 300e-9)
for name, kw in [('std40', {}), ('std45', {'Ta': 45}), ('t600_45', {'Ta': 45, 'tsw': 600}), ('t100_45', {'Ta': 45, 'tsw': 100}),
                 ('case38', {'Ta': 38}), ('clog03', {'Ta': 38, 'clog': 0.3}), ('clog05', {'Ta': 38, 'clog': 0.5}),
                 ('clog08', {'Ta': 38, 'clog': 0.8}), ('fix_rhs1', {'Ta': 38, 'clog': 0.5, 'rhs': 1.0}),
                 ('f20_45', {'Ta': 45, 'fsw': 20}), ('starts60', {'starts': 60})]:
    R[name] = thermal(**kw)
R['window_45'] = tsw_window(Ta=45)
R['window_45_f20'] = tsw_window(Ta=45, fsw=20)
R['burn0'] = burn(0.01, 55, 0); R['burn70_8'] = burn(0.01, 70, 8)
# search burn-in options for task 3
best = sorted((burn(0.01, T, h)['cost'], T, h) for T in range(25, 71) for h in range(0, 49) if burn(0.01, T, h)['ret'] < 0.01 and burn(0.01, T, h)['cost'] <= 9)
R['burn_best'] = best[:3]
# exercises
R['ex1_Psw'] = 0.5 * 310 * 2 * 400e-9 * 16e3
R['ex2_Ths'] = 40 + 20 * 1.8; R['ex2_Tj'] = R['ex2_Ths'] + 3 * 3.5
R['ex3_65'] = 2000 * 2 ** ((105 - 65) / 10); R['ex3_75'] = 2000 * 2 ** ((105 - 75) / 10)
R['ex4_icm'] = 400e-12 * 310 / 100e-9; R['ex4_tr'] = 400e-12 * 310 / 0.5 * 1e9
# quiz / exam extras
R['q_Psw'] = 0.5 * 310 * 3 * 300e-9 * 12e3                     # 3 A avg, 300 ns, 12 kHz
R['q_icm'] = 300e-12 * 310 / 200e-9                             # 200 ns rise
R['q_cap_70'] = 2000 * 2 ** ((105 - 70) / 10)                   # h
R['q_Tj'] = 35 + 18 * 2.0 + 4 * 3.5                              # assignment-like
R['af_70'] = af(70); R['af_ex'] = exp(0.7 / 8.617e-5 * (1 / (50 + 273.15) - 1 / (90 + 273.15)))
R['Ibar_3A'] = sqrt(2) * 3 / pi
# assignment: 5000 h capacitor at 38 C clog 0.5; and Ta 45 fsw 16 window
R['as_L5000_clog05'] = thermal(Ta=38, clog=0.5, L0=5000)
R['as_f16_45'] = thermal(Ta=45, fsw=16); R['as_window_f16'] = tsw_window(Ta=45, fsw=16)

# assignment task 1 hand calc at 45 C
pc, ps, _ = sw(9, 12e3, 300e-9); R['as_dev_peak'] = pc + ps
Pavg = R['std45']['Pavg']; R['as_Tin'] = 45 + 0.6 * (Pavg + 8); R['as_Ths'] = R['as_Tin'] + 1.5 * Pavg
R['as_Tj'] = R['as_Ths'] + R['as_dev_peak'] * 3.5 * (1 - exp(-0.15 / 0.05)); R['as_Tcap'] = R['as_Tin'] + 5
R['as_life_h'] = 2000 * 2 ** ((105 - R['as_Tcap']) / 10)
# assignment task 2: clean heat-sink resistance needed at 38 C, clog 0.5, for Ths <= 100
Tin = 38 + 0.6 * 1.5 * (Pavg + 8); R['as2_Tin'] = Tin; R['as2_rhs_max'] = (100 - Tin) / (1.75 * Pavg)
R['as2_check'] = thermal(Ta=38, clog=0.5, rhs=R['as2_rhs_max'])
R['as2_rise_j'] = R['as_dev_peak'] * 3.5 * (1 - exp(-0.15 / 0.05))
R['as2_rhs_max_j'] = (125 - R['as2_rise_j'] - Tin) / (1.75 * Pavg)
R['as2_check_j'] = thermal(Ta=38, clog=0.5, rhs=R['as2_rhs_max_j'])
R['ex_tr_250pF'] = 250e-12 * 310 / 0.6 * 1e9
R['ex_cap5000_65'] = 5000 * 2 ** ((105 - 65) / 10)

if __name__ == '__main__':
    for k, v in R.items():
        if isinstance(v, dict):
            print(k, {a: round(b, 3) for a, b in v.items()})
        else:
            print(k, v if not isinstance(v, float) else round(v, 4))
