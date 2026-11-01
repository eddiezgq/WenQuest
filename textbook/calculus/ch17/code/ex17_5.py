"""17.5 节：概率密度与期望——编码器量化误差（均匀分布）的均值与标准差；AGV 停靠位置误差（正态分布）落在公差内的概率；
零件到达间隔（指数分布）；第 15 章减速器韦布尔寿命：期望 ∫ t f(t) dt 与 ∫ R(t) dt 相同。"""
import math

from scipy import integrate

from bookout import out

# 编码器：17 位（每圈 2¹⁷ 个计数），量化误差在 [−q/2, q/2] 上均匀分布
q = 2 * math.pi / 2 ** 17
f = lambda x: 1 / q
mean = integrate.quad(lambda x: x * f(x), -q / 2, q / 2)[0]
var = integrate.quad(lambda x: x * x * f(x), -q / 2, q / 2)[0]
out(enc_q_urad=q * 1e6, enc_mean=mean, enc_sd_urad=math.sqrt(var) * 1e6, enc_sd_ex_urad=q / math.sqrt(12) * 1e6,
    enc_sd_um=math.sqrt(var) * 0.85 * 1e6)                       # 0.85 m 臂长处的位置误差（μm）
# 正态分布：归一化 ∫ e^{−x²/2σ²} dx = σ√(2π)
sig = 3.0                                                              # mm
pdf = lambda x: math.exp(-x * x / (2 * sig * sig)) / (sig * math.sqrt(2 * math.pi))
out(norm_total=integrate.quad(pdf, -math.inf, math.inf)[0])
rows = []
for tol in (3.0, 5.0, 6.0, 9.0):
    p = integrate.quad(pdf, -tol, tol)[0]
    rows.append(f"| ±{tol:g} | {tol / sig:.2f}σ | {p * 100:.2f} | {math.erf(tol / (sig * math.sqrt(2))) * 100:.2f} | {(1 - p) * 1e6:.0f} |")
out(norm_tab="\n".join(rows), norm_sig=sig)
# 指数分布：零件平均每 20 s 到一个，λ = 1/20；等待超过 60 s 的概率；已等 30 s 后再等超过 60 s 的概率
lamb = 1 / 20
P60 = integrate.quad(lambda t: lamb * math.exp(-lamb * t), 60, math.inf)[0]
P90_30 = integrate.quad(lambda t: lamb * math.exp(-lamb * t), 90, math.inf)[0] / integrate.quad(lambda t: lamb * math.exp(-lamb * t), 30, math.inf)[0]
out(exp_mean=integrate.quad(lambda t: t * lamb * math.exp(-lamb * t), 0, math.inf)[0], P60=P60, P90_30=P90_30)
# 韦布尔 η = 20000 h、β = 2：E[T] = ∫ t f dt = ∫ R dt = ηΓ(1.5)
eta, beta = 20000.0, 2.0
fw = lambda t: beta / eta * (t / eta) ** (beta - 1) * math.exp(-(t / eta) ** beta)
out(weib_Et=integrate.quad(lambda u: u * eta * fw(u * eta) * eta, 0, math.inf)[0],
    weib_R=eta * integrate.quad(lambda u: math.exp(-u ** beta), 0, math.inf)[0], weib_ex=eta * math.gamma(1.5))
