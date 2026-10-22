"""24.4 节的计算：能量守恒检验。

(1) 定理 24.4.1 的数值核对（算例 24.4.1）：算例 24.2.2 的送料动作，电机做的功 ∫τᵀφ̇ dt 等于机械能的增量（起止都静止，即势能的增量）；
    两个关节各自做的正功、负功。
(2) 算例 24.4.2：UR5e 的关节 2、3（关节 1、4、5、6 焊死，取消转角限位，关掉执行器（模型里是位置伺服），空手）从水平伸直的姿态无驱动地落下。
    本章自己的程序（Planar2 + RK4，步长 1 ms）与 MuJoCo（同一模型、RK4、1 ms）比较前 2 s 的关节角；
    前 2 s 内机械能的最大偏差：显式欧拉法、半隐式（辛）欧拉法、RK4，步长 1、2、4 ms，及步长加倍时偏差放大的倍数；
    MuJoCo 的 Euler（就是半隐式欧拉法）、implicitfast（无阻尼时与之相同）、RK4 与本章程序逐步一致；
    60 s 的长时间仿真（步长 1 ms）：显式欧拉的能量持续增长，半隐式欧拉增长得慢得多，RK4 的偏差很小；半隐式欧拉延长到 600 s，
    每 60 s 一段的偏差（M 随姿态变化时它不是严格的辛方法，偏差仍会慢慢漂移）；UR5e 的自由下落对初值敏感（初值差 10⁻⁹ rad）。
(3) 算例 24.4.3：故意写错的动力学方程，能量检验能不能发现：漏掉科氏项的系数 2、离心项符号写反、关节 1 的重力项漏掉连杆 2、
    M₁₂ 漏掉耦合项 β。每种都用 RK4（1 ms）积分 2 s，看机械能的偏差。
(4) 算例 24.4.5（生活中的例子）：双摆（示意值：两根相同的均匀细杆，长 0.3 m、质量 0.2 kg）从 (120°, 60°) 释放；初始角相差 10⁻⁹ rad 的两次仿真
    何时相差 0.1 rad 以上；两次仿真的机械能都守恒。与 MuJoCo 的同一模型核对前 1 s。
(5) 算例 24.4.4（有阻尼）：关节黏性阻尼 b = 0.5 N·m·s/rad，dE/dt = −b|φ̇|²（式 (24.4.3)），积分形式核对；与 MuJoCo 的 damping 属性一致。
(6) 实验 24.4 的阈值：六关节 UR5e（取消限位、关闭接触和执行器）从 θ = (0, −30°, 0, −90°, 0, 0) 无驱动落下 10 s，
    MuJoCo 三种积分器、两种步长的能量偏差（实验用浏览器里同一版本的 MuJoCo）；双摆的 MuJoCo 模型。
(7) 习题答案。
"""
import math

import numpy as np

from _ch24 import (G0, Planar2, mj_load, mjcf_text, parse_links, payload_parts, payload_xml, planar_params, quintic, rk4_step,
                   ur_to_planar, ur_weld_xml)
from bookout import out

import mujoco                                                           # noqa: E402

links = parse_links(mjcf_text())
P0 = planar_params(links)
PL = planar_params(links, payload=payload_parts())

# ---------------------------------------------------------------- (1) 功与能：送料动作
QA, QB, T1 = (-120.0, 120.0), (-30.0, 30.0), 1.0
pa, pb = ur_to_planar(*np.radians(QA)), ur_to_planar(*np.radians(QB))
n = 4000
ts = np.linspace(0, T1, n + 1)
pw = np.zeros((n + 1, 2))
for i, tt in enumerate(ts):
    q, qd, qdd = quintic(pa, pb, T1, tt)
    pw[i] = PL.tau(q, qd, qdd) * qd                                     # 每个关节的功率 τ_i φ̇_i


def simpson(y, h):
    return h / 3 * (y[0] + y[-1] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum())


