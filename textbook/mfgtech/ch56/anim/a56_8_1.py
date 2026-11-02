"""动画 56.8.1（配图 56.8.1）：工序分散与工序集中——一批 SH-101 在锯床、数控车床（两道）、滚齿机、键槽铣床、热处理炉、
外圆磨床、检验站之间流转，与把粗车、精车和铣键槽集中到一台车铣复合中心上；数一数装夹和工序间搬运的次数（取自算例 56.8.1：
装夹 7 次与 4 次、搬运 7 次与 5 次；检验站另计）。"""
from manim import *
from wq_anim import *
import numpy as np

A = ["锯床", "数控车床\n粗车", "数控车床\n精车", "滚齿机", "键槽铣床", "热处理炉", "外圆磨床", "检验"]
B = ["锯床", "车铣复合\n车 + 键槽", "滚齿机", "热处理炉", "外圆磨床", "检验"]
SET_A = [1, 2, 1, 1, 1, 0, 1, 0]      # 各工作中心的装夹次数（粗车调头 2 次；热处理装炉、检验不计），合计 7
SET_B = [1, 1, 1, 0, 1, 0]            # 车铣复合中心用副主轴接件，一次装夹完成车和铣键槽，合计 4


def row(names, y, color):
    n = len(names)
    xs = np.linspace(-5.6, 5.6, n)
    g = VGroup()
    for x, t in zip(xs, names):
        b = RoundedRectangle(width=1.35, height=0.95, corner_radius=0.1, color=color, stroke_width=3).move_to(np.array([x, y, 0]))
        lab = zh(t, 18, WHITE).move_to(b)
        g.add(VGroup(b, lab))
    return g, xs


class Lesson(Base):
    def construct(self):
        self.title("56.8", "工序分散与工序集中", "Dispersed vs concentrated operations")
        ga, xa = row(A, 1.3, STEEL)
        gb, xb = row(B, -1.4, GREEN)
        la = zh("A 工序分散（现有设备）", 24, STEEL).move_to(np.array([-4.2, 2.4, 0]))
        lb = zh("B 工序集中（车铣复合中心）", 24, GREEN).move_to(np.array([-4.0, -0.3, 0]))
        self.play(FadeIn(ga), FadeIn(la))
        self.play(FadeIn(gb), FadeIn(lb))
        self.caption("同一根 SH-101，两种组织方式", "The same SH-101, organized two ways")
        def counter(sv, mv, y):
            return zh(f"装夹 {sv}   搬运 {mv}", 22, YELLOW).move_to(np.array([3.8, y, 0]))

        ta, tb = counter(0, 0, 2.4), counter(0, 0, -0.3)
        self.play(FadeIn(ta), FadeIn(tb))
        pa = Square(0.32, color=ORANGE, fill_opacity=1).move_to(np.array([xa[0], 0.55, 0]))
        pb = Square(0.32, color=ORANGE, fill_opacity=1).move_to(np.array([xb[0], -2.15, 0]))
        self.play(FadeIn(pa), FadeIn(pb))
        sa = sb = na = nb = 0
        for k in range(len(A)):
            anims = []
            if k > 0:
                na += 1
                anims.append(pa.animate.move_to(np.array([xa[k], 0.55, 0])))
            sa += SET_A[k]
            anims.append(Transform(ta, counter(sa, na, 2.4)))
            if k < len(B):
                if k > 0:
                    nb += 1
                    anims.append(pb.animate.move_to(np.array([xb[k], -2.15, 0])))
                sb += SET_B[k]
                anims.append(Transform(tb, counter(sb, nb, -0.3)))
            self.play(*anims, run_time=0.8)
            self.play(Indicate(ga[k], color=YELLOW), *([Indicate(gb[k], color=YELLOW)] if k < len(B) else []), run_time=0.5)
        self.caption("A：装夹 7 次、搬运 7 次；B：装夹 4 次、搬运 5 次", "A: 7 set-ups, 7 moves; B: 4 set-ups, 5 moves")
        self.card([["工序集中：装夹少、位置精度高、在制品少，但机床贵", "Concentration: fewer set-ups, better positional accuracy, less WIP — costlier machines"],
                   ["工序分散：设备简单、便于平衡节拍，但装夹、搬运多", "Dispersion: simple machines, easy balancing — more set-ups and moves"]])
