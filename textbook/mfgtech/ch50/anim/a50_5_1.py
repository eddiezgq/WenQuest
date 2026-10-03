"""动画 50.5.1（配图 50.5.1）：工序卡上的每一栏从哪里来——工序尺寸来自图纸、余量与尺寸链，转速与机动时间由切削用量算出，单件工时再加上辅助时间。"""
from manim import *
from wq_anim import *


class Lesson(Base):
    def construct(self):
        self.title("50.5", "工序卡上的数从哪里来", "Where the numbers on an operation sheet come from")
        heads = ["工序尺寸", "v_c", "f", "a_p", "n", "t_b", "单件工时"]
        cells = VGroup(*[Rectangle(width=1.7, height=0.75, stroke_color=INK) for _ in heads]).arrange(RIGHT, buff=0).shift(UP * 1.6)
        labels = VGroup(*[zh(h, 22).move_to(c.get_top() + UP * 0.3) for h, c in zip(heads, cells)])
        self.play(Create(cells), FadeIn(labels))
        self.caption("一张工序卡，一行一个工步", "One operation sheet, one row per step")
        src = [("图纸 Ø35 k6", 0), ("余量与尺寸链", 0), ("切削用量手册", 1), ("机床与刀具", 2), ("余量 ÷ 刀数", 3)]
        boxes = VGroup()
        for i, (t, k) in enumerate(src):
            b = VGroup(RoundedRectangle(width=2.3, height=0.6, corner_radius=0.1, stroke_color=STEEL), zh(t, 20, STEEL))
            b[1].move_to(b[0])
            b.move_to(DOWN * 1.4 + RIGHT * (-5 + 2.5 * i))
            boxes.add(b)
            self.play(FadeIn(b), GrowArrow(Arrow(b.get_top(), cells[k].get_bottom(), buff=0.1, color=MUTED)), run_time=0.6)
        vals = ["Ø41.5", "120", "0.3", "2.125"]
        for v, c in zip(vals, cells):
            self.play(Write(zh(v, 24).move_to(c)), run_time=0.4)
        self.caption("工序尺寸来自图纸、余量和尺寸链；切削用量查手册、按机床和刀具定", "Sizes come from the drawing, allowances and chains; cutting data from handbooks, machine and tool")
        n = MathTex(r"n=\frac{1000\,v_c}{\pi d}=\frac{1000\times120}{\pi\times50}\approx 764", font_size=34).shift(DOWN * 0.1)
        self.play(Write(n))
        self.play(Write(zh("764", 24).move_to(cells[4])))
        self.play(FadeOut(n))
        tb = MathTex(r"t_b=\sum\frac{L}{n f}\approx 1.09\ \mathrm{min}", font_size=34).shift(DOWN * 0.1)
        self.play(Write(tb))
        self.play(Write(zh("1.09", 24).move_to(cells[5])))
        self.caption("转速和机动时间不是凭经验填的，由切削用量算出来", "Speed and machining time are computed, not guessed")
        self.play(FadeOut(tb))
        tu = MathTex(r"t_c=t_b+t_a+t_s+t_r+\frac{t_{pz}}{N}", font_size=34).shift(DOWN * 0.1)
        self.play(Write(tu))
        self.play(Write(zh("18", 24).move_to(cells[6])))
        self.caption("单件工时再加上辅助时间和准备时间分摊：机动时间只占一小部分", "Add handling and a share of setup: machining is only a small part")
        self.card([["工序尺寸：图纸 + 余量 + 尺寸链", "Size: drawing + allowance + chains"],
                   ["n、t_b：由 v_c、f、a_p、L 算出", "n, t_b: computed from v_c, f, a_p, L"],
                   ["单件工时：t_b + 辅助 + 布置 + 休息 + 准终分摊", "Time per piece: t_b + handling + allowances + setup share"]])
