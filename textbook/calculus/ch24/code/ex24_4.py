"""24.4 节：二项式级数。
(1) (1 + x)^α 的系数；√(1 + x) 用一项、两项近似的误差；
(2) 拉线位移传感器（拉线编码器）安装偏斜：读数 √(L² + d²) 与真实位移 L 之差 ≈ d²/(2L)；
(3) 单摆周期：(1 − k² sin²φ)^{−1/2} 用二项式级数展开后逐项积分，T/T₀ = Σ [(2n−1)!!/(2n)!!]² k^{2n}（k = sin(θ₀/2)），
    与精确值（椭圆积分）比较；所需项数。"""
import math

from scipy import special

from bookout import out


def binom(a, n):
    c = 1.0
    for j in range(n):
        c *= (a - j) / (j + 1)
    return c


for x in (0.1, 0.5):
    tag = f"{round(x * 10)}"
    ex = math.sqrt(1 + x)
    out(**{f"sq_{tag}_1": abs(1 + x / 2 - ex), f"sq_{tag}_2": abs(1 + x / 2 - x * x / 8 - ex)})
# (2) 拉线传感器
L, d = 0.5, 0.005
out(dw_L=L * 1000, dw_d=d * 1000, dw_err_um=(math.sqrt(L * L + d * d) - L) * 1e6, dw_approx_um=d * d / (2 * L) * 1e6)
# (3) 单摆周期


def coef(n):
    c = 1.0
    for j in range(1, n + 1):
        c *= (2 * j - 1) / (2 * j)
    return c * c


rows = []
for th in (10, 30, 60, 90, 120, 170):
    k = math.sin(math.radians(th) / 2)
    exact = 2 / math.pi * special.ellipk(k * k)
    s1 = 1 + k * k / 4
    s3 = sum(coef(n) * k ** (2 * n) for n in range(4))
    n, S = 0, 0.0
    while abs(S - exact) > 1e-6 and n < 100000:
        S += coef(n) * k ** (2 * n)
        n += 1
    rows.append(f"| {th} | {exact:.6f} | {s1:.6f} | {s3:.6f} | {n} |")
out(pd_tab="\n".join(rows))
# UR5e 上臂（17.4 节）从水平位置松开自由摆动：摆幅 90°（相对最低点）的复摆
m, d, I, g = 8.393, 0.2125, 0.5129, 9.81
T0 = 2 * math.pi * math.sqrt(I / (m * g * d))
k = math.sin(math.radians(90) / 2)
out(ur_T0=T0, ur_T=T0 * 2 / math.pi * special.ellipk(k * k), ur_T1=T0 * (1 + k * k / 4))
