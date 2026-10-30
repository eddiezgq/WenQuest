"""29.4 节的计算：仿真与现实的差距。主角是问渠机器人厂的 WQ-CR5；“现实”取机器人厂的数据。

(1) 算例 29.4.1：延迟。WQ-CR5 的出厂位置环（kp = 2000、1000、300 N·m/rad，kv = 400、200、40 N·m·s/rad）。单关节
    I θ̈ = −kp θ(t − T) − kv θ̇(t − T) 的穿越频率、相位裕度和临界延迟 T* = φ_m/ω_c（式 (29.4.2)），肩关节（关节 2）与腕关节（关节 6）。
    MuJoCo 中（控制每 0.1 ms 更新一次，近似连续；摩擦关掉）给 6 个关节都加上同样的测量延迟，用二分法找出开始振荡的延迟。
(2) 算例 29.4.2：域随机化。负载跑合台的标准动作（wqcr5.runin_ref，带约 5 kg 的标准负载）在“现场”的 WQ-CR5 上执行。现场与模型的差别
    取机器人厂的数据：各关节的库仑摩擦按关节测试台“空载摩擦力矩”的名义值和 σ 随机取（截在 0～上限之间），黏性摩擦按名义值的 0.5～1.5 倍，
    背隙按关节测试台的名义值和 σ 随机取；负载的质量、惯量在名义值的 ±30% 内（用户的工具不一样）；测量延迟 0～3 ms；控制周期 2 ms（500 Hz）。
    比较三种控制器：A 出厂位置环（不加前馈）；B 名义模型（零件库模型）的逆动力学与摩擦前馈 + 按 ω_n = 25 rad/s、ζ = 1 设计的 PD；
    C 同 B，ω_n = 80 rad/s。统计 TCP 的最大误差与停住后仍在振荡的次数；名义条件（无随机化、无延迟）下的结果作对照。
(3) 习题：库仑摩擦造成的静差 f_c/kp；增益与临界延迟成反比。
"""
import math

import mujoco
import numpy as np

from _ch29 import (CR_NAMES, Q_CR, cr_chain, cr_friction, cr_linear, cr_load, cr_load_xml, cr_model, cr_test_sigma, cr_track,
                   pd_delay_margin, pd_discrete_rho, pd_gains, wqcr5)
from bookout import out

W = wqcr5()
KP_A, KV_A = np.array(W.SERVO_KP), np.array(W.SERVO_KV)
FC0, FV0 = cr_friction()
Z6 = np.zeros(6)

# ---------------------------------------------------------------- (1) 延迟
M, K, D = cr_linear(Q_CR, payload=True)            # 带标准负载（下面的仿真也带）
Md = np.diag(M)
mar = [pd_delay_margin(Md[j], KP_A[j], KV_A[j]) for j in range(6)]
jmin = int(np.argmin([x[2] for x in mar]))
out(wc2=mar[1][0], pm2=math.degrees(mar[1][1]), T2_ms=mar[1][2] * 1000, wc6=mar[5][0], pm6=math.degrees(mar[5][1]),
    T6_ms=mar[5][2] * 1000, Tstar_ms=[x[2] * 1000 for x in mar], I2=Md[1], I6=Md[5], jmin=jmin + 1, Tmin_ms=mar[jmin][2] * 1000)


def small_move(t, a=Q_CR, b=Q_CR + 0.02, T=0.3):
    """在工作姿态附近 0.3 s 内移动 0.02 rad（五次多项式），再停住"""
    s = min(max(t / T, 0.0), 1.0)
    d = b - a
    return (a + d * (10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5), d * (30 * s ** 2 - 60 * s ** 3 + 30 * s ** 4) / T,
            d * (60 * s - 180 * s ** 2 + 120 * s ** 3) / T ** 2)


def oscillates(delay):
    r = cr_track(KP_A, KV_A, fc=Z6, fv=Z6, delay=delay, Tc=0.0001, h=0.0001, ref=small_move, T=1.8)
    return r["v_tail"] > 0.01


