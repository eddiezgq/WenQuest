"""24.2 节的计算：两连杆臂的完整推导。

(1) 程序 24.2.1 的符号部分：用 SymPy 从质心的位置写出动能、势能，按拉格朗日方程 (24.1.12) 求导，得到两个关节的力矩；
    与书中手推的结果 (24.2.6)～(24.2.9) 逐项相减，化简为零；再从 M(φ) 按式 (24.3.4) 求克里斯托费尔符号，验证 c = C(φ, φ̇)φ̇。
    质心可以不在两关节的连线上（s_i ≠ 0），所以这里的结果对任意平面两连杆臂成立。
(2) 数值类 Planar2（_ch24.py）与符号结果在随机状态下比较。
(3) 表 24.2.1：把 UR5e 的关节 2、3 看作平面两连杆臂（关节 1 = 0，关节 4、5、6 锁在 (−90°, 0, 0)，即书中各章常用的手腕姿态），
    从书中网页版 UR5e 模型算出两根等效连杆的参数，空手和装夹爪 + SH-301 毛坯（算例 23.2.2）两种情况。
    与 MuJoCo 核对：六关节模型质量矩阵的 2×2 子块、偏置力 qfrc_bias（只有关节 2、3 运动时）；
    关节 1、4、5、6 焊死后的两自由度模型（ur_weld_xml）的逆动力学 mj_inverse。
(4) 算例 24.2.2：装毛坯后，关节 2、3 从 (−120°, 120°) 用五次多项式 (22.1.8) 在 T = 1 s 内走到 (−30°, 30°)（小臂始终水平，
    毛坯平着向前、向下送出）。三类力矩（惯性、速度、重力）的峰值；总力矩的峰值；与 MuJoCo 的逆动力学逐点比较；
    关节力矩不超过模型的上限 150 N·m 时最短的 T（二分法）；同一动作空手时的峰值。
(5) 生活中的例子（示意值）：在水平面内甩手臂，肘关节放松时会被“甩开”：保持肘弯 90° 所需的肘关节力矩。
(6) 习题答案。
"""
import math

import numpy as np
import sympy as sp

from _ch24 import (G0, Planar2, mj_load, mjcf_text, parse_links, payload_parts, payload_xml, planar_params, quintic, ur_to_planar,
                   ur_weld_xml)
from bookout import out

# ---------------------------------------------------------------- (1) SymPy：从 K、U 到运动方程
t = sp.symbols("t")
a1, m1, m2, r1, s1, r2, s2, I1, I2, g = sp.symbols("a_1 m_1 m_2 r_1 s_1 r_2 s_2 I_1 I_2 g", real=True)
f1, f2 = sp.Function("phi1")(t), sp.Function("phi2")(t)
R = lambda a: sp.Matrix([[sp.cos(a), -sp.sin(a)], [sp.sin(a), sp.cos(a)]])
pc1 = R(f1) * sp.Matrix([r1, s1])                                     # 连杆 1 质心
pc2 = sp.Matrix([a1 * sp.cos(f1), a1 * sp.sin(f1)]) + R(f1 + f2) * sp.Matrix([r2, s2])
v1, v2 = pc1.diff(t), pc2.diff(t)
w1, w2 = f1.diff(t), f1.diff(t) + f2.diff(t)
K = sp.Rational(1, 2) * (m1 * v1.dot(v1) + I1 * w1 ** 2 + m2 * v2.dot(v2) + I2 * w2 ** 2)
U = g * (m1 * pc1[1] + m2 * pc2[1])
L = K - U
tau_sym = [sp.simplify(sp.diff(sp.diff(L, q.diff(t)), t) - sp.diff(L, q)) for q in (f1, f2)]

# 书中手推的结果：J_i = I_i + m_i(r_i² + s_i²)，β = m₂a₁(r₂ cos φ₂ − s₂ sin φ₂)，h = m₂a₁(r₂ sin φ₂ + s₂ cos φ₂)
J1, J2 = I1 + m1 * (r1 ** 2 + s1 ** 2), I2 + m2 * (r2 ** 2 + s2 ** 2)
beta = m2 * a1 * (r2 * sp.cos(f2) - s2 * sp.sin(f2))
h = m2 * a1 * (r2 * sp.sin(f2) + s2 * sp.cos(f2))
d1, d2 = f1.diff(t), f2.diff(t)
dd1, dd2 = f1.diff(t, 2), f2.diff(t, 2)
Mh = sp.Matrix([[J1 + J2 + m2 * a1 ** 2 + 2 * beta, J2 + beta], [J2 + beta, J2]])
ch = sp.Matrix([-h * (2 * d1 * d2 + d2 ** 2), h * d1 ** 2])
gh = sp.Matrix([m1 * g * (r1 * sp.cos(f1) - s1 * sp.sin(f1)) + m2 * g * (a1 * sp.cos(f1) + r2 * sp.cos(f1 + f2) - s2 * sp.sin(f1 + f2)),
                m2 * g * (r2 * sp.cos(f1 + f2) - s2 * sp.sin(f1 + f2))])
