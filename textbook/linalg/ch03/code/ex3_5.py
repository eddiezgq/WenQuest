"""3.5 节：解的三种情形；冗余的平面三连杆臂：给定末端速度，关节速度有无穷多组。"""
import math

import numpy as np

from bookout import out
from _elim import fstr, rref, tex_aug

# 三个例子：唯一解、无解、无穷多解
cases = {"uniq": [[1, 1, 1, 6], [1, 2, 3, 14], [2, 3, 5, 21]],
         "none": [[1, 1, 1, 6], [1, 2, 3, 14], [2, 3, 4, 21]],
         "many": [[1, 1, 1, 6], [1, 2, 3, 14], [2, 3, 4, 20]]}
for k, M in cases.items():
    R, piv = rref(M, 3)
    out(**{f"R_{k}": tex_aug(R), f"p_{k}": len(piv)})
# 平面三连杆臂：l = (0.425, 0.392, 0.1) m，关节角 (30°, 45°, −60°)。末端速度 = J θ̇，J 是 2×3
l = [0.425, 0.392, 0.1]
th = np.radians([30, 45, -60])
cum = np.cumsum(th)
J = np.array([[-sum(l[k] * math.sin(cum[k]) for k in range(i, 3)) for i in range(3)],
              [sum(l[k] * math.cos(cum[k]) for k in range(i, 3)) for i in range(3)]])
v = np.array([0.1, 0.0])                     # 要求末端以 0.1 m/s 沿 x 方向运动
R, piv = rref(np.round(np.c_[J, v], 6).tolist(), 3)
Rf = [[float(x) for x in r] for r in R]
out(J=" \\\\ ".join(" & ".join(f"{x:.4f}" for x in r) for r in J), Rrow1=f"{Rf[0][2]:.4f}", Rrow2=f"{Rf[1][2]:.4f}",
    rhs1=f"{Rf[0][3]:.4f}", rhs2=f"{Rf[1][3]:.4f}", piv3=", ".join(str(p + 1) for p in piv),
    t1=f"{Rf[0][3]:.4f} {'-' if Rf[0][2] > 0 else '+'} {abs(Rf[0][2]):.4f}", t2=f"{Rf[1][3]:.4f} {'-' if Rf[1][2] > 0 else '+'} {abs(Rf[1][2]):.4f}",
    nv=f"{-Rf[0][2]:.4f}\\\\ {-Rf[1][2]:.4f}\\\\ 1")
# 取 θ̇3 = 0 与 θ̇3 = 0.5 rad/s 两个解，都给出同样的末端速度
for name, t3 in (("a", 0.0), ("b", 0.5)):
    q = np.array([Rf[0][3] - Rf[0][2] * t3, Rf[1][3] - Rf[1][2] * t3, t3])
    out(**{f"q{name}": "(" + ", ".join(f"{x:.3f}" for x in q) + ")", f"v{name}": "(" + ", ".join(f"{round(x, 3) + 0.0:.3f}" for x in J @ q) + ")"})
