"""19.1 节的计算：车轮约束、可移动度与瞬心；脚轮不施加约束；矢量场的李括号与可控性。

算例 19.1.2  四种车轮布置的不侧滑约束矩阵 C、它的秩、可移动度 δm = 3 − rank C 和瞬心：
             差速 AGV（B-EDU-DIFF）、手推购物车、前轮固定的三轮车、两前轮平行转向的四轮车（以及按阿克曼条件转向）。
             用两种方法求瞬心：由 C 的零空间（运动旋量）算 (−v_y/ω, v_x/ω)，与几何作图（各轮轴线的交点）核对。
算例 19.1.1  脚轮：任给车体运动旋量，由式 (19.1.7) 求出脚轮的转向角速度，脚轮的接地点确实不侧滑（数值微分核对）。
算例 19.1.3  独轮车模型与带轮转角的五维模型的李括号：解析式与数值求导一致；李代数的秩分别为 3 和 4；
             五维模型中与所有矢量场都垂直的方向就是式 (11.5.14) 的完整约束。
"""
import math

import numpy as np

from _mob import diff_cart, flow, icr, jac, lie, noslip_row, nullspace, rank, roll_row, contact
from bookout import T, out

P = diff_cart()
r, b = P["r"], P["b"]

# ---------------------------------------------------------------- 算例 19.1.2：四种车轮布置
deg = math.pi / 180


def layout_C(wheels):
    """wheels：[(x_i, y_i, β_i)]，只列固定或可转向的标准轮；脚轮不施加约束，不列入。"""
    return np.array([noslip_row(x, y, bt) for x, y, bt in wheels])


def axle_point(wheels):
    """几何作图：各轮轴线（过接地点、方向 n_i）的公共交点；最小二乘求，残差为零说明交于一点。"""
    A, rhs = [], []
    for x, y, bt in wheels:
        e = np.array([math.cos(bt), math.sin(bt)])        # 轴线的法向就是滚动方向 e：点 p 在轴线上 ⇔ e·(p − 接地点) = 0
        A.append(e)
        rhs.append(e @ np.array([x, y]))
    A, rhs = np.array(A), np.array(rhs)
    p, *_ = np.linalg.lstsq(A, rhs, rcond=None)
    return p, float(np.linalg.norm(A @ p - rhs))


half = b / 2
diff = [(0.0, half, 0.0), (0.0, -half, 0.0)]                          # 两驱动轮；后部的脚轮不列入
Cd = layout_C(diff)
cart_w = 0.25
cart = [(0.0, cart_w, 0.0), (0.0, -cart_w, 0.0)]                      # 购物车：后轮固定，前轮是脚轮
Cc = layout_C(cart)
tri_L = 0.30
tri = [(0.0, half, 0.0), (0.0, -half, 0.0), (tri_L, 0.0, 0.0)]       # 三轮车：前轮固定朝前
Ct = layout_C(tri)
# 四轮车：轴距 L、轮距 w（取 19.4 节牵引车的数据），内侧（左）前轮转 30°
L4, w4 = 1.2, 0.8
di = 30 * deg
R_ack = L4 / math.tan(di) + w4 / 2                                   # 后轴中点到瞬心
do_ack = math.atan(L4 / (R_ack + w4 / 2))
par = [(0.0, w4 / 2, 0.0), (0.0, -w4 / 2, 0.0), (L4, w4 / 2, di), (L4, -w4 / 2, di)]          # 两前轮平行转向
ack = [(0.0, w4 / 2, 0.0), (0.0, -w4 / 2, 0.0), (L4, w4 / 2, di), (L4, -w4 / 2, do_ack)]      # 按阿克曼条件转向
Cp, Ca = layout_C(par), layout_C(ack)

ranks = dict(diff=rank(Cd), cart=rank(Cc), tri=rank(Ct), par=rank(Cp), ack=rank(Ca))
mob = {k: 3 - v for k, v in ranks.items()}
assert ranks == dict(diff=1, cart=1, tri=2, par=3, ack=2)

