"""3.5 节：夹逼准则与单调有界准则——刘徽不等式夹出 π；n^(1/n) 的夹逼；求 √2 的迭代单调减少、有下界，
误差每步约平方一次（与二分法比较，用 60 位十进制精度计算）；a_{n+1} = √(2 + a_n)。"""
import math
from decimal import Decimal, getcontext

from bookout import out

# 刘徽不等式：S_{2n} < π < S_{2n} + (S_{2n} − S_n)，用稳定的倍增公式
a, n = 1.0, 6
S = {6: 3 * math.sqrt(3) / 2}
while n < 6 * 2**10:
    S[2 * n] = n * a / 2
    a = a / math.sqrt(2 + math.sqrt(4 - a * a))
    n *= 2
rows = []
for m in (12, 24, 96, 192, 768, 3072):
    lo, hi = S[m], 2 * S[m] - S[m // 2]
    assert lo < math.pi < hi
    rows.append((m, lo, hi))


def sci(v):
    m, e = f"{v:.2e}".split("e")
    return f"${m}\\times 10^{{{int(e)}}}$"


out(liu_sq="\n".join(f"| {m} | {lo:.8f} | {hi:.8f} | {sci(hi - lo)} |" for m, lo, hi in rows))
out(w192=rows[3][2] - rows[3][1], w3072=rows[5][2] - rows[5][1])

# n^(1/n) 的夹逼：1 ≤ n^(1/n) ≤ 1 + √(2/(n−1))
for k in (10, 100, 10**4, 10**6):
    out(**{f"nr{k}": k ** (1 / k), f"ub{k}": 1 + math.sqrt(2 / (k - 1))})

# 求 √2：x_{k+1} = (x_k + 2/x_k)/2 与二分法，用 60 位十进制精度
getcontext().prec = 60
two = Decimal(2)
r = two.sqrt()
x = Decimal(2)
lo, hi = Decimal(1), Decimal(2)
tab = []
for k in range(1, 8):
    eh = abs(x - r)
    eb = abs((lo + hi) / 2 - r)
    tab.append((k, eh, eb))
    x = (x + two / x) / 2
    m = (lo + hi) / 2
    lo, hi = (m, hi) if m * m < two else (lo, m)


def tex(d):
    if d == 0:
        return "0"
    m, e = f"{float(d):.2e}".split("e")
    return f"${m}\\times 10^{{{int(e)}}}$"


out(heron_tab="\n".join(f"| {k} | {tex(eh)} | {tex(eb)} |" for k, eh, eb in tab))
# 误差比 e_{k+1}/e_k² → 1/(2√2)
ratios = [float(tab[i + 1][1] / tab[i][1] ** 2) for i in range(4)]
out(ratio4=ratios[3], ratio_lim=1 / (2 * math.sqrt(2)))
# 二分法需要多少步才能达到 10^(−48)
out(bis_steps=math.ceil(48 / math.log10(2)))

# a_{n+1} = √(2 + a_n)，a_1 = √2，单调增加、以 2 为上界，极限 2
s = math.sqrt(2)
seq = [s]
for _ in range(9):
    s = math.sqrt(2 + s)
    seq.append(s)
out(rec="、".join(f"{v:.6f}" for v in seq[:5]), rec10=seq[9], rec_err10=2 - seq[9])
