"""29.4 节的计算：仿真与现实的差距。

(1) 算例 29.4.1：延迟。书中 UR5e 模型的执行器是 PD（kp = 2000、500 N·m/rad，kd = 400、100 N·m·s/rad）。单关节 I θ̈ = −kp θ(t − T) − kd θ̇(t − T)
    的穿越频率、相位裕度和临界延迟 T* = φ_m/ω_c（式 (29.4.2)），肩关节（关节 2）与腕关节（关节 6）。
    MuJoCo 中（控制每 0.1 ms 更新一次，近似连续）给 6 个关节都加上同样的测量延迟，用二分法找出开始振荡的延迟。
(2) 算例 29.4.2：域随机化。上下料动作（第 22 章）在“现场”的 UR5e 上执行：负载质量和惯量在名义值的 ±30% 内、
    各关节摩擦在第 26 章示意值的 0.5～1.5 倍内、测量延迟在 0～3 ms 内随机取，控制周期 2 ms（500 Hz）。比较三种控制器：
    A 模型自带的 PD（不加前馈）；B 名义模型的逆动力学与摩擦前馈 + 按 ω_n = 25 rad/s、ζ = 1 设计的 PD；C 同 B，ω_n = 80 rad/s。
    统计 TCP 的最大误差与停住后仍在振荡的次数；名义条件（无随机化、无延迟）下的结果作对照。
(3) 习题：库仑摩擦造成的静差 f_c/kp；增益与临界延迟成反比。
"""
import math

import mujoco
import numpy as np

from _ch29 import (FC_NOM, FV_NOM, KD_MJ, KP_MJ, Q_WORK, payload_parts, payload_xml, pd_delay_margin, pd_gains, track, ur_chain,
                   ur_linear, ur_model)
from bookout import out

# ---------------------------------------------------------------- (1) 延迟
M, K, D = ur_linear(Q_WORK)
Md = np.diag(M)
mar = [pd_delay_margin(Md[j], KP_MJ[j], KD_MJ[j]) for j in range(6)]
out(wc2=mar[1][0], pm2=math.degrees(mar[1][1]), T2_ms=mar[1][2] * 1000, wc6=mar[5][0], pm6=math.degrees(mar[5][1]),
    T6_ms=mar[5][2] * 1000, Tstar_ms=[x[2] * 1000 for x in mar], I2=Md[1], I6=Md[5])

Z6 = np.zeros(6)
HOLD = (Q_WORK, Q_WORK + 0.02, 0.3)                      # 0.3 s 内移动 0.02 rad，再停 1.5 s


def oscillates(delay):
    r = track(KP_MJ, KD_MJ, fc=Z6, fv=Z6, delay=delay, Tc=0.0001, h=0.0001, hold=1.5, move=HOLD)
    return r["v_tail"] > 0.01


assert not oscillates(0.0) and oscillates(0.003)
lo, hi = 0.0, 0.003
for _ in range(7):
    mid = (lo + hi) / 2
    if oscillates(mid):
        hi = mid
    else:
        lo = mid
T_sim = (lo + hi) / 2
assert abs(T_sim - mar[5][2]) < 0.15e-3
out(T_sim_ms=T_sim * 1000, T_sim_res_us=(hi - lo) * 1e6)

# ---------------------------------------------------------------- (2) 域随机化
P = payload_parts()
_, m, d = ur_model(tool=payload_xml(*P))
d.qpos[:] = Q_WORK
mujoco.mj_forward(m, d)
MP = np.zeros((6, 6))
mujoco.mj_fullM(m, d, MP)
MdP = np.diag(MP)                                         # 带负载的质量矩阵对角元（设计 PD 用）
nom = ur_chain(payload=P)
WN_B, WN_C = 25.0, 80.0
kpB, kdB = pd_gains(MdP, WN_B)
kpC, kdC = pd_gains(MdP, WN_C)
TB = pd_delay_margin(MdP[5], kpB[5], kdB[5])[2]
TC = pd_delay_margin(MdP[5], kpC[5], kdC[5])[2]
out(kpB=kpB.tolist(), kdB=kdB.tolist(), kpC=kpC.tolist(), kdC=kdC.tolist(), TB_ms=TB * 1000, TC_ms=TC * 1000,
    kpB2=kpB[1], kpB6=kpB[5], kpC2=kpC[1], kpC6=kpC[5], wnB=WN_B, wnC=WN_C)

