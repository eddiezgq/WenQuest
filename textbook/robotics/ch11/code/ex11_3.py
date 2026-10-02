"""11.3 节：构型空间与任务空间。

(1) 算例 11.3.1：平面 2R 臂（大臂 0.425 m、小臂 0.392 m，同 UR5e）的构型空间是环面 T²。
    从 θa = (150°, −60°) 到 θb = (−120°, 60°)：按普通平面的直线走，关节 1 转 −270°；在环面上走最短路，关节 1 转 +90°。
    障碍物为圆心 (0.45, 0.35) m、半径 0.10 m 的圆柱（俯视为圆）。两条路径分别做碰撞检查。
(2) 构型空间障碍物：在 1° 网格上检查碰撞，算出被障碍物占据的构型所占的比例。
(3) 正运动学不是一一映射：同一末端位置有肘上、肘下两组关节角，两组都用正运动学核对。
(4) SO(3) 不能用三个数整体地、无奇异地描述：ZYX 欧拉角到旋转矩阵的映射，其雅可比矩阵（9 × 3）在俯仰角 90° 时秩降为 2。
(5) 钟表的时针和分针：构型空间是 T²，但两针由齿轮联动，实际只能在环面上的一条闭曲线上运动；
    这条曲线与“两针重合”的对角线交于 11 点，即 12 小时内两针重合 11 次。
"""
import math

import numpy as np

from _ch11 import L1, L2, OBS_C, OBS_R, collide, fk2, wrap
from bookout import out

# ---------------------------------------------------------------- (1) 环面上的最短路
ta, tb = np.radians([150.0, -60.0]), np.radians([-120.0, 60.0])
d_naive = tb - ta
d_torus = wrap(tb - ta)
s = np.linspace(0, 1, 2001)
hit_naive = collide(ta[0] + s * d_naive[0], ta[1] + s * d_naive[1])
hit_torus = collide(ta[0] + s * d_torus[0], ta[1] + s * d_torus[1])
assert not collide(*ta) and not collide(*tb)
assert hit_naive.any() and not hit_torus.any()
# 两条路的终点是同一个构型：末端位置相同
assert np.allclose(fk2(*(ta + d_naive))[1], fk2(*(ta + d_torus))[1], atol=1e-12)
# 第一次碰到障碍物时，关节 1 转过了多少
k_hit = int(np.argmax(hit_naive))
th1_hit = math.degrees(ta[0] + s[k_hit] * d_naive[0])

# ---------------------------------------------------------------- (2) 构型空间障碍物
g = np.radians(np.arange(-180, 180, 1.0))
T1, T2 = np.meshgrid(g, g, indexing="ij")
C = collide(T1, T2)
frac = C.mean()
# 另一种算法：随机抽样
rng = np.random.default_rng(7)
U = rng.uniform(-np.pi, np.pi, (200000, 2))
frac_mc = collide(U[:, 0], U[:, 1]).mean()
assert abs(frac - frac_mc) < 0.003

# ---------------------------------------------------------------- (3) 肘上、肘下
p = np.array([0.55, -0.25])
c2 = (p @ p - L1 ** 2 - L2 ** 2) / (2 * L1 * L2)
sols = []
for sg in (1, -1):
    t2 = sg * math.acos(c2)
    t1 = math.atan2(p[1], p[0]) - math.atan2(L2 * math.sin(t2), L1 + L2 * math.cos(t2))
    assert np.allclose(fk2(t1, t2)[1], p, atol=1e-12)
    sols.append((math.degrees(t1), math.degrees(t2)))
(up1, up2), (dn1, dn2) = sols[1], sols[0]            # θ2 < 0 为肘上（逆时针为正时肘部在上方）


# ---------------------------------------------------------------- (4) ZYX 欧拉角的奇异
def R_zyx(a):
    ps, th, ph = a
    Rz = np.array([[math.cos(ps), -math.sin(ps), 0], [math.sin(ps), math.cos(ps), 0], [0, 0, 1]])
    Ry = np.array([[math.cos(th), 0, math.sin(th)], [0, 1, 0], [-math.sin(th), 0, math.cos(th)]])
    Rx = np.array([[1, 0, 0], [0, math.cos(ph), -math.sin(ph)], [0, math.sin(ph), math.cos(ph)]])
    return Rz @ Ry @ Rx


def jac_rank(a, h=1e-6):
    J = np.column_stack([(R_zyx(a + h * e) - R_zyx(a - h * e)).ravel() / (2 * h) for e in np.eye(3)])
    return np.linalg.matrix_rank(J, tol=1e-6)


rank_gen = jac_rank(np.array([0.3, 0.4, 0.5]))
rank_sing = jac_rank(np.array([0.3, math.pi / 2, 0.5]))
assert rank_gen == 3 and rank_sing == 2

# ---------------------------------------------------------------- (5) 钟表的两根指针
t = np.linspace(0, 720, 720 * 2000 + 1)              # 分钟，12 小时
a_h = np.radians(0.5 * t) % (2 * np.pi)              # 时针每分钟 0.5°
a_m = np.radians(6.0 * t) % (2 * np.pi)              # 分针每分钟 6°
diff = wrap(a_m - a_h)
crossings = int(((diff[:-1] < 0) & (diff[1:] >= 0)).sum())
# 解析：6t − 0.5t = 360k，t = 720k/11，k = 0, 1, …, 10（t = 720 与 t = 0 是同一时刻）
assert crossings == 11
t_first = 720 / 11

out(d1_naive=math.degrees(d_naive[0]), d1_torus=math.degrees(d_torus[0]), d2=math.degrees(d_torus[1]), th1_hit=th1_hit,
    frac_pct=100 * frac, frac_mc_pct=100 * frac_mc, up1=up1, up2=up2, dn1=dn1, dn2=dn2,
    rank_gen=rank_gen, rank_sing=rank_sing, crossings=crossings, t_first=t_first, t_first_s=(t_first - 65) * 60)
