"""2.5 节：由旧函数得新函数——同一条五次多项式运动规律经平移、伸缩后用于不同的关节运动；
减速器与连杆的复合；NTC 热敏电阻的标定曲线及其反函数。"""
import math

import numpy as np

from bookout import out

p = lambda s: 10 * s**3 - 15 * s**4 + 6 * s**5            # [0, 1] → [0, 1] 的标准运动规律

# 算例 2.5.2：关节从 30° 转到 120°，t = 1 s 开始，历时 1.5 s
th0, D, t0, T = 30.0, 90.0, 1.0, 1.5
theta = lambda t: th0 + D * p(np.clip((t - t0) / T, 0, 1))
out(th_mid=float(theta(t0 + T / 2)), th_end=float(theta(t0 + T)), t_mid=t0 + T / 2)
# 平均角速度
out(w_avg=D / T)

# 复合：电机转角 φ（度）经减速比 N = 100 的减速器得关节角 θ = φ/N，连杆末端高度 y = l sin θ
N, l = 100, 0.392
y_of_phi = lambda phi: l * math.sin(math.radians(phi / N))
out(N=N, phi=3000, th_c=3000 / N, y_c=y_of_phi(3000) * 1000)

# 算例 2.5.4：NTC 热敏电阻 R(T) = R0 exp(B (1/T − 1/T0))，T 用开尔文；R0 = 10 kΩ（25 °C），B = 3950 K
R0, T0, B = 10e3, 298.15, 3950.0
R = lambda Tc: R0 * math.exp(B * (1 / (Tc + 273.15) - 1 / T0))
Tinv = lambda r: 1 / (1 / T0 + math.log(r / R0) / B) - 273.15
for Tc in (0, 25, 50, 80):
    out(**{f"R_{Tc}": R(Tc) / 1000})
out(T5k=Tinv(5e3), T20k=Tinv(20e3), K0=273.15)
# 反函数核对：T → R → T
assert all(abs(Tinv(R(Tc)) - Tc) < 1e-9 for Tc in np.linspace(-20, 120, 141))

# 摄氏与华氏
out(f_of_37=1.8 * 37 + 32)
