"""14.1 节：分部积分——几个基本例子的数值核对；一阶系统误差 e = e₀e^{−t/τ} 的 IAE、ISE、ITAE 指标（分部积分给出的公式）；
沃利斯公式（∫₀^{π/2} sinⁿx dx 的递推）；泰勒公式的积分型余项。"""
import math

from bookout import out


def mid(f, a, b, n=200000):
    h = (b - a) / n
    return sum(f(a + (k + 0.5) * h) for k in range(n)) * h


out(xex=mid(lambda x: x * math.exp(x), 0, 1),                          # = 1
    lnx=mid(math.log, 1, math.e),                                       # = 1
    atan=mid(math.atan, 0, 1), atan_x=math.pi / 4 - math.log(2) / 2)

# 误差指标：e₀ = 1（如 1°），τ 取几个值；积分到 20τ 已足够
rows = []
for tau in (0.05, 0.1, 0.2):
    e = lambda t: math.exp(-t / tau)
    T = 20 * tau
    rows.append(f"| {tau:g} | {mid(e, 0, T, 20000):.4f} | {mid(lambda t: e(t) ** 2, 0, T, 20000):.4f} | "
                f"{mid(lambda t: t * e(t), 0, T, 20000):.5f} | {tau:.4f} | {tau / 2:.4f} | {tau * tau:.5f} |")
out(ise_tab="\n".join(rows))


# 沃利斯公式
def wallis(n):
    if n == 0:
        return math.pi / 2
    if n == 1:
        return 1.0
    return (n - 1) / n * wallis(n - 2)


rows = []
for n in (2, 3, 4, 5, 6, 8):
    rows.append(f"| {n} | {wallis(n):.8f} | {mid(lambda x: math.sin(x) ** n, 0, math.pi / 2, 20000):.8f} |")
out(wallis_tab="\n".join(rows))

# 积分型余项：e^x 在 0 处展开到 3 次，x = 1
P3 = 1 + 1 + 1 / 2 + 1 / 6
R = mid(lambda t: (1 - t) ** 3 * math.exp(t), 0, 1) / math.factorial(3)
out(P3=P3, R_true=math.e - P3, R_int=R)
