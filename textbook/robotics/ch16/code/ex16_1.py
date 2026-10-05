"""16.1 节：空间雅可比与物体雅可比。

(1) 算例 16.1.1：UR5e 在 θ* = (30°, −60°, 90°, −120°, −90°, 45°)（算例 12.3.1、14.5.1 的关节角）时的 J_s 与 J_b；
    用零件库模型（与指数积无关的另一种算法）的差商核对两者；J_s = [Ad_T] J_b；各列的几何意义（此刻的轴方向与轴上一点）。
(2) 末端角速度是各关节角速度之和；J_s 的第 i 列只与 θ1…θ_{i−1} 有关，J_b 的第 i 列只与 θ_{i+1}…θ_n 有关。
(3) 算例 16.1.2：示教器点动。(a) 基座坐标系中沿 x 平移 50 mm/s；(b) 工具坐标系中绕 z_b 转 10°/s、法兰盘中心不动；
    (c) 误把“绕 z 转”写成 V_s = (0, 0, ω, 0, 0, 0)：法兰盘中心绕基座轴线画圆。
(4) 定理 16.1.3：J̇_s 与 J̇_b 的公式，与差商核对；匀速直线点动时关节需要的加速度 θ̈ = −J_s⁻¹ J̇_s θ̇，与数值积分核对。
"""
import math

import numpy as np

from _jac import (TH_STAR, UR_B, UR_Q, UR_S, UR_W, act, adjoint, exp6, inv, jacobian_body, jacobian_body_dot, jacobian_space,
                  jacobian_space_dot, num_jac_body, num_jac_space, skew, svals, ur_fk, ur_model)
from bookout import out, tex, vec

deg = np.degrees
th = TH_STAR.copy()
T = ur_fk(th)
Js = jacobian_space(UR_S, th)
Jb = jacobian_body(UR_B, th)

# ---------------------------------------------------------------- (1) 与零件库模型的差商核对
model = ur_model()
assert np.abs(model.fk(th) - T).max() < 1e-12
Js_n = num_jac_space(model.fk, th)
Jb_n = num_jac_body(model.fk, th)
e_s, e_b = float(np.abs(Js - Js_n).max()), float(np.abs(Jb - Jb_n).max())
assert e_s < 1e-8 and e_b < 1e-8
e_ad = float(np.abs(Js - adjoint(T) @ Jb).max())
assert e_ad < 1e-14
# 各列的几何意义：ω_i(θ) = R_{i−1} ω̂_i，q_i(θ) = T_{i−1} q_i，v_i = −ω_i × q_i(θ)
P = np.eye(4)
geo = 0.0
for i in range(6):
    w = P[:3, :3] @ UR_W[i]
    q = act(P, UR_Q[i])
    geo = max(geo, float(np.abs(Js[:, i] - np.r_[w, -np.cross(w, q)]).max()))
    P = P @ exp6(UR_S[i], th[i])
assert geo < 1e-14
w2 = Js[:3, 1]
q2 = act(exp6(UR_S[0], th[0]), UR_Q[1])

# ---------------------------------------------------------------- (2) 列只依赖于哪些关节
rng = np.random.default_rng(161)
dep_s, dep_b = 0.0, 0.0
for _ in range(100):
    a = rng.uniform(-math.pi, math.pi, 6)
    for i in range(6):
        b = a.copy()
        b[i:] = rng.uniform(-math.pi, math.pi, 6 - i)          # 改变关节 i 及其以后的角
        dep_s = max(dep_s, float(np.abs(jacobian_space(UR_S, a)[:, i] - jacobian_space(UR_S, b)[:, i]).max()))
        c = a.copy()
        c[:i + 1] = rng.uniform(-math.pi, math.pi, i + 1)       # 改变关节 i 及其以前的角
        dep_b = max(dep_b, float(np.abs(jacobian_body(UR_B, a)[:, i] - jacobian_body(UR_B, c)[:, i]).max()))
assert dep_s < 1e-13 and dep_b < 1e-13
# 角速度是各关节角速度之和（在 {s} 中）
dth = np.radians([10, -20, 15, 30, -25, 40])
h = 1e-6
R1, R0 = ur_fk(th + h * dth)[:3, :3], ur_fk(th - h * dth)[:3, :3]
W = (R1 - R0) / (2 * h) @ T[:3, :3].T
w_num = np.array([W[2, 1], W[0, 2], W[1, 0]])
w_sum = sum(Js[:3, i] * dth[i] for i in range(6))
assert np.abs(w_num - w_sum).max() < 1e-8
sv_s, sv_b = svals(Js), svals(Jb)
assert abs(np.prod(sv_s) - np.prod(sv_b)) < 1e-12               # |det J_s| = |det J_b|

