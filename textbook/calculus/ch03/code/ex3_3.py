"""3.3 节：ε–N 定义的计算——对给定的 ε 求出 N（证明中给出的 N 与实际最小的 N 比较）。"""
import math
from fractions import Fraction

from bookout import out


def smallest_N(a, L, eps, nmax=10**7):
    """第一个满足 |a(n) − L| < ε 的下标（只对单调趋近的数列用）。定义 3.3.1 中最小可用的 N 是它减 1（n > N）。"""
    n = 1
    while abs(a(n) - L) >= eps:
        n += 1
    return n


rows = []
for eps_s in ("0.1", "0.01", "0.001", "0.000001"):
    eps, E = float(eps_s), Fraction(eps_s)
    # 算例 3.3.2：a_n = (3n + 1)/(2n − 1) → 3/2；|a_n − 3/2| = 5/(2(2n − 1)) < ε ⇔ n > 5/(4ε) + 1/2
    N_proof = math.floor(5 / (4 * E) + Fraction(1, 2))              # N = ⌊5/(4ε) + 1/2⌋，n > N 时 n > 5/(4ε) + 1/2
    N_true = smallest_N(lambda n: (3 * n + 1) / (2 * n - 1), 1.5, eps) - 1
    # 算例 3.3.3：q^n → 0，q = 0.9；用伯努利不等式得到的 N 与真正最小的 N
    q = 0.9
    h = Fraction(10, 9) - 1                                         # q = 1/(1 + h)，h = 1/9
    N_bern = math.ceil(1 / (E * h))                                 # N ≥ 1/(εh)，n > N 时 nh > 1/ε
    N_q = math.ceil(math.log(eps) / math.log(q))
    while q**N_q >= eps:
        N_q += 1
    rows.append((eps, N_proof, N_true, N_bern, N_q - 1))
    first_q = N_q
fmt = lambda e: f"{e:g}".replace("1e-06", "$10^{-6}$")
out(eps_table="\n".join(f"| {fmt(e)} | {a} | {b} | {c} | {d} |" for e, a, b, c, d in rows))
out(N_bern_6=rows[-1][3], N_q_6=first_q)
