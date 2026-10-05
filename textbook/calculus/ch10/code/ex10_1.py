"""10.1 节：单调性——关节阶跃响应的单调区间（ζ = 0.6 有超调，ζ = 1 单调上升）；
腕心距离 r(θ₂) 在 [0, π] 上严格递减，所以给定距离时肘关节角唯一（逆运动学的唯一性）；(1 + 1/x)^x 递增。"""
import math

from _traj import ur5e_links
from bookout import out

wn = 10.0
z = 0.6
wd = wn * math.sqrt(1 - z * z)
# q′(t) = (ωₙ²/ω_d) e^{−ζωₙt} sin ω_d t：在 kπ/ω_d 处变号
out(z=z, wn=wn, wd=wd, t1=math.pi / wd, t2=2 * math.pi / wd)
q = lambda t: 1 - math.exp(-z * wn * t) * (math.cos(wd * t) + z / math.sqrt(1 - z * z) * math.sin(wd * t))
out(q_t1=q(math.pi / wd), q_t2=q(2 * math.pi / wd))

# 逆运动学：r(θ₂) = √(l₁² + l₂² + 2l₁l₂cos θ₂)，求 r = 0.6 m 的 θ₂
l1, l2 = ur5e_links()
r = lambda t: math.sqrt(l1 * l1 + l2 * l2 + 2 * l1 * l2 * math.cos(t))
target = 0.6
lo, hi = 0.0, math.pi
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if r(mid) > target else (lo, mid)
th = (lo + hi) / 2
out(r_min=r(math.pi), r_max=r(0), target=target, th_deg=math.degrees(th),
    th_formula=math.degrees(math.acos((target ** 2 - l1 * l1 - l2 * l2) / (2 * l1 * l2))))

# (1 + 1/x)^x
rows = []
for x in (1, 2, 5, 10, 100, 1000):
    rows.append(f"| {x} | {math.exp(x * math.log1p(1 / x)):.8f} |")
out(ex_tab="\n".join(rows))
