"""17.2 节：零空间运动。

(1) 定理 17.2.1（广义叉积）：对 m×(m+1) 矩阵 J，c_i = (−1)^{m+1+i} det J_(i) 满足 J c = 0、det[J; cᵀ] = ‖c‖²、
    ‖c‖² = det(J Jᵀ)。在 300 组随机矩阵（6×7 与 2×3）上核对；降秩时 c = 0。
(2) 算例 17.2.1：Panda 停在 ready 姿态。零空间矢量 c（与 SVD 的结果比较，‖c‖ 等于可操作度 w）；
    手的位姿固定在 ready 姿态，沿 c 追踪自运动（每步两阶龙格-库塔预测 + 牛顿校正）：闭曲线的长度、位姿误差、
    限位以内的弧段及两端是哪个关节的限位、肘部绕肩腕连线摆过的角度、腕点的移动、可操作度沿曲线的变化；
    不加校正只积分 c 时，末端的漂移。由 120 个随机初值求逆解，清点同一个位姿有几条互不相连的自运动闭曲线。
(3) 算例 17.2.2：平面 3R 臂的末端沿圆周（圆心 (0.5, 0.2) m，半径 0.15 m，周期 4 s）运动，关节速度取伪逆解：
    每转一圈关节角不回到原处（不可重复）；c · (∇ × c) ≠ 0，即约束 cᵀθ̇ = 0 不可积（定理 11.5.3）；
    加上把关节拉向参考形态的零空间项以后，几圈之内收敛为一条每圈都重复的轨迹。
"""
import math

import numpy as np

from _red import (PA_HI, PA_LO, PA_READY, PL, ik2r, pa_trace, pa_unit_null, jac_planar, joints_planar, manip, null_vector, pa_elbow, pa_fk,
                  pa_js, pa_points, pa_wrist, pinv_rows, pose_error_s, wrap)
from bookout import out, tex

deg = math.degrees
TW = 2 * math.pi

# ---------------------------------------------------------------- (1) 广义叉积
rng = np.random.default_rng(172)
e_null = e_det = e_cb = 0.0
for k in range(300):
    m = 6 if k % 2 else 2
    J = rng.normal(size=(m, m + 1))
    c = null_vector(J)
    e_null = max(e_null, float(np.abs(J @ c).max() / np.abs(J).max() ** m))
    e_det = max(e_det, abs(np.linalg.det(np.vstack([J, c])) - c @ c) / (c @ c))
    e_cb = max(e_cb, abs(c @ c - np.linalg.det(J @ J.T)) / (c @ c))
assert e_null < 1e-12 and e_det < 1e-12 and e_cb < 1e-12
Jd = rng.normal(size=(6, 7))
Jd[5] = Jd[0] + 2 * Jd[3]                                            # 降秩：第 6 行是第 1、4 行的组合
assert np.abs(null_vector(Jd)).max() < 1e-12

# ---------------------------------------------------------------- (2) Panda 在 ready 姿态的自运动
q0 = PA_READY.copy()
J0 = pa_js(q0)
c0 = null_vector(J0)
w0 = manip(J0)
n_svd = np.linalg.svd(J0)[2][-1]
n_svd *= np.sign(n_svd @ c0)
assert abs(np.linalg.norm(c0) - w0) < 1e-15 and np.abs(c0 / np.linalg.norm(c0) - n_svd).max() < 1e-12
Td = pa_fk(q0)
h = 0.01


def unit_c(q):
    return pa_unit_null(q)


def trace(qs, Td, correct=True, maxs=4000, h=h):
    """见 _red.pa_trace。"""
    return pa_trace(qs, Td, h=h, correct=correct, maxs=maxs)


P = trace(q0, Td)
n_pts = len(P)
loop_len = n_pts * h
err_pose = max(float(np.linalg.norm(pose_error_s(pa_fk(q), Td))) for q in P[::5])
assert err_pose < 1e-12
net = np.round((P[-1] + h * unit_c(P[-1]) - P[0]) / TW)               # 一圈下来各关节净转过的整圈数
# 不加校正：同样的步数只积分 c，末端漂离
Pn = trace(q0, Td, correct=False, maxs=n_pts)
drift_pos = max(float(np.linalg.norm(pa_fk(q)[:3, 3] - Td[:3, 3])) for q in Pn)


def into(q):
    return PA_LO + np.mod(q - PA_LO, TW)


Pi = np.array([into(q) for q in P])
inl = np.all(Pi <= PA_HI, axis=1)
frac_in = float(inl.mean())
# ready 所在的那一段限位以内的弧
i1 = 0
while inl[(i1 + 1) % n_pts]:
    i1 += 1