assert not oscillates(0.0) and oscillates(0.006)
lo, hi = 0.0, 0.006
for _ in range(8):
    mid = (lo + hi) / 2
    if oscillates(mid):
        hi = mid
    else:
        lo = mid
T_sim = (lo + hi) / 2
assert abs(T_sim - mar[jmin][2]) < 0.2e-3, (T_sim, mar[jmin][2])
out(T_sim_ms=T_sim * 1000, T_sim_res_us=(hi - lo) * 1e6)

# ---------------------------------------------------------------- (2) 域随机化：现场的数据来自机器人厂
P = cr_load()
_, m, d = cr_model(tool=cr_load_xml())
d.qpos[:] = Q_CR
mujoco.mj_forward(m, d)
MP = np.zeros((6, 6))
mujoco.mj_fullM(m, d, MP)
MdP = np.diag(MP)                                         # 带负载的质量矩阵对角元（设计 PD 用）
nom = cr_chain(payload=P)                                 # 名义模型：零件库的 WQ-CR5 + 名义负载
WN_B, WN_C = 25.0, 80.0
kpB, kdB = pd_gains(MdP, WN_B)
kpC, kdC = pd_gains(MdP, WN_C)
TB = min(pd_delay_margin(MdP[j], kpB[j], kdB[j])[2] for j in range(6))
TC = min(pd_delay_margin(MdP[j], kpC[j], kdC[j])[2] for j in range(6))
out(kpB=kpB.tolist(), kdB=kdB.tolist(), kpC=kpC.tolist(), kdC=kdC.tolist(), TB_ms=TB * 1000, TC_ms=TC * 1000,
    kpB2=kpB[1], kpB6=kpB[5], kpC2=kpC[1], kpC6=kpC[5], wnB=WN_B, wnC=WN_C, T_runin=W.runin_duration(),
    poses_deg=[list(p) for p in W.RUNIN_POSES_DEG], seg_s=W.RUNIN_SEG_S, dwell_s=W.RUNIN_DWELL_S)

CTRL = {
    "A": dict(kp=KP_A, kd=KV_A),
    "B": dict(kp=kpB, kd=kdB, ff_model=nom, fric_ff=(FC0, FV0)),
    "C": dict(kp=kpC, kd=kdC, ff_model=nom, fric_ff=(FC0, FV0)),
}
SIG = cr_test_sigma()
ARCMIN = math.pi / (180 * 60)
rng = np.random.default_rng(2029)
NCASE = 24
cases = []
for _ in range(NCASE):
    fc = np.array([min(max(rng.normal(s["fric"], s["fric_sigma"]), 0.0), s["fric_hi"]) for s in SIG])
    bl = np.array([min(max(rng.normal(s["backlash"], s["backlash_sigma"]), 0.0), s["backlash_hi"]) for s in SIG]) * ARCMIN
    cases.append(dict(scale=float(rng.uniform(0.7, 1.3)), fc=fc, fv=FV0 * rng.uniform(0.5, 1.5, 6), backlash=bl,
                      delay=float(rng.uniform(0, 0.003))))
fc_all = np.array([c["fc"] for c in cases])
out(sig_fric=[s["fric_sigma"] for s in SIG], nom_fric=[s["fric"] for s in SIG], nom_backlash=[s["backlash"] for s in SIG],
    sig_backlash=[s["backlash_sigma"] for s in SIG], fc_min=fc_all.min(axis=0).tolist(), fc_max=fc_all.max(axis=0).tolist())

nominal = {k: cr_track(**v, delay=0.0) for k, v in CTRL.items()}
res = {k: [cr_track(**v, **c) for c in cases] for k, v in CTRL.items()}
OSC = 0.05                                                 # 停住后 0.3 s 内关节角速度超过 0.05 rad/s 算作振荡
summary = {}
for k in CTRL:
    e = np.array([r["e_tcp"] for r in res[k]]) * 1000
    osc = np.array([r["v_tail"] > OSC for r in res[k]])
    dl = np.array([c["delay"] for c in cases]) * 1000
    summary[k] = dict(e_max=float(np.max(e[np.isfinite(e)])) if np.isfinite(e).any() else -1, e_med=float(np.median(e)),
                      n_osc=int(osc.sum()), dl_osc_min=float(dl[osc].min()) if osc.any() else None, e_nom=nominal[k]["e_tcp"] * 1000,
                      osc_nom=bool(nominal[k]["v_tail"] > OSC))
