"""11.2 节：自由度与格吕布勒公式。

对一组机构，分别用格吕布勒公式 (11.2.2) 和“约束的秩”两种方法求自由度：
- 公式：数构件数 N（含机架）、关节数 J 和各关节自由度 f_i；
- 秩：在一个已经装配好的位置上，把各运动构件的运动旋量和各关节速度当作未知数，每个关节给出 6 个线性方程
  V_b − V_a − S_j θ̇_j = 0（_ch11.mobility），自由度 = 未知数个数 − 秩。这是真实的（瞬时）自由度。
两者不一致的地方，就是公式的例外：被动自由度（Delta 的杆绕自身轴线空转）、过约束（平面机构按空间算、
平行四边形加第三根杆、本内特机构），以及奇异位置（平行四边形机构的共线位置）。
另外用单回路的速度闭环方程 Σ S_i θ̇_i = 0 核对单回路机构：自由度 = n − rank(S_1 … S_n)（式 (11.2.6)）。
"""
import math

import numpy as np

from _ch11 import (exp6, grubler, joint_P, joint_R, joint_S, joint_U, mobility, screw_revolute, tinv, ur_screws)
from _fig11 import circ_int
from bookout import T, out

z = np.array([0, 0, 1.0])
xh = np.array([1.0, 0, 0])


def P3(p):
    return np.array([p[0], p[1], 0.0])


rows = []          # (名称, N, J, Σf, 公式 m, 真实 m)


def record(name, m_body, n_moving, joints, f_list, extra=None):
    nu, ne, rank, m_true, N = mobility(n_moving, joints)
    m_formula = grubler(m_body, n_moving + 1, f_list)
    rows.append((name, n_moving + 1, len(f_list), sum(f_list), m_formula, m_true))
    return m_formula, m_true, N


# ---------------------------------------------------------------- 平面机构（转轴都沿 z）
# 四杆机构：机架 0.40，曲柄 0.15，连杆 0.35，摇杆 0.30（满足格拉斯霍夫条件，曲柄能整周转动）
A, D = np.array([0.0, 0.0]), np.array([0.40, 0.0])
t1 = math.radians(60)
B = A + 0.15 * np.array([math.cos(t1), math.sin(t1)])
Cc = circ_int(B, 0.35, D, 0.30, 1)
j4 = [(0, 1, joint_R(z, P3(A))), (1, 2, joint_R(z, P3(B))), (2, 3, joint_R(z, P3(Cc))), (3, 0, joint_R(z, P3(D)))]
g4_planar, m4, _ = record(T("平面四杆机构", "planar four-bar"), 3, 3, j4, [1, 1, 1, 1])
g4_spatial = grubler(6, 4, [1, 1, 1, 1])
assert g4_planar == 1 and m4 == 1 and g4_spatial == -2

# 曲柄滑块机构：曲柄 0.10，连杆 0.30，滑块沿 x
t1 = math.radians(60)
B = 0.1 * np.array([math.cos(t1), math.sin(t1)])
xs = B[0] + math.sqrt(0.3 ** 2 - B[1] ** 2)
jsc = [(0, 1, joint_R(z, P3(A))), (1, 2, joint_R(z, P3(B))), (2, 3, joint_R(z, P3((xs, 0)))), (3, 0, joint_P(xh))]
gsc, msc, _ = record(T("曲柄滑块机构", "slider-crank"), 3, 3, jsc, [1, 1, 1, 1])
assert gsc == 1 and msc == 1

# 平面五杆机构：机架两点相距 0.30，四根杆长 0.20、0.30、0.30、0.20
A5, E5 = np.array([0.0, 0.0]), np.array([0.30, 0.0])
B5 = A5 + 0.2 * np.array([math.cos(math.radians(110)), math.sin(math.radians(110))])
D5 = E5 + 0.2 * np.array([math.cos(math.radians(70)), math.sin(math.radians(70))])
C5 = circ_int(B5, 0.3, D5, 0.3, -1)
j5 = [(0, 1, joint_R(z, P3(A5))), (1, 2, joint_R(z, P3(B5))), (2, 3, joint_R(z, P3(C5))), (3, 4, joint_R(z, P3(D5))), (4, 0, joint_R(z, P3(E5)))]
g5, m5, _ = record(T("平面五杆机构", "planar five-bar"), 3, 4, j5, [1] * 5)
assert g5 == 2 and m5 == 2

