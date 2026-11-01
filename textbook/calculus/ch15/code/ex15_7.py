"""15.7 节：审敛法与 Γ 函数——Γ(n) = (n − 1)!、Γ(1/2) = √π 的数值核对；
减速器寿命的韦布尔分布：可靠度 R(t) = exp(−(t/η)^β)，平均寿命 MTTF = ∫₀^∞ R dt = ηΓ(1 + 1/β)，B10 寿命。"""
import math

from scipy import integrate

from bookout import out


def gamma_num(x):
    v, _ = integrate.quad(lambda t: t ** (x - 1) * math.exp(-t), 0, math.inf)
    return v


out(g_tab="\n".join(f"| {x:g} | {gamma_num(x):.8f} | {math.gamma(x):.8f} |" for x in (0.5, 1, 1.5, 2, 3, 5)), sqrt_pi=math.sqrt(math.pi))
eta = 20000.0          # 特征寿命（h）
rows = []
for beta in (1.0, 1.5, 2.0, 3.0):
    m_num = eta * integrate.quad(lambda u: math.exp(-u ** beta), 0, math.inf)[0]       # t = ηu
    m_f = eta * math.gamma(1 + 1 / beta)
    b10 = eta * (-math.log(0.9)) ** (1 / beta)
    rows.append(f"| {beta:g} | {m_num:.0f} | {m_f:.0f} | {b10:.0f} |")
out(weib_tab="\n".join(rows), eta=eta)
