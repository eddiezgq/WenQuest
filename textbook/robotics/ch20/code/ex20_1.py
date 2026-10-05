"""20.1 节的计算：Go2 一条腿的正运动学、逆运动学、足端雅可比与站立时的关节力矩。

算例 20.1.1  左前腿的三个旋量轴与零位；站立姿态下足端的位置：闭式 (20.1.5)、(20.1.6)，指数积 (20.1.4)、零件库关节表三种算法核对。
算例 20.1.2  把左前足放到落脚点 p_d = (0.28, 0.17, −0.22) m：定理 20.1.2 的四组解，只有一组在限位内（定理 20.1.3）。
算例 20.1.3  站立姿态的足端雅可比、行列式（定理 20.1.4 与数值行列式、差商核对）；站立时每条腿的关节力矩 τ = Jᵀ f（16.5 节），
            与电机的力矩上限比较；机身降低时小腿关节力矩怎样变化。
另：足端中心到大腿关节的距离范围（工作空间的内外半径），由小腿关节的限位决定。
"""
import math

import numpy as np

from _leg import (AX, AY, DY, G, GO2, GO2_FOOT_R, GO2_TAU_MAX, L1, L2, LEGS, MASS_GO2, TH_REST, fk_links, hip, in_limits,
                  leg_fk, leg_fk_poe, leg_ik, leg_ik_all, leg_jac, leg_screws, limits, to_limits)
from bookout import T, out, tex

deg = math.degrees

# ---------------------------------------------------------------- 算例 20.1.1
S, M, (q1, q2, q3) = leg_screws("FL")
p_rest = leg_fk("FL", TH_REST)
p_poe = leg_fk_poe("FL", TH_REST)
q = {"FL_hip_joint": TH_REST[0], "FL_thigh_joint": TH_REST[1], "FL_calf_joint": TH_REST[2]}
p_tab = (fk_links(GO2, q)["FL_calf"] @ np.r_[0, 0, -0.213, 1])[:3]
assert np.allclose(p_rest, p_poe, atol=1e-12) and np.allclose(p_rest, p_tab, atol=1e-12)
for leg in LEGS:                                             # 四条腿的闭式与指数积在随机关节角上一致
    rng = np.random.default_rng(1)
    for _ in range(200):
        th = rng.uniform(limits(leg)[:, 0], limits(leg)[:, 1])
        assert np.allclose(leg_fk(leg, th), leg_fk_poe(leg, th), atol=1e-12)
h_hip = -p_rest[2]                                           # 足端中心在大腿关节下方的深度（= 1.6 节的 h）
h_body = h_hip + GO2_FOOT_R                                  # 机身原点离地高度：足端小球半径 0.022 m 落在地面上

# ---------------------------------------------------------------- 算例 20.1.2
p_d = np.array([0.28, 0.17, -0.22])
sols = leg_ik_all("FL", p_d)
assert len(sols) == 4
rows = []
for s, zs, ks in sols:
    assert np.linalg.norm(leg_fk("FL", s) - p_d) < 1e-12
    rows.append((s, zs, ks, in_limits("FL", to_limits("FL", s))))
ok = [r for r in rows if r[3]]
assert len(ok) == 1 and ok[0][1] == -1 and ok[0][2] == -1      # 只有“足在下、膝向后”的一组在限位内
th_d = ok[0][0]
r_d = p_d - hip("FL")
zp_d = -math.sqrt(r_d[1] ** 2 + r_d[2] ** 2 - DY ** 2)
D_d = math.hypot(r_d[0], zp_d)
lim = limits("FL")
sol_tab = "；".join(f"({deg(s[0]):.2f}°, {deg(s[1]):.2f}°, {deg(s[2]):.2f}°)".replace("-", "−") for s, _, _, _ in rows)

# 由小腿关节的限位得到足端中心到大腿关节距离 D 的范围（式 (20.1.7)）
D_max = math.sqrt(L1 ** 2 + L2 ** 2 + 2 * L1 * L2 * math.cos(lim[2, 1]))
D_min = math.sqrt(L1 ** 2 + L2 ** 2 + 2 * L1 * L2 * math.cos(lim[2, 0]))
assert abs(D_max - 2 * L1 * math.cos(lim[2, 1] / 2)) < 1e-12

# 随机抽样（定理 20.1.3）：足端到髋外摆轴的距离 ρ > 2d 时，限位内恰有一组解；ρ ≤ 2d 时可能有两组
rng = np.random.default_rng(7)
n_chk, n_far, n_two = 20000, 0, 0
for _ in range(n_chk):
    th = rng.uniform(lim[:, 0], lim[:, 1])
    p = leg_fk("FL", th)
    r = p - hip("FL")
    inside = [x for x in (to_limits("FL", s) for s, _, _ in leg_ik_all("FL", p)) if in_limits("FL", x)]
    assert any(np.allclose(x, th, atol=1e-8) for x in inside) and len(inside) <= 2
    if math.hypot(r[1], r[2]) > 2 * DY:
        assert len(inside) == 1
        n_far += 1
    elif len(inside) == 2:
        n_two += 1
for leg in ("FR", "RL", "RR"):                          # 其余三条腿（后腿的大腿关节限位不同，右腿镜像）同样检验定理 20.1.3
    lim_l = limits(leg)
    for _ in range(3000):
        th = rng.uniform(lim_l[:, 0], lim_l[:, 1])
        p = leg_fk(leg, th)
        r = p - hip(leg)
        inside = [x for x in (to_limits(leg, s) for s, _, _ in leg_ik_all(leg, p)) if in_limits(leg, x)]
        assert any(np.allclose(x, th, atol=1e-8) for x in inside)
        if math.hypot(r[1], r[2]) > 2 * DY:
            assert len(inside) == 1
