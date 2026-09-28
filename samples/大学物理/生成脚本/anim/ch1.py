"""Chapter 1 animations (Manim Community), 3Blue1Brown style.

Render one scene:  manim -r 1920,1080 --fps 30 ch1.py RefFrame
"""
import numpy as np
from manim import *

CJK = "Noto Sans CJK SC"
config.background_color = "#0f1419"


EN = {
"车厢匀速向右行驶，乘客松手让小球下落": "The carriage moves right at constant speed; a passenger lets go of a ball",
"同一个小球：车厢里看是直线，地面上看是抛物线": "Same ball: a straight line seen from the carriage, a parabola seen from the ground",
"所以描述运动，必须先选定参考系": "So to describe motion, first choose a reference frame",
"研究地球公转时，地球的大小可以忽略……": "For Earth's orbit around the Sun, Earth's size can be ignored...",
"……把它看成一个有质量的点：质点（理想模型）": "...so treat it as a point with mass: a particle (an idealized model)",
"位置矢量 r(t)：从原点指向质点，端点画出轨迹": "Position vector r(t) points from the origin to the particle; its tip traces the path",
"一般情况下 |Δr| ≠ Δs：弦比弧短": "In general |Δr| ≠ Δs: the chord is shorter than the arc",
"让 Δt 越来越小……": "Now let Δt shrink...",
"Δt → 0 时，弦贴近切线，|dr| = ds": "As Δt → 0 the chord approaches the tangent, and |dr| = ds",
"速度方向沿轨迹切线，大小是速率 ds/dt": "Velocity points along the tangent; its magnitude is the speed ds/dt",
"以 20 m/s、60° 抛出。看它在两个坐标轴上的“影子”": "Launched at 20 m/s and 60°. Watch its 'shadows' on the two axes",
"水平影子匀速前进；竖直影子像竖直上抛：先减速，再加速下落": "The horizontal shadow moves uniformly; the vertical one rises, slows, then falls",
"水平分速度不变（蓝），竖直分速度均匀减小（绿）": "Horizontal velocity stays constant (blue); vertical velocity decreases steadily (green)",
"同样的初速度，哪个角度射得最远？": "Same launch speed: which angle goes farthest?",
"45° 最远；30° 和 60° 落在同一点（互余角射程相同）": "45° goes farthest; 30° and 60° land at the same point (complementary angles)",
"匀速圆周运动：速率不变，但速度方向时刻在变": "Uniform circular motion: constant speed, but the direction keeps changing",
"取两个时刻的速度 v₁、v₂，把它们平移到同一起点": "Take velocities v₁ and v₂ at two instants and move them to a common tail",
"Δv = v₂ − v₁。让两个时刻越来越近……": "Δv = v₂ − v₁. Bring the two instants closer...",
"Δv 最后垂直于 v，指向圆心：这就是法向加速度": "Δv ends up perpendicular to v, pointing to the center: the normal acceleration",
"如果还越转越快：再多一个沿切线的加速度": "If it also speeds up, there is a tangential acceleration too",
"速度越大，法向加速度越大（与 v² 成正比）": "The faster it goes, the larger the normal acceleration (proportional to v²)",
"船头始终垂直河岸，船相对水的速度 1.2 m/s，水流速度 0.8 m/s": "Bow kept perpendicular to the bank: boat 1.2 m/s relative to water, current 0.8 m/s",
"船被冲向下游：它相对岸的速度是两个速度的矢量和": "The boat drifts downstream: its velocity relative to the bank is the vector sum",
"伽利略速度变换：A 对 C = A 对 B + B 对 C": "Galilean velocity addition: A rel. C = A rel. B + B rel. C",
"想正对岸靠岸？船头要斜向上游": "To land straight across, aim the bow upstream",
"船对岸的速度正好垂直河岸——但渡河时间变长了": "Now the velocity relative to the bank is straight across, but the crossing takes longer",
"参考系：运动是相对的": "Reference frames: motion is relative",
"速度：位矢对时间的导数": "Velocity: the time derivative of position",
"抛体运动：两个简单运动的合成": "Projectile motion: two simple motions combined",
"圆周运动：速度方向变了，就有加速度": "Circular motion: changing direction means acceleration",
"相对运动：过河的小船": "Relative motion: crossing a river",
"描述运动三步": "Three steps to describe motion",
"① 选参考系    ② 建坐标系    ③ 选研究对象（质点）": "① choose a frame   ② set up coordinates   ③ choose the object (particle)",
"同一运动，在不同参考系中轨迹和速度都可能不同": "The same motion can have different paths and velocities in different frames",
"求导：由运动方程得到速度、加速度": "Differentiate the equation of motion to get velocity and acceleration",
"|Δr| ≠ Δs，但 |dr| = ds；速度沿切线方向": "|Δr| ≠ Δs, but |dr| = ds; velocity is tangent to the path",
"抛体运动 = 水平匀速 + 竖直匀加速": "Projectile = uniform horizontal + uniformly accelerated vertical motion",
"匀速圆周运动：aₜ = 0，但 aₙ ≠ 0": "Uniform circular motion: aₜ = 0 but aₙ ≠ 0",
"伽利略速度变换": "Galilean velocity addition",
"速度是矢量，相加要用平行四边形（三角形）法则": "Velocities are vectors: add them with the parallelogram (triangle) rule"
}