# 平行四边形机构加第三根曲柄：机架上三个铰点 (0,0)、(0.3,0)、(0.6,0)，三根曲柄长 0.25，连杆连接三个端点
tp = math.radians(60)
e = 0.25 * np.array([math.cos(tp), math.sin(tp)])
G = [np.array([0.0, 0]), np.array([0.3, 0]), np.array([0.6, 0])]
jpp = [(0, 1, joint_R(z, P3(G[0]))), (0, 2, joint_R(z, P3(G[1]))), (0, 3, joint_R(z, P3(G[2]))),
       (1, 4, joint_R(z, P3(G[0] + e))), (2, 4, joint_R(z, P3(G[1] + e))), (3, 4, joint_R(z, P3(G[2] + e)))]
gpp, mpp, _ = record(T("平行四边形加一根曲柄", "parallelogram with an extra crank"), 3, 4, jpp, [1] * 6)
assert gpp == 0 and mpp == 1
# 第三根曲柄若稍长一点（0.26，它在连杆上的铰点也外移 1 cm，原位置仍能装上），机构就卡死了：几何条件一破坏，过约束机构就动不了
jbad = list(jpp)
e2 = 0.26 * np.array([math.cos(tp), math.sin(tp)])
# 此时三根曲柄仍互相平行，按秩算出的瞬时自由度仍为 1；但真正动一下，第三根曲柄的长度约束就不满足了：
jbad[5] = (3, 4, joint_R(z, P3(G[2] + e2)))
_, _, _, m_jam, _ = mobility(4, jbad)
assert m_jam == 1
d_ang = 0.5                                         # 曲柄 1 再转 0.5 rad，连杆随之平移
shift = 0.25 * np.array([math.cos(tp + d_ang), math.sin(tp + d_ang)]) - e
jam_err = abs(np.linalg.norm(G[2] + e2 + shift - G[2]) - 0.26)     # 第三根曲柄需要的长度变化 (m)
assert jam_err > 1e-3

# 剪叉式升降台（一级）：两根长 2a 的杆在中点铰接，下端一个固定铰、一个滑块，上端同样
a, phi = 0.6, math.radians(35)
c, s = math.cos(phi), math.sin(phi)
# 构件：1 杆 A，2 杆 B，3 平台，4 下滑块，5 上滑块
jsl = [(0, 1, joint_R(z, P3((0, 0)))), (0, 4, joint_P(xh)), (4, 2, joint_R(z, P3((2 * a * c, 0)))),
       (1, 2, joint_R(z, P3((a * c, a * s)))), (2, 3, joint_R(z, P3((0, 2 * a * s)))), (3, 5, joint_P(xh)),
       (5, 1, joint_R(z, P3((2 * a * c, 2 * a * s))))]
gsl, msl, _ = record(T("剪叉式升降台（一级）", "scissor lift (one stage)"), 3, 5, jsl, [1] * 7)
assert gsl == 1 and msl == 1

# ---------------------------------------------------------------- 空间机构
# UR5e：开链，6 个转动关节（表 12.1.1 的旋量轴，零位）
S_ur, _ = ur_screws()
jur = [(i, i + 1, S.reshape(6, 1)) for i, S in enumerate(S_ur)]
gur, mur, _ = record(T("UR5e（开链）", "UR5e (open chain)"), 6, 6, jur, [1] * 6)
assert gur == 6 and mur == 6

# Delta：零件库模型的尺寸。主动臂 0.22 m，从动杆 0.5 m，静平台半径 0.15 m，动平台半径 0.04 m；
# 每个平行四边形的两根杆相距 w = 0.06 m。动平台在 (0, 0, −0.42) m 时，主动臂转角为模型给出的 0.187523 rad。
Rb, Rp, La, Lb, w = 0.15, 0.04, 0.22, 0.5, 0.06
pz = np.array([0, 0, -0.42])


