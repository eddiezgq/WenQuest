"""算例 13.1.1–13.1.3：公垂线；标准 DH 与改进 DH；约定用错的后果。

13.1.1 Panda 关节 3 与关节 4 的轴（由零件库模型读出，即表 12.3.1）是异面直线：用式 (13.1.1)–(13.1.3) 求公垂线的垂足、长度和夹角，
       再用“直接求两条直线上距离最近的两点”（数值极小化）独立核对。
13.1.2 平面 3R 臂（与第 12 章相同：0.425、0.392、0.1 m）的标准 DH 表和改进 DH 表；
       θ = (30°, 45°, −90°) 时两种约定给出同一个末端位姿，并与指数积（算例 12.2.1）一致。
       同时核对：四步连乘 (13.1.4)、(13.1.7) 与展开式 (13.1.5)、(13.1.8) 相同；定理 13.1.2 的 T^S = T^M X_n。
13.1.3 把一张表套进另一种约定的公式：平面 3R 臂与 UR5e（算例 12.3.1 的关节角）各差多少。
"""
import math

import numpy as np

from _dh import (Model, Rx, Rz, Tx, Tz, clean, common_normal, exp6, fk_mdh, fk_sdh, fk_space, mdh, mdh_closed, screw_revolute,
                 sdh, sdh_closed, ur_poe, ur_vendor)
from bookout import out, tex, vec

rng = np.random.default_rng(13)

# ---------------------------------------------------------------- 算例 13.1.1 公垂线
pa = Model("B-ARM-PANDA", "link0", "hand", (0, 0, 0), [f"joint{i}" for i in range(1, 8)])
(_, w3, q3), (_, w5, q5) = pa.axes()[2], pa.axes()[3]
kind, f1, f2, dist, n = common_normal(q3, w3, q5, w5)
assert kind == "skew"
# 独立核对：在两条直线上各取一点，数值上使距离最小（网格 + 细化），应得到同样的垂足
u1, u2 = np.asarray(w3, float), np.asarray(w5, float)
best = (1e9, 0, 0)
for t in np.linspace(-1, 1, 201):
    for s in np.linspace(-1, 1, 201):
        dd = np.linalg.norm(np.asarray(q3) + t * u1 - np.asarray(q5) - s * u2)
        if dd < best[0]:
            best = (dd, t, s)
_, t0, s0 = best
for _ in range(60):          # 交替投影：固定一点，求另一条直线上最近的点
    p = np.asarray(q5) + s0 * u2
    t0 = (p - np.asarray(q3)) @ u1
    p = np.asarray(q3) + t0 * u1
    s0 = (p - np.asarray(q5)) @ u2
g1, g2 = np.asarray(q3) + t0 * u1, np.asarray(q5) + s0 * u2
assert np.allclose(g1, f1, atol=1e-9) and np.allclose(g2, f2, atol=1e-9)
assert abs(np.linalg.norm(g2 - g1) - dist) < 1e-9
alpha35 = math.atan2(np.cross(u1, u2) @ n, u1 @ u2)
# 式 (13.1.1) 的系数行列式 = (u1·u2)² − 1 = −|u1 × u2|²
assert abs(((u1 @ u2) ** 2 - 1) + np.linalg.norm(np.cross(u1, u2)) ** 2) < 1e-12

# ---------------------------------------------------------------- 四步连乘与展开式
for _ in range(200):
    a, al, d, th = rng.uniform(-1, 1), rng.uniform(-math.pi, math.pi), rng.uniform(-1, 1), rng.uniform(-math.pi, math.pi)
    assert np.allclose(sdh(a, al, d, th), sdh_closed(a, al, d, th), atol=1e-12)
    assert np.allclose(mdh(a, al, d, th), mdh_closed(a, al, d, th), atol=1e-12)
    # 沿 z 的转动与平移可交换，沿 x 的平移与转动可交换（两个“螺旋运动”）
    assert np.allclose(Rz(th) @ Tz(d), Tz(d) @ Rz(th)) and np.allclose(Tx(a) @ Rx(al), Rx(al) @ Tx(a))

