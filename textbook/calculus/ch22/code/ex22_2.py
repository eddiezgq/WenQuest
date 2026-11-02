"""22.2 节：龙格–库塔法。UR5e 上臂（零件库：8.393 kg，质心 0.2125 m，绕肩轴 0.5129 kg·m²）松开制动后从水平位置自由下摆，
I θ″ = −m g d cos θ（θ 从水平向下为负）：欧拉法、休恩法（二阶）、经典四阶 RK 在不同步长下的误差与函数求值次数；
自己写的 RK4 与 MuJoCo 物理引擎（同样参数的单关节模型，积分器 RK4）的比对。"""
import math

import mujoco
import numpy as np
from scipy.integrate import solve_ivp

from bookout import out

m, d, I, g = 8.393, 0.2125, 0.5129, 9.81
c = m * g * d / I
out(arm_m=m, arm_d=d, arm_I=I)
f = lambda t, y: np.array([y[1], -c * math.cos(y[0])])
T = 2.0
sol = solve_ivp(lambda t, y: f(t, y), (0, T), [0.0, 0.0], method="DOP853", rtol=1e-13, atol=1e-14, dense_output=True)
ref = sol.sol(T)


def s_euler(t, y, h):
    return y + h * f(t, y)


def s_heun(t, y, h):
    k1 = f(t, y); k2 = f(t + h, y + h * k1)
    return y + h / 2 * (k1 + k2)


def s_rk4(t, y, h):
    k1 = f(t, y); k2 = f(t + h / 2, y + h / 2 * k1); k3 = f(t + h / 2, y + h / 2 * k2); k4 = f(t + h, y + h * k3)
    return y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def run(step, n):
    """走 n 步到 T，返回末值和全程（各步时刻）最大的角度误差。"""
    h = T / n
    y = np.array([0.0, 0.0]); me = 0.0
    for j in range(n):
        y = step(j * h, y, h)
        me = max(me, abs(y[0] - sol.sol((j + 1) * h)[0]))
    return y, me


rk4 = lambda h: run(s_rk4, round(T / h))[0]
rows = []
for h in (0.02, 0.01, 0.005, 0.0025):
    n = round(T / h)
    e = [run(st, n)[1] for st in (s_euler, s_heun, s_rk4)]
    rows.append(f"| {h * 1000:g} | {e[0]:.2e} | {e[1]:.2e} | {e[2]:.2e} | {n} / {2 * n} / {4 * n} |")
out(rk_tab="\n".join(rows), rk_c=c, rk_T=T, rk_ref_deg=math.degrees(ref[0]))


# 全程最大误差不超过 1e-6 rad 所需的最少步数（二分法），乘以每步的求值次数
def cost(step, per, lo, hi):
    while hi - lo > max(1, lo // 200):
        mid = (lo + hi) // 2
        if run(step, mid)[1] <= 1e-6:
            hi = mid
        else:
            lo = mid
    return per * hi


# 欧拉法太慢，不逐步搜索，按一阶收敛外推：误差 ∝ h
e0 = run(s_euler, 800)[1]
out(cost_euler=round(800 * e0 / 1e-6), cost_heun=cost(s_heun, 2, 1000, 40000), cost_rk4=cost(s_rk4, 4, 50, 400))
# MuJoCo：同样的单关节模型。铰链轴取水平，质点放在质心处并加惯量使绕铰链的惯量为 I
Icm = I - m * d * d
xml = f"""<mujoco><option timestep="0.001" integrator="RK4" gravity="0 0 -9.81"/>
<worldbody><body name="arm" pos="0 0 0"><joint name="j" type="hinge" axis="0 1 0" damping="0" armature="0" frictionloss="0"/>
<inertial pos="{d} 0 0" mass="{m}" diaginertia="{Icm} {Icm} {Icm}"/></body></worldbody></mujoco>"""
model = mujoco.MjModel.from_xml_string(xml)
data = mujoco.MjData(model)
qs = []
for k in range(round(T / 0.001)):
    mujoco.mj_step(model, data)
mj_q = float(data.qpos[0])
# MuJoCo 中绕 y 轴转动 q 时，质心 x 正方向向下转为负 z：q 与本文的 −θ 对应
my = rk4(0.001)
out(mj_q_deg=math.degrees(mj_q), my_deg=math.degrees(-my[0]), mj_diff=abs(mj_q + my[0]), mj_diff_ref=abs(mj_q + ref[0]))
