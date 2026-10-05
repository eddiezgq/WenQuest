"""17.3 节：次要任务：避限位、避障、提高可操作度。

(1) 定理 17.3.2：可操作度 w = √det(J Jᵀ) 的梯度 ∂w/∂θ_k = w · tr(J⁺ ∂J/∂θ_k)，∂J/∂θ_k 由李括号逐列写出；
    在 Panda 的 200 组随机关节角上与差商比较；并核对 w 对 J_s、J_b、J_g 三种雅可比相同。
(2) 算例 17.3.1（避限位）：Panda 从 ready 出发，4 s 内把手向后 0.30 m、向右 0.25 m、向下 0.20 m，同时绕竖直轴转 80°
    （位置按余弦规律过渡）。只用伪逆时关节 2 超出下限；加上式 (15.4.6) 的 H 的梯度投影后，各关节都在限位以内。
    沿途核对定理 17.3.1：零空间项对 H 的变化率为 −k‖N∇H‖² ≤ 0。
(3) 算例 17.3.2（提高可操作度）：手固定在 ready 姿态，从 17.2 节那条自运动闭曲线上的两个形态出发，沿零空间作 w 的梯度上升：
    从弧长 s = −1 rad 处出发，回到 ready（全局最大）；从 s = −3 rad 处出发，停在 s ≈ −2.2 rad 附近的局部最大。
    停止处满足 N∇w = 0，即 ∇w 落在 J 的行空间里（拉格朗日条件）。
(4) 算例 17.3.3（避障）：手固定在 ready 姿态，一个半径 0.05 m 的球形障碍物在 4 s 内从后方移向肘部。以“手臂到障碍物的距离”
    为一维次要任务，放在手的任务的零空间里（任务优先级，式 (15.4.9) 的连续形式）；平面 3R 臂的同类算例供图和动画使用。
"""
import math

import numpy as np

from _red import (PA_HI, PA_LO, PA_READY, PA_S, PL, ad, adjoint, body_screws, dJs_dtheta, inv, jac_planar, jacobian_body,
                  jacobian_space, joint_mid_cost, joints_planar, lim_margin, manip, manip_grad, pa_fk, pa_jg, pa_js,
                  pa_points, pa_trace, pinv_rows, pose_error_g, pose_error_s, rot, seg_dist, PA_M)
from bookout import out, tex

deg = math.degrees

# ---------------------------------------------------------------- (1) 可操作度的梯度
rng = np.random.default_rng(173)
PA_B = body_screws(PA_S, PA_M)
e_grad = e_frames = e_dJ = 0.0
hh = 1e-6
for _ in range(200):
    q = rng.uniform(PA_LO, PA_HI)
    w, g = manip_grad(PA_S, q)
    gn = np.array([(manip(pa_js(q + hh * e)) - manip(pa_js(q - hh * e))) / (2 * hh) for e in np.eye(7)])
    e_grad = max(e_grad, float(np.abs(g - gn).max() / max(1e-3, np.abs(gn).max())))
    e_frames = max(e_frames, abs(manip(jacobian_body(PA_B, q)) - w), abs(manip(pa_jg(q)) - w))
    k = int(rng.integers(7))
    Dn = (pa_js(q + hh * np.eye(7)[k]) - pa_js(q - hh * np.eye(7)[k])) / (2 * hh)
    e_dJ = max(e_dJ, float(np.abs(Dn - dJs_dtheta(pa_js(q), k)).max()))
assert e_grad < 1e-6 and e_frames < 1e-13 and e_dJ < 1e-8

# ---------------------------------------------------------------- (2) 避限位
T0 = pa_fk(PA_READY)
DP = np.array([-0.30, -0.25, -0.20])
RZ = math.radians(80)
TT, DT = 4.0, 0.004
KP = 5.0


