"""A hand-written example of what the animator writes: lesson 2.1 (AGV emergency stop), in the
chapter-1 benchmark style. It is shown to the AI animator as the pattern to follow, and used as
the offline (no model) animation."""

AGV_2_1 = r'''
from wq_anim import *


class Lesson(Base):
    def construct(self):
        self.title("2.1", "惯性：运动不需要力来维持", "Inertia: motion needs no force to keep going")

        # 1. Galileo's ideal incline: the flatter the second slope, the farther the ball rolls
        h = 1.6
        A = np.array([-5.6, -0.4 + h, 0])
        B = np.array([-3.0, -0.4, 0])
        down = Line(A, B, color=GREY_B, stroke_width=4)
        self.play(Create(down))
        self.caption("伽利略的理想斜面：斜面越平，小球滚得越远",
                     "Galileo's ideal incline: the flatter the slope, the farther the ball rolls", wait=0.3)
        colors = ["#ff7b72", "#ffd33d", "#56d364"]
        for k, ang in enumerate([40, 22, 12]):
            run = h / np.tan(np.radians(ang))
            C = B + np.array([run, h, 0])
            up = Line(B, C, color=colors[k], stroke_width=4)
            ball = Dot(A, radius=0.13, color=colors[k])
            path = VMobject().set_points_as_corners([A, B, C])
            self.play(Create(up), run_time=0.5)
            self.play(MoveAlongPath(ball, path), run_time=1.6, rate_func=smooth)
            mark = DashedLine(C + LEFT * 0.4, C + RIGHT * 0.4, color=colors[k])
            self.add(mark)
        flat = Line(B, B + RIGHT * 9, color=BLUE, stroke_width=4)
        ball = Dot(A, radius=0.13, color=BLUE)
        self.play(Create(flat), run_time=0.5)
        self.caption("没有摩擦时，小球会一直滚下去", "Without friction the ball would roll forever", wait=0)
        self.play(MoveAlongPath(ball, Line(A, B)), run_time=0.8, rate_func=rate_functions.ease_in_quad)
        self.play(ball.animate.move_to(B + RIGHT * 9), run_time=2.2, rate_func=linear)
        self.clear_stage()

        # 2. The AGV brakes: seen from the ground (top) and from the AGV (bottom)
        s = 3.0                       # scene units per metre (ground view)
        v0, a, ak = 1.5, 3.0, 0.25 * 9.8
        t_stop, t_box = v0 / a, v0 / ak
        x_agv = lambda t: v0 * min(t, t_stop) - 0.5 * a * min(t, t_stop) ** 2
        x_box = lambda t: v0 * min(t, t_box) - 0.5 * ak * min(t, t_box) ** 2
        y0, xs = 0.7, -1.2            # ground line and braking point
        floor = ground(y0, -7, 7)
        view = VGroup(zh("地面上看", 24, "#ffd33d"), en("seen from the ground", 18)).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
        view.to_corner(UR, buff=0.4).shift(DOWN * 0.9)
        self.play(FadeIn(floor), FadeIn(view))

        cruise = ValueTracker(-0.9)   # seconds of cruising before braking starts (negative time)
        t = ValueTracker(0)
        def pos_agv():
            c = cruise.get_value()
            return xs + s * (v0 * c if c < 0 else x_agv(t.get_value()))
        def pos_box():
            c = cruise.get_value()
            return xs + s * (v0 * c if c < 0 else x_box(t.get_value()))
        car = always_redraw(lambda: agv(2.4).move_to([pos_agv(), y0, 0], aligned_edge=DOWN).shift(UP * 0.18))
        box = always_redraw(lambda: cargo(0.6).move_to([pos_box(), y0 + 0.18 + 0.7 + 0.3, 0]))
        vread = always_redraw(lambda: VGroup(
            readout(r"v_{\rm AGV}", "%.2f" % (v0 if cruise.get_value() < 0 else max(0, v0 - a * t.get_value())), "m/s", STEEL, 28),
            readout(r"v_{\rm box}", "%.2f" % (v0 if cruise.get_value() < 0 else max(0, v0 - ak * t.get_value())), "m/s", "#d29922", 28),
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(UL, buff=0.4).shift(DOWN * 1.3))
        self.add(car, box, vread)
        self.caption("AGV 匀速行驶，货箱和车一起运动", "The AGV cruises; the box moves with it", wait=0)
        self.play(cruise.animate.set_value(0), run_time=1.6, rate_func=linear)
        self.caption("AGV 急停：地面上看，货箱保持原来的速度向前",
                     "Emergency stop: from the ground, the box keeps going", wait=0)
        brake = Text("STOP", font=LATIN, font_size=26, color=RED, weight=BOLD).move_to([xs + 3.2, y0 + 0.9, 0])
        self.play(FadeIn(brake), run_time=0.3)
        self.play(t.animate.set_value(t_box), run_time=4.0, rate_func=linear)
        self.wait(0.8)

        # the same braking, from the AGV (deck zoomed in 20x)
        z = 20.0
        deck = Rectangle(width=7.0, height=0.25, color=STEEL, fill_color=NAVY, fill_opacity=1).move_to([0, -1.9, 0])
        rail = Rectangle(width=0.15, height=0.9, color=STEEL, fill_color=NAVY, fill_opacity=1).next_to(deck, UP, buff=0).align_to(deck, RIGHT)
        view2 = VGroup(zh("车上看（放大 20 倍）", 24, "#9ecbff"), en("seen from the AGV (20x zoom)", 18)).arrange(DOWN, aligned_edge=LEFT, buff=0.05)
        view2.next_to(deck, UP, buff=1.1).align_to(deck, LEFT)
        t2 = ValueTracker(0)
        box2 = always_redraw(lambda: cargo(0.9).next_to(deck, UP, buff=0).set_x(-1.5 + z * (x_box(t2.get_value()) - x_agv(t2.get_value()))))
        start = DashedLine([-1.5, -1.75, 0], [-1.5, -0.6, 0], color=GREY_B)
        dx = always_redraw(lambda: readout(r"\Delta x", "%.3f" % (x_box(t2.get_value()) - x_agv(t2.get_value())), "m", "#d29922", 30)
                           .next_to(deck, UP, buff=1.1).align_to(deck, RIGHT))
        self.play(FadeIn(deck), FadeIn(rail), FadeIn(view2), FadeIn(start), FadeIn(box2), FadeIn(dx))
        self.caption("车上看，货箱“自己”向前滑——车不是惯性系",
                     "From the AGV the box slides forward by itself: the braking AGV is not an inertial frame", wait=0)
        self.play(t2.animate.set_value(t_box), run_time=3.0, rate_func=linear)
        self.wait(1.2)
        self.clear_stage()

        # 3. Does it slide? compare the braking with what friction can give
        ax = Axes(x_range=[0, 3.5, 0.5], y_range=[0, 2, 1], x_length=7, y_length=2.4, tips=False,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 22}).shift(DOWN * 0.3 + LEFT * 0.5)
        ax.y_axis.set_opacity(0)
        unit = MathTex(r"\mathrm{m/s^2}", font_size=26).next_to(ax.x_axis, RIGHT, buff=0.2)
        bar_a = Rectangle(width=ax.c2p(3.0, 0)[0] - ax.c2p(0, 0)[0], height=0.5, color=RED, fill_opacity=0.8)
        bar_a.move_to(ax.c2p(0, 1.4), aligned_edge=LEFT)
        bar_f = Rectangle(width=ax.c2p(0.3 * 9.8, 0)[0] - ax.c2p(0, 0)[0], height=0.5, color=GREEN, fill_opacity=0.8)
        bar_f.move_to(ax.c2p(0, 0.6), aligned_edge=LEFT)
        la = MathTex(r"a_{\rm AGV}=3.0", color=RED, font_size=32).next_to(bar_a, RIGHT)
        lf = MathTex(r"\mu g = 0.3\times 9.8 = 2.94", color=GREEN, font_size=32).next_to(bar_f, RIGHT)
        self.play(Create(ax), FadeIn(unit))
        self.caption("摩擦力能提供的最大减速度 μg，决定货箱滑不滑",
                     "The largest deceleration friction can give, μg, decides whether it slides", wait=0)
        self.play(GrowFromEdge(bar_a, LEFT), Write(la))
        self.play(GrowFromEdge(bar_f, LEFT), Write(lf))
        verdict = VGroup(MathTex(r"3.0 > 2.94", font_size=40, color=YELLOW),
                         zh("会滑动，约 0.08 m", 28, YELLOW), en("it slides, about 0.08 m", 20))
        verdict.arrange(DOWN, buff=0.12).to_edge(RIGHT, buff=0.5).shift(UP * 1.6)
        self.play(FadeIn(verdict, shift=LEFT * 0.2))
        self.wait(1.5)

        self.card([
            ["牛顿第一定律：合力为零，运动状态不变", "First law: zero net force, no change in motion"],
            MathTex(r"\sum \vec F = 0 \iff \vec v = \text{const}", font_size=42),
            ["加速（刹车）的车不是惯性系", "A braking vehicle is not an inertial frame"],
            MathTex(r"a > \mu g \ \Rightarrow\ \text{slides}", font_size=40),
        ])
'''


