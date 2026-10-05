"""9.7 节：对偶空间与对偶映射。基 b1 = (1, 0, 0)、b2 = (1, 1, 0)、b3 = (1, 1, 1) 的对偶基是 B⁻¹ 的各行；线性映射 A 的对偶映射在对偶基下是 Aᵀ。
力学中的对偶：雅可比 J 把关节速度映成末端速度，它的对偶 Jᵀ 把末端的力映成关节力矩（τ = Jᵀ F），功率 F·(Jθ̇) = τ·θ̇。"""
import numpy as np

from _arm import panda, planar2
from bookout import out, tex, vec

B = np.array([[1.0, 1, 1], [0, 1, 1], [0, 0, 1]])
Bd = np.linalg.inv(B)
out(B=tex(B, 0), Bd=tex(Bd, 0), delta=tex(Bd @ B, 0))
x = np.array([3.0, -2.0, 5.0])
out(x=vec(x, 0), cx=vec(Bd @ x, 0))
# 两连杆平面臂：l1 = 0.4 m，l2 = 0.3 m，θ = (30°, 45°)；末端托住 2 kg 的工件，受力 F = (0, −19.62) N
l1, l2 = 0.4, 0.3
t1, t2 = np.radians(30), np.radians(45)
J = np.array([[-l1 * np.sin(t1) - l2 * np.sin(t1 + t2), -l2 * np.sin(t1 + t2)],
              [l1 * np.cos(t1) + l2 * np.cos(t1 + t2), l2 * np.cos(t1 + t2)]])
F = np.array([0.0, -2 * 9.81])
tau = J.T @ F
out(J2=tex(J, 4), F=vec(F, 2), tau2=vec(tau, 3))
qd = np.array([0.3, -0.5])
out(pow_tool=float(F @ (J @ qd)), pow_joint=float(tau @ qd))
# 力矩由几何直接验证：关节 1 承受工件重力对它的力矩 = −m g × 水平距离
xt = l1 * np.cos(t1) + l2 * np.cos(t1 + t2)
out(xt=xt, tau1_geom=float(-2 * 9.81 * xt), x2=l2 * np.cos(t1 + t2), tau2_geom=float(-2 * 9.81 * l2 * np.cos(t1 + t2)))
# Panda：准备姿态，末端受 20 N 向下的力；J 按 (角速度, 线速度) 排列，对偶的“力旋量”按 (力矩, 力) 排列
arm = panda()
q = np.array([0.0, -np.pi / 4, 0, -3 * np.pi / 4, 0, np.pi / 2, np.pi / 4])
Jp = arm.jacobian(q)
w = np.array([0, 0, 0, 0, 0, -20.0])
taup = Jp.T @ w
rng = np.random.default_rng(7)
qdp = rng.normal(size=7) * 0.2
out(taup=vec(taup, 2), powp=float(w @ (Jp @ qdp)), powq=float(taup @ qdp))
