"""2.1 节的算例：平面 2R 臂的雅可比矩阵、矩阵乘法、逆矩阵、行列式与迹。

算例 2.1.1：θ = (30°, 60°)，关节速度 θ̇ = (0.5, −1.0) rad/s，求末端速度；按“列的线性组合”和“行与向量的点积”两种看法各算一次。
算例 2.1.2：平行四边形连杆驱动，θ̇ = C φ̇；求 J C，并验证 J C ≠ C J。
算例 2.1.3：要末端以 0.1 m/s 沿 x 方向运动，求关节速度（2×2 逆矩阵公式与通用解法核对）。
另外核对：det J = L1 L2 sin θ2；det(AB) = det A det B；tr(AB) = tr(BA)（含非方阵）；tr(ABC) 与 tr(ACB) 一般不等；
‖A‖_F² = tr(AᵀA)；3×3 行列式按第一行展开。
"""
import math

import numpy as np

from _la import L2R, arm_points, d, jac, jac_formula_2r
from bookout import out, tex, vec

L1, L2 = L2R
th = np.array([d(30), d(60)])
pts = arm_points(th, L2R)
elbow, tip = pts[1], pts[2]
J = jac(th, L2R)
assert np.allclose(J, jac_formula_2r(th))                       # 几何作图与式 (2.1.9) 一致

# ---------------------------------------------------------------- 算例 2.1.1
thd = np.array([0.5, -1.0])                                      # rad/s
v_cols = thd[0] * J[:, 0] + thd[1] * J[:, 1]                     # 列的线性组合
v_rows = np.array([J[0] @ thd, J[1] @ thd])                      # 行与向量的点积
assert np.allclose(v_cols, v_rows) and np.allclose(v_cols, J @ thd)
speed = float(np.linalg.norm(v_cols))
j1, j2 = J[:, 0], J[:, 1]
cos12 = float(j1 @ j2 / (np.linalg.norm(j1) * np.linalg.norm(j2)))
assert abs(cos12) <= 1                                           # 柯西-施瓦茨不等式

# ---------------------------------------------------------------- 算例 2.1.2
Cm = np.array([[1.0, 0.0], [-1.0, 1.0]])                          # θ = C φ：θ1 = φ1，θ2 = φ2 − φ1
phid = np.array([0.5, -0.5])                                     # 两个电机侧的绝对角速度，rad/s
assert np.allclose(Cm @ phid, thd)
JC, CJ = J @ Cm, Cm @ J
assert np.allclose(JC @ phid, J @ (Cm @ phid))                   # 结合律
assert not np.allclose(JC, CJ)                                   # 不可交换
assert np.allclose(JC.T, Cm.T @ J.T)                             # (AB)ᵀ = BᵀAᵀ

# ---------------------------------------------------------------- 算例 2.1.3
detJ = float(J[0, 0] * J[1, 1] - J[0, 1] * J[1, 0])
assert abs(detJ - L1 * L2 * math.sin(th[1])) < 1e-12              # det J = L1 L2 sin θ2
assert abs(detJ - np.linalg.det(J)) < 1e-12
Jinv = np.array([[J[1, 1], -J[0, 1]], [-J[1, 0], J[0, 0]]]) / detJ   # 2×2 逆矩阵公式
assert np.allclose(Jinv, np.linalg.inv(J)) and np.allclose(J @ Jinv, np.eye(2))
v_des = np.array([0.0, 0.1])
thd_need = Jinv @ v_des
assert np.allclose(J @ thd_need, v_des) and np.allclose(thd_need, np.linalg.solve(J, v_des))
assert np.allclose(np.linalg.inv(J @ Cm), np.linalg.inv(Cm) @ Jinv)  # (AB)⁻¹ = B⁻¹A⁻¹

