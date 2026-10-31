"""动画 30.1.1（配图 30.1.1）：从任务到设计任务书。
(1) 减速器厂部件装配工位的六个取放点（俯视，示例布置）逐个出现；一个圆从 0.6 m 慢慢长大，直到每个点都留出 5% 的裕量：0.76 m；
    再加上通用性（机床上下料等别的工位），定为臂展 0.86 m 一类。
(2) 肩关节力矩的第一估计：负载 5 kg 在臂展处，手臂运动部分约为负载的 2.4 倍、质心在一半处：
    τ ≈ 𝔤(5 × 0.86 + 12 × 0.43) ≈ 93 N·m；按完整模型算是 96 N·m，差 4%。量级对了，就能先定减速器的规格（32 号，额定 137 N·m）。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("30.1", "从任务到设计任务书", "From the job to the design brief")
        sc = 3.0                                     # 图中 1 m
        o = np.array([-3.2, -0.4, 0])
        pts = [("轴料架", -90, 0.55), ("轴承料盘", -45, 0.45), ("压装工装", 0, 0.50), ("齿轮料架", 45, 0.60),
               ("AGV 料箱", 90, 0.70), ("检具", 150, 0.35)]
        base = Circle(radius=0.075 * sc, color=GREY_B, fill_opacity=1).move_to(o)
        bench = Rectangle(width=1.8 * sc, height=0.9 * sc, color=GREY_C, stroke_width=2).move_to(o)
        self.play(FadeIn(bench), FadeIn(base), run_time=0.6)
        dots = VGroup()
        for name, phi, r in pts:
            p = o + sc * r * np.array([np.cos(np.radians(phi)), np.sin(np.radians(phi)), 0])
            d = Dot(p, color=GREEN if name != "AGV 料箱" else RED, radius=0.09)
            lab = zh(name, 18, INK).next_to(d, RIGHT, buff=0.08)
            dots.add(VGroup(d, lab))
            self.play(FadeIn(d, scale=0.5), FadeIn(lab), run_time=0.35)
        self.caption("先列出机器人要去的地方：取轴、取轴承、放进压装工装、放进台面下的 AGV 料箱……",
                     "First list where the robot must go: pick the shaft and bearings, load the press, drop into the AGV tote below the bench", wait=1.0)
        R = ValueTracker(0.60)
        circ = always_redraw(lambda: Circle(radius=sc * R.get_value(), color=STEEL, stroke_width=3).move_to(o))
        rd = always_redraw(lambda: zh(f"臂展 {R.get_value():.2f} m", 26, STEEL).move_to([3.4, 1.6, 0]))
        self.add(circ, rd)
        self.play(R.animate.set_value(0.759), run_time=2.5, rate_func=linear)
        self.play(Indicate(rd, color=YELLOW), run_time=0.6)
        self.caption("圆长到 0.76 m，每个点（还要从上方 0.1 m 接近）都留出 5% 的裕量",
                     "At 0.76 m every point, approached from 0.1 m above, keeps a 5 % margin", wait=1.0)
        self.play(R.animate.set_value(0.86), run_time=1.2)
        note = VGroup(zh("再照顾机床上下料等别的工位", 24, INK), zh("→ 臂展 0.86 m 一类，负载 5 kg", 26, YELLOW)).arrange(DOWN, aligned_edge=LEFT).move_to([3.6, 0.6, 0])
        self.play(FadeIn(note), run_time=0.8)
        self.caption("任务书的数从任务里来：够得着、拿得动、走得快、放得准",
                     "The numbers in the brief come from the jobs: reach, payload, speed, accuracy", wait=1.5)
        self.clear_stage()
        # (2) 肩关节力矩的第一估计
        sh = np.array([-4.5, -1.3, 0])
        L = 0.86 * 6.5
        arm_line = Line(sh, sh + RIGHT * L, color=STEEL, stroke_width=10)
        load = Square(0.45, color=ORANGE, fill_opacity=0.9).move_to(sh + RIGHT * L + DOWN * 0.35)
        mid = Dot(sh + RIGHT * L / 2, color=RED, radius=0.12)
        self.play(Create(arm_line), FadeIn(Dot(sh, color=YELLOW, radius=0.14)), run_time=0.8)
        self.play(FadeIn(load), FadeIn(zh("5 kg", 22, ORANGE).next_to(load, RIGHT, buff=0.1)), run_time=0.5)
        self.play(FadeIn(mid), FadeIn(zh("手臂 ≈ 2.4 × 5 = 12 kg，质心在一半处", 22, RED).next_to(mid, UP, buff=0.2)), run_time=0.6)
        self.play(GrowArrow(Arrow(sh + RIGHT * L + DOWN * 0.6, sh + RIGHT * L + DOWN * 1.3, color=ORANGE, buff=0)),
                  GrowArrow(Arrow(sh + RIGHT * L / 2 + DOWN * 0.2, sh + RIGHT * L / 2 + DOWN * 1.2, color=RED, buff=0)), run_time=0.6)
        eq = VGroup(MathTex(r"\tau_2 \approx \mathfrak g\,(m_p R + m_{arm} R/2)", font_size=40),
                    MathTex(r"= 9.81\,(5\times0.86 + 12\times0.43) \approx 93\ \mathrm{N\,m}", font_size=36),
                    zh("完整模型（30.3 节）：96 N·m，只差 4%", 24, YELLOW),
                    zh("→ 肩关节用谐波 32 号（额定 137 N·m）一类", 24, INK)).arrange(DOWN, aligned_edge=LEFT).move_to([1.6, 1.3, 0])
        fit(eq, 7.5)
        self.play(LaggedStart(*[Write(m) for m in eq], lag_ratio=0.5), run_time=3.0)
        self.caption("还没有图纸，先用一根杆估力矩：量级对了，减速器的规格就能先定下来",
                     "Before any drawing, a single bar gives the torque; with the right order of magnitude the gearbox size can be fixed", wait=2.0)
        self.card([["设计任务书", "The design brief"],
                   ["负载 5 kg，臂展 0.86 m 一类：由工位的取放点和通用性定", "5 kg, 0.86 m class: set by the station's points and by versatility"],
                   ["关节 180°/s、360°/s²；重复定位 ±0.03 mm", "Joints 180°/s, 360°/s²; repeatability ±0.03 mm"],
                   MathTex(r"\tau_2 \approx \mathfrak g\,(m_p R + m_{arm} R/2)", font_size=40)])
