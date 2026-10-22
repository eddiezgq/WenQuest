"""25.1 节的计算：前向递推运动旋量与加速度。

(1) 表 25.1.1：书中 UR5e 模型的连杆坐标系 {i}（MJCF 的 body 坐标系）——关节轴 ω_i、零位时 {i−1} 在 {i} 中的位姿 M_{i,i−1}；
    由它们算出的空间旋量轴 S_i = [Ad_{M_{0i}}]A_i 与表 12.1.1 一致。
(2) 算例 25.1.1：第 22 章上下料动作（A → B，五次多项式，最短时间 T）中 t = 0.40 s 时刻，前向递推求各连杆的运动旋量和加速度；
    法兰的运动旋量与物体雅可比 J_b θ̇（第 16 章）比较，各连杆的 (ω, v)、(ω̇, a) 与 MuJoCo 的 mj_objectVelocity、mj_objectAcceleration 比较
    （a 是连杆坐标系原点的加速度：a = v̇ + ω × v，式 (25.1.6)）。
(3) 重力的处理（25.1.5 节）：取 𝒱̇₀ = (0, −𝔤) 与 𝒱̇₀ = 0 时 a 之差恰为 −Rᵀ𝔤；MuJoCo 的连杆加速度也含这一项。
(4) 整个动作中 TCP 的速度与各关节的贡献（图 25.1.2 的数据）：速度最大的时刻，每个关节单独转动产生的 TCP 速度。
(5) 习题答案。
"""
import math

import numpy as np

from _ch25 import (G0, TCP, adjoint, cell_move, inv, mj_link_motion, quintic, ur_chain, ur_mj, UR_S)
from bookout import out, tex, vec

deg = np.degrees
ch = ur_chain()
mj, m, d = ur_mj()
n = ch.n

# ---------------------------------------------------------------- (1) 表 25.1.1


def fmt_vec(v, k=3):
    s = []
    for x in v:
        x = 0.0 if abs(x) < 1e-12 else float(x)
        s.append(("−" if x < 0 else "") + (f"{abs(x):.{k}f}".rstrip("0").rstrip(".") if x != 0 else "0"))
    return "(" + ", ".join(s) + ")"


AXN = {(1, 0, 0): "x", (0, 1, 0): "y", (0, 0, 1): "z"}


def describe_R(R):
    """R 写成“绕某坐标轴转某角”（本模型的 R 都是这样）。"""
    if np.allclose(R, np.eye(3)):
        return "I"
    ang = math.acos(max(-1.0, min(1.0, (np.trace(R) - 1) / 2)))
    if abs(ang - math.pi) < 1e-9:
        w = np.sqrt(np.maximum(np.diag(R) + 1, 0) / 2)
    else:
        w = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / (2 * math.sin(ang))
    w = np.round(w, 9)
    k = int(np.argmax(np.abs(w)))
    assert abs(abs(w[k]) - 1) < 1e-9
    sgn = 1 if w[k] > 0 else -1
    a = round(deg(ang) * sgn)
    return f"R_{'xyz'[k]}({a}°)".replace("-", "−")


rows = {}
T0 = np.eye(4)
err_S = 0.0
for i in range(n):
    Mi = ch.Mi[i]
    rows[f"w{i + 1}"] = fmt_vec(ch.A[i][:3], 0)
    rows[f"p{i + 1}"] = fmt_vec(Mi[:3, 3])
    rows[f"R{i + 1}"] = describe_R(Mi[:3, :3])
    T0 = T0 @ inv(Mi)                                   # M_{0i} = M_{0,i−1} M_{i−1,i}
    S = adjoint(T0) @ ch.A[i]
    err_S = max(err_S, float(np.abs(S - UR_S[i]).max()))
assert err_S < 1e-12

# ---------------------------------------------------------------- (2) 算例 25.1.1
thA, thB, T_move = cell_move()
t1 = 0.40
q, qd, qdd = quintic(thA, thB, T_move, t1)
Ts, Vs, Vds = ch.forward(q, qd, qdd)
Tf6 = inv(ch.Mf)                                         # {6} 在 {f} 中的位姿
Vf = adjoint(Tf6) @ Vs[-1]
Jf = adjoint(Tf6) @ ch.jacobians(q)[-1]
err_J = float(np.abs(Jf @ qd - Vf).max())
err_V = err_A = 0.0
for i, name in enumerate(ch.names):
    v_mj, a_mj = mj_link_motion(mj, m, d, name, q, qd, qdd)
    w, v = Vs[i][:3], Vs[i][3:]
    acl = Vds[i][3:] + np.cross(w, v)                   # 原点的加速度 a = v̇ + ω × v（式 (25.1.6)）
    err_V = max(err_V, float(np.abs(Vs[i] - v_mj).max()))
    err_A = max(err_A, float(np.abs(np.r_[Vds[i][:3], acl] - a_mj).max()))
