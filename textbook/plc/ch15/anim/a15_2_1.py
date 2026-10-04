"""动画 15.2.1（配图 15.2.1、15.2.2）：一个压装循环——当前状态在状态转换图上依次移动，时序图上的信号同步逐段画出。
各段时间取自程序 15.3.1 在虚拟压装工位上的实测（夹紧 0.3 s、压装约 2.0 s、回程约 1.9 s、松开 0.3 s）。"""
from manim import *
from wq_anim import *


class Lesson(Base):
    def construct(self):
        self.title("15.2", "状态转换图与时序图", "State diagram and timing diagram")
        names = ["IDLE", "CLAMPING", "PRESSING", "RETURNING", "UNCLAMPING"]
        boxes = VGroup()
        for i, n in enumerate(names):
            r = RoundedRectangle(width=1.95, height=0.6, corner_radius=0.12, stroke_color=INK, stroke_width=2)
            t = Text(n, font=LATIN, font_size=16, color=INK)
            boxes.add(VGroup(r, t))
        boxes.arrange(RIGHT, buff=0.8).move_to(UP * 2.0)
        arrows = VGroup(*[Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.04, stroke_width=3, max_tip_length_to_length_ratio=0.35, color=MUTED) for i in range(4)])
        back = CurvedArrow(boxes[4].get_bottom() + DOWN * 0.02, boxes[0].get_bottom() + DOWN * 0.02, angle=-0.35, color=MUTED, stroke_width=3)
        conds = ["双手启动", "夹紧到位", "压到底", "上位"]
        clabels = VGroup(*[Text(c, font=CJK, font_size=14, color=MUTED).next_to(arrows[i], UP, buff=0.06) for i, c in enumerate(conds)])
        blabel = Text("松开到位", font=CJK, font_size=15, color=MUTED).next_to(back, DOWN, buff=0.05)
        self.play(LaggedStart(*[FadeIn(b) for b in boxes], lag_ratio=0.15), run_time=1.2)
        self.play(*[GrowArrow(a) for a in arrows], Create(back), FadeIn(clabels), FadeIn(blabel))
        self.caption("状态转换图：设备处于且只处于一个状态，条件满足就沿箭头转移", "State diagram: the machine is in exactly one state and moves along an arrow when its condition holds")

        # 时序图
        sigs = [("Y_Clamp", STEEL), ("B_Clamped", GREEN), ("Y_PressDown", ORANGE), ("B_PressDown", YELLOW), ("Y_PressUp", RED)]
        x0, x1, T = -4.6, 6.3, 5.4                       # 横轴 0–5.4 s
        sx = lambda t: x0 + (x1 - x0) * t / T
        y0, dy, hh = 0.3, -0.55, 0.32
        rows = VGroup()
        for k, (n, c) in enumerate(sigs):
            y = y0 + k * dy
            rows.add(Text(n, font=LATIN, font_size=16, color=c).move_to([x0 - 1.1, y + hh / 2, 0]))
            rows.add(DashedLine([x0, y, 0], [x1, y, 0], stroke_width=1, color=GREY_D))
        axis = Arrow([x0, y0 + 4 * dy - 0.25, 0], [x1 + 0.25, y0 + 4 * dy - 0.25, 0], buff=0, stroke_width=2, color=MUTED, max_tip_length_to_length_ratio=0.02)
        tl = Text("t / s", font=LATIN, font_size=15, color=MUTED).next_to(axis, RIGHT, buff=0.05)
        ticks = VGroup(*[Text(str(s), font=LATIN, font_size=13, color=MUTED).move_to([sx(s), y0 + 4 * dy - 0.48, 0]) for s in range(6)])
        self.play(FadeIn(rows), Create(axis), FadeIn(tl), FadeIn(ticks))

        # 每个信号为 1 的时间段（s）：0.2 s 双手启动
        t1, t2, t3, t4, t5 = 0.2, 0.5, 2.5, 4.4, 4.7
        on = {"Y_Clamp": [(t1, t4)], "B_Clamped": [(t2, t4 + 0.05)], "Y_PressDown": [(t2, t3)], "B_PressDown": [(t3, t3 + 0.08)], "Y_PressUp": [(t3, t4)]}
        phases = [(0, t1, 0), (t1, t2, 1), (t2, t3, 2), (t3, t4, 3), (t4, t5, 4), (t5, 5.4, 0)]
        say = {1: ("夹紧阀得电；夹紧到位开关一来，转入压装", "Clamp valve on; the clamped switch moves it on to pressing"),
               2: ("压头下行约 2 s，压到底：判定结果，转入回程", "The ram descends for about 2 s; at the bottom the result is judged and it returns"),
               3: ("上行阀得电，压头回到上位", "The up valve brings the ram back to the top"),
               4: ("夹紧阀断电，松开到位，回到等待", "Clamp off; unclamped, back to idle")}

        def level(n, t):
            return any(a <= t < b for a, b in on[n])

        hi = SurroundingRectangle(boxes[0], color=YELLOW, buff=0.06, stroke_width=4)
        cursor = Line([sx(0), y0 + 0.5, 0], [sx(0), y0 + 4 * dy - 0.2, 0], color=YELLOW, stroke_width=2)
        self.play(Create(hi), Create(cursor))
        for a, b, st in phases:
            self.play(hi.animate.move_to(boxes[st]), run_time=0.4)
            segs = VGroup()
            for k, (n, c) in enumerate(sigs):
                y = y0 + k * dy
                pts, t, step = [[sx(a), y + (hh if a > 0 and level(n, a - 1e-3) else 0), 0]], a, 0.02   # 段首补一个点，接上竖边
                while t <= b + 1e-9:
                    pts.append([sx(t), y + (hh if level(n, t) else 0), 0]); t += step
                segs.add(VMobject(stroke_color=c, stroke_width=3).set_points_as_corners(pts))
            dur = max(0.6, (b - a) * 0.9)
            self.play(Create(segs, lag_ratio=0), cursor.animate.move_to([sx(b), cursor.get_center()[1], 0]), run_time=dur, rate_func=linear)
            if st in say:
                self.caption(*say[st], wait=0.8)
        self.caption("时序图回答“什么时候”，状态转换图回答“在什么情况下变成什么”", "The timing diagram tells when; the state diagram tells what follows what, under which condition")
        self.card([["输出变化的时刻把时序图切成一段段状态", "The instants where outputs change cut the timing diagram into states"],
                   ["切开两个状态的那个输入变化，就是转移条件", "The input change between two states is the transition condition"]])
