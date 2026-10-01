"""算例 4.1.1：手腕转过 30° 后，零件角点 P 的新位置。

按式 (4.1.3)（先化极坐标）和式 (4.1.4)、(4.1.5)（旋转矩阵）分别计算，两者必须一致；
再验证定理 4.1.1 的性质：长度不变、转回去等于转置。
"""
import math

import numpy as np

from bookout import out

x, y = 0.2, 0.1                      # 角点 P 在 {a} 中的分量，m
theta = math.radians(30)             # 转角，rad

# 式 (4.1.2)、(4.1.3)：极坐标
r = math.hypot(x, y)
phi = math.atan2(y, x)
xp_polar = r * math.cos(phi + theta)
yp_polar = r * math.sin(phi + theta)

# 式 (4.1.4)、(4.1.5)：旋转矩阵
c, s = math.cos(theta), math.sin(theta)
R = np.array([[c, -s], [s, c]])
p = np.array([x, y])
pp = R @ p

assert abs(pp[0] - xp_polar) < 1e-12 and abs(pp[1] - yp_polar) < 1e-12        # 两种算法一致
assert np.allclose(R.T @ R, np.eye(2)) and abs(np.linalg.det(R) - 1) < 1e-12   # 定理 4.1.1 (1)(2)
back = R.T @ pp
assert np.allclose(back, p)                                                  # 定理 4.1.1 (3)
assert abs(np.linalg.norm(pp) - np.linalg.norm(p)) < 1e-12                   # 定理 4.1.1 (4)

out(
    r=r, r_sq=x * x + y * y, phi_deg=math.degrees(phi), phi_theta_deg=math.degrees(phi + theta),
    c30=c, s30=s, theta_rad=theta,
    x_p=pp[0], y_p=pp[1],
    term_xc=x * c, term_ys=y * s, term_xs=x * s, term_yc=y * c,
    norm_p=float(np.linalg.norm(p)), norm_pp=float(np.linalg.norm(pp)),
)
