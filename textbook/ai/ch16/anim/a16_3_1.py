"""动画 16.3.1（配图 16.3.1）：扩散的正向与反向。

正向：一堆点（三个峰）被一步步加噪，推到最后就是一团标准正态——这一步没有参数，谁来做都一样。
反向：从纯噪声出发，每一步把"这里的噪声大概是多少"估出来减掉，三个峰一个个长回来。

关键的一步是**前向有闭式解**：$x_t=\\sqrt{\\bar\\alpha_t}\\,x_0+\\sqrt{1-\\bar\\alpha_t}\\,\\varepsilon$。
所以训练时不用真的一步步加噪，随手抽一个时刻 $t$ 跳过去就行；要学的只有一件事——
从 $x_t$ 把那个 $\\varepsilon$ 估回来。

画面上的点都是现算的。渲染服务只允许 manim、wq_anim、numpy、math、random，不能 import 章内模块，
所以这里按 code/_ch16.py 的同一套做法把最小的一份重写一遍。
"""
import numpy as np
from manim import *
from wq_anim import *

# 与 code/_ch16.py 同一个三峰分布（标准化之后）
W = np.array([0.5, 0.35, 0.15])
MU = np.array([-2.0, 0.6, 3.2])
SD = np.array([0.45, 0.6, 0.25])
M = float((W * MU).sum())
S = float(np.sqrt((W * (SD ** 2 + MU ** 2)).sum() - M ** 2))
ZMU, ZSD = (MU - M) / S, SD / S

T_TOTAL = 1000
BETA = np.linspace(1e-4, 0.02, T_TOTAL)
ABAR = np.cumprod(1 - BETA)
N_PTS = 220


def sample(n, seed):
    g = np.random.default_rng(seed)
    k = g.choice(len(W), size=n, p=W)
    return (g.normal(MU[k], SD[k]) - M) / S


def eps_star(z, t):
    """最优噪声预测器：这个分布的分数函数写得出来，所以动画里不用训模型。"""
    ab = ABAR[t]
    mu, var = np.sqrt(ab) * ZMU, ab * ZSD ** 2 + (1 - ab)
    d = z[:, None] - mu
    comp = W / np.sqrt(2 * np.pi * var) * np.exp(-0.5 * d ** 2 / var)
    score = (comp * (-d / var)).sum(1) / np.maximum(comp.sum(1), 1e-300)
    return -np.sqrt(1 - ab) * score


def forward_track(z0, ts, seed=3):
    g = np.random.default_rng(seed)
    eps = g.normal(size=len(z0))
    return [np.sqrt(ABAR[t]) * z0 + np.sqrt(1 - ABAR[t]) * eps for t in ts]


def reverse_track(n, ts_show, seed=5):
    g = np.random.default_rng(seed)
    z = g.normal(size=n)
    out, want = [], set(ts_show)
    for t in range(T_TOTAL - 1, -1, -1):
        if t in want:
            out.append((t, z.copy()))
        e = eps_star(z, t)
        zh = np.clip((z - np.sqrt(1 - ABAR[t]) * e) / np.sqrt(ABAR[t]), -6, 6)
        ab_prev = ABAR[t - 1] if t > 0 else 1.0
        sig = np.sqrt(max((1 - ab_prev) / (1 - ABAR[t]) * (1 - ABAR[t] / ab_prev), 0.0)) if t > 0 else 0.0
        z = np.sqrt(ab_prev) * zh + np.sqrt(max(1 - ab_prev - sig ** 2, 0.0)) * e
        if sig > 0:
            z = z + sig * g.normal(size=n)
    out.append((0, z))
    return out


TS = [0, 60, 150, 300, 600, 999]
Z0 = sample(N_PTS, 11)
FWD = forward_track(Z0, TS)
REV = reverse_track(N_PTS, TS[1:])

X_LO, X_HI = -3.4, 3.4
Y_ROWS = np.linspace(-1.15, 1.15, 12)


def cloud(vals, color, y0):
    """把一维的点摊成一片：横坐标是取值，纵坐标只是为了看得清。"""
    g = np.random.default_rng(99)
    dots = VGroup()
    for i, v in enumerate(vals):
        x = float(np.clip(v, X_LO, X_HI)) * (6.0 / X_HI)
        y = y0 + float(Y_ROWS[i % len(Y_ROWS)]) * 0.42 + float(g.normal(0, 0.03))
        dots.add(Dot([x, y, 0], radius=0.045, color=color, fill_opacity=0.75))
    return dots


