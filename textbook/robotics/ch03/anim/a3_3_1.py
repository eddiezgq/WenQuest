"""动画 3.3.1（配图 3.3.1）：{b} 相对 {a} 转动，x_b 与 {a} 三根轴的夹角变化，方向余弦矩阵第一列同步更新，平方和始终为 1。"""
from manim import *
from wq_anim import *
import numpy as np
import math

O = np.array([-3.2, -1.2, 0])
SC = 2.4


class Lesson(Base):
    def construct(self):
        self.title("3.3", "方向余弦矩阵", "The direction cosine matrix")
        P = lambda p: proj3(p, O, SC)
        fa = frame3(O, np.eye(3), length=1.0, labels=(r"\hat{\boldsymbol x}_a", r"\hat{\boldsymbol y}_a", r"\hat{\boldsymbol z}_a"), scale=SC)
        fa.set_opacity(0.45)
        self.play(FadeIn(fa), run_time=0.8)
        psi = ValueTracker(0.0)
        phi = ValueTracker(0.0)

        def Rb():
            return rot_z(math.degrees(psi.get_value())) @ rot_y(math.degrees(phi.get_value()))   # wq_anim 的 rot_z、rot_y 以度为单位

        def frame_b():
            R = Rb()
            g = frame3(O, R, length=1.0, labels=(r"\hat{\boldsymbol x}_b", r"\hat{\boldsymbol y}_b", r"\hat{\boldsymbol z}_b"), scale=SC)
            xb = R[:, 0]
            for i, col in enumerate((RED, GREEN, BLUE)):          # x_b 的端点向 {a} 三根轴作垂线：垂足到原点的有向长度 = cos α_i1
                foot = np.zeros(3)
                foot[i] = xb[i]
                g.add(DashedLine(P(xb), P(foot), color=col, stroke_width=2, dash_length=0.08))
                g.add(Dot(P(foot), radius=0.05, color=col))
            return g

        def column():
            R = Rb()
            c = R[:, 0]
            m = MathTex(r"\begin{pmatrix}" + r"\\".join("%.3f" % v for v in c) + r"\end{pmatrix}", font_size=40)
            lab = MathTex(r"\cos\alpha_{11}", r"\\", r"\cos\alpha_{21}", r"\\", r"\cos\alpha_{31}", font_size=32)
            lab[0].set_color(RED)
            lab[2].set_color(GREEN)
            lab[4].set_color(BLUE)
            top = VGroup(lab, MathTex("=", font_size=40), m).arrange(RIGHT, buff=0.25)
            s = MathTex(r"\cos^2\alpha_{11}+\cos^2\alpha_{21}+\cos^2\alpha_{31} = %.3f" % float(c @ c), font_size=30, color=YELLOW)
            ang = MathTex(r"(\psi,\ \varphi) = (%d^\circ,\ %d^\circ)" % (round(math.degrees(psi.get_value())), round(math.degrees(phi.get_value()))),
                          font_size=30, color=GREY_B)
            return VGroup(bi(["R_ab 的第一列 = x_b 在 {a} 中的分量", "Column 1 of R_ab = x_b written in {a}"], 24, WHITE),
                          top, s, ang).arrange(DOWN, buff=0.3).move_to(np.array([3.4, 0.4, 0]))

        fb = always_redraw(frame_b)
        col = always_redraw(column)
        self.add(fb, col)
        self.caption("{b} 与 {a} 重合：第一列是 (1, 0, 0)", "{b} coincides with {a}: column 1 is (1, 0, 0)")
        self.caption("绕 z 轴转：x_b 离开 x_a，向 y_a 靠拢", "Turn about z: x_b leaves x_a and approaches y_a", wait=0)
        self.play(psi.animate.set_value(math.radians(50)), run_time=3, rate_func=smooth)
        self.caption("再绕自身 y 轴转：x_b 离开水平面，第三个余弦不再为零", "Then about its own y axis: x_b leaves the horizontal plane, the third cosine is no longer zero", wait=0)
        self.play(phi.animate.set_value(math.radians(-40)), run_time=3, rate_func=smooth)
        self.caption("虚线是投影：垂足的位置就是三个方向余弦", "Dashed lines are projections: the feet give the three cosines", wait=0)
        self.play(psi.animate.set_value(math.radians(-25)), phi.animate.set_value(math.radians(30)), run_time=4, rate_func=smooth)
        self.wait(0.5)
        self.card([["方向余弦矩阵", "Direction cosine matrix"],
                   MathTex(r"(R_{ab})_{ij} = \cos\alpha_{ij} = \hat{\boldsymbol e}^{a}_{i}\cdot\hat{\boldsymbol e}^{b}_{j}", font_size=42),
                   ["第 j 列：{b} 的第 j 根轴在 {a} 中的分量", "Column j: axis j of {b} written in {a}"],
                   MathTex(r"p_a = R_{ab}\,p_b,\qquad R_{ab}^{\mathsf T}R_{ab} = I", font_size=42)])
