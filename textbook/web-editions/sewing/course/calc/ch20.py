"""Ch20 numbers for the course pack. Uses the book's own models figsrc/ch20_model.py and figsrc/ch20_ol.py."""
import sys, os, math, statistics as st
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'figsrc'))
import ch20_model as M
import ch20_ol as OL

R = {}
# solenoid delays (ch13 model): cold/hot, +-10 % supply
for V in (21.6, 24.0, 26.4):
    for Rc in (8.0, 9.5):
        R[f'sol_{V}_{Rc}'] = tuple(x * 1e3 for x in M.sol_delay(V, Rc))
tpmin, tpmax = M.sol_delay(26.4, 8.0)[0], M.sol_delay(21.6, 9.5)[0]
R['tp_min_ms'], R['tp_max_ms'] = tpmin * 1e3, tpmax * 1e3
R['tr_ms'] = M.sol_delay(24.0, 8.0)[1] * 1e3
R['R_hot_dT'] = (9.5 / 8 - 1) / 0.00393
for n in (300, 400, 700):
    R[f'deg_ms_{n}'] = 6 * n / 1000
    R[f'pull_deg_{n}'] = (6 * n * tpmin, 6 * n * tpmax, 6 * n * (tpmax - tpmin))
    R[f'trim_on_centre_{n}'] = 315 - 6 * n * (tpmin + tpmax) / 2
R['trel_on_latest_300'] = 335 - 6 * 300 * tpmax
R['hot_shift_deg_300'] = 6 * 300 * (M.sol_delay(24, 9.5)[0] - M.sol_delay(24, 8.0)[0])
R['n_max_20deg'] = 20 / (6 * tpmax); R['n_max_20deg_6ms'] = 20 / (6 * 0.006)
# exercise 1 uses book's 6.2-9.4 ms at 400 r/min
R['ex1'] = (6 * 400 * 0.0062, 6 * 400 * 0.0094, 6 * 400 * 0.0032, 315 - 6 * 400 * (0.0062 + 0.0094) / 2)
# encoder / Z calibration (symmetric two-point method)
r1, r2 = 307.6, 137.2
bdc = (r1 + r2 + 360) / 2 % 360; R['zcal_bdc'] = bdc; R['zcal_offset'] = 180 - bdc
# needle-bar displacement near TDC: r = 15.5, l = 55
r_, l_ = 15.5, 55.0
def drop(phi_deg):
    p = math.radians(phi_deg)
    return r_ + l_ - (r_ * math.cos(p) + math.sqrt(l_**2 - (r_ * math.sin(p))**2))
R['drop_1.8deg_mm'] = drop(1.8)
# slope at 12 mm from TDC
from scipy.optimize import brentq  # noqa
phi12 = brentq(lambda a: drop(a) - 12.0, 1, 179); R['phi_12mm'] = phi12
R['slope_12mm_mm_per_deg'] = (drop(phi12 + 0.01) - drop(phi12 - 0.01)) / 0.02
R['res_deg_0.01mm'] = 0.01 / R['slope_12mm_mm_per_deg']
# quiz variant: readings 79.0 (down) and 301.0 (up), no wrap
R['q_zcal'] = 180 - (79.0 + 301.0) / 2
# servo: inertia identification, bandwidth
J, T, Tf, w = 6e-4, 1.0, 0.15, 1000 * 2 * math.pi / 60
R['J_test_ms'] = J * w / (T - Tf - 2e-4 * w / 2) * 1e3
R['vel_bw'] = 0.2 / 6e-4; R['Kp_ratio'] = 200 / R['vel_bw']
# backtack
for t in (0.018, 0.020, 0.022):
    R[f'bt_nmax_{int(t*1e3)}'] = 201.6 / (6 * t)
R['bt_1500_22'] = 6 * 1500 * 0.022
# speed profile 60 % of capacity
a = 0.6 * (2.5 + 0.15) / 6e-4; R['alpha60'] = a
for (n1, n2) in ((400, 4000), (4000, 300)):
    dw = abs(n2 - n1) * 2 * math.pi / 60; tt = dw / a; R[f'ramp_{n1}_{n2}'] = (tt, (n1 + n2) / 2 / 60 * tt)
