"""7.2.5 节：由陀螺仪读数积分姿态（李群积分）。

锥形运动 R(t) = Rot(ẑ, a t) Rot(x̂, b t)，a = 2 rad/s，b = 3 rad/s，物体角速度有闭式 ω_b(t) = (b, a sin bt, a cos bt)，
所以真实姿态精确已知。五种方法积分 Ṙ = R[ω_b]：
  欧拉法（矩阵元素）        R_{k+1} = R_k (I + h[ω_b(t_k)])
  RK4（矩阵元素）           对 9 个元素用经典四阶龙格-库塔法
  李-欧拉法                 R_{k+1} = R_k exp(h[ω_b(t_k)])
  李-中点法                 R_{k+1} = R_k exp(h[ω_b(t_k + h/2)])
  四阶马格努斯法            R_{k+1} = R_k exp(Ω)，Ω = h(ω₁ + ω₂)/2 + (√3/12)h² ω₁ × ω₂（式 (7.2.22)）
测量 t = 2 s 时的姿态误差角和正交性误差 ‖RᵀR − I‖；步长减半，求各方法的阶。再看 100 s 后的正交性误差。
"""
import math

import numpy as np

from _ode import CONE, S3, angle_between, cone_R, cone_wb, lie_integrate as integrate, orth
from bookout import out

# ω_b 的闭式由数值求导核对：[ω_b] = Rᵀ Ṙ
for t in (0.3, 1.7):
    e = 1e-6
    Rd = (cone_R(t + e) - cone_R(t - e)) / (2 * e)
    W = cone_R(t).T @ Rd
    assert np.allclose(W, -W.T, atol=1e-8)
    assert np.allclose([W[2, 1], W[0, 2], W[1, 0]], cone_wb(t), atol=1e-8)

T = 2.0
R_true = cone_R(T)
hs = [0.02, 0.01, 0.005]
meths = ["euler", "rk4", "lie", "mid", "mag4"]
err, ort, order = {}, {}, {}
for m in meths:
    Rs = [integrate(m, T, h) for h in hs]
    err[m] = [math.degrees(angle_between(R, R_true)) for R in Rs]
    ort[m] = [orth(R) for R in Rs]
    order[m] = [math.log2(err[m][i] / err[m][i + 1]) for i in range(2)]
expect = {"euler": 1, "rk4": 4, "lie": 1, "mid": 2, "mag4": 4}
for m, p in expect.items():
    assert all(abs(o - p) < 0.2 for o in order[m]), (m, order[m])
for m in ("lie", "mid", "mag4"):
    assert max(ort[m]) < 1e-13                               # 李群方法：始终是旋转矩阵（只差舍入误差）
assert ort["euler"][0] > 1e-2                                # 欧拉法离开 SO(3)
# 欧拉法：每步 det(I + h[ω]) = 1 + h²|ω|²，行列式不断变大
det_eu = float(np.linalg.det(integrate("euler", T, 0.01)))
w2 = CONE["a"] ** 2 + CONE["b"] ** 2                          # |ω_b|² 为常数
det_pred = (1 + 0.01 ** 2 * w2) ** 200                       # 每步行列式乘 1 + h²|ω|²，共 200 步
assert abs(det_eu - det_pred) < 1e-12

# 长时间：100 s 后 RK4 的正交性误差继续增长，李群方法仍为舍入量级
T_long = 100.0
ort_rk4_long = orth(integrate("rk4", T_long, 0.01))
ort_mag_long = orth(integrate("mag4", T_long, 0.01))
assert ort_rk4_long > 10 * ort["rk4"][1] and ort_mag_long < 1e-12

vals = {}
for m in meths:
    for i in range(3):
        vals[f"err_{m}{i}"] = err[m][i]
        vals[f"ort_{m}{i}"] = ort[m][i]
    for i in range(2):
        vals[f"p_{m}{i}"] = order[m][i]
out(a=CONE["a"], b=CONE["b"], wnorm=math.sqrt(w2), det_eu=det_eu, ort_rk4_long=ort_rk4_long, ort_mag_long=ort_mag_long,
    s3_12=S3 / 12, **vals)
