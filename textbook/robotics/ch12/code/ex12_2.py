"""算例 12.2.1、12.2.2：平面 3R 臂的空间形式与物体形式。

θ = (30°, 45°, −90°)。逐个乘上指数，记录每一步末端的位置；与几何解法
x = L1 cos θ1 + L2 cos(θ1+θ2) + L3 cos(θ1+θ2+θ3)（y 同理）比较；
再用 B_i = [Ad_{M⁻¹}] S_i 得物体形式，两种形式结果相同。
"""
import numpy as np

from _poe import adjoint, clean, exp6, fk_body, fk_space, inv, screw_revolute
from bookout import out, tex, vec

L1, L2, L3 = 0.425, 0.392, 0.1
z = np.array([0, 0, 1.0])
S = [screw_revolute(z, q) for q in ([0, 0, 0], [L1, 0, 0], [L1 + L2, 0, 0])]
M = np.eye(4)
M[0, 3] = L1 + L2 + L3
deg = np.array([30.0, 45.0, -90.0])
th = np.radians(deg)

# 空间形式：从最后一个关节往前乘
step3 = exp6(S[2], th[2]) @ M
step2 = exp6(S[1], th[1]) @ step3
step1 = exp6(S[0], th[0]) @ step2
T = fk_space(S, M, th)
assert np.allclose(T, step1)

# 几何解法
a1, a12, a123 = th[0], th[0] + th[1], th.sum()
geo = np.array([L1 * np.cos(a1) + L2 * np.cos(a12) + L3 * np.cos(a123), L1 * np.sin(a1) + L2 * np.sin(a12) + L3 * np.sin(a123)])
assert np.allclose(T[:2, 3], geo, atol=1e-12)
assert np.isclose(np.arctan2(T[1, 0], T[0, 0]), a123)

# 物体形式
B = [adjoint(inv(M)) @ s for s in S]
Tb = fk_body(B, M, th)
assert np.allclose(Tb, T, atol=1e-12)

# 反过来按“从第一个关节往后乘”的错误次序（为 12.4 节准备）
wrong = exp6(S[2], th[2]) @ exp6(S[1], th[1]) @ exp6(S[0], th[0]) @ M

out(T=tex(clean(T), 4), x=T[0, 3], y=T[1, 3], phi=np.degrees(a123), c15=T[0, 0],
    p3=vec(clean(step3[:3, 3])[:2], 4), p2=vec(clean(step2[:3, 3])[:2], 4), p1=vec(clean(step1[:3, 3])[:2], 4),
    B1=vec(clean(B[0]), 3), B2=vec(clean(B[1]), 3), B3=vec(clean(B[2]), 3),
    wx=wrong[0, 3], wy=wrong[1, 3], wdist=float(np.linalg.norm(wrong[:3, 3] - T[:3, 3])),
    wnorm=float(np.linalg.norm(wrong[:3, 3])), reach=L1 + L2 + L3)
