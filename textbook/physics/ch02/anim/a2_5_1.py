"""动画 2.5.1（配图 2.5.1）：叉积。A 固定，B 绕起点转一圈；平行四边形的面积等于 |A × B| = AB sin θ。
右侧的竖直箭头表示 A × B（画面朝外为上），θ 在 0°～180° 时朝外，180°～360° 时（从 A 逆时针量超过 180°，
即 B 转到 A 的另一侧）朝里；下方的曲线是 (A × B)_z 随 θ 的变化，正是正弦曲线。"""
from manim import *
from wq_anim import *
import numpy as np

O = np.array([-4.2, 0.4, 0])
A = np.array([2.6, 0, 0])
Bl = 1.8


class Lesson(Base):
    def construct(self):
        self.title("2.5", "叉积：有方向的面积", "The cross product: an area with a direction")
        th = ValueTracker(30.0)
        a = vec(O, O + A, BLUE, r"\boldsymbol A", DOWN)

        def Bv():
            t = np.radians(th.get_value())
            return O + Bl * np.array([np.cos(t), np.sin(t), 0])

        b = always_redraw(lambda: Arrow(O, Bv(), buff=0, color=GREEN, stroke_width=5, max_tip_length_to_length_ratio=0.2))
        bl = always_redraw(lambda: MathTex(r"\boldsymbol B", color=GREEN, font_size=34).next_to(Bv(), UP, buff=0.1))
        par = always_redraw(lambda: Polygon(O, O + A, O + A + (Bv() - O), Bv(),
                                            color=YELLOW if np.sin(np.radians(th.get_value())) >= 0 else RED,
                                            fill_opacity=0.25, stroke_width=1))
        self.play(GrowArrow(a[0]), FadeIn(a[1]))
        self.add(par, b, bl)
        base = np.array([2.2, 0.4, 0])

        def zarrow():
            s = np.sin(np.radians(th.get_value()))
            g = VGroup(Line(base + LEFT * 0.5, base + RIGHT * 0.5, color=GREY_B))
            if abs(s) > 0.02:
                g.add(Arrow(base, base + UP * 2.0 * s, buff=0, color=RED, stroke_width=7, max_tip_length_to_length_ratio=0.25))
            g.add(MathTex(r"\boldsymbol A\times\boldsymbol B", font_size=30, color=RED).next_to(base, RIGHT, buff=0.6).shift(UP * 1.6))
            g.add(zh("朝外" if s > 0.02 else ("朝里" if s < -0.02 else "零"), 24, RED).next_to(base, RIGHT, buff=0.6).shift(UP * 0.9))
            return g

        za = always_redraw(zarrow)
        ax = Axes(x_range=[0, 360, 90], y_range=[-1.1, 1.1, 1], x_length=5.0, y_length=1.6, tips=False,
                  axis_config={"color": GREY_B, "font_size": 20}).move_to(np.array([3.6, -2.0, 0]))
        lab = MathTex(r"(\boldsymbol A\times\boldsymbol B)_z \propto \sin\theta", font_size=26).next_to(ax, UP, buff=0.05)
        trace = always_redraw(lambda: ax.plot(lambda x: np.sin(np.radians(x)), x_range=[0, max(0.5, th.get_value() % 360.0001)],
                                              color=RED) if th.get_value() > 0.5 else VGroup())
        self.play(FadeIn(za), Create(ax), FadeIn(lab))
        self.caption("面积 = AB sin θ；拇指方向（右手定则）是 A × B 的方向", "Area = AB sin θ; the right-hand thumb gives the direction of A × B", wait=0)
        th.set_value(0.0)
        self.add(trace)
        self.play(th.animate.set_value(90), run_time=2.5, rate_func=linear)
        self.caption("垂直时面积最大", "Largest when perpendicular", wait=0.8)
        self.play(th.animate.set_value(180), run_time=2.5, rate_func=linear)
        self.caption("平行时面积为零，叉积为零", "Parallel: zero area, zero cross product", wait=0.8)
        self.play(th.animate.set_value(359), run_time=4, rate_func=linear)
        self.caption("B 转到 A 的另一侧，A × B 朝里：B × A = −A × B", "With B on the other side of A, A × B points in: B × A = −A × B")
        self.card([["叉积", "The cross product"],
                   ["大小：平行四边形的面积 AB sin θ", "Size: the parallelogram area AB sin θ"],
                   ["方向：垂直于 A、B，按右手定则；交换次序就反向", "Direction: perpendicular to A and B by the right-hand rule; swapping the order reverses it"]])
