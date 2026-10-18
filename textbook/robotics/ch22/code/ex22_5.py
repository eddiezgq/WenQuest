"""22.5 节的计算：SE(3) 上的位姿插值。

(1) 算例 22.5.1：TCP 从料架上方 A（夹爪竖直朝下）到卡盘前 B（轴水平、对准主轴）的位姿插值，三种做法：
    (a) 解耦插值，参考点取 TCP：TCP 走直线，姿态走测地线；(b) 解耦插值，参考点取法兰盘中心；(c) 旋量插值 T_A e^{[V]s}。
    比较中点处 TCP 的位置、TCP 与法兰盘中心走过的路程；求旋量插值的螺旋轴（方向、轴上一点、节距）。
    沿三条路径逐点求逆解（同一支），比较关节转过的角度。
(2) 定理 22.5.1 的数值核对：换基座坐标系（左乘随机的 G）——三种插值都随之变换；换工具坐标系（右乘随机的 H）——
    旋量插值描述的刚体运动不变，解耦插值改变（偏离若干毫米）；旋量插值的物体运动旋量沿途不变。
(3) 算例 22.5.2：三个姿态 R_0（竖直朝下）、R_1（轴倾斜 45°、指向卡盘一侧，示意值）、R_2（水平），两段各 0.8 s。
    分段测地线（每段匀角速度）在 R_1 处物体角速度的跳变；按式 (22.5.6)、(22.5.7) 构造的 C¹ 姿态样条：
    R_1 处角速度连续、两端为零（差商核对），并与 A(r) 的闭式核对 Rᵀ Ṙ = [A(r)ᵀ ṙ]。
"""
import math

import numpy as np

from _traj import (A_left, R_CHUCK, R_DOWN, TBT, cell_joints, cell_poses, decoupled, exp_twist, expso3, inv, log_twist, logR, pose,
                   rot, roty, screw_interp, skew, slerp_R, tcp_ik, ur_fk, ur_labels)
from bookout import out, tex, vec

deg = np.degrees
TR, TA, TB, TC = cell_poses()
thR, thA, thB, thC = cell_joints()
ss = np.linspace(0, 1, 2001)

# ---------------------------------------------------------------- (1) 三种插值
d_fl = (inv(TBT) @ np.array([0, 0, 0, 1.0]))[:3]          # 法兰盘中心在工具坐标系中的位置（0, 0, −0.15）
meth = {
    "tcp": lambda s: decoupled(TA, TB, s),
    "fl": lambda s: decoupled(TA, TB, s, d_fl),
    "screw": lambda s: screw_interp(TA, TB, s),
}
paths = {k: np.array([f(s) for s in ss]) for k, f in meth.items()}
L_tcp = {k: float(np.sum(np.linalg.norm(np.diff(P[:, :3, 3], axis=0), axis=1))) for k, P in paths.items()}
fl_pts = {k: np.array([(T @ np.r_[d_fl, 1])[:3] for T in P]) for k, P in paths.items()}
L_fl = {k: float(np.sum(np.linalg.norm(np.diff(F, axis=0), axis=1))) for k, F in fl_pts.items()}
mid = {k: P[1000][:3, 3] for k, P in paths.items()}
d_mid_fl = float(np.linalg.norm(mid["fl"] - mid["tcp"]) * 1000)
d_mid_sc = float(np.linalg.norm(mid["screw"] - mid["tcp"]) * 1000)
chord = float(np.linalg.norm(TB[:3, 3] - TA[:3, 3]))
assert abs(L_tcp["tcp"] - chord) < 1e-9
# 三种插值的姿态完全相同（都是测地线）
for k in ("fl", "screw"):
    assert max(np.linalg.norm(logR(a[:3, :3].T @ b[:3, :3])) for a, b in zip(paths["tcp"], paths[k])) < 1e-9
rot_deg = float(deg(np.linalg.norm(logR(TA[:3, :3].T @ TB[:3, :3]))))
# 旋量插值的螺旋轴（物体坐标系中 V = log(T_A⁻¹T_B)，换到 {s}：[Ad_{T_A}] V）
V = log_twist(inv(TA) @ TB)
th_sc = float(np.linalg.norm(V[:3]))
from _traj import adjoint
Vs = adjoint(TA) @ V
w_s, v_s = Vs[:3] / th_sc, Vs[3:] / th_sc
h_pitch = float(w_s @ v_s)
q_ax = np.cross(w_s, v_s)                                  # 轴上离 {s} 原点最近的点（式 (6.3.12)）
d_ax = h_pitch * th_sc
r_tcp = float(np.linalg.norm(np.cross(w_s, TA[:3, 3] - q_ax)))
# 逐点求逆解：三条路径都在同一支上，关节转过的角度
jt = {}
for k, P in paths.items():
    th = thA.copy()
    tot = np.zeros(6)
    for T in P[::20]:
        th1 = tcp_ik(T, th)
        tot += np.abs(th1 - th)
        th = th1
    assert np.allclose(th, thB, atol=1e-6)
    jt[k] = float(deg(tot.sum()))

# ---------------------------------------------------------------- (2) 不变性
rng = np.random.default_rng(225)


def rand_pose():
    w = rng.normal(size=3)
    return pose(rot(w / np.linalg.norm(w), rng.uniform(0.3, 2.5)), rng.normal(size=3) * 0.3)


