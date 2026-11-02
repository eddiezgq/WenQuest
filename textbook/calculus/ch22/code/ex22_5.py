"""22.5 节：守恒与辛积分。UR5e 上臂从水平位置松开自由摆动（不计摩擦），步长 10 ms，算 100 s：
显式欧拉、经典 RK4、辛欧拉（半隐式欧拉：先更新角速度、再用新角速度更新角度）、蛙跳法（速度韦尔莱）的能量漂移；
简谐振子一步映射的行列式（面积放大系数）；MuJoCo 默认积分器（Euler）与辛欧拉逐步一致。"""
import math

import mujoco
import numpy as np

from bookout import out

m, d, I, g = 8.393, 0.2125, 0.5129, 9.81
c = m * g * d / I
acc = lambda q: -c * math.cos(q)
E = lambda q, v: 0.5 * v * v + c * math.sin(q)        # 单位质量惯量的能量，初值 0，最低点 −c
h, T = 0.01, 100.0
N = round(T / h)


def run(step):
    q, v = 0.0, 0.0
    es = np.empty(N)
    for n in range(N):
        q, v = step(q, v)
        es[n] = E(q, v)
    return es, q


def s_euler(q, v):
    return q + h * v, v + h * acc(q)


def s_symp(q, v):
    v = v + h * acc(q)
    return q + h * v, v


def s_leap(q, v):
    v = v + h / 2 * acc(q)
    q = q + h * v
    return q, v + h / 2 * acc(q)


def s_rk4(q, v):
    def F(y):
        return np.array([y[1], acc(y[0])])
    y = np.array([q, v])
    k1 = F(y); k2 = F(y + h / 2 * k1); k3 = F(y + h / 2 * k2); k4 = F(y + h * k3)
    y = y + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return y[0], y[1]


res = {}
for name, st in (("eu", s_euler), ("rk4", s_rk4), ("sy", s_symp), ("lf", s_leap)):
    es, q = run(st)
    rel = es / c                                         # 以摆动能量 c 为单位
    res[name] = rel
    out(**{f"{name}_end": float(rel[-1]), f"{name}_max": float(np.max(np.abs(rel)))})
# 欧拉法的能量在第一秒、前 10 秒就增长了多少
out(eu_1s=float(res["eu"][99]), eu_10s=float(res["eu"][999]), rk4_10s=float(res["rk4"][999]),
    rk4_rate=float(res["rk4"][-1] / T))

# 简谐振子 q'' = −ω²q 的一步映射与行列式
w0 = math.sqrt(c * 1.0)                                  # 小振动角频率（在最低点 cos 的导数为 1）
Aeu = np.array([[1, h], [-h * w0 ** 2, 1]])
Asy = np.array([[1 - h * h * w0 ** 2, h], [-h * w0 ** 2, 1]])
out(ho_w0=w0, ho_det_eu=float(np.linalg.det(Aeu)), ho_det_sy=float(np.linalg.det(Asy)),
    ho_growth_100s=float(np.linalg.det(Aeu) ** N), ho_hcrit=2 / w0)

# MuJoCo 默认积分器 Euler：无阻尼时就是辛欧拉
Icm = I - m * d * d
xml = f"""<mujoco><option timestep="{h}" gravity="0 0 -9.81"/>
<worldbody><body name="arm"><joint name="j" type="hinge" axis="0 1 0"/>
<inertial pos="{d} 0 0" mass="{m}" diaginertia="{Icm} {Icm} {Icm}"/></body></worldbody></mujoco>"""
model = mujoco.MjModel.from_xml_string(xml)
data = mujoco.MjData(model)
q, v, md = 0.0, 0.0, 0.0
for n in range(1000):
    mujoco.mj_step(model, data)
    q, v = s_symp(q, v)
    md = max(md, abs(data.qpos[0] + q))
out(mj_integrator=mujoco.mjtIntegrator(model.opt.integrator).name, mj_symp_diff=md)

# 同样的计算量（每秒 100 次加速度计算）：RK4 取 h = 40 ms，蛙跳法取 h = 10 ms，算到 10000 s
def long_rk4(hh, TT):
    y = np.array([0.0, 0.0]); outv = {}
    F = lambda y: np.array([y[1], acc(y[0])])
    for n in range(1, round(TT / hh) + 1):
        k1 = F(y); k2 = F(y + hh / 2 * k1); k3 = F(y + hh / 2 * k2); k4 = F(y + hh * k3)
        y = y + hh / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if n * hh in (100.0, 1000.0, 10000.0) or abs(n * hh - round(n * hh)) < 1e-9 and round(n * hh) in (100, 1000, 10000):
            outv[round(n * hh)] = E(y[0], y[1]) / c
    return outv


def long_lf(hh, TT):
    q, v, mx = 0.0, 0.0, 0.0
    for n in range(round(TT / hh)):
        v += hh / 2 * acc(q); q += hh * v; v += hh / 2 * acc(q)
        mx = max(mx, abs(E(q, v) / c))
    return mx


r = long_rk4(0.04, 10000.0)
out(lg_rk4_100=float(r[100]), lg_rk4_1000=float(r[1000]), lg_rk4_10000=float(r[10000]), lg_lf_max=long_lf(0.01, 10000.0))