hstep = T1 / n
W = simpson(pw.sum(1), hstep)
dE = PL.U(pb) - PL.U(pa)
err_W = abs(W - dE)
assert err_W < 1e-9
W_pos = [simpson(np.maximum(pw[:, j], 0), hstep) for j in range(2)]
W_neg = [simpson(np.minimum(pw[:, j], 0), hstep) for j in range(2)]
W_joint = [simpson(pw[:, j], hstep) for j in range(2)]
dh = dE / ((PL.m1 + PL.m2) * G0)                                        # 整体质心升高（等效）

# ---------------------------------------------------------------- (2) 算例 24.4.1：自由下落
X0 = np.array([0.0, 0.0, 0.0, 0.0])                                     # 水平伸直、静止


def integrate(P, x0, h, T, method="rk4", c_fun=None, tau_fun=None):
    x = np.array(x0, float)
    N = int(round(T / h))
    X = np.zeros((N + 1, 4))
    X[0] = x
    for k in range(N):
        tau = (0.0, 0.0) if tau_fun is None else tau_fun(x)
        if method == "rk4":
            f = P.rhs(tau, c_fun) if tau_fun is None else (lambda s: np.r_[s[2:], P.fd(s[:2], s[2:], tau_fun(s), c_fun)])
            x = rk4_step(f, x, h)
        elif method == "euler":                                         # 显式欧拉
            a = P.fd(x[:2], x[2:], tau, c_fun)
            x = np.r_[x[:2] + h * x[2:], x[2:] + h * a]
        elif method == "symp":                                          # 半隐式（辛）欧拉：先更新速度，再用新速度更新位置
            a = P.fd(x[:2], x[2:], tau, c_fun)
            v = x[2:] + h * a
            x = np.r_[x[:2] + h * v, v]
        X[k + 1] = x
    return X


def energy_dev(P, X):
    E = np.array([P.E(x[:2], x[2:]) for x in X])
    return float(np.abs(E - E[0]).max()), E


def mj_free_planar(integrator, h, T, x0=X0, damping=0.0):
    opt = f'<option timestep="{h}" integrator="{integrator}"><flag contact="disable" actuation="disable"/></option>'
    xml = ur_weld_xml(option=opt, free=True)
    if damping:
        for name in ("shoulder_lift_joint", "elbow_joint"):
            xml = xml.replace(f'<joint name="{name}"', f'<joint name="{name}" damping="{damping}"', 1)
    mj_, m_, d_ = mj_load(xml)
    d_.qpos[:] = -x0[:2]
    d_.qvel[:] = -x0[2:]
    N = int(round(T / h))
    X = np.zeros((N + 1, 4))
    X[0] = x0
    E = np.zeros(N + 1)
    for k in range(N + 1):
        if k:
            mujoco.mj_step(m_, d_)
            X[k] = np.r_[-d_.qpos, -d_.qvel]
        mujoco.mj_forward(m_, d_)
        mujoco.mj_energyPos(m_, d_)
        mujoco.mj_energyVel(m_, d_)
        E[k] = d_.energy[0] + d_.energy[1]
    return X, E


# 本章程序与 MuJoCo：同一个模型、同一种方法、同一个步长
X_ours = integrate(P0, X0, 1e-3, 2.0)
X_mj, E_mj = mj_free_planar("RK4", 0.001, 2.0)
diff_traj = float(np.abs(X_ours[:, :2] - X_mj[:, :2]).max())
assert diff_traj < 1e-8
# 两者的能量定义一致（MuJoCo 的势能零点不同，比较变化量）
E_ours = np.array([P0.E(x[:2], x[2:]) for x in X_mj])
assert np.abs((E_ours - E_ours[0]) - (E_mj - E_mj[0])).max() < 1e-9
# 下落中的最大动能（作为能量偏差的参照尺度）
K_max = max(P0.K(x[:2], x[2:]) for x in X_ours)

# 精度：前 2 s 内机械能的最大偏差（这段时间里舍入误差还没有被混沌放大，各方法可以逐位比较）
T_ACC, T_LONG = 2.0, 60.0
dev = {}
for meth in ("euler", "symp", "rk4"):
    for h in (0.001, 0.002, 0.004):
        dev[(meth, h)] = energy_dev(P0, integrate(P0, X0, h, T_ACC, meth))[0]
