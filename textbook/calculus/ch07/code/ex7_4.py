"""7.4 节：(a^h − 1)/h 的极限；正弦的差商；电机转速的一阶响应 ω = ω∞(1 − e^(−t/τ))。"""
import math

from bookout import out

vals = {}
for name, a in (("two", 2.0), ("e", math.e), ("three", 3.0)):
    for k, h in enumerate((0.1, 0.01, 0.001, 1e-6), 1):
        vals[f"{name}{k}"] = (a**h - 1) / h
out(**vals, ln2=math.log(2), ln3=math.log(3))

# 差商 (sin(1 + h) − sin 1)/h 与 cos 1
out(sinq1=(math.sin(1.1) - math.sin(1)) / 0.1, sinq3=(math.sin(1.001) - math.sin(1)) / 0.001, cos1=math.cos(1))

# 算例 7.4.2：空载电机通电后的转速 ω(t) = ω∞(1 − e^(−t/τ))，ω∞ = 300 rad/s，τ = 0.05 s
w_inf, tau = 300.0, 0.05
out(alpha0=w_inf / tau, frac_tau=1 - math.exp(-1), frac_3tau=1 - math.exp(-3), w_tau=w_inf * (1 - math.exp(-1)),
    alpha_tau=w_inf / tau * math.exp(-1), rpm_inf=w_inf * 60 / (2 * math.pi))

# 7.4.9 节：摩天轮 H(t) = 30 − 25 cos(2πt/20)，高度变化率的最大值（m/min）
out(ferris=25 * 2 * math.pi / 20)
