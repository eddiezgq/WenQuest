"""Examples 39.4.1, 39.4.2: moving average and first-order low-pass filtering.

Signal: the gripper clamping force F(t), rising from 0 to 30 N within 0.2 s (smooth transition), with 50 Hz mains
interference of amplitude 2 N and white noise of standard deviation 0.3 N superimposed; sampling frequency 1 kHz.
39.4.1 20-point moving average: frequency response zero at 50 Hz (f_s/N = 50 Hz), group delay (N − 1)/2 sampling periods.
39.4.2 First-order low-pass y_k = y_{k−1} + α(x_k − y_{k−1}): relation between α and the cutoff frequency; residual
interference and response delay compared with the moving average.
"""
import math

import numpy as np

from bookout import out

fs = 1000.0
t = np.arange(0, 0.6, 1 / fs)
rng = np.random.default_rng(394)
clean = 30 * np.clip(t / 0.2, 0, 1) ** 2 * (3 - 2 * np.clip(t / 0.2, 0, 1))     # smooth step (smoothstep)
x = clean + 2 * np.sin(2 * math.pi * 50 * t) + rng.normal(0, 0.3, t.size)

# moving average
N = 20
ma = np.convolve(x, np.ones(N) / N, mode="full")[: t.size]


def H_ma(f):
    w = math.pi * f / fs
    return abs(math.sin(N * w) / (N * math.sin(w))) if f > 0 else 1.0


assert H_ma(50) < 1e-12
delay_ma = (N - 1) / 2 / fs

# first-order low-pass: cutoff frequency 10 Hz
fc = 10.0
alpha = 1 - math.exp(-2 * math.pi * fc / fs)
y = np.zeros_like(x)
for k in range(1, x.size):
    y[k] = y[k - 1] + alpha * (x[k] - y[k - 1])


def H_lp(f):
    z = complex(math.cos(2 * math.pi * f / fs), math.sin(2 * math.pi * f / fs))
    return abs(alpha / (1 - (1 - alpha) / z))


tau = -1 / fs / math.log(1 - alpha)            # time constant (discrete)
# residual ripple in the steady part (t > 0.35 s): standard deviation of the difference from the true value
ss = t > 0.35
res_raw = float((x - clean)[ss].std())
res_ma = float((ma - clean)[ss].std())
res_lp = float((y - clean)[ss].std())
# delay on the rise: how much later the filtered signal reaches 15 N than the true signal
t15 = float(t[np.argmax(clean >= 15)])
lag_ma = float(t[np.argmax(ma >= 15)]) - t15
lag_lp = float(t[np.argmax(y >= 15)]) - t15

out(N=N, fs=fs, zero_f=fs / N, delay_ma_ms=delay_ma * 1e3, H50_lp=H_lp(50), H10_lp=H_lp(10), alpha=alpha, fc=fc,
    tau_ms=tau * 1e3, res_raw=res_raw, res_ma=res_ma, res_lp=res_lp, lag_ma_ms=lag_ma * 1e3, lag_lp_ms=lag_lp * 1e3,
    H5_ma=H_ma(5), H25_ma=H_ma(25))