# ---------------------------------------------------------------- 行列式
detC = float(np.linalg.det(Cm))
assert abs(np.linalg.det(JC) - detJ * detC) < 1e-12              # det(AB) = det A det B
assert abs(np.linalg.det(J.T) - detJ) < 1e-12                    # det Aᵀ = det A
A3 = np.array([[2.0, 1.0, 0.0], [1.0, 3.0, 1.0], [0.0, 1.0, 4.0]])
cof = [A3[0, 0] * (A3[1, 1] * A3[2, 2] - A3[1, 2] * A3[2, 1]),
       -A3[0, 1] * (A3[1, 0] * A3[2, 2] - A3[1, 2] * A3[2, 0]),
       A3[0, 2] * (A3[1, 0] * A3[2, 1] - A3[1, 1] * A3[2, 0])]
det3 = sum(cof)
assert abs(det3 - np.linalg.det(A3)) < 1e-12
# 按第二列展开，结果相同
col2 = (-A3[0, 1] * (A3[1, 0] * A3[2, 2] - A3[1, 2] * A3[2, 0]) + A3[1, 1] * (A3[0, 0] * A3[2, 2] - A3[0, 2] * A3[2, 0])
        - A3[2, 1] * (A3[0, 0] * A3[1, 2] - A3[0, 2] * A3[1, 0]))
assert abs(col2 - det3) < 1e-12
# 伸直与折叠时 det J = 0
for t2 in (0.0, math.pi):
    assert abs(np.linalg.det(jac([d(30), t2], L2R))) < 1e-12

# ---------------------------------------------------------------- 迹
trJC, trCJ = float(np.trace(JC)), float(np.trace(CJ))
assert abs(trJC - trCJ) < 1e-12
A = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 3.0]])                  # 2×3
B = np.array([[2.0, 1.0], [0.0, 1.0], [1.0, 0.0]])                # 3×2
trAB, trBA = float(np.trace(A @ B)), float(np.trace(B @ A))
assert trAB == trBA and (A @ B).shape == (2, 2) and (B @ A).shape == (3, 3)
P = np.array([[1.0, 1.0], [0.0, 1.0]])
Q = np.array([[1.0, 0.0], [1.0, 1.0]])
S = np.array([[1.0, 0.0], [0.0, 0.0]])
trPQS, trSPQ, trPSQ = (float(np.trace(P @ Q @ S)), float(np.trace(S @ P @ Q)), float(np.trace(P @ S @ Q)))
assert trPQS == trSPQ and trPQS != trPSQ                         # 轮换可以，任意对换不行
froJ = float(np.linalg.norm(J, "fro"))
assert abs(froJ ** 2 - np.trace(J.T @ J)) < 1e-12

out(
    elbow=vec(elbow, 4), tip=vec(tip, 4), tip_x=tip[0], tip_y=tip[1], e_x=elbow[0], e_y=elbow[1],
    J=tex(J, 4), j1=vec(j1, 4), j2=vec(j2, 4),
    v=vec(v_cols, 5), vx=v_cols[0], vy=v_cols[1], speed=speed, cos12=cos12, ang12=math.degrees(math.acos(cos12)),
    t1x=thd[0] * j1[0], t1y=thd[0] * j1[1], t2x=thd[1] * j2[0], t2y=thd[1] * j2[1],
    JC=tex(JC, 4), CJ=tex(CJ, 4),
    detJ=detJ, sin60=math.sin(th[1]), L1L2=L1 * L2, Jinv=tex(Jinv, 4), thd_need=vec(thd_need, 4),
    thd1_need=thd_need[0], thd2_need=thd_need[1],
    detC=detC, det3=det3, cof1=cof[0], cof2=cof[1], cof3=cof[2],
    trJ=float(np.trace(J)), trJC=trJC, trCJ=trCJ, trAB=trAB, trBA=trBA, AB=tex(A @ B, 0), BA=tex(B @ A, 0),
    trPQS=trPQS, trPSQ=trPSQ, froJ=froJ, froJ2=froJ ** 2,
)