i0 = 0
while inl[(i0 - 1) % n_pts]:
    i0 -= 1
arc = [k % n_pts for k in range(i0, i1 + 1)]
arc_len = (i1 - i0) * h
assert abs(arc_len / loop_len - frac_in) < 0.01                    # 限位以内的只有这一段
viol_hi = [j + 1 for j in range(7) if into(P[(i1 + 1) % n_pts])[j] > PA_HI[j]]
viol_lo = [j + 1 for j in range(7) if into(P[(i0 - 1) % n_pts])[j] > PA_HI[j]]
assert viol_hi == [2] and viol_lo == [2]
q_end1, q_end0 = Pi[i1 % n_pts], Pi[i0 % n_pts]
t1_rng = (deg(min(wrap(Pi[k][0]) for k in arc)), deg(max(wrap(Pi[k][0]) for k in arc)))


def swing(q, ref):
    """肘点绕肩腕连线摆过的角（从 ready 量起，右手定则绕 S→W）。"""
    S, W, Ep = pa_points(q)[1], pa_wrist(q), pa_elbow(q)
    u = (W - S) / np.linalg.norm(W - S)
    e = (Ep - S) - ((Ep - S) @ u) * u
    return math.atan2(u @ np.cross(ref, e), ref @ e)


S0, W0, E0 = pa_points(q0)[1], pa_wrist(q0), pa_elbow(q0)
u0 = (W0 - S0) / np.linalg.norm(W0 - S0)
ref = (E0 - S0) - ((E0 - S0) @ u0) * u0
sw = np.array([swing(q, ref) for q in P])
sw_arc = np.unwrap(sw[arc])
sw_lo, sw_hi = deg(sw_arc.min()), deg(sw_arc.max())
wr_move = max(float(np.linalg.norm(pa_wrist(q) - W0)) for q in P)
el_r = float(np.linalg.norm(ref))                                    # ready 时肘点到肩腕连线的距离
w_loop = np.array([manip(pa_js(q)) for q in P])
k_wmax = int(np.argmax(w_loop))
assert np.linalg.norm([wrap(x) for x in P[k_wmax] - q0]) < 2 * h    # 可操作度在 ready 处最大
w_arc_min = float(w_loop[arc].min())
w_loop_min = float(w_loop.min())

# 清点自运动闭曲线：200 个随机初值求逆解，看解落在哪一条闭曲线上
def ik(q):
    for _ in range(100):
        e = pose_error_s(pa_fk(q), Td)
        if np.linalg.norm(e) < 1e-12:
            return q, True
        J = pa_js(q)
        q = q + J.T @ np.linalg.solve(J @ J.T + 1e-6 * np.eye(6), e)
    return q, False


wrapv = np.vectorize(wrap)
loops = [wrapv(P)]
loop_info = [(loop_len, frac_in)]
rng = np.random.default_rng(1722)
n_ok = 0
for _ in range(120):
    q, ok = ik(rng.uniform(-math.pi, math.pi, 7))
    if not ok:
        continue
    n_ok += 1
    qw = wrapv(q)
    if any(np.abs(wrapv(Lp - qw)).max(axis=1).min() < 0.03 for Lp in loops):
        continue
    Q = trace(qw, Td, h=0.02)
    loops.append(wrapv(Q))
    loop_info.append((len(Q) * 0.02, float(np.mean([np.all(into(x) <= PA_HI) for x in Q]))))
n_loops = len(loops)
assert n_loops == 8
n_loops_in = sum(1 for L_, f in loop_info if f > 0)

# ---------------------------------------------------------------- (3) 伪逆控制不可重复
CC, RR, TP = np.array([0.5, 0.2]), 0.15, 4.0


def ik3(p, phi):
    w = p - PL[2] * np.array([math.cos(phi), math.sin(phi)])
    t1, t2 = ik2r(w[0], w[1], PL[0], PL[1])[0]
    return np.array([t1, t2, wrap(phi - t1 - t2)])


th0 = ik3(CC + np.array([RR, 0.0]), math.radians(-30))
assert np.linalg.norm(joints_planar(th0)[-1] - CC - [RR, 0]) < 1e-14


