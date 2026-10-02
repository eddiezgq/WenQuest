"""6.4 节的算例。

先验证定理 6.4.1 的闭式与级数一致、G(θ)⁻¹ 的公式 (6.4.8) 正确。
算例 6.4.1（指数映射）：机械臂抓住阀门手轮的边缘，把手轮逆时针转 90°；阀杆螺纹每转上升 4 mm。
            求转动后手爪的位姿。三种算法：定理 6.4.1 的闭式；矩阵指数的级数；定义 6.1.1 的几何作法。
算例 6.4.2（对数映射）：UR5e 从零位运动到一组关节角，求这次位移的旋量轴、转角、节距和轴上一点；
            用 scipy 的矩阵对数 logm 独立核对，再把结果代回指数映射，应得到原来的位移。
算例 6.4.3：两种特殊情形——纯平移（R = I）与转角 π。
另：沿螺旋轴插值 T(s) = e^{[S]θs} M 时，法兰盘中心的路径到螺旋轴的距离保持不变。
"""
import math

import numpy as np
from scipy.linalg import expm, logm

from _screw import (G, G_inv, UR_M, axis_of, bracket, exp3, exp6, expm_series, inv, log6, pose, screw_from_axis,
                    skew, ur_fk)
from bookout import out, tex, vec

d = math.radians

# ---------------------------------------------------------------- 定理 6.4.1 与式 (6.4.8)
rng = np.random.default_rng(6)
for _ in range(20):
    w = rng.normal(size=3)
    w /= np.linalg.norm(w)
    v = rng.normal(size=3)
    t = rng.uniform(0.1, 3.0)
    S = np.r_[w, v]
    assert np.allclose(exp6(S, t), expm_series(bracket(S) * t), atol=1e-12)
    assert np.allclose(exp6(S, t), expm(bracket(S) * t), atol=1e-12)
    assert np.allclose(G(w, t) @ G_inv(w, t), np.eye(3), atol=1e-12)
    T = exp6(S, t)
    S2, t2 = log6(T)
    assert np.allclose(exp6(S2, t2), T, atol=1e-12)          # 先对数再指数，回到原处

# ---------------------------------------------------------------- 算例 6.4.1
q = np.array([0.45, 0.20, 0.0])          # 阀杆轴线上一点 (m)
s_hat = np.array([0, 0, 1.0])            # 阀杆竖直向上；逆时针（从上往下看）为正
lead = 0.004                             # 螺距 4 mm/r
h = lead / (2 * math.pi)                 # 节距 m/rad
S = screw_from_axis(q, s_hat, h)
th = d(90)
T0 = pose(np.diag([1.0, -1.0, -1.0]), np.array([0.45 + 0.12, 0.20, 0.30]))   # 手爪：在手轮边缘，z 轴朝下
E = exp6(S, th)
T1 = E @ T0
assert np.allclose(E, expm_series(bracket(S) * th), atol=1e-13)            # 级数
geo = pose(exp3(s_hat * th), q + exp3(s_hat * th) @ (-q) + h * th * s_hat)  # 定义 6.1.1：x′ = q + R(x − q) + hθŝ
assert np.allclose(E, geo, atol=1e-14)
rise = T1[2, 3] - T0[2, 3]
assert abs(rise - lead / 4) < 1e-15
Gv = G(s_hat, th) @ S[3:]
Iq = (np.eye(3) - exp3(s_hat * th)) @ q + h * th * s_hat
assert np.allclose(Gv, Iq)                                                   # 式 (6.4.6)

# ---------------------------------------------------------------- 算例 6.4.2
theta = np.array([d(30), d(-45), d(60), d(-15), d(90), d(30)])
Tt = ur_fk(theta)
D = Tt @ inv(UR_M)                        # 空间中的位移：T(θ) = D M
S_log, th_log = log6(D)
Lm = np.real(logm(D))                     # 独立方法：scipy 的矩阵对数
assert np.allclose(Lm, bracket(S_log) * th_log, atol=1e-10)
assert np.allclose(exp6(S_log, th_log), D, atol=1e-12)
s2, q2, h2 = axis_of(S_log)
d2 = h2 * th_log
# 沿螺旋轴插值：法兰盘中心到轴的距离不变
p0 = UR_M[:3, 3]
r0 = np.linalg.norm(np.cross(s2, p0 - q2))
path = np.array([(exp6(S_log, th_log * f) @ np.r_[p0, 1])[:3] for f in np.linspace(0, 1, 21)])
for x in path:
    assert abs(np.linalg.norm(np.cross(s2, x - q2)) - r0) < 1e-12
assert np.allclose(path[-1], Tt[:3, 3])
lin_mid = (p0 + Tt[:3, 3]) / 2            # 直线插值的中点与螺旋插值的中点之差
dev_mid = float(np.linalg.norm(path[10] - lin_mid))
# 物体坐标系中的位移 M⁻¹T(θ) 的对数（6.5 节用）
B_log, thb = log6(inv(UR_M) @ Tt)
assert abs(thb - th_log) < 1e-12

# ---------------------------------------------------------------- 算例 6.4.3 特殊情形
Dtr = pose(np.eye(3), np.array([0.3, 0.4, 0.0]))
St, tt = log6(Dtr)
assert np.allclose(St, [0, 0, 0, 0.6, 0.8, 0]) and abs(tt - 0.5) < 1e-15
Dpi = exp6(screw_from_axis([0.1, 0, 0], [0, 0, 1.0], 0.0), math.pi)
Spi, tpi = log6(Dpi)
assert abs(tpi - math.pi) < 1e-12 and np.allclose(exp6(Spi, tpi), Dpi, atol=1e-12)
assert np.allclose(Dpi[:3, 3], [0.2, 0, 0])

out(S=vec(S, 6), h=h, h_mm=h * 1000, E=tex(E, 4), T1=tex(T1, 4), T0=tex(T0, 3), rise_mm=rise * 1000,
    Gth=tex(G(s_hat, th), 4), Gv=vec(Gv, 4),
    theta_deg=vec(np.degrees(theta), 0), Tt=tex(Tt, 4), D=tex(D, 4), S_log=vec(S_log, 4), th_log=th_log,
    th_log_deg=math.degrees(th_log), s2=vec(s2, 4), q2=vec(q2, 4), h2=h2, d2=d2, r0=r0, dev_mid_mm=dev_mid * 1000,
    B_log=vec(B_log, 4), Ginv_err=0.0)