def en(s, size=20, color="#9aa7b2"):
    return Text(s, font="DejaVu Sans", font_size=size * 0.92, color=color)


def zh(s, size=30, color=WHITE, weight=NORMAL):
    return Text(s, font=CJK, font_size=size, color=color, weight=weight)


class Base(Scene):
    """Title, bottom captions and a closing formula card shared by every clip."""

    def title(self, no, text):
        head = VGroup(zh(no, 26, YELLOW), zh(text, 34, WHITE, BOLD)).arrange(RIGHT, buff=0.3)
        t = VGroup(head, en(EN.get(text, ""), 20)).arrange(DOWN, aligned_edge=LEFT, buff=0.1) if text in EN else head
        t.to_corner(UL, buff=0.4)
        self.play(FadeIn(t, shift=DOWN * 0.2), run_time=0.8)
        self._title = t
        self._cap = None
        return t

    def caption(self, text, wait=0.0):
        new = zh(text, 26, "#e6edf3")
        if text in EN:
            new = VGroup(new, en(EN[text], 19)).arrange(DOWN, buff=0.08)
        bg = BackgroundRectangle(new, color="#0f1419", fill_opacity=0.85, buff=0.15)
        g = VGroup(bg, new).to_edge(DOWN, buff=0.25)
        if self._cap is None:
            self.play(FadeIn(g, shift=UP * 0.15), run_time=0.6)
        else:
            self.play(FadeOut(self._cap, shift=UP * 0.15), FadeIn(g, shift=UP * 0.15), run_time=0.6)
        self._cap = g
        if wait:
            self.wait(wait)

    def card(self, lines, wait=2.5):
        """lines: list of mobjects (MathTex or zh) for the closing summary."""
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)
        full = []
        for m in lines:
            full.append(m)
            src = getattr(m, "text", None) or getattr(m, "original_text", None)
            if isinstance(m, Text) and src in EN:
                full.append(en(EN[src], 22))
        lines = full
        body = VGroup(*lines).arrange(DOWN, buff=0.3)
        box = SurroundingRectangle(body, color=YELLOW, buff=0.45, corner_radius=0.15, stroke_width=2)
        self.play(Create(box), LaggedStart(*[Write(m) for m in lines], lag_ratio=0.35), run_time=2.2)
        self.wait(wait)


# ---------------------------------------------------------------------------------- 1.1
def train_car(width=3.2, height=1.6):
    body = RoundedRectangle(width=width, height=height, corner_radius=0.15, color="#58a6ff",
                            fill_color="#1f3a5f", fill_opacity=1, stroke_width=3)
    windows = VGroup(*[Rectangle(width=0.55, height=0.45, color="#9ecbff", fill_color="#0f1419",
                                 fill_opacity=1, stroke_width=2) for _ in range(3)]).arrange(RIGHT, buff=0.35)
    windows.move_to(body.get_top() + DOWN * 0.45)
    wheels = VGroup(*[Circle(0.2, color=GREY_B, fill_color=GREY_D, fill_opacity=1) for _ in range(2)])
    wheels.arrange(RIGHT, buff=width - 1.2).next_to(body, DOWN, buff=-0.1)
    return VGroup(body, windows, wheels)


