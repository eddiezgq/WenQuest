"""4.3 节的算例。

算例 4.3.1：R = Rot(ẑ,30°) Rot(x̂,45°)（算例 4.2.3 中绕自身轴转动的结果）。按欧拉定理求它的转轴和转角：
转轴是特征值 1 的特征向量，转角由迹求出，tr R = 1 + 2 cos θ；再绕所得的轴转所得的角，应得到原来的 R。
"""
import math

import numpy as np

from _rot import is_rotation, rot_axis, rot_x, rot_z
from bookout import out, tex, vec

d = math.radians
R = rot_z(d(30)) @ rot_x(d(45))
assert is_rotation(R)

# 定理 4.3.1 的证明：det(R − I) = 0
det_RI = np.linalg.det(R - np.eye(3))
assert abs(det_RI) < 1e-12

# 转轴：特征值为 1 的特征向量
vals, vecs = np.linalg.eig(R)
k = int(np.argmin(abs(vals - 1)))
w = np.real(vecs[:, k])
w = w / np.linalg.norm(w)
assert np.allclose(R @ w, w)

# 转角：tr R = 1 + 2 cos θ，θ ∈ [0, π]
tr = float(np.trace(R))
theta = math.acos((tr - 1) / 2)
# 取轴的方向，使得按右手定则转过 θ（而不是 −θ）
if not np.allclose(rot_axis(w, theta), R):
    w = -w
assert np.allclose(rot_axis(w, theta), R)

# 另两个特征值是 e^{±iθ}
others = sorted((v for i, v in enumerate(vals) if i != k), key=lambda z: z.imag)
assert np.allclose(others[1], complex(math.cos(theta), math.sin(theta)))

# 轴上的点不动；与轴垂直的矢量转过 θ 后仍与轴垂直、长度不变
u = np.cross(w, [1.0, 0, 0])
u /= np.linalg.norm(u)
Ru = R @ u
assert abs(Ru @ w) < 1e-12 and abs(np.linalg.norm(Ru) - 1) < 1e-12
assert abs(math.acos(float(np.clip(u @ Ru, -1, 1))) - theta) < 1e-12

out(R=tex(R), w=vec(w), w1=w[0], w2=w[1], w3=w[2], tr=tr, cos_theta=(tr - 1) / 2,
    theta_deg=math.degrees(theta), theta_rad=theta, ev_re=others[1].real, ev_im=others[1].imag)