def run_limits(kH):
    q, rec, dH_max = PA_READY.copy(), [], -1.0
    for i in range(int(round(TT / DT)) + 1):
        t = i * DT
        s = (1 - math.cos(math.pi * t / TT)) / 2
        sd = math.pi / TT * math.sin(math.pi * t / TT) / 2
        Td = T0.copy()
        Td[:3, 3] = T0[:3, 3] + s * DP
        Td[:3, :3] = rot([0, 0, 1], s * RZ) @ T0[:3, :3]
        V = np.r_[np.array([0, 0, RZ]) * sd, sd * DP]
        J = pa_jg(q)
        Jp = pinv_rows(J)
        qd = Jp @ (V + KP * pose_error_g(pa_fk(q), Td))
        H, gH = joint_mid_cost(q, PA_LO, PA_HI)
        if kH:
            zn = -(np.eye(7) - Jp @ J) @ (kH * gH)
            dH_max = max(dH_max, float(gH @ zn + kH * np.linalg.norm((np.eye(7) - Jp @ J) @ gH) ** 2))   # 应为 0（定理 17.3.1）
            assert gH @ zn <= 1e-15
            qd = qd + zn
        rec.append((t, *q, H, float(np.linalg.norm(pose_error_g(pa_fk(q), Td)))))
        if i < int(round(TT / DT)):
            q = q + DT * qd
    return np.array(rec), dH_max


R0, _ = run_limits(0.0)
KH = 5.0
R1, dH_id = run_limits(KH)
mg0 = np.array([lim_margin(r[1:8], PA_LO, PA_HI) for r in R0])
mg1 = np.array([lim_margin(r[1:8], PA_LO, PA_HI) for r in R1])
j_viol = int(np.argmin(mg0.min(axis=0))) + 1
assert j_viol == 2 and mg0.min() < 0 and mg1.min() > 0
t2_min0, t2_min1 = deg(R0[:, 2].min()), deg(R1[:, 2].min())
j_min1 = int(np.argmin(mg1.min(axis=0))) + 1
err_lim = max(R0[:, -1].max(), R1[:, -1].max())
assert err_lim < 1e-3 and abs(dH_id) < 1e-12
H_end0, H_end1 = R0[-1, 8], R1[-1, 8]

# ---------------------------------------------------------------- (3) 提高可操作度
h2 = 0.01
P = pa_trace(PA_READY, pa_fk(PA_READY), h=h2)                        # 17.2 节那条自运动闭曲线（算例 17.2.1）
n2 = len(P)
s_of = np.arange(n2) * h2
s_of = np.where(s_of > s_of[-1] / 2, s_of - s_of[-1] - h2, s_of)
Td_r = pa_fk(PA_READY)
KW = 50.0


def ascend(q, T_end=30.0, dt=0.01):
    hist = []
    for i in range(int(round(T_end / dt))):
        J = pa_js(q)
        Jp = pinv_rows(J)
        N = np.eye(7) - Jp @ J
        w, g = manip_grad(PA_S, q)
        hist.append((i * dt, w))
        q = q + dt * (Jp @ (KP * pose_error_s(pa_fk(q), Td_r)) + N @ (KW * g))
    w, g = manip_grad(PA_S, q)
    J = pa_js(q)
    lam = np.linalg.solve(J @ J.T, J @ g)                            # ∇w = Jᵀλ 的最小二乘解
    return q, np.array(hist), float(np.linalg.norm(g - J.T @ lam) / np.linalg.norm(g))


k_a = int(np.argmin(np.abs(s_of + 1.0)))
k_b = int(np.argmin(np.abs(s_of + 3.0)))
qa, Ha, lag_a = ascend(P[k_a].copy())
qb, Hb, lag_b = ascend(P[k_b].copy())
w_ready = manip(pa_js(PA_READY))
wa0, wa1 = manip(pa_js(P[k_a])), manip(pa_js(qa))
wb0, wb1 = manip(pa_js(P[k_b])), manip(pa_js(qb))

