"""16.3 节：奇异性及其物理意义。

(1) 算例 16.3.1：平面 2R 臂（0.425、0.392 m）伸直，θ = (30°, 0)：J 的秩、零空间（自运动）、失去的方向（左零空间）、
    由结构承受的力 F（Jᵀ F = 0）；接近伸直（θ₂ = 2°、1°、0.5°）时，末端沿径向以 0.1 m/s 运动所需的关节速度 ∝ 1/sin θ₂。
(2) 定理 16.3.3：UR5e 的 det J = −L1 L2 sin θ3 sin θ5 · r(θ)，r = −L1 cos θ2 − L2 cos(θ2+θ3) + H2 sin(θ2+θ3+θ4)，
    用 2000 组随机关节角核对；r 是手腕点到“过基座轴线、垂直于手臂平面的竖直平面”的带号距离，ρ² = r² + d4²。
(3) 算例 16.3.2：从 θ* 出发分别令 θ3 = 0、θ5 = 0、r = 0（解 θ2），得到三类奇异位形：奇异值、零空间、左零空间；
    肩部奇异与手腕奇异的左零空间是一个纯力（节距为零），作用线与六根轴都相交或平行；肘部奇异时轴 2 到轴 4 的距离已达最大值 L1 + L2，对各关节角的导数为零。
(4) 接近奇异：最小奇异值与各因子成正比（图 16.3.3）。
"""
import math

import numpy as np

from _jac import (D4, H2, L1, L2, TH_STAR, UR_Q, UR_S, act, exp6, jac_2r, rotz, svals, ur_det, ur_det_factors, ur_fk, ur_js,
                  ur_shoulder_r, ur_wrist_point)
from bookout import out, tex, vec

deg = np.degrees
LL = (0.425, 0.392)

# ---------------------------------------------------------------- (1) 平面 2R 臂伸直
th = np.radians([30.0, 0.0])
J = jac_2r(th)
U, s, Vt = np.linalg.svd(J)
assert s[1] < 1e-15 and abs(np.linalg.det(J)) < 1e-15
nul = Vt[-1] * np.sign(Vt[-1][0])                      # 零空间：末端不动的关节速度方向
nul_ratio = float(nul[1] / nul[0])
assert abs(nul_ratio + (LL[0] + LL[1]) / LL[1]) < 1e-12
lost = U[:, -1] * np.sign(U[0, -1])                    # 失去的方向：沿手臂的径向
radial = np.array([math.cos(th[0]), math.sin(th[0])])
assert abs(abs(lost @ radial) - 1) < 1e-12
assert np.abs(J.T @ radial).max() < 1e-15             # 沿手臂的力不需要关节力矩
reach_dir = U[:, 0] * np.sign(U[1, 0])
# 接近伸直：沿径向 0.1 m/s 所需的关节速度
near = []
for t2 in (2.0, 1.0, 0.5):
    t = np.radians([30.0, t2])
    Jt = jac_2r(t)
    p = np.array([LL[0] * math.cos(t[0]) + LL[1] * math.cos(t[0] + t[1]), LL[0] * math.sin(t[0]) + LL[1] * math.sin(t[0] + t[1])])
    v = 0.1 * p / np.linalg.norm(p)
    qd = np.linalg.solve(Jt, v)
    near.append((t2, float(svals(Jt)[-1]), float(np.linalg.norm(deg(qd)))))
r21 = near[0][2] / near[1][2]
r32 = near[1][2] / near[2][2]
assert 1.9 < 1 / r21 < 2.1 and 1.9 < 1 / r32 < 2.1      # 角度减半，所需速度加倍

# ---------------------------------------------------------------- (2) det J 的因式分解
rng = np.random.default_rng(163)
e_det, e_r, e_rho = 0.0, 0.0, 0.0
for _ in range(2000):
    q = rng.uniform(-math.pi, math.pi, 6)
    s3, s5, r = ur_det_factors(q)
    e_det = max(e_det, abs(ur_det(q) + L1 * L2 * s3 * s5 * r))
    e_r = max(e_r, abs(r - ur_shoulder_r(q)))
    pw = ur_wrist_point(q)
    e_rho = max(e_rho, abs(pw[0] ** 2 + pw[1] ** 2 - r * r - D4 * D4))
assert e_det < 1e-14 and e_r < 1e-14 and e_rho < 1e-14
s3, s5, r_star = ur_det_factors(TH_STAR)
det_star = ur_det(TH_STAR)

# ---------------------------------------------------------------- (3) 三类奇异位形
def bisect(f, a, b, n=200):
    fa = f(a)
    for _ in range(n):
        m = (a + b) / 2
        if fa * f(m) <= 0:
            b = m
        else:
            a, fa = m, f(m)
    return (a + b) / 2


cases = {}
q_el = TH_STAR.copy()
q_el[2] = 0.0
q_wr = TH_STAR.copy()
q_wr[4] = 0.0
f_sh = lambda t2: ur_shoulder_r(np.r_[TH_STAR[0], t2, TH_STAR[2:]])
t2_sh = bisect(f_sh, math.radians(-170), math.radians(-100))
q_sh = TH_STAR.copy()
q_sh[1] = t2_sh
for name, q in (("el", q_el), ("wr", q_wr), ("sh", q_sh)):
    Jq = ur_js(q)
    U, s, Vt = np.linalg.svd(Jq)
    n = Vt[-1] / np.abs(Vt[-1]).max()
    F = U[:, -1]
    cases[name] = dict(q=q, s=s, n=n, F=F, rank=int(np.sum(s > 1e-10 * s[0])))
    assert cases[name]["rank"] == 5 and s[-1] < 1e-14
    assert np.abs(Jq.T @ F).max() < 1e-14                 # 左零空间中的力旋量：所有关节力矩为零

