"""动画 2.3.1（配图 2.3.3）：同一支箭头在两套坐标系里。坡道上 AGV 的重力 W 竖直向下，长度不变；坐标系从水平—竖直
转到沿坡—垂直坡面（转过 α），两个分量随之改变，读数显示分量和由分量算出的大小，大小始终不变。"""
from manim import *
from wq_anim import *
import numpy as np

W = 3.0                      # 画面中 W 的长度


class Lesson(Base):
    def construct(self):
        self.title("2.3", "同一支箭头，两套分量", "One arrow, two sets of components")
        al = ValueTracker(0.0)
        o = np.array([-2.0, 1.0, 0])
        Wv = vec(o, o + DOWN * W, RED, r"\boldsymbol W", LEFT)

        def axes():
            t = np.radians(al.get_value())
            ex, ey = np.array([np.cos(t), np.sin(t), 0]), np.array([-np.sin(t), np.cos(t), 0])
            return VGroup(Arrow(o - 2.2 * ex, o + 2.8 * ex, buff=0, color=GREY_B, stroke_width=3),
                          Arrow(o - 3.6 * ey, o + 1.6 * ey, buff=0, color=GREY_B, stroke_width=3),
                          MathTex("x'", font_size=30, color=GREY_B).move_to(o + 3.1 * ex),
                          MathTex("y'", font_size=30, color=GREY_B).move_to(o + 1.9 * ey))

        def comps():
            t = np.radians(al.get_value())
            ex, ey = np.array([np.cos(t), np.sin(t), 0]), np.array([-np.sin(t), np.cos(t), 0])
            w = DOWN * W
            px, py = np.dot(w, ex) * ex, np.dot(w, ey) * ey
            g = VGroup(DashedLine(o + w, o + px, color=GREY_C, stroke_width=2), DashedLine(o + w, o + py, color=GREY_C, stroke_width=2))
            if np.linalg.norm(px) > 0.05:
                g.add(Arrow(o, o + px, buff=0, color=BLUE, stroke_width=6, max_tip_length_to_length_ratio=0.3))
            g.add(Arrow(o, o + py, buff=0, color=GREEN, stroke_width=6, max_tip_length_to_length_ratio=0.15))
            return g

        def numbers():
            t = np.radians(al.get_value())
            wx, wy = -np.sin(t), -np.cos(t)          # 以 mg 为单位
            return VGroup(MathTex(r"\alpha = %.0f^\circ" % al.get_value(), font_size=34),
                          MathTex(r"W_{x'} = %.3f\,mg" % wx, font_size=34, color=BLUE),
                          MathTex(r"W_{y'} = %.3f\,mg" % wy, font_size=34, color=GREEN),
                          MathTex(r"\sqrt{W_{x'}^2+W_{y'}^2} = %.3f\,mg" % np.hypot(wx, wy), font_size=34, color=RED)
                          ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_edge(RIGHT, buff=0.6).shift(UP * 0.4)

        ax = always_redraw(axes)
        cp = always_redraw(comps)
        nb = always_redraw(numbers)
        self.play(Create(ax), GrowArrow(Wv[0]), FadeIn(Wv[1]))
        self.add(cp, nb)
        self.caption("水平—竖直坐标系：重力只有竖直分量", "Level axes: gravity has only a vertical component")
        self.caption("坐标轴转动，箭头不动", "The axes turn; the arrow stays", wait=0)
        self.play(al.animate.set_value(20), run_time=3)
        self.caption("沿坡分量 −mg sin α 出现了，长度始终是 mg", "An along-slope component −mg sin α appears; the length stays mg")
        self.play(al.animate.set_value(-35), run_time=3)
        self.caption("反向转：分量变号，长度仍不变", "Turning the other way flips the sign; the length is unchanged")
        self.play(al.animate.set_value(20), run_time=2)
        self.wait(1)
        self.card([["矢量与坐标系无关", "A vector does not depend on the axes"],
                   ["坐标系一转，分量就变；箭头和它的长度不变", "Turn the axes and the components change; the arrow and its length do not"],
                   MathTex(r"A_{x'} = A_x\cos\alpha + A_y\sin\alpha,\quad A_{y'} = -A_x\sin\alpha + A_y\cos\alpha", font_size=36)])