assert abs(wa1 - w_ready) < 2e-4 and wb1 < w_ready - 1e-3 and lag_b < 1e-4
# qb 停在闭曲线上的哪里
wrapv = np.vectorize(lambda a: math.atan2(math.sin(a), math.cos(a)))
k_stop = int(np.argmin(np.abs(wrapv(P - qb)).max(axis=1)))
s_stop = float(s_of[k_stop])
w_loop = np.array([manip(pa_js(q)) for q in P])
k_loc = int(np.argmin(np.where(np.abs(s_of - s_stop) < 0.5, -w_loop, 0)))
assert abs(s_of[k_loc] - s_stop) < 0.05 and abs(w_loop[k_loc] - wb1) < 1e-4
t99 = float(Ha[np.argmax(Ha[:, 1] >= wa0 + 0.99 * (w_ready - wa0)), 0])
err_hand = float(np.linalg.norm(pose_error_s(pa_fk(qa), Td_r)) + np.linalg.norm(pose_error_s(pa_fk(qb), Td_r)))
assert err_hand < 1e-6

# ---------------------------------------------------------------- (4) 避障
SEGLINK = [0, 3, 3, 4, 4, 6, 7]          # pa_points 的第 i 段（点 i 到点 i+1）随关节 1…SEGLINK[i] 运动


def closest_arm(q, c):
    P_ = pa_points(q)
    best = (1e9, None, None)
    for i in range(1, 7):
        d, x, _ = seg_dist(c, P_[i], P_[i + 1])
        if d < best[0]:
            best = (d, x, i)
    return best


def point_jac(q, x, k):
    """手臂上点 x 的速度雅可比（3×7）：它随关节 1…k 运动，第 i 列为 v_i + ω_i × x（由空间雅可比的第 i 列）。"""
    Js = pa_js(q)
    Jx = np.zeros((3, 7))
    for i in range(k):
        Jx[:, i] = Js[3:, i] + np.cross(Js[:3, i], x)
    return Jx


RAD, D_ACT, K_D, LAM_O = 0.05, 0.12, 3.0, 0.02
C0, C1 = np.array([-0.55, 0.03, 0.62]), np.array([-0.12, 0.03, 0.62])


def run_obstacle(avoid, T_end=4.0, dt=0.004):
    q, rec = PA_READY.copy(), []
    for i in range(int(round(T_end / dt)) + 1):
        t = i * dt
        s = (1 - math.cos(math.pi * t / T_end)) / 2
        sd = math.pi / T_end * math.sin(math.pi * t / T_end) / 2
        c, cd = C0 + s * (C1 - C0), sd * (C1 - C0)
        J = pa_jg(q)
        Jp = pinv_rows(J)
        N = np.eye(7) - Jp @ J
        qd = Jp @ (KP * pose_error_g(pa_fk(q), T0))
        d, x, k = closest_arm(q, c)
        d -= RAD
        if avoid and d < D_ACT:
            u = (x - c) / np.linalg.norm(x - c)
            a = u @ point_jac(q, x, SEGLINK[k])                        # ḋ = a θ̇ − uᵀ ċ
            want = u @ cd + K_D * (D_ACT - d)                          # 希望的 ḋ：抵消障碍物的接近，并把距离推回 D_ACT
            A1 = (a @ N)[None, :]
            qd = qd + (A1.T / (A1 @ A1.T + LAM_O ** 2)) @ (np.array([want]) - a @ qd)
        rec.append((t, d, float(np.linalg.norm(pose_error_g(pa_fk(q), T0))), *q))
        if i < int(round(T_end / dt)):
            q = q + dt * qd
    return np.array(rec)


O0, O1 = run_obstacle(False), run_obstacle(True)
dmin0, dmin1 = float(O0[:, 1].min()), float(O1[:, 1].min())
assert dmin0 < 0 and dmin1 > 0.1
err_obs = float(O1[:, 2].max())
assert err_obs < 1e-3
q_obs_end = O1[-1, 3:]
el_end = pa_points(q_obs_end)[3]
mg_obs = float(min(lim_margin(r[3:], PA_LO, PA_HI).min() for r in O1))
w_obs_end = manip(pa_js(q_obs_end))
assert mg_obs > 0

