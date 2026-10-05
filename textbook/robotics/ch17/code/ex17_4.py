"""17.4 节：七轴 Panda 实例。

数字工厂减速器车间的协作工位：Panda 把齿轮从 A = (0.40, 0.35, 0.30) m 搬到 B = (0.40, −0.35, 0.30) m，手竖直向下
（姿态同 ready），3 s 走直线，位置按余弦规律过渡。工人的手（看作半径 0.06 m 的球）在前 1.8 s 从 C0 = (−0.45, 0.35, 0.60) m
伸到 C1 = (−0.05, 0.12, 0.60) m，然后停住。要求：末端轨迹不变；手臂离工人的手至少 0.10 m；关节不超限；关节速度不超过上限。

(1) 目标位姿 A 的自运动闭曲线：长度、限位以内的比例；以 θ3 作冗余参数时，θ3 沿闭曲线的极值点（c3 = 0）个数——在这些点 θ3 不能
    唯一地确定形态。
(2) 四种做法：
    S0：锁住关节 3（θ3 = 0），Panda 成为六轴臂，逆解唯一，θ̇ = J⁻¹V；
    S1：七轴，取离 ready 最近的起始形态，θ̇ 取最小范数解；
    S2：七轴，同一起始形态，三层优先级：末端位姿 > 离开工人的手 > 避限位（式 (15.4.6) 的 H）；
    S3：七轴，先沿 A 的自运动闭曲线挑选起始形态（全局），再用 S2 的控制器（局部）。
    比较：最小距离、关节限位余量、可操作度、关节速度与上限之比、末端误差。
"""
import math

import numpy as np

from _red import (PA_HI, PA_LO, PA_QDMAX, PA_READY, joint_mid_cost, lim_margin, manip, null_vector, pa_fk, pa_jg, pa_js,
                  pa_points, pa_trace, pinv_rows, pose_error_g, pose_error_s, rot, seg_dist, wrap)
from bookout import out, tex

deg = math.degrees
TW = 2 * math.pi
R_DOWN = pa_fk(PA_READY)[:3, :3]
A_ = np.array([0.40, 0.35, 0.30])
B_ = np.array([0.40, -0.35, 0.30])
C0, C1 = np.array([-0.45, 0.35, 0.60]), np.array([-0.05, 0.12, 0.60])
RAD = 0.06
D_SAFE, D_ACT = 0.10, 0.14
TT = 3.0
KP, K_D, LAM_O, KH = 5.0, 3.0, 0.03, 2.0
SEGLINK = [0, 3, 3, 4, 4, 6, 7]


def pose(p):
    T = np.eye(4)
    T[:3, :3] = R_DOWN
    T[:3, 3] = p
    return T


def ik(Td, q, fixed=None):
    """数值逆解（15.1 节的牛顿法，伪逆）；fixed 为锁住的关节号（从 0 数），它不参与迭代。"""
    q = np.array(q, float)
    free = [i for i in range(7) if i != fixed]
    for _ in range(100):
        e = pose_error_s(pa_fk(q), Td)
        if np.linalg.norm(e) < 1e-13:
            return q
        J = pa_js(q)[:, free]
        q[free] += np.linalg.lstsq(J, e, rcond=None)[0]
    raise RuntimeError("逆解不收敛")


def into(q):
    return PA_LO + np.mod(q - PA_LO, TW)


def human(t):
    """工人的手：前 0.6 TT 内从 C0 移到 C1（余弦过渡），然后停住。返回位置与速度。"""
    Th = 0.6 * TT
    if t >= Th:
        return C1.copy(), np.zeros(3)
    s = (1 - math.cos(math.pi * t / Th)) / 2
    sd = math.pi / Th * math.sin(math.pi * t / Th) / 2
    return C0 + s * (C1 - C0), sd * (C1 - C0)


def closest_arm(q, c):
    P_ = pa_points(q)
    best = (1e9, None, None)
    for i in range(1, 7):
        d, x, _ = seg_dist(c, P_[i], P_[i + 1])
        if d < best[0]:
            best = (d, x, i)
    return best


def point_jac(q, x, k):
    Js = pa_js(q)
    Jx = np.zeros((3, 7))
    for i in range(k):
        Jx[:, i] = Js[3:, i] + np.cross(Js[:3, i], x)
    return Jx


def run(q0, mode, dt=0.004):
    """mode：'six'（锁关节 3）、'min'（最小范数）、'pri'（三层优先级）。返回逐步记录与终了关节角。"""
    q, rec = np.array(q0, float), []
    n = int(round(TT / dt))
    for i in range(n + 1):
        t = i * dt
        s = (1 - math.cos(math.pi * t / TT)) / 2
        sd = math.pi / TT * math.sin(math.pi * t / TT) / 2
        Td = pose(A_ + s * (B_ - A_))
        V = np.r_[0, 0, 0, sd * (B_ - A_)]
        e = pose_error_g(pa_fk(q), Td)
        J = pa_jg(q)
        c, cd = human(t)
        d, x, k = closest_arm(q, c)
        d -= RAD
        if mode == "six":
            Jr = np.delete(J, 2, axis=1)
            qd = np.insert(np.linalg.solve(Jr, V + KP * e), 2, 0.0)
            w = abs(np.linalg.det(Jr))
        else:
            Jp = pinv_rows(J)
            N = np.eye(7) - Jp @ J
            qd = Jp @ (V + KP * e)
            w = manip(J)
            if mode == "pri":
                N2 = N
                if d < D_ACT:                                   # 第二层：离开工人的手（一维）
                    u = (x - c) / np.linalg.norm(x - c)
                    a = u @ point_jac(q, x, SEGLINK[k])
                    A1 = (a @ N)[None, :]
                    G = A1.T / (A1 @ A1.T + LAM_O ** 2)
                    qd = qd + G @ (np.array([u @ cd + K_D * (D_ACT - d)]) - a @ qd)
                    N2 = N - G @ A1                              # 前两层的零空间（阻尼形式，近似）
                _, gH = joint_mid_cost(q, PA_LO, PA_HI)          # 第三层：避限位
                qd = qd - N2 @ (KH * gH)
        rec.append((t, d, float(lim_margin(into(q) if mode != "six" else q, PA_LO, PA_HI).min()), w,
                    float(np.abs(qd / PA_QDMAX).max()), float(np.linalg.norm(e[3:])), *q))
        if i < n:
            q = q + dt * qd
    return np.array(rec)