assert err_J < 1e-12 and err_V < 1e-12 and err_A < 1e-10
w6, v6 = Vs[-1][:3], Vs[-1][3:]
# 法兰（{f} 原点）
wf, vf = Vf[:3], Vf[3:]
Vdf = adjoint(Tf6) @ Vds[-1]
af = Vdf[3:] + np.cross(wf, vf)
# 重力的处理：𝒱̇₀ = 0 时
_, _, Vds0 = ch.forward(q, qd, qdd, Vd0=np.zeros(6))
Vdf0 = adjoint(Tf6) @ Vds0[-1]
af0 = Vdf0[3:] + np.cross(wf, vf)
T0f = ch.flange_pose(q)
g_in_f = T0f[:3, :3].T @ np.array([0, 0, G0])            # 向上 𝔤 在 {f} 中的分量
err_grav = float(np.abs((af - af0) - g_in_f).max())
assert err_grav < 1e-12

# ---------------------------------------------------------------- (4) 整个动作中 TCP 的速度，各关节的贡献
r_tcp = np.array([0, TCP, 0])                            # TCP 在 {f} 中
ts = np.linspace(0, T_move, 1319)
speed = []
for t in ts:
    qq, qqd, _ = quintic(thA, thB, T_move, t)
    J = adjoint(Tf6) @ ch.jacobians(qq)[-1]
    V = J @ qqd
    speed.append(np.linalg.norm(V[3:] + np.cross(V[:3], r_tcp)))
speed = np.array(speed)
k_pk = int(np.argmax(speed))
t_pk = ts[k_pk]
v_pk = speed[k_pk]
qq, qqd, _ = quintic(thA, thB, T_move, t_pk)
J = adjoint(Tf6) @ ch.jacobians(qq)[-1]
contrib = np.array([np.linalg.norm(J[3:, j] * qqd[j] + np.cross(J[:3, j] * qqd[j], r_tcp)) for j in range(n)])
sum_contrib = float(contrib.sum())
j_big = int(np.argmax(contrib)) + 1

# ---------------------------------------------------------------- (5) 习题答案
# 习题 25.1.3：只转关节 1（θ̇₁ = 1 rad/s），各连杆角速度大小都是 1 rad/s
_, Vs1, _ = ch.forward(q, np.array([1.0, 0, 0, 0, 0, 0]), np.zeros(6), Vd0=np.zeros(6))
assert all(abs(np.linalg.norm(V[:3]) - 1) < 1e-12 for V in Vs1)
# 习题 25.1.4：关节匀速转动（θ̈ = 0），法兰原点的加速度不为零
_, _, Vdc = ch.forward(q, qd, np.zeros(6), Vd0=np.zeros(6))
Vdc_f = adjoint(Tf6) @ Vdc[-1]
a_const = float(np.linalg.norm(Vdc_f[3:] + np.cross(wf, vf)))

out(err_S=err_S, t1=t1, T_move=T_move,
    q1=tex(deg(q).reshape(1, -1), 2), qd1=tex(qd.reshape(1, -1), 3), qdd1=tex(qdd.reshape(1, -1), 3),
    Vf=tex(Vf.reshape(1, -1), 4), wf_n=float(np.linalg.norm(wf)), vf_n=float(np.linalg.norm(vf)),
    Vdf=tex(Vdf.reshape(1, -1), 3), af=vec(af, 3), af_n=float(np.linalg.norm(af)), af0_n=float(np.linalg.norm(af0)),
    err_J=err_J, err_V=err_V, err_A=err_A, err_grav=err_grav,
    t_pk=t_pk, v_pk=v_pk, c1=contrib[0], c2=contrib[1], c3=contrib[2], c4=contrib[3], c5=contrib[4], c6=contrib[5],
    sum_contrib=sum_contrib, j_big=j_big, a_const=a_const, **rows)