CTRL = {
    "A": dict(kp=KP_MJ, kd=KD_MJ),
    "B": dict(kp=kpB, kd=kdB, ff_model=nom, fric_ff=(FC_NOM, FV_NOM)),
    "C": dict(kp=kpC, kd=kdC, ff_model=nom, fric_ff=(FC_NOM, FV_NOM)),
}
rng = np.random.default_rng(2029)
NCASE = 24
cases = []
for _ in range(NCASE):
    s = rng.uniform(0.7, 1.3)
    fs = rng.uniform(0.5, 1.5, 6)
    cases.append(dict(payload=(P[0] * s, P[1], P[2] * s), fc=FC_NOM * fs, fv=FV_NOM * fs, delay=float(rng.uniform(0, 0.003))))

nominal = {k: track(**v, payload=P, delay=0.0) for k, v in CTRL.items()}
res = {k: [track(**v, **c) for c in cases] for k, v in CTRL.items()}
OSC = 0.05                                                 # 停住后 0.5 s 内关节角速度超过 0.05 rad/s 算作振荡
summary = {}
for k in CTRL:
    e = np.array([r["e_tcp"] for r in res[k]]) * 1000
    osc = np.array([r["v_tail"] > OSC for r in res[k]])
    dl = np.array([c["delay"] for c in cases]) * 1000
    summary[k] = dict(e_max=float(e.max()), e_med=float(np.median(e)), n_osc=int(osc.sum()),
                      dl_osc_min=float(dl[osc].min()) if osc.any() else None, e_nom=nominal[k]["e_tcp"] * 1000,
                      osc_nom=bool(nominal[k]["v_tail"] > OSC))
for k in CTRL:
    assert not summary[k]["osc_nom"]
assert summary["B"]["n_osc"] == 0 and summary["A"]["n_osc"] > NCASE // 4 and summary["C"]["n_osc"] > 0
assert summary["B"]["e_max"] < summary["A"]["e_med"]
out(ncase=NCASE, **{f"{k}_{a}": v for k, s in summary.items() for a, v in s.items()})

# 图 29.4.2 用：一个延迟 2.5 ms 的典型情形（名义负载与摩擦）下三种控制器的 TCP 误差随时间
typ = dict(payload=P, fc=FC_NOM, fv=FV_NOM, delay=0.0025)
curves = {k: track(**v, **typ) for k, v in CTRL.items()}
out(typ_A=curves["A"]["e_tcp"] * 1000, typ_B=curves["B"]["e_tcp"] * 1000, typ_C=curves["C"]["e_tcp"] * 1000,
    typ_oscA=bool(curves["A"]["v_tail"] > OSC), typ_oscC=bool(curves["C"]["v_tail"] > OSC))

# ---------------------------------------------------------------- 习题
# 29.4.2：腕关节 3 用 B 的增益，库仑摩擦 0.5 N·m 没有补偿时的静差
out(ex_static_B6_mrad=FC_NOM[5] / kpB[5] * 1000, ex_static_A6_mrad=FC_NOM[5] / KP_MJ[5] * 1000)
# 29.4.3：kp、kd 同乘 s 倍（ζ 不变时 ω_n 乘 √s）——临界延迟
out(ex_T_x4_ms=pd_delay_margin(Md[5], 4 * KP_MJ[5], 2 * KD_MJ[5])[2] * 1000)