left_err, right_sc, right_dec, twist_var = 0.0, 0.0, 0.0, 0.0
for _ in range(20):
    G, H = rand_pose(), rand_pose()
    for s in (0.2, 0.5, 0.8):
        left_err = max(left_err, np.abs(screw_interp(G @ TA, G @ TB, s) - G @ screw_interp(TA, TB, s)).max(),
                       np.abs(decoupled(G @ TA, G @ TB, s) - G @ decoupled(TA, TB, s)).max())
        right_sc = max(right_sc, np.abs(screw_interp(TA @ H, TB @ H, s) - screw_interp(TA, TB, s) @ H).max())
        right_dec = max(right_dec, np.linalg.norm((decoupled(TA @ H, TB @ H, s) - decoupled(TA, TB, s) @ H)[:3, 3]))
assert left_err < 1e-12 and right_sc < 1e-12 and right_dec > 1e-3
hh = 1e-6
for s in (0.1, 0.4, 0.9):
    Vb = log_twist(inv(screw_interp(TA, TB, s)) @ screw_interp(TA, TB, s + hh)) / hh
    twist_var = max(twist_var, float(np.abs(Vb - V).max()))
assert twist_var < 1e-5
# 换工具坐标系（法兰盘作参考点）就是 (b)：它与 (a) 中点相差 d_mid_fl
# ---------------------------------------------------------------- (3) 多个姿态：分段测地线与 C¹ 姿态样条
R0, R2 = R_DOWN, R_CHUCK
R1 = roty(math.radians(45)) @ R_DOWN
h = np.array([0.8, 0.8])
r01, r12 = logR(R0.T @ R1), logR(R1.T @ R2)
w01, w12 = r01 / h[0], r12 / h[1]                           # 两段测地线上的物体角速度（各自不变）
jump = float(np.linalg.norm(w12 - w01))
ang01, ang12 = float(deg(np.linalg.norm(r01))), float(deg(np.linalg.norm(r12)))
ang02 = float(deg(np.linalg.norm(logR(R0.T @ R2))))
# C¹ 姿态样条：路径点处的物体角速度取两段的平均，两端为零
W = [np.zeros(3), 0.5 * (w01 + w12), np.zeros(3)]
Rs = [R0, R1, R2]


def herm3(T, a0, a1, v0, v1):
    c2 = (3 * (a1 - a0) - (2 * v0 + v1) * T) / T ** 2
    c3 = (-2 * (a1 - a0) + (v0 + v1) * T) / T ** 3
    return a0, v0, c2, c3


segs = []
for k in range(2):
    rk = logR(Rs[k].T @ Rs[k + 1])
    v1 = np.linalg.solve(A_left(rk).T, W[k + 1])           # ṙ(h) = A(r_k)⁻ᵀ ω_{k+1}
    segs.append((Rs[k], h[k], herm3(h[k], np.zeros(3), rk, W[k], v1)))


def R_of(t):
    k = 0 if t <= h[0] else 1
    Rk, T, c = segs[k]
    u = t - (0 if k == 0 else h[0])
    r = c[0] + c[1] * u + c[2] * u * u + c[3] * u ** 3
    rd = c[1] + 2 * c[2] * u + 3 * c[3] * u * u
    return Rk @ expso3(r), A_left(r).T @ rd


tt = np.linspace(0, h.sum(), 1601)
wb = np.array([R_of(t)[1] for t in tt])
# 差商核对 ω_b，以及 R1 处的连续性、两端为零
dtt = 1e-6
err_w = 0.0
for t in (0.3, 0.7, 1.1, 1.5):
    Ra, Rb = R_of(t - dtt)[0], R_of(t + dtt)[0]
    err_w = max(err_w, float(np.abs(logR(Ra.T @ Rb) / (2 * dtt) - R_of(t)[1]).max()))
assert err_w < 1e-6
wl, wr = R_of(h[0] - 1e-9)[1], R_of(h[0] + 1e-9)[1]
cont = float(np.linalg.norm(wl - wr))
assert cont < 1e-6 and np.linalg.norm(R_of(0)[1]) < 1e-12 and np.linalg.norm(R_of(h.sum())[1]) < 1e-9
assert np.allclose(R_of(h[0])[0], R1, atol=1e-12) and np.allclose(R_of(h.sum())[0], R2, atol=1e-12)
wmax_spl = float(np.linalg.norm(wb, axis=1).max())
# A(r)ᵀ 公式的核对：e^{−[r]} A(r) = A(r)ᵀ
rr = np.array([0.4, -0.9, 0.7])
assert np.allclose(expso3(-rr) @ A_left(rr), A_left(rr).T, atol=1e-12)

out(rot_deg=rot_deg, chord=chord, L_tcp_tcp=L_tcp["tcp"], L_tcp_fl=L_tcp["fl"], L_tcp_sc=L_tcp["screw"],
    L_fl_tcp=L_fl["tcp"], L_fl_fl=L_fl["fl"], L_fl_sc=L_fl["screw"], d_mid_fl=d_mid_fl, d_mid_sc=d_mid_sc,
    th_sc=float(deg(th_sc)), w_s=vec(w_s, 4), q_ax=vec(q_ax, 4), h_pitch=h_pitch, d_ax=d_ax, r_tcp=r_tcp,
    jt_tcp=jt["tcp"], jt_fl=jt["fl"], jt_sc=jt["screw"],
    left_err=left_err, right_sc=right_sc, right_dec_mm=right_dec * 1000, twist_var=twist_var,
    ang01=ang01, ang12=ang12, ang02=ang02, w01=float(np.linalg.norm(w01)), w12=float(np.linalg.norm(w12)), jump=jump,
    jump_deg=float(deg(jump)), err_w=err_w, wmax_spl=wmax_spl, wmax_spl_deg=float(deg(wmax_spl)))
