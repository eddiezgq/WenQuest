"""15.4 节：自适应积分——夹爪碰到工件时的接触力是一个很窄的冲击脉冲（半正弦，持续 1 ms），叠加在逐渐建立的夹持力上。
在 1 s 内求冲量 ∫F dt：均匀步长的梯形公式要很多点；自适应辛普森把点集中在脉冲附近；scipy 的 quad 作为对照。"""
import math

from scipy import integrate

from _quad import adaptive_simpson, trap
from bookout import T as T_, out

t0, w, Fp, T = 0.4013, 0.001, 400.0, 1.0     # 脉冲起点、持续时间（s）、峰值（N）、统计时长（s）


def F(t):
    hold = 2 * (1 - math.exp(-max(t - t0, 0.0) / 0.05))          # 夹持力逐渐建立到 2 N
    pulse = Fp * math.sin(math.pi * (t - t0) / w) if t0 <= t <= t0 + w else 0.0
    return hold + pulse


hold_ex = 2 * ((T - t0) - 0.05 * (1 - math.exp(-(T - t0) / 0.05)))
pulse_ex = Fp * 2 * w / math.pi
J = hold_ex + pulse_ex
rows = []
for n in (100, 1000, 2000, 10000, 100000):
    v = trap(F, 0, T, n)
    rows.append(f"| {T_("均匀梯形，步长", "uniform trapezoid, step")} {T / n * 1000:g} ms | {n + 1} | {v:.4f} | {abs(v - J) / J * 100:.3f} |")
for tol in (1e-3, 1e-5):
    v, pts = adaptive_simpson(F, 0, T, tol)
    rows.append(f"| {T_("自适应辛普森，容差", "adaptive Simpson, tolerance")} {tol:g} | {len(pts)} | {v:.4f} | {abs(v - J) / J * 100:.3f} |")
q, err, info = integrate.quad(F, 0, T, full_output=1, limit=200)[:3]
rows.append(f"| {T_("scipy quad（不告诉它脉冲在哪里）", "scipy quad (pulse location not given)")} | {info['neval']} | {q:.4f} | {abs(q - J) / J * 100:.3f} |")
q2, err2, info2 = integrate.quad(F, 0, T, points=[t0, t0 + w], full_output=1, limit=200)[:3]
rows.append(f"| {T_("scipy quad（给出脉冲的起止时刻）", "scipy quad (pulse start and end given)")} | {info2['neval']} | {q2:.4f} | {abs(q2 - J) / J * 100:.5f} |")
out(t0=t0, J=J, J_pulse=pulse_ex, J_hold=hold_ex, adapt_tab="\n".join(rows))
v, pts = adaptive_simpson(F, 0, T, 1e-5)
out(n_near=sum(1 for p in pts if abs(p - t0) < 0.01), n_total=len(pts))
