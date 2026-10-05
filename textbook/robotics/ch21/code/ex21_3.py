"""21.3 节的计算：欠驱动。

算例 21.3.1  X2 的输入矩阵 B(R)（以总推力和物体角加速度为输入）的秩；缺少的两个方向就是 x_b、y_b 方向的推力加速度。
算例 21.3.2  横移 2 m（起止悬停，高度不变）：倾角限制 25°、横滚角速度限制 2 rad/s（示意值）。
             求对称梯形倾角曲线下的最短时间，与“能直接侧推、不必倾斜”的假想全驱动飞行器比较（侧向加速度上限相同）。
             用两种方法核对：解析的分段积分与数值积分；终点速度为零。
算例 21.3.3  倾斜旋翼的六旋翼（示意：臂长 0.25 m，质量、单个推力上限与 X2 相同）：力旋量矩阵的秩随倾斜角的变化；
             机身水平时的最大侧向加速度（线性规划）；悬停所需总推力与重力之比。
"""
import math

import numpy as np
from scipy.optimize import brentq, linprog

from _uav import EZ, G, x2
from bookout import out

P = x2()
m, fmax = P["m"], P["fmax"]

# ---------------------------------------------------------------- 算例 21.3.1
def B_of(R):
    """(p̈, ω̇_b) = (−𝔤ẑ, 0) + B(R) (f, ω̇_b)：6×4 输入矩阵。"""
    B = np.zeros((6, 4))
    B[0:3, 0] = R[:, 2] / m
    B[3:6, 1:4] = np.eye(3)
    return B


rng = np.random.default_rng(1)
ranks = set()
for _ in range(200):
    A = rng.normal(size=(3, 3))
    Q, _r = np.linalg.qr(A)
    Q = Q * np.sign(np.linalg.det(Q))
    B = B_of(Q)
    ranks.add(int(np.linalg.matrix_rank(B)))
    # 推力加速度在 x_b、y_b 上的分量恒为零：B 的前三行与 x_b、y_b 正交
    assert abs(Q[:, 0] @ B[0:3, 0]) < 1e-14 and abs(Q[:, 1] @ B[0:3, 0]) < 1e-14
assert ranks == {4}
rankB = 4

# ---------------------------------------------------------------- 算例 21.3.2：横移 2 m
d, phi_max, w_max = 2.0, math.radians(25), 2.0
tr = phi_max / w_max                                     # 倾角由 0 转到上限所需时间


def profile(h, n_per=4000):
    """对称梯形倾角曲线：0 → φ_max（tr），保持 h，φ_max → −φ_max（2tr），保持 h，−φ_max → 0（tr）。
    返回 (时间, 倾角, 侧向加速度, 速度, 位移)，用梯形法逐段数值积分。"""
    T = 4 * tr + 2 * h
    t = np.linspace(0, T, int(n_per * max(T, 1e-3)) + 1)

    def phi(tt):
        if tt < tr:
            return w_max * tt
        if tt < tr + h:
            return phi_max
        if tt < 3 * tr + h:
            return phi_max - w_max * (tt - tr - h)
        if tt < 3 * tr + 2 * h:
            return -phi_max
        return -phi_max + w_max * (tt - 3 * tr - 2 * h)

    ph = np.array([phi(x) for x in t])
    a = G * np.tan(ph)
    v = np.concatenate([[0], np.cumsum((a[1:] + a[:-1]) / 2 * np.diff(t))])
    y = np.concatenate([[0], np.cumsum((v[1:] + v[:-1]) / 2 * np.diff(t))])
    return t, ph, a, v, y


def dist_analytic(h):
    """解析算法：倾角曲线关于中点奇对称，终点速度为零，位移 = 2 × 前半段的位移。前半段：斜升 tr、保持 h、斜降 tr。
    斜升：v(t) = (𝔤/ω)[−ln cos ωt]；保持：匀加速 𝔤 tan φ_max；斜降：v(t) = v₂ + (𝔤/ω)[ln cos(φ_max − ωt) − ln cos φ_max]。
    各段的位移是速度的积分（数值求积，误差 < 1e-12）。返回 (位移, 最大速度)。"""
    from scipy.integrate import quad
    w = w_max
    v1 = G / w * (-math.log(math.cos(phi_max)))
    a_hold = G * math.tan(phi_max)
    v2 = v1 + a_hold * h
    s1 = quad(lambda t: G / w * (-math.log(math.cos(w * t))), 0, tr, epsabs=1e-13)[0]
    s2 = v1 * h + 0.5 * a_hold * h * h
    s3 = quad(lambda t: v2 + G / w * (math.log(math.cos(phi_max - w * t)) - math.log(math.cos(phi_max))), 0, tr, epsabs=1e-13)[0]
    return 2 * (s1 + s2 + s3), v2 + v1


