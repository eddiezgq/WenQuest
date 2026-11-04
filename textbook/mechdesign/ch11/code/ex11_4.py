"""11.5 组合应力下的疲劳：WQ-CR5 大臂内角在一个节拍里的应力——当量应力怎样取。

算例 11.5.1  先看一个最简单的情形：对称循环弯曲 σ = σa sin ωt（σa = 60 MPa，6061-T6）。冯·米塞斯应力 |σ| 永远为正，
            雨流计数把它当成频率加倍、R = 0 的脉动循环；与按 σ 本身算的结果比较（数字工厂 fatigue.compute，同一组参数）；
算例 11.5.2  WQ-CR5 带 5 kg 跑机器人厂的标准动作（初始位姿 → 两个位姿 → 回来，每段 1.2 s，段间停 0.3 s；“多体动力学”同一个求解器，
            梯形速度），大臂 J3 端面上的载荷（Fx、Fy、Fz、Mx、My、Mz）随时间变：J1 转动时有水平方向的惯性弯矩，与重力弯矩叠加，
            弯矩的方向在转——非比例加载。有限元（单位载荷工况叠加，_ch11.py）给出 J2 端（根部）、J3 端两处法兰内角圆角表面
            72 × 41 个点的应力张量历程。五种算法比较最危险点的疲劳安全系数 S = S_D / σa,eq（最大一个循环，古德曼）和损伤：
            (a) 数字工厂现在的做法：静止伸直时的冯·米塞斯 × |M(t)| / |M₀|（M 为 J3 处反力矩的大小，“多体动力学”的 rm.link3.abs）；
            (b) 冯·米塞斯历程（无符号）；(c) 带符号的冯·米塞斯；(d) 最大主应力；(e) 临界平面：垂直于表面的各个面（每 5°）上的正应力。
            (b)–(e) 先按应力变程粗筛候选点，再对候选点逐一用 fatigue.compute；
图 11.5.1。
"""
import math

import numpy as np

import _ch11 as H
from bookout import T, figure, out, style

# ---------------------------------------------------------------- 算例 11.5.1
SA = 60.0
tt = np.linspace(0, 2, 401)                              # 两个周期
sig = SA * np.sin(2 * math.pi * tt)
_, d_true = H.damage(sig)
_, d_vm = H.damage(np.abs(sig))
D_true, D_vm = d_true["damage_per_block"], d_vm["damage_per_block"]

# ---------------------------------------------------------------- 算例 11.5.2
R = H.heavy()
t, L6, L0 = R["t"], R["L6"], R["L0"]
Mabs = np.linalg.norm(L6[3:], axis=0)
M0 = float(np.linalg.norm(L0[3:]))
TCYC = float(t[-1])


def study(end):
    U = R["U"][end]
    F = H.field(U, L6, L0)
    npt = len(F["vm0"])
    # (a) 数字工厂：一个标量载荷谱 × 各点的静态应力
    Dfac, sfac = H.FT.compute(F["vm0"], M0, list(Mabs), TCYC, H.AL, "fine_turned", 0.85, 1.0, True)
    ia = int(np.argmax(Dfac))
    _, sa = H.damage(F["vm0"][ia] * Mabs / M0)
    res = {"a": (sa["S_fat"], ia, float(Dfac[ia]))}
    # (b)–(d)：每个点最大一个循环的等效应力幅一次算完，找最危险的点，再用 fatigue.compute 核对
    for key, arr in (("b", F["vm"]), ("c", F["svm"]), ("d", F["s1"])):
        i = int(np.argmax(H.proxy(arr)))
        D, s = H.damage(arr[i])
        res[key] = (s["S_fat"], i, D)
    # (e) 临界平面：垂直于表面、每 5° 一个面，全部点 × 36 个面的正应力
    ie, _, worst_dir, sn = H.critical_plane(U, F, end)
    D, s = H.damage(sn)
    res["e"] = (s["S_fat"], ie, D)
    loc = {k: (math.degrees(F["theta"][v_[1]]), F["phi"][v_[1]]) for k, v_ in res.items()}
    i_c = res["c"][1]
    flip = (float(F["svm"][i_c].min()), float(F["svm"][i_c].max()), float(F["s1"][i_c].min()), float(F["s1"][i_c].max()),
            float(np.min(H.eig_all(F["h"][i_c])[:, 0])))
    return res, loc, F, worst_dir, flip, npt, sfac


J2 = study("J2")
J3 = study("J3")
resA, locA, FA, dirA, flipA, NPT, sfacA = J2
resB, locB, FB, dirB, flipB, _, _ = J3

# 圆周上的应力幅（根部，圆角上（a）的最危险位置那一排）：数字工厂的做法 vs 实际的最大主应力
kA = int(FA["k"][resA["a"][1]])
ths = np.degrees(H.THETA)
nphi = int(FA["k"].max()) + 1
sel = [j * nphi + kA for j in range(len(H.THETA))]
amp_a = np.array([np.ptp(FA["vm0"][i] * Mabs / M0) / 2 for i in sel])
amp_s1 = np.array([np.ptp(FA["s1"][i]) / 2 for i in sel])
mean_s1 = np.array([(FA["s1"][i].max() + FA["s1"][i].min()) / 2 for i in sel])
amp_cp = []
for i in sel:
    n_, t1, t2 = H.surface_axes(R["U"]["J2"], kA, float(FA["theta"][i]), end="J2")
    amp_cp.append(max(np.ptp(H.normal_stress(FA["h"][i], math.cos(a) * t1 + math.sin(a) * t2)) / 2 for a in np.radians(np.arange(0, 180, 15))))
