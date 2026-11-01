"""15.5 节：无穷区间上的反常积分——∫₁^T x^{−p} dx 随 T 的变化（p = 1 发散、p = 2 收敛）；关节制动时阻尼器在无穷长时间内
耗散的能量 b∫₀^∞ ω² dt 等于初始动能，以及多长时间耗散 99%；∫₀^∞ e^{−x²} dx 截断计算的误差；∫₀^∞ sin x / x 的缓慢收敛。"""
import math

from scipy import special

from _quad import gauss
from bookout import out

out(pow_tab="\n".join(f"| {T:g} | {math.log(T):.3f} | {1 - 1 / T:.6f} |" for T in (10, 100, 1e4, 1e6)))
# 关节阻尼制动：J ω' = −b ω，ω = ω₀ e^{−t/τ}，τ = J/b
J, b, w0 = 0.5, 0.2, 2.0
tau = J / b
out(tau=tau, E_damp=b * w0 * w0 * tau / 2, E_kin=0.5 * J * w0 * w0, t99=tau / 2 * math.log(100))
# ∫₀^∞ e^{−x²}：截断到 L，尾巴不超过 e^{−L²}/(2L)
rows = []
for L in (2, 3, 4, 5):
    v = sum(gauss(lambda x: math.exp(-x * x), k * L / 8, (k + 1) * L / 8, 10) for k in range(8))
    rows.append(f"| {L} | {v:.12f} | {abs(v - math.sqrt(math.pi) / 2):.1e} | {math.exp(-L * L) / (2 * L):.1e} |")
out(gauss_tab="\n".join(rows), half_sqrt_pi=math.sqrt(math.pi) / 2)
out(si_tab="\n".join(f"| {T:g} | {special.sici(T)[0]:.6f} | {special.sici(T)[0] - math.pi / 2:+.2e} |" for T in (10, 100, 1000)))
