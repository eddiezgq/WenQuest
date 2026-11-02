"""21.2 节：相平面与轨线。单摆（l = 0.5 m）的能量等值线与分界线：从最低点出发越过最高点所需的最小角速度；
略低于/略高于分界线的两条轨线（数值解）；有阻尼时轨线螺旋地趋于原点。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import out

g, l = 9.81, 0.5
w_sep = 2 * math.sqrt(g / l)
out(pd_l=l, pd_wsep=w_sep)
f = lambda t, y, c=0.0: [y[1], -g / l * math.sin(y[0]) - c * y[1]]
for fac, key in ((0.99, "lo"), (1.01, "hi")):
    s = solve_ivp(f, (0, 6), [0.0, fac * w_sep], rtol=1e-10, atol=1e-12, max_step=0.01)
    out(**{f"pd_{key}_thmax": float(np.degrees(np.max(np.abs(s.y[0])))), f"pd_{key}_thend": float(np.degrees(s.y[0, -1]))})
# 有阻尼 c = 0.5 /s：从 θ = 0、ω = 1.2 ω_sep 出发，转过几圈后停在哪个平衡点
s = solve_ivp(lambda t, y: f(t, y, 0.5), (0, 30), [0.0, 1.2 * w_sep], rtol=1e-10, atol=1e-12, max_step=0.01)
out(pd_damp_turns=float(s.y[0, -1] / (2 * math.pi)), pd_damp_end_deg=float(np.degrees(s.y[0, -1])))
# 能量（每单位 m l²）：E = ω²/2 − (g/l) cos θ，在分界线上 E = g/l
E = lambda th, w: w * w / 2 - g / l * math.cos(th)
out(pd_Esep=g / l, pd_E_check=E(math.pi, 0.0))
