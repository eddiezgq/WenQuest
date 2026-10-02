"""动画 6.4.1（配图 6.4.1）：AGV 推料车。作用力与反作用力成对出现，分别作用在两个物体上；再加上地面对 AGV 的力。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("6.4", "作用力与反作用力", "Action and reaction")
        y = -0.8
        fl = ground(y=y, x0=-6.8, x1=6.8)
        A = agv(width=2.6, height=0.7, label="A").move_to(np.array([-1.8, y, 0]), aligned_edge=DOWN)
        cart = RoundedRectangle(width=2.0, height=0.55, corner_radius=0.05, color=GREY_B, fill_color=GREY_D, fill_opacity=1)
        wheels = VGroup(*[Circle(0.13, color=GREY_B, stroke_width=2) for _ in range(2)]).arrange(RIGHT, buff=1.3).next_to(cart, DOWN, buff=0)
        B = VGroup(cart, wheels, zh("B", 22, INK).move_to(cart)).next_to(A, RIGHT, buff=0.02).align_to(A, DOWN)
        self.play(Create(fl), FadeIn(A), FadeIn(B))
        self.caption("AGV（A）推着料车（B）一起向右加速", "The AGV (A) pushes the cart (B); both speed up to the right")
        contact = A.get_right() + UP * 0.75
        mark = DashedLine(A.get_right() + DOWN * 0.3, contact, color=MUTED, dash_length=0.08)
        self.play(Create(mark), run_time=0.4)
        pAB = vec(contact, contact + RIGHT * 1.3, RED, r"\boldsymbol F_{AB}", UP)
        self.play(GrowArrow(pAB[0]), Write(pAB[1]))
        self.caption("A 推 B：力作用在料车上", "A pushes B: this force acts on the cart")
        pBA = vec(contact, contact + LEFT * 1.3, RED, r"\boldsymbol F_{BA}", UP)
        self.play(GrowArrow(pBA[0]), Write(pBA[1]))
        self.caption("同时 B 推 A：大小相等、方向相反，作用在 AGV 上", "At the same time B pushes A: equal, opposite, acting on the AGV")
        self.play(FadeOut(mark), VGroup(A, pBA).animate.shift(LEFT * 1.2), VGroup(B, pAB).animate.shift(RIGHT * 1.2), run_time=1.2)
        self.caption("把两个物体分开画：一对力从不画在同一个物体上", "Draw the bodies apart: a pair never acts on the same body")
        wheel = A[1][0].get_bottom()
        f = vec(wheel + DOWN * 0.25, wheel + DOWN * 0.25 + RIGHT * 2.0, BLUE, r"\boldsymbol F_\mathrm{d}", RIGHT)
        self.play(GrowArrow(f[0]), Write(f[1]))
        self.caption("A 能加速，是因为地面向前推它的驱动轮，这个力比 B 对 A 的推力大", "A speeds up because the floor pushes its wheels forward harder than B pushes back")
        back = vec(wheel + DOWN * 0.75, wheel + DOWN * 0.75 + LEFT * 2.0, BLUE, r"-\boldsymbol F_\mathrm{d}", LEFT)
        self.play(GrowArrow(back[0]), Write(back[1]))
        self.caption("而驱动轮向后推地面：这又是一对作用力与反作用力", "And the wheels push the floor backwards: another action–reaction pair")
        self.wait(1)
        self.card([["牛顿第三定律", "Newton's third law"],
                   MathTex(r"\boldsymbol F_{AB} = -\boldsymbol F_{BA}", font_size=46),
                   ["同时产生，同一直线，同种性质，作用在两个物体上", "Simultaneous, collinear, same kind, on two different bodies"]])
