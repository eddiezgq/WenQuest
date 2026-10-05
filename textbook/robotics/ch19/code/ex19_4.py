"""19.4 节的计算：阿克曼转向、自行车模型、转向梯形、最小转弯半径、侧方停车与可控性。

设一台牵引式 AGV：轴距 L = 1.2 m，两前轮主销间距（前轮距）w = 0.8 m，后轮距也取 0.8 m，内侧前轮最大转角 40°；
车身长 1.8 m、宽 1.0 m，前轴到车头 0.3 m，后轴到车尾 0.3 m。

算例 19.4.1  内侧前轮转 30°：由阿克曼条件求外侧前轮的转角、转弯半径、自行车模型的等效转角；四个车轮的转弯半径和转速之比。
             两前轮平行转向时外侧前轮的侧偏角。
算例 19.4.2  最小转弯半径；车身扫过的圆环；一次调头所需的通道宽度。与差速 AGV 比较。
算例 19.4.3  转向梯形：按“梯形臂延长线交于后轴中点”的经验取底角，求外侧轮转角与理想值之差；再扫描底角，求最大误差最小的底角。
算例 19.4.4  自行车模型的李括号：g1、g2、[g1, g2]、[g1, [g1, g2]] 在随机构型处的秩为 4（解析式与数值求导一致）；
             侧方停车：两段反向圆弧加一段直行，横向挪动 0.6 m 所需的转角和路程（精确积分核对）。
"""
import math

import numpy as np

from _mob import flow, lie, rank
from bookout import T, out

L, w, wr = 1.2, 0.8, 0.8
d_max = math.radians(40)
body_L, body_W, oh_f, oh_r = 1.8, 1.0, 0.3, 0.3
deg = math.pi / 180

# ---------------------------------------------------------------- 算例 19.4.1
di = 30 * deg
R = L / math.tan(di) + w / 2                      # 后轴中点的转弯半径
do = math.atan(L / (R + w / 2))
assert abs((1 / math.tan(do) - 1 / math.tan(di)) - w / L) < 1e-12          # 式 (19.4.2)
d_bic = math.atan(L / R)
assert abs(1 / math.tan(d_bic) - (1 / math.tan(di) + 1 / math.tan(do)) / 2) < 1e-12   # 等效转角的余切是两者的平均
R_fi = L / math.sin(di)
R_fo = L / math.sin(do)
R_ri, R_ro = R - wr / 2, R + wr / 2
ratio_rear = R_ro / R_ri
ratio_front = R_fo / R_fi
# 平行转向：两前轮都转 30°，车体若绕阿克曼瞬心转，外侧前轮的速度方向是 do，轮平面却是 di
slip_par = di - do

# ---------------------------------------------------------------- 算例 19.4.2：最小转弯半径与调头
R_min = L / math.tan(d_max) + w / 2
do_max = math.atan(L / (R_min + w / 2))
R_fo_min = math.hypot(R_min + w / 2, L)                      # 外侧前轮
R_out = math.hypot(R_min + body_W / 2, L + oh_f)             # 车身外侧前角
R_in = R_min - body_W / 2                                    # 车身内侧（后轴处）
ring = R_out - R_in
# 一次调头：车头朝 +x 出发，以最小转弯半径左转 180°。车身轮廓上各点绕瞬心转过 0～180°，扫过范围的最高点与最低点之差
outline = [(x, y) for x in np.linspace(-oh_r, L + oh_f, 61) for y in (-body_W / 2, body_W / 2)] + \
          [(x, y) for y in np.linspace(-body_W / 2, body_W / 2, 31) for x in (-oh_r, L + oh_f)]
ys = []
for a in np.linspace(0, math.pi, 721):
    for x, y in outline:                                     # 相对瞬心 (0, R_min) 的位置绕瞬心转 a
        px, py = x, y - R_min
        ys.append(py * math.cos(a) + px * math.sin(a))
U_width = max(ys) - min(ys)
assert abs(max(ys) - R_out) < 1e-3 and U_width < 2 * R_out
# 差速 AGV（B-EDU-DIFF，车身 0.32 m × 0.22 m）原地转动扫过的圆
U_diff = math.hypot(0.32, 0.22)

# ---------------------------------------------------------------- 算例 19.4.3：转向梯形
a_k = 0.15                                                   # 梯形臂长，m


def outer_angle(din, lam):
    """左转（左轮在内侧，转 din）时，由转向梯形的闭环条件求右轮（外侧）的转角。"""
    Kl, Kr = np.array([0.0, w / 2]), np.array([0.0, -w / 2])
    ul = np.array([-math.cos(lam), -math.sin(lam)])           # 零位时左臂的方向：向后、向内
    ur = np.array([-math.cos(lam), math.sin(lam)])
    rod = w - 2 * a_k * math.sin(lam)                        # 横拉杆长
    Rm = lambda t: np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])
    Al = Kl + a_k * Rm(din) @ ul
    f = lambda t: np.linalg.norm(Al - (Kr + a_k * Rm(t) @ ur)) - rod
    lo, hi = -0.05, din + 0.05                               # 外侧轮的转角在 0 与内侧轮转角之间
    for _ in range(50):                                      # 二分法（7.3 节）
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def ideal_outer(din):
    return math.atan(1 / (1 / math.tan(din) + w / L)) if din > 0 else 0.0