# ---------------------------------------------------------------- 算例 13.1.2 平面 3R
L1, L2, L3 = 0.425, 0.392, 0.1
th = np.radians([30.0, 45.0, -90.0])
sdh3 = [(L1, 0, 0, 0), (L2, 0, 0, 0), (L3, 0, 0, 0)]                  # (a_i, α_i, d_i, θ_i)
mdh3 = [(0, 0, 0, 0), (L1, 0, 0, 0), (L2, 0, 0, 0)]                   # (a_{i-1}, α_{i-1}, d_i, θ_i)
T_s = fk_sdh(sdh3, th)
T_m = fk_mdh(mdh3, th)
T_m_tool = T_m @ Tx(L3)                                               # 改进 DH 的 {3} 在关节 3 上，末端还差 X_3
z = np.array([0, 0, 1.0])
S3r = [screw_revolute(z, q) for q in ([0, 0, 0], [L1, 0, 0], [L1 + L2, 0, 0])]
M3r = np.eye(4)
M3r[0, 3] = L1 + L2 + L3
T_poe = fk_space(S3r, M3r, th)
assert np.allclose(T_s, T_poe, atol=1e-12) and np.allclose(T_m_tool, T_poe, atol=1e-12)
tip_m = T_m[:3, 3]                                                    # 改进 DH 的 {3}：关节 3 的中心

# 定理 13.1.2：T^S_{0n} = T^M_{0n} X_n，对一般的空间链（随机参数）也成立
for _ in range(100):
    nj = 5
    A = rng.uniform(-0.5, 0.5, nj)
    AL = rng.uniform(-math.pi, math.pi, nj)
    D = rng.uniform(-0.5, 0.5, nj)
    q = rng.uniform(-math.pi, math.pi, nj)
    s_tab = [(A[i], AL[i], D[i], 0) for i in range(nj)]
    m_tab = [((A[i - 1], AL[i - 1]) if i else (0, 0)) + (D[i], 0) for i in range(nj)]
    assert np.allclose(fk_sdh(s_tab, q), fk_mdh(m_tab, q) @ Tx(A[-1]) @ Rx(AL[-1]), atol=1e-12)

# ---------------------------------------------------------------- 算例 13.1.3 约定用错
wrong3 = fk_sdh(mdh3, th)                    # 把改进 DH 表代进标准 DH 公式
err3 = float(np.linalg.norm(wrong3[:3, 3] - T_poe[:3, 3]))
vend = ur_vendor()
q_ex = np.radians([30.0, -60.0, 90.0, -120.0, -90.0, 45.0])            # 算例 12.3.1 的关节角
right = fk_sdh(vend, q_ex)
wrong_ur = fk_mdh(vend, q_ex)                                         # 把标准 DH 表代进改进 DH 公式
err_ur = float(np.linalg.norm(wrong_ur[:3, 3] - right[:3, 3]))
# 在一万组随机关节角下，用错约定的末端位置误差
errs = []
for _ in range(10000):
    q = rng.uniform(-math.pi, math.pi, 6)
    errs.append(np.linalg.norm(fk_mdh(vend, q)[:3, 3] - fk_sdh(vend, q)[:3, 3]))
errs = np.array(errs)

out(f1=vec(clean(f1), 4), f2=vec(clean(f2), 4), dist=dist, n=vec(clean(n), 0), alpha35=math.degrees(alpha35),
    q3=vec(clean(q3), 4), q4=vec(clean(q5), 4), w3=vec(clean(w3), 0), w4=vec(clean(w5), 0),
    T3=tex(clean(T_s, 1e-12), 4), tipx=T_s[0, 3], tipy=T_s[1, 3], jx=tip_m[0], jy=tip_m[1],
    wx=wrong3[0, 3], wy=wrong3[1, 3], err3=err3,
    ur_right=vec(right[:3, 3], 4), ur_wrong=vec(wrong_ur[:3, 3], 4), err_ur=err_ur,
    err_min=errs.min(), err_mean=errs.mean(), err_max=errs.max())
