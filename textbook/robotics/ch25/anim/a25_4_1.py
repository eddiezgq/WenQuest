"""动画 25.4.1（配图 25.4.1）：一次逆动力学要做多少次乘法。数据取自程序 25.4.1（通用串联臂，不利用零元素）：
牛顿-欧拉递推 222n − 24 次；拉格朗日-欧拉的 4×4 矩阵写法 n = 1～10 依次为 417、1730、4644、10053、19040、32877、53025、81134、119043、168780 次。
纵轴是对数刻度：每升高一格，次数乘 10。n 从 1 增加到 10，递推的柱子匀速长高，拉格朗日-欧拉的柱子越长越快。
最后提到历史上的用时与今天的用时（几微秒，远小于 500 Hz 控制周期的 2 ms）。"""
from manim import *
from wq_anim import *
import numpy as np
import math

RN = [222 * n - 24 for n in range(1, 11)]
LE = [417, 1730, 4644, 10053, 19040, 32877, 53025, 81134, 119043, 168780]
O = np.array([-4.6, -1.9, 0])
DX = 0.95
YS = 0.82                                 # 每个数量级的高度


def h(v):
    return (math.log10(v) - 2) * YS       # 100 次在基线上


class Lesson(Base):
    def construct(self):
        self.title("25.4", "数一数：一次逆动力学要做多少次乘法", "Counting the multiplications in one inverse-dynamics call")
        self.add(Line(O + LEFT * 0.3, O + RIGHT * (10 * DX + 0.3), color=GREY_B, stroke_width=2))
        for k in range(2, 7):
            y = (k - 2) * YS
            self.add(DashedLine(O + UP * y + LEFT * 0.3, O + UP * y + RIGHT * (10 * DX + 0.3), color=GREY_D, stroke_width=1))
            self.add(MathTex(r"10^{%d}" % k, font_size=24, color=MUTED).next_to(O + UP * y + LEFT * 0.3, LEFT, buff=0.1))
        for n in range(1, 11):
            self.add(zh(str(n), 18, INK).move_to(O + RIGHT * (DX * (n - 0.5)) + DOWN * 0.25))
        self.add(zh("关节数 n", 18, MUTED).move_to(O + RIGHT * (DX * 5) + DOWN * 0.6))
        self.add(VGroup(Square(0.2, color=BLUE, fill_opacity=0.9), bi(["牛顿-欧拉递推", "recursive Newton–Euler"], 18, BLUE)).arrange(RIGHT, buff=0.15)
                 .move_to([4.6, 2.2, 0]))
        self.add(VGroup(Square(0.2, color=RED, fill_opacity=0.9), bi(["拉格朗日-欧拉（4×4 矩阵）", "Lagrange–Euler (4×4 matrices)"], 18, RED))
                 .arrange(RIGHT, buff=0.15).move_to([4.6, 1.5, 0]))
        self.caption("同一台通用的串联臂，两种写法算同一组关节力矩：结果相同，运算次数差得很远",
                     "One general serial arm, two ways to the same joint torques: same answer, very different amounts of work", wait=0.5)
        for n in range(1, 11):
            x = O + RIGHT * (DX * (n - 0.5))
            b1 = Rectangle(width=0.3, height=h(RN[n - 1]), color=BLUE, fill_color=BLUE, fill_opacity=0.85, stroke_width=0)
            b1.move_to(x + LEFT * 0.17 + UP * h(RN[n - 1]) / 2)
            b2 = Rectangle(width=0.3, height=h(LE[n - 1]), color=RED, fill_color=RED, fill_opacity=0.85, stroke_width=0)
            b2.move_to(x + RIGHT * 0.17 + UP * h(LE[n - 1]) / 2)
            anims = [GrowFromEdge(b1, DOWN), GrowFromEdge(b2, DOWN)]
            if n in (1, 6, 10):
                anims.append(FadeIn(zh(f"{RN[n - 1]}", 14, BLUE).next_to(b1, UP, buff=0.05).shift(LEFT * 0.12)))
                anims.append(FadeIn(zh(f"{LE[n - 1]}", 14, RED).next_to(b2, UP, buff=0.05).shift(RIGHT * 0.15)))
            self.play(*anims, run_time=0.45)
        self.caption("递推：每加一个关节多 222 次，与 n 成正比；拉格朗日-欧拉：随 n 的四次方增长，n = 6 时已是 25 倍",
                     "Recursion: 222 more per joint, proportional to n; Lagrange–Euler grows like n⁴ and is already 25 times as much at n = 6", wait=2.5)
        self.caption("1980 年，卢、沃克、保罗的递推程序在 PDP-11/45 上算斯坦福臂只要 4.5 ms；今天的普通计算机算 UR5e 只要几微秒",
                     "In 1980 Luh, Walker and Paul's recursion took 4.5 ms on a PDP-11/45 for the Stanford arm; today an ordinary computer does the UR5e in a few microseconds", wait=2.5)
        self.card([["计算量", "The cost"],
                   MathTex(r"\text{RNEA: } 222n - 24 \quad\text{multiplications}", font_size=38),
                   MathTex(r"\text{Lagrange--Euler: } \tfrac{63}{8}n^4 + \cdots", font_size=38),
                   ["递推让动力学能在每个控制周期里实时计算", "Recursion lets the dynamics be computed in every control cycle"]])
