"""动画 7.6.1（配图 7.6.1）：WQR-105 中的力流——从电机经齿轮、轴、轴承到箱体和地脚螺栓。
数值与程序 7.6.1 相同（额定输出转矩 350 N·m；数字孪生的转矩、啮合力、轴承力模型；地脚螺栓沿箱长方向的中心距 450 mm 为本书设定）：
输入轴 36.1 N·m、中间轴 104.1 N·m、输出轴 350 N·m；第一级啮合力 1603 N、第二级 3694 N；
六个轴承 1135、467、2079、2990、2000、1694 N；箱体反力偶 314 N·m；每个地脚螺栓的力变化 349 N。
力偶的轴线与轴平行，所以俯视图里螺栓的力垂直于画面：一端两个拉力增加（⊙，指向读者），另一端两个拉力减小（⊗），哪一端增加取决于转向。"""
from manim import *
from wq_anim import *

Y_IN, Y_MID, Y_OUT = -1.7, -0.3, 1.3          # 三根轴（俯视，画面上从下到上）
X0, X1 = -3.4, 2.6


class Lesson(Base):
    def construct(self):
        self.title("7.6", "WQR-105 中的力流", "Force flow in the WQR-105")
        box = Rectangle(width=7.0, height=4.6, stroke_color=GREY_B, stroke_width=2).move_to([-0.6, -0.15, 0])
        shafts = VGroup(
            Line([X0 - 1.2, Y_IN, 0], [X1 - 0.6, Y_IN, 0], stroke_width=6, color=GREY_A),
            Line([X0, Y_MID, 0], [X1 - 0.6, Y_MID, 0], stroke_width=9, color=GREY_A),
            Line([X0, Y_OUT, 0], [X1 + 1.6, Y_OUT, 0], stroke_width=13, color=GREY_A))
        g12 = VGroup(Rectangle(width=0.35, height=0.7, fill_color=BLUE_D, fill_opacity=0.8, stroke_width=1).move_to([-2.4, Y_IN, 0]),
                     Rectangle(width=0.35, height=2.1, fill_color=BLUE_D, fill_opacity=0.8, stroke_width=1).move_to([-2.4, Y_MID, 0]))
        g34 = VGroup(Rectangle(width=0.35, height=0.72, fill_color=ORANGE, fill_opacity=0.8, stroke_width=1).move_to([-0.6, Y_MID, 0]),
                     Rectangle(width=0.35, height=2.48, fill_color=ORANGE, fill_opacity=0.8, stroke_width=1).move_to([-0.6, Y_OUT, 0]))
        motor = Rectangle(width=1.1, height=0.9, fill_color=GREY_D, fill_opacity=1, stroke_width=1).move_to([X0 - 1.8, Y_IN, 0])
        load = Rectangle(width=1.0, height=0.9, fill_color=GREY_D, fill_opacity=1, stroke_width=1).move_to([X1 + 2.1, Y_OUT, 0])
        self.play(Create(box), FadeIn(motor), FadeIn(load), *[Create(s) for s in shafts], FadeIn(g12), FadeIn(g34), run_time=1.5)
        self.caption("俯视：输入轴、中间轴、输出轴在同一平面；虚框是箱体", "Top view: input, intermediate and output shafts in one plane; the frame is the housing")

        def torque_tag(text_zh, text_en, pos, color):
            return bi([text_zh, text_en], size=20, color=color).move_to(pos)

        dot = Dot(color=YELLOW, radius=0.12).move_to(motor.get_center())
        self.add(dot)
        t_in = torque_tag("输入 36.1 N·m", "input 36.1 N·m", [X0 - 1.8, Y_IN + 0.85, 0], YELLOW)
        self.play(dot.animate.move_to([-2.4, Y_IN, 0]), FadeIn(t_in), run_time=1.2)
        self.caption("电机的转矩沿输入轴传到小齿轮——只有 36 N·m，轴最细", "The motor's torque runs along the input shaft to the pinion — only 36 N·m, the thinnest shaft")
        f12 = torque_tag("啮合力 1603 N", "mesh force 1603 N", [-1.2, Y_IN + 0.45, 0], BLUE_B)
        self.play(dot.animate.move_to([-2.4, Y_MID, 0]), FadeIn(f12), run_time=1.0)
        self.caption("在齿面上，转矩变成力：啮合力 = 2T/d", "At the tooth the torque becomes a force: mesh force = 2T/d")
        t_mid = torque_tag("中间轴 104.1 N·m", "intermediate 104.1 N·m", [0.75, Y_MID - 0.62, 0], YELLOW)
        self.play(dot.animate.move_to([-0.6, Y_MID, 0]), FadeIn(t_mid), run_time=1.0)
        f34 = torque_tag("啮合力 3694 N", "mesh force 3694 N", [0.75, Y_MID + 0.55, 0], ORANGE)
        self.play(dot.animate.move_to([-0.6, Y_OUT, 0]), FadeIn(f34), run_time=1.0)
        t_out = torque_tag("输出 350 N·m", "output 350 N·m", [X1 + 2.1, Y_OUT - 0.8, 0], YELLOW)
        self.play(dot.animate.move_to(load.get_center()), FadeIn(t_out), run_time=1.2)
        self.caption("每经过一级，转速降、转矩升：输出轴转矩是输入轴的 9.7 倍（10.5 倍减去效率损失），所以轴越来越粗", "Each stage lowers speed and raises torque: 9.7 times the input at the output (10.5 less the losses), so the shafts get thicker", wait=2)
        # 轴承
        brg = [([X0, Y_IN], 1135), ([X1 - 0.6, Y_IN], 467), ([X0, Y_MID], 2079), ([X1 - 0.6, Y_MID], 2990), ([-1.7, Y_OUT], 2000), ([0.9, Y_OUT], 1694)]
        squares = VGroup(*[Square(side_length=0.18 + 0.3 * f / 2990, fill_color=RED, fill_opacity=1, stroke_width=0).move_to([x, y, 0]) for (x, y), f in brg])
        tags = VGroup(*[Text(f"{f} N", font_size=16, color=RED_B).next_to(sq, DOWN, buff=0.05) for sq, (_, f) in zip(squares, brg)])
        self.play(FadeIn(squares, lag_ratio=0.15), FadeIn(tags, lag_ratio=0.15), run_time=1.5)
        self.caption("啮合力把轴推向一边，由两端的轴承顶住：轴承力 467–2990 N，中间轴的轴承 B 最大", "The mesh forces push each shaft sideways; the bearings at both ends hold it: 467–2990 N, largest at intermediate bearing B", wait=2)
        # 箱体与地脚螺栓
        self.play(box.animate.set_stroke(YELLOW, width=4), run_time=0.8)
        couple = bi(["箱体：合力为零\n只剩反力偶 314 N·m", "housing: zero net force,\na couple of 314 N·m"], size=22, color=YELLOW).move_to([5.0, -1.0, 0])
        self.play(FadeIn(couple))
        self.caption("啮合力是内力，各轴承传给箱体的力合起来为零；剩下的是输出转矩减输入转矩的力偶", "Mesh forces are internal: the bearing forces on the housing add up to zero, leaving a couple = output torque − input torque", wait=2)
        bolts = VGroup()
        for x in (-4.35, 3.15):
            for y, up in ((1.95, True), (-2.25, False)):
                c = Circle(radius=0.2, color=GREEN, stroke_width=4).move_to([x, y, 0])
                mark = Dot([x, y, 0], radius=0.07, color=GREEN) if up else VGroup(Line([x - 0.13, y - 0.13, 0], [x + 0.13, y + 0.13, 0], color=GREEN, stroke_width=4),
                                                                                    Line([x - 0.13, y + 0.13, 0], [x + 0.13, y - 0.13, 0], color=GREEN, stroke_width=4))
                bolts.add(VGroup(c, mark))
        self.play(FadeIn(bolts, lag_ratio=0.2))
        self.caption("最后由 4 个地脚螺栓传到机架：上方两个拉力增加（⊙），下方两个拉力减小（⊗），每个变化约 349 N", "Finally 4 foot bolts carry it to the frame: tension rises in the top two (⊙) and falls in the bottom two (⊗), by about 349 N each", wait=2)
        self.card([["力流：力从哪里进、从哪里出", "Force flow: where force enters and leaves"],
                   ["转矩 → 啮合力 → 轴 → 轴承 → 箱体 → 地脚螺栓", "torque → mesh force → shaft → bearings → housing → foot bolts"],
                   ["路径上每个零件都要按它分到的力设计", "every part on the path is designed for its share"],
                   ["力流短而直、在局部闭合，零件就小而硬", "a short, direct, locally closed path gives small, stiff parts"]])
