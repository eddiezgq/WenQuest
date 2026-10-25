"""动画 27.4.1（配图 27.4.1）：力封闭。数值与算例 27.4.1、27.4.2 相同。
(1) 两指捏住宽 40 mm 的零件，μ = 0.2（摩擦锥半顶角 11.3°）：下面的接触点逐渐错开 Δ，两点的连线还在两个摩擦锥内时是力封闭；
    Δ 超过 μw = 8 mm，连线伸出锥外，失去力封闭——对夹时下面的指要打滑。
(2) 没有摩擦时，接触力只能沿法向：3 个接触总有一个方向挡不住（图中零件可以向右滑出），4 个摆得对才能形封闭。
(3) 夹圆柱毛坯：两个点接触的连线就是夹紧方向，所有接触力对它都没有力矩，毛坯会绕它转；线接触（两端两点）才能挡住。"""
from manim import *
from wq_anim import *
import numpy as np
import math

MU = 0.2
W = 40.0                 # 零件宽 / mm
SC = 0.07                # 图中 1 mm 的长度


class Lesson(Base):
    def construct(self):
        self.title("27.4", "力封闭：这样夹，牢不牢", "Force closure: is the grasp secure?")
        a = math.atan(MU)
        o = np.array([-2.0, 0.0, 0])
        part = Rectangle(width=70 * SC, height=W * SC, color=GREY_B, fill_opacity=0.5).move_to(o)
        self.play(FadeIn(part), run_time=0.5)
        dlt = ValueTracker(0.0)
        top = o + np.array([0, W * SC / 2, 0])
        L = 1.4

        def cone(p, n):
            e1 = np.array([n[0] * math.cos(a) - n[1] * math.sin(a), n[0] * math.sin(a) + n[1] * math.cos(a), 0])
            e2 = np.array([n[0] * math.cos(a) + n[1] * math.sin(a), -n[0] * math.sin(a) + n[1] * math.cos(a), 0])
            return Polygon(p, p + L * e1, p + L * e2, color=BLUE, fill_opacity=0.25, stroke_width=2)

        def bot():
            return o + np.array([dlt.get_value() * SC, -W * SC / 2, 0])
        ok = lambda: dlt.get_value() <= MU * W                     # noqa: E731
        c1 = cone(top, np.array([0, -1.0]))
        c2 = always_redraw(lambda: cone(bot(), np.array([0, 1.0])))
        f1 = Triangle(color=STEEL, fill_opacity=1).scale(0.18).rotate(PI).move_to(top + UP * 0.18)
        f2 = always_redraw(lambda: Triangle(color=STEEL, fill_opacity=1).scale(0.18).move_to(bot() + DOWN * 0.18))
        ln = always_redraw(lambda: Line(top, bot(), color=GREEN if ok() else RED, stroke_width=5))
        rd = always_redraw(lambda: VGroup(zh(f"Δ = {dlt.get_value():.1f} mm", 30, WHITE),
                                          bi(["力封闭 ✓", "force closure ✓"] if ok() else ["不是力封闭 ✗", "no force closure ✗"], 28,
                                             GREEN if ok() else RED)).arrange(DOWN, aligned_edge=LEFT).move_to([3.6, 0.8, 0]))
        self.add(c1, c2, f1, f2, ln, rd)
        self.add(zh("μ = 0.2，μw = 8 mm", 24, YELLOW).move_to([3.6, -0.6, 0]))
        self.play(dlt.animate.set_value(MU * W), run_time=2.5, rate_func=linear)
        self.wait(0.5)
        self.play(dlt.animate.set_value(12.0), run_time=1.5, rate_func=linear)
        self.caption("两指对径：两点的连线必须同时在两个摩擦锥内；错开超过 μw，对夹时下面的指就要打滑",
                     "Antipodal grasp: the line between the fingers must lie in both cones; beyond μw the lower finger slips", wait=2.5)
        self.clear_stage()
        # (2) 无摩擦：3 个与 4 个
        o2 = np.array([-3.2, 0.2, 0])
        o3 = np.array([3.2, 0.2, 0])
        for oc, pts, good in ((o2, [((-0.6, 1.4), (0, -1)), ((0.9, -1.4), (0, 1)), ((-2.45, 0), (1, 0))], False),
                              (o3, [((-0.9, 1.4), (0, -1)), ((0.9, -1.4), (0, 1)), ((-2.45, 0.6), (1, 0)), ((2.45, -0.6), (-1, 0))], True)):
            box = Rectangle(width=4.9, height=2.8, color=GREY_B, fill_opacity=0.5).move_to(oc)
            arrs = VGroup(*[Arrow(oc + np.array([p[0] - 0.7 * n[0], p[1] - 0.7 * n[1], 0]), oc + np.array([p[0], p[1], 0]), buff=0,
                                  color=STEEL, stroke_width=6) for p, n in pts])
            self.play(FadeIn(box), GrowFromCenter(arrs), run_time=0.8)
            self.add(bi(["3 个：总有方向挡不住", "3 contacts: some motion escapes"] if not good else ["4 个：形封闭", "4 contacts: form closure"], 24,
                        RED if not good else GREEN).next_to(box, UP, buff=0.3))
            if not good:
                esc = Arrow(oc + RIGHT * 0.6, oc + RIGHT * 2.0, buff=0, color=RED, stroke_width=6)   # 右边没有接触：零件可以向右滑出
                self.play(GrowArrow(esc), run_time=0.6)
        self.caption("没有摩擦时只能靠法向力：平面上至少要 4 个接触、空间至少 7 个才能形封闭",
                     "Without friction only normal forces help: form closure needs at least 4 contacts in the plane, 7 in space", wait=2.5)
        self.clear_stage()
        # (3) 圆柱：两点与线接触
        cyl = Rectangle(width=5.0, height=1.2, color=GREY_B, fill_opacity=0.5).move_to([-0.5, 0.3, 0])
        axis = DashedLine([-3.5, 0.3, 0], [2.5, 0.3, 0], color=YELLOW)
        self.play(FadeIn(cyl), Create(axis), run_time=0.6)
        p1 = Dot([-2.2, 0.3, 0], color=STEEL, radius=0.15)
        self.add(p1, bi(["两个点接触在夹紧方向的直线上（垂直于纸面）", "two point contacts on the grip line (normal to the page)"], 22, WHITE).move_to([0, 2.2, 0]))
        rot = Arc(radius=0.5, start_angle=-PI / 2, angle=1.6 * PI, color=RED, stroke_width=5).add_tip().move_to([-2.2, 0.3, 0])
        self.play(Create(rot), run_time=0.8)
        self.play(Rotate(VGroup(cyl, axis), angle=-0.35, about_point=np.array([-2.2, 0.3, 0])), run_time=1.0)
        self.caption("点接触的摩擦力对夹紧线没有力矩：重力一扭，毛坯就绕两指的连线转下去",
                     "Point-contact friction has no moment about the grip line: the weight twists the blank down about it", wait=2.0)
        self.play(Rotate(VGroup(cyl, axis), angle=0.35, about_point=np.array([-2.2, 0.3, 0])), FadeOut(rot), run_time=0.8)
        pad = Rectangle(width=1.0, height=0.3, color=STEEL, fill_opacity=0.9).move_to([-2.2, 0.3, 0])
        up = Arrow([-1.75, 0.3, 0], [-1.75, 1.3, 0], buff=0, color=GREEN, stroke_width=6)
        dn = Arrow([-2.65, 0.3, 0], [-2.65, -0.15, 0], buff=0, color=ORANGE, stroke_width=6)
        self.play(FadeIn(pad), GrowArrow(up), GrowArrow(dn), run_time=1.0)
        self.caption("线接触：两端方向相反的摩擦力组成力偶，挡住这个转动——平口、V 形夹爪都是这样夹住圆柱的",
                     "Line contact: opposite friction at the two ends forms a couple that stops the twist—how flat and V-jaws hold a cylinder", wait=2.5)
        self.card([["力封闭", "Force closure"],
                   ["接触力的母线力旋量能正张成整个空间", "the contact wrench edges positively span the whole space"],
                   MathTex(r"\operatorname{rank}W = n,\qquad Wk = 0,\ k_j > 0", font_size=40),
                   ["圆柱只能靠摩擦夹住：指面要线接触，最好用 V 形指", "A cylinder is held only by friction: use line contacts, preferably V-jaws"]])
