"""21.1 节的计算：零件库四旋翼 X2 的结构参数、推力分配矩阵与力矩能力。

算例 21.1.1  质心位置、旋翼到质心的距离、旋翼的转向；四个推力对质心产生的力旋量，6×4 矩阵的秩；
             旋翼的高度不影响力矩（两种算法核对）。
算例 21.1.2  4×4 推力分配矩阵的各行两两正交，由此写出逆矩阵（与数值求逆核对）；悬停推力（与模型的悬停关键帧核对）。
算例 21.1.3  悬停时产生 0.1 N·m 的横滚、俯仰、偏航力矩，各旋翼推力要改变多少；偏航与横滚的“力臂”之比。
算例 21.1.4  悬停时各轴能产生的最大力矩；力矩能力随总推力的变化（推力上下限同时约束）。
"""
import math

import numpy as np

from _uav import G, alloc, x2
from bookout import out

P = x2()
m, com, r, c, sig, fmax = P["m"], P["com"], P["r"], P["c"], P["sig"], P["fmax"]
lx, ly = P["lx"], P["ly"]
arm = math.hypot(lx, ly)                               # 旋翼中心到机体中心竖直轴的水平距离
span_diag = 2 * arm                                    # 对角两旋翼中心的距离

# ---------------------------------------------------------------- 算例 21.1.1
A, A6 = alloc(P)
rank6 = np.linalg.matrix_rank(A6)
assert rank6 == 4
assert np.allclose(A6[3:5], 0)                          # 力的 x、y 分量恒为零
# 旋翼高度不影响力矩：把四个旋翼都移到质心所在的水平面上，力矩列不变
P0 = dict(P)
P0["r"] = [np.array([ri[0], ri[1], 0.0]) for ri in r]
assert np.allclose(alloc(P0)[1], A6)
# 力矩的直接写法 m_x = y_i f_i、m_y = −x_i f_i，与叉积一致
for i, ri in enumerate(r):
    assert abs(A6[0, i] - ri[1]) < 1e-15 and abs(A6[1, i] + ri[0]) < 1e-15 and abs(A6[2, i] - sig[i] * c) < 1e-15
com_z = com[2]
z_rot_lo, z_rot_hi = r[0][2], r[2][2]                    # 以质心为原点，后、前旋翼的高度
imu_z = P["imu"][2]
# 转向：反扭矩 σ_i c f_i ẑ_b 与旋翼的转向相反；σ = −1 → 旋翼绕 +z_b 转（从上往下看逆时针）
spin_ccw = [i + 1 for i in range(4) if sig[i] < 0]
assert spin_ccw == [1, 3]

# ---------------------------------------------------------------- 算例 21.1.2
AAT = A @ A.T
assert np.allclose(AAT, np.diag(np.diag(AAT)), atol=1e-15)        # 各行两两正交
d = np.diag(AAT)
assert np.allclose(d, [4, 4 * ly ** 2, 4 * lx ** 2, 4 * c ** 2])
Ainv = A.T @ np.diag(1 / d)
assert np.allclose(Ainv, np.linalg.inv(A), atol=1e-12)
W = m * G
f_hover = np.linalg.solve(A, [W, 0, 0, 0])
assert np.allclose(f_hover, W / 4)
assert abs(f_hover[0] - P["hover"]) < 1e-9                    # 模型文件的悬停关键帧
tw = 4 * fmax / W

# ---------------------------------------------------------------- 算例 21.1.3
mom = 0.1
df_roll = Ainv @ [0, mom, 0, 0]
df_pitch = Ainv @ [0, 0, mom, 0]
df_yaw = Ainv @ [0, 0, 0, mom]
assert np.allclose(np.abs(df_roll), mom / (4 * ly)) and np.allclose(np.abs(df_yaw), mom / (4 * c))
ratio_ly_c = ly / c
f_yaw = f_hover + df_yaw
f_pitch = f_hover + df_pitch
assert np.allclose(A @ f_yaw, [W, 0, 0, mom]) and np.allclose(A @ f_pitch, [W, 0, mom, 0])


# ---------------------------------------------------------------- 算例 21.1.4
def max_moment(F, axis):
    """总推力为 F、另两个力矩为零时，绕 axis（1 = x，2 = y，3 = z）能产生的最大力矩：
    f_i = F/4 + Ainv[i, axis]·M ∈ [0, f_max]，取各旋翼允许的 M 的最小值。"""
    lim = []
    for i in range(4):
        a = Ainv[i, axis]
        lo, hi = (0 - F / 4) / a, (fmax - F / 4) / a
        lim.append(max(lo, hi))
    return min(lim)


mx_h, my_h, mz_h = (max_moment(W, k) for k in (1, 2, 3))
assert abs(mx_h - 4 * ly * W / 4) < 1e-12 and abs(mz_h - 4 * c * W / 4) < 1e-12
F_best = 2 * fmax                                            # 平均推力在上下限中间时，力矩能力最大
mx_best = max_moment(F_best, 1)
mx_2W, mx_3W, mx_35W = max_moment(2 * W, 1), max_moment(3 * W, 1), max_moment(3.5 * W, 1)
# 用线性规划核对：最大化 m_x，约束 A f = (F, ·, 0, 0)，0 ≤ f ≤ f_max
from scipy.optimize import linprog                          # noqa: E402
lp = linprog(-A[1], A_eq=A[[0, 2, 3]], b_eq=[W, 0, 0], bounds=[(0, fmax)] * 4, method="highs")
assert lp.success and abs(-lp.fun - mx_h) < 1e-7
lp3 = linprog(-A[1], A_eq=A[[0, 2, 3]], b_eq=[3 * W, 0, 0], bounds=[(0, fmax)] * 4, method="highs")
assert abs(-lp3.fun - mx_3W) < 1e-7

out(m=m, com_z=com_z, z_rot_lo=z_rot_lo, z_rot_hi=z_rot_hi, imu_z=imu_z, lx=lx, ly=ly, arm=arm, span_diag=span_diag,
    c=c, fmax=fmax, W=W, f_hover=f_hover[0], hover_key=P["hover"], tw=tw, rank6=rank6,
    d1=d[1], d2=d[2], d3=d[3],
    df_roll=abs(df_roll[0]), df_pitch=abs(df_pitch[0]), df_yaw=abs(df_yaw[0]), ratio_ly_c=ratio_ly_c,
    f_yaw_13=f_yaw[0], f_yaw_24=f_yaw[1], f_pitch_back=f_pitch[0], f_pitch_front=f_pitch[2],
    mx_h=mx_h, my_h=my_h, mz_h=mz_h, mx_best=mx_best, F_best=F_best, mx_2W=mx_2W, mx_3W=mx_3W,
    pct_2W=mx_2W / mx_h * 100, pct_3W=mx_3W / mx_h * 100, mx_35W=mx_35W, pct_35W=mx_35W / mx_h * 100)
