"""20.4 节的计算：质心、支撑多边形与静态稳定裕度。

算例 20.4.1  Go2 站立姿态的质心（由 MJCF 的连杆质量与质心位置，按关节表的正运动学）；抬起一条腿时质心移动多少。
定理 20.4.1  静止在水平地面上、只受重力与地面支持力时，质心的投影必在支撑多边形内：随机取质心位置，用非负最小二乘
            求各脚的支持力，在多边形内残差为零、在外面残差不为零。
算例 20.4.2  Go2 四脚站立，依次抬起每一条腿：三脚支撑三角形的稳定裕度只有毫米量级；机身（脚不动）平移多少，
            质心才能移到三角形的内心、裕度最大；质心雅可比的平移部分小于 1 的原因。
算例 20.4.3  爬行步态（后左、前左、后右、前右）一个周期内的最小稳定裕度，占地系数 β 与机身侧摆幅度 A 的影响。
算例 20.4.4  G1 从双脚站立到单脚站立：骨盆要向支撑脚一侧平移多少，质心才落到左脚底的中央。
"""
import math

import numpy as np

from _leg import (AX, AY, DY, crawl_min_margin, G1, G1_INERTIAL, G1_REST, G1_SOLE, G1_SOLE_R, GAITS, GO2, GO2_FOOT_R, GO2_INERTIAL, LEG_EN, LEG_ZH,
                  LEGS, MASS_G1, MASS_GO2, TH_REST, Tinv, Tm, com, fk_links, g1_leg_ik, g1_sole_world, g1_stand_height, go2_q,
                  hull, in_stance, leg_fk, leg_ik, margin, stance_ik, swing_profile)
from bookout import T, out, tex

h_hip = -leg_fk("FL", TH_REST)[2]
h0 = h_hip + GO2_FOOT_R
feet0 = {leg: leg_fk(leg, TH_REST) + np.array([0, 0, h0]) for leg in LEGS}
T0 = Tm(np.eye(3), (0, 0, h0))


def go2_com_world(T_sb, feet):
    th = stance_ik(T_sb, feet)
    assert not np.any(np.isnan(th))
    return com(GO2, GO2_INERTIAL, go2_q(th), T_sb)[0], th


# ---------------------------------------------------------------- 算例 20.4.1
c_b, m_go2 = com(GO2, GO2_INERTIAL, go2_q(np.tile(TH_REST, 4)))
assert abs(m_go2 - MASS_GO2) < 1e-12
trunk_m = GO2_INERTIAL["base"][1]
trunk_frac = trunk_m / m_go2
# 抬起右前腿：足端向前上方移 (0.05, 0, 0.08) m，其余三只脚不动
feet_lift = dict(feet0)
feet_lift["FR"] = feet0["FR"] + np.array([0.05, 0, 0.08])
c_lift, _ = go2_com_world(T0, feet_lift)
c_0, _ = go2_com_world(T0, feet0)
dc_lift = c_lift - c_0
assert np.allclose(c_0, c_b + np.array([0, 0, h0]), atol=1e-12)


# ---------------------------------------------------------------- 定理 20.4.1：非负支持力存在 ⇔ 质心投影在凸包内
def nnls(A, b, it=4000):
    """非负最小二乘：投影梯度法（小规模，足够准确）。"""
    x = np.zeros(A.shape[1])
    L = np.linalg.norm(A, 2) ** 2
    for _ in range(it):
        x = np.maximum(0, x - (A.T @ (A @ x - b)) / L)
    return x, float(np.linalg.norm(A @ x - b))


P4 = np.array([feet0[l][:2] for l in LEGS])
poly4 = hull(P4)
rng = np.random.default_rng(11)
n_in = n_out = 0
for _ in range(400):
    c = rng.uniform([-0.35, -0.25], [0.35, 0.25])
    A = np.vstack([np.ones(4), P4[:, 0], P4[:, 1]])        # Σf = m𝔤，Σ f p_x = m𝔤 c_x，Σ f p_y = m𝔤 c_y（各除以 m𝔤）
    w, r = nnls(A, np.array([1.0, c[0], c[1]]))
    mg = margin(poly4, c)
    if mg > 1e-3:
        assert r < 1e-6
        n_in += 1
    elif mg < -1e-3:
        assert r > 1e-4
        n_out += 1

# ---------------------------------------------------------------- 算例 20.4.2：抬起一条腿
c0xy = c_0[:2]
tri = {}
for lift in LEGS:
    pts = np.array([feet0[l][:2] for l in LEGS if l != lift])
    tri[lift] = (hull(pts), margin(hull(pts), c0xy))
marg = {l: tri[l][1] for l in LEGS}
assert max(abs(v) for v in marg.values()) < 0.005


def incircle(P):
    a = np.linalg.norm(P[1] - P[2])
    b = np.linalg.norm(P[0] - P[2])
    c = np.linalg.norm(P[0] - P[1])
    s = (a + b + c) / 2
    u, w = P[1] - P[0], P[2] - P[0]
    area = abs(u[0] * w[1] - u[1] * w[0]) / 2
    return (a * P[0] + b * P[1] + c * P[2]) / (a + b + c), area / s


