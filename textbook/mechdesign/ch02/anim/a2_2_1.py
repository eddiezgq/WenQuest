"""动画 2.2.1（配图 2.2.1）：从总功能到分功能，再到形态矩阵——每行选一个解法，组成一个方案（Go2 充电桩对接机构）。"""
from manim import *
from wq_anim import *

FUNCS = [(["走到桩前", "approach"], [["视觉标记", "visual marker"], ["红外信标", "IR beacon"], ["导引条", "guide strip"]]),
         (["消除误差", "absorb error"], [["V 形导槽", "V-guide"], ["浮动板", "floating plate"], ["锥销", "taper pin"]]),
         (["接通电流", "make contact"], [["弹簧顶针", "spring pins"], ["刀片触点", "blade contacts"], ["无线感应", "inductive"]]),
         (["保持接触", "hold"], [["自重", "own weight"], ["永磁", "magnet"], ["卡扣", "latch"]])]
PICKS = {"A": ([0, 0, 0, 0], BLUE), "C": ([1, 0, 2, 0], RED)}


class Lesson(Base):
    def construct(self):
        self.title("2.2", "从功能到方案", "From functions to concepts")
        top = bi(["总功能：让机器人与充电桩可靠地接通电流", "overall function: connect the robot to the dock reliably"], 26).to_edge(UP, buff=1.1)
        self.play(FadeIn(top))
        self.caption("先不想“它长什么样”，只问“它要做哪些事”", "Don't ask what it looks like; ask what it must do")
        rows = VGroup()
        for k, (f, opts) in enumerate(FUNCS):
            y = 1.0 - k * 1.05
            head = VGroup(RoundedRectangle(width=2.6, height=0.8, corner_radius=0.1, color=BLUE_B, fill_opacity=0.15),
                          bi(f, 22)).move_to([-4.6, y, 0])
            head[1].move_to(head[0])
            cells = VGroup()
            for j, o in enumerate(opts):
                c = VGroup(RoundedRectangle(width=2.3, height=0.8, corner_radius=0.1, color=GREY_B), bi(o, 20)).move_to([-1.9 + j * 2.5, y, 0])
                c[1].move_to(c[0])
                cells.add(c)
            rows.add(VGroup(head, cells))
        self.play(LaggedStart(*[FadeIn(r[0], shift=RIGHT * 0.3) for r in rows], lag_ratio=0.2))
        self.caption("分解成分功能：动词加名词，不提结构", "Split into sub-functions: verb + noun, no hardware yet")
        self.play(LaggedStart(*[FadeIn(r[1]) for r in rows], lag_ratio=0.2))
        self.caption("每个分功能列出几种解法：这就是形态矩阵（3 × 3 × 3 × 3 = 81 种组合）", "List solutions for each: the morphological matrix (3 × 3 × 3 × 3 = 81 combinations)")
        for name, (pick, col) in PICKS.items():
            marks = VGroup(*[SurroundingRectangle(rows[k][1][j], color=col, buff=0.06, stroke_width=5) for k, j in enumerate(pick)])
            path = VMobject(color=col, stroke_width=4).set_points_as_corners([rows[k][1][j].get_center() for k, j in enumerate(pick)])
            lab = Text(name, font_size=34, color=col, weight=BOLD).next_to(rows[0][1][pick[0]], UP, buff=0.15).shift(RIGHT * 0.9)
            self.play(Create(marks), Create(path), FadeIn(lab), run_time=1.5)
            self.caption("每行选一个：方案 {}".format(name), "One per row: concept {}".format(name), wait=1)
            self.play(FadeOut(path))
        self.wait(1)
        self.card([["形态矩阵", "Morphological matrix"],
                   ["行：分功能；列：解法；每行选一个 = 一个方案", "Rows: sub-functions; columns: solutions; one per row = one concept"],
                   ["排除不相容的组合，再用普氏矩阵和加权评分比较（2.4 节）", "Drop incompatible pairs, then compare with Pugh and weighted scoring (Section 2.4)"]])