def summary(R):
    return dict(d=float(R[:, 1].min()), mg=float(R[:, 2].min()), w=float(R[:, 3].min()), v=float(R[:, 4].max()), e=float(R[:, 5].max()))


# ---------------------------------------------------------------- 起始形态
qA = ik(pose(A_), PA_READY)                                          # 离 ready 最近（从 ready 出发的牛顿迭代）
qA6 = ik(pose(A_), np.r_[qA[:2], 0.0, qA[3:]], fixed=2)              # 锁住关节 3 = 0 的六轴解
assert abs(qA6[2]) < 1e-15 and np.all(lim_margin(qA6, PA_LO, PA_HI) > 0)

# (1) A 的自运动闭曲线
LA = pa_trace(qA, pose(A_), h=0.01)
nA = len(LA)
LAi = np.array([into(q) for q in LA])
inl = np.all(LAi <= PA_HI, axis=1)
c3 = np.array([null_vector(pa_js(q))[2] for q in LA])
n_c3 = int(np.sum(np.sign(c3) != np.sign(np.roll(c3, 1))))           # θ3 的极值点个数
t3_in = np.degrees([LAi[inl, 2].min(), LAi[inl, 2].max()])
net3A = int(round((LA[-1, 2] + 0.01 * null_vector(pa_js(LA[-1]))[2] / np.linalg.norm(null_vector(pa_js(LA[-1]))) - LA[0, 2]) / TW))
assert n_c3 == 0 and abs(net3A) == 1                                 # θ3 沿 A 的闭曲线单调，正好转一圈：可作全局参数
LR = pa_trace(PA_READY, pa_fk(PA_READY), h=0.01)                     # 对照：17.2 节 ready 姿态的闭曲线
c3R = np.array([null_vector(pa_js(q))[2] for q in LR])
n_c3R = int(np.sum(np.sign(c3R) != np.sign(np.roll(c3R, 1))))
t3R = np.degrees([LR[:, 2].min(), LR[:, 2].max()])
assert n_c3R == 2
# 定理 17.4.1：θ3 取极值处 c3 = 0，锁住关节 3 得到的六轴臂奇异（删去第 3 列的 6×6 雅可比行列式为零）
ext = [k for k in range(len(LR)) if np.sign(c3R[k]) != np.sign(c3R[k - 1])]
ext_det = max(abs(np.linalg.det(np.delete(pa_js(LR[k]), 2, axis=1))) for k in ext)      # 相邻两点中前一点，h = 0.01 rad
ext_t3 = [deg(LR[k, 2]) for k in ext]
det_ready6 = abs(np.linalg.det(np.delete(pa_js(PA_READY), 2, axis=1)))
assert ext_det < 0.02 * det_ready6

# (2) 全局挑选：在限位以内的点中每隔 0.15 rad 取一个起始形态，用最小范数解粗算一遍（dt = 0.02 s）
cand = []
for k in range(0, nA, 15):
    if not inl[k]:
        continue
    R = run(LAi[k], "min", dt=0.02)
    sm = summary(R)
    cand.append((k, sm["d"], sm["mg"], sm["w"], sm["v"], deg(LAi[k, 2])))
cand = np.array(cand)
ok = (cand[:, 1] > D_SAFE + 0.05) & (cand[:, 2] > 0.05) & (cand[:, 4] < 0.8)
assert ok.any()
k_best = int(cand[ok][np.argmax(cand[ok][:, 3]), 0])                # 满足要求的里面，取最小可操作度最大的
q3 = LAi[k_best]
n_cand, n_ok = len(cand), int(ok.sum())

R0, R1, R2, R3 = run(qA6, "six"), run(qA, "min"), run(qA, "pri"), run(q3, "pri")
S = [summary(R) for R in (R0, R1, R2, R3)]
assert S[1]["d"] < D_SAFE and S[0]["d"] < D_SAFE                    # 六轴与最小范数解：离工人的手太近
assert S[3]["d"] > D_SAFE and S[3]["mg"] > 0 and S[3]["v"] < 1      # 全局 + 局部：全部满足
assert max(s["e"] for s in S) < 1e-3
w_ready = manip(pa_jg(PA_READY))

out(qA=tex(np.degrees(qA), 1), qA6=tex(np.degrees(qA6), 1), q3=tex(np.degrees(q3), 1),
    lenA=nA * 0.01, fracA=float(inl.mean()) * 100, n_c3=n_c3, n_c3R=n_c3R, t3R_lo=t3R[0], t3R_hi=t3R[1], t3_lo=t3_in[0], t3_hi=t3_in[1],
    n_cand=n_cand, n_okc=n_ok, t3_best=deg(q3[2]),
    **{f"{k}{i}": v for i, s in enumerate(S) for k, v in s.items()},
    qd14=PA_QDMAX[0], qd57=PA_QDMAX[4], ext_det=ext_det, det_ready6=det_ready6, w_ready=w_ready, d_safe=D_SAFE, d_act=D_ACT)
