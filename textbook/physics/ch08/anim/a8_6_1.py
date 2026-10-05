"""动画 8.6.1（配图 8.6.1）：罚函数接触与步长。左：步长 0.5 ms，网球压进地面几毫米后弹起；右：步长 1/60 s，
一步就压进地面 3 cm，下一步被巨大的弹力弹飞。为看清穿入，地面以下的深度放大 10 倍画出。"""
from manim import *
from wq_anim import *
import numpy as np

M, K, G = 0.058, 3.0e4, 9.81
C = 7.6
SC = 2.6                               # 画面单位 / 米（高度）
DEEP = 10.0                            # 地面以下放大倍数
BASE = [np.array([-3.4, -1.3, 0]), np.array([3.4, -1.3, 0])]


def run(h, T=1.2):
    y, v, t = 1.0, 0.0, 0.0
    out = [(t, y)]
    while t < T and y < 3.0:
        F = -M * G + (max(0.0, -K * y - C * v) if y < 0 else 0.0)
        v += h * F / M; y += h * v; t += h
        out.append((t, y))
    return out


def ypos(y):
    return SC * y if y >= 0 else SC * y * DEEP


class Lesson(Base):
    def construct(self):
        self.title("8.6", "步长太大，球被“弹飞”", "Too large a step launches the ball")
        A, B = run(0.0005), run(1 / 60)
        grounds = VGroup(*[Line(b + LEFT * 2.2, b + RIGHT * 2.2, color=GREY_B, stroke_width=4) for b in BASE])
        heads = VGroup(bi(["步长 0.5 ms", "step 0.5 ms"], size=24).move_to(BASE[0] + UP * 3.3),
                       bi(["步长 1/60 s", "step 1/60 s"], size=24).move_to(BASE[1] + UP * 3.3))
        note = bi(["地面以下的深度放大 10 倍", "depth below the floor ×10"], size=20).move_to(np.array([0, -2.2, 0]))
        self.play(FadeIn(grounds), FadeIn(heads), FadeIn(note))
        t = ValueTracker(0.0)

        def ball(path, base):
            def make():
                tt = t.get_value()
                i = min(len(path) - 1, int(np.searchsorted([p[0] for p in path], tt)))
                y = path[i][1]
                return Circle(radius=0.17, color=YELLOW_E, fill_opacity=0.9).move_to(base + UP * (ypos(y) + 0.17))
            return always_redraw(make)
        self.add(ball(A, BASE[0]), ball(B, BASE[1]))
        self.caption("网球从 1.0 m 落下，地面用很硬的弹簧表示（罚函数）", "The ball drops from 1.0 m onto a floor modelled as a very stiff spring (penalty)", wait=0)
        self.play(t.animate.set_value(0.42), run_time=3, rate_func=linear)
        self.caption("接触只持续约 4 ms：小步长时算了好几步，大步长时一步就跨过去了", "The contact lasts about 4 ms: many small steps, or a single large one", wait=0)
        self.play(t.animate.set_value(0.5), run_time=6, rate_func=linear)
        self.play(t.animate.set_value(1.2), run_time=3, rate_func=linear)
        self.caption("大步长：一步压进 3 cm，下一步地面的弹力把球以 260 多米每秒弹飞", "Large step: 3 cm deep in one step, then the floor launches the ball at over 260 m/s", wait=2.0)
        self.card([["接触与步长", "Contact and time step"],
                   ["罚函数接触是很硬的弹簧：ωh < 2 只是必要条件，每次接触约 10 步才准", "Penalty contact is a stiff spring: ωh < 2 is only necessary; ~10 steps per contact for accuracy"],
                   ["游戏引擎常用冲量法：放回地面，速度按恢复系数反向", "Games use impulses: put it back, reverse the speed by e"],
                   ["MuJoCo：2 ms 步长，接触用软约束", "MuJoCo: 2 ms steps, contacts as soft constraints"]])
