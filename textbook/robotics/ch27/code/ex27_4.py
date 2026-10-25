"""27.4 节的计算：抓取的力封闭。

(1) 算例 27.4.1：两个手指捏住一块截面 40 mm 宽的零件（平面问题），两个接触点在相对的两面上错开 Δ。
    由定理 27.4.2（两指对径条件）判断，再用线性规划（定理 27.4.1）核对；μ = 0.2 时 Δ 最大能到多少。
(2) 算例 27.4.2：夹 SH-301 毛坯的几种接触（空间问题），是否力封闭、抓取质量 ε（力矩除以毛坯半径 r）：
    两指各一个点接触（有摩擦）；同上但为软指（扭转摩擦）；平口夹爪（每指一条接触线，两端两点）；V 形夹爪；无摩擦时。
(3) 算例 27.4.3：上下料动作（第 22 章，A → B）中，平口与 V 形夹爪所需的最小夹紧力（线性规划，式 (27.4.6)），
    含惯性力；最大值出现在哪里；B 处平口夹爪“接触线两端法向力相等”时的值（与 27.2 节、MuJoCo 一致）。
"""
import math

import numpy as np

from _ch27 import (D_BAR, MU_JAW, blank_wrench, cell_move, contact_wrenches, ferrari_canny, force_closure, hand_motion, jaw_contacts,
                   min_grip, quintic, ur_chain)
from bookout import out

# ---------------------------------------------------------------- (1) 平面：两指对径
WIDTH = 0.040
MU1 = 0.2


def planar_fc(delta, mu, width=WIDTH, k=2):
    """两个点接触在 y = ±width/2 的两个平面上，x 方向错开 delta。平面力旋量 (m_z, f_x, f_y)，力矩除以 width。"""
    C = [(np.array([0.0, width / 2]), np.array([0.0, -1.0])), (np.array([delta, -width / 2]), np.array([0.0, 1.0]))]
    cols = []
    for p, n in C:
        t = np.array([-n[1], n[0]])
        for s in (1, -1):
            f = n + s * mu * t
            cols.append(np.r_[(p[0] * f[1] - p[1] * f[0]) / width, f])
    return force_closure(np.array(cols).T)


delta_max = MU1 * WIDTH                               # 定理 27.4.2：连线与法向的夹角 arctan(Δ/w) ≤ arctan μ
ok_in = planar_fc(0.99 * delta_max, MU1)[0]
ok_out = planar_fc(1.01 * delta_max, MU1)[0]
assert ok_in and not ok_out
# 二分法从线性规划求出边界，与公式比较
lo, hi = 0.0, 0.05
while hi - lo > 1e-7:
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if planar_fc(mid, MU1)[0] else (lo, mid)
delta_lp = (lo + hi) / 2

# ---------------------------------------------------------------- (2) 空间：夹毛坯的几种接触
r = D_BAR / 2
single = [(np.array([r, 0, 0]), np.array([-1.0, 0, 0]), 0), (np.array([-r, 0, 0]), np.array([1.0, 0, 0]), 1)]
MU_T_A = MU_JAW * 0.005                               # 软指：扭转摩擦矩 = μ_t a × 法向力，取 μ_t a = 0.2 × 5 mm（示意值）
cases = {}
for name, C, mu, soft in (("single", single, MU_JAW, None), ("soft", single, MU_JAW, MU_T_A), ("flat", jaw_contacts("flat"), MU_JAW, None),
                          ("V", jaw_contacts("V"), MU_JAW, None), ("flat0", jaw_contacts("flat"), 0.0, None), ("V0", jaw_contacts("V"), 0.0, None)):
    W = contact_wrenches(C, mu, k=8, scale=r, soft=soft)
    fc, s = force_closure(W)
    cases[name] = (fc, ferrari_canny(W) if fc else 0.0, np.linalg.matrix_rank(W, 1e-10))
assert not cases["single"][0] and cases["soft"][0] and cases["flat"][0] and cases["V"][0] and not cases["flat0"][0] and not cases["V0"][0]

