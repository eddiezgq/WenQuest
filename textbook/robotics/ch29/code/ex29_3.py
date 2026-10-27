"""29.3 节的计算：时间步长与稳定性。

(1) 单自由度弹簧-阻尼器 ẍ = −ω²x − cẋ（c = 2ζω）的稳定步长：半隐式欧拉（阻尼显式）(hω)² + 2hc ≤ 4，阻尼隐式 (hω)² ≤ 4 + 2hc，
    显式欧拉 h ≤ 2ζ/ω（ζ ≤ 1），RK4（无阻尼时 hω ≤ 2√2）；公式与放大矩阵谱半径的数值结果核对。
(2) 算例 29.3.1：书中 UR5e 的执行器是 PD（kp = 2000、500 N·m/rad，kd = 400、100 N·m·s/rad）。在工作姿态线性化，
    各关节的 ω、c、ζ，按单关节公式估计的临界步长；6 个关节耦合后的临界步长（Euler、RK4；implicitfast 不受限）。
    MuJoCo 中 h = 1、1.5、2、2.5、3、5 ms 各仿真 2 s，最后 1 s 的关节速度幅值；把阻尼改写成关节的 damping（Euler 隐式处理）后的结果。
(3) 算例 29.3.2：能量漂移。不加驱动的单摆（两连杆臂的连杆 1）从水平放开，两连杆臂从“连杆 1 水平、连杆 2 下垂 0.5 rad”放开，仿真 20 s：Euler、implicit、RK4，
    h = 4、2、1、0.5 ms 的能量误差；单摆的误差有界，两连杆臂的 Euler 能量随时间线性增长（速度形式的半隐式欧拉在 M 随位形变化时不是辛方法）。
(4) 算例 29.3.3：混沌。两连杆臂从两杆水平放开，用 RK4，h = 1 ms 与 0.5 ms 两次仿真的关节角何时相差 0.1 rad；初值差 1e−9 rad 时又如何；
    连杆 2 下垂 0.5 rad 放开时运动规则，两种步长 20 s 后仍一致。
(5) 算例 29.3.4：接触的时间常数。MuJoCo 保证 solref 的时间常数 τ ≥ 2h（refsafe）：读出 efc_KBIP 换算的 τ；关掉 refsafe 后
    τ < 2h 的球落地反弹得比放开时还高；参考弹簧-阻尼器显式处理时的稳定条件 τ ≥ h/(0.828 d_max)，用二分法找出临界 τ。
"""
import math

import mujoco
import numpy as np

from _ch29 import ARM2, Q_WORK, amp_matrix, arm2_xml, h_limit, mjcf_text, ur_h_limit, ur_linear
from bookout import out

# ---------------------------------------------------------------- (1) 单自由度的稳定步长
def h_formula(w, c, method):
    z = c / (2 * w)
    if method == "euler":
        return 2 / w * (math.sqrt(1 + z * z) - z)
    if method == "implicit":
        return 2 / w * (math.sqrt(1 + z * z) + z)
    if method == "explicit":                            # det ≤ 1 给出 h ≤ 2ζ/ω；ζ > 1 时还要 1 + tr + det ≥ 0
        return 2 * z / w if z <= 1 else 2 / w * (z - math.sqrt(z * z - 1))
    raise ValueError


err = 0.0
for w in (10.0, 70.0, 300.0):
    for z in (0.05, 0.5, 1.0, 3.0, 7.0):
        c = 2 * z * w
        for meth in ("euler", "implicit", "explicit"):
            hn = h_limit(w, c, meth, hmax=50.0 / w)
            hf = h_formula(w, c, meth)
            err = max(err, abs(hn - hf) / hf)
assert err < 1e-7
rk4_0 = h_limit(1.0, 0.0, "rk4", hmax=5.0)
assert abs(rk4_0 - 2 * math.sqrt(2)) < 1e-9
rk4_real = h_limit(1e-6, 1.0, "rk4", hmax=5.0)                # 纯阻尼（实特征值 −c）时 RK4 的极限 hc
out(stab_err=err, rk4_imag=rk4_0, rk4_real=rk4_real)
out(z_lim_euler1=h_formula(1, 2, "euler"), z_lim_impl1=h_formula(1, 2, "implicit"))   # ζ = 1 时的 hω

# ---------------------------------------------------------------- (2) UR5e
M, K, D = ur_linear(Q_WORK)
kp, kd, Mii = np.diag(K), np.diag(D), np.diag(M)
w_j = np.sqrt(kp / Mii)
c_j = kd / Mii
z_j = c_j / (2 * w_j)
h_j = np.array([h_formula(w, c, "euler") for w, c in zip(w_j, c_j)])
h_eu = ur_h_limit(M, K, D, "euler")
h_rk = ur_h_limit(M, K, D, "rk4")
h_im = ur_h_limit(M, K, D, "implicit", hmax=0.2)
assert h_im == math.inf
eigD = np.sort(np.linalg.eigvals(np.linalg.solve(M, D)).real)
out(Mii=Mii.tolist(), w_j=w_j.tolist(), c_j=c_j.tolist(), z_j=z_j.tolist(), h_j_ms=(h_j * 1000).tolist(),
    w6=w_j[5], c6=c_j[5], z6=z_j[5], h6_ms=h_j[5] * 1000, h_eu_ms=h_eu * 1000, h_rk_ms=h_rk * 1000, eigD_max=eigD[-1],
    I6=Mii[5], h_eu_est_ms=2 / eigD[-1] * 1000, h_rk_est_ms=rk4_real / eigD[-1] * 1000)


