"""动画 2.5.1（配图 2.5.1）：算例 2.5.1 的计算图。先从左到右计算每个节点的值，再从右到左传回梯度：
每经过一个节点，上游传来的梯度乘以该节点的局部导数；到达 w、b 时得到参数的梯度。数值与程序 2.5.1 相同。"""
from manim import *
from wq_anim import *
import math

XV, WV, BV, YV = 1.5, 0.8, -0.3, 1.0


class Lesson(Base):
    def construct(self):
        self.title("2.5", "反向传播：梯度沿计算图流回", "Backpropagation: gradients flow back through the graph")
        zv = WV * XV + BV
        pv = 1 / (1 + math.exp(-zv))
        Lv = (pv - YV) ** 2
        dLdp = 2 * (pv - YV)
        dpdz = pv * (1 - pv)
        dLdz = dLdp * dpdz
        pos = {"w": [-5.6, 1.6, 0], "x": [-5.6, 0.2, 0], "b": [-5.6, -1.2, 0], "u": [-3.2, 0.9, 0], "z": [-0.9, 0.2, 0],
               "p": [1.5, 0.2, 0], "L": [3.9, 0.2, 0]}
        names = {"w": "w", "x": "x", "b": "b", "u": "wx", "z": "z", "p": "p", "L": "L"}
        nodes = {}
        for k, pnt in pos.items():
            box = RoundedRectangle(width=1.25, height=0.75, corner_radius=0.12, color=BLUE if k in "wxb" else GOLD,
                                   fill_opacity=0.15, stroke_width=2.5).move_to(pnt)
            nodes[k] = VGroup(box, MathTex(names[k], font_size=34).move_to(pnt))
        edges = [("w", "u"), ("x", "u"), ("u", "z"), ("b", "z"), ("z", "p"), ("p", "L")]
        arrows = VGroup(*[Arrow(nodes[a][0].get_right(), nodes[b][0].get_left(), buff=0.08, stroke_width=3, color=GREY_B)
                          for a, b in edges])
        self.play(*[FadeIn(n) for n in nodes.values()], Create(arrows), run_time=1.2)
        self.caption("计算图：每个节点是一次简单运算", "The computational graph: each node is one simple operation")
        vals = {"w": WV, "x": XV, "b": BV, "u": WV * XV, "z": zv, "p": pv, "L": Lv}
        vt = {}
        for k in ["w", "x", "b", "u", "z", "p", "L"]:
            vt[k] = DecimalNumber(vals[k], num_decimal_places=4, font_size=24, color=WHITE).next_to(nodes[k], UP, buff=0.12)
        self.play(*[FadeIn(vt[k]) for k in "wxb"], run_time=0.6)
        self.caption("前向：从左到右算出每个节点的值", "Forward: compute each node's value from left to right")
        for k in ["u", "z", "p", "L"]:
            self.play(Indicate(nodes[k][0], color=YELLOW), FadeIn(vt[k], shift=UP * 0.1), run_time=0.7)
        grads = {"L": 1.0, "p": dLdp, "z": dLdz, "u": dLdz, "b": dLdz, "w": dLdz * XV, "x": dLdz * WV}
        local = {"p": r"\frac{\partial L}{\partial p} = 2(p - y)", "z": r"\frac{\partial p}{\partial z} = p(1-p)",
                 "u": r"\frac{\partial z}{\partial (wx)} = 1", "b": r"\frac{\partial z}{\partial b} = 1",
                 "w": r"\frac{\partial (wx)}{\partial w} = x", "x": r"\frac{\partial (wx)}{\partial x} = w"}
        gt = {}
        self.caption("反向：从 L 出发，∂L/∂L = 1", "Backward: start at L with ∂L/∂L = 1")
        gt["L"] = DecimalNumber(1.0, num_decimal_places=4, font_size=24, color=RED).next_to(nodes["L"], DOWN, buff=0.12)
        self.play(FadeIn(gt["L"]))
        self.caption("每经过一个节点：上游梯度 × 局部导数", "At each node: upstream gradient × local derivative")
        for k, frm in (("p", "L"), ("z", "p"), ("u", "z"), ("b", "z"), ("w", "u"), ("x", "u")):
            eq = MathTex(local[k], font_size=32, color=GREY_A).to_edge(RIGHT, buff=0.5).shift(UP * 2.4)
            dot = Dot(nodes[frm][0].get_left(), color=RED, radius=0.09)
            gt[k] = DecimalNumber(grads[k], num_decimal_places=4, font_size=24, color=RED).next_to(nodes[k], DOWN, buff=0.12)
            self.play(FadeIn(eq), FadeIn(dot), run_time=0.4)
            self.play(dot.animate.move_to(nodes[k][0].get_right()), run_time=0.7)
            self.play(FadeIn(gt[k]), FadeOut(dot), FadeOut(eq), run_time=0.5)
        self.caption("到达参数：∂L/∂w = %.4f，∂L/∂b = %.4f" % (grads["w"], grads["b"]),
                     "At the parameters: dL/dw = %.4f, dL/db = %.4f" % (grads["w"], grads["b"]), wait=2.0)
        self.card([["链式法则，从输出往回乘", "The chain rule, multiplied back from the output"],
                   MathTex(r"\frac{\partial L}{\partial w} = \frac{\partial L}{\partial p}\,\frac{\partial p}{\partial z}\,\frac{\partial z}{\partial (wx)}\,\frac{\partial (wx)}{\partial w}", font_size=40)])
