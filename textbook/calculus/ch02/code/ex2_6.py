"""2.6 节：双曲函数——恒等式的数值核对；反双曲正弦的公式；悬链线与同跨度、同垂度的抛物线的比较；tanh 的饱和。"""
import math

import numpy as np

from bookout import out

x = np.linspace(-5, 5, 1001)
assert np.allclose(np.cosh(x) ** 2 - np.sinh(x) ** 2, 1)
assert np.allclose(np.arcsinh(x), np.log(x + np.sqrt(x * x + 1)))
out(c1=math.cosh(1), s1=math.sinh(1), t1=math.tanh(1), t3=math.tanh(3))

# 算例 2.6.2：两根立柱相距 2L = 20 m，电缆的悬链线参数 a = 25 m：y = a cosh(x/a)
L, a = 10.0, 25.0
sag = a * (math.cosh(L / a) - 1)                 # 垂度：两端比最低点高多少
length = 2 * a * math.sinh(L / a)                # 弧长（第 16 章证明）
# 同跨度、同垂度的抛物线 y = a + sag (x/L)²，两者最大相差多少
xs = np.linspace(-L, L, 20001)
cat = a * np.cosh(xs / a)
par = a + sag * (xs / L) ** 2
diff = np.abs(cat - par)
out(L=L, a=a, sag=sag, length=length, extra_mm=(length - 2 * L) * 1000, dmax_mm=float(diff.max()) * 1000,
    dmax_at=float(abs(xs[diff.argmax()])))
# 垂度更大时（a = 5 m），差别变大
a2 = 5.0
sag2 = a2 * (math.cosh(L / a2) - 1)
d2 = np.abs(a2 * np.cosh(xs / a2) - (a2 + sag2 * (xs / L) ** 2)).max()
out(a2=a2, sag2=sag2, dmax2=float(d2))

# tanh 的饱和：x 很小时 tanh x ≈ x，|x| > 3 时与 ±1 相差不到 1%
out(th01=math.tanh(0.1), sat3=1 - math.tanh(3))
