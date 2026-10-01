"""动画 4.1.2（配图 4.1.2）：两根坐标轴的单位矢量一同转过 θ，旋转矩阵两列的数值与箭头端点同步变化。"""
from manim import *
from wq_anim import *
import numpy as np
import math


class Lesson(Base):
    def construct(self):
        self.title("4.1", "旋转矩阵的两列", "The two columns of a rotation matrix")
        O = np.array([-3.2, -0.9, 0])
        L = 2.6
        base = VGroup(DashedLine(O, O + RIGHT * L * 1.15, color=GREY_B), DashedLine(O, O + UP * L * 1.15, color=GREY_B))
        self.play(Create(base))
        th = ValueTracker(0.0)

        def arrows():
            t = th.get_value()
            ex = O + L * np.array([math.cos(t), math.sin(t), 0])
            ey = O + L * np.array([-math.sin(t), math.cos(t), 0])
            g = VGroup(Arrow(O, ex, buff=0, color=RED, stroke_width=6), Arrow(O, ey, buff=0, color=GREEN, stroke_width=6),
                       MathTex(r"R\hat x", color=RED, font_size=32).next_to(ex, UR, buff=0.05),
                       MathTex(r"R\hat y", color=GREEN, font_size=32).next_to(ey, UL, buff=0.05))
            if t > 0.02:
                g.add(DashedLine(ex, [ex[0], O[1], 0], color=RED, stroke_width=2),
                      Arc(radius=0.7, start_angle=0, angle=t, arc_center=O, color=YELLOW))
            return g

        arr = always_redraw(arrows)
        self.add(arr)

        def mat():
            t = th.get_value()
            c, s = math.cos(t), math.sin(t)
            m = MathTex(r"R(\theta)=\begin{pmatrix}", "%.3f" % c, "&", "%.3f" % (-s), r"\\", "%.3f" % s, "&", "%.3f" % c,
                        r"\end{pmatrix}", font_size=40)
            for i in (1, 5):
                m[i].set_color(RED)
            for i in (3, 7):
                m[i].set_color(GREEN)
            g = VGroup(m, MathTex(r"\theta=%d^\circ" % round(math.degrees(t)), color=YELLOW, font_size=36))
            return g.arrange(DOWN, buff=0.4).move_to(np.array([3.4, 0.6, 0]))

        m = always_redraw(mat)
        self.add(m)
        self.caption("红：第一列，转动后的 x 轴；绿：第二列，转动后的 y 轴", "Red: column 1 = rotated x axis; green: column 2 = rotated y axis")
        self.play(th.animate.set_value(math.radians(30)), run_time=2.5)
        self.caption("第一列 = (cos θ, sin θ)：转动后 x 轴端点的坐标", "Column 1 = (cos θ, sin θ): the tip of the rotated x axis")
        self.play(th.animate.set_value(math.radians(75)), run_time=2.5)
        self.play(th.animate.set_value(math.radians(30)), run_time=2)
        self.caption("读一个旋转矩阵，就是读转动后的坐标轴指向何方", "Reading a rotation matrix = reading where the axes point")
        self.wait(1)
        self.card([["旋转矩阵的第 i 列", "Column i of a rotation matrix"],
                   MathTex(r"R(\theta)=\begin{pmatrix}\cos\theta & -\sin\theta\\ \sin\theta & \cos\theta\end{pmatrix}", font_size=44),
                   ["= 第 i 根坐标轴转动后在原坐标系中的分量", "= the i-th axis after rotation, in the original frame"]])
