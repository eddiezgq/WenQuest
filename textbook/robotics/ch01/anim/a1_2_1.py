"""动画 1.2.1（配图 1.2.1）：机器人发展年表逐条展开。

时间轴分两段：1900 年以前压缩（约 2200 年画成 4 个单位），1900 年以后展开（约 126 年画成 8.4 个单位）。
颜色表示线索：自动机与程序（棕）、反馈与控制（绿）、工业机器人（蓝）、智能与移动（红）。
"""
from manim import *
from wq_anim import *
import numpy as np

COL = {"auto": "#c8a24a", "ctrl": "#3fb950", "ind": "#58a6ff", "ai": "#ff7b72"}
EVENTS = [
    (-250, "浮子调节的水钟", "float-regulated water clock", "ctrl"),
    (60, "希罗的“编程”小车", "Hero's programmed cart", "auto"),
    (1088, "水运仪象台", "Su Song's clock tower", "auto"),
    (1804, "穿孔卡片织机", "punched-card loom", "auto"),
    (1868, "麦克斯韦《论调速器》", "Maxwell: On Governors", "ctrl"),
    (1920, "《罗素姆万能机器人》", "R.U.R.", "ind"),
    (1948, "《控制论》、机器乌龟", "Cybernetics, robot tortoises", "ctrl"),
    (1961, "第一台 Unimate", "first Unimate", "ind"),
    (1969, "斯坦福机械臂", "Stanford Arm", "ind"),
    (1973, "WABOT-1", "WABOT-1", "ai"),
    (2000, "达芬奇手术系统", "da Vinci surgical system", "ai"),
    (2008, "协作机器人 UR5", "cobot UR5", "ind"),
    (2023, "视觉-语言-动作模型", "vision-language-action models", "ai"),
]
Y0 = -0.15


def xpos(year):
    if year < 1900:
        return -6.3 + (year + 300) / 2200 * 4.0
    return -2.3 + (year - 1900) / 126 * 8.6


class Lesson(Base):
    def construct(self):
        self.title("1.2", "从自动机到具身智能", "From automata to embodied intelligence")
        axis = VGroup(Line([-6.4, Y0, 0], [-2.4, Y0, 0], color=GREY_B, stroke_width=3),
                      Line([-2.2, Y0, 0], [6.4, Y0, 0], color=GREY_B, stroke_width=3),
                      Line([-2.45, Y0 - 0.15, 0], [-2.35, Y0 + 0.15, 0], color=GREY_B),
                      Line([-2.25, Y0 - 0.15, 0], [-2.15, Y0 + 0.15, 0], color=GREY_B))
        ticks = VGroup()
        for y, s in ((-300, "-300"), (1000, "1000"), (1900, "1900"), (1950, "1950"), (2000, "2000"), (2026, "2026")):
            ticks.add(Text(s, font=LATIN, font_size=16, color=MUTED).move_to([xpos(y) + (0.12 if y == 1900 else 0), Y0 - 0.32, 0]))
        self.play(Create(axis), FadeIn(ticks))
        self.caption("时间轴：1900 年以前压缩，1900 年以后展开", "The axis is compressed before 1900, expanded after")
        heights = [1.0, 1.95, -0.95, -1.75]
        shown = VGroup()
        for k, (year, z, e, th) in enumerate(EVENTS):
            x = xpos(year)
            h = heights[k % 4]
            dot = Dot([x, Y0, 0], radius=0.09, color=COL[th])
            yr = ("约前 %d" % -year) if year < 0 else ("约 %d" % year if year < 1000 else str(year))
            lab = VGroup(zh(yr, 17, COL[th]), zh(z, 18, WHITE), en(e, 13)).arrange(DOWN, buff=0.04)
            lab.move_to([np.clip(x, -5.6, 5.6), Y0 + h, 0])
            # 竖线只画到标签边缘；标签加底色并放在上层，别的事件的竖线从它后面穿过，不压字
            y_end = lab.get_bottom()[1] - 0.04 if h > 0 else lab.get_top()[1] + 0.04
            stem = Line([x, Y0, 0], [x, y_end, 0], color=COL[th], stroke_width=2)
            lab.add_to_back(BackgroundRectangle(lab, color=BG, fill_opacity=1, buff=0.04))
            lab.set_z_index(2)
            g = VGroup(dot, stem, lab)
            shown.add(g)
            if year == 1961:
                self.caption("1961 年：第一台工业机器人进入通用汽车工厂", "1961: the first industrial robot starts work at GM", wait=0)
            elif year == 2000:
                self.caption("机器人走出工厂：手术、家庭、物流", "Robots leave the factory: surgery, homes, logistics", wait=0)
            self.play(FadeIn(dot, scale=2), Create(stem), FadeIn(lab, shift=UP * 0.1 * np.sign(h)), run_time=0.9)
            if year == 1868:
                self.caption("程序与机器分离，反馈闭合了回路", "Programs separate from machines; feedback closes the loop", wait=0.6)
        self.wait(1.0)
        legend = VGroup(*[VGroup(Dot(radius=0.07, color=COL[k]), zh(t, 16, INK)).arrange(RIGHT, buff=0.1)
                          for k, t in (("auto", "自动机与程序"), ("ctrl", "反馈与控制"), ("ind", "工业机器人"), ("ai", "智能与移动"))])
        legend.arrange(RIGHT, buff=0.5).to_edge(UP, buff=1.25).shift(RIGHT * 2.2)
        self.play(FadeIn(legend))
        self.caption("截至 2025 年末，全球在役工业机器人约 500 万台", "By the end of 2025, about 5 million industrial robots were in operation", wait=2)
        self.card([["四条线索", "Four threads"],
                   ["自动机与程序：同一台机器，换程序就做另一件事", "automata: change the program, change the task"],
                   ["反馈与控制：依据测量调整动作", "feedback: act on measurements"],
                   ["工业机器人：精确、可靠、可重复编程", "industrial robots: precise, reliable, reprogrammable"],
                   ["智能与学习：应付没有事先规定的情况", "intelligence: cope with what was not foreseen"]])
