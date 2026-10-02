"""6.1 节的算例。

算例 6.1.1：平面位移的极点。零件在台面上从位姿 A 移到位姿 B，求一个点 c，使绕 c 转一次就能完成这次位移。
            两种算法：解线性方程 (I − R)c = p（式 (6.1.3)）；两点连线的中垂线交点（几何作图）。
算例 6.1.2：UR5e 把零件从输送带搬到夹具上：零件先后两个位姿之间的位移是一个螺旋运动。
            按定理 6.1.1 的构造求 ŝ、θ、d、q、h；再用式 (6.1.7) 的闭式公式求 q；
            最后取零件上的八个角点，验证“绕轴转 θ、再沿轴移 d”与原位移逐点一致，且两个分步可以交换次序。
"""
import math

import numpy as np

from _screw import exp3, log3, pose, rot_z
from bookout import out, tex, vec

d = math.radians

# ---------------------------------------------------------------- 算例 6.1.1 平面
def rot2(t):
    return np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])


pA, phiA = np.array([0.30, 0.05]), d(0)          # 零件参考点的位置 (m) 与朝向
pB, phiB = np.array([0.54, 0.13]), d(60)
R2 = rot2(phiB - phiA)
p2 = pB - R2 @ pA                                # 位移 x′ = R x + p 中的 p
c_lin = np.linalg.solve(np.eye(2) - R2, p2)      # 方法一：(I − R) c = p

# 方法二：零件上两个点 P1、P2 各自从旧位置到新位置，两条连线的中垂线交于极点
P1, P2 = pA, pA + np.array([0.15, 0.0])          # 参考点和沿零件长边 0.15 m 处的点
Q1, Q2 = R2 @ P1 + p2, R2 @ P2 + p2


def bisector(a, b):
    m = (a + b) / 2
    n = b - a                                    # 中垂线：n · (x − m) = 0
    return n, n @ m


n1, c1 = bisector(P1, Q1)
n2, c2 = bisector(P2, Q2)
c_geo = np.linalg.solve(np.array([n1, n2]), np.array([c1, c2]))
assert np.allclose(c_lin, c_geo, atol=1e-12)
assert np.allclose(R2 @ (pA - c_lin) + c_lin, pB)                       # 绕 c 转 60° 把 A 送到 B
assert abs(np.linalg.norm(pA - c_lin) - np.linalg.norm(pB - c_lin)) < 1e-12
cot = 1 / math.tan((phiB - phiA) / 2)
c_formula = 0.5 * (p2 + cot * np.array([-p2[1], p2[0]]))               # 式 (6.1.7) 的平面形式
assert np.allclose(c_formula, c_lin)

# ---------------------------------------------------------------- 算例 6.1.2 空间
p1 = np.array([0.5, -0.2, 0.1])                  # 零件在输送带上的位置 (m)，姿态与 {s} 相同
T1 = pose(np.eye(3), p1)
R_2 = rot_z(d(90))                               # 放到夹具上：绕竖直轴转 90°，位置抬高
T2 = pose(R_2, np.array([0.3, 0.4, 0.25]))
D = T2 @ np.linalg.inv(T1)                       # 位移：x′ = R x + p（在 {s} 中描述），T2 = D T1
R, p = D[:3, :3], D[:3, 3]

# 定理 6.1.1 的构造
s, th = log3(R)                                  # 欧拉定理：转轴和转角
dd = float(s @ p)                                # 沿轴的平移
p_perp = p - dd * s
A = np.eye(3) - R
# 在垂直于 ŝ 的平面内解 (I − R) q = p⊥：用最小二乘（I − R 奇异，但 p⊥ 在其值域内），再去掉沿 ŝ 的分量
q = np.linalg.lstsq(A, p_perp, rcond=None)[0]
q = q - (q @ s) * s
assert np.allclose(A @ q, p_perp, atol=1e-12)
q_formula = 0.5 * (p_perp + (1 / math.tan(th / 2)) * np.cross(s, p_perp))   # 式 (6.1.7)
assert np.allclose(q, q_formula, atol=1e-12)
h = dd / th


def screw_motion(x, frac=1.0):
    """绕过 q、方向 ŝ 的轴转 frac·θ，再沿 ŝ 移 frac·d。"""
    return q + exp3(s * th * frac) @ (x - q) + frac * dd * s


a, b, c = 0.06, 0.04, 0.03                       # 零件半长 (m)
corners = [p1 + np.array([x, y, z]) for x in (-a, a) for y in (-b, b) for z in (-c, c)]
for x in corners:
    xd = R @ x + p
    assert np.allclose(screw_motion(x), xd, atol=1e-12)                   # 逐点一致
    swapped = q + exp3(s * th) @ (x + dd * s - q)                         # 先移后转
    assert np.allclose(swapped, xd, atol=1e-12)
# 轴上的点只沿轴移动 d
assert np.allclose(screw_motion(q) - q, dd * s)
# 零件中心走过的螺旋线：到轴的距离保持不变
r0 = np.linalg.norm(np.cross(s, p1 - q))
for f in np.linspace(0, 1, 11):
    x = screw_motion(p1, f)
    assert abs(np.linalg.norm(np.cross(s, x - q)) - r0) < 1e-12

out(R2=tex(R2, 4), p2=vec(p2, 4), c=vec(c_lin, 4), cx=c_lin[0], cy=c_lin[1], rA=float(np.linalg.norm(pA - c_lin)),
    D=tex(D, 3), p=vec(p, 3), s=vec(s, 3), th_deg=math.degrees(th), d=dd, p_perp=vec(p_perp, 3),
    q=vec(q, 3), h=h, h_mm_per_deg=h * 1000 * math.pi / 180, r0=r0, cot=1 / math.tan(th / 2),
    s_cross=vec(np.cross(s, p_perp), 3))
