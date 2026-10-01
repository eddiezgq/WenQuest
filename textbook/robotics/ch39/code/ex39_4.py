"""算例 39.4.1、39.4.2：滑动平均与一阶低通滤波。

信号：夹爪夹紧时的力 F(t)，0.2 s 内从 0 升到 30 N（平滑过渡），叠加 50 Hz、幅值 2 N 的工频干扰和标准差 0.3 N 的白噪声；
采样频率 1 kHz。
39.4.1 N = 20 点滑动平均：频率响应在 50 Hz 处为零（f_s/N = 50 Hz），群延迟 (N − 1)/2 个采样周期。
39.4.2 一阶低通 y_k = y_{k−1} + α(x_k − y_{k−1})：α 与截止频率的关系；与滑动平均比较残余干扰和响应延迟。
"""
import math

import numpy as np

from bookout import out

fs = 1000.0
t = np.arange(0, 0.6, 1 / fs)
rng = np.random.default_rng(394)
clean = 30 * np.clip(t / 0.2, 0, 1) ** 2 * (3 - 2 * np.clip(t / 0.2, 0, 1))     # 平滑阶跃（smoothstep）
x = clean + 2 * np.sin(2 * math.pi * 50 * t) + rng.normal(0, 0.3, t.size)

# 滑动平均
N = 20
ma = np.convolve(x, np.ones(N) / N, mode="full")[: t.size]


def H_ma(f):
    w = math.pi * f / fs
    return abs(math.sin(N * w) / (N * math.sin(w))) if f > 0 else 1.0


assert H_ma(50) < 1e-12
delay_ma = (N - 1) / 2 / fs

# 一阶低通：取截止频率 10 Hz
fc = 10.0
alpha = 1 - math.exp(-2 * math.pi * fc / fs)
y = np.zeros_like(x)
for k in range(1, x.size):
    y[k] = y[k - 1] + alpha * (x[k] - y[k - 1])


def H_lp(f):
    z = complex(math.cos(2 * math.pi * f / fs), math.sin(2 * math.pi * f / fs))
    return abs(alpha / (1 - (1 - alpha) / z))


tau = -1 / fs / math.log(1 - alpha)            # 时间常数（离散）
# 稳态段（t > 0.35 s）残余波动：与真实值之差的标准差
ss = t > 0.35
res_raw = float((x - clean)[ss].std())
res_ma = float((ma - clean)[ss].std())
res_lp = float((y - clean)[ss].std())
# 上升段延迟：滤波后达到 15 N 比原信号晚多少
t15 = float(t[np.argmax(clean >= 15)])
lag_ma = float(t[np.argmax(ma >= 15)]) - t15
lag_lp = float(t[np.argmax(y >= 15)]) - t15

out(N=N, fs=fs, zero_f=fs / N, delay_ma_ms=delay_ma * 1e3, H50_lp=H_lp(50), H10_lp=H_lp(10), alpha=alpha, fc=fc,
    tau_ms=tau * 1e3, res_raw=res_raw, res_ma=res_ma, res_lp=res_lp, lag_ma_ms=lag_ma * 1e3, lag_lp_ms=lag_lp * 1e3,
    H5_ma=H_ma(5), H25_ma=H_ma(25))
