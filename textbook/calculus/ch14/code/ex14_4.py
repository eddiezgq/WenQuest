"""14.4 节：部分分式——无人机停止水平推进后滑行减速：m dv/dt = −(c₁v + c₂v²)。分离变量后用部分分式积出
减速所需的时间与滑行距离，并与数值积分（小步长欧拉法）比较；只有线性阻力时的对照。"""
import math

from bookout import out

m, c1, c2 = 1.5, 0.3, 0.05      # kg，N·s/m，N·s²/m²
v0, v1 = 10.0, 1.0


def t_formula(v0, v1):
    return m / c1 * math.log(v0 * (c1 + c2 * v1) / (v1 * (c1 + c2 * v0)))


def x_formula(v0, v1):
    return m / c2 * math.log((c1 + c2 * v0) / (c1 + c2 * v1))


# 数值核对：小步长积分 dv/dt
dt = 1e-5
v, t, x = v0, 0.0, 0.0
while v > v1:
    a = -(c1 * v + c2 * v * v) / m
    x += v * dt + 0.5 * a * dt * dt
    v += a * dt
    t += dt
out(t_f=t_formula(v0, v1), x_f=x_formula(v0, v1), t_num=t, x_num=x,
    t_lin=m / c1 * math.log(v0 / v1), x_lin=m / c1 * (v0 - v1),
    t_quad=m / c2 * (1 / v1 - 1 / v0), x_quad=m / c2 * math.log(v0 / v1))
rows = []
for va in (8.0, 5.0, 2.0, 1.0, 0.5):
    rows.append(f"| {va:g} | {t_formula(v0, va):.2f} | {x_formula(v0, va):.2f} |")
out(coast_tab="\n".join(rows))