def delta_angle(p, k):
    """动平台中心在 p 时，第 k 条支链的主动臂转角（逆运动学，11.5 节式 (11.5.6)）。"""
    ph = 2 * math.pi * k / 3
    er, et = np.array([math.cos(ph), math.sin(ph), 0]), np.array([-math.sin(ph), math.cos(ph), 0])
    q = p + Rp * er - Rb * er              # 球关节中点相对主动臂转轴中心
    u, v, h = q @ er, q @ et, q[2]
    # |(La cosθ − u, −v, −La sinθ − h)| = Lb  ⇒  A cosθ + B sinθ = C
    Aa, Bb = -2 * La * u, 2 * La * h
    Cc_ = Lb ** 2 - La ** 2 - u * u - v * v - h * h
    r = math.hypot(Aa, Bb)
    base = math.atan2(Bb, Aa)
    return base + math.acos(Cc_ / r)       # 肘部朝外的那一支


th_rest = delta_angle(pz, 0)
assert abs(th_rest - 0.187523) < 1e-6


def delta_joints(p, th, rod_end="S"):
    """Delta 的关节表。构件编号：1–3 主动臂，4–9 从动杆（每条支链两根），10 动平台。"""
    js = []
    for k in range(3):
        ph = 2 * math.pi * k / 3
        er, et = np.array([math.cos(ph), math.sin(ph), 0]), np.array([-math.sin(ph), math.cos(ph), 0])
        Bk = Rb * er
        Ek = Bk + La * (math.cos(th[k]) * er - math.sin(th[k]) * np.array([0, 0, 1.0]))
        Pk = p + Rp * er
        js.append((0, 1 + k, joint_R(et, Bk)))                  # 主动臂的转轴沿切向
        for sgn, rod in ((1, 4 + 2 * k), (-1, 5 + 2 * k)):
            e1, e2 = Ek + sgn * w / 2 * et, Pk + sgn * w / 2 * et
            js.append((1 + k, rod, joint_S(e1)))
            if rod_end == "S":
                js.append((rod, 10, joint_S(e2)))
            else:                                               # 用万向节代替一端的球关节，消去杆的空转
                d = (e2 - e1) / np.linalg.norm(e2 - e1)
                n1 = np.cross(d, et)
                n1 /= np.linalg.norm(n1)
                js.append((rod, 10, joint_U(et, n1, e2)))
    return js


th3 = [th_rest] * 3
jd = delta_joints(pz, th3, "S")
fd = [1] * 3 + [3] * 12
gd, md, Nd = record(T("Delta（杆两端为球关节）", "Delta (ball joints at both rod ends)"), 6, 10, jd, fd)
# 动平台的运动旋量：取零空间里各基向量中动平台的 6 个分量，其张成的空间是 3 维的纯平移
Vp = Nd[6 * 9:6 * 10, :]
rank_p = np.linalg.matrix_rank(Vp, tol=1e-9)
assert rank_p == 3 and np.allclose(Vp[:3, :], 0, atol=1e-9)
# 杆的空转：每根杆的角速度可以沿杆的方向任意取，共 6 个
jd2 = delta_joints(pz, th3, "U")
fd2 = [1] * 3 + [3, 2] * 6
gd2, md2, _ = record(T("Delta（杆一端改为万向节）", "Delta (one rod end a universal joint)"), 6, 10, jd2, fd2)
assert (gd, md) == (9, 9) and (gd2, md2) == (3, 3)

# Stewart 平台 6-UPS：静平台、动平台上的六个点（三对，对称布置）
ra, rb = 0.5, 0.3
aa = [ra * np.array([math.cos(t), math.sin(t), 0]) for t in np.radians([-10, 10, 110, 130, 230, 250])]
bb = [rb * np.array([math.cos(t), math.sin(t), 0]) + np.array([0, 0, 0.6]) for t in np.radians([-50, 50, 70, 170, 190, 290])]
jst = []
for i in range(6):
    d = (bb[i] - aa[i]) / np.linalg.norm(bb[i] - aa[i])
    u1 = np.cross(d, z)
    u1 /= np.linalg.norm(u1)
    u2 = np.cross(d, u1)
    low, up = 1 + i, 7 + i
    jst += [(0, low, joint_U(u1, u2, aa[i])), (low, up, joint_P(d)), (up, 13, joint_S(bb[i]))]
gst, mst, _ = record(T("Stewart 平台 6-UPS", "Stewart platform 6-UPS"), 6, 13, jst, [2, 1, 3] * 6)
assert gst == 6 and mst == 6

# 本内特机构：四个转动关节的空间单回路。DH 参数 a1 = a3 = a，α1 = α3 = α；a2 = a4 = b，α2 = α4 = β，a/sinα = b/sinβ
aB, alB, beB = 0.3, math.radians(30), math.radians(60)
bB = aB * math.sin(beB) / math.sin(alB)
KB = math.sin((beB + alB) / 2) / math.sin((beB - alB) / 2)