grid = np.linspace(0.5, 40, 40) * deg
lam0 = math.atan((w / 2) / L)                                # 经验：梯形臂延长线交于后轴中点
err0 = np.array([outer_angle(d, lam0) - ideal_outer(d) for d in grid])
assert abs(outer_angle(1e-9 + 0.0, lam0)) < 1e-6
e0_max = float(np.abs(err0).max()) / deg
e0_30 = (outer_angle(30 * deg, lam0) - ideal_outer(30 * deg)) / deg
lams = np.linspace(10, 30, 81) * deg
worst = [float(np.abs([outer_angle(d, lm) - ideal_outer(d) for d in grid]).max()) for lm in lams]
k_best = int(np.argmin(worst))
lam_best, e_best = lams[k_best], worst[k_best] / deg
assert e_best <= e0_max + 1e-12
err_best = np.array([outer_angle(d, lam_best) - ideal_outer(d) for d in grid])
# 平行转向（λ = 0，梯形变成平行四边形）：外侧轮与内侧轮转角相同
assert abs(outer_angle(30 * deg, 0.0) - 30 * deg) < 1e-6
rod0 = w - 2 * a_k * math.sin(lam0)
par_err40 = (d_max - ideal_outer(d_max)) / deg                # 平行转向在 40° 时的误差

# ---------------------------------------------------------------- 算例 19.4.4：李括号与侧方停车
g1 = lambda q: np.array([math.cos(q[2]), math.sin(q[2]), math.tan(q[3]) / L, 0.0])   # 后轴中点以 v = 1 前进
g2 = lambda q: np.array([0.0, 0.0, 0.0, 1.0])                                         # 转向角以 1 rad/s 变化
g3 = lie(g1, g2)
g4 = lie(g1, g3)
rng = np.random.default_rng(194)
ranks = set()
for _ in range(20):
    q = np.r_[rng.uniform(-3, 3, 3), rng.uniform(-1.2, 1.2)]
    s2 = 1 / math.cos(q[3]) ** 2
    assert np.allclose(g3(q), [0, 0, -s2 / L, 0], atol=1e-6)
    assert np.allclose(g4(q), [-math.sin(q[2]) * s2 / L, math.cos(q[2]) * s2 / L, 0, 0], atol=1e-5)
    ranks.add(rank(np.column_stack([g1(q), g2(q), g3(q), g4(q)]), 1e-6))
assert ranks == {4}
# 侧方停车（车位在右侧）：倒车右打满转过 α，再倒车左打满转回 α，最后前进 2R sin α 回到原来的纵向位置
y_shift = 0.6
alpha = math.acos(1 - y_shift / (2 * R_min))
x_back = 2 * R_min * math.sin(alpha)


def drive(q, v, delta, dist, n=4000):
    """后轴中点以车速符号 v（±1）走路程 dist，转向角 delta 不变；按圆弧精确积分。"""
    q = np.array(q, float)
    h = dist / n
    k = math.tan(delta) / L
    for _ in range(n):
        ds = v * h
        dphi = k * ds
        if abs(dphi) < 1e-12:
            q[0] += ds * math.cos(q[2]); q[1] += ds * math.sin(q[2])
        else:
            q[0] += (math.sin(q[2] + dphi) - math.sin(q[2])) / k
            q[1] -= (math.cos(q[2] + dphi) - math.cos(q[2])) / k
        q[2] += dphi
    return q


s_arc = R_min * alpha
dmax_bic = math.atan(L / R_min)                              # 自行车模型的等效最大转角
q = drive([0, 0, 0], -1, -dmax_bic, s_arc)                  # 倒车、向右打满：车尾摆向右侧（路沿）
q = drive(q, -1, +dmax_bic, s_arc)
q = drive(q, +1, 0.0, x_back)
assert abs(q[0]) < 1e-9 and abs(q[1] + y_shift) < 1e-9 and abs(q[2]) < 1e-9          # 向右（路沿一侧）挪了 y_shift
path_total = 2 * s_arc + x_back

out(L=L, w=w, d_max_deg=40, body_L=body_L, body_W=body_W, oh_f=oh_f,
    di_deg=30, R=R, do_deg=do / deg, d_bic_deg=d_bic / deg, R_fi=R_fi, R_fo=R_fo, R_ri=R_ri, R_ro=R_ro,
    ratio_rear=ratio_rear, ratio_front=ratio_front, slip_par_deg=slip_par / deg,
    R_min=R_min, do_max_deg=do_max / deg, R_fo_min=R_fo_min, R_out=R_out, R_in=R_in, ring=ring, U_width=U_width, U_diff=U_diff,
    par_err40=par_err40, a_k=a_k, lam0_deg=lam0 / deg, rod0=rod0, e0_max=e0_max, e0_30=e0_30, lam_best_deg=lam_best / deg, e_best=e_best,
    y_shift=y_shift, alpha_deg=alpha / deg, x_back=x_back, s_arc=s_arc, path_total=path_total, dmax_bic_deg=dmax_bic / deg)
