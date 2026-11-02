"""动画 13.4.1（配图 13.4.1）：陀螺进动。自行车轮 2.0 kg、J = 0.15 kg·m²，以 5.0 r/s 自转，轮轴一端用绳吊起，轮心离吊点 0.20 m
（与算例 13.4.1 一致）。左：侧视，重力对吊点的力矩水平；右：俯视，力矩 M 始终垂直于角动量 L，只改变 L 的方向，L 的尖端画圆，
进动角速度 Ω = mgl/(Jω) = 0.83 rad/s，一圈 7.5 s，按真实时间播放一圈。章动略去（见图 13.4.1）。"""
from manim import *
from wq_anim import *
import numpy as np

OM = 2.0 * 9.81 * 0.20 / (0.15 * 2 * np.pi * 5.0)
TP = 2 * np.pi / OM
P = np.array([3.2, 0.4, 0])                                   # 俯视图的吊点
LL = 1.5                                                         # 俯视图中 L 箭头的长度


class Lesson(Base):
    def construct(self):
        self.title("13.4", "陀螺进动", "Precession of a gyroscope")
        # ---- 左：侧视
        q = np.array([-4.2, 1.6, 0])
        rope = Line(q + UP * 1.2, q, color=GREY_B, stroke_width=3)
        axle = Line(q, q + RIGHT * 2.0, color=GREY_B, stroke_width=5)
        wheel = Ellipse(width=0.5, height=2.2, color=BLUE, stroke_width=5).move_to(q + RIGHT * 2.0)
        mg = Arrow(q + RIGHT * 2.0, q + RIGHT * 2.0 + DOWN * 1.5, buff=0, color=RED, stroke_width=5)
        Lside = Arrow(q + RIGHT * 2.0, q + RIGHT * 3.4, buff=0, color=YELLOW, stroke_width=5)
        lab = VGroup(MathTex(r"m\vec g", font_size=32, color=RED).next_to(mg, LEFT, buff=0.1),
                     MathTex(r"\vec L", font_size=34, color=YELLOW).next_to(Lside, UP, buff=0.1),
                     MathTex(r"l", font_size=30).next_to(axle, DOWN, buff=0.1))
        side = VGroup(rope, axle, wheel, mg, Lside, lab, Dot(q, color=WHITE))
        sl = bi(["侧视", "side view"], size=20).next_to(side, DOWN, buff=0.5)
        self.play(FadeIn(side), FadeIn(sl))
        self.caption("轮子高速自转，只吊住轮轴的一端：重力对吊点有力矩，轮子却不掉下来", "The wheel spins fast and hangs by one end of its axle: gravity has a torque about the pivot, yet it does not fall", wait=1.5)
        # ---- 右：俯视
        t = ValueTracker(0.0)
        ring = Circle(radius=LL, color=GREY_D, stroke_width=1.5).move_to(P)

        def top():
            ph = OM * t.get_value(); u = np.array([np.cos(ph), np.sin(ph), 0]); n = np.array([-np.sin(ph), np.cos(ph), 0])
            La = Arrow(P, P + u * LL, buff=0, color=YELLOW, stroke_width=6)
            Ma = Arrow(P + u * LL, P + u * LL + n * 0.8, buff=0, color=RED, stroke_width=5)
            ml = MathTex(r"\vec M", font_size=32, color=RED).move_to(P + u * LL + n * 1.05)
            ll = MathTex(r"\vec L", font_size=32, color=YELLOW).move_to(P + u * (LL * 0.55) - n * 0.3)
            return VGroup(La, Ma, ml, ll, Dot(P, color=WHITE))

        tl = bi(["俯视", "top view"], size=20).move_to(P + DOWN * (LL + 0.4))
        self.play(FadeIn(ring), FadeIn(tl))
        self.add(always_redraw(top))
        clock = always_redraw(lambda: MathTex(rf"t = {t.get_value():.1f}\ \mathrm s", font_size=30).move_to(P + UP * (LL + 0.35) + RIGHT * 1.8))
        self.add(clock)
        self.caption("力矩 M 水平，始终垂直于 L：它不改变 L 的大小，只让 L 的方向在水平面内转", "The torque M is horizontal and always perpendicular to L: it turns L round without changing its size", wait=0)
        self.play(t.animate.set_value(TP / 2), run_time=TP / 2, rate_func=linear)
        self.caption("dL = M dt：L 的尖端画圆，进动一圈约 7.5 s", "dL = M dt: the tip of L traces a circle, one turn in about 7.5 s", wait=0)
        self.play(t.animate.set_value(TP), run_time=TP / 2, rate_func=linear)
        self.card([["进动", "Precession"],
                   MathTex(r"\Omega = \frac{M}{L} = \frac{mgl}{J\omega}", font_size=46),
                   ["自转越快，进动越慢", "the faster the spin, the slower the precession"],
                   ["力矩改变的是角动量的方向", "the torque changes the direction of L"]])
