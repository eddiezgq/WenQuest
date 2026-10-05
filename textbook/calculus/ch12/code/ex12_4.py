"""12.4 节：定积分的性质——估值不等式：∫₀¹ e^{−x²} dx 介于 2/3 与 23/30 之间（真值约 0.7468）；积分中值定理：∫₀^π sin x dx = 2，
中值点 ξ = arcsin(2/π)；关节转角的上界 |θ(T) − θ(0)| ≤ ∫|ω| dt ≤ VT。"""
import math

from bookout import out

n = 200000
h = 1 / n
I = sum(math.exp(-((k + 0.5) * h) ** 2) for k in range(n)) * h
out(I_gauss=I, lo1=math.exp(-1))
mean = 2 / math.pi
out(sin_mean=mean, xi1=math.asin(mean), xi2=math.pi - math.asin(mean))
