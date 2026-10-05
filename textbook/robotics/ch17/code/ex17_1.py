"""17.1 节：冗余度。

(1) 算例 17.1.1：平面 3R 臂（0.425、0.392、0.1 m）只管末端位置（m = 2，r = 1）。对目标 A = (0.5, 0.3) m 与
    B = (0.75, 0.10) m，按工具朝向 φ 逐点求出全部解（腕点 w = p − L3(cos φ, sin φ)，再用 2R 臂的解析解），得到自运动流形：
    A 是两条互不相连的闭曲线（θ2 > 0、θ2 < 0 各一条），B 是一条闭曲线（肘上、肘下两支在 θ2 = 0 处连成一条）。
    核对定理 17.1.1：沿流形的切向与雅可比矩阵的零空间平行。目标到基座的距离 d 跨过 |L1 ± L2 ± L3| 时，闭曲线的条数改变。
(2) 算例 17.1.2：UR5e 装弯头焊枪（颈长 0.15 m，弯 45°，弯后 0.12 m），任务为枪尖位置与焊枪轴线方向（m = 5，r = 1）。
    θ* 处 5×6 任务雅可比的秩与零空间（广义叉积，17.2 节）；零空间就是“绕焊枪轴线转动”，与 J_s⁻¹ 乘以该轴的旋量一致。
    沿自运动从 θ* 出发，焊枪绕自身轴线能转的范围 [ψ_min, ψ_max]：两端都是肘部伸直（θ3 = 0），此时 det J_s = 0，ψ 的变化率为零（定理 17.1.2）。
"""
import math

import numpy as np

from _red import (PL, TH_STAR, UR_M, UR_S, act, exp6, geometric_jacobian, ik2r, inv, jacobian_space, jac_planar,
                  joints_planar, log_twist, logR, null_vector, skew, ur_fk, wrap)
from bookout import out, tex

deg = math.degrees
L = PL


# ---------------------------------------------------------------- (1) 平面 3R 臂的自运动流形
def branch(p, up, n=3600):
    """按 φ 扫描：返回 [(φ, θ1, θ2, θ3)]，够不着的 φ 跳过。up 为 θ2 > 0 的一支（第 14 章称为肘下）。"""
    out_ = []
    for phi in np.linspace(-math.pi, math.pi, n, endpoint=False):
        w = p - L[2] * np.array([math.cos(phi), math.sin(phi)])
        s = ik2r(w[0], w[1], L[0], L[1])
        if not s:
            continue
        t1, t2 = s[0] if up else s[1]
        out_.append((phi, t1, t2, wrap(phi - t1 - t2)))
    return np.array(out_)


def n_loops(d, n=7200):
    """目标在 (d, 0) 时自运动流形的闭曲线条数：φ 全周都够得着时为 2（肘上、肘下各一条），否则等于够得着的 φ 区间数。"""
    p = np.array([d, 0.0])
    ok = np.array([bool(ik2r(*(p - L[2] * np.array([math.cos(f), math.sin(f)])), L[0], L[1]))
                   for f in np.linspace(-math.pi, math.pi, n, endpoint=False)])
    if ok.all():
        return 2
    return int(np.sum(ok & ~np.roll(ok, 1)))


PA_ = np.array([0.5, 0.3])
PB_ = np.array([0.75, 0.10])
dA, dB = float(np.linalg.norm(PA_)), float(np.linalg.norm(PB_))
A_up, A_dn = branch(PA_, True), branch(PA_, False)
B_up, B_dn = branch(PB_, True), branch(PB_, False)
assert len(A_up) == 3600 and len(A_dn) == 3600                      # A：φ 全周都够得着，两条闭曲线
assert len(B_up) < 3600                                             # B：只有一段 φ 够得着
# 区间端点：腕点落在 2R 外圆 |w| = L1 + L2 上，cos(φ − β) = (d² + L3² − (L1 + L2)²)/(2 d L3)，β 为目标的方位角
betaB = math.atan2(PB_[1], PB_[0])
halfB = math.acos((dB ** 2 + L[2] ** 2 - (L[0] + L[1]) ** 2) / (2 * dB * L[2]))
phiB_lo, phiB_hi = deg(betaB - halfB), deg(betaB + halfB)
assert abs(deg(B_up[:, 0].min()) - phiB_lo) < 0.11 and abs(deg(B_up[:, 0].max()) - phiB_hi) < 0.11
# B 的区间是连续的一段（不跨过 ±180°）
assert np.all(np.diff(B_up[:, 0]) < 2 * 2 * math.pi / 3600 + 1e-12)
# 区间端点处 θ2 → 0：肘上、肘下两支在这里相接
i_hi = int(np.argmax(B_up[:, 0]))
t2_end = float(abs(B_up[i_hi, 2]))
assert t2_end < math.radians(3)
# 每一点都是解；切向与零空间平行（定理 17.1.1）
err_tip, err_tan = 0.0, 0.0
for arr, p in ((A_up, PA_), (A_dn, PA_), (B_up, PB_), (B_dn, PB_)):
    for k in range(1, len(arr) - 1, 7):
        th = arr[k, 1:]
        err_tip = max(err_tip, float(np.linalg.norm(joints_planar(th)[-1] - p)))
        d_th = np.array([wrap(x) for x in arr[k + 1, 1:] - arr[k - 1, 1:]])        # 中心差商
        if np.linalg.norm(d_th) > 0.1:           # 跨过 ±180° 的接缝或区间端点，跳过
            continue
        c = null_vector(jac_planar(th))
        cosang = abs(d_th @ c) / (np.linalg.norm(d_th) * np.linalg.norm(c))
        err_tan = max(err_tan, 1 - cosang)