tau_hand = Mh * sp.Matrix([dd1, dd2]) + ch + gh
diff_sym = [sp.simplify(sp.expand_trig(tau_sym[i] - tau_hand[i])) for i in range(2)]
assert diff_sym == [0, 0]
assert sp.simplify(h + sp.diff(beta, f2)) == 0                         # h = −dβ/dφ₂
# 动能就是 ½ φ̇ᵀ M φ̇，势能的梯度就是 g
assert sp.simplify(sp.expand(K - sp.Rational(1, 2) * (sp.Matrix([d1, d2]).T * Mh * sp.Matrix([d1, d2]))[0])) == 0
assert all(sp.simplify(sp.diff(U, q) - gh[i]) == 0 for i, q in enumerate((f1, f2)))
# 克里斯托费尔符号 (24.3.4)、(24.3.5) 给出的 C(φ, φ̇)：c = C φ̇，且 Ṁ − 2C 反对称
qs = [f1, f2]
Gam = [[[sp.Rational(1, 2) * (sp.diff(Mh[i, j], qs[k]) + sp.diff(Mh[i, k], qs[j]) - sp.diff(Mh[j, k], qs[i])) for k in range(2)]
        for j in range(2)] for i in range(2)]
qd = [d1, d2]
Cm = sp.Matrix(2, 2, lambda i, j: sum(Gam[i][j][k] * qd[k] for k in range(2)))
assert sp.simplify(Cm * sp.Matrix(qd) - ch) == sp.zeros(2, 1)
Nm = sp.simplify(Mh.diff(t) - 2 * Cm)
assert sp.simplify(Nm + Nm.T) == sp.zeros(2, 2)
# 规模：展开以后两个关节力矩表达式中的项数（说明为什么六轴不手推）
n_terms = [len(sp.Add.make_args(sp.expand(tau_sym[i]))) for i in range(2)]

# ---------------------------------------------------------------- (2) 数值类与符号结果比较
syms = (a1, m1, m2, r1, s1, r2, s2, I1, I2, g)
ph1, ph2, w1s, w2s, a1s, a2s = sp.symbols("ph1 ph2 w1 w2 al1 al2")
subs = {dd1: a1s, dd2: a2s}
subs2 = {d1: w1s, d2: w2s}
subs3 = {f1: ph1, f2: ph2}
tau_num = sp.lambdify(syms + (ph1, ph2, w1s, w2s, a1s, a2s),
                      [e.subs(subs).subs(subs2).subs(subs3) for e in tau_sym], "numpy")
rng = np.random.default_rng(242)
err_cls = 0.0
for _ in range(50):
    par = rng.uniform(0.1, 2.0, 10)
    par[4] = rng.uniform(-0.3, 0.3)
    par[6] = rng.uniform(-0.3, 0.3)
    A1, M1_, M2_, R1, S1, R2, S2, II1, II2, GG = par
    P = Planar2(A1, M1_, R1, S1, II1 + M1_ * (R1 ** 2 + S1 ** 2), M2_, R2, S2, II2 + M2_ * (R2 ** 2 + S2 ** 2), g=GG)
    x = rng.normal(size=6)
    err_cls = max(err_cls, float(np.abs(np.array(tau_num(*par, *x)) - P.tau(x[:2], x[2:4], x[4:])).max()))
assert err_cls < 1e-11

# ---------------------------------------------------------------- (3) 表 24.2.1：UR5e 的关节 2、3
links = parse_links(mjcf_text())
WRIST = (-math.pi / 2, 0.0, 0.0)
P0 = planar_params(links, WRIST)                                       # 空手
pl = payload_parts()
PL = planar_params(links, WRIST, payload=pl)                           # 装夹爪 + 毛坯
for P in (P0, PL):
    assert abs(P.s1) < 1e-14 and abs(P.s2) < 1e-14                     # 这个手腕姿态下两个质心都在关节连线上
assert abs(P0.a1 - 0.425) < 1e-12

import mujoco                                                           # noqa: E402

