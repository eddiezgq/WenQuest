"""1.1 节：y = x² 在 (1, 1) 处割线斜率的变化；y = x² 下方 [0, 1] 上的面积用 n 个矩形逼近；阿基米德的抛物线弓形。"""
from fractions import Fraction

from bookout import out

# 割线斜率 ((1 + h)² − 1)/h = 2 + h
hs = [1, 0.1, 0.01, 0.001]
out(**{f"sec{i}": ((1 + h) ** 2 - 1) / h for i, h in enumerate(hs)})

# 右端点矩形之和 S_n = Σ (k/n)² · (1/n) = (n + 1)(2n + 1)/(6n²)，左端点 L_n = (n − 1)(2n − 1)/(6n²)
def right(n):
    return sum(Fraction(k, n) ** 2 for k in range(1, n + 1)) / n
def left(n):
    return sum(Fraction(k, n) ** 2 for k in range(0, n)) / n
for n in (4, 10, 100, 1000):
    R, L = right(n), left(n)
    assert R == Fraction((n + 1) * (2 * n + 1), 6 * n * n)
    out(**{f"R{n}": float(R), f"L{n}": float(L), f"gap{n}": float(R - L)})
out(R4_frac=str(right(4)), L4_frac=str(left(4)))

# 阿基米德：抛物线弓形面积等于内接三角形面积的 4/3。以 y = x² 与弦 y = 1（−1 ≤ x ≤ 1）为例：
# 弓形面积 = 2 − 2/3 = 4/3；内接三角形顶点 (−1, 1)、(1, 1)、(0, 0)，面积 1
tri = Fraction(1)
seg = Fraction(2) - 2 * Fraction(1, 3)
out(seg=float(seg), tri=float(tri), ratio=str(seg / tri))
# 他的“穷竭”：每一步新增的三角形面积是上一步的 1/4，总和 1 + 1/4 + 1/16 + … → 4/3
partial = [float(sum(Fraction(1, 4) ** k for k in range(m))) for m in (1, 2, 3, 5, 10)]
out(arch1=partial[0], arch2=partial[1], arch3=partial[2], arch5=partial[3], arch10=partial[4])