def circle_run(th, loops, k_null=0.0, ref=None, kp=10.0, dt=4e-3):
    """末端沿圆周运动：θ̇ = J⁺(ṗ_d + k_p (p_d − p)) + k (I − J⁺J)(θ_ref − θ)，四阶龙格-库塔积分。返回每圈结束时的 θ。"""
    def f(th, t):
        a = 2 * math.pi * t / TP
        pd = CC + RR * np.array([math.cos(a), math.sin(a)])
        vd = RR * 2 * math.pi / TP * np.array([-math.sin(a), math.cos(a)])
        J = jac_planar(th)
        Jp = pinv_rows(J)
        qd = Jp @ (vd + kp * (pd - joints_planar(th)[-1]))
        if k_null:
            qd = qd + (np.eye(3) - Jp @ J) @ (k_null * (ref - th))
        return qd
    ends, t, tip_err = [th.copy()], 0.0, 0.0
    for _ in range(loops):
        for _ in range(int(round(TP / dt))):
            k1 = f(th, t)
            k2 = f(th + dt / 2 * k1, t + dt / 2)
            k3 = f(th + dt / 2 * k2, t + dt / 2)
            k4 = f(th + dt * k3, t + dt)
            th = th + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            t += dt
            a = 2 * math.pi * t / TP
            tip_err = max(tip_err, float(np.linalg.norm(joints_planar(th)[-1] - CC - RR * np.array([math.cos(a), math.sin(a)]))))
        ends.append(th.copy())
    return np.array(ends), tip_err


ends, tip_err = circle_run(th0, 10)
assert tip_err < 1e-9
d1, d10 = np.degrees(ends[1] - th0), np.degrees(ends[10] - th0)
# 每圈的漂移大致相同（第 10 圈与第 1 圈的漂移之比）
ratio_10 = float(np.linalg.norm(ends[10] - ends[9]) / np.linalg.norm(ends[1] - ends[0]))
ends_k, tip_err_k = circle_run(th0, 10, k_null=2.0, ref=th0)
assert tip_err_k < 1e-9
dk10 = np.degrees(ends_k[10] - th0)
rep_k = float(np.abs(np.degrees(ends_k[10] - ends_k[9])).max())
assert rep_k < 1e-6 and np.abs(d10).max() > 5


# c · (∇ × c)：用中心差商求 c 的旋度
def curl_c(th, hh=1e-6):
    Dc = np.zeros((3, 3))
    for j in range(3):
        e = np.zeros(3)
        e[j] = hh
        Dc[:, j] = (null_vector(jac_planar(th + e)) - null_vector(jac_planar(th - e))) / (2 * hh)
    return np.array([Dc[2, 1] - Dc[1, 2], Dc[0, 2] - Dc[2, 0], Dc[1, 0] - Dc[0, 1]])


c_th0 = null_vector(jac_planar(th0))
ccurl = float(c_th0 @ curl_c(th0))
ccurl_n = ccurl / float(c_th0 @ c_th0)                               # 除以 ‖c‖²：与 c 的长度无关，单位 1/rad
rng = np.random.default_rng(1723)
ccurl_rand = []
for _ in range(20):
    th = rng.uniform(-math.pi, math.pi, 3)
    if np.linalg.svd(jac_planar(th), compute_uv=False)[-1] < 0.05:
        continue
    cc = null_vector(jac_planar(th))
    ccurl_rand.append(float(cc @ curl_c(th)) / float(cc @ cc))
assert min(abs(x) for x in ccurl_rand) > 1e-3

out(e_null=e_null, e_det=e_det, e_cb=e_cb,
    c0=tex(c0, 4), w0=w0, nsvd=tex(n_svd, 4),
    loop_len=loop_len, n_pts=n_pts, err_pose=err_pose, drift_pos=drift_pos, net=[int(x) for x in net], net1=int(net[0]), net7=int(net[6]), net_rest=int(np.abs(net[1:6]).max()),
    frac_in=frac_in * 100, arc_len=arc_len, q_end1=tex(np.degrees(q_end1), 1), q_end0=tex(np.degrees(q_end0), 1),
    t1_lo=t1_rng[0], t1_hi=t1_rng[1], sw_lo=sw_lo, sw_hi=sw_hi, wr_move=wr_move, el_r=el_r,
    w_arc_min=w_arc_min, w_loop_min=w_loop_min, n_loops=n_loops, n_loops_in=n_loops_in, n_ok=n_ok,
    th0=tex(np.degrees(th0), 2), d1=tex(d1, 3), d10=tex(d10, 2), ratio_10=ratio_10, tip_err=tip_err,
    dk10=tex(dk10, 3), rep_k=rep_k, ccurl=ccurl, ccurl_n=ccurl_n,
    ccurl_min=min(abs(x) for x in ccurl_rand), ccurl_max=max(abs(x) for x in ccurl_rand), n_rand=len(ccurl_rand))
