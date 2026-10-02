"""算例 9.1.1～9.1.3：编码器的量化误差、夹爪测力传感器的读数统计、多次读数取平均；贝塞尔公式与中心极限定理。

9.1.2 测力传感器承受 15 N 的恒定夹紧力，以 1 kHz 采样 2 s，共 2000 个读数，噪声为高斯分布、标准差 0.08 N
      （固定种子生成）。求样本均值、样本标准差，并数出落在 ±1、±2、±3 个标准差内的比例，与高斯分布的理论值比较。
9.1.1 每转 4096 个计数的编码器，量化误差在 ±q/2 内均匀分布：标准差 q/√12（式 (9.1.11)），用蒙特卡洛核对。
9.1.3 每 16 个读数取一次平均：平均值的标准差为 σ/4（定理 9.1.4），用蒙特卡洛核对。
定理 9.1.5：每组 5 个读数，样本方差除以 n − 1 是无偏的，除以 n 偏小，用蒙特卡洛核对。
另：12 个均匀随机数之和（中心极限定理），落在均值 ±1 个标准差内的比例接近高斯分布的值。
"""
import math

import numpy as np

from _prob import p_within
from bookout import out

rng = np.random.default_rng(901)

# ---------------------------------------------------------------- 算例 9.1.2
F0, sig, n = 15.0, 0.08, 2000
x = F0 + sig * rng.standard_normal(n)
mean = x.mean()
s = x.std(ddof=1)
frac = [np.mean(np.abs(x - mean) < k * s) for k in (1, 2, 3)]
theory = [p_within(k) for k in (1, 2, 3)]
assert abs(mean - F0) < 4 * sig / math.sqrt(n)                     # 均值落在理论范围内
assert abs(s - sig) / sig < 0.05
assert all(abs(f - t) < 0.02 for f, t in zip(frac, theory))
# 两种算法一致：逐项定义与 E[X²] − (E[X])² 形式
var_def = np.sum((x - mean) ** 2) / (n - 1)
var_alt = (np.sum(x ** 2) - n * mean ** 2) / (n - 1)
assert abs(var_def - var_alt) < 1e-9

# 高斯分布 ±1、±2、±3 σ 的概率，两种算法：误差函数与数值积分
zz = np.linspace(-3, 3, 600001)
dens = np.exp(-zz ** 2 / 2) / math.sqrt(2 * math.pi)
for k in (1, 2, 3):
    m = np.abs(zz) <= k
    assert abs(np.trapezoid(dens[m], zz[m]) - p_within(k)) < 1e-6
k95 = 1.959963984540054                                          # Pr(|Z| < k) = 0.95 的 k
assert abs(p_within(k95) - 0.95) < 1e-12
# 高斯积分 ∫ e^{−x²/2} dx = √(2π)：数值积分核对
xx = np.linspace(-12, 12, 400001)
gint = np.trapezoid(np.exp(-xx ** 2 / 2), xx)
assert abs(gint - math.sqrt(2 * math.pi)) < 1e-9

# ---------------------------------------------------------------- 算例 9.1.1 编码器量化
counts = 4096
q_deg = 360.0 / counts
sig_q = q_deg / math.sqrt(12)
ang = rng.uniform(0, 360, 200000)
err = np.round(ang / q_deg) * q_deg - ang
sig_q_mc = err.std()
assert np.all(np.abs(err) <= q_deg / 2 + 1e-12)
assert abs(sig_q_mc - sig_q) / sig_q < 0.01

# ---------------------------------------------------------------- 算例 9.1.3 平均 16 个读数
N16 = 16
groups = F0 + sig * rng.standard_normal((20000, N16))
avg = groups.mean(axis=1)
sig_avg = sig / math.sqrt(N16)
sig_avg_mc = avg.std(ddof=1)
assert abs(sig_avg_mc - sig_avg) / sig_avg < 0.02

# ---------------------------------------------------------------- 定理 9.1.5 贝塞尔公式
n5 = 5
g5 = sig * rng.standard_normal((200000, n5))
s2_unb = g5.var(axis=1, ddof=1).mean()
s2_b = g5.var(axis=1, ddof=0).mean()
assert abs(s2_unb / sig ** 2 - 1) < 0.01
assert abs(s2_b / sig ** 2 - (n5 - 1) / n5) < 0.01

# ---------------------------------------------------------------- 中心极限定理：12 个均匀随机数之和
u12 = rng.uniform(0, 1, (200000, 12)).sum(axis=1) - 6.0
clt_var = u12.var()
clt_p1 = np.mean(np.abs(u12) < 1)
assert abs(clt_var - 1) < 0.01 and abs(clt_p1 - p_within(1)) < 0.01

# 掷骰子：期望与方差（离散随机变量）
die = np.arange(1, 7)
die_mean = die.mean()
die_var = np.mean((die - die_mean) ** 2)
assert abs(die_var - 35 / 12) < 1e-12

out(F0=F0, sig=sig, n=n, mean=mean, s=s,
    f1=100 * frac[0], f2=100 * frac[1], f3=100 * frac[2],
    p1=100 * theory[0], p2=100 * theory[1], p3=100 * theory[2], k95=k95,
    out3=int(np.sum(np.abs(x - mean) >= 3 * s)), exp_out3=n * (1 - theory[2]),
    q_deg=q_deg, q_mrad=1000 * math.radians(q_deg), sig_q=sig_q, sig_q_mc=sig_q_mc, sig_q_mrad=1000 * math.radians(sig_q),
    N16=N16, sig_avg=sig_avg, sig_avg_mc=sig_avg_mc,
    s2_unb=s2_unb / sig ** 2, s2_b=s2_b / sig ** 2,
    clt_var=clt_var, clt_p1=100 * clt_p1,
    die_var=die_var, sqrt2pi=math.sqrt(2 * math.pi), gint=gint)
