"""4.2 节的算例。

算例 4.2.1：工具坐标系 {b} 相对 {s} 的姿态为 Rot(ẑ, 30°)，工具上一点在 {b} 中的分量为 (0.1, 0, 0.05) m，求它在 {s} 中的分量。
算例 4.2.2：同样两个 90° 转动，先后次序不同，结果不同（书本实验）。
算例 4.2.3：绕固定轴 x̂_s 转 45° 与绕自身轴 x̂_b 转 45°，结果不同。
"""
import math

import numpy as np

from bookout import out, tex, vec


from _rot import is_rotation, rot_x, rot_z  # noqa: E402

d = math.radians

# 算例 4.2.1
R_sb = rot_z(d(30))
p_b = np.array([0.1, 0.0, 0.05])
p_s = R_sb @ p_b
assert is_rotation(R_sb)
assert abs(np.linalg.norm(p_s) - np.linalg.norm(p_b)) < 1e-12

# 算例 4.2.2：书本先绕 x 转 90° 再绕 z 转 90°（绕固定轴，左乘），与相反次序比较
A = rot_z(d(90)) @ rot_x(d(90))
B = rot_x(d(90)) @ rot_z(d(90))
assert is_rotation(A) and is_rotation(B) and not np.allclose(A, B)
# 书脊方向 ŷ（书本自身的 y 轴）最终指向哪里
spine_A, spine_B = A @ np.array([0, 1, 0]), B @ np.array([0, 1, 0])

# 算例 4.2.3：在 R_sb = Rot(z,30°) 的基础上，分别绕固定轴 x̂_s、绕自身轴 x̂_b 转 45°
R_fixed = rot_x(d(45)) @ R_sb      # 左乘
R_body = R_sb @ rot_x(d(45))       # 右乘
assert is_rotation(R_fixed) and is_rotation(R_body) and not np.allclose(R_fixed, R_body)
# 绕自身轴转动：x̂_b 不变；绕固定轴转动：x̂_s 方向上的分量不变
assert np.allclose(R_body[:, 0], R_sb[:, 0])
assert np.allclose(R_fixed[0, :], R_sb[0, :])

out(
    Rsb=tex(R_sb), p_s=tex(p_s), p_s_x=p_s[0], p_s_y=p_s[1], c30=math.cos(d(30)), norm_p=float(np.linalg.norm(p_b)),
    Rx90=tex(rot_x(d(90))), Rz90=tex(rot_z(d(90))), A=tex(A), B=tex(B), spine_A=vec(spine_A), spine_B=vec(spine_B),
    Rx45=tex(rot_x(d(45))), R_fixed=tex(R_fixed), R_body=tex(R_body), c45=math.cos(d(45)),
)
