"""动画 52.2.1（配图 52.2.5）：三爪卡盘夹薄壁套车内孔——夹紧时外圆被压成“三角形”，在变形状态下车圆的孔，
松开后工件弹回，孔变成三棱形（变形放大画出）。"""
from manim import *
from wq_anim import *
import numpy as np


class Lesson(Base):
    def construct(self):
        self.title("52.2", "薄壁件的夹紧变形", "Clamping distortion of a thin-walled sleeve")
        R_out, R_in = 2.2, 1.85
        c = np.array([-2.2, -0.3, 0])
        squeeze = ValueTracker(0.0)          # 0 自由，1 夹紧
        bored = ValueTracker(0.0)            # 0 未车，1 已在夹紧状态下车圆

        def w(th, s):
            # 三爪在 90°、210°、330°：径向位移以三阶为主（向内为负），放大画出
            return -0.22 * s * np.cos(3 * (th - PI / 2))

        def ring():
            s = squeeze.get_value()
            b = bored.get_value()
            th = np.linspace(0, TAU, 241)
            outer = [c + (R_out + w(t, s)) * np.array([np.cos(t), np.sin(t), 0]) for t in th]
            # 车削：在当前（夹紧）形状上把孔车成半径 R_in 的正圆；之后孔的形状 = 正圆 + （当前变形 − 车削时的变形）
            inner = []
            for t in th:
                if b < 0.5:
                    r = R_in + w(t, s)
                else:
                    r = R_in + w(t, s) - w(t, 1.0)
                inner.append(c + r * np.array([np.cos(t), np.sin(t), 0]))
            o = VMobject(color=INK, stroke_width=3).set_points_as_corners(outer)
            i = VMobject(color=ORANGE if b > 0.5 else INK, stroke_width=3).set_points_as_corners(inner)
            return VGroup(o, i)

        def jaws():
            s = squeeze.get_value()
            g = VGroup()
            for k in range(3):
                t = PI / 2 + k * TAU / 3
                d = np.array([np.cos(t), np.sin(t), 0])
                r = R_out + w(t, s) + 0.35
                jaw = Rectangle(width=0.7, height=0.55, color=STEEL, fill_opacity=0.6).rotate(t - PI / 2).move_to(c + r * d)
                g.add(jaw)
            return g

        rg = always_redraw(ring)
        jg = always_redraw(jaws)
        self.play(FadeIn(rg), FadeIn(jg))
        self.caption("薄壁套放进三爪卡盘，内外圆都是圆的", "A thin sleeve in a three-jaw chuck; bore and outside are round")
        self.play(squeeze.animate.set_value(1.0), run_time=2.5)
        self.caption("夹紧：三个爪把外圆压成“三角形”，内孔跟着变形（放大画出）", "Clamped: the jaws squeeze the sleeve into a rounded triangle (exaggerated)")
        self.play(bored.animate.set_value(1.0), run_time=1.0)
        self.caption("在变形状态下把内孔车成正圆（橙色）", "The bore is turned truly round while distorted (orange)")
        self.play(squeeze.animate.set_value(0.0), run_time=2.5)
        self.caption("松开卡爪，工件弹回：外圆恢复，孔反而变成三棱形", "Released, the sleeve springs back: the outside recovers, the bore is now three-lobed")
        note = VGroup(bi(["圆度误差与夹紧力成正比，与 EI 成反比", "Roundness error ∝ clamping force / EI"], size=24),
                      bi(["对策：扇形软爪、开缝套、轴向压紧端面", "Cures: soft jaws, split sleeve, end clamping"], size=24)).arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT).shift(LEFT * 0.3)
        self.play(FadeIn(note))
        self.card([["车削时发现不了：零件下了机床才显出三棱", "You cannot see it while turning: the lobes appear off the machine"],
                   ["夹紧后在加工面上放千分表，松开时看表针变化", "Put an indicator on the bore, release, and watch the needle"]])