for k in CTRL:
    assert not summary[k]["osc_nom"], (k, nominal[k]["v_tail"])
assert summary["B"]["n_osc"] == 0 and summary["A"]["n_osc"] > 0 and summary["C"]["n_osc"] > 0
assert summary["B"]["e_max"] < summary["A"]["e_nom"] / 3
out(ncase=NCASE, **{f"{k}_{a}": v for k, s in summary.items() for a, v in s.items()})
# 同样的情形去掉背隙：控制器 B 的 TCP 误差变了多少（关节测试台的背隙不到 1′，折到 TCP 只有零点几毫米）
nobl = [cr_track(**CTRL["B"], **dict(c, backlash=None)) for c in cases]
e_nobl = np.array([r["e_tcp"] for r in nobl]) * 1000
eB = np.array([r["e_tcp"] for r in res["B"]]) * 1000
out(B_e_max_nobl=float(e_nobl.max()), B_bl_effect_max=float(np.abs(eB - e_nobl).max()),
    bl_tcp_mm=float(max(s["backlash"] for s in SIG) * ARCMIN * 0.76 * 1000))

# 采样：控制周期 2 ms 的零阶保持相当于又加了约半个周期的延迟。单关节的离散模型（与仿真相同：每 0.5 ms 一步，每 4 步更新一次力矩，
# 测量延迟 nd 步）：一个控制周期的转移矩阵的谱半径 > 1 就不稳定。A 的腕关节 J6 在 1.0 ms 与 1.5 ms 之间失稳，与仿真一致
rhoA = [pd_discrete_rho(MdP[5], KP_A[5], KV_A[5], nd) for nd in range(0, 7)]
nd_crit = next(nd for nd, r in enumerate(rhoA) if r > 1)
assert rhoA[2] < 1 < rhoA[3]
osc_dl = sorted(c["delay"] for c, r in zip(cases, res["A"]) if r["v_tail"] > OSC)
ok_dl = sorted(c["delay"] for c, r in zip(cases, res["A"]) if r["v_tail"] <= OSC)
assert ok_dl[-1] < osc_dl[0]
out(rhoA=rhoA, rho_nd2=rhoA[2], rho_nd3=rhoA[3], ndA_ms=nd_crit * 0.5, A_ok_max_ms=ok_dl[-1] * 1000, A_osc_min_ms=osc_dl[0] * 1000,
    kdTc_I6=KV_A[5] * 0.002 / MdP[5], Ieff=(1 / np.diag(np.linalg.inv(MP))).tolist(), C_vj=res["C"][int(np.argmax([c["delay"] for c in cases]))]["vj_tail"].tolist())

# 图 29.4.2 用：一个延迟 2.5 ms 的典型情形（名义负载与摩擦）下三种控制器的 TCP 误差随时间
typ = dict(delay=0.0025)
curves = {k: cr_track(**v, **typ) for k, v in CTRL.items()}
out(typ_A=curves["A"]["e_tcp"] * 1000, typ_B=curves["B"]["e_tcp"] * 1000, typ_C=curves["C"]["e_tcp"] * 1000,
    typ_oscA=bool(curves["A"]["v_tail"] > OSC), typ_oscC=bool(curves["C"]["v_tail"] > OSC))

# ---------------------------------------------------------------- 习题
# 29.4.2：腕关节 J6 用 B 的增益，库仑摩擦没有补偿时的静差
out(ex_static_B6_mrad=FC0[5] / kpB[5] * 1000, ex_static_A6_mrad=FC0[5] / KP_A[5] * 1000, fc6=FC0[5])
# 29.4.3：kp 乘 4、kv 乘 2（ζ 不变时 ω_n 乘 2）——临界延迟
out(ex_T_x4_ms=pd_delay_margin(Md[5], 4 * KP_A[5], 2 * KV_A[5])[2] * 1000)