class RefFrame(Base):
    def construct(self):
        self.title("1.1", "参考系：运动是相对的")
        divider = DashedLine(UP * 2.6, DOWN * 2.4, color=GREY_C)
        lt = zh("在车厢里看 In the carriage", 28, "#9ecbff").move_to([-3.6, 2.4, 0])
        rt = zh("在地面上看 From the ground", 28, "#ffd33d").move_to([3.6, 2.4, 0])
        ground_r = Line([0.4, -1.9, 0], [7.0, -1.9, 0], color=GREY_B)
        floor_l = Line([-6.6, -1.9, 0], [-0.6, -1.9, 0], color="#58a6ff")
        self.play(Create(divider), FadeIn(lt), FadeIn(rt), Create(ground_r), Create(floor_l))

        # physics (scene units): train speed u, gravity g, drop height h
        u, g, h = 2.4, 2.2, 2.6
        T = np.sqrt(2 * h / g)
        t = ValueTracker(0)

        car_l = train_car(4.0, 3.4).move_to([-3.6, -0.1, 0])
        car_l[0].set_fill(opacity=0.25)
        x0 = 1.9
        car_r = train_car(2.6, 3.4).move_to([x0, -0.1, 0])
        car_r[0].set_fill(opacity=0.25)
        car_r.add_updater(lambda m: m.move_to([x0 + u * t.get_value(), -0.1, 0]))
        top = 1.3

        ball_l = always_redraw(lambda: Dot([-3.6, top - 0.5 * g * t.get_value() ** 2, 0], radius=0.12, color=YELLOW))
        ball_r = always_redraw(lambda: Dot([x0 + u * t.get_value(), top - 0.5 * g * t.get_value() ** 2, 0],
                                           radius=0.12, color=YELLOW))
        self.play(FadeIn(car_l), FadeIn(car_r))
        self.caption("车厢匀速向右行驶，乘客松手让小球下落")

        # the train moves a bit before the release so the ground viewer sees it moving
        pre = ValueTracker(-0.9)
        car_r.clear_updaters()
        car_r.add_updater(lambda m: m.move_to([x0 + u * pre.get_value(), -0.1, 0]))
        held = always_redraw(lambda: Dot([x0 + u * pre.get_value(), top, 0], radius=0.12, color=YELLOW))
        car_r.shift(LEFT * u * 0.9)
        self.add(held, Dot([-3.6, top, 0], radius=0.12, color=YELLOW).set_z_index(1))
        self.play(pre.animate.set_value(0), run_time=1.2, rate_func=linear)
        self.remove(held)
        self.remove(*[m for m in self.mobjects if isinstance(m, Dot)])
        car_r.clear_updaters()
        car_r.add_updater(lambda m: m.move_to([x0 + u * t.get_value(), -0.1, 0]))

        trace_l = TracedPath(ball_l.get_center, stroke_color=YELLOW, stroke_width=4)
        trace_r = TracedPath(ball_r.get_center, stroke_color=YELLOW, stroke_width=4)
        self.add(trace_l, trace_r, ball_l, ball_r)
        self.play(t.animate.set_value(T * 0.999), run_time=3.2, rate_func=linear)
        self.wait(0.3)

        lab_l = zh("直线 line", 30, YELLOW).next_to([-3.6, 0, 0], RIGHT, buff=0.35)
        lab_r = zh("抛物线 parabola", 30, YELLOW).move_to([x0 + 0.6, -0.9, 0])
        self.play(Write(lab_l), Write(lab_r))
        self.caption("同一个小球：车厢里看是直线，地面上看是抛物线", wait=2.2)
        self.caption("所以描述运动，必须先选定参考系", wait=1.8)

        # point-particle idea
        self.play(*[FadeOut(m) for m in self.mobjects if m is not self._title and m is not self._cap])
        sun = Dot(ORIGIN + LEFT * 0.5, radius=0.35, color="#ffb000")
        orbit = Circle(2.2, color=GREY_C, stroke_width=2).move_to(sun)
        earth = Circle(0.55, color="#58a6ff", fill_color="#1f6feb", fill_opacity=1).move_to(orbit.point_at_angle(0))
        self.play(FadeIn(sun), Create(orbit), FadeIn(earth))
        self.caption("研究地球公转时，地球的大小可以忽略……")
        self.play(earth.animate.scale(0.18), run_time=1.2)
        self.play(MoveAlongPath(earth, orbit.copy().rotate(0)), run_time=2.5, rate_func=linear)
        self.caption("……把它看成一个有质量的点：质点（理想模型）", wait=1.8)

        self.card([
            zh("描述运动三步", 34, YELLOW, BOLD),
            zh("① 选参考系    ② 建坐标系    ③ 选研究对象（质点）", 30),
            zh("同一运动，在不同参考系中轨迹和速度都可能不同", 26, GREY_A),
        ])