# MuJoCo 的三种积分器：Euler 就是半隐式（辛）欧拉法；没有阻尼时 implicitfast 与它相同；RK4 与本章的 RK4 相同
err_mj_int = 0.0
for integ, meth in (("Euler", "symp"), ("implicitfast", "symp"), ("RK4", "rk4")):
    for h in (0.001, 0.002, 0.004):
        Xm, Em = mj_free_planar(integ, h, T_ACC)
        Xo = integrate(P0, X0, h, T_ACC, meth)
        err_mj_int = max(err_mj_int, float(np.abs(Xm[:, :2] - Xo[:, :2]).max()))
        assert abs(float(np.abs(Em - Em[0]).max()) - dev[(meth, h)]) < 1e-6 * max(dev[(meth, h)], 1.0)
assert err_mj_int < 1e-8
rk4_ratio = dev[("rk4", 0.002)] / dev[("rk4", 0.001)]
symp_ratio = dev[("symp", 0.002)] / dev[("symp", 0.001)]
euler_ratio = dev[("euler", 0.002)] / dev[("euler", 0.001)]
assert 12 < rk4_ratio < 20 and 1.7 < symp_ratio < 2.3 and 1.7 < euler_ratio < 2.3
# 长时间：60 s，步长 1 ms
long = {meth: energy_dev(P0, integrate(P0, X0, 0.001, T_LONG, meth))[1] for meth in ("euler", "symp", "rk4")}
long_dev = {k: float(np.abs(v - v[0]).max()) for k, v in long.items()}
assert long_dev["euler"] > 5 * long_dev["symp"] and long_dev["rk4"] < 1e-6
# 显式欧拉的能量大体随时间线性增长：前 10 s 与最后 10 s 的平均偏差
# 半隐式欧拉法用于 M 随姿态变化的系统时并不是严格的辛方法：延长到 600 s，看每 60 s 一段的最大能量偏差
X_sy600 = integrate(P0, X0, 0.001, 600.0, "symp")
E_sy600 = np.array([P0.E(x[:2], x[2:]) for x in X_sy600[::10]])
seg_sy = [float(np.abs(E_sy600[k * 6000:(k + 1) * 6000 + 1] - E_sy600[0]).max()) for k in range(10)]
assert seg_sy[-1] > 3 * seg_sy[0]                                       # 不再有界：慢慢漂移
# UR5e 的自由下落也对初值敏感：φ₁ 的初值差 10⁻⁹ rad，两次 RK4 仿真的角度差
X_a = integrate(P0, X0, 1e-3, 25.0)
X_b = integrate(P0, X0 + np.array([1e-9, 0, 0, 0]), 1e-3, 25.0)
gap_ur = np.abs(X_a[:, :2] - X_b[:, :2]).max(1)
gap10, gap20, gap25 = float(gap_ur[10000]), float(gap_ur[20000]), float(gap_ur[25000])
assert gap10 < 1e-6 and gap25 > 0.1
eu_10 = float(np.mean(long["euler"][:10001] - long["euler"][0]))
eu_last = float(np.mean(long["euler"][-10001:] - long["euler"][0]))
sy_last = float(np.abs(long["symp"][-10001:] - long["symp"][0]).max())

# ---------------------------------------------------------------- (3) 算例 24.4.3：故意写错
class NoBeta(Planar2):
    def M(self, p):
        A = super().M(p)
        b = self.beta(p[1])
        return A - np.array([[0.0, b], [b, 0.0]])                        # M₁₂ 漏掉 β


def c_half(P, p, pd):                                                    # 科氏项漏了系数 2
    h = P.hh(p[1])
    return np.array([-h * (pd[0] * pd[1] + pd[1] ** 2), h * pd[0] ** 2])


def c_sign(P, p, pd):                                                    # 离心项符号写反
    h = P.hh(p[1])
    return np.array([-h * (2 * pd[0] * pd[1] + pd[1] ** 2), -h * pd[0] ** 2])