# power budget
R['psu_peak_A'] = 2 * 24 / 8 + 0.5; R['psu_peak_W'] = R['psu_peak_A'] * 24
R['trim_trel_gap_ms'] = 10 / 1.8
R['pfl_hold_W'] = 1.0**2 * 8
# event-table scan error at 10 kHz
R['scan_err_300'] = 6 * 300 * 1e-4; R['scan_err_700'] = 6 * 700 * 1e-4
# CAN latency example
R['can_0.5ms_deg_300'] = 6 * 300 * 0.5e-3
# overlock
for i in (1.0, 1.25, 1.4):
    R[f'ol_{i}'] = OL.opt(i)
o = OL.opt(1.25)
R['ol_counts_1.25'] = 10000 / 1.25; R['ol_counts_1.4'] = 10000 / 1.4
R['ol_N1'] = 25 / 3; R['ol_N2'] = 40 / 3
for n in (4000, 5000, 7000):
    Nb = o['revs_dec'] * (n / 7000)**2; R[f'ol_Nb_{n}'] = (Nb, 23 - Nb)
R['ol_extra_mm_7000'] = o['revs_dec'] * 3
R['ol_extra_5000'] = (R['ol_Nb_5000'][0], R['ol_Nb_5000'][0] * 3)
R['ol_v_7000'] = 3 * 7000 / 60
R['deb_6000_20ms'] = 2.5 * 6000 / 60 * 0.02; R['deb_6000_2st'] = 2 * 2.5
R['diff_travel'] = (2.0 - 0.7) * 20; R['diff_step'] = 1.0 / (200 * 8); R['diff_time'] = R['diff_travel'] / 10
# quiz variant: 6000 r/min decel stitches with 1.25
R['q_Nb_6000'] = o['revs_dec'] * (6000 / 7000)**2
# exam: 3 mm stitch, 4500 r/min, 30 ms debounce
R['ex_deb_4500_30'] = 3 * 4500 / 60 * 0.03
# assignment: trimming at 500 r/min using tp 6.2-9.4
R['as_500'] = (6 * 500 * 0.0062, 6 * 500 * 0.0094, 315 - 6 * 500 * (0.0062 + 0.0094) / 2, 335 - 6 * 500 * 0.0094)
# assignment (350 r/min trimming; book's 6.2-9.4 ms spread)
R['as_350'] = (6 * 350 * 0.0062, 6 * 350 * 0.0094, 6 * 350 * 0.0032, 315 - 6 * 350 * (0.0062 + 0.0094) / 2, 335 - 6 * 350 * 0.0094)
bdc2 = (296.3 + 125.9 + 360) / 2 % 360; R['as_zcal'] = (bdc2, 180 - bdc2)
N1, N2 = 30 / 2.5, 35 / 2.5; Nb6 = o['revs_dec'] * (6000 / 7000)**2
R['as_ol'] = (N1, N2, N1 + N2, Nb6, N1 + N2 - Nb6, Nb6 * 2.5)
R['ex_nmax_7.5ms'] = 20 / (6 * 0.0075)
R['q_bt_20ms'] = 201.6 / (6 * 0.020)
# reuse ratio
R['reuse'] = 11 / 19

if __name__ == '__main__':
    mc = '--mc' in sys.argv
    if mc:
        Mx = M.monte(1000, n=300, calib=0.1, seed=7)
        s = [m['stop'] - M.TARGET for m in Mx]; e = [m['entry'] for m in Mx]
        R['mc300'] = dict(ok=sum(m['all'] for m in Mx), entry=(min(e), max(e)), stop=(min(s), max(s), st.mean(s), st.pstdev(s)),
                          tstop_ms=st.mean(m['tstop'] for m in Mx) * 1e3)
    for k, v in R.items():
        if isinstance(v, float): v = round(v, 4)
        elif isinstance(v, tuple): v = tuple(round(x, 4) if isinstance(x, float) else x for x in v)
        elif isinstance(v, dict): v = {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items()}
        print(k, v)