def dhA(th, a_, al):
    ct, st, ca, sa = math.cos(th), math.sin(th), math.cos(al), math.sin(al)
    return np.array([[ct, -st * ca, st * sa, a_ * ct], [st, ct * ca, -ct * sa, a_ * st], [0, sa, ca, 0], [0, 0, 0, 1]])


def bennett(t1_):
    """给定 θ1，按本内特的关系 tan(θ1/2) tan(θ2/2) = K、θ3 = −θ1、θ4 = −θ2 求四个关节角，并返回闭环误差。"""
    t2_ = 2 * math.atan(KB / math.tan(t1_ / 2))
    th = [t1_, t2_, -t1_, -t2_]
    Tl = dhA(th[0], aB, alB) @ dhA(th[1], bB, beB) @ dhA(th[2], aB, alB) @ dhA(th[3], bB, beB)
    return th, np.abs(Tl - np.eye(4)).max()


closure = max(bennett(t)[1] for t in np.linspace(0.2, 3.0, 15))
assert closure < 1e-12
# 在 θ1 = 1 rad 处：四根关节轴（DH 的 z 轴）在机架坐标系中的旋量
thB, _ = bennett(1.0)
Tcur, SB = np.eye(4), []
for k in range(4):
    SB.append(screw_revolute(Tcur[:3, 2], Tcur[:3, 3]))
    Tcur = Tcur @ dhA(thB[k], [aB, bB][k % 2], [alB, beB][k % 2])
jB = [(0, 1, SB[1].reshape(6, 1)), (1, 2, SB[2].reshape(6, 1)), (2, 3, SB[3].reshape(6, 1)), (3, 0, SB[0].reshape(6, 1))]
gB, mB, _ = record(T("本内特机构（4R 空间单回路）", "Bennett linkage (spatial 4R loop)"), 6, 3, jB, [1] * 4)
rank_B = np.linalg.matrix_rank(np.column_stack(SB), tol=1e-9)
assert gB == -2 and mB == 1 and rank_B == 3
# 对照：任取四根空间直线作关节轴，单回路的秩为 4，自由度为 0
rng = np.random.default_rng(3)
Sr = [screw_revolute(v / np.linalg.norm(v), q) for v, q in zip(rng.normal(size=(4, 3)), rng.normal(size=(4, 3)))]
rank_r = np.linalg.matrix_rank(np.column_stack(Sr), tol=1e-9)
assert rank_r == 4

# ---------------------------------------------------------------- 单回路公式 (11.2.6) 与奇异位置
# 四杆机构：四个平面转动旋量的秩为 3，n − rank = 1
rank4 = np.linalg.matrix_rank(np.column_stack([j[2][:, 0] for j in j4]), tol=1e-9)
assert 4 - rank4 == m4
# 平行四边形机构（机架 0.4、曲柄 0.2、连杆 0.4、摇杆 0.2）转到四杆共线的位置：四个铰点都在 x 轴上
col = [P3((0, 0)), P3((0.2, 0)), P3((0.6, 0)), P3((0.4, 0))]
rank_col = np.linalg.matrix_rank(np.column_stack([screw_revolute(z, q) for q in col]), tol=1e-9)
m_col = 4 - rank_col
assert m_col == 2
# 一般位置（曲柄 60°）时仍为 1
q2 = P3(0.2 * np.array([math.cos(1.0), math.sin(1.0)]))
gen = [P3((0, 0)), q2, q2 + P3((0.4, 0)), P3((0.4, 0))]
assert 4 - np.linalg.matrix_rank(np.column_stack([screw_revolute(z, q) for q in gen]), tol=1e-9) == 1

table = "\n".join(f"| {n} | {N} | {J} | {sf} | {str(g).replace('-', '−')} | {m} |" for n, N, J, sf, g, m in rows)
out(table=table, jam_err_mm=jam_err * 1000, g4s=g4_spatial, delta_th=th_rest, delta_th_deg=math.degrees(th_rest), bB=bB, KB=KB,
    rank_B=rank_B, rank_r=rank_r, rank_col=rank_col, m_col=m_col, gd=gd, gd2=gd2, gst=gst, gB=gB)