def ur_run(h, integ, T=2.0, damping_in_joint=False):
    t = mjcf_text(option=f'<option timestep="{h!r}" integrator="{integ}"><flag contact="disable"/></option>')
    m = mujoco.MjModel.from_xml_string(t)
    if damping_in_joint:                                 # 阻尼从执行器挪到关节：biasprm 的速度项置零，dof_damping = kd
        m.dof_damping[:] = -m.actuator_biasprm[:, 2]
        m.actuator_biasprm[:, 2] = 0.0
    d = mujoco.MjData(m)
    d.qpos[:] = Q_WORK
    d.ctrl[:] = Q_WORK + 0.05
    vmax = 0.0
    n = int(round(T / h))
    for k in range(n):
        mujoco.mj_step(m, d)
        if k >= n // 2:
            vmax = max(vmax, float(np.abs(d.qvel).max()))
    return vmax


HS = (0.001, 0.0015, 0.002, 0.0025, 0.003, 0.005)
runs = {(integ, h): ur_run(h, integ) for integ in ("Euler", "implicitfast", "RK4") for h in HS}
runs_j = {h: ur_run(h, "Euler", damping_in_joint=True) for h in (0.002, 0.005, 0.01)}
for h in HS:                                            # 稳定时最后 1 s 只剩慢模态的残余速度（约 0.002 rad/s），不稳定时在力矩上限之间来回振荡
    assert runs[("implicitfast", h)] < 0.01
assert runs[("Euler", 0.0015)] < 0.01 and runs[("Euler", 0.002)] > 0.1
assert runs[("RK4", 0.0025)] < 0.01 and runs[("RK4", 0.003)] > 0.1
assert all(v < 0.01 for v in runs_j.values())
out(ur_hs_ms=[h * 1000 for h in HS], ur_v_euler=[runs[("Euler", h)] for h in HS], ur_v_impl=[runs[("implicitfast", h)] for h in HS],
    ur_v_rk4=[runs[("RK4", h)] for h in HS], v_eu2=runs[("Euler", 0.002)], v_eu25=runs[("Euler", 0.0025)],
    v_eu3=runs[("Euler", 0.003)], v_rk3=runs[("RK4", 0.003)], v_j10=runs_j[0.01])

# ---------------------------------------------------------------- (3) 能量漂移
FREE = 'energy="enable" limit="disable"'               # 关掉关节限位：摆过 ±170° 也不碰
Q0_2 = (0.0, 0.5)                                      # 能量：连杆 1 水平、连杆 2 下垂 0.5 rad，静止放开（运动规则）
Q0_C = (0.0, 0.0)                                      # 混沌：两根连杆都水平，静止放开


def energy_run(xml, q0, T=20.0):
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    d.qpos[:] = q0
    mujoco.mj_forward(m, d)
    E0 = float(d.energy.sum())
    Es, ts = [], []
    while d.time < T - 1e-12:
        mujoco.mj_step(m, d)
        Es.append(float(d.energy.sum()) - E0)
        ts.append(d.time)
    return np.array(ts), np.array(Es), E0


energy = {}
for integ in ("Euler", "implicit", "RK4"):
    for h in (0.004, 0.002, 0.001, 0.0005):
        t1, e1, E01 = energy_run(arm2_xml(timestep=h, integrator=integ, flags=FREE, one=True), (0.0,))
        t2, e2, E02 = energy_run(arm2_xml(timestep=h, integrator=integ, flags=FREE), Q0_2)
        slope = np.polyfit(t2, e2, 1)[0]
        energy[(integ, h)] = (float(np.abs(e1).max()), float(np.abs(e2).max()), float(e2[-1]), float(slope))
# 单摆：Euler 误差有界、约与 h 成正比；两连杆臂：Euler 线性漂移，斜率约与 h 成正比；RK4 误差约与 h³～h⁴ 成正比
assert energy[("Euler", 0.004)][0] / energy[("Euler", 0.001)][0] > 3.5
assert energy[("Euler", 0.001)][3] > 0 and 1.7 < energy[("Euler", 0.002)][3] / energy[("Euler", 0.001)][3] < 2.3
assert energy[("implicit", 0.001)][3] < 0
assert energy[("RK4", 0.002)][1] / energy[("RK4", 0.001)][1] > 6
out(E0_one=E01, E0_two=E02,
    e1_eu4=energy[("Euler", 0.004)][0], e1_eu1=energy[("Euler", 0.001)][0], e2_eu1=energy[("Euler", 0.001)][1],
    e2_eu1_end=energy[("Euler", 0.001)][2], s_eu1=energy[("Euler", 0.001)][3], s_eu2=energy[("Euler", 0.002)][3],
    s_eu05=energy[("Euler", 0.0005)][3], s_im1=energy[("implicit", 0.001)][3], e2_im1_end=energy[("implicit", 0.001)][2],
    e2_rk1=energy[("RK4", 0.001)][1], e2_rk2=energy[("RK4", 0.002)][1], e2_rk4=energy[("RK4", 0.004)][1],
    e2_rk05=energy[("RK4", 0.0005)][1], e1_rk1=energy[("RK4", 0.001)][0],
    rk_ratio=energy[("RK4", 0.002)][1] / energy[("RK4", 0.001)][1], e2_eu1_pct=energy[("Euler", 0.001)][2] / E02 * 100)


