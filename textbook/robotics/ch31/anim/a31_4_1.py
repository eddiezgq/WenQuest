"""动画 31.4.1（配图 31.4.1）：把材料放到外面去。
(1) 同样重的实心杆和薄壁管（截面积相同）：管的惯性矩是实心杆的约 15 倍，端部受同样的力，弯得少得多。
(2) 拓扑优化（问渠 CAE 的平面 SIMP“悬臂梁”算例，大臂做成一块板，材料用量 30%，左边固定在 J2 上、右端中点受向下的力）：
    材料从均匀的灰色一步步向上下两边和斜撑聚集，长成桁架。密度场取程序 31.4.1 同一个算例的粗网格版本（48 × 10）。"""
from manim import *
from wq_anim import *
import numpy as np

# 问渠 CAE topo.run("cantilever") 的结果（48 × 10 的粗网格，0–9 表示密度）
D = ['999999999999999998888888888888887655431100000000', '333333334444456463111111111111465312455531100000',
     '000000000013562026200000000002632520011355542100', '000000000126620002620000000026200252000011245542',
     '000000002564100000362000000262000025200000011256', '000000136520000000036200002630000002520000001454',
     '000002563100000000003620026300000000252000126521', '000136520000000000001362263000000000025201463100',
     '765674222111111112222256641111111111113535520000', '999999999999999999999999877777777777777663100000']


class Lesson(Base):
    def construct(self):
        self.title("31.4", "把材料放到外面去", "Put the material on the outside")
        # (1) 实心杆与薄壁管：截面积相同
        solid = Circle(radius=0.62, color=STEEL, fill_opacity=0.8).move_to([-4.5, 1.2, 0])
        tube = VGroup(Circle(radius=1.736, color=STEEL, fill_opacity=0.8), Circle(radius=1.622, color=BG, fill_opacity=1, stroke_width=0)).move_to([-0.6, 1.2, 0])
        self.play(FadeIn(solid), FadeIn(tube))
        t1 = VGroup(zh("实心杆 Ø25", 22, INK).next_to(solid, DOWN), zh("薄壁管 Ø70×2.3（一样重）", 22, INK).next_to(tube, DOWN))
        self.play(FadeIn(t1))
        ratio = VGroup(zh("惯性矩 I：实心杆 1，薄壁管约 15", 26, YELLOW), zh("同样的力，管的挠度只有实心杆的约 1/15", 24, INK)).arrange(DOWN, aligned_edge=LEFT).move_to([4.2, 1.3, 0])
        fit(ratio, 5.5)
        self.play(Write(ratio), run_time=1.5)
        self.caption("弯曲时离中性轴越远的材料出力越大：I 与半径的三次方成正比", "In bending the material far from the neutral axis does the work: I grows with the cube of the radius", wait=1.5)
        self.clear_stage()
        # (2) 拓扑优化
        ny, nx = len(D), len(D[0])
        c = 0.24
        o = np.array([-nx * c / 2, ny * c / 2 - 0.3, 0])
        cells = VGroup()
        dens = []
        for j in range(ny):
            for i in range(nx):
                sq = Square(side_length=c, stroke_width=0, fill_color=WHITE, fill_opacity=0.3).move_to(o + np.array([(i + 0.5) * c, -(j + 0.5) * c, 0]))
                cells.add(sq)
                dens.append(int(D[j][i]) / 9.0)
        self.play(FadeIn(cells), run_time=0.8)
        wall = Line(o, o + DOWN * ny * c, color=BLUE, stroke_width=6)
        tip = o + np.array([nx * c, -ny * c / 2, 0])
        F = Arrow(tip + UP * 0.1, tip + DOWN * 1.4, color=RED, buff=0)
        self.play(Create(wall), GrowArrow(F))
        self.caption("大臂做成一块板：左边固定在 J2 上、右端（J3）受向下的力，只许用 30% 的材料", "The upper arm as a plate: fixed to J2 on the left, loaded at J3 on the right, only 30 % material", wait=1.0)
        s = ValueTracker(0.0)
        for sq, d in zip(cells, dens):
            sq.add_updater(lambda m, d=d: m.set_fill(WHITE, opacity=0.3 + (d - 0.3) * s.get_value()))
        self.play(s.animate.set_value(1.0), run_time=4.0, rate_func=smooth)
        for sq in cells:
            sq.clear_updaters()
        self.caption("材料长到上下两边，中间留斜撑：一个桁架——和薄壁管、工字梁是同一个道理",
                     "Material gathers along the top and bottom with braces between: a truss, the same idea as a tube or an I-beam", wait=1.5)
        self.card([["材料与轻量化", "Materials and lightweight design"],
                   ["铝和钢的比刚度几乎一样；碳纤维管是铝的两倍多", "Al and steel have nearly the same specific stiffness; CFRP twice as much"],
                   ["加大直径、减薄壁厚：同样重，更硬", "Bigger diameter, thinner wall: stiffer for the same weight"],
                   ["协作臂的轻量化先从关节模组下手", "A cobot's weight savings start with the joint modules"]])
