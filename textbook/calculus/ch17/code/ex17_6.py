"""17.6 节：能量、功率与电机耗电——水平关节（不计重力）按五次多项式在 1 s 内转 90°，停 1 s，循环往复：
惯性力矩与摩擦力矩、机械功率（正负）、动能峰值、铜损 ∫i²R dt、摩擦耗能、每个循环的耗电（有无能量回收），均方根电流，
以及 960 Wh 电池能做多少个循环。"""
import math

from scipy import integrate

from bookout import out

J, b = 0.6, 0.4                    # 关节侧转动惯量 kg·m²、黏性摩擦 N·m·s/rad
kt, N, R = 0.08, 50, 0.6           # 电机力矩常数 N·m/A、减速比、绕组电阻 Ω
D, T, dwell = math.pi / 2, 1.0, 1.0
w = lambda t: D / T * 30 * (t / T) ** 2 * (1 - t / T) ** 2
a = lambda t: D / T ** 2 * 60 * (t / T) * (1 - t / T) * (1 - 2 * t / T)
tau = lambda t: J * a(t) + b * w(t)
P = lambda t: tau(t) * w(t)
i = lambda t: tau(t) / (kt * N)
Pp = integrate.quad(lambda t: max(P(t), 0), 0, T, limit=200)[0]
Pn = integrate.quad(lambda t: min(P(t), 0), 0, T, limit=200)[0]
Ecu = integrate.quad(lambda t: i(t) ** 2 * R, 0, T)[0]
Efr = integrate.quad(lambda t: b * w(t) ** 2, 0, T)[0]
Ek = 0.5 * J * w(T / 2) ** 2
i_rms = math.sqrt(integrate.quad(lambda t: i(t) ** 2, 0, T)[0] / (T + dwell))
i_max = max(abs(i(k / 1000)) for k in range(1001))
E_noregen = integrate.quad(lambda t: max(P(t) + i(t) ** 2 * R, 0), 0, T, limit=200)[0]   # 电功率为正的部分（不回收）
E_regen = Pp + Pn + Ecu                         # 制动段回收（理想）
out(J=J, b=b, kt=kt, N=N, R=R, Ek=Ek, Pp=Pp, Pn=Pn, Ecu=Ecu, Efr=Efr, net_mech=Pp + Pn, P_peak=max(P(k / 1000) for k in range(1001)),
    i_rms=i_rms, i_max=i_max, E_noregen=E_noregen, E_regen=E_regen,
    cycles_noregen=960 * 3600 / E_noregen, cycles_noregen_w=960 * 3600 / E_noregen / 1e4, Pn_abs=-Pn, cycles_regen=960 * 3600 / E_regen, avgW=E_noregen / (T + dwell))
