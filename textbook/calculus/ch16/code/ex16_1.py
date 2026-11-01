"""16.1 节：平面图形的面积——割草机器人的草坪：沿长边每隔 2 m 量一次上、下边界，用梯形公式与辛普森公式求面积，
估计割草时间；两条曲线所围的面积；按 y 积分；扇形面积 θ/2；摆线一拱下的面积 3πr²。"""
import math

from scipy import integrate

from _quad import simpson, trap
from bookout import out

# 草坪：0 ≤ x ≤ 20 m，上边界 top(x)、下边界 bot(x)
top = lambda x: 12 + 2 * math.sin(math.pi * x / 20) + 0.8 * math.sin(3 * math.pi * x / 20)
bot = lambda x: 1.5 * math.sin(math.pi * x / 10) ** 2 + 0.05 * x
w = lambda x: top(x) - bot(x)
A_ex = integrate.quad(w, 0, 20)[0]
A_t, A_s = trap(w, 0, 20, 10), simpson(w, 0, 20, 10)
out(lawn_tab="\n".join(f"| {2 * k} | {top(2 * k):.2f} | {bot(2 * k):.2f} | {w(2 * k):.2f} |" for k in range(11)),
    A_ex=A_ex, A_t=A_t, A_s=A_s, A_t_err=(A_ex - A_t) / A_ex * 100, A_s_err=(A_s - A_ex) / A_ex * 100)
# 割草时间：刀盘宽 0.25 m，速度 0.4 m/s，重叠与掉头按多走 15% 计
cut, v = 0.25, 0.4
out(mow_min=A_ex / (cut * v) * 1.15 / 60)
# 算例：y = x 与 y = x² 之间；x = y² 与 x = y + 2 之间
out(a_xx2=integrate.quad(lambda x: x - x * x, 0, 1)[0], a_y=integrate.quad(lambda y: (y + 2) - y * y, -1, 2)[0])
# 扇形面积：圆心角 θ = 1 rad 的单位圆扇形 = 三角形 O、(cos θ, 0)、B 加上曲线 √(1 − x²) 在 [cos θ, 1] 下方的面积，应为 θ/2
th = 1.0
c = math.cos(th)
sector = 0.5 * c * math.sin(th) + integrate.quad(lambda x: math.sqrt(1 - x * x), c, 1)[0]
out(sector=sector)
# 摆线一拱下的面积：x = r(t − sin t)，y = r(1 − cos t)，∫ y dx = ∫ y x'(t) dt
r = 0.075
cyc = integrate.quad(lambda t: r * (1 - math.cos(t)) * r * (1 - math.cos(t)), 0, 2 * math.pi)[0]
out(r=r, cyc=cyc, cyc_ex=3 * math.pi * r * r, cyc_ratio=cyc / (math.pi * r * r))
