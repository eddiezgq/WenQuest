"""10.2 节：线性代数基本定理（二）。8.1 节的 A：行空间 ⊥ 零空间，列空间 ⊥ 左零空间，且互为正交补。
x 正交分解为 x_r + x_n，Ax = Ax_r，‖x‖² = ‖x_r‖² + ‖x_n‖²；Ax = b 的全部解中，行空间里的那个（x_r）范数最小。
三连杆平面臂：最小范数的关节速度与自运动方向正交。"""
import numpy as np
import scipy.linalg as sla

from _a import A
from _elim import tex_frac
from _num import sci
from _frac import fr, fvec
from bookout import out, vec

Qr = sla.orth(A.T)                     # 行空间的标准正交基（4×2）
Qn = sla.null_space(A)                 # 零空间的标准正交基（4×2）
Qc, Ql = sla.orth(A), sla.null_space(A.T)
out(rn=sci(float(np.abs(Qr.T @ Qn).max()) + 1e-17, 0), cl=sci(float(np.abs(Qc.T @ Ql).max()) + 1e-17, 0), dims=f"{Qr.shape[1]} + {Qn.shape[1]} = 4，{Qc.shape[1]} + {Ql.shape[1]} = 3")
x = np.array([4.0, 1, 0, 2])
xr = Qr @ (Qr.T @ x)
xn = x - xr
out(x=vec(x, 0), xr=fvec(xr), xn=fvec(xn), Ax=vec(A @ x, 0), Axr=vec(A @ xr, 4), nr_f=tex_frac(fr(xr @ xr)), nn_f=tex_frac(fr(xn @ xn)), dot=round(float(xr @ xn), 10) + 0.0,
    nx=float(x @ x), nr=float(xr @ xr), nn=float(xn @ xn))
# b = (1, 3, 4)：特解 (1, 0, 1, 0) 与最小范数解
b = np.array([1.0, 3, 4])
xp = np.array([1.0, 0, 1, 0])
xmin = np.linalg.pinv(A) @ b
out(xmin=fvec(xmin), nmin=float(np.linalg.norm(xmin)), np_=float(np.linalg.norm(xp)), rowcheck=float(np.abs(Qn.T @ xmin).max()),
    xmin_from_p=fvec(Qr @ (Qr.T @ xp)))
# 左零空间与相容条件
y = np.array([1.0, 1, -1])
out(yA=vec(y @ A, 0), yb=float(y @ b), yb2=float(y @ np.array([1.0, 3, 5])))
# 三连杆臂（8.3 节）：最小范数解 qp 在 J 的行空间里，与零空间方向 n 正交
L = 0.3
th = np.radians([30, 45, -60])
c = np.cumsum(th)
J = np.array([[-L * np.sin(c[i:]).sum() for i in range(3)], [L * np.cos(c[i:]).sum() for i in range(3)]])
nvec = sla.null_space(J)[:, 0]
qp = np.linalg.pinv(J) @ np.array([0.1, 0.0])
q2 = qp + 0.5 * nvec / np.abs(nvec).max()
out(qp=vec(qp, 4), qn=sci(abs(float(qp @ nvec)) + 1e-17, 0), nqp=float(np.linalg.norm(qp)), nq2=float(np.linalg.norm(q2)))