# 平面 3R 臂的同类算例：末端固定在 (0.6, 0.2) m，圆形障碍物（半径 0.05 m）在 3 s 内从正上方压向肘部
PT = np.array([0.6, 0.2])



def ik_planar(p, phi, up=True):
    from _red import ik2r, wrap
    w = p - PL[2] * np.array([math.cos(phi), math.sin(phi)])
    t1, t2 = ik2r(w[0], w[1], PL[0], PL[1])[0 if up else 1]
    return np.array([t1, t2, wrap(phi - t1 - t2)])


th_p0 = ik_planar(PT, math.radians(-60), up=False)
PC0, PC1 = np.array([0.17, 0.85]), np.array([0.17, 0.42])
PRAD, PD_ACT = 0.05, 0.10


def run_planar(avoid, T_end=4.0, dt=0.004):
    th, rec = th_p0.copy(), []
    for i in range(int(round(T_end / dt)) + 1):
        t = i * dt
        s = (1 - math.cos(math.pi * min(t, 3.0) / 3.0)) / 2
        sd = math.pi / 3.0 * math.sin(math.pi * t / 3.0) / 2 if t < 3.0 else 0.0
        c, cd = PC0 + s * (PC1 - PC0), sd * (PC1 - PC0)
        J = jac_planar(th)
        Jp = pinv_rows(J)
        N = np.eye(3) - Jp @ J
        qd = Jp @ (KP * (PT - joints_planar(th)[-1]))
        pts = joints_planar(th)
        best = (1e9, None, None)
        for k in range(3):
            d, x, _ = seg_dist(c, pts[k], pts[k + 1])
            if d < best[0]:
                best = (d, x, k)
        d, x, k = best
        d -= PRAD
        if avoid and d < PD_ACT:
            u = (x - c) / np.linalg.norm(x - c)
            Jx = np.zeros((2, 3))
            for j in range(k + 1):
                r = x - pts[j]
                Jx[:, j] = [-r[1], r[0]]
            a = u @ Jx
            want = u @ cd + K_D * (PD_ACT - d)
            A1 = (a @ N)[None, :]
            qd = qd + (A1.T / (A1 @ A1.T + LAM_O ** 2)) @ (np.array([want]) - a @ qd)
        rec.append((t, d, *th, *c))
        if i < int(round(T_end / dt)):
            th = th + dt * qd
    return np.array(rec)


PL0, PL1 = run_planar(False), run_planar(True)
pdmin0, pdmin1 = float(PL0[:, 1].min()), float(PL1[:, 1].min())
assert pdmin0 < 0 and pdmin1 > 0.05
p_tip_err = max(float(np.linalg.norm(joints_planar(r[2:5])[-1] - PT)) for r in PL1)
assert p_tip_err < 1e-3

out(e_grad=e_grad, e_frames=e_frames, e_dJ=e_dJ,
    mg0=mg0.min(), mg1=mg1.min(), t2_min0=t2_min0, t2_min1=t2_min1, j_min1=j_min1, t2_lo=deg(PA_LO[1]), err_lim=err_lim,
    dH_id=dH_id, KH=KH, H_end0=H_end0, H_end1=H_end1, q_end0=tex(np.degrees(R0[-1, 1:8]), 1), q_end1=tex(np.degrees(R1[-1, 1:8]), 1),
    t4_end=deg(R1[-1, 4]),
    w_ready=w_ready, wa0=wa0, wa1=wa1, wb0=wb0, wb1=wb1, s_stop=s_stop, lag_b=lag_b, lag_a=lag_a, t99=t99, KW=KW,
    dmin0=dmin0, dmin1=dmin1, err_obs=err_obs, el_end=tex(el_end, 3), mg_obs=mg_obs, w_obs_end=w_obs_end,
    q_obs_end=tex(np.degrees(q_obs_end), 1), D_ACT=D_ACT,
    pdmin0=pdmin0, pdmin1=pdmin1, p_tip_err=p_tip_err, th_p0=tex(np.degrees(th_p0), 1))
