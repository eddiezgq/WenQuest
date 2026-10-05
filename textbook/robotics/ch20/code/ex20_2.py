"""20.2 节的计算：浮动基座。四只脚踩在地上不动，机身改变位姿时 12 个关节怎样变化；速度关系；腿式里程计与打滑的发现；
由关节角和落脚点反求机身位姿。

算例 20.2.1  机身横滚 8°、俯仰 −12°（抬头）、偏航 10°，并平移 (0.03, −0.02, −0.05) m：每条腿各解一次逆运动学，得 12 个关节角；
            用关节表的正运动学把脚放回 {s} 核对；机身单独俯仰、下蹲、升高各能到多大，受哪个限位约束。
算例 20.2.2  机身以运动旋量 V_b 运动、四只脚不动：由定理 20.2.1 求 12 个关节速度，与位姿差商核对。
算例 20.2.3  腿式里程计：由关节速度和陀螺仪的角速度估计机身速度；只有对角两只脚着地时，腿的运动学测不出绕对角线的转动
            （秩 5）；一只脚打滑时由残差找出它。
另：定理 20.2.4 的点集配准由关节角和落脚点求机身位姿；格吕布勒公式数自由度。
"""
import math

import numpy as np

from _leg import (GO2, GO2_FOOT_R, LEG_EN, LEG_ZH, LEGS, TH_REST, Tinv, Tm, body_from_feet, exp_twist, fk_links, go2_q, in_limits,
                  leg_fk, leg_ik, leg_jac, limits, rpy, skew, stance_ik)
from bookout import T, out, tex, vec

deg, rad = math.degrees, math.radians

h0 = -leg_fk("FL", TH_REST)[2] + GO2_FOOT_R                   # 站立时机身原点离地高度（算例 20.1.1）
feet_s = {leg: leg_fk(leg, TH_REST) + np.array([0, 0, h0]) for leg in LEGS}   # 四只脚的足端中心在 {s} 中的位置
T0 = Tm(np.eye(3), (0, 0, h0))

# ---------------------------------------------------------------- 格吕布勒公式 (11.2.1)：地面、机身、12 个连杆；12 个转动副 + 4 个点接触（球副）
N_bodies, J_rev, J_sph = 14, 12, 4
M_dof = 6 * (N_bodies - 1 - (J_rev + J_sph)) + (J_rev * 1 + J_sph * 3)
assert M_dof == 6
M_free = 6 * (N_bodies - 1 - J_rev) + J_rev          # 四只脚都离地（腾空）时：6 + 12 = 18
assert M_free == 18

# ---------------------------------------------------------------- 算例 20.2.1
roll, pitch, yaw = rad(8), rad(-12), rad(10)
dp = np.array([0.03, -0.02, -0.05])
T1 = Tm(rpy(roll, pitch, yaw), np.array([0, 0, h0]) + dp)
th1 = stance_ik(T1, feet_s)
assert not np.any(np.isnan(th1))
for i, leg in enumerate(LEGS):
    assert in_limits(leg, th1[3 * i:3 * i + 3])
Tl = fk_links(GO2, go2_q(th1), T1)                           # 关节表正运动学：脚回到原处
for leg in LEGS:
    assert np.linalg.norm((Tl[f"{leg}_calf"] @ np.r_[0, 0, -0.213, 1])[:3] - feet_s[leg]) < 1e-12
tab = {leg: [deg(v) for v in th1[3 * i:3 * i + 3]] for i, leg in enumerate(LEGS)}
pb1 = {leg: (Tinv(T1) @ np.r_[feet_s[leg], 1])[:3] for leg in LEGS}


def ok_pose(Tb):
    th = stance_ik(Tb, feet_s)
    if np.any(np.isnan(th)):
        return False, th
    return all(in_limits(leg, th[3 * i:3 * i + 3]) for i, leg in enumerate(LEGS)), th


def scan(make, lo, hi, n=4000):
    """make(s) 为机身位姿；在 [lo, hi] 中从 0 出发找第一个不可行的 s（二分细化）。"""
    xs = np.linspace(lo, hi, n)
    prev = xs[0]
    for x in xs:
        if not ok_pose(make(x))[0]:
            a, b = prev, x
            for _ in range(60):
                m = (a + b) / 2
                if ok_pose(make(m))[0]:
                    a = m
                else:
                    b = m
            return a
        prev = x
    return hi