err_blk = err_bias = 0.0
for tool, P in (("", P0), (payload_xml(*pl), PL)):
    mj, m, d = mj_load(mjcf_text(tool=tool))
    for _ in range(20):
        th2, th3 = rng.uniform(-math.pi, math.pi, 2)
        v = rng.normal(size=2)
        d.qpos[:] = [rng.uniform(-math.pi, math.pi), th2, th3, *WRIST]
        d.qvel[:] = 0
        d.qvel[1:3] = v
        mujoco.mj_forward(m, d)
        Mf = np.zeros((6, 6))
        mujoco.mj_fullM(m, d, Mf)
        p, pd = ur_to_planar(th2, th3), -v
        err_blk = max(err_blk, float(np.abs(Mf[1:3, 1:3] - P.M(p)).max()))
        err_bias = max(err_bias, float(np.abs(-d.qfrc_bias[1:3] - (P.c(p, pd) + P.g(p))).max()))
assert err_blk < 1e-12 and err_bias < 1e-11

mjw, mw, dw = mj_load(ur_weld_xml(tool=payload_xml(*pl)))
assert mw.nv == 2
err_inv = 0.0
for _ in range(50):
    p, pd, pdd = rng.uniform(-3, 3, 2), rng.normal(size=2) * 2, rng.normal(size=2) * 5
    dw.qpos[:], dw.qvel[:], dw.qacc[:] = -p, -pd, -pdd
    mujoco.mj_inverse(mw, dw)
    err_inv = max(err_inv, float(np.abs(-dw.qfrc_inverse - PL.tau(p, pd, pdd)).max()))
assert err_inv < 1e-11

# ---------------------------------------------------------------- (4) 算例 24.2.2：把毛坯送向卡盘
QA, QB, T1 = (-120.0, 120.0), (-30.0, 30.0), 1.0
pa, pb = ur_to_planar(*np.radians(QA)), ur_to_planar(*np.radians(QB))
TAU_MAX = 150.0                                                        # 模型中关节 2、3 的力矩上限（forcerange），N·m
assert 'forcerange="-150 150"' in mjcf_text()


def breakdown(P, T, n=2001):
    ts = np.linspace(0, T, n)
    rows = []
    for tt in ts:
        q, qd, qdd = quintic(pa, pb, T, tt)
        rows.append(np.r_[P.M(q) @ qdd, P.c(q, qd), P.g(q)])
    return ts, np.array(rows)


ts, B = breakdown(PL, T1)
tot = B[:, 0:2] + B[:, 2:4] + B[:, 4:6]
pk_in, pk_vel, pk_g, pk_tot = (np.abs(B[:, 0:2]).max(0), np.abs(B[:, 2:4]).max(0), np.abs(B[:, 4:6]).max(0),
                               np.abs(tot).max(0))
i_pk = int(np.argmax(np.abs(tot[:, 0])))
t_pk1 = float(ts[i_pk])
g_at_pk = float(B[i_pk, 4])
share_g = g_at_pk / tot[i_pk, 0]
# 小臂始终水平：φ₁ + φ₂ = 0，连杆 2 只平动不转动
assert abs((pa[0] + pa[1])) < 1e-12 and abs(pb[0] + pb[1]) < 1e-12
# 峰值速度：五次多项式 1.875 Δ/T
vmax_deg = 1.875 * abs(QB[0] - QA[0]) / T1
VLIM = 180.0                                                           # UR5e 各关节的最大速度，°/s（厂家参数表）
T_vlim = 1.875 * abs(QB[0] - QA[0]) / VLIM
v_at_Tmin = 1.875 * abs(QB[0] - QA[0])  # 除以 T_min 见下
# 与 MuJoCo 的逆动力学逐点比较（UR5e 的符号：τ_UR = −τ）
err_traj = 0.0
for k in range(0, len(ts), 20):
    q, qd, qdd = quintic(pa, pb, T1, ts[k])
    dw.qpos[:], dw.qvel[:], dw.qacc[:] = -q, -qd, -qdd
    mujoco.mj_inverse(mw, dw)
    err_traj = max(err_traj, float(np.abs(-dw.qfrc_inverse - tot[k]).max()))
assert err_traj < 1e-10


def peak(P, T):
    _, Bx = breakdown(P, T, 1001)
    return float(np.abs(Bx[:, 0:2] + Bx[:, 2:4] + Bx[:, 4:6]).max())


lo, hi = 0.3, 1.0
assert peak(PL, lo) > TAU_MAX > peak(PL, hi)
for _ in range(40):
    mid = 0.5 * (lo + hi)
    lo, hi = (mid, hi) if peak(PL, mid) > TAU_MAX else (lo, mid)