ang_tan = math.degrees(math.acos(1 - err_tan))                     # 差商切向与零空间矢量的最大夹角
assert err_tip < 1e-12 and ang_tan < 0.5
# 两条闭曲线互不相交：A 的肘上、肘下两支 θ2 异号
assert A_up[:, 2].min() > 0 and A_dn[:, 2].max() < 0
# 闭曲线的条数随 d 变化；临界半径为 |L1 ± L2 ± L3|
crit = sorted({abs(L[0] + s2 * L[1] + s3 * L[2]) for s2 in (1, -1) for s3 in (1, -1)})
table_d = [0.05, 0.10, 0.30, dA, dB, 0.95]
loops = [n_loops(d) for d in table_d]
assert loops == [2, 1, 2, 2, 1, 0]
assert n_loops(crit[1] - 0.003) == 1 and n_loops(crit[1] + 0.003) == 2 and n_loops(crit[2] - 0.003) == 2 and n_loops(crit[2] + 0.003) == 1
assert n_loops(crit[0] - 0.003) == 2 and n_loops(crit[0] + 0.003) == 1 and n_loops(crit[3] - 0.003) == 1 and n_loops(crit[3] + 0.003) == 0


# ---------------------------------------------------------------- (2) UR5e 的弯头焊枪：五维任务
a45 = math.radians(45)
TIP_B = np.array([0.12 * math.sin(a45), 0.15 + 0.12 * math.cos(a45), 0.0])     # 枪尖在 {b} 中（y_b 为法兰盘法线）
AX_B = np.array([math.sin(a45), math.cos(a45), 0.0])                           # 焊枪轴线（弯后一段）在 {b} 中


def torch(q):
    T = ur_fk(q)
    return act(T, TIP_B), T[:3, :3] @ AX_B, T


def task_jac(q):
    """五维任务雅可比（式 (17.1.5)）：前三行为枪尖速度，后两行为角速度在与轴线垂直的两个方向上的分量。"""
    p, a, T = torch(q)
    Jg = geometric_jacobian(UR_S, UR_M, q)
    Jw, Jv = Jg[:3], Jg[3:]
    r = p - T[:3, 3]
    u1 = np.cross(a, [0, 0, 1.0])
    u1 /= np.linalg.norm(u1)
    u2 = np.cross(a, u1)
    return np.vstack([Jv - skew(r) @ Jw, u1 @ Jw, u2 @ Jw]), a, p


Jt, a0, p0 = task_jac(TH_STAR)
sv_t = np.linalg.svd(Jt, compute_uv=False)
assert np.linalg.matrix_rank(Jt) == 5
c = null_vector(Jt)
c_unit = c / np.linalg.norm(c) * np.sign(c[5])
# 另一种算法：绕焊枪轴线（过枪尖、方向 a）的单位转动旋量，S = (a, −a × p)；关节速度 J_s⁻¹ S
S_ax = np.r_[a0, -np.cross(a0, p0)]
Js = jacobian_space(UR_S, TH_STAR)
qd_ax = np.linalg.solve(Js, S_ax)
mu0 = 1 / np.linalg.norm(qd_ax)                                     # 沿单位零空间矢量运动时，绕轴转动的角速度
e_null = float(np.abs(qd_ax / np.linalg.norm(qd_ax) * np.sign(qd_ax[5]) - c_unit).max())
assert e_null < 1e-12
# 三个分量的核对：零空间运动时枪尖不动、轴线不转
assert np.abs(Jt @ c).max() < 1e-15


def ik_ur(Td, q):
    for _ in range(60):
        e = log_twist(Td @ inv(ur_fk(q)))
        if np.linalg.norm(e) < 1e-12:
            return q, True
        q = q + np.linalg.solve(jacobian_space(UR_S, q), e)
    return q, False


