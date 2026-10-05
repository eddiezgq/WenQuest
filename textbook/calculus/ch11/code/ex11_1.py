"""11.1 节：最优化建模——减速比的选择：电机转子惯量 J_m、负载惯量 J_L，减速比 n 时负载的角加速度 α = nτ/(n²J_m + J_L)，
最佳 n* = √(J_L/J_m)（惯量匹配）；相机离工件多远时视角最大：θ(x) = arctan(b/x) − arctan(a/x)，x* = √(ab)。"""
import math

from bookout import out

# 减速比（数值为教学用的假设值，量级与协作机器人关节相近）
Jm, JL, tau = 1.2e-4, 0.30, 0.8          # kg·m²，kg·m²，N·m（电机额定力矩）
alpha = lambda n: n * tau / (n * n * Jm + JL)
n_star = math.sqrt(JL / Jm)
out(Jm=Jm, JL=JL, tau=tau, n_star=n_star, a_star=alpha(n_star), a_star_deg=math.degrees(alpha(n_star)))
rows = []
for n in (10, 25, 50, 100, 200):
    rows.append(f"| {n} | {alpha(n):.3f} | {alpha(n) / alpha(n_star):.3f} |")
out(gear_tab="\n".join(rows))

# 相机视角：工件上沿、下沿高出相机光轴 a、b（a < b），相机沿水平方向移动
a, b = 0.30, 0.50
th = lambda x: math.atan(b / x) - math.atan(a / x)
xs = math.sqrt(a * b)
out(cam_a=a, cam_b=b, cam_x=xs, cam_deg=math.degrees(th(xs)), cam_deg_1=math.degrees(th(1.0)), cam_deg_02=math.degrees(th(0.2)))