# ---------------------------------------------------------------- (3) 上下料动作中的最小夹紧力
ch = ur_chain()
thA, thB, T_move = cell_move()
ts = np.linspace(0, T_move, 81)
F_flat, F_v, S_flat, S_v, F_in = [], [], [], [], []
for t in ts:
    q, qd, qdd = quintic(thA, thB, T_move, t)
    V, Vd = hand_motion(ch, q, qd, qdd)
    V0, Vd0 = hand_motion(ch, q, np.zeros(6), np.zeros(6))          # 同一姿态静止时（只有重力）
    w, w0 = blank_wrench(V, Vd), blank_wrench(V0, Vd0)
    F_flat.append(min_grip(jaw_contacts("flat"), w)[0])
    F_v.append(min_grip(jaw_contacts("V"), w)[0])
    S_flat.append(min_grip(jaw_contacts("flat"), w0)[0])
    S_v.append(min_grip(jaw_contacts("V"), w0)[0])
    F_in.append(float(np.linalg.norm((w - w0)[3:])))                  # 惯性力的大小
F_flat, F_v, S_flat, S_v = np.array(F_flat), np.array(F_v), np.array(S_flat), np.array(S_v)
up_flat, up_v = F_flat / S_flat - 1, F_v / S_v - 1
iu = int(np.argmax(np.abs(up_flat)))
F_in_max = max(F_in) / (blank_wrench(*hand_motion(ch, thA, np.zeros(6), np.zeros(6)))[5])
iF, iV = int(np.argmax(F_flat)), int(np.argmax(F_v))
# 静止时（A、B 两点）
VA, VdA = hand_motion(ch, thA, np.zeros(6), np.zeros(6))
VB, VdB = hand_motion(ch, thB, np.zeros(6), np.zeros(6))
wA, wB = blank_wrench(VA, VdA), blank_wrench(VB, VdB)
FA_flat, FB_flat = min_grip(jaw_contacts("flat"), wA)[0], min_grip(jaw_contacts("flat"), wB)[0]
FA_v, FB_v = min_grip(jaw_contacts("V"), wA)[0], min_grip(jaw_contacts("V"), wB)[0]
FB_flat_eq = min_grip(jaw_contacts("flat"), wB, equal_ends=True)[0]
# 惯性的影响：动作中的最大值比两端静止时的较大值大多少
inert_flat = F_flat.max() / max(FA_flat, FB_flat) - 1
inert_v = F_v.max() / max(FA_v, FB_v) - 1
# B 点平口夹爪：线性规划给出的两端法向力（每个指）
_, fB = min_grip(jaw_contacts("flat"), wB)
CB = jaw_contacts("flat")
nB = [float(fB[i] @ CB[i][1]) for i in range(len(CB))]
N_near = max(nB[0], nB[1])                           # 靠近质心一端（z_h = −PAD_HALF）
N_far = min(nB[0], nB[1])
# A 点 V 形夹爪：线性规划的闭式（斜面上沿圆周方向的摩擦取对夹紧有利的方向）
m_b = 2.8
F_v_lp = m_b * 9.81 * math.sqrt(math.cos(math.pi / 4) ** 2 - MU_JAW ** 2 * math.sin(math.pi / 4) ** 2) / (2 * MU_JAW)
assert abs(F_v_lp / FA_v - 1) < 2e-3

# 习题 27.4.4：μ = 0.1 时 B 点 V 形夹爪、平口夹爪的最小夹紧力
FB_v01 = min_grip(jaw_contacts("V"), wB, mu=0.1)[0]
FB_flat01 = min_grip(jaw_contacts("flat"), wB, mu=0.1)[0]

out(FB_v01=FB_v01, FB_flat01=FB_flat01, width_mm=WIDTH * 1e3, mu1=MU1, delta_max_mm=delta_max * 1e3, delta_lp_mm=delta_lp * 1e3,
    fc_single=cases["single"][0], rank_single=cases["single"][2], eps_soft=cases["soft"][1], eps_flat=cases["flat"][1], eps_v=cases["V"][1],
    rank_flat0=cases["flat0"][2], rank_v0=cases["V0"][2], mut_a_mm=MU_T_A * 1e3,
    T_move=T_move, F_flat_max=F_flat.max(), t_flat_max=ts[iF], F_v_max=F_v.max(), t_v_max=ts[iV],
    FA_flat=FA_flat, FB_flat=FB_flat, FA_v=FA_v, FB_v=FB_v, FB_flat_eq=FB_flat_eq, inert_flat=inert_flat * 100, inert_v=inert_v * 100,
    ratio_B=FB_flat_eq / FB_v, ratio_B_lp=FB_flat / FB_v, N_near=N_near, N_far=N_far, F_v_lp=F_v_lp, up_flat=up_flat[iu] * 100, t_up=ts[iu], up_v_min=up_v.min() * 100,
    up_v_max=up_v.max() * 100, F_in_max=F_in_max * 100)