# ---------------------------------------------------------------- (3) 算例 16.1.2：点动
p = T[:3, 3]
# (a) 基座坐标系中沿 x_s 平移 50 mm/s，姿态不变：V_s = (0, ṗ − ω × p) = (0, 0, 0, 0.05, 0, 0)
Va = np.r_[0, 0, 0, 0.05, 0, 0]
qa = np.linalg.solve(Js, Va)
# (b) 工具坐标系中绕 z_b 转 10°/s，法兰盘中心（{b} 的原点）不动：V_b = (0, 0, ω, 0, 0, 0)
om = math.radians(10)
Vb = np.r_[0, 0, om, 0, 0, 0]
qb = np.linalg.solve(Jb, Vb)
# 核对：V_s = [Ad_T] V_b 的线速度部分恰为 −ω_s × p，法兰盘中心速度 v_s + ω_s × p = 0
Vs_b = adjoint(T) @ Vb
assert np.linalg.norm(Vs_b[3:] + np.cross(Vs_b[:3], p)) < 1e-14
# (c) 误写：V_s = (0, 0, ω, 0, 0, 0) —— 绕过 {s} 原点的竖直线转动，即只转关节 1
Vc = np.r_[0, 0, om, 0, 0, 0]
qc = np.linalg.solve(Js, Vc)
assert np.abs(qc - np.r_[om, 0, 0, 0, 0, 0]).max() < 1e-12
vc = Vc[3:] + np.cross(Vc[:3], p)                               # 法兰盘中心的速度
rc = math.hypot(p[0], p[1])


def rk4(f, y, dt):
    k1 = f(y)
    k2 = f(y + dt / 2 * k1)
    k3 = f(y + dt / 2 * k2)
    k4 = f(y + dt * k3)
    return y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


# 三种点动各进行 3 s，核对法兰盘中心的路径
def run(V, frame, dur=3.0, dt=1e-3):
    f = (lambda q: np.linalg.solve(jacobian_space(UR_S, q), V)) if frame == "s" else (lambda q: np.linalg.solve(jacobian_body(UR_B, q), V))
    q = th.copy()
    path = [ur_fk(q)[:3, 3]]
    for _ in range(int(round(dur / dt))):
        q = rk4(f, q, dt)
        path.append(ur_fk(q)[:3, 3])
    return q, np.array(path)


qa_end, Pa = run(Va, "s")
Ta = ur_fk(qa_end)
dev_a = float(np.max(np.linalg.norm(np.cross(Pa - p, [1, 0, 0]), axis=1)))     # 偏离直线的最大距离
ang_a = float(np.linalg.norm(np.array([0.0])))
Ra = Ta[:3, :3] @ T[:3, :3].T
ang_a = math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(Ra) - 1) / 2))))
assert dev_a < 1e-9 and ang_a < 1e-7 and abs(Ta[0, 3] - p[0] - 0.15) < 1e-9
qb_end, Pb = run(Vb, "b")
mv_b = float(np.max(np.linalg.norm(Pb - p, axis=1)))
assert mv_b < 1e-9
# 关节速度在 3 s 内怎样变化（直线点动）
qq = th.copy()
spd = []
for k in range(3001):
    v = np.linalg.solve(jacobian_space(UR_S, qq), Va)
    spd.append(v)
    qq = rk4(lambda q: np.linalg.solve(jacobian_space(UR_S, q), Va), qq, 1e-3)
spd = np.degrees(np.array(spd))
j2_0, j2_3 = spd[0, 1], spd[-1, 1]

# ---------------------------------------------------------------- (4) 雅可比矩阵的时间导数
Jsd = jacobian_space_dot(UR_S, th, dth)
Jbd = jacobian_body_dot(UR_B, th, dth)
Jsd_n = (jacobian_space(UR_S, th + h * dth) - jacobian_space(UR_S, th - h * dth)) / (2 * h)
Jbd_n = (jacobian_body(UR_B, th + h * dth) - jacobian_body(UR_B, th - h * dth)) / (2 * h)
e_sd, e_bd = float(np.abs(Jsd - Jsd_n).max()), float(np.abs(Jbd - Jbd_n).max())
assert e_sd < 1e-8 and e_bd < 1e-8
# 匀速直线点动所需的关节加速度：0 = J_s θ̈ + J̇_s θ̇
acc = np.linalg.solve(Js, -jacobian_space_dot(UR_S, th, qa) @ qa)
dt = 1e-4
f = lambda q: np.linalg.solve(jacobian_space(UR_S, q), Va)
acc_n = (f(rk4(f, th, dt)) - f(rk4(f, th, -dt))) / (2 * dt)
e_acc = float(np.abs(acc - acc_n).max())
assert e_acc < 1e-6

out(Js=tex(Js, 4), Jb=tex(Jb, 4), e_s=e_s, e_b=e_b, e_ad=e_ad, w2=vec(w2, 4), q2=vec(q2, 4),
    sv_s=", ".join(f"{x:.4f}" for x in sv_s), sv_b=", ".join(f"{x:.4f}" for x in sv_b), det=float(np.prod(sv_s)),
    dep_s=dep_s, dep_b=dep_b,
    p=vec(p, 4), qa=vec(deg(qa), 3), qb=vec(deg(qb), 3), qc=vec(deg(qc), 3), vc=float(np.linalg.norm(vc)), rc=rc,
    dev_a=dev_a, ang_a=ang_a, mv_b=mv_b, j2_0=float(j2_0), j2_3=float(j2_3),
    e_sd=e_sd, e_bd=e_bd, acc=vec(deg(acc), 3), acc_max=float(np.abs(deg(acc)).max()), e_acc=e_acc,
    w_sum=vec(w_sum, 4), dth=vec(deg(dth), 0))