class NoG2(Planar2):
    def g(self, p):
        A = super().g(p)
        return A - np.array([self.m2 * self.g0 * (self.a1 * math.cos(p[0]) + self.r2 * math.cos(p[0] + p[1])
                                                  - self.s2 * math.sin(p[0] + p[1])), 0.0])


T_BUG = 2.0
bug = {"ok": energy_dev(P0, integrate(P0, X0, 1e-3, T_BUG))[0],
       "half": energy_dev(P0, integrate(P0, X0, 1e-3, T_BUG, c_fun=c_half))[0],
       "sign": energy_dev(P0, integrate(P0, X0, 1e-3, T_BUG, c_fun=c_sign))[0]}
kw = {k: getattr(P0, k) for k in ("a1", "m1", "r1", "s1", "J1", "m2", "r2", "s2", "J2")}
Pb = NoBeta(**kw, arm=P0.arm)
bug["beta"] = energy_dev(Pb, integrate(Pb, X0, 1e-3, T_BUG))[0]
Pg = NoG2(**kw, arm=P0.arm)
bug["g2"] = energy_dev(Pg, integrate(Pg, X0, 1e-3, T_BUG))[0]
assert all(bug[k] > 1e5 * bug["ok"] for k in ("half", "sign", "beta", "g2"))

# ---------------------------------------------------------------- (4) 算例 24.4.5（生活中的例子）：双摆的混沌
Ld, md = 0.3, 0.2
DP = Planar2(Ld, md, Ld / 2, 0.0, md * Ld ** 2 / 3, md, Ld / 2, 0.0, md * Ld ** 2 / 3)
x_dp = np.array([math.radians(120), math.radians(60), 0.0, 0.0])
T_DP, h_dp = 20.0, 1e-3
A_ = integrate(DP, x_dp, h_dp, T_DP)
B_ = integrate(DP, x_dp + np.array([1e-9, 0, 0, 0]), h_dp, T_DP)
gap = np.abs(A_[:, :2] - B_[:, :2]).max(1)
t_div = float(np.argmax(gap > 0.1) * h_dp)
assert 0 < t_div < T_DP
dev_dp = max(energy_dev(DP, A_)[0], energy_dev(DP, B_)[0])
E_dp0 = DP.E(x_dp[:2], x_dp[2:]) - DP.E(np.array([-math.pi / 2, 0.0]), np.zeros(2))   # 相对两杆都竖直下垂
# MuJoCo 的同一个双摆（细杆用质量集中在轴线上的胶囊近似：给出与细杆相同的惯量）
xml_dp = f"""<mujoco><option timestep="{h_dp}" integrator="RK4" gravity="0 0 {-G0}"><flag contact="disable"/></option>
<worldbody><body name="r1"><joint name="j1" type="hinge" axis="0 -1 0"/>
<inertial pos="{Ld / 2} 0 0" mass="{md}" diaginertia="1e-9 {md * Ld ** 2 / 12} {md * Ld ** 2 / 12}"/>
<body name="r2" pos="{Ld} 0 0"><joint name="j2" type="hinge" axis="0 -1 0"/>
<inertial pos="{Ld / 2} 0 0" mass="{md}" diaginertia="1e-9 {md * Ld ** 2 / 12} {md * Ld ** 2 / 12}"/></body></body></worldbody></mujoco>"""
mjd, mdp, ddp = mj_load(xml_dp)
ddp.qpos[:] = x_dp[:2]
diff_dp = 0.0
for k in range(int(1.0 / h_dp)):
    mujoco.mj_step(mdp, ddp)
    diff_dp = max(diff_dp, float(np.abs(ddp.qpos - A_[k + 1, :2]).max()))
assert diff_dp < 1e-8

