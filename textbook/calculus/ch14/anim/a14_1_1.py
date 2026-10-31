"""动画 14.1.1（配图 14.1.1）：分部积分的几何意义——参数曲线 (u(s), v(s)) 下方的面积 ∫v du 与左方的面积 ∫u dv
随曲线一起长出来，两块合起来正好是大矩形 u₁v₁ 去掉小矩形 u₀v₀。"""
from manim import *
from wq_anim import *
import numpy as np

U = lambda s: 1 + 2 * s
V = lambda s: 0.6 + 1.6 * s * s


class Lesson(Base):
    def construct(self):
        self.title("14.1", "分部积分", "Integration by parts")
        ax = Axes(x_range=[0, 3.4, 1], y_range=[0, 2.6, 1], x_length=7, y_length=5, tips=False,
                  axis_config={"color": GREY_B}).shift(LEFT * 1.6 + DOWN * 0.3)
        lu = MathTex("u", font_size=34).next_to(ax.x_axis, RIGHT)
        lv = MathTex("v", font_size=34).next_to(ax.y_axis, UP)
        self.play(Create(ax), Write(lu), Write(lv))
        s = ValueTracker(0.01)
        curve = always_redraw(lambda: ParametricFunction(lambda q: ax.c2p(U(q), V(q)), t_range=[0, s.get_value()], color=WHITE, stroke_width=4))

        def below():
            q = np.linspace(0, s.get_value(), 60)
            pts = [ax.c2p(U(a), 0) for a in q] + [ax.c2p(U(a), V(a)) for a in q[::-1]]
            return Polygon(*pts, color=STEEL, fill_opacity=0.45, stroke_width=0)

        def left():
            q = np.linspace(0, s.get_value(), 60)
            pts = [ax.c2p(0, V(a)) for a in q] + [ax.c2p(U(a), V(a)) for a in q[::-1]]
            return Polygon(*pts, color=RED, fill_opacity=0.4, stroke_width=0)

        b = always_redraw(below)
        l = always_redraw(left)
        self.add(b, l, curve)
        small = Rectangle(width=ax.c2p(U(0), 0)[0] - ax.c2p(0, 0)[0], height=ax.c2p(0, V(0))[1] - ax.c2p(0, 0)[1],
                          color=YELLOW, stroke_width=3).move_to(ax.c2p(U(0) / 2, V(0) / 2))
        self.play(Create(small))
        self.caption("曲线从 (u₀, v₀) 出发；黄框是小矩形 u₀v₀", "The curve starts at (u₀, v₀); the yellow box is u₀v₀", wait=0.3)
        self.play(s.animate.set_value(1.0), run_time=5, rate_func=linear)
        big = Rectangle(width=ax.c2p(U(1), 0)[0] - ax.c2p(0, 0)[0], height=ax.c2p(0, V(1))[1] - ax.c2p(0, 0)[1],
                        color=ORANGE, stroke_width=3).move_to(ax.c2p(U(1) / 2, V(1) / 2))
        self.play(Create(big))
        tb = MathTex(r"\int v\,du", font_size=40, color=STEEL).move_to(ax.c2p(2.2, 0.6))
        tl = MathTex(r"\int u\,dv", font_size=40, color=RED).move_to(ax.c2p(0.7, 1.6))
        self.play(Write(tb), Write(tl))
        eq = MathTex(r"\int u\,dv+\int v\,du", r"=", r"u_1v_1-u_0v_0", font_size=38).to_edge(RIGHT, buff=0.4).shift(UP * 1.2)
        eq[0].set_color(WHITE)
        eq[2].set_color(ORANGE)
        self.play(Write(eq))
        self.caption("蓝、红两块合起来 = 大矩形去掉小矩形", "Blue plus red = big rectangle minus small one", wait=0.8)
        eq2 = MathTex(r"\int u\,dv=uv\Big|-\int v\,du", font_size=40, color=YELLOW).next_to(eq, DOWN, buff=0.6)
        self.play(Write(eq2))
        self.caption("一块面积难求时，换成求另一块", "If one area is hard, compute the other", wait=1.0)
        self.play(*[FadeOut(m) for m in (ax, lu, lv, b, l, curve, small, big, tb, tl, eq, eq2)])
        self.card([["分部积分", "Integration by parts"],
                   MathTex(r"\int u\,dv=uv-\int v\,du", font_size=48),
                   ["乘积法则 (uv)′ = u′v + uv′ 的逆运算", "The product rule (uv)′ = u′v + uv′, read backwards"]])
