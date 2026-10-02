"""Examples 39.6.1–39.6.3: decision rules for automatic inspection and statistical process control.

39.6.1 Decision and guard band: expanded measurement uncertainty U; the acceptance zone is narrowed by U at each end.
39.6.2 Digital factory, SH-301 bearing-seat diameter Ø35 k6 (35.002–35.018 mm): with the factory simulation's grinding model
       (factory/digital/sim/engine.py) take 100 consecutive parts, 5 per subgroup, draw mean–range control charts, find
       out-of-control subgroups with the common rules, and compare them with the parts out of tolerance.
39.6.3 Improvement: change the wheel dressing interval from "life used up" (about 28 parts) to every 14 parts, and compare
       the number of parts out of tolerance and the process performance index.
"""
import numpy as np

from _meas import A2, D2, D3, D4, NOMINAL, SPEC_HI, SPEC_LO, bearing_seat
from bookout import T, out

# 39.6.1 guard band
U = 0.0012
acc_lo, acc_hi = SPEC_LO + U, SPEC_HI - U


def chart(x):
    g = x.reshape(-1, 5)
    xbar, R = g.mean(1), g.max(1) - g.min(1)
    xbb, Rbar = float(xbar.mean()), float(R.mean())
    return xbar, R, xbb, Rbar, xbb + A2 * Rbar, xbb - A2 * Rbar, D4 * Rbar, D3 * Rbar


def signals(xbar, xbb, ucl, lcl):
    """Common rules for special causes (only the first one per subgroup is recorded): one point beyond a control limit;
    6 points in a row rising or falling; 9 points in a row on one side of the centre line."""
    out = []
    for i in range(len(xbar)):
        if xbar[i] > ucl or xbar[i] < lcl:
            out.append((i + 1, T("一点越出控制限", "one point beyond a control limit")))
        elif i >= 5 and (all(xbar[j] > xbar[j - 1] for j in range(i - 4, i + 1)) or all(xbar[j] < xbar[j - 1] for j in range(i - 4, i + 1))):
            out.append((i + 1, T("连续 6 点递增或递减", "6 points in a row rising or falling")))
        elif i >= 8 and (all(v > xbb for v in xbar[i - 8:i + 1]) or all(v < xbb for v in xbar[i - 8:i + 1])):
            out.append((i + 1, T("连续 9 点在中心线同侧", "9 points in a row on one side of the centre line")))
    return out


def online(x, k0=4):
    """Real-time use: after each subgroup, compute the control limits from the subgroups so far only and check this subgroup.
    Returns the subgroup number and rule of the first alarm."""
    g = x.reshape(-1, 5)
    for i in range(k0, len(g) + 1):
        xbar, _, xbb, _, ucl, lcl, _, _ = chart(g[:i].ravel())
        hit = [s for s in signals(xbar, xbb, ucl, lcl) if s[0] == i]
        if hit:
            return hit[0]
    return None


def perf(x, Rbar):
    sig_w = Rbar / D2                         # within-subgroup (short-term) standard deviation
    s_all = float(x.std(ddof=1))              # overall (long-term) standard deviation, including the drift from wheel wear
    mu = float(x.mean())
    cp = (SPEC_HI - SPEC_LO) / (6 * sig_w)
    ppk = min(SPEC_HI - mu, mu - SPEC_LO) / (3 * s_all)
    n_out = int(np.sum((x < SPEC_LO) | (x > SPEC_HI)))
    return sig_w, s_all, cp, ppk, n_out


x, wear = bearing_seat(100)
n_guard = int(np.sum(((x >= SPEC_LO) & (x < acc_lo)) | ((x <= SPEC_HI) & (x > acc_hi))))   # parts within tolerance but in a guard band, hence rejected
xbar, R, xbb, Rbar, ucl, lcl, r_ucl, r_lcl = chart(x)
sig = signals(xbar, xbb, ucl, lcl)
sig_w, s_all, cp, ppk, n_out = perf(x, Rbar)
outs = [i + 1 for i, v in enumerate(x) if v < SPEC_LO or v > SPEC_HI]
r_out = [i + 1 for i, r in enumerate(R) if r > r_ucl]
assert sig and outs and sig[0][0] * 5 <= outs[0] + 4          # the control chart alarms before, or in the same subgroup as, the first part out of tolerance

on_g, on_rule = online(x)
assert 30 <= outs[0] - on_g * 5 < 40                            # text: in real-time use, too, more than 30 parts before the first scrap part
clean = [i for i in range(len(R)) if i + 1 not in r_out]        # drop the subgroups in which a dressing happened
sig_w_clean = float(np.mean(R[clean]) / D2)

x2, _ = bearing_seat(100, dress_every=14)
xbar2, R2, xbb2, Rbar2, ucl2, lcl2, _, _ = chart(x2)
sig_w2, s_all2, cp2, ppk2, n_out2 = perf(x2, Rbar2)
assert n_out2 < n_out and ppk2 > ppk

out(on_g=on_g, on_part=on_g * 5, on_rule=on_rule, sig_w_clean_um=sig_w_clean * 1000, U=U, u_ratio=U / (SPEC_HI - SPEC_LO) * 100, n_guard=n_guard, rules=T("；", "; ").join(f"{g}:{r}" for g, r in sig), acc_lo=acc_lo, acc_hi=acc_hi, lo=SPEC_LO, hi=SPEC_HI, nominal=NOMINAL, xbb=xbb, Rbar_um=Rbar * 1000,
    ucl=ucl, lcl=lcl, r_ucl_um=r_ucl * 1000, sig_w_um=sig_w * 1000, s_all_um=s_all * 1000, cp=cp, ppk=ppk, n_out=n_out,
    first_sig=sig[0][0], first_rule=sig[0][1], n_sig=len(sig), sig_groups=T("、", ", ").join(str(g) for g, _ in sig),
    first_out=outs[0], outs=T("、", ", ").join(map(str, outs)), r_out=len(r_out),
    n_out2=n_out2, ppk2=ppk2, s_all2_um=s_all2 * 1000, A2=A2, D4=D4, D2=D2,
    _xbar=xbar.tolist(), _R=R.tolist(), _x=x.tolist(), _xbar2=xbar2.tolist(), _lim=[xbb, ucl, lcl])
