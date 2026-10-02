"""动画 5.4.1（配图 5.4.1）：工作站的坐标系树逐层长出；从 {c} 到 {t} 的路径先向上到 {w}，再向下到 {t}，矩阵依次排成乘积。"""
from manim import *
from wq_anim import *
import numpy as np


def node(text_zh, pos, color=STEEL):
    t = zh(text_zh, 24, INK)
    box = RoundedRectangle(width=max(1.9, t.width + 0.4), height=0.6, corner_radius=0.12, color=color,
                           fill_color=NAVY, fill_opacity=0.9, stroke_width=3)
    return VGroup(box, t).move_to(pos)


def edge(a, b, color=GREY_B, width=3):
    return Arrow(a.get_bottom(), b.get_top(), buff=0.05, color=color, stroke_width=width, max_tip_length_to_length_ratio=0.15)


class Lesson(Base):
    def construct(self):
        self.title("5.4", "坐标系树", "A tree of frames")
        P = {"w": [0, 2.0, 0], "s": [-2.6, 1.0, 0], "c": [2.6, 1.0, 0], "L": [-2.6, 0.0, 0], "b": [-2.6, -1.0, 0],
             "t": [-2.6, -2.0, 0], "o": [2.6, 0.0, 0]}
        names = {"w": "{w} 工作台", "s": "{s} 基座", "c": "{c} 相机", "L": "连杆 0 … 6", "b": "{b} 法兰",
                 "t": "{t} 工具", "o": "{o} 工件"}
        N = {k: node(v, P[k]) for k, v in names.items()}
        E = {("w", "s"): edge(N["w"], N["s"]), ("w", "c"): edge(N["w"], N["c"]), ("s", "L"): edge(N["s"], N["L"]),
             ("L", "b"): edge(N["L"], N["b"]), ("b", "t"): edge(N["b"], N["t"]), ("c", "o"): edge(N["c"], N["o"])}
        self.play(FadeIn(N["w"]))
        self.caption("根：工作台坐标系 {w}", "The root: the worktable frame {w}", wait=0.8)
        self.play(GrowArrow(E[("w", "s")]), GrowArrow(E[("w", "c")]), FadeIn(N["s"]), FadeIn(N["c"]))
        self.play(GrowArrow(E[("s", "L")]), FadeIn(N["L"]), GrowArrow(E[("c", "o")]), FadeIn(N["o"]))
        self.play(GrowArrow(E[("L", "b")]), FadeIn(N["b"]))
        self.play(GrowArrow(E[("b", "t")]), FadeIn(N["t"]))
        self.caption("每个坐标系只记一个位姿：相对它的父坐标系", "Each frame stores one pose: relative to its parent")

        self.play(*[n[0].animate.set_stroke(YELLOW) for n in (N["c"], N["t"])])
        self.caption("问：从相机看，工具在哪里？", "Question: where is the tool, seen from the camera?", wait=1.0)
        terms = [r"T_{ct}", "=", r"T_{wc}^{-1}", r"T_{ws}", r"T_{s0}\cdots T_{6b}", r"T_{bt}"]
        formula = MathTex(*terms, font_size=40).to_edge(RIGHT, buff=0.6).shift(DOWN * 1.6)
        self.play(Write(formula[0:2]))
        up = Arrow(N["c"].get_top() + LEFT * 0.3, N["w"].get_right() + DOWN * 0.1, buff=0.05, color=RED, stroke_width=7)
        self.play(GrowArrow(up), Write(formula[2].set_color(RED)))
        self.caption("向上一步：从子走到父，乘这条边的逆", "One step up, child to parent: multiply by the inverse", wait=1.0)
        steps = [(("w", "s"), 3), (("s", "L"), 4), (("L", "b"), 4), (("b", "t"), 5)]
        for (k, i) in steps:
            anims = [E[k].animate.set_color(RED).set_stroke(width=7)]
            if k != ("L", "b"):
                anims.append(Write(formula[i].set_color(RED)))
            self.play(*anims, run_time=0.8)
        self.caption("向下各步：从父走到子，乘这条边本身", "Steps down, parent to child: multiply by the edge itself", wait=1.2)
        self.caption("路径唯一：先上到最近公共祖先 {w}，再下到 {t}", "The path is unique: up to the common ancestor {w}, then down to {t}")
        self.card([["任意两个坐标系之间的位姿", "The pose between any two frames"],
                   MathTex(r"T_{ab} = T_{ra}^{-1}\,T_{rb}", font_size=46),
                   ["沿树中唯一的路径相乘：向上乘逆，向下乘本身", "multiply along the unique path: inverse going up, the edge itself going down"]])
