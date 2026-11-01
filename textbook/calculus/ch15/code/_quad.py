"""第 15 章共用：几种数值积分公式。以下划线开头，构建时不单独运行。"""
import math


def trap(f, a, b, n):
    h = (b - a) / n
    return h * (0.5 * f(a) + sum(f(a + k * h) for k in range(1, n)) + 0.5 * f(b))


def simpson(f, a, b, n):
    """复合辛普森公式，n 为偶数（小区间个数）。"""
    if n % 2:
        n += 1
    h = (b - a) / n
    s = f(a) + f(b) + 4 * sum(f(a + (2 * k - 1) * h) for k in range(1, n // 2 + 1)) + 2 * sum(f(a + 2 * k * h) for k in range(1, n // 2))
    return s * h / 3


def gauss_nodes(n):
    """n 点高斯–勒让德求积的节点与权（牛顿迭代求勒让德多项式的根）。"""
    xs, ws = [], []
    for i in range(1, n + 1):
        x = math.cos(math.pi * (i - 0.25) / (n + 0.5))
        for _ in range(100):
            p0, p1 = 1.0, x
            for k in range(2, n + 1):
                p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
            dp = n * (x * p1 - p0) / (x * x - 1)
            dx = p1 / dp
            x -= dx
            if abs(dx) < 1e-15:
                break
        xs.append(x)
        ws.append(2 / ((1 - x * x) * dp * dp))
    return xs, ws


def gauss(f, a, b, n):
    xs, ws = gauss_nodes(n)
    c, d = (a + b) / 2, (b - a) / 2
    return d * sum(w * f(c + d * x) for x, w in zip(xs, ws))


def romberg(f, a, b, levels):
    """龙贝格表：R[k][0] 为 2^k 段的梯形公式，逐列做理查森外推。返回整张表与函数求值次数。"""
    R = [[trap(f, a, b, 1)]]
    for k in range(1, levels):
        R.append([trap(f, a, b, 2 ** k)])
        for j in range(1, k + 1):
            R[k].append(R[k][j - 1] + (R[k][j - 1] - R[k - 1][j - 1]) / (4 ** j - 1))
    return R


def adaptive_simpson(f, a, b, tol, depth=50):
    """自适应辛普森：比较一段上的辛普森值与对分后两半之和，差太大就继续对分。返回 (积分, 求值点列表)。"""
    pts = []

    def F(x):
        pts.append(x)
        return f(x)

    def simp(a, fa, b, fb):
        m = (a + b) / 2
        fm = F(m)
        return m, fm, (b - a) / 6 * (fa + 4 * fm + fb)

    def rec(a, fa, b, fb, m, fm, whole, tol, d):
        lm, flm, left = simp(a, fa, m, fm)
        rm, frm, right = simp(m, fm, b, fb)
        if d <= 0 or abs(left + right - whole) <= 15 * tol:
            return left + right + (left + right - whole) / 15
        return rec(a, fa, m, fm, lm, flm, left, tol / 2, d - 1) + rec(m, fm, b, fb, rm, frm, right, tol / 2, d - 1)

    fa, fb = F(a), F(b)
    m, fm, whole = simp(a, fa, b, fb)
    return rec(a, fa, b, fb, m, fm, whole, tol, depth), pts
