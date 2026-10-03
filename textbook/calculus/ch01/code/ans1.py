"""本章“部分习题答案”中的数值。"""
import math

from bookout import out

# 习题 1.3.2：10000 元，年利率 5%，十年
P, r = 10000, 0.05
out(e132_y=P * (1 + r) ** 10, e132_m=P * (1 + r / 12) ** 120, e132_d=P * (1 + r / 365) ** 3650, e132_c=P * math.exp(0.5))

# 习题 1.4.1：正 n 边形面积
out(**{f"e141_{n}": n / 2 * math.sin(2 * math.pi / n) for n in (6, 12, 24, 96)})

# 习题 1.4.3
out(e143_y=22 / 7 - math.pi, e143_m=355 / 113 - math.pi)

# 习题 1.5.7：2^n > n² 何时成立（n ≤ 100）
ok = [n for n in range(1, 101) if 2**n > n * n]
assert ok == [1] + list(range(5, 101))
out(e157_ok=1)

# 习题 1.1.5：x³ 的 L_n、R_n
for n in (10, 100, 1000):
    R = sum((k / n) ** 3 for k in range(1, n + 1)) / n
    L = sum((k / n) ** 3 for k in range(0, n)) / n
    out(**{f"e115_R{n}": R, f"e115_L{n}": L})

# 习题 1.3.4：步长系数 0.25、0.5、0.9、1.1，各走 10 步
for c in (0.25, 0.5, 0.9, 1.1):
    x = 0.0
    for _ in range(10):
        x -= c * 2 * (x - 3)
    out(**{f"e134_{int(c * 100)}": x})