# ---------------------------------------------------------------------------------- 1.2
class Derivative(Base):
    def construct(self):
        self.title("1.2", "速度：位矢对时间的导数")
        ax = Axes(x_range=[0, 7, 1], y_range=[0, 21, 5], x_length=6.0, y_length=4.5,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 22},
                  tips=False).to_edge(LEFT, buff=0.7).shift(DOWN * 0.05)
        xl = MathTex("x/\\mathrm{m}", font_size=28).next_to(ax.x_axis, RIGHT, buff=0.15)
        yl = MathTex("y/\\mathrm{m}", font_size=28).next_to(ax.y_axis, UP, buff=0.15)
        r_of = lambda s: np.array([2 * s, 19 - 2 * s * s])
        P = lambda s: ax.c2p(*r_of(s))
        path = ParametricFunction(P, t_range=[0, 3], color="#58a6ff", stroke_width=4)
        eq = MathTex(r"\vec r = 2t\,\vec i + (19-2t^2)\,\vec j", font_size=36).to_corner(UR, buff=0.6).shift(DOWN * 0.6)
        self.play(Create(ax), Write(xl), Write(yl), Write(eq))

        t = ValueTracker(0)
        dot = always_redraw(lambda: Dot(P(t.get_value()), color=YELLOW))
        rvec = always_redraw(lambda: Arrow(ax.c2p(0, 0), P(t.get_value()), buff=0, color=YELLOW,
                                           stroke_width=5, max_tip_length_to_length_ratio=0.06))
        rlab = always_redraw(lambda: MathTex(r"\vec r(t)", color=YELLOW, font_size=34)
                             .move_to((ax.c2p(0, 0) + P(t.get_value())) / 2 + np.array([0.35, 0.25, 0])))
        self.add(rvec, dot, rlab)
        self.caption("位置矢量 r(t)：从原点指向质点，端点画出轨迹")
        self.play(Create(path), t.animate.set_value(3), run_time=3.5, rate_func=linear)
        self.play(t.animate.set_value(0.8), run_time=1.2)
        self.remove(rlab)

        # displacement vs path length
        t0 = 0.8
        dt = ValueTracker(1.3)
        P0 = P(t0)
        P1 = lambda: P(t0 + dt.get_value())
        r1 = always_redraw(lambda: Arrow(ax.c2p(0, 0), P1(), buff=0, color=GREY_B, stroke_width=3,
                                         max_tip_length_to_length_ratio=0.05))
        arc = always_redraw(lambda: ParametricFunction(P, t_range=[t0, t0 + dt.get_value()], color=GREEN, stroke_width=8))
        dr = always_redraw(lambda: Arrow(P0, P1(), buff=0, color=RED, stroke_width=6,
                                         max_tip_length_to_length_ratio=0.25 if dt.get_value() > 0.3 else 0.5))
        dot1 = always_redraw(lambda: Dot(P1(), color=WHITE, radius=0.07))
        self.play(FadeIn(r1), FadeIn(dot1))
        self.play(Create(arc), GrowArrow(dr))
        leg = VGroup(
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=RED, stroke_width=6), zh("位移 Δr displacement", 24)).arrange(RIGHT),
            VGroup(Line(ORIGIN, RIGHT * 0.5, color=GREEN, stroke_width=8), zh("路程 Δs path length", 24)).arrange(RIGHT),
        ).arrange(DOWN, aligned_edge=LEFT).next_to(eq, DOWN, buff=0.6).align_to(eq, LEFT)

        def arc_len(a, b, n=200):
            s = np.linspace(a, b, n)
            return np.trapezoid(np.sqrt(4 + 16 * s * s), s)

        nums = always_redraw(lambda: VGroup(
            MathTex(r"|\Delta\vec r| = %.3f" % np.linalg.norm(r_of(t0 + dt.get_value()) - r_of(t0)), color=RED, font_size=34),
            MathTex(r"\Delta s = %.3f" % arc_len(t0, t0 + dt.get_value()), color=GREEN, font_size=34),
            MathTex(r"\Delta t = %.2f" % dt.get_value(), font_size=34),
        ).arrange(DOWN, aligned_edge=LEFT).next_to(leg, DOWN, buff=0.5).align_to(leg, LEFT))
        self.play(FadeIn(leg), FadeIn(nums))
        self.caption("一般情况下 |Δr| ≠ Δs：弦比弧短", wait=1.2)
        self.caption("让 Δt 越来越小……")
        self.play(dt.animate.set_value(0.04), run_time=4, rate_func=smooth)
        self.caption("Δt → 0 时，弦贴近切线，|dr| = ds", wait=1.0)

        # velocity = limit of Δr/Δt, tangent to the path
        self.play(FadeOut(r1), FadeOut(dot1), FadeOut(arc), FadeOut(dr))
        vel = r_of(t0) * 0 + np.array([2, -4 * t0])
        scale = 0.55
        tip = ax.c2p(*(r_of(t0) + vel * scale))
        v_arrow = Arrow(P0, tip, buff=0, color=ORANGE, stroke_width=6)
        tangent = DashedLine(ax.c2p(*(r_of(t0) - vel * 0.6)), ax.c2p(*(r_of(t0) + vel * 0.9)), color=GREY_B)
        vlab = MathTex(r"\vec v", color=ORANGE, font_size=38).next_to(tip, RIGHT, buff=0.1)
        self.play(Create(tangent), GrowArrow(v_arrow), Write(vlab))
        lim = MathTex(r"\vec v=\lim_{\Delta t\to 0}\frac{\Delta\vec r}{\Delta t}=\frac{d\vec r}{dt}", font_size=40, color=ORANGE)
        lim.next_to(leg, DOWN, buff=0.5).align_to(leg, LEFT)
        self.play(FadeOut(nums), Write(lim))
        self.caption("速度方向沿轨迹切线，大小是速率 ds/dt", wait=2.0)

        self.card([
            MathTex(r"\vec r(t)\ \xrightarrow{\ d/dt\ }\ \vec v(t)\ \xrightarrow{\ d/dt\ }\ \vec a(t)", font_size=48),
            zh("求导：由运动方程得到速度、加速度", 28),
            zh("|Δr| ≠ Δs，但 |dr| = ds；速度沿切线方向", 26, GREY_A),
        ])


