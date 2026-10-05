"""16.2 节：解析雅可比与几何雅可比的关系。

(1) 几何雅可比 J_g：行为 (ω_s, ṗ)，ṗ 是法兰盘中心的速度。核对 J_g = [[I, 0], [−[p], I]] J_s = diag(R, R) J_b，
    第 i 列为 (ω_i, ω_i × (p − q_i))；J_g 与 J_b 的奇异值相同。
(2) ZYX 欧拉角：ω_s = B(η) η̇，det B = −cos β；解析雅可比 J_a = diag(B⁻¹, I) J_g，用零件库模型的差商核对（算例 16.2.2）。
(3) 指数坐标（UR 示教器上的旋转矢量）：ω_s = A(r) ṙ，A = I + (1 − cos φ)/φ² [r] + (φ − sin φ)/φ³ [r]²，
    det A = 2(1 − cos φ)/φ²；J_a = diag(A⁻¹, I) J_g，差商核对。
(4) 算例 16.2.3：法兰盘中心不动、以 20°/s 绕一根水平轴转动 180°，转轴与 z_b 相差 1°，俯仰角 β 最大到 89°：
    欧拉角速率的峰值、指数坐标速率的峰值、关节转速的峰值；最大 β 处 J_g 与 J_a 的条件数。
"""
import math

import numpy as np

from _jac import (A_exp, gimbal_path, B_zyx, R_zyx, TH_STAR, UR_Q, UR_S, UR_W, act, euler_zyx, exp6, jacobian_body, logR, rot, skew, svals,
                  ur_fk, ur_jb, ur_jg, ur_js, ur_model)
from bookout import T as tr, out, tex, vec

deg = np.degrees
th = TH_STAR.copy()
Tm = ur_fk(th)
R, p = Tm[:3, :3], Tm[:3, 3]
Jg = ur_jg(th)

# ---------------------------------------------------------------- (1) 几何雅可比
P1 = np.eye(6)
P1[3:, :3] = -skew(p)
P2 = np.zeros((6, 6))
P2[:3, :3] = R
P2[3:, 3:] = R
e_g1 = float(np.abs(Jg - P1 @ ur_js(th)).max())
e_g2 = float(np.abs(Jg - P2 @ ur_jb(th)).max())
E = np.eye(4)
e_col = 0.0
for i in range(6):
    w = E[:3, :3] @ UR_W[i]
    q = act(E, UR_Q[i])
    e_col = max(e_col, float(np.abs(Jg[:, i] - np.r_[w, np.cross(w, p - q)]).max()))
    E = E @ exp6(UR_S[i], th[i])
assert e_g1 < 1e-14 and e_g2 < 1e-14 and e_col < 1e-14
assert np.abs(svals(Jg) - svals(ur_jb(th))).max() < 1e-12
# 差商：角速度用 Ṙ Rᵀ，线速度用法兰盘中心位置的差商（零件库模型）
model = ur_model()
h = 1e-6
Jg_n = np.zeros((6, 6))
for i in range(6):
    d = np.zeros(6)
    d[i] = h
    Ta, Tb = model.fk(th + d), model.fk(th - d)
    W = (Ta[:3, :3] - Tb[:3, :3]) / (2 * h) @ R.T
    Jg_n[:, i] = np.r_[W[2, 1], W[0, 2], W[1, 0], (Ta[:3, 3] - Tb[:3, 3]) / (2 * h)]
e_gn = float(np.abs(Jg - Jg_n).max())
assert e_gn < 1e-8

# ---------------------------------------------------------------- (2) ZYX 欧拉角
eta = euler_zyx(R)
assert np.abs(R_zyx(eta) - R).max() < 1e-14
B = B_zyx(eta)
rng = np.random.default_rng(162)
e_B, e_detB = 0.0, 0.0
for _ in range(200):
    e0 = rng.uniform([-math.pi, -1.5, -math.pi], [math.pi, 1.5, math.pi])
    ed = rng.normal(size=3)
    Rd = (R_zyx(e0 + h * ed) - R_zyx(e0 - h * ed)) / (2 * h)
    W = Rd @ R_zyx(e0).T
    e_B = max(e_B, float(np.abs(np.array([W[2, 1], W[0, 2], W[1, 0]]) - B_zyx(e0) @ ed).max()))
    e_detB = max(e_detB, abs(np.linalg.det(B_zyx(e0)) + math.cos(e0[1])))
assert e_B < 1e-8 and e_detB < 1e-14
Ja = np.zeros((6, 6))
Ja[:3] = np.linalg.solve(B, Jg[:3])
Ja[3:] = Jg[3:]
# 差商：x(θ) = (η(θ), p(θ))，由零件库模型算出
Ja_n = np.zeros((6, 6))
for i in range(6):
    d = np.zeros(6)
    d[i] = h
    Ta, Tb = model.fk(th + d), model.fk(th - d)
    Ja_n[:, i] = np.r_[(euler_zyx(Ta[:3, :3]) - euler_zyx(Tb[:3, :3])) / (2 * h), (Ta[:3, 3] - Tb[:3, 3]) / (2 * h)]
