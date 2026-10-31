"""动画 15.3.1（配图 15.3.1）：蒙特卡洛树搜索的四步。

取木棍游戏：桌上 13 根，两人轮流取 1—3 根，取到最后一根的人赢。它有必胜策略
（剩下的根数是 4 的倍数时轮到谁谁输），所以能核对搜索到底搜对没有。

一轮搜索分四步：**选择**（沿着已经展开的节点，按 $\\bar v + c\\sqrt{\\ln N/n}$ 往下走，
既照顾看着好的，也照顾没试过的）、**扩展**（挑一个没见过的孩子加进树里）、
**模拟**（从那里随便走到底，看谁赢）、**回传**（把结果沿路往上记，每上一层换一个视角，
价值取反）。跑够多轮，访问次数最多的那一支就是要走的那一步。

画面上的数都是现算的：按 code/_ch15.py 的同一套做法就地跑一遍 UCT。
渲染服务只允许 manim、wq_anim、numpy、math、random，所以不能 import 章内模块，代码在这里重写一遍。
"""
import numpy as np
from manim import *
from wq_anim import *

N0, TAKE, C_UCB = 13, (1, 2, 3), 1.4


def rollout(n, g):
    turn = 0
    while n > 0:
        n -= int(g.choice([t for t in TAKE if t <= n]))
        turn ^= 1
    return 1.0 if turn == 1 else 0.0


def uct(n, sims, seed=7):
    """与书中同一套实现，另外把每一轮走过的路径记下来，供动画逐步展示。"""
    g = np.random.default_rng(seed)
    N, W = {n: 0.0}, {n: 0.0}
    trace = []
    for _ in range(sims):
        path, s = [], n
        while s > 0:
            kids = [s - t for t in TAKE if t <= s]
            unseen = [k for k in kids if k not in N]
            if unseen:
                k = int(g.choice(unseen))
                N[k], W[k] = 0.0, 0.0
                path.append(s)
                s = k
                break
            tot = sum(N[k] for k in kids)
            ucb = [(1 - W[k] / max(N[k], 1e-9)) + C_UCB * np.sqrt(np.log(tot + 1) / max(N[k], 1e-9)) for k in kids]
            path.append(s)
            s = kids[int(np.argmax(ucb))]
        v = 0.0 if s == 0 else rollout(s, g)
        leaf = s
        N[s] = N.get(s, 0.0) + 1
        W[s] = W.get(s, 0.0) + v
        for anc in reversed(path):
            v = 1 - v
            N[anc] += 1
            W[anc] += v
        trace.append((list(path), leaf, dict(N), dict(W)))
    return N, W, trace


NFIN, WFIN, TRACE = uct(N0, 400)
KIDS = [N0 - t for t in TAKE]
VISITS = [NFIN[k] for k in KIDS]
WINS = [NFIN[k] - WFIN[k] for k in KIDS]
BEST = TAKE[int(np.argmax(VISITS))]


def node(label, pos, color=BLUE):
    c = Circle(radius=0.36, color=color, fill_opacity=0.18).move_to(pos)
    t = Text(str(label), font_size=22).move_to(pos)
    return VGroup(c, t)