# 差速：零空间 = {ω, v_x 任意, v_y = 0}；瞬心在 y_b 轴上，位置由 v_x/ω 决定
Nd = nullspace(Cd)
assert Nd.shape[1] == 2 and np.allclose(np.abs(Nd[2]), 0, atol=1e-12)
# 三轮车：零空间只有 (0, 1, 0)：只能直行
Nt = nullspace(Ct)
assert Nt.shape[1] == 1 and np.allclose(np.abs(Nt[:, 0]), [0, 1, 0], atol=1e-12)
# 阿克曼：零空间一维，瞬心 = 后轴延长线上 R_ack 处；与几何作图（四条轴线的交点）一致
Na = nullspace(Ca)[:, 0]
c_null = icr(Na)
c_geo, res_geo = axle_point(ack)
assert np.allclose(c_null, [0, R_ack], atol=1e-9) and np.allclose(c_geo, c_null, atol=1e-9) and res_geo < 1e-9
# 平行转向：四条轴线不交于一点，最小二乘残差不为零
_, res_par = axle_point(par)
assert res_par > 0.05
# 平行转向时外侧前轮的侧偏角：若车体绕阿克曼瞬心转动，外侧前轮的速度方向与轮平面的夹角
p_of = np.array([L4, -w4 / 2]) - np.array([0, R_ack])
vdir = math.atan2(p_of[0], -p_of[1])          # ω ẑ × (p − c) 的方向（ω > 0），与 x_b 的夹角
slip_par = (di - vdir)                        # 轮平面方向 di 与速度方向之差
assert abs(vdir - do_ack) < 1e-12

# 差速 AGV：由纯滚动的两行求两轮转速，与 1.6 节的式 (1.6.3)、(1.6.4) 核对
V_ex = np.array([0.5, 0.5, 0.0])               # ω = 0.5 rad/s，v_x = 0.5 m/s
wR = roll_row(0.0, -half, 0.0) @ V_ex / r
wL = roll_row(0.0, half, 0.0) @ V_ex / r
assert abs(r * (wR + wL) / 2 - V_ex[1]) < 1e-12 and abs(r * (wR - wL) / b - V_ex[0]) < 1e-12

# ---------------------------------------------------------------- 算例 19.1.1：脚轮
d_c = 0.04                                       # 脚轮偏距，m
A_c = np.array([0.64, 0.25])                     # 脚轮转向轴在 {b} 中的位置（购物车左前角），m
beta0 = 0.0                                      # 脚轮此刻朝前
V_side = np.array([0.0, 0.0, 0.5])               # 车体向左平移 0.5 m/s（v_y = 0.5）
vA = contact(*A_c) @ V_side
e0 = np.array([math.cos(beta0), math.sin(beta0)])
n0 = np.array([-math.sin(beta0), math.cos(beta0)])
beta_dot = n0 @ vA / d_c - V_side[0]             # 式 (19.1.7)
theta_dot_c = e0 @ vA / 0.05                     # 脚轮半径取 0.05 m
# 数值核对：接地点 C = A − d e(β) 随时间的位置（{s} 中，车体此刻在原点、φ = 0），C 的速度在轮轴方向的分量应为零
def C_world(t):
    phi = V_side[0] * t
    Rm = np.array([[math.cos(phi), -math.sin(phi)], [math.sin(phi), math.cos(phi)]])
    o = V_side[1:] * t                            # ω = 0，平移
    bt = beta0 + beta_dot * t
    return o + Rm @ (A_c - d_c * np.array([math.cos(bt), math.sin(bt)]))
h = 1e-6
vC = (C_world(h) - C_world(-h)) / (2 * h)
assert abs(n0 @ vC) < 1e-8
# 一个任意的运动旋量也一样：随机取 20 个，都能解出 β̇，接地点不侧滑
rng = np.random.default_rng(19)
for _ in range(20):
    V = rng.normal(size=3)
    bt = rng.uniform(-math.pi, math.pi)
    e, n = np.array([math.cos(bt), math.sin(bt)]), np.array([-math.sin(bt), math.cos(bt)])
    vA_ = contact(*A_c) @ V
    bd = n @ vA_ / d_c - V[0]
    vC_ = vA_ - d_c * (V[0] + bd) * n             # 式 (19.1.6)
    assert abs(n @ vC_) < 1e-12

