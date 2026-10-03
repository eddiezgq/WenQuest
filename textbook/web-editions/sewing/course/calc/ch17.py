"""Ch17 numbers for the course pack (all from the formulas of Chapter 17)."""
from math import pi, sqrt

def p(E):            # needle pitch mm
    return 25.4 / E

def tn(E, v):        # ms per needle
    return p(E) / v

R = {}
# 17.1 / 17.3
R['p_E12'] = p(12); R['p_E7'] = p(7)
R['tn_E12_1.2'] = tn(12, 1.2)
# selector force & armature time (17.2.1)
mu0 = 4e-7 * pi
R['F_sel'] = 0.8**2 * 10e-6 / (2 * mu0)
R['t_arm_ms'] = sqrt(2 * 0.0003 * 0.0005 / 2.5) * 1e3
# lag without compensation
R['lag_E12'] = 1.2 * 0.6 / p(12)                 # v[m/s]*Td[ms] = mm
# exercise 1 & 2
R['ex1_E7'] = tn(7, 1.0); R['ex1_E16'] = tn(16, 1.0)
R['ex2_E14'] = 1.2 * 0.5 / p(14)
# exercise 3: fixed lead tuned at 1.2 m/s, needle passed at 0.5 m/s
R['ex3_mm'] = (1.2 - 0.5) * 0.6; R['ex3_p'] = R['ex3_mm'] / p(12)
# fig 17-4 fixed-lead max early error 0.283 p -> speed at start
R['fig174_v0'] = 1.2 - 0.283 * p(12) / 0.6
# braking distance
R['brake_mm'] = 1.2**2 / (2 * 20) * 1e3
# 17.6 needles/courses
R['needles'] = 50 * 5.5; R['courses'] = 60 * 7
# 17.7 closed loop worked example
N, ls, Lm = 275, 5.0, 1400
dl = Lm / N - ls; R['cl_dl'] = dl; R['cl_dev_pct'] = (Lm / (N * ls) - 1) * 100
R['cl_dd'] = -0.5 * dl / 2; R['cl_steps'] = R['cl_dd'] / 0.01
# exercise 6
dl6 = 1176 / 200 - 6.0; R['ex6_dl'] = dl6; R['ex6_dd'] = -0.5 * dl6 / 2
# quiz: N=240, l*=5.5, Lm=1290
dlq = 1290 / 240 - 5.5; R['q_dl'] = dlq; R['q_dd'] = -0.5 * dlq / 2; R['q_steps'] = R['q_dd'] / 0.01

# 17.8 design example
def pass_time(w, Lk, v, a, c=None, dwell=0.05):
    if c is None: c = v**2 / (2 * a) * 1e3
    D = w + Lk + 2 * c
    return D, D / 1e3 / v + v / a + dwell
w = 275 * p(12); R['w'] = w
D0, t0 = pass_time(w, 150, 1.2, 10); R['base_D'] = D0; R['base_t'] = t0; R['base_min'] = t0 * 760 / 60
DA, tA = pass_time(w, 150, 1.2, 10, c=20); R['A_t'] = tA; R['A_min'] = tA * 760 / 60
DB, tB = pass_time(w, 300, 1.2, 10); R['B_t'] = tB; R['B_min'] = tB * 460 / 60
DC, tC = pass_time(w, 150, 1.6, 10); R['C_t'] = tC; R['C_min'] = tC * 760 / 60; R['C_c'] = 1.6**2 / 20 * 1e3
R['C_gain_pct'] = (1 - R['C_min'] / R['base_min']) * 100
R['tn_E12_1.6'] = tn(12, 1.6)
R['E18_vmax'] = p(18) / 1.2; R['tn_E18_1.2'] = tn(18, 1.2)
# exercise 7: 100-needle cuff
wc = 100 * p(12); Dc, tc = pass_time(wc, 150, 1.2, 10); R['cuff_D'] = Dc; R['cuff_t'] = tc
R['cuff_overhead_pct'] = (150 + 2 * 72) / Dc * 100
# three cuffs side by side (3 x 100 needles, 10-needle gaps not counted)
w3 = 300 * p(12); D3, t3 = pass_time(w3, 150, 1.2, 10); R['cuff3_t_each'] = t3 / 3

# assignment: E14 sleeve 180 needles, v=1.0, a=8, Lk=150, dwell .05, Td=0.5, Tc=1.3, 500 courses
pE = p(14); R['as_p'] = pE; R['as_tn'] = tn(14, 1.0); R['as_lag'] = 1.0 * 0.5 / pE
ws = 180 * pE; R['as_w'] = ws
Ds, ts = pass_time(ws, 150, 1.0, 8); R['as_c'] = 1.0**2 / 16 * 1e3; R['as_D'] = Ds; R['as_t'] = ts; R['as_min'] = ts * 500 / 60
R['as_vmax'] = pE / 1.3
Ds2, ts2 = pass_time(ws, 150, 1.0, 8, c=20); R['as_t_rt'] = ts2; R['as_min_rt'] = ts2 * 500 / 60; R['as_save_min'] = R['as_min'] - R['as_min_rt']
dla = 1026 / 180 - 5.5; R['as_dl'] = dla; R['as_dd'] = -0.5 * dla / 2; R['as_steps'] = R['as_dd'] / 0.01
# two sleeves side by side (360 needles) vs one: overhead share
R['as_overhead1'] = (150 + 2 * 62.5) / Ds * 100
D2s, t2s = pass_time(2 * ws, 150, 1.0, 8); R['as_overhead2'] = (150 + 2 * 62.5) / D2s * 100; R['as_t2_each'] = t2s / 2
# exam: E10, v 1.0, Td .6 fixed lead tuned 1.0, needle at 0.4
R['ex_E10_early_p'] = (1.0 - 0.4) * 0.6 / p(10)

if __name__ == '__main__':
    for k, v in R.items():
        print(f'{k:16s} {v:.4f}')