pitch_up = scan(lambda s: Tm(rpy(0, -s, 0), (0, 0, h0)), 0, rad(60))       # 抬头（俯仰为负）
pitch_dn = scan(lambda s: Tm(rpy(0, s, 0), (0, 0, h0)), 0, rad(60))
roll_max = scan(lambda s: Tm(rpy(s, 0, 0), (0, 0, h0)), 0, rad(60))
yaw_max = scan(lambda s: Tm(rpy(0, 0, s), (0, 0, h0)), 0, rad(90))
z_low = h0 - scan(lambda s: Tm(np.eye(3), (0, 0, h0 - s)), 0, 0.25)
z_high = h0 + scan(lambda s: Tm(np.eye(3), (0, 0, h0 + s)), 0, 0.25)


def which_limit(Tb):
    """位姿 Tb 不可行的原因：哪条腿够不着，或哪个关节超限。"""
    Ti = Tinv(Tb)
    msgs = []
    for leg in LEGS:
        pb = (Ti @ np.r_[feet_s[leg], 1])[:3]
        s = leg_ik(leg, pb)
        if s is None:
            msgs.append((leg, "reach"))
    return msgs


why_up = which_limit(Tm(rpy(0, -(pitch_up + 1e-4), 0), (0, 0, h0)))
_, th_up = ok_pose(Tm(rpy(0, -pitch_up, 0), (0, 0, h0)))
_, th_low = ok_pose(Tm(np.eye(3), (0, 0, z_low)))
_, th_high = ok_pose(Tm(np.eye(3), (0, 0, z_high)))
lim = limits("FL")
assert abs(th_low[2] - lim[2, 0]) < 1e-6          # 下蹲到底：小腿关节到达 −156°
assert abs(th_high[2] - lim[2, 1]) < 1e-6         # 升到最高：小腿关节到达 −48°

# ---------------------------------------------------------------- 算例 20.2.2：速度
w_b = np.array([0.2, -0.3, 0.1])                   # rad/s（设）
v_b = np.array([0.05, 0.02, -0.04])                # m/s（设）
Vb = np.r_[w_b, v_b]
thd = []
for i, leg in enumerate(LEGS):
    th = th1[3 * i:3 * i + 3]
    rhs = skew(pb1[leg]) @ w_b - v_b                # 式 (20.2.4)：J_i θ̇_i = [p_i] ω_b − v_b
    thd.append(np.linalg.solve(leg_jac(leg, th), rhs))
thd = np.concatenate(thd)
h = 1e-6                                            # 差商：机身沿 V_b 走一小步（物体右乘 e^[V_b]h，6.4 节），重解逆运动学
th_p = stance_ik(T1 @ exp_twist(Vb, h), feet_s)
th_m = stance_ik(T1 @ exp_twist(Vb, -h), feet_s)
thd_fd = (th_p - th_m) / (2 * h)
assert np.allclose(thd, thd_fd, atol=1e-6)


# ---------------------------------------------------------------- 算例 20.2.3：腿式里程计
def A_of(legs, pb):
    """式 (20.2.6)：把 V_b = (ω_b, v_b) 映成各支撑腿“J_i θ̇_i”的矩阵（每条腿三行 [ [p_i], −I ]）。"""
    return np.vstack([np.hstack([skew(pb[leg]), -np.eye(3)]) for leg in legs])


A4 = A_of(LEGS, pb1)
y4 = np.concatenate([leg_jac(leg, th1[3 * i:3 * i + 3]) @ thd[3 * i:3 * i + 3] for i, leg in enumerate(LEGS)])
Vb_est, *_ = np.linalg.lstsq(A4, y4, rcond=None)
assert np.allclose(Vb_est, Vb, atol=1e-12) and np.linalg.matrix_rank(A4) == 6
# 只有对角两只脚（FL、RR）着地：秩 5，零空间是绕两只脚连线的转动
A2 = A_of(["FL", "RR"], pb1)
rank2 = np.linalg.matrix_rank(A2)
_, sv2, Vt2 = np.linalg.svd(A2)
nul = Vt2[-1]
diag_dir = (pb1["RR"] - pb1["FL"]) / np.linalg.norm(pb1["RR"] - pb1["FL"])
w_n = nul[:3] / np.linalg.norm(nul[:3])
assert rank2 == 5 and abs(abs(w_n @ diag_dir) - 1) < 1e-9
# 零空间运动下，两只脚的速度确为零：v + ω × p = 0
for leg in ("FL", "RR"):
    assert np.linalg.norm(nul[3:] + np.cross(nul[:3], pb1[leg])) < 1e-12
