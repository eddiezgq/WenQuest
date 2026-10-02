"""18.6 节：伪逆与最小范数解。算例 18.6.1（接算例 18.2.1）；算例 18.6.2（不相容方程组）；Panda 的最小范数关节速度。"""
import math

import numpy as np

from _arm import panda, svd_fixed
from bookout import out, tex, vec

A = np.array([[3.0, 2.0, 2.0], [2.0, 3.0, -2.0]])
Ap = np.linalg.pinv(A)
b = np.array([5.0, 5.0])
x = Ap @ b
n = np.array([2.0, -2.0, -1.0]) / 3
ts = np.linspace(-2, 2, 401)
norms = [np.linalg.norm(x + t * n) for t in ts]
out(Ap=tex(Ap * 45, 0), Ap_dec=tex(Ap, 4), x=vec(x, 4), xnorm=np.linalg.norm(x), tmin=ts[int(np.argmin(norms))],
    other=vec(x + 1.5 * n, 4), other_norm=np.linalg.norm(x + 1.5 * n),
    full_row=np.abs(Ap - A.T @ np.linalg.inv(A @ A.T)).max(),
    P_row=tex(Ap @ A, 4), P_col=tex(A @ Ap, 4))
# 彭罗斯四个条件
out(pen1=np.abs(A @ Ap @ A - A).max(), pen2=np.abs(Ap @ A @ Ap - Ap).max(),
    pen3=np.abs((A @ Ap).T - A @ Ap).max(), pen4=np.abs((Ap @ A).T - Ap @ A).max())

# 算例 18.6.2：秩 1 的 3×2 矩阵，b 不在列空间中——既无解、最小二乘解也不唯一
C = np.array([[1.0, 2.0], [2.0, 4.0], [1.0, 2.0]])
d = np.array([1.0, 1.0, 2.0])
xc = np.linalg.pinv(C) @ d
Uc, sc, Vc = svd_fixed(C)
out(C=tex(C, 0), d=vec(d, 0), sc1=sc[0], sc1_sq=round(sc[0] ** 2), xc=vec(xc, 4), xc_frac=vec(xc * 30, 0),
    res=np.linalg.norm(C @ xc - d), Cxc=vec(C @ xc, 4), Cxc_frac=vec(C @ xc * 6, 0), vc1=vec(Vc[:, 0], 4), uc1=vec(Uc[:, 0], 4),
    xc_alt=vec(xc + np.array([2, -1]), 4), res_alt=np.linalg.norm(C @ (xc + np.array([2, -1])) - d))

# Panda：末端以 0.1 m/s 沿 x 方向平移、不转动
P = panda()
q = np.array([0, -math.pi / 4, 0, -3 * math.pi / 4, 0, math.pi / 2, math.pi / 4])
J = P.jacobian(q)
xi = np.array([0, 0, 0, 0.1, 0, 0])
qd = np.linalg.pinv(J) @ xi
z = svd_fixed(J)[2][:, 6]
qd2 = qd + 0.05 * z
out(qd=vec(qd, 4), qd_norm=np.linalg.norm(qd), qd2=vec(qd2, 4), qd2_norm=np.linalg.norm(qd2),
    tw1=np.abs(J @ qd - xi).max(), tw2=np.abs(J @ qd2 - xi).max(), qd_dot_z=abs(qd @ z),
    qd_deg=", ".join(f"{(math.degrees(v) if abs(math.degrees(v)) >= 5e-3 else 0.0):.2f}" for v in qd))
