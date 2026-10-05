"""18.1 节：并联与串联对比。

平面五杆机器人（两台电机在 (∓0.15, 0) m，主动杆 0.20 m，从动杆 0.30 m，同 11.2 节）与同样杆长的 2R 串联臂
（基座在原点，大臂 0.20 m、小臂 0.30 m）。
(1) 算例 18.1.1：P0 = (0, 0.35) m 的逆解与正解。五杆按支链分别求逆解（肘部朝外），再由两圆求交求正解，
    两种装配模式；2R 臂按 14.2 节求逆解。
(2) 算例 18.1.2：工作空间。2R 臂是两个圆的“和”（圆环，面积有公式），五杆是两条支链工作空间的“交”；
    再限定一种装配模式和一种工作模式，以及局部条件指标不低于 0.3 的部分。网格 2.5 mm。
(3) 算例 18.1.3：P0 处的速度关系 A ẋ = B θ̇ 与差商核对；编码器误差 0.01° 引起的末端误差；关节扭转刚度
    k = 5000 N·m/rad 时的柔度；末端受 20 N 力时的电机力矩。在两者条件都不太差（LCI ≥ 0.3）的区域内比较误差放大系数。
(4) 格吕布勒公式的并联形式 (18.1.1)：Stewart、Delta 与五杆。
"""
import math

import numpy as np

from _ch18 import (ARM2, FIVE, SIG_OUT, arm2_fk, arm2_ik, arm2_J, five_AB, five_elbows, five_fk, five_ik, five_leg_ik,
                   five_motors)
from bookout import T, out

deg = math.degrees
c, l1, l2 = FIVE["c"], FIVE["l1"], FIVE["l2"]
L1, L2 = ARM2["L1"], ARM2["L2"]

# ---------------------------------------------------------------- (1) 逆解与正解
P0 = np.array([0.0, 0.35])
th_p = five_ik(P0)                                   # 五杆，肘部朝外
th_all = [five_ik(P0, (s1, s2)) for s1 in (1, -1) for s2 in (1, -1)]      # 四种工作模式
assert all(t is not None for t in th_all)
for t in th_all:                                     # 每一组都满足两条闭环条件 (18.1.2)
    B1, B2 = five_elbows(t)
    assert abs(np.linalg.norm(P0 - B1) - l2) < 1e-12 and abs(np.linalg.norm(P0 - B2) - l2) < 1e-12
Pup, Pdn = five_fk(th_p, +1), five_fk(th_p, -1)
assert np.abs(Pup - P0).max() < 1e-12                # 正解（上方的装配模式）回到 P0
B1, B2 = five_elbows(th_p)
assert abs(np.linalg.norm(Pdn - B1) - l2) < 1e-12 and abs(np.linalg.norm(Pdn - B2) - l2) < 1e-12
th_s = arm2_ik(P0, +1)
assert np.abs(arm2_fk(th_s) - P0).max() < 1e-12

# ---------------------------------------------------------------- (2) 工作空间
h = 0.0025
g = np.arange(-0.7, 0.7 + h / 2, h)
X, Y = np.meshgrid(g, g)
r0 = np.hypot(X, Y)
ser = (r0 >= L2 - L1) & (r0 <= L1 + L2)
A_ser = ser.sum() * h * h
A_ser_formula = math.pi * ((L1 + L2) ** 2 - (L2 - L1) ** 2)
assert abs(A_ser - A_ser_formula) / A_ser_formula < 0.01
r1, r2 = np.hypot(X + c, Y), np.hypot(X - c, Y)
par = (r1 >= l2 - l1) & (r1 <= l1 + l2) & (r2 >= l2 - l1) & (r2 <= l1 + l2)
A_par = par.sum() * h * h
# 用逆解逐点判断（与几何判断应一致）：五杆每条支链有解 ⇔ 点到电机的距离在 [l2 − l1, l1 + l2] 内
idx = np.argwhere(par)[:: 97]
for i, j in idx:
    assert five_ik(np.array([X[i, j], Y[i, j]])) is not None

# 一种装配模式（上方）+ 一种工作模式（肘部朝外），以及 LCI ≥ 0.3 的部分
h2 = 0.005
g2 = np.arange(-0.6, 0.6 + h2 / 2, h2)
LCI_MIN = 0.3
A_mode = A_par_good = A_ser_good = 0.0
amp_s, amp_p, ratio = [], [], []
for x in g2:
    for y in g2:
        P = np.array([x, y])
        ts = arm2_ik(P, +1)
        Js = None
        if ts is not None:
            Js = arm2_J(ts)
            ss = np.linalg.svd(Js)[1]
            if ss[1] / ss[0] >= LCI_MIN:
                A_ser_good += h2 * h2
                amp_s.append(np.abs(Js).sum(1).max())
        tp = five_ik(P)
        if tp is None:
            continue
        Q = five_fk(tp, +1)
        if Q is None or np.abs(Q - P).max() > 1e-9:
            continue
        A_mode += h2 * h2
        A, B = five_AB(P, tp)
        Jp = np.linalg.solve(A, B)
        sp = np.linalg.svd(Jp)[1]
        if sp[1] / sp[0] >= LCI_MIN:
            A_par_good += h2 * h2
            amp_p.append(np.abs(Jp).sum(1).max())
            if Js is not None and np.linalg.svd(Js)[1][1] / np.linalg.svd(Js)[1][0] >= LCI_MIN:
                ratio.append(np.abs(Jp).sum(1).max() / np.abs(Js).sum(1).max())
amp_s, amp_p, ratio = map(np.array, (amp_s, amp_p, ratio))