h_star = brentq(lambda h: dist_analytic(h)[0] - d, 0.0, 5.0, xtol=1e-14)
T_under = 4 * tr + 2 * h_star
t_, ph_, a_, v_, y_ = profile(h_star)
assert abs(y_[-1] - d) < 1e-6 and abs(v_[-1]) < 1e-9                       # 两种方法一致；终点静止
v_peak = dist_analytic(h_star)[1]
assert abs(v_peak - v_.max()) < 1e-6
a_cap = G * math.tan(phi_max)
T_ideal = 2 * math.sqrt(d / a_cap)                       # 全驱动：侧向加速度阶跃 ±a_cap
penalty = T_under - T_ideal
f_peak = m * G / math.cos(phi_max)
# 角速度不受限时（w → ∞），时间趋于 T_ideal：w = 20 rad/s 时
w_save = w_max


def T_for_w(w):
    global w_max, tr
    w_max, tr = w, phi_max / w
    hh = brentq(lambda h: dist_analytic(h)[0] - d, 0.0, 5.0, xtol=1e-14)
    T = 4 * tr + 2 * hh
    w_max, tr = w_save, phi_max / w_save
    return T


T_w1 = T_for_w(1.0)
T_w20 = T_for_w(20.0)
assert T_ideal < T_w20 < T_under < T_w1

# ---------------------------------------------------------------- 算例 21.3.3：倾斜旋翼的六旋翼
L6, c6 = 0.25, P["c"]


def hexa(alpha):
    """6×6 力旋量矩阵：旋翼 i 在方位 60°·i，推力方向绕机臂（径向）交替倾斜 ±α；转向交替。"""
    A = np.zeros((6, 6))
    for i in range(6):
        az = math.radians(60 * i)
        r = L6 * np.array([math.cos(az), math.sin(az), 0.0])
        e_t = np.array([-math.sin(az), math.cos(az), 0.0])             # 切向
        s = 1 if i % 2 == 0 else -1
        u = math.cos(alpha) * EZ + s * math.sin(alpha) * e_t              # 推力方向（单位矢量）
        sig = -1 if i % 2 == 0 else 1
        A[0:3, i] = np.cross(r, u) + sig * c6 * u
        A[3:6, i] = u
    return A


rows6 = []
for deg in (0, 10, 20, 30):
    A6 = hexa(math.radians(deg))
    rk = int(np.linalg.matrix_rank(A6, tol=1e-9))
    # 机身水平、保持悬停时的最大侧向力（沿 x_b）：线性规划
    if rk == 6:
        res = linprog(c=-A6[3], A_eq=A6[[0, 1, 2, 4, 5]], b_eq=[0, 0, 0, 0, m * G], bounds=[(0, fmax)] * 6, method="highs")
        assert res.success
        a_side = -res.fun / m
    else:
        a_side = 0.0
    # 悬停（无侧向力）所需的推力之和
    res0 = linprog(c=np.ones(6), A_eq=A6, b_eq=[0, 0, 0, 0, 0, m * G], bounds=[(0, fmax)] * 6, method="highs")
    assert res0.success
    sv = np.linalg.svd(A6, compute_uv=False)
    rows6.append((deg, rk, a_side, res0.x.sum() / (m * G), sv[-1]))
assert rows6[0][1] == 4 or rows6[0][1] == 5
assert all(r[1] == 6 for r in rows6[1:])
assert abs(rows6[2][3] - 1 / math.cos(math.radians(20))) < 1e-6        # 悬停效率 cos α
rank_hex0 = rows6[0][1]

out(rankB=rankB, d=d, phi_max_deg=math.degrees(phi_max), w_max=w_max, tr=tr, h_star=h_star, T_under=T_under, T_ideal=T_ideal,
    penalty=penalty, penalty_pct=penalty / T_ideal * 100, a_cap=a_cap, f_peak=f_peak, v_peak=v_peak, T_w1=T_w1, T_w20=T_w20,
    rank_hex0=rank_hex0,
    hx10_a=rows6[1][2], hx20_a=rows6[2][2], hx30_a=rows6[3][2],
    hx10_e=(rows6[1][3] - 1) * 100, hx20_e=(rows6[2][3] - 1) * 100, hx30_e=(rows6[3][3] - 1) * 100,
    hx10_s=rows6[1][4], hx20_s=rows6[2][4], hx30_s=rows6[3][4])
