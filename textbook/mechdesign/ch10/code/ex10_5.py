"""10.6 安全系数的确定：从“多体动力学”到“仿真与分析”，再把安全系数拆开。

算例 10.6.1  WQ-CR5（机器人厂原件 wqcr5.py 生成的模型，数字工厂“多体动力学”的同一个求解器 cae/mbd.py）带 5 kg，手臂从水平以上 0.5 rad
            向下摆到水平并制动停住（J2 梯形速度，用时 0.6 s，加减速各占 25%，本书设定的“快速摆动后制动停止”；急停、碰撞要另算）。
            读出肘关节 J3 处小臂一侧
            受到的力矩（“关节反力”通道 rm.link3）的最大值，与静止伸直时之比就是动载系数 K_d；把大臂示例零件的预设载荷乘 K_d，
            用 CAE 同一套程序算一次（网格 7 mm），得到这一时刻的最大冯·米塞斯应力和安全系数；运动用时从 1.0 s 缩短到 0.4 s，K_d 怎样变；
            刚体动力学不含结构的弹性振动，梯形速度的加速度是阶跃，实际的动载还会再放大一些（γ_F 管这一项）；
算例 10.6.2  安全系数的分项：载荷（K_d，动力学给出）、材料（材料库的屈服强度是标准规定的最低值）、计算模型（有限元：管与法兰内角的
            网格误差，程序 10.4.1 的收敛研究给出量级；梁理论与有限元之差）、后果（协作机器人与人共处，本书取 1.5）；要求的安全系数
            与有限元算出的比较；
图 10.6.1。
"""
import math

import numpy as np

import _ch10 as H
from bookout import T, figure, out, style
from cae import mbd, mbd_models as MM, wqcr5 as W

AL = H.mat("6061-T6")
PATH = MM.robot_path("B-ARM-WQCR5")
Q0 = dict(zip(W.JOINTS, np.radians(W.OUTSTRETCHED_DEG)))
PAY = [{"body": "link6", "mass": W.PAYLOAD_KG, "pos": [float(x) for x in W.tcp_local()]}]
SWING = 0.5                                        # rad，从水平以上摆下来（J2 取负为抬起）


def run(t_move):
    q = dict(Q0)
    q["J2"] = -SWING
    dr = [{"joint": "J2", "kind": "move", "to": 0.0, "t0": 0.0, "t1": t_move}] + [{"joint": j, "kind": "hold"} for j in W.JOINTS if j != "J2"]
    info, ch, _ = mbd.simulate(mbd.load_spec(path=PATH), {"duration_s": t_move + 0.3, "initial": q, "payloads": PAY, "drives": dr, "sample_hz": 500})
    return info, ch


# 静止伸直时的同一个通道
_, ch0, _ = mbd.simulate(mbd.load_spec(path=PATH), {"duration_s": 0.3, "initial": Q0, "payloads": PAY,
                                                 "drives": [{"joint": j, "kind": "hold"} for j in W.JOINTS], "sample_hz": 500})
M_static = float(ch0["rm.link3.abs"][-1])
T_MOVE = 0.6
info, ch = run(T_MOVE)
rm = np.asarray(ch["rm.link3.abs"])
t = np.asarray(ch["t"])
Kd = float(rm.max()) / M_static
t_peak = float(t[int(np.argmax(rm))])
tau_J2 = max(d["peak"] for d in info["drives"] if d["joint"] == "J2")
sweep = []
for tm in (1.0, 0.8, 0.6, 0.5, 0.4):
    inf_, c_ = run(tm)
    sweep.append((tm, float(np.max(c_["rm.link3.abs"])) / M_static, max(d["peak"] for d in inf_["drives"] if d["joint"] == "J2")))

# 有限元：预设载荷 × K_d
p, step, faces, loads, ex = H.upper_arm(scale=Kd)
st, surf, P, STR = H.fe_solve(step, loads, 7.0, AL)
vm_dyn = st["vm_max_mpa"]
SF_fe = AL["yield_mpa"] / vm_dyn
beam_dyn = ex["formula"]["vm_mpa"] * Kd

# 分项系数
g_load = Kd                                         # 已经乘进载荷里了，这里只为列表
SY_MIN = 241.0                                      # 6061-T6 挤压管的最低屈服强度（ASTM B221：35 ksi）；材料库的 276 MPa 是典型值
g_mat = AL["yield_mpa"] / SY_MIN                     # 用典型值算安全系数，就要再除这个系数
g_model = 1.3                                       # 有限元的模型误差：内角是尖角、应力随网格变（程序 10.4.1 的外推值约是 7 mm 网格的 1.3 倍），螺孔未建模，本书取 1.3
g_cons = 1.5                                        # 后果：协作机器人与人共处，断了会砸到人，本书取 1.5
g_load_dyn = 1.3                                    # 载荷：刚体动力学没算的弹性振动放大、操作误差，本书取 1.3（碰撞由控制系统限力）
S_req = g_load_dyn * g_mat * g_model * g_cons

plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.4, 3.0))
a0.plot(t, rm, color="#1f77b4", lw=1.3, label=T(f"运动 {T_MOVE:g} s", f"move {T_MOVE:g} s"))
a0.axhline(M_static, color=H.MUTED, lw=0.8, ls="--", label=T("静止伸直", "held outstretched"))
a0.axvline(t_peak, color="#d62728", lw=0.6, ls=":")
a0.set_xlabel(T("时间 / s", "Time / s"), fontsize=7.0)
a0.set_ylabel(T("J3 处的力矩 / N·m", "Moment at J3 / N·m"), fontsize=7.0)
a0.legend(fontsize=6.0, frameon=False, loc="upper left")
a0.tick_params(labelsize=6.2)
a0.set_title(T(f"(a) 多体动力学：K_d = {Kd:.2f}", f"(a) Multibody dynamics: K_d = {Kd:.2f}"), fontsize=7.2)
a1.plot([s[0] for s in sweep], [s[1] for s in sweep], "o-", color="#d62728", lw=1.3, ms=3.5)
a1.invert_xaxis()
a1.set_xlabel(T("摆动用时 / s", "Swing time / s"), fontsize=7.0)
a1.set_ylabel(T("动载系数 K_d", "Dynamic factor K_d"), fontsize=7.0)
a1.tick_params(labelsize=6.2)
a1.set_title(T("(b) 动作越快，动载越大", "(b) Faster motion, larger dynamic load"), fontsize=7.2)
fig.tight_layout()
figure(fig, "fig10_6_1")

out(swing=SWING, t_move=T_MOVE, M_static=M_static, M_peak=float(rm.max()), Kd=Kd, t_peak=t_peak, tau_J2=tau_J2,
    Kd10=sweep[0][1], Kd04=sweep[-1][1], tau04=sweep[-1][2],
    vm_dyn=vm_dyn, SF_fe=SF_fe, beam_dyn=beam_dyn, sy=AL["yield_mpa"], el=st["elements"],
    sy_min=SY_MIN, g_mat=g_mat, g_model=g_model, g_load_dyn=g_load_dyn, g_cons=g_cons, S_req=S_req, margin=SF_fe / S_req)