class Lesson(Base):
    def construct(self):
        self.title("15.3", "搜索的四步", "Four steps of one search")

        root = node(N0, [0, 1.9, 0], YELLOW)
        kid_pos = [[-3.2, 0.2, 0], [0, 0.2, 0], [3.2, 0.2, 0]]
        kids = [node(k, p) for k, p in zip(KIDS, kid_pos)]
        edges = [Line(root.get_bottom(), k.get_top(), color=GREY) for k in kids]
        self.play(FadeIn(root), run_time=0.6)
        self.caption(f"桌上 {N0} 根木棍，轮流取 1—3 根，取到最后一根的人赢。该怎么取？",
                     f"{N0} sticks on the table; take 1 to 3 in turn; whoever takes the last one wins")
        self.play(*[Create(e) for e in edges], *[FadeIn(k) for k in kids], run_time=1.0)
        self.caption("三种取法，各留下 12、11、10 根。哪一种好，先不知道",
                     "Three moves, leaving 12, 11 or 10 sticks. Which one is good? Nobody knows yet")

        # 一、选择
        box = SurroundingRectangle(kids[1], color=GREEN, buff=0.12)
        self.play(Create(box), run_time=0.6)
        self.caption("①选择：沿着已经展开的节点往下走，按 $\\bar v + c\\sqrt{\\ln N/n}$ 挑——"
                     "前一项照顾看着好的，后一项照顾还没试过的",
                     "1. Selection: walk down by $\\bar v + c\\sqrt{\\ln N/n}$ — exploit what looks good, explore what is untried")

        # 二、扩展
        leaf = node(KIDS[1] - 2, [0, -1.5, 0], GREEN)
        e2 = Line(kids[1].get_bottom(), leaf.get_top(), color=GREY)
        self.play(Create(e2), FadeIn(leaf), run_time=0.8)
        self.caption("②扩展：挑一个没见过的孩子，加进树里", "2. Expansion: add one unvisited child to the tree")

        # 三、模拟
        dots = VGroup(*[Dot([0 + 0.5 * i - 1.0, -2.5, 0], radius=0.07, color=GREY) for i in range(5)])
        self.play(FadeOut(box), FadeIn(dots), run_time=0.6)
        res = Text("赢", font_size=28, color=GREEN).move_to([1.8, -2.5, 0])
        self.play(Write(res), run_time=0.6)
        self.caption("③模拟：从这里起双方随便走到底，看谁赢。一次只得一个 0 或 1，很粗——但便宜",
                     "3. Simulation: play on at random to the end. One rollout gives only a 0 or a 1 — crude, but cheap")

        # 四、回传
        arrows = [Arrow(leaf.get_top(), kids[1].get_bottom(), buff=0.05, color=YELLOW, stroke_width=3),
                  Arrow(kids[1].get_top(), root.get_bottom(), buff=0.05, color=YELLOW, stroke_width=3)]
        for ar in arrows:
            self.play(GrowArrow(ar), run_time=0.5)
        self.caption("④回传：把这一次的结果沿路记上去。每上一层换一个人走子，价值取反",
                     "4. Backpropagation: record the result up the path; each level is the other player, so the value flips")
        self.play(FadeOut(dots), FadeOut(res), *[FadeOut(ar) for ar in arrows], FadeOut(e2), FadeOut(leaf), run_time=0.6)

        # 跑满 400 轮之后的样子
        labels = VGroup(*[Text(f"{int(v)} 次\n胜率 {w / max(v, 1) * 100:.0f}%", font_size=20,
                               line_spacing=0.6).next_to(k, DOWN, buff=0.25)
                          for k, v, w in zip(kids, VISITS, WINS)])
        self.play(FadeIn(labels), run_time=1.0)
        self.caption(f"跑满 400 轮：访问次数最多的是“取 {BEST} 根”，留下 {N0 - BEST} 根——正是必胜的那一步",
                     f"After 400 rounds the most visited move is taking {BEST}, leaving {N0 - BEST} — the provably winning move")

        self.card([["搜索做了什么", "What the search did"],
                   ["四步一轮：选择、扩展、模拟、回传；跑够多轮，访问次数最多的那一支就是答案",
                    "Four steps per round: select, expand, simulate, back up. The most visited branch is the answer"],
                   ["它不平均用力——大半的模拟花在看着最好的那一支上",
                    "It does not spread effort evenly: most simulations go to the most promising branch"],
                   ["AlphaGo 这一路，是把“随便走到底”换成了网络给的落子概率与胜率估计",
                    "AlphaGo replaced the random rollout with a policy network and a value estimate"]])
