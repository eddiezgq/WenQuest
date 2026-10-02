"""动画 33.2.1（配图 33.2.1）：输出轴的装配顺序。零件从两端依次装上，看出为什么轴“中间粗、两头细”。"""
from manim import *
from wq_anim import *
import numpy as np

S = 0.045                    # 屏幕单位 / mm
SEG = [(35, 37), (40, 53), (48, 10), (42, 15), (35, 17), (35, 40), (30, 72)]
Z0 = -122 * S                # 轴左端的屏幕 x


def zx(z):
    return Z0 + z * S


class Lesson(Base):
    def construct(self):
        self.title("33.2", "轴上零件怎样装上去", "How the parts go onto the shaft")
        segs = VGroup()
        z = 0
        for d, L in SEG:
            segs.add(Rectangle(width=L * S, height=d * S, color=GREY_B, fill_color="#3b4b5a", fill_opacity=1,
                               stroke_width=2).move_to([zx(z + L / 2), 0.4, 0]))
            z += L
        axis = DashedLine([zx(-10), 0.4, 0], [zx(254), 0.4, 0], color=MUTED, stroke_width=1.5)
        self.play(Create(axis), LaggedStart(*[FadeIn(s) for s in segs], lag_ratio=0.15), run_time=2)
        self.caption("B 版输出轴：Ø35–Ø40–Ø48–Ø42–Ø35–Ø30，轴环在齿轮右侧", "Rev. B output shaft; the collar sits right of the gear")

        def part(w, h_in, h_out, color, label=None):
            top = Rectangle(width=w * S, height=(h_out - h_in) / 2 * S, color=WHITE, fill_color=color, fill_opacity=1, stroke_width=1.5)
            bot = top.copy()
            top.shift(UP * (h_in + h_out) / 4 * S)
            bot.shift(DOWN * (h_in + h_out) / 4 * S)
            g = VGroup(top, bot)
            return g

        # 从左端装：齿轮（越过 Ø35，推到 Ø40 上靠轴环）
        gear = part(55, 40, 130, "#d29922")
        gear.move_to([zx(-60), 0.4, 0])
        lab = zh("齿轮", 24, "#d29922").next_to(gear, UP, buff=0.1)
        self.play(FadeIn(gear), FadeIn(lab))
        self.caption("① 齿轮从左端套入：孔 Ø40 能越过 Ø35 的轴段，一直推到轴环", "① The gear slides on from the left over Ø35 until it meets the collar")
        self.play(gear.animate.move_to([zx(35 + 27.5), 0.4, 0]), lab.animate.move_to([zx(62.5), 0.4 + 3.6 * S * 12, 0]), run_time=2)
        sleeve = part(18, 35, 46, "#7ee787").move_to([zx(-40), 0.4, 0])
        self.play(FadeIn(sleeve))
        self.caption("② 套筒：把齿轮压在轴环上，也给左轴承定位", "② The sleeve holds the gear against the collar and locates the left bearing")
        self.play(sleeve.animate.move_to([zx(17 + 9), 0.4, 0]), run_time=1.5)
        brgL = part(17, 35, 72, "#58a6ff").move_to([zx(-30), 0.4, 0])
        self.play(FadeIn(brgL))
        self.caption("③ 左轴承（6207）最后装，靠在套筒上", "③ The left bearing (6207) goes on last, against the sleeve")
        self.play(brgL.animate.move_to([zx(8.5), 0.4, 0]), run_time=1.5)
        # 从右端装
        brgR = part(17, 35, 72, "#58a6ff").move_to([zx(290), 0.4, 0])
        self.play(FadeIn(brgR))
        self.caption("④ 右轴承从右端套入：越过 Ø30、Ø35 密封段，靠在 Ø42 轴肩上", "④ The right bearing comes from the right and stops at the Ø42 shoulder")
        self.play(brgR.animate.move_to([zx(123.5), 0.4, 0]), run_time=2)
        cpl = part(70, 30, 62, "#c48ac9").move_to([zx(300), 0.4, 0])
        self.play(FadeIn(cpl))
        self.caption("⑤ 轴承盖、密封装进箱体后，最后装联轴器", "⑤ After the bearing cap and seal, the coupling goes on")
        self.play(cpl.animate.move_to([zx(209), 0.4, 0]), run_time=1.5)
        arrows = VGroup(Arrow([zx(-20), -2.4, 0], [zx(80), -2.4, 0], color=YELLOW, buff=0),
                        Arrow([zx(260), -2.4, 0], [zx(140), -2.4, 0], color=YELLOW, buff=0))
        self.play(GrowArrow(arrows[0]), GrowArrow(arrows[1]))
        self.caption("零件从两端往中间装：直径必须从中间向两端逐级减小", "Parts go on from both ends, so the diameters must step down towards the ends", wait=2)
        self.card([["轴的结构设计", "Shaft layout"],
                   ["每个零件都要装得上、拆得下、定得住位", "Every part must go on, come off, and stay located"],
                   ["中间粗、两头细；每个台阶都有用处", "Thick in the middle, thin at the ends; every step has a job"]])
