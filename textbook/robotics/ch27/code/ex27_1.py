"""27.1 节的计算：接触模型。

(1) 算例 27.1.1：SH-301 毛坯（Ø50 mm 钢，2.8 kg）横放在 90° 钢制 V 形块里，每条接触线的载荷、赫兹线接触的半宽与最大压强。
    同一毛坯若换成 Ø10 mm 钢球压在钢板上（同样的载荷），压入量、接触圆半径、最大压强（点接触与线接触的对比）。
(2) 算例 27.1.2：MuJoCo 的软接触。一个球静止在地面上：穿透量与质量无关（1、10、100 kg），与 solref 的时间常数 τ 有关；
    与式 (27.1.7) 的预测比较；默认参数下的穿透量与 (1) 中钢的真实压入量相差多少倍。
"""
import math

from _ch27 import (D_BAR, G0, ball_xml, e_star, hertz_line, hertz_sphere, mj_impedance, mj_rest, mj_rest_penetration,
                   sh301_blank)
from bookout import out

# ---------------------------------------------------------------- (1) 赫兹接触
m_b, r_b, L_b = sh301_blank()
W = m_b * G0
gam = math.radians(45)                               # 90° V 形块：两条接触线的法向与竖直方向成 45°
N_line = W / (2 * math.cos(gam))                     # 每条线的法向载荷
P_len = N_line / L_b                                 # 单位长度载荷
Es = e_star()
b, p0 = hertz_line(P_len, r_b)
b_al, p0_al = hertz_line(P_len, r_b, e_star(E1=70e9, nu1=0.33))     # 习题 27.1.2：铝合金毛坯
# 同样的载荷压一颗 Ø10 mm 钢球
R_ball = 0.005
dl_ball, a_ball, p0_ball = hertz_sphere(N_line, R_ball)
# 刚度：球-平面 dF/dδ = 2E*√R √δ = (3/2)F/δ
k_ball = 1.5 * N_line / dl_ball

# ---------------------------------------------------------------- (2) MuJoCo 的软接触
pen = {}
for m in (1.0, 10.0, 100.0):
    mm, d = mj_rest(ball_xml(m=m))
    pen[m] = -d.contact[0].dist
pen_pred = mj_rest_penetration(0.02, 1.0)
assert all(abs(p / pen_pred - 1) < 1e-6 for p in pen.values())
d_rest = mj_impedance(pen_pred)
taus = [0.005, 0.01, 0.02, 0.04]
pen_tau, pred_tau = [], []
for tau in taus:
    mm, d = mj_rest(ball_xml(solref=f"{tau} 1", dt=min(0.001, tau / 4)), steps=int(4 / min(0.001, tau / 4)))
    pen_tau.append(-d.contact[0].dist)
    pred_tau.append(mj_rest_penetration(tau, 1.0))
err_tau = max(abs(a / b_ - 1) for a, b_ in zip(pen_tau, pred_tau))
assert err_tau < 1e-4
# 习题 27.1.5：0.1 m 的方块（MuJoCo 在四个角各生成一个接触点）
_, dbox = mj_rest(ball_xml().replace('<geom type="sphere" size="0.05" mass="1.0"/>', '<geom type="box" size="0.05 0.05 0.05" mass="1.0"/>'))
pen_box = -min(dbox.contact[i].dist for i in range(dbox.ncon))
assert dbox.ncon == 4
ratio_mj_steel = pen_pred / dl_ball                 # MuJoCo 默认的穿透量是钢球真实压入量的多少倍
pen99 = mj_rest_penetration(0.02, 1.0, imp=(0.99, 0.99, 0.001, 0.5, 2.0))   # 习题 27.1.4
_, d99 = mj_rest(ball_xml().replace('condim="1"/>', 'condim="1" solimp="0.99 0.99 0.001 0.5 2"/>'))
assert abs(-d99.contact[0].dist / pen99 - 1) < 1e-6

out(m_b=m_b, L_b=L_b, W=W, N_line=N_line, P_len=P_len, Es_GPa=Es / 1e9, a_um=b * 1e6, p0_MPa=p0 / 1e6, a_ratio=2 * b / D_BAR, a_al_um=b_al * 1e6, p0_al_MPa=p0_al / 1e6, pen99_mm=pen99 * 1e3,
    dl_ball_um=dl_ball * 1e6, a_ball_um=a_ball * 1e6, p0_ball_MPa=p0_ball / 1e6, k_ball=k_ball / 1e6,
    pen1_mm=pen[1.0] * 1e3, pen10_mm=pen[10.0] * 1e3, pen100_mm=pen[100.0] * 1e3, pen_pred_mm=pen_pred * 1e3, d_rest=d_rest,
    err_tau=err_tau, r_5_40=pen_tau[3] / pen_tau[0], r_20_40=pen_tau[3] / pen_tau[2], pen_box_mm=pen_box * 1e3,
    pen005_mm=pen_tau[0] * 1e3, pen04_mm=pen_tau[3] * 1e3, ratio_mj=ratio_mj_steel)