# ---------------------------------------------------------------------------------- 1.3
class Projectile(Base):
    def construct(self):
        self.title("1.3", "抛体运动：两个简单运动的合成")
        g, v0 = 9.8, 20.0
        ax = Axes(x_range=[0, 44, 10], y_range=[0, 22, 5], x_length=10.5, y_length=4.4,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 22}, tips=False)
        ax.move_to([0.3, -0.05, 0])
        self.play(Create(ax))

        th = np.radians(60)
        T = 2 * v0 * np.sin(th) / g
        pos = lambda s: (v0 * np.cos(th) * s, v0 * np.sin(th) * s - 0.5 * g * s * s)
        t = ValueTracker(0)
        ball = always_redraw(lambda: Dot(ax.c2p(*pos(t.get_value())), radius=0.11, color=YELLOW))
        px = always_redraw(lambda: Dot(ax.c2p(pos(t.get_value())[0], 0), radius=0.09, color=BLUE))
        py = always_redraw(lambda: Dot(ax.c2p(0, pos(t.get_value())[1]), radius=0.09, color=GREEN))
        lx = always_redraw(lambda: DashedLine(ax.c2p(*pos(t.get_value())), px.get_center(), color=BLUE, stroke_width=2))
        ly = always_redraw(lambda: DashedLine(ax.c2p(*pos(t.get_value())), py.get_center(), color=GREEN, stroke_width=2))
        k = 0.05  # arrow length per m/s

        def comp(which):
            s = t.get_value()
            p = ax.c2p(*pos(s))
            vx, vy = v0 * np.cos(th), v0 * np.sin(th) - g * s
            d = {"x": [vx, 0], "y": [0, vy], "v": [vx, vy]}[which]
            col = {"x": BLUE, "y": GREEN, "v": ORANGE}[which]
            end = p + np.array([d[0] * k, d[1] * k, 0])
            if np.linalg.norm(end - p) < 0.05:
                return Dot(p, radius=0.001, fill_opacity=0)
            return Arrow(p, end, buff=0, color=col, stroke_width=5, max_tip_length_to_length_ratio=0.25)

        vxa = always_redraw(lambda: comp("x"))
        vya = always_redraw(lambda: comp("y"))
        va = always_redraw(lambda: comp("v"))
        trace = TracedPath(ball.get_center, stroke_color=YELLOW, stroke_width=3, dissipating_time=None)
        self.add(trace, lx, ly, px, py, ball, vxa, vya, va)
        self.caption("以 20 m/s、60° 抛出。看它在两个坐标轴上的“影子”")
        self.play(t.animate.set_value(T), run_time=5, rate_func=linear)
        self.caption("水平影子匀速前进；竖直影子像竖直上抛：先减速，再加速下落", wait=1.5)
        eqs = VGroup(
            MathTex(r"x=v_0\cos\theta\cdot t", color=BLUE, font_size=36),
            MathTex(r"y=v_0\sin\theta\cdot t-\tfrac12 g t^2", color=GREEN, font_size=36),
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(UR, buff=0.6).shift(DOWN * 0.7)
        self.play(Write(eqs))
        self.caption("水平分速度不变（蓝），竖直分速度均匀减小（绿）", wait=1.5)
        self.play(t.animate.set_value(T * 0.5), run_time=1.5)
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in [trace, lx, ly, px, py, ball, vxa, vya, va, eqs]])

        # which angle goes farthest?
        self.caption("同样的初速度，哪个角度射得最远？")
        colors = {15: "#79c0ff", 30: "#56d364", 45: "#ffd33d", 60: "#ff7b72", 75: "#d2a8ff"}
        paths = VGroup()
        for deg, col in colors.items():
            a = np.radians(deg)
            Tf = 2 * v0 * np.sin(a) / g
            p = ax.plot_parametric_curve(lambda s, a=a: np.array([v0 * np.cos(a) * s, v0 * np.sin(a) * s - 0.5 * g * s * s, 0]),
                                         t_range=[0, Tf], color=col, stroke_width=4)
            lab = MathTex(r"%d^\circ" % deg, color=col, font_size=30).next_to(p.point_from_proportion(0.5), UP, buff=0.1)
            paths.add(VGroup(p, lab))
            self.play(Create(p), FadeIn(lab), run_time=1.1)
        R45 = v0 ** 2 / g
        mark = Arrow(ax.c2p(R45, 5), ax.c2p(R45, 0.3), buff=0, color=YELLOW)
        self.play(GrowArrow(mark), Indicate(paths[2], color=YELLOW, scale_factor=1.03))
        self.caption("45° 最远；30° 和 60° 落在同一点（互余角射程相同）", wait=1.2)
        R = MathTex(r"R=\frac{v_0^2\sin 2\theta}{g}", font_size=46).to_corner(UR, buff=0.6).shift(DOWN * 0.7)
        self.play(Write(R))
        self.play(Indicate(paths[1]), Indicate(paths[3]), run_time=1.5)
        self.wait(1.2)

        self.card([
            zh("抛体运动 = 水平匀速 + 竖直匀加速", 34, YELLOW, BOLD),
            MathTex(r"x=v_0\cos\theta\, t,\qquad y=v_0\sin\theta\, t-\tfrac12 g t^2", font_size=40),
            MathTex(r"R=\frac{v_0^2\sin2\theta}{g}\quad(\theta=45^\circ\ \text{max})", font_size=40),
        ])


