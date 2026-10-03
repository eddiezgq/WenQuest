"""1.5 节：数学归纳法的例子（前 n 个奇数之和）；“试了很多次都对”不等于证明（n² + n + 41）。"""
from bookout import out


def is_prime(m):
    if m < 2:
        return False
    k = 2
    while k * k <= m:
        if m % k == 0:
            return False
        k += 1
    return True


assert all(sum(2 * k - 1 for k in range(1, n + 1)) == n * n for n in range(1, 1001))
first_bad = next(n for n in range(0, 100) if not is_prime(n * n + n + 41))
out(checked=1000, first_bad=first_bad, bad_value=first_bad**2 + first_bad + 41, factor=41)
# 费马猜想的反例（欧拉 1732 年发现）：费马数 2^(2^n) + 1 在 n = 5 时不是素数
F5 = 2 ** 32 + 1
out(F5=F5, F5_factor=641, F5_other=F5 // 641)
assert F5 % 641 == 0