# ---------------------------------------------------------------- (4) 混沌
def traj(h, q0, T=20.0, every=0.01):
    m = mujoco.MjModel.from_xml_string(arm2_xml(timestep=h, integrator="RK4", flags=FREE))
    d = mujoco.MjData(m)
    d.qpos[:] = q0
    out_t, out_q = [], []
    k = int(round(every / h))
    n = 0
    while d.time < T - 1e-12:
        mujoco.mj_step(m, d)
        n += 1
        if n % k == 0:
            out_t.append(d.time)
            out_q.append(d.qpos.copy())
    return np.array(out_t), np.array(out_q)


tA, qA = traj(0.001, Q0_C)
tB, qB = traj(0.0005, Q0_C)
tC, qC = traj(0.001, (0.0, 1e-9))
tD, qD = traj(0.0005, (0.0, 0.5))                      # 连杆 2 下垂 0.5 rad 放开：运动是规则的，不发散（习题 29.3.4）
tE, qE = traj(0.001, (0.0, 0.5))
dAB = np.abs(qA - qB).max(axis=1)
dAC = np.abs(qA - qC).max(axis=1)
t_ab = float(tA[np.argmax(dAB > 0.1)])
t_ac = float(tA[np.argmax(dAC > 0.1)])
assert dAB.max() > 0.1 and dAC.max() > 0.1
# 李雅普诺夫指数的粗估：初值差 1e−9 增长到 0.1 用的时间
lyap = math.log(0.1 / 1e-9) / t_ac
dDE = float(np.abs(qD - qE).max())
assert dDE < 1e-6
out(dDE=dDE, t_ab=t_ab, t_ac=t_ac, lyap=lyap, d_ab_1s=float(dAB[np.argmin(np.abs(tA - 1.0))]))


# ---------------------------------------------------------------- (5) 接触的时间常数
def ball(tau, h, refsafe=True, zeta=1.0, z0=0.3, T=3.0):
    fl = "" if refsafe else '<flag refsafe="disable"/>'
    x = (f'<mujoco><option timestep="{h!r}">{fl}</option><default><geom solref="{tau!r} {zeta!r}"/></default>'
         f'<worldbody><geom type="plane" size="1 1 0.1"/><body pos="0 0 {z0!r}"><freejoint/>'
         f'<geom type="sphere" size="0.05" mass="1"/></body></worldbody></mujoco>')
    m = mujoco.MjModel.from_xml_string(x)
    d = mujoco.MjData(m)
    zmax_after = 0.0
    touched = False
    tau_eff = None
    while d.time < T - 1e-12:
        mujoco.mj_step(m, d)
        if d.nefc and tau_eff is None:
            K, B, I, P = d.efc_KBIP[0]
            tau_eff = 2 / (0.95 * B)                     # b = 2/(d_max τ)，d_max = 0.95（solimp 默认）
        if d.nefc:
            touched = True
        if touched:
            zmax_after = max(zmax_after, float(d.qpos[2]))
        if not np.isfinite(d.qpos).all() or d.qpos[2] > 10:
            return tau_eff, math.inf
    return tau_eff, zmax_after


H_C = 0.002
taus = (0.0005, 0.001, 0.002, 0.003, 0.004, 0.01)
rs_on = {t: ball(t, H_C) for t in taus}
rs_off = {t: ball(t, H_C, refsafe=False) for t in taus}
for t in taus:
    assert abs(rs_on[t][0] - max(t, 2 * H_C)) < 1e-9
assert rs_off[0.001][1] > 1.0 and rs_off[0.004][1] < 0.3
# 临界 τ（关掉 refsafe）：二分
lo, hi = 0.001, 0.004
for _ in range(20):
    mid = (lo + hi) / 2
    if ball(mid, H_C, refsafe=False)[1] > 0.3:
        lo = mid
    else:
        hi = mid
tau_crit = hi
x_crit = math.sqrt(8) - 2                              # x² + 4x − 4 = 0 的正根：h/(d_max τ) ≤ 2√2 − 2
out(tau_eff_list=[rs_on[t][0] for t in taus], taus_ms=[t * 1000 for t in taus], zoff=[rs_off[t][1] if rs_off[t][1] < math.inf else -1 for t in taus],   # −1：飞走了
   
    zoff2=rs_off[0.002][1], zoff3=rs_off[0.003][1], tau_crit_ms=tau_crit * 1000, x_crit=x_crit,
    tau_pred_ms=H_C / (x_crit * 0.95) * 1000)