# ---------------------------------------------------------------------------------- 1.4
class Circular(Base):
    def construct(self):
        self.title("1.4", "圆周运动：速度方向变了，就有加速度")
        C = np.array([-3.2, -0.4, 0])
        R = 2.3
        circ = Circle(R, color=GREY_B).move_to(C)
        cdot = Dot(C, color=GREY_B, radius=0.05)
        self.play(Create(circ), FadeIn(cdot))
        L = 1.5
        on = lambda a: C + R * np.array([np.cos(a), np.sin(a), 0])
        tang = lambda a: np.array([-np.sin(a), np.cos(a), 0])

        th = ValueTracker(0)
        dot = always_redraw(lambda: Dot(on(th.get_value()), color=YELLOW, radius=0.1))
        v = always_redraw(lambda: Arrow(on(th.get_value()), on(th.get_value()) + L * tang(th.get_value()),
                                        buff=0, color=ORANGE, stroke_width=5))
        self.add(v, dot)
        self.caption("匀速圆周运动：速率不变，但速度方向时刻在变")
        self.play(th.animate.set_value(2 * PI), run_time=4, rate_func=linear)
        self.remove(v, dot)

        # Δv between two instants, drawn tail-to-tail on the right
        a1 = PI / 3
        da = ValueTracker(PI / 2.2)
        Q = np.array([3.6, -0.2, 0])
        v1c = always_redraw(lambda: Arrow(on(a1), on(a1) + L * tang(a1), buff=0, color=ORANGE, stroke_width=5))
        v2c = always_redraw(lambda: Arrow(on(a1 + da.get_value()), on(a1 + da.get_value()) + L * tang(a1 + da.get_value()),
                                          buff=0, color=PINK, stroke_width=5))
        d1 = Dot(on(a1), color=YELLOW)
        d2 = always_redraw(lambda: Dot(on(a1 + da.get_value()), color=YELLOW))
        self.play(FadeIn(d1), FadeIn(d2), GrowArrow(v1c), GrowArrow(v2c))
        self.caption("取两个时刻的速度 v₁、v₂，把它们平移到同一起点")
        w1 = always_redraw(lambda: Arrow(Q, Q + 2.0 * tang(a1), buff=0, color=ORANGE, stroke_width=5))
        w2 = always_redraw(lambda: Arrow(Q, Q + 2.0 * tang(a1 + da.get_value()), buff=0, color=PINK, stroke_width=5))
        dv = always_redraw(lambda: Arrow(Q + 2.0 * tang(a1), Q + 2.0 * tang(a1 + da.get_value()), buff=0, color=RED,
                                         stroke_width=6, max_tip_length_to_length_ratio=0.3))
        labs = always_redraw(lambda: VGroup(
            MathTex(r"\vec v_1", color=ORANGE, font_size=34).next_to(Q + 2.0 * tang(a1), UP + LEFT * 0.3, buff=0.1),
            MathTex(r"\vec v_2", color=PINK, font_size=34).next_to(Q + 2.0 * tang(a1 + da.get_value()), DOWN, buff=0.1),
        ))
        self.play(TransformFromCopy(v1c, w1), TransformFromCopy(v2c, w2))
        self.add(labs)
        self.play(GrowArrow(dv))
        dvl = always_redraw(lambda: MathTex(r"\Delta\vec v", color=RED, font_size=36).next_to(
            (Q + 2.0 * tang(a1) + Q + 2.0 * tang(a1 + da.get_value())) / 2, UR, buff=0.12))
        self.play(Write(dvl))
        self.caption("Δv = v₂ − v₁。让两个时刻越来越近……")
        self.play(da.animate.set_value(0.08), run_time=4)
        # direction of Δv/Δt at the limit: toward the centre
        self.caption("Δv 最后垂直于 v，指向圆心：这就是法向加速度", wait=0.5)
        a_n = always_redraw(lambda: Arrow(on(a1), on(a1) + (C - on(a1)) * 0.55, buff=0, color=RED, stroke_width=6))
        self.play(GrowArrow(a_n))
        an = MathTex(r"a_n=\frac{v^2}{R}", color=RED, font_size=46).move_to([3.6, 2.0, 0])
        self.play(Write(an))
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in [v1c, v2c, d1, d2, w1, w2, dv, labs, dvl, a_n, an]])

        # speeding up: tangential + normal components
        self.caption("如果还越转越快：再多一个沿切线的加速度")
        s = ValueTracker(0)
        ang = lambda: 0.35 * s.get_value() ** 2  # θ = ½αt²
        speed = lambda: 0.7 * s.get_value() * R  # v = Rω
        dot = always_redraw(lambda: Dot(on(ang()), color=YELLOW, radius=0.1))
        vv = always_redraw(lambda: Arrow(on(ang()), on(ang()) + min(0.35 * speed(), 1.6) * tang(ang()), buff=0, color=ORANGE, stroke_width=5)
                           if speed() > 0.2 else Dot(on(ang()), radius=0.001, fill_opacity=0))
        at = always_redraw(lambda: Arrow(on(ang()), on(ang()) + 0.9 * tang(ang()), buff=0, color=GREEN, stroke_width=5))
        ann = always_redraw(lambda: Arrow(on(ang()), on(ang()) + min(0.06 * speed() ** 2 / R * 3, 2.0) * (C - on(ang())) / R,
                                          buff=0, color=RED, stroke_width=5) if speed() > 0.5 else Dot(on(ang()), radius=0.001, fill_opacity=0))
        self.add(vv, at, ann, dot)
        leg = VGroup(
            VGroup(MathTex(r"a_t=\frac{dv}{dt}", color=GREEN, font_size=38), zh("切向：改变快慢 tangential: speed", 26, GREEN)).arrange(RIGHT, buff=0.4),
            VGroup(MathTex(r"a_n=\frac{v^2}{R}", color=RED, font_size=38), zh("法向：改变方向 normal: direction", 26, RED)).arrange(RIGHT, buff=0.4),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to([3.4, 0.6, 0])
        leg2 = VGroup()
        self.play(FadeIn(leg), FadeIn(leg2))
        self.play(s.animate.set_value(3.2), run_time=5, rate_func=linear)
        self.caption("速度越大，法向加速度越大（与 v² 成正比）", wait=1.2)

        self.card([
            MathTex(r"\vec a = a_t\,\vec e_t + a_n\,\vec e_n", font_size=48),
            MathTex(r"a_t=\frac{dv}{dt}=R\alpha,\qquad a_n=\frac{v^2}{R}=R\omega^2", font_size=42),
            zh("匀速圆周运动：aₜ = 0，但 aₙ ≠ 0", 28, GREY_A),
        ])


# ---------------------------------------------------------------------------------- 1.5
def boat(heading):
    hull = Polygon([0.45, 0, 0], [0.15, 0.18, 0], [-0.35, 0.18, 0], [-0.35, -0.18, 0], [0.15, -0.18, 0],
                   color=WHITE, fill_color="#e6edf3", fill_opacity=1, stroke_width=2)
    return hull.rotate(heading, about_point=ORIGIN)


class Relative(Base):
    def construct(self):
        self.title("1.5", "相对运动：过河的小船")
        bank_top, bank_bot = 1.9, -1.9
        water = Rectangle(width=14.5, height=bank_top - bank_bot, fill_color="#0b3a5e", fill_opacity=1, stroke_width=0)
        water.move_to([0, (bank_top + bank_bot) / 2, 0])
        lines = VGroup(Line([-7.3, bank_top, 0], [7.3, bank_top, 0], color="#56d364", stroke_width=5),
                       Line([-7.3, bank_bot, 0], [7.3, bank_bot, 0], color="#56d364", stroke_width=5))
        self.play(FadeIn(water), Create(lines))

        # flowing ripples
        ripples = VGroup(*[Line(ORIGIN, RIGHT * 0.5, color="#4a86b8", stroke_width=3).move_to([x, y, 0])
                           for x in np.arange(-7, 7.5, 1.6) for y in (-1.2, -0.2, 0.8)])
        flow = ValueTracker(0)
        base = ripples.copy()

        def move(m):
            for r, b in zip(m, base):
                x = (b.get_center()[0] + 7 + flow.get_value()) % 14.4 - 7
                r.move_to([x, b.get_center()[1], 0])
        ripples.add_updater(move)
        self.add(ripples)

        u, w = 1.2, 0.8  # boat speed relative to water, water speed relative to bank (scene units/s)
        start = np.array([-3.0, bank_bot, 0])
        t = ValueTracker(0)
        cross_T = (bank_top - bank_bot) / u

        bpos = lambda: start + np.array([w * t.get_value(), u * t.get_value(), 0])
        b = always_redraw(lambda: boat(PI / 2).move_to(bpos()))
        trace = TracedPath(lambda: bpos(), stroke_color=YELLOW, stroke_width=4)
        ghost = DashedLine(start, start + UP * (bank_top - bank_bot), color=GREY_B)
        self.add(trace, b)
        self.caption("船头始终垂直河岸，船相对水的速度 1.2 m/s，水流速度 0.8 m/s")
        self.play(Create(ghost), run_time=0.6)
        self.play(t.animate.set_value(cross_T), flow.animate.set_value(0.8 * cross_T), run_time=4.5, rate_func=linear)
        self.caption("船被冲向下游：它相对岸的速度是两个速度的矢量和", wait=0.5)

        # vector triangle
        O = np.array([3.8, -1.2, 0])
        k = 1.6
        vbw = Arrow(O, O + UP * u * k, buff=0, color=YELLOW, stroke_width=6)
        vwb = Arrow(O + UP * u * k, O + UP * u * k + RIGHT * w * k, buff=0, color=BLUE, stroke_width=6)
        vbb = Arrow(O, O + UP * u * k + RIGHT * w * k, buff=0, color=RED, stroke_width=6)
        l1 = zh("船对水 boat/water", 24, YELLOW).next_to(vbw, LEFT, buff=0.1)
        l2 = zh("水对岸 water/bank", 24, BLUE).next_to(vwb, UP, buff=0.1)
        l3 = zh("船对岸 boat/bank", 24, "#ff9b94").next_to(vbb.get_center(), RIGHT, buff=0.2)
        self.play(GrowArrow(vbw), FadeIn(l1))
        self.play(GrowArrow(vwb), FadeIn(l2))
        self.play(GrowArrow(vbb), FadeIn(l3))
        formula = MathTex(r"\vec v_{AC}=\vec v_{AB}+\vec v_{BC}", font_size=44).to_corner(UR, buff=0.5).shift(DOWN * 0.55)
        key = zh("A 船 boat  B 水 water  C 岸 bank", 21, GREY_A).next_to(formula, DOWN, buff=0.15).align_to(formula, RIGHT)
        self.play(Write(formula), FadeIn(key))
        self.caption("伽利略速度变换：A 对 C = A 对 B + B 对 C", wait=2.0)

        # aim upstream to land straight across
        self.play(*[FadeOut(m) for m in [b, trace, vbw, vwb, vbb, l1, l2, l3, ghost]])
        self.caption("想正对岸靠岸？船头要斜向上游")
        phi = np.arcsin(w / u)  # angle from the perpendicular, upstream
        heading = PI / 2 + phi
        vy = u * np.cos(phi)
        t2 = ValueTracker(0)
        bpos2 = lambda: start + np.array([0, vy * t2.get_value(), 0])
        b2 = always_redraw(lambda: boat(heading).move_to(bpos2()))
        trace2 = TracedPath(lambda: bpos2(), stroke_color=YELLOW, stroke_width=4)
        O2 = np.array([3.8, -1.2, 0])
        a1 = Arrow(O2, O2 + k * u * np.array([-np.sin(phi), np.cos(phi), 0]), buff=0, color=YELLOW, stroke_width=6)
        a2 = Arrow(a1.get_end(), a1.get_end() + RIGHT * w * k, buff=0, color=BLUE, stroke_width=6)
        a3 = Arrow(O2, a2.get_end(), buff=0, color=RED, stroke_width=6)
        self.play(GrowArrow(a1), GrowArrow(a2), GrowArrow(a3))
        self.add(trace2, b2)
        self.play(t2.animate.set_value((bank_top - bank_bot) / vy), flow.animate.increment_value(0.8 * 4),
                  run_time=5, rate_func=linear)
        sinphi = MathTex(r"\sin\varphi=\frac{v_{\text{water}}}{v_{\text{boat}}}=\frac{0.8}{1.2}", font_size=38)
        sinphi.move_to([0.6, -0.4, 0])
        sp_bg = BackgroundRectangle(sinphi, color="#0f1419", fill_opacity=0.8, buff=0.15)
        self.play(FadeIn(sp_bg), Write(sinphi))
        self.caption("船对岸的速度正好垂直河岸——但渡河时间变长了", wait=2.0)
        ripples.clear_updaters()

        self.card([
            zh("伽利略速度变换", 34, YELLOW, BOLD),
            MathTex(r"\vec v_{AC}=\vec v_{AB}+\vec v_{BC}", font_size=48),
            zh("速度是矢量，相加要用平行四边形（三角形）法则", 28, GREY_A),
        ])