amp_cp = np.array(amp_cp)

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
a0.plot(t, L6[3], color="#d62728", lw=1.1, label="Mx")
a0.plot(t, L6[4], color="#2ca02c", lw=1.1, label="My")
a0.plot(t, L6[5], color="#1f77b4", lw=1.1, label="Mz")
a0.plot(t, Mabs, color=H.INK, lw=1.0, ls="--", label=T("|M|（数字工厂现在用的标量）", "|M| (the scalar the factory uses now)"))
a0.set_xlabel(T("时间 / s", "Time / s"), fontsize=7.0)
a0.set_ylabel(T("J3 端面上的力矩 / N·m（零件坐标）", "Moment on the J3 end face / N·m (part frame)"), fontsize=7.0)
a0.legend(fontsize=5.6, frameon=False, loc="lower center", ncol=2, bbox_to_anchor=(0.5, 0.0))
a0.set_ylim(-48, 55)
a0.tick_params(labelsize=6.2)
a0.set_title(T("(a) 一个节拍里大臂端部的力矩", "(a) Moments at the arm end over one cycle"), fontsize=7.0)
a1.plot(ths, amp_a, color=H.INK, lw=1.1, ls="--", label=T("(a) 静态冯·米塞斯 × |M|/|M₀|", "(a) static von Mises × |M|/|M₀|"))
a1.plot(ths, amp_s1, color="#d62728", lw=1.1, label=T("(d) 最大主应力", "(d) max principal stress"))
a1.plot(ths, amp_cp, color="#1f77b4", lw=1.1, label=T("(e) 临界平面上的正应力", "(e) normal stress on the critical plane"))
a1.set_xlabel(T("圆周位置 θ / (°)", "Position around the tube θ / (°)"), fontsize=7.0)
a1.set_ylabel(T("最大一个循环的应力幅 / MPa", "Amplitude of the largest cycle / MPa"), fontsize=7.0)
a1.set_xticks(range(0, 361, 90))
a1.legend(fontsize=5.8, frameon=False, loc="upper right")
a1.tick_params(labelsize=6.2)
a1.set_title(T("(b) J2 端内角，圆角上同一位置一圈", "(b) J2-end corner, one ring on the fillet"), fontsize=7.0)
fig.tight_layout()
figure(fig, "fig11_5_1")

# 根部载荷里没有算大臂自己（铝管 + 罩壳）的重力：它在根部的弯矩约 m g L/2，与静止伸直时根部的弯矩比较
m_self = sum(pp["mass"] for nm, pp, _ in H.W.link_parts(1) if "铝管" in nm or "罩壳" in nm)
M_self = m_self * H.W.G0 * float(np.linalg.norm(H.W._child_pos(1))) / 2
M_root0 = H.W.upper_arm_end_loads()["moment_root_nm"]
v = dict(SA=SA, m_self=m_self, M_self=M_self, self_pct=M_self / (M_root0 - M_self) * 100, Mz_max=float(np.abs(L6[5]).max()), sa_true=d_true["sa_eq"], sa_vm=d_vm["sa_eq"], n_true=d_true["n"], n_vm=d_vm["n"],
         D_true=D_true, D_vm=D_vm, D_ratio=D_true / D_vm, life_true=1 / D_true, life_vm=1 / D_vm,
         t_cycle=TCYC, M0=M0, Mmax=float(Mabs.max()), Mmin=float(Mabs.min()), npt=NPT, nphi=nphi,
         My_max=float(np.abs(L6[4]).max()), Mx_max=float(np.abs(L6[3]).max()), Mx_min=float(np.abs(L6[3]).min()),
         amp_a_max=float(amp_a.max()), amp_s1_max=float(amp_s1.max()), amp_cp_max=float(amp_cp.max()),
         th_a_max=float(ths[int(np.argmax(amp_a))]), th_s1_max=float(ths[int(np.argmax(amp_s1))]),
         SD=sfacA["S_D"], cps=sfacA["cycles_per_block"])
for tag, res, loc, flip in (("r", resA, locA, flipA), ("t", resB, locB, flipB)):
    for k, (S_, i, D) in res.items():
        v[f"S_{k}_{tag}"] = S_
        v[f"th_{k}_{tag}"] = loc[k][0]
        v[f"ph_{k}_{tag}"] = loc[k][1]
    v[f"svm_lo_{tag}"], v[f"svm_hi_{tag}"], v[f"s1_lo_{tag}"], v[f"s1_hi_{tag}"], v[f"s3_lo_{tag}"] = flip
v["ratio_ae_r"] = resA["a"][0] / resA["e"][0]
v["ratio_ce_r"] = resA["c"][0] / resA["e"][0]
v["dir_e_r"] = dirA
out(**v)
