"""动画 27.2.1（配图 27.2.2）：摩擦锥与夹紧力。数值与算例 27.2.2、27.2.3 相同（μ = 0.2，示意值）。
(1) 摩擦锥：半顶角 arctan 0.2 = 11.3°；接触力在锥内时黏着，伸出锥外就打滑。截面上 4 条母线的棱锥在对角方向只有 μcos45°。
(2) 平口夹爪竖直提起 2.8 kg 的毛坯：每个指的摩擦力 m𝔤/2 = 13.7 N，法向力 F。F 从 100 N 降下来，降到 68.7 N 以下，
    合力伸出摩擦锥，毛坯滑落。
(3) 毛坯横过来：质心离夹持点 d = 50.8 mm，指面长 ℓ = 40 mm，远端一点要 24.3 N 向上、近端 10.6 N 向下，平口夹爪需要 243 N；
    换成 V 形指，重力由斜面的法向力兜住，只要约 23 N。"""
from manim import *
from wq_anim import *
import numpy as np
import math

MU = 0.2
W = 27.47                # 毛坯重力 / N
F_V = 68.67              # 竖直提起所需的夹紧力 / N
F_H = 243.2              # 毛坯水平、平口夹爪 / N
F_VH = 22.7              # 毛坯水平、V 形夹爪（MuJoCo）/ N
FP, FM = 24.32, -10.59   # 远端、近端一点的摩擦力 / N


