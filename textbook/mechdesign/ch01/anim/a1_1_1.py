"""动画 1.1.1（配图 1.1.2）：WQR-105 二级圆柱齿轮减速器的展开示意——箱体打开、三根轴与四个齿轮，
电机带动输入轴，两级齿轮逐级降速、放大转矩；数字与算例 1.1.1 相同（4 kW、1450 r/min）。"""
from manim import *
from wq_anim import *
import numpy as np

# 示意尺寸（屏幕单位）：分度圆半径按齿数比例缩放
R1, R2, R3, R4 = 0.36, 1.08, 0.45, 1.58          # z = 24、72（m2），20、70（m3）
X1 = -4.2
X2 = X1 + R1 + R2
X3 = X2 + R3 + R4
Y = -0.4


def gear(r, color, n_teeth):
    g = VGroup(Circle(radius=r, color=color, fill_color=color, fill_opacity=0.35, stroke_width=3))
    for k in range(n_teeth):
        a = 2 * PI * k / n_teeth
        g.add(Line(r * np.array([np.cos(a), np.sin(a), 0]), (r + 0.08) * np.array([np.cos(a), np.sin(a), 0]), color=color, stroke_width=3))
    g.add(Line(ORIGIN, r * RIGHT, color=WHITE, stroke_width=2))
    return g


class Lesson(Base):
    def construct(self):
        self.title("1.1", "动力从电机到输出轴", "Power from the motor to the output shaft")
        box = RoundedRectangle(width=6.8, height=4.0, corner_radius=0.2, color=GREY_B).move_to([(X1 - R1 + X3 + R4) / 2, Y, 0])
        lid = box.copy().set_fill(GREY_D, opacity=0.9)
        self.play(FadeIn(box), FadeIn(lid))
        self.caption("WQR-105：箱座、箱盖和三根轴。打开箱盖看里面", "WQR-105: base, cover and three shafts. Lift the cover")
        self.play(lid.animate.shift(UP * 5).set_opacity(0), run_time=1.5)
        g1, g2, g3, g4 = gear(R1, BLUE, 12), gear(R2, BLUE_D, 36), gear(R3, ORANGE, 10), gear(R4, GOLD, 35)
        g1.move_to([X1, Y, 0]); g2.move_to([X2, Y, 0]); g3.move_to([X2, Y, 0]); g4.move_to([X3, Y, 0])
        self.play(FadeIn(g1), FadeIn(g2), FadeIn(g3), FadeIn(g4))
        labels = VGroup(
            bi(["输入轴 z = 24", "input, z = 24"], 20).next_to(g1, DOWN, buff=0.35),
            bi(["中间轴 z = 72 / 20", "intermediate, z = 72 / 20"], 20).next_to(g2, DOWN, buff=0.35),
            bi(["输出轴 z = 70", "output, z = 70"], 20).next_to(g4, DOWN, buff=0.15))
        self.play(FadeIn(labels))
        self.caption("第一级 72/24 = 3，第二级 70/20 = 3.5，总传动比 10.5", "Stage 1: 72/24 = 3; stage 2: 70/20 = 3.5; overall 10.5")
        # 转起来：角速度按传动比
        w1 = 2.4
        for g, w in ((g1, w1), (g2, -w1 / 3), (g3, -w1 / 3), (g4, w1 / 10.5)):
            g.c = g.get_center().copy()
            g.add_updater(lambda m, dt, w=w: m.rotate(w * dt, about_point=m.c))
        info = VGroup(
            MathTex(r"n:\ 1450 \rightarrow 483 \rightarrow 138\ \mathrm{r/min}", font_size=30, color=BLUE),
            MathTex(r"T:\ 26.1 \rightarrow 75.1 \rightarrow 252.5\ \mathrm{N\cdot m}", font_size=30, color=PURPLE_B),
            MathTex(r"P:\ 3.96 \rightarrow 3.80 \rightarrow 3.65\ \mathrm{kW}", font_size=30, color=GOLD)).arrange(DOWN, aligned_edge=LEFT).to_corner(UR).shift(DOWN * 0.6)
        self.caption("转速一级级降低，转矩一级级放大；功率在每对齿轮和轴承上损失一点", "Speed falls stage by stage and torque grows; a little power is lost at each gear mesh and bearing pair", wait=0)
        self.play(Write(info), run_time=2)
        self.wait(5)
        for g in (g1, g2, g3, g4):
            g.clear_updaters()
        self.card([["减速器：降速、增矩", "A reducer: less speed, more torque"],
                   MathTex(r"i=\frac{z_2}{z_1}\cdot\frac{z_4}{z_3},\qquad T=9550\,\frac{P}{n}", font_size=44),
                   ["总效率是各级效率之积：0.97² × 0.99³ ≈ 0.913", "Overall efficiency is the product of the stages: 0.97² × 0.99³ ≈ 0.913"]])