# ---------------------------------------------------------------- 算例 19.1.3：李括号与可控性
g1 = lambda q: np.array([math.cos(q[2]), math.sin(q[2]), 0.0])      # 前进（v = 1）
g2 = lambda q: np.array([0.0, 0.0, 1.0])                             # 转动（ω = 1）
g12 = lie(g1, g2)
ranks_uni = []
for _ in range(20):
    q = rng.uniform(-3, 3, 3)
    br = g12(q)
    assert np.allclose(br, [math.sin(q[2]), -math.cos(q[2]), 0], atol=1e-7)          # 式 (19.1.14)
    ranks_uni.append(rank(np.column_stack([g1(q), g2(q), br]), 1e-6))
assert set(ranks_uni) == {3}
# 交替运动的净位移 ≈ ε²[g1, g2]（与 6.7 节一致，这里用矢量场的流计算）
eps = 0.1
q0 = np.array([0.0, 0.0, math.radians(30)])
q4 = flow(lambda q: -g2(q), flow(lambda q: -g1(q), flow(g2, flow(g1, q0, eps), eps), eps), eps)
pred = eps ** 2 * g12(q0)
gap_bracket = float(np.linalg.norm((q4 - q0) - pred))
assert gap_bracket < 2 * eps ** 3

# 五维模型 q = (x, y, φ, θ_R, θ_L)：输入是两轮转速
gR = lambda q: np.array([r / 2 * math.cos(q[2]), r / 2 * math.sin(q[2]), r / b, 1.0, 0.0])
gL = lambda q: np.array([r / 2 * math.cos(q[2]), r / 2 * math.sin(q[2]), -r / b, 0.0, 1.0])
gRL = lie(gR, gL)
gRRL = lie(gR, gRL)
gLRL = lie(gL, gRL)
ranks5 = []
covec = []
for _ in range(20):
    q = rng.uniform(-3, 3, 5)
    k = r * r / b
    assert np.allclose(gRL(q), [-k * math.sin(q[2]), k * math.cos(q[2]), 0, 0, 0], atol=1e-7)
    M = np.column_stack([gR(q), gL(q), gRL(q), gRRL(q), gLRL(q)])
    ranks5.append(rank(M, 1e-6))
    u, s, vt = np.linalg.svd(M.T)
    a = vt[-1] / vt[-1][2]                        # 与所有矢量场垂直的方向，按 φ 分量归一
    covec.append(a)
assert set(ranks5) == {4}
covec = np.array(covec)
assert np.allclose(covec, [0, 0, 1, -r / b, r / b], atol=1e-6)           # 即 dφ − (r/b)(dθ_R − dθ_L) = 0，式 (11.5.14)

out(r=r, b=b, half=half, cart_w=cart_w, tri_L=tri_L, L4=L4, w4=w4,
    rk_diff=ranks["diff"], rk_cart=ranks["cart"], rk_tri=ranks["tri"], rk_par=ranks["par"], rk_ack=ranks["ack"],
    dm_diff=mob["diff"], dm_cart=mob["cart"], dm_tri=mob["tri"], dm_par=mob["par"], dm_ack=mob["ack"],
    R_ack=R_ack, do_ack_deg=do_ack / deg, slip_par_deg=slip_par / deg, res_par=res_par,
    wR_ex=wR, wL_ex=wL,
    d_c=d_c, beta_dot=beta_dot, theta_dot_c=theta_dot_c,
    eps=eps, gap_bracket=gap_bracket, k_br=r * r / b, rank_uni=3, rank5=4, rb=r / b,
    dx4=float(q4[0] - q0[0]), dy4=float(q4[1] - q0[1]), px=float(pred[0]), py=float(pred[1]))