class Lesson(Base):
    def construct(self):
        self.title("16.3", "扩散：正向与反向", "Diffusion: forward and reverse")

        axis = Line([-6.4, -2.4, 0], [6.4, -2.4, 0], color=GREY, stroke_width=2)
        ticks = VGroup(*[Text(f"{v:+.0f}" if v else "0", font_size=18).move_to(
            [v * (6.0 / X_HI), -2.75, 0]) for v in (-3, -1.5, 0, 1.5, 3)])
        self.play(Create(axis), FadeIn(ticks), run_time=0.6)

        pts = cloud(FWD[0], BLUE, 0.6)
        self.play(FadeIn(pts), run_time=0.8)
        self.caption("先看一堆真样本：三个峰，左边那个最密，右边那个又矮又窄",
                     "Start from real samples: three modes, the left one densest, the right one low and narrow")

        tlab = Text("t = 0", font_size=26).move_to([5.2, 2.0, 0])
        self.play(FadeIn(tlab), run_time=0.4)
        self.caption("正向过程：每一步掺一点高斯噪声。这一步**没有参数**，不用学",
                     "Forward process: add a little Gaussian noise at each step. No parameters to learn here")

        for t, vals in zip(TS[1:], FWD[1:]):
            new = cloud(vals, BLUE, 0.6)
            self.play(Transform(pts, new), Transform(tlab, Text(f"t = {t}", font_size=26).move_to([5.2, 2.0, 0])),
                      run_time=0.9)
        self.caption("推到最后，三个峰全平了，剩下一团标准正态——原来是什么，看不出来了",
                     "At the end the modes are gone: just a standard normal. Nothing of the original remains")

        self.caption("这里有一件要紧的事：第 t 步的结果有闭式解，"
                     "$x_t=\\sqrt{\\bar\\alpha_t}x_0+\\sqrt{1-\\bar\\alpha_t}\\varepsilon$。"
                     "所以训练时不必一步步加，随手抽一个 t 跳过去就行",
                     "One key fact: step t has a closed form, "
                     "$x_t=\\sqrt{\\bar\\alpha_t}x_0+\\sqrt{1-\\bar\\alpha_t}\\varepsilon$, "
                     "so training jumps straight to a random t")

        self.clear_stage()
        axis2 = Line([-6.4, -2.4, 0], [6.4, -2.4, 0], color=GREY, stroke_width=2)
        self.play(Create(axis2), FadeIn(ticks.copy()), run_time=0.5)
        rev_pts = cloud(REV[0][1], GREEN, 0.6)
        rlab = Text(f"t = {REV[0][0]}", font_size=26).move_to([5.2, 2.0, 0])
        self.play(FadeIn(rev_pts), FadeIn(rlab), run_time=0.8)
        self.caption("反向过程：从纯噪声起步。每一步问同一个问题——"
                     "这里掺进去的噪声大概是多少？估出来，减掉一点",
                     "Reverse: start from pure noise. Each step asks the same question — "
                     "how much noise is in here? Estimate it, subtract a bit")

        for t, vals in REV[1:]:
            new = cloud(vals, GREEN, 0.6)
            self.play(Transform(rev_pts, new),
                      Transform(rlab, Text(f"t = {t}" if t else "走完 / done", font_size=26).move_to([5.2, 2.0, 0])),
                      run_time=0.9)
        self.caption("三个峰一个个长回来了，连右边那个又矮又窄的也在——"
                     "模型要学的只有那一件事：从带噪的 $x_t$ 把 $\\varepsilon$ 估回来",
                     "The three modes come back, the low narrow one included. "
                     "All the model ever learns is to predict $\\varepsilon$ from the noisy $x_t$")

        self.card([["扩散模型做了什么", "What a diffusion model does"],
                   ["正向加噪没有参数，而且第 t 步有闭式解，可以直接跳过去",
                    "The forward noising has no parameters and a closed form: jump straight to any t"],
                   ["要学的只有一个噪声预测器；训练目标就是 $\\|\\varepsilon-\\hat\\varepsilon\\|^2$",
                    "The only thing learned is a noise predictor, trained on $\\|\\varepsilon-\\hat\\varepsilon\\|^2$"],
                   ["代价是采样要走很多步——这也是后面所有加速办法要解决的问题",
                    "The price is many sampling steps — which is what every speed-up method attacks"]])