def march(sign, step=0.5):
    """沿 ψ 逐步转动焊枪（每步 0.5°），每步用牛顿法求逆解，直到求不出或关节角跳动（到了转折点）。"""
    q, last, rec = TH_STAR.copy(), None, [(0.0, *TH_STAR)]
    T0 = ur_fk(TH_STAR)
    for k in range(1, 800):
        psi = sign * math.radians(step * k)
        q2, ok = ik_ur(exp6(S_ax, psi) @ T0, q)
        if not ok or np.abs(q2 - q).max() > 0.2:
            break
        q = q2
        rec.append((psi, *q))
    return np.array(rec)


def turning_point(q):
    """令 θ3 = 0，用其余五个关节解五维任务（5 个方程、5 个未知数），得到肘部伸直的那个形态。"""
    q = q.copy()
    q[2] = 0.0
    for _ in range(50):
        p, a, _ = torch(q)
        e = np.r_[p0 - p, np.cross(a0, a)]
        if np.linalg.norm(e) < 1e-14:
            break
        T = ur_fk(q)
        Jg = geometric_jacobian(UR_S, UR_M, q)
        r = p - T[:3, 3]
        B = np.vstack([Jg[3:] - skew(r) @ Jg[:3], -skew(a0) @ (-skew(a)) @ Jg[:3]])   # d(a × a0) = (ω × a) × a0
        B = np.delete(B, 2, axis=1)
        dq = np.linalg.lstsq(B, e, rcond=None)[0]
        q[[0, 1, 3, 4, 5]] += dq
    p, a, T = torch(q)
    assert np.linalg.norm(p - p0) < 1e-12 and np.linalg.norm(a - a0) < 1e-12
    R_rel = T[:3, :3] @ ur_fk(TH_STAR)[:3, :3].T
    psi = float(logR(R_rel) @ a0)
    return q, psi


fwd, bwd = march(1), march(-1)
q_hi, psi_hi = turning_point(fwd[-1, 1:])
q_lo, psi_lo = turning_point(bwd[-1, 1:])
assert abs(psi_hi - fwd[-1, 0]) < math.radians(0.5) and abs(psi_lo - bwd[-1, 0]) < math.radians(0.5)
# 在转折点：五维任务仍满秩，但 J_s 奇异，零空间运动的 ψ 变化率为零（定理 17.1.2）
mus, dets = [], []
for qq in (q_hi, q_lo):
    J5, a5, p5 = task_jac(qq)
    assert np.linalg.matrix_rank(J5) == 5
    cc = null_vector(J5)
    cc /= np.linalg.norm(cc)
    Vs = jacobian_space(UR_S, qq) @ cc
    mus.append(float(Vs[:3] @ a5))
    dets.append(float(np.linalg.det(jacobian_space(UR_S, qq))))
assert max(abs(m) for m in mus) < 1e-10 and max(abs(d) for d in dets) < 1e-12
# 沿途：J_s c = μ S（零空间运动就是绕焊枪轴线转动），μ 与 det J_s 同号变化
e_twist = 0.0
for row in fwd[::20]:
    qq = row[1:]
    J5, a5, p5 = task_jac(qq)
    cc = null_vector(J5)
    Vs = jacobian_space(UR_S, qq) @ cc
    mu = Vs[:3] @ a5
    e_twist = max(e_twist, float(np.abs(Vs - mu * np.r_[a5, -np.cross(a5, p5)]).max()))
assert e_twist < 1e-12

loop_rows = "\n".join(f"| {d:.3f} | {k} |" for d, k in sorted(zip(table_d, loops)))
out(dA=dA, dB=dB, loop_rows=loop_rows, psi_span=deg(psi_hi - psi_lo), phiB_lo=phiB_lo, phiB_hi=phiB_hi, t2_end=deg(t2_end),
    err_tip=err_tip, ang_tan=ang_tan, crit=", ".join(f"{x:.3f}" for x in crit), loops=loops,
    crit0=crit[0], crit1=crit[1], crit2=crit[2], crit3=crit[3],
    p_tip=tex(p0, 4), a_tip=tex(a0, 4), sv_t=", ".join(f"{x:.4f}" for x in sv_t), c_unit=tex(c_unit, 4),
    e_null=e_null, mu0=mu0,
    psi_hi=deg(psi_hi), psi_lo=deg(psi_lo), q_hi=tex(np.degrees(q_hi), 2), q_lo=tex(np.degrees(q_lo), 2),
    mu_end=max(abs(m) for m in mus), det_end=max(abs(d) for d in dets), e_twist=e_twist,
    t3_fwd_last=deg(fwd[-1, 3]), t3_bwd_last=deg(bwd[-1, 3]), n_fwd=len(fwd), n_bwd=len(bwd))
