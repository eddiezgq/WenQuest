"""18.6 节：黎曼–斯蒂尔切斯积分——UR5e 上臂“铝管 + 两端关节模块”（实验 17.4）的质量分布函数 m(x) 在两端有跳跃，
绕肩关节的转动惯量 ∫x² dm 的斯蒂尔切斯和；量程 ±50 N 的力传感器读数（真实力 N(0, 40²) 被截断）的均方值：
读数的分布函数在 ±50 N 处有跳跃。"""
import math

from scipy import integrate, stats

from bookout import out

L, ro, ri, rho, m1, m2 = 0.425, 0.045, 0.041, 2700.0, 3.55, 3.55
lam = rho * math.pi * (ro * ro - ri * ri)


def m(x):          # 从 x = −∞ 到 x 的累计质量（只计质量沿杆长的分布）
    if x < 0:
        return 0.0
    return m1 + lam * min(x, L) + (m2 if x >= L else 0.0)


I_ex = lam * L ** 3 / 3 + m2 * L * L
rows = []
for n in (10, 100, 1000):
    a, b = -0.01, L + 0.01
    h = (b - a) / n
    s = sum(((a + (k + 0.5) * h) ** 2) * (m(a + (k + 1) * h) - m(a + k * h)) for k in range(n))
    rows.append(f"| {n} | {s:.5f} | {s - I_ex:+.1e} |")
out(lam=lam, M=m(1), I_ex=I_ex, I_tube=lam * L ** 3 / 3, I_mod=m2 * L * L, st_tab="\n".join(rows))
# 截断的传感器读数
sig, F = 40.0, 50.0
p_hi = 1 - stats.norm.cdf(F / sig)
cont = integrate.quad(lambda x: x * x * stats.norm.pdf(x, 0, sig), -F, F)[0]
EY2 = cont + 2 * F * F * p_hi
out(sat_p=2 * p_hi * 100, sat_EY2=EY2, sat_rms=math.sqrt(EY2), sat_sig=sig, sat_under=(1 - math.sqrt(EY2) / sig) * 100)