# The pattern shown to the animator since the team rebuild: HOW a lesson animation is written (title,
# a moving picture driven by the real formula with ValueTracker/always_redraw, live readings, captions for
# each beat, a closing card) with placeholder content. Its subject is deliberately empty so nothing of it
# can end up in a real course; AGV_2_1 above stays only as a physics sample for tests.
TECHNIQUE = r'''
from wq_anim import *


class Lesson(Base):
    def construct(self):
        # Title: lesson number and THIS lesson's title (placeholders here).
        self.title("X.Y", "（本课标题）", "(lesson title)")

        # 1. The situation: draw THIS lesson's own objects (for a robotics course: planar_arm, frame3,
        #    mobile_robot, lidar ...). Here only a placeholder shape on axes.
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 2.5, 0.5], x_length=6, y_length=3.2, tips=False,
                  axis_config={"color": GREY_B}).shift(LEFT * 2.6 + DOWN * 0.2)
        labels = VGroup(MathTex("s", font_size=30).next_to(ax.x_axis, RIGHT), MathTex("q(s)", font_size=30).next_to(ax.y_axis, UP))
        self.play(Create(ax), FadeIn(labels))
        self.caption("先看要研究的量怎样随参数变化", "First, how the quantity changes with the parameter")

        # 2. Motion computed from the formula (never hand-placed): a tracker drives the picture and readings.
        s = ValueTracker(0.0)
        f = lambda x: 2.0 * (1 - np.exp(-x))
        curve = always_redraw(lambda: ax.plot(f, x_range=[0, max(s.get_value(), 0.01)], color=C_V))
        dot = always_redraw(lambda: Dot(ax.c2p(s.get_value(), f(s.get_value())), color=YELLOW))
        reading = always_redraw(lambda: readout("q", f"{f(s.get_value()):.2f}", "", YELLOW, 32).to_corner(UR).shift(DOWN * 1.1 + LEFT * 0.4))
        self.add(curve, dot, reading)
        self.play(s.animate.set_value(4.0), run_time=4, rate_func=linear)
        self.caption("读数由公式实时算出，与画面同步", "The reading is computed from the formula, in step with the picture")

        # 3. The key moment: point at it and name it.
        mark = DashedLine(ax.c2p(0, 2.0), ax.c2p(4, 2.0), color=GREY_B)
        note = MathTex(r"q \to q_{\max}", font_size=32, color=GREY_B).next_to(mark, UP, buff=0.1).align_to(mark, RIGHT)
        self.play(Create(mark), Write(note))
        self.caption("关键现象：说清它为什么发生", "The key effect, and why it happens", wait=2.0)

        # 4. Closing card: the lesson's key formula(s) and one sentence each.
        self.clear_stage()
        self.card([MathTex(r"q(s) = q_{\max}\,(1 - e^{-s})", font_size=44), ["（本课的结论）", "(the lesson's conclusion)"]])
'''
