"""1.3 节的计算：

算例 1.3.1  单摆的周期可能与质量 m、摆长 L、重力加速度 g 有关。设 T = C m^a L^b g^c，由量纲列出方程组并求解 a、b、c；
            C 由实验或精确理论定出（2π）。
算例 1.3.2  弗劳德数 Fr = v²/(gL)：人和许多动物在 Fr ≈ 0.5 时由走变跑。用它估算腿长约 0.9 m 的人与
            Unitree Go2 四足机器人（站立时髋关节高约 0.28 m）走跑转换的速度（图 1.3.1）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

# ---- 算例 1.3.1：量纲矩阵。行：M、L、T 的指数；列：m、L、g
D = np.array([[1, 0, 0],      # M
              [0, 1, 1],      # L
              [0, 0, -2]],    # T
             float)
rhs = np.array([0, 0, 1])      # [T] = M⁰ L⁰ T¹
a, b, c_ = np.linalg.solve(D, rhs)
assert np.allclose([a, b, c_], [0, 0.5, -0.5])

# ---- 算例 1.3.2
Fr = 0.5
L_h, L_go2 = 0.9, 0.28
v_h = math.sqrt(Fr * g * L_h)
v_go2 = math.sqrt(Fr * g * L_go2)
ratio = math.sqrt(L_h / L_go2)

out(a=a, b=b, c=c_, Fr=Fr, L_h=L_h, L_go2=L_go2, v_h=v_h, v_go2=v_go2, ratio=ratio)

plt = style()
fig, ax = plt.subplots(figsize=(5.0, 3.0))
Ls = np.linspace(0.05, 1.5, 200)
ax.plot(Ls, np.sqrt(Fr * g * Ls), color=d.FIT, lw=2, label=T("$v=\\sqrt{0.5\\,gL}$", "$v=\\sqrt{0.5\\,gL}$"))
for L_, v_, lab in ((L_h, v_h, T("人", "human")), (L_go2, v_go2, "Go2")):
    ax.plot([L_], [v_], "o", color=d.INK)
    ax.annotate(lab + f"  {v_:.1f} m/s", (L_, v_), xytext=(L_ + 0.05, v_ - 0.35), fontsize=9)
ax.set_xlabel(T("腿长 $L$ / m", "leg length $L$ / m")); ax.set_ylabel(T("走跑转换速度 $v$ / (m/s)", "walk–run speed $v$ / (m/s)"))
ax.set_xlim(0, 1.5); ax.set_ylim(0, 3); ax.legend(frameon=False, fontsize=9, loc="upper left"); d.spines(ax)
figure(fig, "fig1_3_1")