rho_rest = math.hypot(*(p_rest - hip("FL"))[1:])

# ---------------------------------------------------------------- 算例 20.1.3
J = leg_jac("FL", TH_REST)
eps = 1e-7
Jn = np.column_stack([(leg_fk("FL", TH_REST + eps * e) - leg_fk("FL", TH_REST - eps * e)) / (2 * eps) for e in np.eye(3)])
assert np.allclose(J, Jn, atol=1e-8)
t1, t2, t3 = TH_REST
zp = -L1 * math.cos(t2) - L2 * math.cos(t2 + t3)
det_formula = -L1 * L2 * zp * math.sin(t3)                  # 定理 20.1.4
assert abs(np.linalg.det(J) - det_formula) < 1e-14
rng = np.random.default_rng(3)
for _ in range(500):
    th = rng.uniform(lim[:, 0], lim[:, 1])
    zp_ = -L1 * math.cos(th[1]) - L2 * math.cos(th[1] + th[2])
    assert abs(np.linalg.det(leg_jac("FL", th)) + L1 * L2 * zp_ * math.sin(th[2])) < 1e-13
sin_min = min(abs(math.sin(lim[2, 0])), abs(math.sin(lim[2, 1])))   # 限位内 |sin θ3| 的最小值

F = MASS_GO2 * G / 4                                         # 每只脚承受机身重量的四分之一（设，见正文）
f_apply = np.array([0, 0, -F])                               # 足对地面施加的力（16.5 节的约定）
tau = J.T @ f_apply
# 另一条路：虚功原理，各关节分别转一个小角度，足端位移点乘力
tau_vw = np.array([f_apply @ (leg_fk("FL", TH_REST + eps * e) - leg_fk("FL", TH_REST - eps * e)) / (2 * eps) for e in np.eye(3)])
assert np.allclose(tau, tau_vw, atol=1e-6)
assert abs(tau[0] + F * DY) < 1e-12 and abs(tau[1]) < 1e-12          # 髋关节力矩 = F·d；足在大腿关节正下方，大腿关节力矩为零
knee_arm = L2 * math.sin(-(t2 + t3))                          # 小腿关节到足端中心的水平距离
assert abs(tau[2] - F * knee_arm) < 1e-12

# 机身降低（足端仍在大腿关节正下方）时的小腿关节力矩
heights = np.arange(0.10, 0.40001, 0.0025)
knee = []
for h in heights:
    s = leg_ik("FL", np.array([AX, AY + DY, -h]))
    knee.append(np.nan if s is None else float((leg_jac("FL", s).T @ f_apply)[2]))
knee = np.array(knee)
h_low = 0.12
s_low = leg_ik("FL", np.array([AX, AY + DY, -h_low]))
tau_low = leg_jac("FL", s_low).T @ f_apply
assert abs(tau_low[2]) < GO2_TAU_MAX["calf"]
datasheet_torque = 45                                         # 厂家参数表：最大关节扭矩约 45 N·m（entry.json 的 datasheet 说明）

out(ax=AX, ay=AY, dy=DY, l1=L1, l2=L2, foot_r=GO2_FOOT_R,
    S1=tex(S[0], 4), S2=tex(S[1], 4), S3=tex(S[2], 4), M=tex(M, 4), Mz=M[2],
    th_rest_deg=tex(np.degrees(TH_REST), 2), p_rest=tex(p_rest, 4), h_hip=h_hip, h_body=h_body,
    pdx=p_d[0], pdy=p_d[1], pdz=p_d[2],
    rdy=r_d[1], rdz=r_d[2], zp_d=zp_d, xp_d=r_d[0], D_d=D_d,
    th1_d=deg(th_d[0]), th2_d=deg(th_d[1]), th3_d=deg(th_d[2]),
    sol_tab=sol_tab, sols=[[deg(v) for v in r[0]] + [r[1], r[2], r[3]] for r in rows],
    lim_hip=deg(lim[0, 1]), lim_thigh_lo=deg(lim[1, 0]), lim_thigh_hi=deg(lim[1, 1]),
    lim_calf_lo=deg(lim[2, 0]), lim_calf_hi=deg(lim[2, 1]),
    lim_thigh_rear_lo=deg(limits("RL")[1, 0]), lim_thigh_rear_hi=deg(limits("RL")[1, 1]),
    lim_hip_sheet=GO2["datasheet"]["axes"][0]["range_deg"][1],
    D_max=D_max, D_min=D_min, n_chk=n_chk, n_far=n_far, n_two=n_two, rho_rest=rho_rest, two_d=2 * DY, sqrt3d=math.sqrt(3) * DY,
    J=tex(J, 4), detJ=float(np.linalg.det(J)), det_formula=det_formula, zp_rest=zp, sin_min=sin_min,
    mass=MASS_GO2, F=F, tau1=tau[0], tau2=tau[1], tau3=tau[2], knee_arm=knee_arm,
    h_low=h_low, h_low_body=h_low + GO2_FOOT_R, tau3_low=tau_low[2], th2_low=deg(s_low[1]), th3_low=deg(s_low[2]),
    tau_max_hip=GO2_TAU_MAX["hip"], tau_max_calf=GO2_TAU_MAX["calf"], datasheet_torque=datasheet_torque,
    note=T("闭式、指数积、关节表三种算法一致", "closed form, PoE and joint table agree"))