# ---------------------------------------------------------------- (3) P0 处的速度、误差、刚度
A, B = five_AB(P0, th_p)
Jp = np.linalg.solve(A, B)
dh = 1e-7                                            # 差商核对：电机转一点，按正解看 P 动多少
Jfd = np.column_stack([(five_fk(th_p + dh * np.eye(2)[i], +1) - five_fk(th_p - dh * np.eye(2)[i], +1)) / (2 * dh) for i in range(2)])
assert np.abs(Jfd - Jp).max() < 1e-7
Js = arm2_J(th_s)
Jsfd = np.column_stack([(arm2_fk(th_s + dh * np.eye(2)[i]) - arm2_fk(th_s - dh * np.eye(2)[i])) / (2 * dh) for i in range(2)])
assert np.abs(Jsfd - Js).max() < 1e-7
sv_p, sv_s = np.linalg.svd(Jp)[1], np.linalg.svd(Js)[1]

eps = math.radians(0.01)                             # 编码器误差 ±0.01°
corners = [np.array([a, b]) * eps for a in (-1, 1) for b in (-1, 1)]
err_s = max(np.linalg.norm(Js @ d) for d in corners)
err_p = max(np.linalg.norm(Jp @ d) for d in corners)
# 与“两台电机各自随机误差”的蒙特卡罗比较：上界确实是上界
rng = np.random.default_rng(181)
mc = rng.uniform(-eps, eps, (20000, 2))
assert np.linalg.norm(mc @ Js.T, axis=1).max() <= err_s + 1e-15
assert np.linalg.norm(mc @ Jp.T, axis=1).max() <= err_p + 1e-15

k_joint = 5000.0                                     # N·m/rad
Cs, Cp = Js @ Js.T / k_joint, Jp @ Jp.T / k_joint   # 柔度矩阵 (16.5.9)
cs_max, cp_max = np.linalg.eigvalsh(Cs).max(), np.linalg.eigvalsh(Cp).max()
cs_min, cp_min = np.linalg.eigvalsh(Cs).min(), np.linalg.eigvalsh(Cp).min()
f20 = np.array([0.0, -20.0])                         # 末端对外施加的力（竖直向下 20 N）
tau_s, tau_p = Js.T @ f20, Jp.T @ f20                # τ = Jᵀ f
assert abs(tau_s[0]) < 1e-12                         # P0 在关节 1 正上方：竖直力对关节 1 没有力臂
tau_s[0] = 0.0                                       # 去掉舍入误差，避免排成“−0.00”
# 静力核对：五杆的电机力矩，用虚功 τ·δθ = f·δx 的差商
for i in range(2):
    d = np.eye(2)[i] * 1e-7
    dx = five_fk(th_p + d, +1) - five_fk(th_p - d, +1)
    assert abs(f20 @ dx / 2e-7 - tau_p[i]) < 1e-5
dx_s = Cs @ f20
dx_p = Cp @ f20

# ---------------------------------------------------------------- (4) 并联形式的格吕布勒公式 (18.1.1)：M = 6 − Σ c_i
def par_dof(F, m=6):
    return m - sum(m - f for f in F)


M_st = par_dof([6] * 6)                              # UPS：2 + 1 + 3
M_delta = par_dof([5] * 3)                           # R + 平行四边形（去掉两根杆的空转后为 4）
assert (M_st, M_delta) == (6, 3)

fmt = lambda t: f"({deg(t[0]):.2f}°, {deg(t[1]):.2f}°)"
out(th_p=fmt(th_p), th_s=fmt(th_s), th_p1=deg(th_p[0]), th_p2=deg(th_p[1]), th_s1=deg(th_s[0]), th_s2=deg(th_s[1]),
    pdn_y=Pdn[1] * 1000, n_modes=len(th_all),
    A_ser=A_ser, A_ser_f=A_ser_formula, A_par=A_par, A_mode=A_mode, A_par_good=A_par_good, A_ser_good=A_ser_good,
    par_pct=100 * A_par / A_ser, good_pct=100 * A_par_good / A_ser_good,
    amp_s_med=np.median(amp_s), amp_p_med=np.median(amp_p), amp_s_min=amp_s.min(), amp_p_min=amp_p.min(),
    amp_s_max=amp_s.max(), amp_p_max=amp_p.max(), ratio_med=np.median(ratio), ratio_lt1=100 * (ratio < 1).mean(),
    J_p=Jp, J_s=Js, A11=A[0, 0], A12=A[0, 1], A21=A[1, 0], A22=A[1, 1], B11=B[0, 0], B22=B[1, 1],
    sv_p1=sv_p[0], sv_p2=sv_p[1], sv_s1=sv_s[0], sv_s2=sv_s[1],
    err_s=err_s * 1000, err_p=err_p * 1000, cs_max=cs_max * 1e6, cp_max=cp_max * 1e6, cs_min=cs_min * 1e6, cp_min=cp_min * 1e6,
    tau_s1=tau_s[0], tau_s2=tau_s[1], tau_p1=tau_p[0], tau_p2=tau_p[1],
    dx_s=np.linalg.norm(dx_s) * 1e6, dx_p=np.linalg.norm(dx_p) * 1e6,
    M_st=M_st, M_delta=M_delta,
    Jp_tex=r"\begin{pmatrix} %.4f & %.4f \\ %.4f & %.4f \end{pmatrix}" % tuple(Jp.ravel()),
    Js_tex=r"\begin{pmatrix} %.4f & %.4f \\ %.4f & %.4f \end{pmatrix}" % tuple(Js.ravel()))