# ---------------------------------------------------------------- (5) 有阻尼
B_DAMP = 0.5
Xd_ = integrate(P0, X0, 1e-3, 5.0, tau_fun=lambda s: -B_DAMP * s[2:])
E_d = np.array([P0.E(x[:2], x[2:]) for x in Xd_])
diss = simpson(np.array([B_DAMP * x[2:] @ x[2:] for x in Xd_]), 1e-3)
err_diss = abs((E_d[-1] - E_d[0]) + diss)
assert err_diss < 1e-6
assert np.all(np.diff(E_d) <= 1e-12)                                    # 有阻尼时能量单调不增
Xmd, Emd = mj_free_planar("RK4", 0.001, 5.0, damping=B_DAMP)
diff_damp = float(np.abs(Xmd[:, :2] - Xd_[:, :2]).max())
assert diff_damp < 1e-7
E_loss5 = E_d[0] - E_d[-1]

# ---------------------------------------------------------------- (6) 实验 24.4 的阈值：六关节 UR5e 自由下落
TH0 = np.radians([0, -30, 0, -90, 0, 0])


def ur6_free(integrator, h, T=10.0):
    xml = mjcf_text(option=f'<option timestep="{h}" integrator="{integrator}"><flag contact="disable" actuation="disable"/></option>')
    xml = xml.replace('<joint ', '<joint limited="false" ')               # 取消转角限位（与实验程序相同的改法）
    mj_, m_, d_ = mj_load(xml)
    assert not m_.jnt_limited.any()
    d_.qpos[:] = TH0
    N = int(round(T / h))
    E = np.zeros(N + 1)
    for k in range(N + 1):
        if k:
            mujoco.mj_step(m_, d_)
        mujoco.mj_forward(m_, d_)
        mujoco.mj_energyPos(m_, d_)
        mujoco.mj_energyVel(m_, d_)
        E[k] = d_.energy[0] + d_.energy[1]
    return float(np.abs(E - E[0]).max())


lab = {(i, h): ur6_free(i, h) for i in ("RK4", "Euler", "implicitfast") for h in (0.001, 0.004)}

# ---------------------------------------------------------------- (7) 习题答案
# 24.4.3：送料动作放慢到 2 s，电机做的总功（不变：只与起止位置有关）
W2 = PL.U(pb) - PL.U(pa)

out(W=W, dE=dE, err_W=err_W, W_pos1=W_pos[0], W_neg1=W_neg[0], W_pos2=W_pos[1], W_neg2=W_neg[1], W_j1=W_joint[0], W_j2=W_joint[1],
    dh=dh, dh_abs=abs(dh), Ld=Ld, md=md,
    diff_traj=diff_traj, K_max=K_max,
    eu1=dev[("euler", 0.001)], eu2=dev[("euler", 0.002)], eu4=dev[("euler", 0.004)],
    sy1=dev[("symp", 0.001)], sy2=dev[("symp", 0.002)], sy4=dev[("symp", 0.004)],
    rk1=dev[("rk4", 0.001)], rk2=dev[("rk4", 0.002)], rk4_=dev[("rk4", 0.004)], err_mj_int=err_mj_int,
    rk4_ratio=rk4_ratio, symp_ratio=symp_ratio, euler_ratio=euler_ratio,
    seg_sy1=seg_sy[0], seg_sy10=seg_sy[-1], gap10=gap10, gap20=gap20, gap25=gap25,
    L_eu=long_dev["euler"], L_sy=long_dev["symp"], L_rk=long_dev["rk4"], eu_10=eu_10, eu_last=eu_last, sy_last=sy_last,
    bug_ok=bug["ok"], bug_half=bug["half"], bug_sign=bug["sign"], bug_beta=bug["beta"], bug_g2=bug["g2"],
    t_div=t_div, dev_dp=dev_dp, E_dp0=E_dp0, diff_dp=diff_dp,
    B_DAMP=B_DAMP, err_diss=err_diss, diff_damp=diff_damp, E_loss5=E_loss5,
    labR1=lab[("RK4", 0.001)], labR4=lab[("RK4", 0.004)], labE1=lab[("Euler", 0.001)], labE4=lab[("Euler", 0.004)],
    labI1=lab[("implicitfast", 0.001)], labI4=lab[("implicitfast", 0.004)],
    W2=W2)
