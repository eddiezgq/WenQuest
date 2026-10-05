"""动画 8.3.1（配图 8.3.1）：同一个弹簧振子，三种算法在相平面上分道扬镳。状态为 (x, v/ω)，精确解是单位圆。
步长取 ωh = 0.3：欧拉法每步半径乘以 √(1 + 0.09)，向外盘旋；半隐式欧拉法沿一个略斜的闭合椭圆；RK4 几乎与圆重合。"""
from manim import *
from wq_anim import *
import numpy as np

Z = 0.3                                # ωh
N = 63                                 # 约 3 个周期
S = 1.15                               # 画面单位 / 状态单位
CEN = [np.array([-4.4, -0.7, 0]), np.array([0.0, -0.7, 0]), np.array([4.4, -0.7, 0])]


def paths():
    out = []
    x, u = 1.0, 0.0; p = [(x, u)]
    for _ in range(N):
        x, u = x + Z * u, u - Z * x; p.append((x, u))
    out.append(p)
    x, u = 1.0, 0.0; p = [(x, u)]
    for _ in range(N):
        u = u - Z * x; x = x + Z * u; p.append((x, u))
    out.append(p)
    x, u = 1.0, 0.0; p = [(x, u)]
    F = lambda a: np.array([a[1], -a[0]])
    for _ in range(N):
        a = np.array([x, u]); k1 = F(a); k2 = F(a + Z / 2 * k1); k3 = F(a + Z / 2 * k2); k4 = F(a + Z * k3)
        a = a + Z / 6 * (k1 + 2 * k2 + 2 * k3 + k4); x, u = a; p.append((x, u))
    out.append(p)
    return out


class Lesson(Base):
    def construct(self):
        self.title("8.3", "三种算法，同一个振子", "Three integrators, one oscillator")
        names = [["欧拉法", "Euler"], ["半隐式欧拉法", "semi-implicit Euler"], ["RK4", "RK4"]]
        cols = [RED, BLUE, GREEN]
        frames = VGroup()
        for c, nm in zip(CEN, names):
            frames.add(Circle(radius=S, color=GREY_B, stroke_opacity=0.8).move_to(c).set_stroke(width=2))
            frames.add(Line(c + LEFT * 1.9, c + RIGHT * 1.9, color=GREY_D, stroke_width=1), Line(c + DOWN * 1.9, c + UP * 1.9, color=GREY_D, stroke_width=1))
            frames.add(bi(nm, size=24).move_to(c + UP * 2.35))
        frames.add(bi(["（欧拉法盘旋出画面后不再画出）", "(Euler is not drawn once it leaves the frame)"], size=18).move_to(CEN[0] + DOWN * 1.8))
        self.play(FadeIn(frames))
        self.caption("相平面：横轴 x，纵轴 v/ω；精确解沿灰色的圆周而复始", "Phase plane: x across, v/ω up; the exact motion goes round the grey circle", wait=0.5)
        P = paths()
        k = ValueTracker(0)
        def trail(i):
            def make():
                n = int(k.get_value())
                pts = [CEN[i] + S * np.array([a, b, 0]) for a, b in P[i][:n + 1] if a * a + b * b < 2.6]   # 跑出画面的部分不画
                if len(pts) < 2:
                    return VGroup(Dot(pts[0], color=cols[i], radius=0.06))
                return VGroup(VMobject(stroke_color=cols[i], stroke_width=3).set_points_as_corners(pts), Dot(pts[-1], color=cols[i], radius=0.07))
            return always_redraw(make)
        self.add(trail(0), trail(1), trail(2))
        self.caption("每步 ωh = 0.3，三种方法同时出发", "Each step has ωh = 0.3; all three start together", wait=0)
        self.play(k.animate.set_value(N), run_time=9, rate_func=linear)
        self.caption("欧拉法向外盘旋，能量越算越大；半隐式欧拉法沿闭合的斜椭圆；RK4 几乎与圆重合", "Euler spirals out, gaining energy; semi-implicit Euler stays on a closed tilted ellipse; RK4 sits on the circle", wait=2.5)
        self.card([["长时间仿真选什么方法", "Choosing a method for long runs"],
                   ["欧拉法：每步能量乘以 1 + (ωh)²，总会“爆掉”", "Euler: energy times 1 + (ωh)² each step; it always blows up"],
                   ["半隐式欧拉法：计算量一样，能量不漂移", "Semi-implicit Euler: same cost, no energy drift"],
                   ["RK4：每步算四次，精度高得多", "RK4: four evaluations per step, far more accurate"]])
