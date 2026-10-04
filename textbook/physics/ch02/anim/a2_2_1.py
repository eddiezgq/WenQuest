"""动画 2.2.1（配图 2.2.1）：矢量的加法与减法。a、b 首尾相接得 a + b；换个次序先走 b 再走 a，到达同一个顶点，
两条路线围成平行四边形，所以 a + b = b + a；最后把 a、b 的起点放在一起，a − b 是从 b 的终点指向 a 的终点。"""
from manim import *
from wq_anim import *
import numpy as np

O = np.array([-3.2, -1.6, 0])
A = np.array([3.4, 0.9, 0])
B = np.array([1.0, 2.2, 0])


class Lesson(Base):
    def construct(self):
        self.title("2.2", "矢量的加法与减法", "Adding and subtracting vectors")
        a = vec(O, O + A, BLUE, r"\boldsymbol a", DOWN)
        b = vec(O, O + B, GREEN, r"\boldsymbol b", LEFT)
        self.play(GrowArrow(a[0]), FadeIn(a[1]), GrowArrow(b[0]), FadeIn(b[1]))
        self.caption("两个矢量：大臂 a 和小臂 b", "Two vectors: the upper arm a and the forearm b")
        b2 = vec(O + A, O + A + B, GREEN, r"\boldsymbol b", RIGHT)
        self.play(TransformFromCopy(b, b2), run_time=1.2)
        r = vec(O, O + A + B, RED, r"\boldsymbol a+\boldsymbol b", UP + LEFT)
        self.caption("首尾相接：从 a 的起点指向 b 的终点，就是 a + b", "Head to tail: from the start of a to the end of b is a + b", wait=0)
        self.play(GrowArrow(r[0]), FadeIn(r[1]))
        self.wait(1.2)
        a2 = vec(O + B, O + A + B, BLUE, r"\boldsymbol a", UP)
        self.caption("换个次序：先走 b 再走 a，到达同一个顶点", "The other order: b first, then a, reaches the same corner", wait=0)
        self.play(TransformFromCopy(a, a2), run_time=1.2)
        par = Polygon(O, O + A, O + A + B, O + B, color=YELLOW, fill_opacity=0.12, stroke_width=0)
        self.play(FadeIn(par))
        self.caption("两条路线围成平行四边形：a + b = b + a", "The two routes make a parallelogram: a + b = b + a")
        self.play(FadeOut(par), FadeOut(a2), FadeOut(b2), FadeOut(r))
        d = vec(O + B, O + A, ORANGE, r"\boldsymbol a-\boldsymbol b", UP + RIGHT)
        self.caption("减法：起点放在一起，a − b 从 b 的终点指向 a 的终点", "Subtraction: with a common start, a − b runs from the end of b to the end of a", wait=0)
        self.play(GrowArrow(d[0]), FadeIn(d[1]))
        self.wait(1.0)
        chk = MathTex(r"\boldsymbol b+(\boldsymbol a-\boldsymbol b)=\boldsymbol a", font_size=36).to_edge(RIGHT, buff=0.6).shift(UP * 1.2)
        self.play(Write(chk))
        self.caption("因为 b 再加上 a − b，正好回到 a", "because b followed by a − b lands on a", wait=1.5)
        self.card([["矢量的加法与减法", "Adding and subtracting vectors"],
                   ["加法：首尾相接，或平行四边形的对角线", "Addition: head to tail, or the parallelogram diagonal"],
                   ["a + b = b + a；a − b 从 b 的终点指向 a 的终点", "a + b = b + a; a − b runs from the end of b to the end of a"]])
