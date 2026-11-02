"""13.2 节的计算：

算例 13.2.1  机械臂的肘关节带着小臂和 1 kg 负载（绕肘关节 J = 0.272 kg·m²，算例 12.3.2）以 2.0 rad/s 转动，
            碰撞检测触发急停，制动器在 0.050 s 内使它停下。小臂的角动量变化多少？关节受到的平均制动力矩多大？
算例 13.2.2  反作用飞轮转动卫星：小卫星绕某主轴的转动惯量 50 kg·m²，飞轮绕同一轴的转动惯量 0.020 kg·m²。
            飞轮电机先以 +0.050 N·m、后以 −0.050 N·m 的力矩驱动飞轮（先加速后减速），让卫星从静止转过 90° 并停下。
            要多长时间？飞轮的最高转速多大？（图 13.2.1）
算例 13.2.3  四旋翼的偏航：每个螺旋桨的反扭矩 Q = k_Q ω²，k_Q = 5.0×10⁻⁸ N·m/(rad/s)²，悬停转速 1000 rad/s；机身绕竖直轴
            J_z = 0.012 kg·m²。顺时针的一对螺旋桨转速加 δ、逆时针的一对减 δ，δ = 50 rad/s 时偏航力矩多大？
            用“先加速、后减速”在多长时间内转过 90°？总升力变了多少？（图 13.2.2）
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

J, w, tb = 0.272, 2.0, 0.050
out(Ja=J, wa=w, tb=tb, dL=J * w, Mb=J * w / tb)

Js, Jw, Mm, th = 50.0, 0.020, 0.050, math.pi / 2
al_s = Mm / Js                                                  # 电机对飞轮 +M，飞轮对卫星 −M：卫星反向转
Tt = 2 * math.sqrt(th / al_s)
ws_max = al_s * Tt / 2
ww_max = Js * ws_max / Jw                                       # 总角动量为零：Jw ωw = −Js ωs
out(Js=Js, Jw=Jw, Mm=Mm, al_s_e3=al_s * 1e3, Tt=Tt, ws_max=ws_max, ws_deg=math.degrees(ws_max), ww_max=ww_max,
    nw_max=ww_max * 60 / (2 * math.pi), Lmax=Js * ws_max)

t = np.linspace(0, Tt, 801)
ws = np.where(t < Tt / 2, al_s * t, al_s * (Tt - t))
ths = np.where(t < Tt / 2, 0.5 * al_s * t ** 2, th - 0.5 * al_s * (Tt - t) ** 2)
assert abs(ths[-1] - th) < 1e-9
plt = style()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.8))
a1.plot(t, np.degrees(ths), color=d.VA, lw=2); a1.set_xlabel(T("时间 / s", "time / s")); a1.set_ylabel(T("卫星转角 / (°)", "satellite angle / (°)"))
a1.set_title(T("(a) 卫星", "(a) satellite"), fontsize=9.5); d.spines(a1)
a2.plot(t, -Js * ws / Jw * 60 / (2 * math.pi), color=d.VR, lw=2)
a2.axhline(0, color=d.MUTED, lw=0.6)
a2.set_xlabel(T("时间 / s", "time / s")); a2.set_ylabel(T("飞轮转速 / (r/min)", "wheel speed / (r/min)"))
a2.set_title(T("(b) 飞轮（与卫星反向转）", "(b) wheel (turns the opposite way)"), fontsize=9.5); d.spines(a2)
fig.tight_layout()
figure(fig, "fig13_2_1")

# ---- 算例 13.2.3：四旋翼的偏航
kQ, w0, Jz, dl = 5.0e-8, 1000.0, 0.012, 50.0
Q0 = kQ * w0 ** 2
Mz = 2 * kQ * ((w0 + dl) ** 2 - (w0 - dl) ** 2)                 # 两对螺旋桨的反扭矩之差
assert abs(Mz - 8 * kQ * w0 * dl) < 1e-12
alz = Mz / Jz
Tq = 2 * math.sqrt((math.pi / 2) / alz)
thrust = (2 * (w0 + dl) ** 2 + 2 * (w0 - dl) ** 2) / (4 * w0 ** 2) - 1
out(kQ_e8=kQ * 1e8, w0=w0, Jz=Jz, dl=dl, Q0=Q0, Mz=Mz, alz=alz, Tq=Tq, thrust_pct=thrust * 100, wz_max=alz * Tq / 2)

t = np.linspace(0, Tq, 401)
th = np.where(t < Tq / 2, 0.5 * alz * t ** 2, math.pi / 2 - 0.5 * alz * (Tq - t) ** 2)
M = np.where(t < Tq / 2, Mz, -Mz)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.8))
a1.plot(t, M, color=d.VR, lw=2); a1.axhline(0, color=d.MUTED, lw=0.6)
a1.set_xlabel(T("时间 / s", "time / s")); a1.set_ylabel(T("偏航力矩 / (N·m)", "yaw torque / (N·m)")); d.spines(a1)
a1.set_title(T("(a) 反扭矩之差", "(a) difference of reaction torques"), fontsize=9.5)
a2.plot(t, np.degrees(th), color=d.VA, lw=2)
a2.set_xlabel(T("时间 / s", "time / s")); a2.set_ylabel(T("机头方向 / (°)", "heading / (°)")); d.spines(a2)
a2.set_title(T("(b) 转过 90°", "(b) turning 90°"), fontsize=9.5)
fig.tight_layout()
figure(fig, "fig13_2_2")
