"""7.6 节：反正弦的导数；肘关节随“肩—腕心距离”变化的速度（隐函数求导）；x^x 的导数。"""
import math

from scipy.optimize import brentq

from _traj import ur5e_links
from bookout import out

# 反函数：arcsin 在 0.5 处的导数 1/√(1 − 0.25)，与差商比较
h = 1e-6
out(asin_d=1 / math.sqrt(1 - 0.25), asin_q=(math.asin(0.5 + h) - math.asin(0.5 - h)) / (2 * h))

# 算例 7.6.2：r² = l1² + l2² + 2 l1 l2 cos θ2（θ2 为肘关节相对转角，伸直时为 0）
l1, l2 = ur5e_links()
r, rdot = 0.6, 0.1                       # m, m/s
c = (r**2 - l1**2 - l2**2) / (2 * l1 * l2)
th2 = math.acos(c)
th2dot = -r * rdot / (l1 * l2 * math.sin(th2))
# 数值核对：θ2(r) 的中心差商乘 ṙ
f = lambda rr: math.acos((rr**2 - l1**2 - l2**2) / (2 * l1 * l2))
num = (f(r + 1e-6) - f(r - 1e-6)) / 2e-6 * rdot
assert abs(num - th2dot) < 1e-7
# 肘关节角速度达到限速 180°/s（π rad/s）时的 r
g = lambda rr: rr * rdot / (l1 * l2 * math.sin(f(rr))) - math.pi
r_lim = brentq(g, 0.7, l1 + l2 - 1e-9)
table = []
for rr in (0.3, 0.5, 0.7, 0.8, 0.81, 0.815):
    table.append((rr, math.degrees(f(rr)), math.degrees(rr * rdot / (l1 * l2 * math.sin(f(rr))))))
out(c=c, th2=th2, th2_deg=math.degrees(th2), th2dot=th2dot, th2dot_deg=math.degrees(th2dot), reach=l1 + l2,
    r_lim=r_lim, gap_mm=(l1 + l2 - r_lim) * 1000,
    table="\n".join(f"| {rr:.3f} | {a:.2f} | {b:.2f} |" for rr, a, b in table))

# 算例 7.6.4：y = x^x，y' = x^x (ln x + 1)，x = 2 处
out(xx_d=4 * (math.log(2) + 1), xx_q=((2 + h) ** (2 + h) - (2 - h) ** (2 - h)) / (2 * h))

# 7.6.7 节：气球半径 r = 10 cm 时，dr/dV = 1/(4πr²)；再吹进 1000 cm³，半径约增加多少
rb = 10.0
out(balloon_rate=1 / (4 * math.pi * rb**2), balloon_dr=1000 / (4 * math.pi * rb**2))
