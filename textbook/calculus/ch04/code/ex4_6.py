"""4.6 节：无穷小的比较——等价无穷小的相对误差；等价代换用错的例子；关节重力矩的小角度线性化。"""
import math

from bookout import out

x = 0.1
pairs = {"sin": (math.sin(x), x), "tan": (math.tan(x), x), "cos": (1 - math.cos(x), x * x / 2), "ln": (math.log1p(x), x),
         "exp": (math.expm1(x), x), "sqrt": (math.sqrt(1 + x) - 1, x / 2), "asin": (math.asin(x), x), "atan": (math.atan(x), x)}
for k, (a, b) in pairs.items():
    out(**{f"re_{k}": abs(a - b) / abs(a)})

# (tan x − sin x)/x³：正确的极限 1/2；若把 tan x、sin x 都换成 x，会得到 0
for xv in (0.1, 0.01, 0.001):
    out(**{f"ts_{str(xv).replace('.', '_')}": (math.tan(xv) - math.sin(xv)) / xv**3})

# 关节重力矩 τ = m g l sin θ（θ 从竖直向下量起），线性化 τ ≈ m g l θ 的相对误差
for deg in (5, 10, 20, 30):
    t = math.radians(deg)
    out(**{f"lin_{deg}": (t - math.sin(t)) / math.sin(t)})
# 相对误差 1% 的角度：θ/sin θ − 1 = 0.01，二分法
lo, hi = 0.01, 1.0
for _ in range(60):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if m / math.sin(m) - 1 < 0.01 else (lo, m)
out(deg1pct=math.degrees(lo), est1pct=math.degrees(math.sqrt(0.06)))