e_an = float(np.abs(Ja - Ja_n).max())
assert e_an < 1e-8

# ---------------------------------------------------------------- (3) 指数坐标（旋转矢量）
r = logR(R)
phi = float(np.linalg.norm(r))
A = A_exp(r)
e_A, e_detA = 0.0, 0.0
for _ in range(200):
    r0 = rng.normal(size=3)
    r0 *= rng.uniform(0.05, 3.0) / np.linalg.norm(r0)
    rd = rng.normal(size=3)
    f = lambda x: rot(x / np.linalg.norm(x), np.linalg.norm(x))
    W = (f(r0 + h * rd) - f(r0 - h * rd)) / (2 * h) @ f(r0).T
    e_A = max(e_A, float(np.abs(np.array([W[2, 1], W[0, 2], W[1, 0]]) - A_exp(r0) @ rd).max()))
    ph = np.linalg.norm(r0)
    e_detA = max(e_detA, abs(np.linalg.det(A_exp(r0)) - 2 * (1 - math.cos(ph)) / ph ** 2))
assert e_A < 1e-8 and e_detA < 1e-12
Jr = np.zeros((6, 6))
Jr[:3] = np.linalg.solve(A, Jg[:3])
Jr[3:] = Jg[3:]
Jr_n = np.zeros((6, 6))
for i in range(6):
    d = np.zeros(6)
    d[i] = h
    Ta, Tb = model.fk(th + d), model.fk(th - d)
    Jr_n[:, i] = np.r_[(logR(Ta[:3, :3]) - logR(Tb[:3, :3])) / (2 * h), (Ta[:3, 3] - Tb[:3, 3]) / (2 * h)]
e_rn = float(np.abs(Jr - Jr_n).max())
assert e_rn < 1e-8
detA = 2 * (1 - math.cos(phi)) / phi ** 2


# ---------------------------------------------------------------- (4) 算例 16.2.3：绕水平轴转过万向节锁附近（gimbal_path 见 _jac.py）
H, u = gimbal_path()
bmax = float(deg(H["eta"][:, 1].max()))
kmax = int(np.argmax(H["eta"][:, 1]))
assert abs(bmax - 89.0) < 1e-3
pk_a = float(deg(np.abs(H["etad"][:, 0]).max()))
pk_g = float(deg(np.abs(H["etad"][:, 2]).max()))
pk_r = float(deg(np.abs(H["rd"]).max()))
pk_q = float(deg(np.abs(H["qd"]).max()))
p_drift = float(np.linalg.norm(H["p"] - H["p"][0], axis=1).max())
assert p_drift < 1e-8
# 理论值：ω cos β / … ；在 β 最大处 α̇ ≈ ω/ sin δ（转轴偏 δ 时，见正文）
pred = 20.0 / math.sin(math.radians(1.0))
assert abs(pk_a - pred) / pred < 0.01
qk = H["q"][kmax]
Jgk = ur_jg(qk)
ek = euler_zyx(ur_fk(qk)[:3, :3])
Jak = np.vstack([np.linalg.solve(B_zyx(ek), Jgk[:3]), Jgk[3:]])
sg, sa = svals(Jgk), svals(Jak)
kg, ka = float(sg[0] / sg[-1]), float(sa[0] / sa[-1])
t_star = float(H["t"][kmax])
smin_min = float(np.min(H["smin"]))
q_end = deg(H["q"][-1])
# 旋转矢量在转角经过 π 时整体跳到反方向：找出跳变的时刻
RV = np.array([logR(ur_fk(qq)[:3, :3]) for qq in H["q"]])
kj = int(np.argmax(np.linalg.norm(np.diff(RV, axis=0), axis=1)))
assert np.linalg.norm(RV[kj + 1] - RV[kj]) > 5.0                  # 从 πω̂ 跳到 −πω̂，跳变量约 2π
t_jump = float(H["t"][kj + 1])

out(Jg=tex(Jg, 4), e_g1=e_g1, e_g2=e_g2, e_gn=e_gn, p=vec(p, 4),
    eta=vec(deg(eta), 2), B=tex(B, 4), Ja=tex(Ja, 4), e_an=e_an, e_B=e_B, condB=float(np.linalg.cond(B)),
    r=vec(r, 4), phi_deg=float(deg(phi)), detA=detA, e_A=e_A, e_rn=e_rn, Jr=tex(Jr, 4),
    bmax=bmax, pk_a=pk_a, pk_g=pk_g, pk_r=pk_r, pk_q=pk_q, pred=pred, p_drift=p_drift, kg=kg, ka=ka, t_star=t_star,
    smin_min=smin_min, t_jump=t_jump, u=vec(u, 4), q_end=vec(q_end, 1), cosb=math.cos(math.radians(bmax)))
