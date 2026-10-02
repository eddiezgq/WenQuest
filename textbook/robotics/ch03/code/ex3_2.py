"""3.2 节的算例。

算例 3.2.1：抛光工具的轴线方向与工件表面法线的夹角（点积），并把工具轴分解为沿法线和沿表面的两部分（投影公式）。
算例 3.2.2：力传感器所受的力矩 m = r × F：分量公式、反对称矩阵 [r]F、几何办法（力臂 × 力）三种算法互相核对。
算例 3.2.3：三点确定工作台面，第四点到台面的距离 = 混合积 / 平行四边形面积；与行列式、与“法线点积”两种算法核对。
另外验证：二重叉积公式、[a]² = aaᵀ − |a|²I、拉格朗日恒等式、雅可比恒等式（随机矢量）；左手系的行列式为 −1。
"""
import math

import numpy as np

from _vec import cross, d, skew, unit
from bookout import out, tex, vec

# ---------------------------------------------------------------- 算例 3.2.1 点积与投影
u_raw = np.array([0.05, 0.12, -0.99])           # 工具轴的方向（机座坐标系 {a} 中，未归一化）
u = unit(u_raw)
n = np.array([0.0, -math.sin(d(10)), math.cos(d(10))])   # 表面外法线（单位矢量）
m_in = -n                                        # 工具应当沿内法线指向表面
cos_t = float(u @ m_in)                          # 式 (3.2.3)：分量公式
theta = math.degrees(math.acos(cos_t))
# 几何核对：用叉积的长度 |u × m| = sin θ 求同一个角
assert abs(math.degrees(math.asin(np.linalg.norm(np.cross(u, m_in)))) - theta) < 1e-9
u_par = (u @ n) * n                               # 式 (3.2.5)：沿法线的部分
u_perp = u - u_par                               # 沿表面的部分
assert abs(u_perp @ n) < 1e-15 and abs(np.linalg.norm(u_perp) - math.sin(math.radians(theta))) < 1e-12

# ---------------------------------------------------------------- 算例 3.2.2 叉积与力矩
r = np.array([0.08, 0.03, -0.10])               # 传感器中心 → 零件质心，m
mass, g = 1.5, 9.81
F = np.array([0.0, 0.0, -mass * g])             # 重力，N
m1 = cross(r, F)                                 # 分量公式 (3.2.9)
m2 = skew(r) @ F                                 # 反对称矩阵 (3.2.10)
assert np.allclose(m1, m2) and np.allclose(m1, np.cross(r, F))
rho = math.hypot(r[0], r[1])                     # 力臂：质心到“过传感器中心的竖直线”的距离
assert abs(np.linalg.norm(m1) - rho * mass * g) < 1e-12        # 几何办法：|m| = 力臂 × 力
assert abs(m1 @ r) < 1e-12 and abs(m1 @ F) < 1e-12             # m 垂直于 r 和 F
assert np.allclose(skew(r).T, -skew(r))

# ---------------------------------------------------------------- 算例 3.2.3 混合积
P = np.array([[400, -200, 100], [700, -180, 103], [450, 150, 98], [680, 120, 104]], float)   # mm
a, b, c = P[1] - P[0], P[2] - P[0], P[3] - P[0]
axb = np.cross(a, b)
area = np.linalg.norm(axb)                       # 平行四边形面积，mm²
mixed = float(axb @ c)                           # 混合积 = 平行六面体有向体积，mm³
det = float(np.linalg.det(np.column_stack([a, b, c])))
assert abs(mixed - det) < 1e-6 * abs(det)        # 定理：混合积 = 行列式
h = mixed / area                                 # 第四点到台面的有向距离，mm
nhat = axb / area
assert abs(h - nhat @ c) < 1e-9                  # 第二种算法：单位法线点积
assert abs(np.cross(b, c) @ a - mixed) < 1e-6 and abs(np.cross(c, a) @ b - mixed) < 1e-6   # 轮换不变
tilt = math.degrees(math.acos(abs(nhat[2])))     # 台面相对水平面的倾角

# ---------------------------------------------------------------- 右手系与左手系
X, Y, Z = np.array([0, 1.0, 0]), np.array([1.0, 0, 0]), np.array([0, 0, 1.0])   # 某配置文件给出的三根轴
det_lh = float(np.linalg.det(np.column_stack([X, Y, Z])))
assert abs(det_lh + 1) < 1e-12 and abs(np.cross(X, Y) @ Z + 1) < 1e-12

# ---------------------------------------------------------------- 恒等式（随机矢量）
rng = np.random.default_rng(3)
for _ in range(200):
    A, B, Cc = rng.normal(size=(3, 3))
    assert np.allclose(np.cross(A, np.cross(B, Cc)), B * (A @ Cc) - Cc * (A @ B))      # 二重叉积
    assert np.allclose(np.cross(np.cross(A, B), Cc), B * (A @ Cc) - A * (B @ Cc))
    assert np.allclose(skew(A) @ skew(A), np.outer(A, A) - (A @ A) * np.eye(3))       # [a]²
    assert abs(np.linalg.norm(np.cross(A, B)) ** 2 - ((A @ A) * (B @ B) - (A @ B) ** 2)) < 1e-9   # 拉格朗日恒等式
    jac = np.cross(A, np.cross(B, Cc)) + np.cross(B, np.cross(Cc, A)) + np.cross(Cc, np.cross(A, B))
    assert np.allclose(jac, 0)                                                          # 雅可比恒等式
    assert np.allclose(skew(A) @ skew(A) @ skew(A), -(A @ A) * skew(A))                # [a]³ = −|a|²[a]

out(
    u1=u[0], u2=u[1], u3=u[2], u_norm=float(np.linalg.norm(u_raw)), s10=math.sin(d(10)), c10=math.cos(d(10)),
    cos_t=cos_t, theta=theta, un=float(u @ n), u_perp=vec(u_perp, 4), u_perp_len=float(np.linalg.norm(u_perp)),
    Fz=F[2], m_vec=vec(m1, 4), mx=m1[0], my=m1[1], m_len=float(np.linalg.norm(m1)), rho=rho, mg=mass * g,
    skew_r=tex(skew(r), 2),
    a_vec=vec(a, 0), b_vec=vec(b, 0), c_vec=vec(c, 0), axb=vec(axb, 0), area=area, mixed=mixed, h=h, tilt=tilt,
    det_lh=det_lh,
)
