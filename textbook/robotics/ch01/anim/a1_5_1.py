"""动画 1.5.1（配图 1.5.1）：AGV 在数字工厂车间完成输出轴 SH-301 的七次搬运。

车间布置、上下料点和路线与工厂仿真相同（factory/digital/wqbus/layout.py 的 LAYOUT、dock、route），这里抄出坐标（m，y 轴向下）。
每次搬运：行驶 L / 1.0 m/s，装、卸各 30 s；屏幕上累计路程与时间。
"""
from manim import *
from wq_anim import *
import numpy as np
import math

UNITS = {"store-01": (3, 4, 4, 5, "原料库", "raw store"), "saw-01": (10, 4, 4, 2.5, "带锯床", "saw"),
         "cnc-l01-a": (17, 4, 4, 2.2, "车床 A", "lathe A"), "cnc-l01-b": (24, 4, 4, 2.2, "车床 B", "lathe B"),
         "key-01": (31, 4, 3, 2.2, "键槽铣", "keyway"), "ht-01": (17, 13, 5, 4, "热处理", "furnace"),
         "grd-01": (31, 13, 4.5, 2.2, "外圆磨", "grinder"), "qc-01": (38, 13, 4, 3, "检验站", "inspection"),
         "vmc-01": (10, 22, 3.5, 3, "立加", "VMC"), "hmc-01": (17, 22, 4.5, 3.5, "卧加", "HMC"),
         "hob-01": (24, 22, 3.5, 2.5, "滚齿机", "hobber"), "asm-01": (31, 22, 5, 3, "装配", "assembly"),
         "test-01": (38, 22, 3.5, 2.5, "跑合", "run-in"), "store-02": (45, 22, 4, 5, "成品库", "store")}
PATHS = [("带锯床 → 车床 A", [(10, 6.25), (10, 9.0), (17, 9.0), (17, 6.1)]),
         ("车床 A → 热处理", [(17, 6.1), (17, 9.0), (7.0, 9.0), (7.0, 18.5), (17, 18.5), (17, 16.0)]),
         ("热处理 → 车床 B", [(17, 16.0), (17, 18.5), (7.0, 18.5), (7.0, 9.0), (24, 9.0), (24, 6.1)]),
         ("车床 B → 键槽铣", [(24, 6.1), (24, 9.0), (31, 9.0), (31, 6.1)]),
         ("键槽铣 → 外圆磨", [(31, 6.1), (31, 9.0), (7.0, 9.0), (7.0, 18.5), (31, 18.5), (31, 15.1)]),
         ("外圆磨 → 检验站", [(31, 15.1), (31, 18.5), (38, 18.5), (38, 15.5)]),
         ("检验站 → 成品库", [(38, 15.5), (38, 18.5), (45, 18.5)])]
K = 0.2


def P(x, y):
    return np.array([-5.0 + K * x, 2.3 - K * y, 0])


def length(path):
    return sum(math.dist(p, q) for p, q in zip(path, path[1:]))


class Lesson(Base):
    def construct(self):
        self.title("1.5", "数字工厂：一根输出轴的搬运", "Digital factory: moving one output shaft")
        floor = Rectangle(width=50 * K, height=25 * K, color=GREY_B, stroke_width=2, fill_color="#1b2530", fill_opacity=1)
        floor.move_to((P(0, 0) + P(50, 25)) / 2)
        aisles = VGroup(*[Rectangle(width=49 * K, height=2 * K, stroke_width=0, fill_color="#2c3a48", fill_opacity=1)
                          .move_to(P(25, y)) for y in (9.0, 18.5)],
                        Rectangle(width=2 * K, height=9.5 * K, stroke_width=0, fill_color="#2c3a48", fill_opacity=1).move_to(P(7, 13.75)))
        units = VGroup()
        for key, (x, y, w, d, z, e) in UNITS.items():
            box = Rectangle(width=w * K, height=d * K, color=GREY_A, stroke_width=1.5,
                            fill_color="#41536a" if key.startswith("store") else "#24303c", fill_opacity=1).move_to(P(x, y))
            units.add(VGroup(box, zh(z, 13, INK).move_to(P(x, y))))
        self.play(FadeIn(floor), FadeIn(aisles), LaggedStart(*[FadeIn(u) for u in units], lag_ratio=0.05), run_time=1.6)
        self.caption("车间 50 m × 28 m；AGV 只在灰色通道中行驶", "Workshop 50 m × 28 m; AGVs drive only in the aisles", wait=1.0)

        agv_dot = Square(side_length=0.22, color=ORANGE, fill_color=ORANGE, fill_opacity=1).move_to(P(*PATHS[0][1][0]))
        self.play(FadeIn(agv_dot, scale=1.5))
        total_L, total_t = 0.0, 0.0
        board = VGroup(zh("第 0 次", 22, YELLOW), MathTex(r"L = 0\ \mathrm{m}", font_size=30), MathTex(r"t = 0\ \mathrm{s}", font_size=30))
        board.arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UR, buff=0.45).shift(DOWN * 0.15)
        self.add(board)
        self.caption("输出轴 SH-301：七道工序，七次搬运", "Output shaft SH-301: seven operations, seven moves", wait=0)
        for k, (name, path) in enumerate(PATHS):
            pts = [P(*p) for p in path]
            trail = VMobject(color=YELLOW, stroke_width=3).set_points_as_corners(pts)
            L = length(path)
            total_L += L
            total_t += L / 1.0 + 60
            new = VGroup(zh(f"第 {k + 1} 次：{name}", 20, YELLOW),
                         MathTex(r"L = %.1f\ \mathrm{m}" % total_L, font_size=30),
                         MathTex(r"t = %.0f\ \mathrm{s}" % total_t, font_size=30))
            new.arrange(DOWN, aligned_edge=LEFT, buff=0.12).to_corner(UR, buff=0.45).shift(DOWN * 0.15)
            self.play(Transform(board, new), run_time=0.3)
            self.play(Create(trail), MoveAlongPath(agv_dot, trail), run_time=0.6 + 0.025 * L, rate_func=linear)
            self.play(trail.animate.set_stroke(opacity=0.35), agv_dot.animate.scale(1.25), run_time=0.2)
            self.play(agv_dot.animate.scale(0.8), run_time=0.1)
        self.caption("共 189.5 m、约 10 min，其中装卸占 7 min", "189.5 m and about 10 min in all; 7 min of it is loading and unloading", wait=2)
        self.card([["搬运时间", "Transport time"],
                   MathTex(r"t = \frac{L}{v} + 2\,t_{\text{load}}", font_size=44),
                   ["距离近时，交接比行驶更费时间", "for short hops, hand-over costs more than driving"]])