# 肩部奇异：左零空间是一个纯力，沿 ŷ′ = Rot(ẑ, θ1)(0, −1, 0)，作用线经过手腕点 P56，并与基座轴线相交
y1 = rotz(TH_STAR[0]) @ np.array([0, -1.0, 0])
F = cases["sh"]["F"]
m, f = F[:3], F[3:]
f_u = f / np.linalg.norm(f)
pitch_sh = float(m @ f / (f @ f))
pw_sh = ur_wrist_point(q_sh)
assert abs(abs(f_u @ y1) - 1) < 1e-12 and abs(pitch_sh) < 1e-14
assert np.linalg.norm(m - np.cross(pw_sh, f)) < 1e-14     # 力过 P56：m = P56 × f
hit_sh = float(pw_sh[2])                                  # 作用线与基座轴线（z 轴）交于高度 z = P56 的高度
assert abs(math.hypot(pw_sh[0], pw_sh[1]) - D4) < 1e-14  # 手腕点落在半径 d4 的圆柱面上（14.5.7 节）
# 手腕奇异：轴 2、3、4、6 平行；左零空间是平行于它们的纯力，与轴 1、轴 5 都相交
F = cases["wr"]["F"]
m, f = F[:3], F[3:]
pitch_wr = float(m @ f / (f @ f))
assert abs(pitch_wr) < 1e-14 and abs(abs(f / np.linalg.norm(f) @ y1) - 1) < 1e-12
Jw = ur_js(q_wr)
par = float(np.abs(np.cross(Jw[:3, 5], Jw[:3, 1])).max())  # 轴 6 与轴 2 平行
assert par < 1e-15
# 肘部奇异：J 的第 3 列减第 2 列与第 4 列减第 3 列平行（式 (16.3.4) 的 t3、t4）
Je = ur_js(q_el)
t3, t4 = Je[3:, 2] - Je[3:, 1], Je[3:, 3] - Je[3:, 2]
assert np.linalg.norm(np.cross(t3, t4)) < 1e-15
nel = cases["el"]["n"]
ratio_el = float(nel[1] / -nel[2])
assert abs(ratio_el - L2 / (L1 + L2)) < 1e-12
# 肘部奇异时，轴 2 与轴 4 之间的距离（在手臂平面内）已是最大值 L1 + L2：它对每个关节角的导数都为零
def axis24(q):
    E1 = exp6(UR_S[0], q[0])
    E123 = E1 @ exp6(UR_S[1], q[1]) @ exp6(UR_S[2], q[2])
    d = act(E123, UR_Q[3]) - act(E1, UR_Q[1])
    y = rotz(q[0]) @ np.array([0, -1.0, 0])
    return float(np.linalg.norm(d - y * (d @ y)))


d24 = axis24(q_el)
assert abs(d24 - (L1 + L2)) < 1e-14
grad = []
for i in range(6):
    e = np.zeros(6)
    e[i] = 1e-6
    grad.append((axis24(q_el + e) - axis24(q_el - e)) / 2e-6)
lost_el = float(np.abs(grad).max())
assert lost_el < 1e-8

# ---------------------------------------------------------------- (4) 接近奇异：σ_min 与因子成正比
slopes = {}
for name, k, base in (("el", 2, TH_STAR), ("wr", 4, TH_STAR)):
    xs, ys = [], []
    for e in np.logspace(-4, -1, 7):
        q = base.copy()
        q[k] = e
        xs.append(abs(math.sin(e)))
        ys.append(svals(ur_js(q))[-1])
    slopes[name] = float(np.polyfit(np.log(xs), np.log(ys), 1)[0])
xs, ys = [], []
for e in np.logspace(-4, -1, 7):
    q = q_sh.copy()
    q[1] += e
    xs.append(abs(ur_shoulder_r(q)))
    ys.append(svals(ur_js(q))[-1])
slopes["sh"] = float(np.polyfit(np.log(xs), np.log(ys), 1)[0])
assert all(abs(v - 1) < 0.01 for v in slopes.values())
sv_wr1 = float(svals(ur_js(np.r_[TH_STAR[:4], math.radians(1), TH_STAR[5]]))[-1])

fmt = lambda v: ", ".join(f"{x:.4f}" for x in v)
out(J2=tex(J, 4), nul=vec(nul / abs(nul[0]), 4), nul_ratio=nul_ratio, lost=vec(lost, 4), reach=vec(reach_dir, 4),
    n2_sv=near[0][1], n2_qd=near[0][2], n1_qd=near[1][2], n05_qd=near[2][2],
    e_det=e_det, e_rho=e_rho, det_star=det_star, r_star=r_star, L1L2=L1 * L2,
    sv_el=fmt(cases["el"]["s"][:5]), sv_wr=fmt(cases["wr"]["s"][:5]), sv_sh=fmt(cases["sh"]["s"][:5]),
    n_el=vec(cases["el"]["n"], 4), n_wr=vec(cases["wr"]["n"], 4), n_sh=vec(cases["sh"]["n"], 4), ratio_el=ratio_el,
    t2_sh=float(deg(t2_sh)), pw_sh=vec(pw_sh, 4), hit_sh=hit_sh, y1=vec(y1, 4), pitch_sh=pitch_sh,
    F_sh=vec(cases["sh"]["F"] / np.abs(cases["sh"]["F"]).max(), 4), F_wr=vec(cases["wr"]["F"] / np.abs(cases["wr"]["F"]).max(), 4),
    q_sh=vec(deg(q_sh), 2), slope_el=slopes["el"], slope_wr=slopes["wr"], slope_sh=slopes["sh"], sv_wr1=sv_wr1, need_wr1=float(deg(0.1 / sv_wr1)), lost_el=lost_el)
