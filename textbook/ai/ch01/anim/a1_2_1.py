"""动画 1.2.1（配图 1.2.2）：感知机在零件检验数据上逐次更新。每遇到一个判错的零件，该点闪烁，权重向量 w
加上（或减去）这个点的增广向量，分界线随之移动；更新次数累计，直到一整轮不再出错。
数据与学习规则同程序 1.2.1（code/_perceptron.py）：η = 1，从 w = 0 出发，按固定顺序循环。"""
from manim import *
from wq_anim import *
import numpy as np

PARTS = [
    (0.2, 0.4, 1), (0.6, 0.2, 1), (0.4, 1.2, 1), (1.0, 0.6, 1), (0.2, 1.8, 1), (1.4, 0.2, 1), (0.8, 1.0, 1),
    (0.0, 0.8, 1), (1.2, 1.0, 1), (0.6, 1.6, 1), (1.6, 0.4, 1), (0.2, 2.2, 1), (1.0, 1.2, 1), (0.4, 0.6, 1),
    (1.8, 0.0, 1),
    (2.6, 0.4, -1), (2.2, 1.0, -1), (1.6, 1.6, -1), (1.0, 2.4, -1), (0.4, 3.0, -1), (2.8, 1.8, -1), (1.8, 2.6, -1),
    (0.8, 3.4, -1), (3.0, 0.6, -1), (2.4, 2.4, -1), (1.2, 3.0, -1), (0.0, 3.4, -1), (2.6, 1.2, -1), (1.4, 2.0, -1),
    (2.0, 1.6, -1),
]


def learn():
    """返回每次更新的 (样本序号, 更新后的 w)。"""
    w = np.zeros(3)
    steps = []
    for _ in range(100):
        wrong = 0
        for i, (a, b, y) in enumerate(PARTS):
            x = np.array([a, b, 1.0])
            if y * (w @ x) <= 0:
                w = w + y * x
                steps.append((i, w.copy()))
                wrong += 1
        if wrong == 0:
            break
    return steps


class Lesson(Base):
    def construct(self):
        self.title("1.2", "感知机怎样学习", "How a perceptron learns")
        ax = Axes(x_range=[-0.2, 3.4, 1], y_range=[-0.2, 3.8, 1], x_length=5.4, y_length=6.0,
                  axis_config={"color": GREY_B, "include_numbers": True, "font_size": 20}).shift(LEFT * 2.2 + DOWN * 0.35)
        self.play(Create(ax), run_time=0.8)
        dots = VGroup()
        for a, b, y in PARTS:
            p = ax.c2p(a, b)
            if y > 0:
                dots.add(Circle(radius=0.09, color=BLUE, stroke_width=3).move_to(p))
            else:
                dots.add(Square(side_length=0.17, color=RED, fill_opacity=1, stroke_width=0).move_to(p))
        self.play(FadeIn(dots, lag_ratio=0.03), run_time=1.2)
        self.caption("圆点合格，方块不合格；横轴外径偏差，纵轴圆度误差（10 μm）",
                     "Circles accepted, squares rejected; diameter deviation vs roundness error (10 μm)")
        steps = learn()
        w = ValueTracker(0.0)
        state = {"w": np.zeros(3)}

        def boundary():
            a, c, b = state["w"]
            if abs(a) + abs(c) < 1e-9:
                return VGroup()
            pts = []
            for xx in (-0.2, 3.4):
                if abs(c) > 1e-9:
                    yy = -(a * xx + b) / c
                    if -0.2 <= yy <= 3.8:
                        pts.append((xx, yy))
            for yy in (-0.2, 3.8):
                if abs(a) > 1e-9:
                    xx = -(c * yy + b) / a
                    if -0.2 <= xx <= 3.4:
                        pts.append((xx, yy))
            if len(pts) < 2:
                return VGroup()
            line = Line(ax.c2p(*pts[0]), ax.c2p(*pts[1]), color=YELLOW, stroke_width=5)
            mid = (np.array(pts[0]) + np.array(pts[1])) / 2
            n = np.array([a, c]) / np.hypot(a, c)
            arr = Arrow(ax.c2p(*mid), ax.c2p(*(mid + 0.5 * n)), buff=0, color=YELLOW, stroke_width=5)
            return VGroup(line, arr)

        bnd = always_redraw(boundary)
        self.add(bnd)
        counter = VGroup(zh("更新次数", 26, GREY_A), Integer(0, font_size=40, color=YELLOW)).arrange(RIGHT, buff=0.3)
        counter.to_edge(RIGHT, buff=0.8).shift(UP * 1.6)
        wtxt = always_redraw(lambda: MathTex(r"\boldsymbol w = (%.0f,\ %.0f,\ %.0f)" % tuple(state["w"]),
                                             font_size=34).next_to(counter, DOWN, buff=0.5, aligned_edge=LEFT))
        rule = MathTex(r"\boldsymbol w \leftarrow \boldsymbol w + y\,\tilde{\boldsymbol x}", font_size=38, color=GREY_A)
        rule.next_to(counter, DOWN, buff=1.4, aligned_edge=LEFT)
        self.play(FadeIn(counter), FadeIn(rule))
        self.add(wtxt)
        self.caption("判错的零件出现时，w 加上 y x̃，分界线转向把它拉回正确的一侧",
                     "At each mistake, w gains y x̃ and the line turns to pull the part to the right side")
        for k, (i, wn) in enumerate(steps):
            ring = Circle(radius=0.22, color=GREEN, stroke_width=4).move_to(dots[i].get_center())
            fast = k >= 6
            self.play(Create(ring), run_time=0.12 if fast else 0.4)
            state["w"] = wn
            counter[1].set_value(k + 1)
            self.play(FadeOut(ring), w.animate.set_value(k + 1), run_time=0.18 if fast else 0.6)
        self.caption("一整轮不再出错：共 %d 次更新，30 个零件全部分对" % len(steps),
                     "A full epoch without mistakes: %d updates, all 30 parts correct" % len(steps), wait=1.0)
        self.card([["感知机学习规则与收敛定理", "The perceptron rule and its convergence theorem"],
                   MathTex(r"\boldsymbol w \leftarrow \boldsymbol w + \eta\, y_i\,\tilde{\boldsymbol x}_i", font_size=44),
                   MathTex(r"k \le (R/\gamma)^2", font_size=44)])