lift = "FR"
ctr, r_in = incircle(np.array([feet0[l][:2] for l in LEGS if l != lift]))
# 机身平移 (dx, dy)（脚不动），使质心投影到内心：二维牛顿迭代，雅可比用差商
d = np.zeros(2)
for _ in range(20):
    c, _ = go2_com_world(Tm(np.eye(3), (d[0], d[1], h0)), feet0)
    e = ctr - c[:2]
    if np.linalg.norm(e) < 1e-12:
        break
    Jc = np.zeros((2, 2))
    for k in range(2):
        dd = np.zeros(2)
        dd[k] = 1e-6
        cp, _ = go2_com_world(Tm(np.eye(3), (d[0] + dd[0], d[1] + dd[1], h0)), feet0)
        cm, _ = go2_com_world(Tm(np.eye(3), (d[0] - dd[0], d[1] - dd[1], h0)), feet0)
        Jc[:, k] = (cp[:2] - cm[:2]) / 2e-6
    d = d + np.linalg.solve(Jc, e)
c_sh, th_sh = go2_com_world(Tm(np.eye(3), (d[0], d[1], h0)), feet0)
assert np.linalg.norm(c_sh[:2] - ctr) < 1e-10
ratio = float(np.linalg.norm(c_sh[:2] - c0xy) / np.linalg.norm(d))
# 质心雅可比的平移部分（定义 20.4.2）：机身连同髋连杆随机身平移，腿的其余部分只随了一部分
Jc_xx = Jc[0, 0]
assert 0.6 < Jc_xx < 1.0
m_hip = sum(GO2_INERTIAL[f"{l}_hip"][1] for l in LEGS)
lower = (trunk_m + m_hip) / m_go2                       # 质心至少随机身移动这一比例

# ---------------------------------------------------------------- 算例 20.4.3：爬行步态的稳定裕度
table = {}
for beta in (0.75, 0.8, 0.85, 0.9):
    for A in (0.0, 0.02, 0.04):
        table[(beta, A)] = crawl_min_margin(beta, A)
assert table[(0.75, 0.0)] < 0.002
best_key = max(table, key=table.get)
rows = [[b] + [table[(b, A)] * 1000 for A in (0.0, 0.02, 0.04)] for b in (0.75, 0.8, 0.85, 0.9)]
cells = {f"mg_{int(round(b * 100))}_{int(round(A * 100))}": table[(b, A)] * 1000 for (b, A) in table}
slope = (table[(0.9, 0.0)] - table[(0.8, 0.0)]) / 0.1 * 1000      # 裕度随 β 增大的速率，mm/(单位 β)

# 裕度为什么只有毫米量级：四脚着地的过渡段（周期的 1/4 到 β − 1/2）里，质心要从对角线 RL–FR 的一侧走到另一侧。
# 过渡段长 (β − 3/4)t_c，机身前进 (β − 3/4)L_s，质心随之前进 k 倍（脚不动时 k < 1，见算例 20.4.2），
# 垂直于对角线的位移再乘 sin α（α 为对角线与 x 轴的夹角）。质心若恰在过渡段中点越过对角线，两端离对角线各为一半；
# 质心偏后 2 mm 使越线时刻偏离中点，β = 3/4 时的裕度 −δ 正是这一偏差。于是 S_min ≈ ½ η (β − 3/4) L_s sin α − δ（式 (20.4.4)）。
V_CR, TC_CR = 0.1, 2.0
LS_CR = V_CR * TC_CR
_, (ts_c, ms_c, cs_c, _, feet_c) = crawl_min_margin(0.85, 0.0, ret=True)
n_c = len(ts_c)
i0, i1 = n_c // 4, int(round(n_c * (0.85 - 0.5)))
dg = feet_c[i0 + 1]["FR"][:2] - feet_c[i0 + 1]["RL"][:2]          # 过渡段中的对角线（两只脚在 {s} 中不动）
sin_a = abs(dg[1]) / float(np.linalg.norm(dg))
k_cw = float((cs_c[i1][0] - cs_c[i0][0]) / ((0.85 - 0.75) * LS_CR))
delta = -table[(0.75, 0.0)]
pred = {b: 0.5 * k_cw * (b - 0.75) * LS_CR * sin_a - delta for b in (0.8, 0.85, 0.9)}
for b_ in pred:
    assert abs(pred[b_] - table[(b_, 0.0)]) < 5e-5                # 近似式与逐时刻计算相差不到 0.05 mm
diag_dx = float(abs(dg[0]))
assert abs(diag_dx - (2 * AX - LS_CR / 4)) < 1e-9                  # 对角线的前后长度 2a_x − L_s/4
mg_tc4 = crawl_min_margin(0.9, 0.0, tc=4.0)                       # 步态周期加倍（步幅 0.4 m）