T_min = hi
v_at_Tmin = v_at_Tmin / T_min
pk_empty = peak(P0, T1)
# 起点、终点静止，只有重力
g_start, g_end = PL.g(pa), PL.g(pb)
# 惯性项与 T² 成反比：T = T_min 时的惯性峰值
_, Bm = breakdown(PL, T_min)
pk_in_min = np.abs(Bm[:, 0:2]).max(0)

# ---------------------------------------------------------------- (5) 生活中的例子：甩手臂（示意值）
ma1, mm1, mr1, mm2, mr2, ml2 = 0.30, 2.1, 0.13, 1.6, 0.20, 0.42     # 上臂长、质量、质心；前臂连手的质量、质心、长度
mI2 = mm2 * (0.12) ** 2                                               # 前臂连手对质心的转动惯量（回转半径 0.12 m，示意值）
H = Planar2(ma1, mm1, mr1, 0.0, mm1 * ma1 ** 2 / 3, mm2, mr2, 0.0, mI2 + mm2 * mr2 ** 2, g=0.0)
w_sh = 10.0                                                           # 肩以 10 rad/s 匀速转动
tau_elbow = float(H.c(np.array([0.0, math.pi / 2]), np.array([w_sh, 0.0]))[1])     # 保持 φ₂ = 90° 不动所需的肘力矩（取负号前）
h_arm = H.hh(math.pi / 2)
assert abs(tau_elbow - h_arm * w_sh ** 2) < 1e-12
# 肘放松（τ₂ = 0）时，肘关节角加速度（肩匀速）：M₂₁·0 + M₂₂ φ̈₂ + h φ̇₁² = 0
acc_elbow = -h_arm * w_sh ** 2 / H.M(np.array([0, math.pi / 2]))[1, 1]

# ---------------------------------------------------------------- (6) 习题答案
# 24.2.3：均匀细杆两连杆（a = 0.5 m，m = 2 kg）在 φ = (0, 0) 静止时两关节的重力矩
Pr = Planar2(0.5, 2.0, 0.25, 0.0, 2.0 * 0.25 / 3, 2.0, 0.25, 0.0, 2.0 * 0.25 / 3)
gr = Pr.g(np.zeros(2))
# 24.2.4：算例 24.2.2 空手时 T 最短可到多少
lo, hi = 0.2, 1.0
for _ in range(40):
    mid = 0.5 * (lo + hi)
    lo, hi = (mid, hi) if peak(P0, mid) > TAU_MAX else (lo, mid)
T_min_empty = hi

out(n_terms1=n_terms[0], n_terms2=n_terms[1], err_cls=err_cls,
    a1=P0.a1, m1=P0.m1, r1=P0.r1, J1=P0.J1, m2=P0.m2, r2=P0.r2, J2=P0.J2,
    m2L=PL.m2, r2L=PL.r2, J2L=PL.J2, m_p=pl[0], arm=float(P0.arm[0]),
    M11z=float(P0.M(np.zeros(2))[0, 0]), M12z=float(P0.M(np.zeros(2))[0, 1]), M22z=float(P0.M(np.zeros(2))[1, 1]),
    M11L=float(PL.M(np.zeros(2))[0, 0]), hL=float(PL.hh(math.pi / 2)), betaL=float(PL.beta(0.0)),
    err_blk=err_blk, err_bias=err_bias, err_inv=err_inv,
    pk_in1=pk_in[0], pk_in2=pk_in[1], pk_vel1=pk_vel[0], pk_vel2=pk_vel[1], pk_g1=pk_g[0], pk_g2=pk_g[1],
    pk_tot1=pk_tot[0], pk_tot2=pk_tot[1], t_pk1=t_pk1, share_g=share_g, vmax_deg=vmax_deg, err_traj=err_traj,
    T_min=T_min, T_vlim=T_vlim, v_at_Tmin=v_at_Tmin, pk_empty=pk_empty, g_start1=g_start[0], g_start2=g_start[1], g_end1=g_end[0], g_end2=g_end[1],
    pk_in_min1=pk_in_min[0], ratio_in=(T1 / T_min) ** 2,
    tau_elbow=tau_elbow, h_arm=h_arm, acc_elbow=acc_elbow, acc_elbow_abs=abs(acc_elbow), J2_arm=H.J2, ma1=ma1, mm2=mm2, mr2=mr2,
    pk_in1_min=pk_in_min[0],
    gr1=gr[0], gr2=gr[1], T_min_empty=T_min_empty)
