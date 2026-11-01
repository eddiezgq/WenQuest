"""18.2 节：可积准则——振幅和 Σωᵢ Δxᵢ = U − L 随 n 的变化：连续函数 x²、阶梯函数（零阶保持的速度指令）、
托马伊函数（黎曼函数：x = p/q 时取 1/q，无理数处取 0）、狄利克雷函数。"""
import math

from bookout import out


def thomae_upper(n):
    """[0, 1] n 等分时托马伊函数的上和：每个小区间 [k/n, (k+1)/n] 上的上确界是其中有理数的最小分母的倒数。"""
    s = 0.0
    for k in range(n):
        for q in range(1, n + 1):
            if math.ceil(k * q / n) <= math.floor((k + 1) * q / n):
                s += 1 / q / n
                break
    return s


step = lambda x: 0.2 * math.floor(5 * x)          # 阶梯：每 0.2 一个台阶
rows = []
for n in (10, 100, 1000):
    h = 1 / n
    w_sq = sum(((k + 1) * h) ** 2 - (k * h) ** 2 for k in range(n)) * h
    w_step = 0.0
    for k in range(n):
        a, b = k * h, (k + 1) * h
        vals = [step(a), step(b - 1e-12), step(b)]
        w_step += (max(vals) - min(vals)) * h
    rows.append(f"| {n} | {w_sq:.4f} | {w_step:.4f} | {thomae_upper(n):.4f} | 1 |")
out(osc_tab="\n".join(rows))