# ---------------------------------------------------------------- 算例 20.4.4：G1 单脚站立
z_pel = g1_stand_height()                                # 腿伸直、脚底着地时骨盆原点高度
T_p0 = Tm(np.eye(3), (0, 0, z_pel))
Tl0 = fk_links(G1, G1_REST, T_p0)
T_fl = Tl0["left_ankle_roll_link"].copy()
T_fr = Tl0["right_ankle_roll_link"].copy()
c_g1, m_g1 = com(G1, G1_INERTIAL, G1_REST, T_p0)
soles = np.vstack([g1_sole_world(G1_REST, T_p0, "left"), g1_sole_world(G1_REST, T_p0, "right")])
poly2 = hull(soles[:, :2])
mg2 = margin(poly2, c_g1[:2])
polyL = hull(g1_sole_world(G1_REST, T_p0, "left")[:, :2])
sole_len = float(G1_SOLE[2][0] - G1_SOLE[0][0])
sole_w = float(2 * G1_SOLE[0][1])
area_L = 0.5 * abs(np.sum(polyL[:, 0] * np.roll(polyL[:, 1], -1) - np.roll(polyL[:, 0], -1) * polyL[:, 1]))
ctr_L = polyL.mean(0)
mgL0 = margin(polyL, c_g1[:2])                          # 不动骨盆就抬右脚：质心在左脚外面


def g1_pose(dy, dz=0.0):
    """骨盆平移 (0, dy, dz)，两脚不动，两腿各用数值逆解；返回关节、质心。"""
    Tp = Tm(np.eye(3), (0, dy, z_pel + dz))
    q = None
    for side, Tf in (("left", T_fl), ("right", T_fr)):
        q, it, err = g1_leg_ik(side, Tp, Tf, q)
        assert err < 1e-10
    c, _ = com(G1, G1_INERTIAL, q, Tp)
    return q, c, Tp


dz = -0.03                                              # 设：膝稍弯，骨盆降低 3 cm（伸直的腿处在奇异位形，见 20.5 节）
dy = 0.0
for _ in range(30):                                     # 割线法：求骨盆侧移 dy，使质心的 y 坐标等于左脚底中心
    q, c, _ = g1_pose(dy, dz)
    e = ctr_L[1] - c[1]
    if abs(e) < 1e-12:
        break
    q2, c2, _ = g1_pose(dy + 1e-5, dz)
    dy += e / ((c2[1] - c[1]) / 1e-5)
q_sh, c_sh_g1, Tp_sh = g1_pose(dy, dz)
mgL = margin(polyL, c_sh_g1[:2])
ratio_g1 = (c_sh_g1[1] - com(G1, G1_INERTIAL, g1_pose(0.0, dz)[0], Tm(np.eye(3), (0, 0, z_pel + dz)))[0][1]) / dy
hip_roll_L = math.degrees(q_sh["left_hip_roll_joint"])
ankle_roll_L = math.degrees(q_sh["left_ankle_roll_joint"])
assert mgL > 0.0

out(m_go2=m_go2, cbx=c_b[0], cby=c_b[1], cbz=c_b[2], cb=tex(c_b, 4), trunk_m=trunk_m, trunk_frac=trunk_frac * 100,
    c0z=c_0[2], dc_lift=tex(dc_lift * 1000, 2), dcx_mm=dc_lift[0] * 1000, dcz_mm=dc_lift[2] * 1000,
    n_in=n_in, n_out=n_out, n_edge=400 - n_in - n_out,
    m_FL=marg["FL"] * 1000, m_FR=marg["FR"] * 1000, m_RL=marg["RL"] * 1000, m_RR=marg["RR"] * 1000,
    ctr=tex(ctr, 4), ctrx=ctr[0], ctry=ctr[1], r_in=r_in, dx=d[0], dy_go2=d[1], d_norm=float(np.linalg.norm(d)), ratio=ratio,
    Jc_xx=Jc_xx, Jc_yy=Jc[1, 1], lower=lower,
    rows=rows, best_beta=best_key[0], best_A=best_key[1], best_m=table[best_key] * 1000,
    m_075_0=table[(0.75, 0.0)] * 1000, m_09_0=table[(0.9, 0.0)] * 1000, m_075_4=table[(0.75, 0.04)] * 1000,
    m_085_4=table[(0.85, 0.04)] * 1000,
    z_pel=z_pel, m_g1=m_g1, cg1=tex(c_g1, 4), cg1z=c_g1[2], mg2=mg2, sole_len=sole_len, sole_w=sole_w, area_L=area_L * 1e4,
    mgL0=mgL0, ctrLy=ctr_L[1], ctrLx=ctr_L[0], dz=dz, dy_g1=dy, mgL=mgL, ratio_g1=ratio_g1,
    hip_roll_L=hip_roll_L, ankle_roll_L=ankle_roll_L,
    lift_zh=T(LEG_ZH[lift], LEG_EN[lift]), slope=slope, sin_a=sin_a, k_cw=k_cw, delta_mm=delta * 1000,
    pred85=pred[0.85] * 1000, diag_dx=diag_dx, mg_tc4=mg_tc4 * 1000, half_slope=0.5 * k_cw * LS_CR * sin_a * 1000, **cells)
