"""动画 11.6.1（配图 11.6.1）：雨流计数怎样把一段杂乱的载荷拆成一个个循环。
载荷取 WQ-CR5 标准动作一个节拍里 J3 处反力矩的大小 |M|（程序 11.10.1 的同一条记录，只留转折点，四舍五入到 0.1 N·m）：
39.1、42.5、35.2、45.1、38.9、49.7、29.4、48.2、44.2、45.9、40.4、41.7（N·m）。
步骤：① 载荷不断重复，从最大值处切开、首尾相接（数字工厂 fatigue.closed_block）；② 三点法：连续三个转折点 A、B、C，
若 |B − C| ≥ |A − B|，A–B 就是一个闭合的循环，记下幅值和平均值，把 A、B 去掉；③ 最后剩下最大值到最小值的那个大循环。
数字工厂用 pyLife 的四点法，结果相同（ASTM E1049-85）。"""
from manim import *
from wq_anim import *

PTS = [39.1, 42.5, 35.2, 45.1, 38.9, 49.7, 29.4, 48.2, 44.2, 45.9, 40.4, 41.7]
Y0, YS = 39.0, 0.17          # 画面：y = (M − Y0) · YS
X0, DX = -6.3, 0.5


def block(pts):
    i = max(range(len(pts)), key=lambda k: pts[k])
    b = pts[i:] + pts[:i + 1]
    out = []
    for v in b:                                # 只留转折点
        if out and v == out[-1]:
            continue
        if len(out) >= 2 and (out[-1] - out[-2]) * (v - out[-1]) > 0:
            out[-1] = v
        else:
            out.append(v)
    return out


def three_point(pts):
    """返回 [(被去掉的两个点在原序列里的下标, 幅值, 平均值)]；剩下的点"""
    idx = list(range(len(pts)))
    found = []
    k = 0
    while len(idx) >= 3 and k <= len(idx) - 3:
        a, b, c = (pts[idx[k]], pts[idx[k + 1]], pts[idx[k + 2]])
        if abs(b - c) >= abs(a - b) and k > 0:
            found.append(((idx[k], idx[k + 1]), abs(a - b) / 2, (a + b) / 2))
            del idx[k:k + 2]
            k = max(k - 2, 0)
        else:
            k += 1
    return found, idx


class Lesson(Base):
    def construct(self):
        self.title("11.6", "雨流计数：把杂乱的载荷拆成一个个循环", "Rainflow counting: breaking a messy load record into cycles")
        pos = lambda k, v: [X0 + DX * k, (v - Y0) * YS - 0.4, 0]   # noqa: E731
        raw = VMobject(color=BLUE, stroke_width=3).set_points_as_corners([pos(k, v) for k, v in enumerate(PTS)])
        axis = Line(pos(0, 25) , pos(len(PTS) - 1, 25), color=GREY_B, stroke_width=1)
        lab = zh("WQ-CR5 一个节拍里 J3 处的力矩 |M|（只留转折点）", size=20, color=GREY_A).move_to([-3.3, 2.15, 0])
        self.play(FadeIn(lab), Create(axis), Create(raw), run_time=2)
        self.caption("载荷一个节拍接一个节拍地重复。先只留下转折点：峰和谷",
                     "The load repeats cycle after cycle. Keep only the turning points: peaks and valleys")
        b = block(PTS)
        X1 = 0.4
        posb = lambda k, v: [X1 + DX * k, (v - Y0) * YS - 0.4, 0]   # noqa: E731
        blk = VMobject(color=YELLOW, stroke_width=3).set_points_as_corners([posb(k, v) for k, v in enumerate(b)])
        self.play(Create(blk), run_time=2)
        self.caption("① 从最大值 49.7 处切开、首尾相接：这样每个循环都能闭合（数字工厂的 closed_block）",
                     "① Cut at the maximum 49.7 and join the ends, so every cycle closes (the factory's closed_block)", wait=2)
        dots = VGroup(*[Dot(posb(k, v), radius=0.05, color=YELLOW) for k, v in enumerate(b)])
        self.play(FadeIn(dots), FadeOut(raw), FadeOut(axis), FadeOut(lab))
        found, left = three_point(b)
        table = VGroup()
        for n, ((i, j), a, m) in enumerate(found):
            seg = Line(posb(i, b[i]), posb(j, b[j]), color=RED, stroke_width=7)
            self.play(Create(seg), run_time=0.6)
            row = zh("循环 {}：幅值 {:.2f}，平均 {:.2f} N·m".format(n + 1, a, m), size=20, color=RED).move_to([-3.4, 1.6 - 0.42 * n, 0])
            table.add(row)
            self.play(FadeIn(row), FadeOut(seg), dots[i].animate.set_color(GREY_D), dots[j].animate.set_color(GREY_D), run_time=0.6)
            if n == 0:
                self.caption("② 连续三个转折点 A、B、C：若 B→C 比 A→B 跨得大，A–B 就是一个闭合的小循环，记下来，把 A、B 拿掉",
                             "② Three turning points A, B, C: if B→C spans more than A→B, A–B is a closed cycle — record it and remove A and B", wait=2)
        big = Line(posb(left[0], b[left[0]]), posb(left[1], b[left[1]]), color=ORANGE, stroke_width=8)
        self.play(Create(big))
        rowb = zh("大循环：幅值 {:.2f}，平均 {:.2f} N·m".format(abs(b[left[0]] - b[left[1]]) / 2, (b[left[0]] + b[left[1]]) / 2),
                  size=22, color=ORANGE).move_to([-3.4, 1.6 - 0.42 * len(found) - 0.1, 0])
        self.play(FadeIn(rowb))
        self.caption("③ 最后剩下最大值到最小值的那个大循环（49.7 ↔ 29.4）：它一个就占了几乎全部损伤（程序 11.6.1）",
                     "③ What remains is the big cycle from the maximum to the minimum (49.7 ↔ 29.4): it alone causes almost all the damage (Program 11.6.1)",
                     wait=2.5)
        self.card([["雨流计数：只看转折点，把载荷拆成闭合的循环", "rainflow: turning points only, split into closed cycles"],
                   ["每个循环有幅值和平均值，各自查 S–N 曲线", "each cycle has an amplitude and a mean, each read off the S–N curve"],
                   ["迈因纳：D = Σ nᵢ/Nᵢ，D = 1 时破坏", "Miner: D = Σ nᵢ/Nᵢ, failure at D = 1"],
                   ["损伤 ∝ 应力幅的 k 次方：大循环说了算", "damage ∝ amplitude to the power k: the big cycles dominate"]])
