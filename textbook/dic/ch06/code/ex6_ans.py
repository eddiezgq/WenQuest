"""第 6 章部分习题答案中的数值（06-99.md“部分习题答案与提示”引用）。与正文程序用同一个模型。"""
import math

from bookout import out
from mos import P, ff_timing, gamma_self, r_ratio, tau

r = r_ratio()
g = gamma_self()
tu = tau()
S = P["arith_syn"]
g_c = (2 + 2 * r) / (1 + r)
p_aoi = g * (3 + 2 * r) / (1 + r)
d_bit = (g_c + 4) + p_aoi
d_pg, d_sum = 4 + 4 * g, 1 + 4 * g

# 6.1.2：64 位行波进位
D64 = d_pg + 63 * d_bit + d_sum
out(a612_tau=D64, a612_ns=D64 * tu * 1e9)
# 6.1.3：进位选择的最优分组（t_mux 取一个进位位的延时）
n = 32
k = math.sqrt(n)
out(a613_k=k, a613_blocks=n / k)
# 6.1.4：16 位累加器、400 MHz：满足预算的结构里面积最小的
ff = ff_timing()
budget = 1 / 400e6 - ff["tcq"] - ff["tsu"]
ok = [kk for kk in ("rca", "cla", "csel", "bk", "ks") if S[f"add_{kk}_16"]["delay"] * 1e-12 <= budget]
best = min(ok, key=lambda kk: S[f"add_{kk}_16"]["area"])
okm = [kk for kk in ("rca", "cla", "csel", "bk", "ks") if S[f"add_{kk}_16"]["delay_amin"] * 1e-12 <= budget]
bestm = min(okm, key=lambda kk: S[f"add_{kk}_16"]["area_min"])
out(a614_best=best, a614_n=len(ok), a614_area=S[f"add_{best}_16"]["area"], a614_budget=budget * 1e12,
    a614_rca_dm=S["add_rca_16"]["delay_amin"], a614_bestm=bestm, a614_bestm_a=S[f"add_{bestm}_16"]["area_min"],
    a614_bestm_d=S[f"add_{bestm}_16"]["delay_amin"])
# 6.2.1：Kogge–Stone 的前缀单元个数 n·log2 n − n + 1
for m in (16, 32, 64):
    out(**{f"a621_{m}": m * int(math.log2(m)) - m + 1})
# 6.3.1：乘数 123 的基 4 Booth 编码
b = 123
bits = [0] + [(b >> i) & 1 for i in range(10)]
digits = []
for i in range(5):
    b0, b1, b2 = bits[2 * i], bits[2 * i + 1], bits[2 * i + 2]
    digits.append(-2 * b2 + b1 + b0)
out(a631=" ".join(f"{x:+d}" for x in digits), a631_check=sum(dg * 4 ** i for i, dg in enumerate(digits)))


# 6.3.2：32 位乘法的部分积行数与压缩级数
def levels(rows):
    seq, h = [2], 2
    while h < rows:
        h = h * 3 // 2
        seq.append(h)
    return len(seq) - 1


def booth_height(n):
    """无符号 n 位基 4 Booth：各列的位数（部分积 n + 2 位、取反加 1 的位、符号处理的常数位），取最高的一列。"""
    W, nd = 2 * n, n // 2 + 1
    cols = [0] * W
    const = 0
    for i in range(nd):
        for j in range(n + 2):
            if 2 * i + j < W:
                cols[2 * i + j] += 1
        if 2 * i < W:
            cols[2 * i] += 1
        const -= 1 << (2 * i + n + 1)
    const %= 1 << W
    for k in range(W):
        cols[k] += const >> k & 1
    return max(cols)


out(a632_plain=levels(32), a632_booth=levels(booth_height(32)), a632_bh=booth_height(32))