class Lesson(Base):
    def construct(self):
        self.title("27.2", "摩擦锥与夹紧力", "Friction cones and grip force")
        # (1) 摩擦锥
        p = np.array([-3.5, -1.0, 0])
        surf = Line(p + LEFT * 2.5, p + RIGHT * 2.5, color=GREY_B, stroke_width=4)
        a = math.atan(MU)
        L = 3.2
        cone = Polygon(p, p + L * np.array([math.sin(a), math.cos(a), 0]), p + L * np.array([-math.sin(a), math.cos(a), 0]),
                       color=BLUE, fill_opacity=0.25, stroke_width=3)
        self.play(Create(surf), FadeIn(cone), run_time=0.8)
        self.add(zh("11.3°", 22, BLUE).move_to(p + np.array([0.75, 2.0, 0])))
        ang = ValueTracker(0.05)
        arr = always_redraw(lambda: Arrow(p, p + 2.6 * np.array([math.sin(ang.get_value()), math.cos(ang.get_value()), 0]), buff=0,
                                          color=GREEN if ang.get_value() <= a else RED, stroke_width=6))
        txt = always_redraw(lambda: bi(["黏着", "sticks"] if ang.get_value() <= a else ["打滑", "slips"], 26,
                                       GREEN if ang.get_value() <= a else RED).move_to(p + np.array([2.2, 1.0, 0])))
        self.add(arr, txt)
        self.play(ang.animate.set_value(0.35), run_time=2.0)
        self.play(ang.animate.set_value(0.1), run_time=1.0)
        # 截面
        c = np.array([3.4, 0.6, 0])
        R = 1.5
        circ = Circle(radius=R, color=BLUE, stroke_width=4).move_to(c)
        sq = Polygon(*[c + R * np.array([math.cos(k * PI / 2), math.sin(k * PI / 2), 0]) for k in range(4)], color=RED, stroke_width=3)
        diag = Arrow(c, c + R * math.cos(PI / 4) * np.array([math.cos(PI / 4), math.sin(PI / 4), 0]), buff=0, color=RED, stroke_width=5)
        self.play(Create(circ), Create(sq), GrowArrow(diag), run_time=1.2)
        self.add(zh("μ cos 45°", 22, RED).next_to(diag.get_end(), UR, buff=0.05))
        self.caption("接触力只能在摩擦锥内；4 条母线的棱锥在对角方向只有 μcos45°，MuJoCo 默认就是它",
                     "The contact force must stay in the cone; a 4-edge pyramid reaches only μcos45° on the diagonal (MuJoCo's default)", wait=2.5)
        self.clear_stage()
        # (2) 竖直提起
        blank = Rectangle(width=1.0, height=3.6, color=GREY_B, fill_opacity=0.6).move_to([-3.0, -0.6, 0])
        j1 = Rectangle(width=0.35, height=1.0, color=STEEL, fill_opacity=0.9).next_to(blank, LEFT, buff=0).shift(UP * 1.1)
        j2 = Rectangle(width=0.35, height=1.0, color=STEEL, fill_opacity=0.9).next_to(blank, RIGHT, buff=0).shift(UP * 1.1)
        grp = VGroup(blank, j1, j2)
        self.play(FadeIn(grp), run_time=0.6)
        Fv = ValueTracker(100.0)
        pt = j2.get_left()
        sc = 0.025

        def cone_at():
            n = 3.0 * np.array([-1, 0, 0])
            return Polygon(pt, pt + n + 3.0 * MU * UP, pt + n - 3.0 * MU * UP, color=BLUE, fill_opacity=0.2, stroke_width=2)
        cn = always_redraw(cone_at)
        res = always_redraw(lambda: Arrow(pt, pt + sc * np.array([-Fv.get_value(), W / 2, 0]), buff=0, stroke_width=6,
                                          color=GREEN if Fv.get_value() >= F_V else RED))
        rd = always_redraw(lambda: VGroup(zh(f"F = {Fv.get_value():.1f} N", 30, GREEN if Fv.get_value() >= F_V else RED),
                                          zh(f"最小 m𝔤/(2μ) = {F_V:.1f} N", 24, YELLOW)).arrange(DOWN, aligned_edge=LEFT).move_to([3.2, 1.4, 0]))
        wv = Arrow(blank.get_center(), blank.get_center() + DOWN * 1.2, buff=0, color=C_F, stroke_width=6)
        self.add(cn, res, rd, wv, zh("m𝔤", 24, C_F).next_to(wv, RIGHT, buff=0.05))
        self.caption("每个指要提供 m𝔤/2 的摩擦力；指面的合力（法向 F 加摩擦力）必须在摩擦锥内",
                     "Each jaw supplies m𝔤/2 of friction; the jaw force (normal F plus friction) must stay in the cone", wait=1.5)
        self.play(Fv.animate.set_value(F_V), run_time=2.5)
        self.play(Fv.animate.set_value(55.0), run_time=1.0)
        self.play(blank.animate.shift(DOWN * 1.8), rate_func=rate_functions.ease_in_quad, run_time=0.8)
        self.caption("夹紧力小于 m𝔤/(2μ)，合力伸出摩擦锥，毛坯从指间滑落",
                     "Below m𝔤/(2μ) the force leaves the cone and the blank slides out", wait=2.0)
        self.clear_stage()
        # (3) 横着拿
        bl = Rectangle(width=4.6, height=0.9, color=GREY_B, fill_opacity=0.6).move_to([-1.5, 0.3, 0])
        x0 = bl.get_left()[0]
        pad = Rectangle(width=1.0, height=0.25, color=STEEL, fill_opacity=0.9).move_to([x0 + 0.9, bl.get_top()[1] + 0.12, 0])
        self.play(FadeIn(bl), FadeIn(pad), run_time=0.6)
        com = Dot([x0 + 0.9 + 1.27, 0.3, 0], color=YELLOW, radius=0.08)
        wv = Arrow(com.get_center(), com.get_center() + DOWN * 1.1, buff=0, color=C_F, stroke_width=6)
        fpl = Arrow([x0 + 1.4, 0.3, 0], [x0 + 1.4, 0.3 + FP * 0.07, 0], buff=0, color=GREEN, stroke_width=6)
        fmi = Arrow([x0 + 0.4, 0.3, 0], [x0 + 0.4, 0.3 + FM * 0.07, 0], buff=0, color=ORANGE, stroke_width=6)
        self.play(FadeIn(com), GrowArrow(wv), run_time=0.6)
        self.play(GrowArrow(fpl), GrowArrow(fmi), run_time=1.0)
        dl = DoubleArrow([x0 + 0.9, bl.get_bottom()[1] - 0.35, 0], [com.get_center()[0], bl.get_bottom()[1] - 0.35, 0], buff=0,
                         color=YELLOW, stroke_width=3, tip_length=0.15)
        self.add(zh(f"{FP:.1f} N", 22, GREEN).next_to(fpl.get_end(), RIGHT, buff=0.1), zh(f"{-FM:.1f} N", 22, ORANGE).next_to(fmi.get_end(), LEFT, buff=0.1),
                 dl, zh("d = 50.8 mm", 22, YELLOW).next_to(dl, DOWN, buff=0.1))
        rd2 = VGroup(zh(f"平口：F ≥ {F_H:.0f} N", 30, RED), zh(f"竖直时 {F_V:.1f} N 的 {F_H / F_V:.1f} 倍", 24, MUTED)).arrange(DOWN, aligned_edge=LEFT).move_to([4.2, 1.5, 0])
        self.play(FadeIn(rd2), run_time=0.6)
        self.caption("横着拿时，重力还绕夹紧方向产生力矩，要靠指面两端方向相反的摩擦力去平衡",
                     "Held horizontally, gravity also twists about the grip axis; friction at the two pad ends must balance it", wait=2.5)
        # V 形指的截面
        c = np.array([4.2, -1.4, 0])
        circ = Circle(radius=0.7, color=GREY_B, fill_opacity=0.6).move_to(c)
        vs = VGroup()
        for s in (1, -1):
            for sg in (1, -1):
                t = math.pi / 4 * sg if s > 0 else math.pi - math.pi / 4 * sg
                q = c + 0.7 * np.array([math.cos(t), math.sin(t), 0])
                d = np.array([-math.sin(t), math.cos(t), 0])
                vs.add(Line(q - 0.45 * d, q + 0.45 * d, color=STEEL, stroke_width=8))
                if sg < 0:
                    vs.add(Arrow(q, q - 0.6 * np.array([math.cos(t), math.sin(t), 0]), buff=0, color=GREEN, stroke_width=5))
        self.play(FadeIn(circ), Create(vs), run_time=1.0)
        self.add(zh(f"V 形：约 {F_VH:.0f} N", 28, GREEN).next_to(circ, LEFT, buff=0.5))
        self.caption("V 形指：下面两个斜面的法向力本身就向上，把重力兜住，所需的夹紧力只有平口的十分之一",
                     "V-jaws: the lower faces push upwards, so normal forces carry the weight; a tenth of the flat-jaw force", wait=2.5)
        self.card([["摩擦锥与夹紧力", "Friction cones and grip force"],
                   MathTex(r"\|f_t\| \le \mu f_n ,\qquad F \ge \frac{m(\mathfrak g + a)}{2\mu}", font_size=40),
                   ["横着拿时还要平衡重力矩：F ≥ m𝔤(1/2 + d/ℓ)/μ", "Held horizontally the weight also twists: F ≥ m𝔤(1/2 + d/ℓ)/μ"],
                   ["夹持点靠近质心、指面做长、用 V 形指", "Grip near the CoM, use long pads, use V-jaws"]])
