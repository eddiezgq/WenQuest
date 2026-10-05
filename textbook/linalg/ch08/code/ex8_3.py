"""8.3 节：Ax = b 的完整解——相容条件 b₃ = b₁ + b₂；特解（自由变量取 0）加零空间；
三连杆平面臂（只看末端位置，2×3 雅可比矩阵）的全部关节速度：特解 + 自运动。"""
import math

import numpy as np
import scipy.linalg as sla

from _a import A
from _elim import rref
from bookout import out, tex, vec

b = np.array([1.0, 3, 4])
aug = np.column_stack([A, b])
R, piv = rref(aug.tolist(), 4)
xp = np.zeros(4)
for i, p in enumerate(piv):
    xp[p] = float(R[i][4])
out(xp=vec(xp, 0), Axp=vec(A @ xp, 0))
# 三连杆平面臂：每节 0.3 m，θ = (30°, 45°, −60°)
L = [0.3, 0.3, 0.3]
th = np.radians([30.0, 45.0, -60.0])
c = np.cumsum(th)
J = np.array([[-sum(L[k] * math.sin(c[k]) for k in range(i, 3)) for i in range(3)],
              [sum(L[k] * math.cos(c[k]) for k in range(i, 3)) for i in range(3)]])
v = np.array([0.1, 0.0])
qp = np.linalg.lstsq(J, v, rcond=None)[0]      # 最小范数的特解（第 18 章）
n = sla.null_space(J)[:, 0]
n = n / n[np.argmax(np.abs(n))]
out(J=tex(J, 4), qp=vec(qp, 4), n=vec(n, 4), Jn=float(np.abs(J @ n).max()),
    q2=vec(qp + 0.5 * n, 4), Jq2=vec(J @ (qp + 0.5 * n), 4))
