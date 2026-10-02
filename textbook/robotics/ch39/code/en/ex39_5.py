"""Example 39.5.1: calibration of the force-sensor measurement chain (loading 0→100 N→0, steps of 20 N, repeated 3 times).

Sensor model (true characteristic of the chain, unknown before calibration): output V = G·(V0 + S·F + n(F) + h(F)), where
zero V0 = 0.03 mV (bridge imbalance), sensitivity S = 0.1 mV/N (2 mV/V × 5 V / 100 N), nonlinearity n(F) = −0.04%·FS·4(F/FS)(1 − F/FS),
hysteresis h: unloading reads 0.06%·FS·sin(πF/FS) higher than loading, reading noise 0.2 mV (after amplification; each reading
is the mean of 100 ADC samples, so it can resolve finer than 1 LSB).
The parameters are chosen so that "hysteresis is the largest" does not depend on the random seed (checked with 1000 seeds).
A least-squares line is fitted to all loading and unloading data to find zero, sensitivity, linearity, hysteresis and repeatability (%FS).
"""
import math

import numpy as np

from _meas import F_FS, GAIN
from bookout import out

rng = np.random.default_rng(395)
S = 0.1e-3                                      # V/N (before amplification)
V0 = 0.03e-3
FS_V = S * F_FS


def chain(F, unloading):
    n = -0.0004 * FS_V * 4 * (F / F_FS) * (1 - F / F_FS)
    h = 0.0006 * FS_V * math.sin(math.pi * F / F_FS) if unloading else 0.0
    return GAIN * (V0 + S * F + n + h) + rng.normal(0, 0.2e-3)


loads = np.arange(0, F_FS + 1, 20.0)
up, down = [], []
for _ in range(3):
    up.append([chain(F, False) for F in loads])
    down.append([chain(F, True) for F in loads[::-1]][::-1])
up, down = np.array(up), np.array(down)
Fx = np.r_[np.tile(loads, 3), np.tile(loads, 3)]
Vy = np.r_[up.ravel(), down.ravel()]
b, a = np.polyfit(Fx, Vy, 1)                     # V = a + b·F
fit = a + b * loads
y_fs = b * F_FS                                  # full-scale output (fitted)
lin = float(np.max(np.abs(np.r_[up.mean(0), down.mean(0)] - np.r_[fit, fit])) / y_fs * 100)
hyst = float(np.max(np.abs(down.mean(0) - up.mean(0))) / y_fs * 100)
rep = float(np.max(np.r_[up.std(0, ddof=1), down.std(0, ddof=1)]) * 2 / y_fs * 100)   # 2 standard deviations
assert hyst > lin and hyst > rep                # text: hysteresis is the largest of the three indices
# force back-calculated from the fit: F = (V − a)/b
F_back = (up.mean(0) - a) / b

def f1(v):
    t = f"{v:.1f}"
    return "0.0" if t == "-0.0" else t


rows = r" \\ ".join(f"{F:.0f} & {f1(u * 1e3)} & {f1(d * 1e3)} & {f1((d - u) * 1e3)}" for F, u, d in zip(loads, up.mean(0), down.mean(0)))
out(a_mV=a * 1e3, b_mV=b * 1e3, y_fs=y_fs, lin=lin, hyst=hyst, rep=rep, rows=rows, gain=GAIN,
    S_true_mV=S * GAIN * 1e3, zero_true_mV=V0 * GAIN * 1e3, F_err_max=float(np.max(np.abs(F_back - loads))),
    _loads=loads.tolist(), _up=up.mean(0).tolist(), _down=down.mean(0).tolist(), _fit=[a, b])
