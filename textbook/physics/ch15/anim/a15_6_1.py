"""动画 15.6.1（配图 15.6.1）：潮汐为什么一天两次。俯视图：月球在右方，潮汐加速度在朝向和背向月球的两侧把海水拉出两个隆起（夸大画出）。
地球自转，岸边的一点（黄点）一天之内两次经过隆起，水位两涨两落；右下随时间画出它的水位。
月球同时在公转，所以相邻两次高潮相隔约 12 h 25 min，这里只示意，不计月球的公转。"""
from manim import *
from wq_anim import *
import numpy as np

C = np.array([-2.6, 0.1, 0])
RE, EPS = 1.6, 0.22


def h(phi):                                                      # 相对水位：∝ (3cos²φ − 1)/2，φ 为与月球方向的夹角
    return (3 * np.cos(phi) ** 2 - 1) / 2


class Lesson(Base):
    def construct(self):
        self.title("15.6", "潮汐为什么一天两次", "Why there are two tides a day")
        earth = Circle(radius=RE, color=BLUE_E, fill_opacity=0.5, stroke_width=2).move_to(C)
        ocean = ParametricFunction(lambda t: C + (RE + 0.15 + EPS * h(t)) * np.array([np.cos(t), np.sin(t), 0]), t_range=[0, 2 * np.pi], color=BLUE, stroke_width=3)
        moon = Circle(radius=0.3, color=GREY_B, fill_opacity=0.8).move_to(C + RIGHT * 5.2)
        ml = bi(["月球", "Moon"], size=18).next_to(moon, DOWN, buff=0.15)
        arrows = VGroup(*[Arrow(C + RE * np.array([np.cos(t), np.sin(t), 0]), C + RE * np.array([np.cos(t), np.sin(t), 0]) + 0.45 * np.array([2 * np.cos(t), -np.sin(t), 0]),
                                buff=0, color=RED, stroke_width=3, max_tip_length_to_length_ratio=0.3) for t in np.linspace(0, 2 * np.pi, 12, endpoint=False)])
        self.play(FadeIn(earth), FadeIn(moon), FadeIn(ml))
        self.caption("月球对地球各处的引力，减去对地心的引力，就是潮汐加速度：朝月一侧向外，背月一侧也向外", "The Moon's pull at each point minus its pull at the centre: outward on the near side, and outward on the far side too", wait=0)
        self.play(GrowFromCenter(arrows), run_time=1.5); self.wait(1.5)
        self.caption("海水被拉成两个隆起（夸大画出）", "The ocean is pulled into two bulges (exaggerated)", wait=0)
        self.play(Create(ocean), FadeOut(arrows), run_time=1.5)
        t = ValueTracker(0.0)                                    # 小时
        city = always_redraw(lambda: Dot(C + (RE + 0.15 + EPS * h(2 * np.pi * t.get_value() / 24)) * np.array([np.cos(2 * np.pi * t.get_value() / 24), np.sin(2 * np.pi * t.get_value() / 24), 0]),
                                         radius=0.1, color=YELLOW))
        ax = Axes(x_range=[0, 24, 6], y_range=[-0.6, 1.1, 0.5], x_length=4.0, y_length=1.3, tips=False,
                  axis_config=dict(include_numbers=False, color=GREY_B)).move_to(np.array([3.8, -1.65, 0]))
        axl = VGroup(MathTex(r"t", font_size=26).next_to(ax.x_axis, RIGHT, buff=0.1),
                     bi(["水位", "water level"], size=16).next_to(ax.y_axis, UP, buff=0.1),
                     MathTex(r"24\ \mathrm h", font_size=22).next_to(ax.c2p(24, -0.6), DOWN, buff=0.1))
        trace = always_redraw(lambda: ax.plot(lambda x: h(2 * np.pi * x / 24), x_range=[0, max(t.get_value(), 0.01)], color=YELLOW, stroke_width=3))
        self.play(FadeIn(ax), FadeIn(axl)); self.add(city, trace)
        self.caption("地球自转一周，岸边的一点两次经过隆起：两涨两落", "In one turn of the Earth a point on the coast passes both bulges: two highs, two lows", wait=0)
        self.play(t.animate.set_value(24), run_time=8, rate_func=linear)
        self.wait(1.0)
        self.card([["潮汐", "Tides"],
                   MathTex(r"a_\mathrm{tide} \approx \frac{2GMR}{d^3}", font_size=46),
                   ["与距离的三次方成反比：月球的潮汐作用是太阳的两倍多", "falls off as 1/d³: the Moon's effect is more than twice the Sun's"],
                   ["月球同时在公转，相邻两次高潮相隔约 12 小时 25 分", "the Moon also moves on, so high tides come about 12 h 25 min apart"]])
