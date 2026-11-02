"""动画 57.1.1（配图 57.1.2）：最小余量的组成（式 57.1.3）——以 SH-101 半精车、渗碳淬火后磨削为例：上道留下的粗糙度 Rz、
缺陷层 Hₐ、弯曲与变形 ρ 一层层叠起来，加上装夹误差 ε（两顶尖取 0），就是磨削要切掉的最小余量。厚度放大画出，数值取企业工艺标准
WQ-PS-01（教学示意值）：Rz 0.0125、Hₐ 0.05、ρ 0.10 mm，2Z_min = 0.325 mm。"""
from manim import *
from wq_anim import *
import numpy as np

K = 18.0                      # 1 mm 画成 18 单位（厚度放大）


class Lesson(Base):
    def construct(self):
        self.title("57.1", "最小余量由什么组成", "What the minimum stock is made of")
        x0, x1, y0 = -5.5, 5.5, -1.6
        core = Rectangle(width=x1 - x0, height=0.9, color=STEEL, fill_opacity=0.35).move_to(np.array([0, y0 - 0.45, 0]))
        lab = zh("磨后的表面 Ø25 k6（要得到的）", 22, WHITE).move_to(core)
        self.play(FadeIn(core), FadeIn(lab))
        layers = [(0.10, ORANGE, "ρ = 0.10：渗碳淬火的弯曲与变形", "ρ: distortion"), (0.05, RED, "Hₐ = 0.05：渗碳淬火的氧化、内氧化层", "Hₐ: oxidized layer"),
                  (0.0125, YELLOW, "Rz = 0.0125：半精车的粗糙度（Ra 3.2）", "Rz: roughness")]
        y = y0
        grp = VGroup()
        for t, c, z, e in layers:
            h = t * K
            if c == YELLOW:
                pts = [np.array([x0 + i * 0.25, y + (h if i % 2 else 0), 0]) for i in range(int((x1 - x0) / 0.25) + 1)]
                shape = VMobject(color=c, stroke_width=3).set_points_as_corners(pts)
            elif c == ORANGE:
                xs = np.linspace(x0, x1, 60)
                pts = [np.array([x, y + h * (0.5 + 0.5 * np.sin(np.pi * (x - x0) / (x1 - x0))), 0]) for x in xs]
                shape = VMobject(color=c, stroke_width=4).set_points_smoothly(pts)
            else:
                shape = Rectangle(width=x1 - x0, height=h, color=c, fill_opacity=0.45, stroke_width=1).move_to(np.array([0, y + h / 2, 0]))
            self.play(Create(shape), run_time=0.9)
            self.caption(z, e)
            grp.add(shape)
            y += h
        top = Line(np.array([x0, y, 0]), np.array([x1, y, 0]), color=WHITE)
        br = Brace(Line(np.array([x1 + 0.2, y0, 0]), np.array([x1 + 0.2, y, 0])), RIGHT, color=WHITE)
        self.play(Create(top), GrowFromCenter(br))
        r = zh("单边 Z_min = Rz + Hₐ + ρ = 0.1625", 22, WHITE).next_to(br, UP, buff=0.15).shift(LEFT * 1.6)
        self.play(FadeIn(r))
        self.caption("两顶尖装夹，装夹误差 ε 取 0；直径上 2Z_min = 2(Rz + Hₐ) + 2√(ρ² + ε²) = 0.325 mm",
                     "Between centres ε = 0; on diameter 2Z_min = 0.325 mm")
        self.card([["决定磨削余量的主要是热处理变形，而不是粗糙度", "Heat-treatment distortion, not roughness, sets the grinding stock"],
                   ["变形分散的零件，先实测一批再定 ρ", "Measure a batch before fixing ρ"]])