# 有陀螺仪时（ω_b 已知），两只脚就够了：v_b 由每条腿各给一次，取平均
v_from = [-(leg_jac(leg, th1[3 * i:3 * i + 3]) @ thd[3 * i:3 * i + 3]) - np.cross(w_b, pb1[leg]) for i, leg in enumerate(LEGS)]
assert all(np.allclose(v, v_b, atol=1e-12) for v in v_from)

# 右后脚在地面上沿 x_s 打滑 0.05 m/s：它的关节速度里多了这一项
slip_s = np.array([0.05, 0.0, 0.0])
slip_b = T1[:3, :3].T @ slip_s
y_slip = y4.copy()
y_slip[9:12] += slip_b                               # 腿 RR 的足端相对机身多了这一速度
Vb_s, *_ = np.linalg.lstsq(A4, y_slip, rcond=None)
res = A4 @ Vb_s - y_slip
res_leg = [float(np.linalg.norm(res[3 * k:3 * k + 3])) for k in range(4)]
assert int(np.argmax(res_leg)) == 3
err_v = float(np.linalg.norm(Vb_s[3:] - v_b))
err_w = float(np.linalg.norm(Vb_s[:3] - w_b))
# 剔除残差最大的一条腿后重估：恢复真值
Vb_3, *_ = np.linalg.lstsq(A_of(LEGS[:3], pb1), y_slip[:9], rcond=None)
assert np.allclose(Vb_3, Vb, atol=1e-12)

# ---------------------------------------------------------------- 定理 20.2.4：由关节角和落脚点求机身位姿
pb_from_joints = {leg: leg_fk(leg, th1[3 * i:3 * i + 3]) for i, leg in enumerate(LEGS)}
T_est = body_from_feet(pb_from_joints, feet_s)
assert np.allclose(T_est, T1, atol=1e-12)
rng = np.random.default_rng(5)
errs_p, errs_r = [], []
for _ in range(2000):                                # 每只脚的落脚点位置有 1 mm 的随机误差（设，标准差）
    noisy = {leg: feet_s[leg] + rng.normal(0, 1e-3, 3) for leg in LEGS}
    Te = body_from_feet(pb_from_joints, noisy)
    errs_p.append(np.linalg.norm(Te[:3, 3] - T1[:3, 3]))
    c = (np.trace(Te[:3, :3].T @ T1[:3, :3]) - 1) / 2
    errs_r.append(math.acos(min(1.0, c)))
reg_p = float(np.sqrt(np.mean(np.square(errs_p))))
reg_r = deg(float(np.sqrt(np.mean(np.square(errs_r)))))


def row(leg):
    a = tab[leg]
    return f"{a[0]:.2f}°, {a[1]:.2f}°, {a[2]:.2f}°".replace("-", "−")


out(h0=h0, N=N_bodies, Jr=J_rev, Js=J_sph, M_dof=M_dof, M_free=M_free,
    roll=8, pitch=-12, yaw=10, dpx=dp[0], dpy=dp[1], dpz=dp[2],
    T1=tex(T1, 4), row_FL=row("FL"), row_FR=row("FR"), row_RL=row("RL"), row_RR=row("RR"),
    th1=[[deg(v) for v in th1[3 * i:3 * i + 3]] for i in range(4)],
    pb_RR=tex(pb1["RR"], 4), pb_FL=tex(pb1["FL"], 4),
    pitch_up=deg(pitch_up), pitch_dn=deg(pitch_dn), roll_max=deg(roll_max), yaw_max=deg(yaw_max),
    why_up=", ".join(T(LEG_ZH[l], LEG_EN[l]) for l, _ in why_up),
    z_low=z_low, z_high=z_high, th_up_RL=deg(th_up[7]), th_up_RLc=deg(th_up[8]),
    th3_low=deg(th_low[2]), th3_high=deg(th_high[2]),
    w_b=tex(w_b, 2), v_b=tex(v_b, 2), Vb=tex(Vb, 2),
    thd_FL=tex(thd[0:3], 4), thd_FR=tex(thd[3:6], 4), thd_RL=tex(thd[6:9], 4), thd_RR=tex(thd[9:12], 4),
    thd_max=float(np.max(np.abs(thd))), fd_err=float(np.max(np.abs(thd - thd_fd))),
    rank4=int(np.linalg.matrix_rank(A4)), rank2=int(rank2), sv2_min=float(sv2[-1]),
    w_null=vec(w_n, 4), diag=vec(diag_dir, 4),
    slip=0.05, res_FL=res_leg[0], res_FR=res_leg[1], res_RL=res_leg[2], res_RR=res_leg[3],
    err_v=err_v, err_w=err_w, err_v_mm=err_v * 1000,
    reg_p_mm=reg_p * 1000, reg_r=reg_r)
