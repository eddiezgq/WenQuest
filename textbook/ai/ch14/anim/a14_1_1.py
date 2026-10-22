"""动画 14.1.1（配图 14.1.1）：图像和文字，怎样被放进同一个空间。

左边是视觉编码器给出的向量，右边是文本编码器给出的向量——两个编码器分别训练，
同一件事（"SH-301 的轴颈处有划痕"与那张照片）在两边毫无关系。对比学习做的事只有一件：
再学两个投影，使**配对的靠近、不配对的推开**。推的力气由 InfoNCE 给出，一个批里有多少
样本，这一步就能比较多少个"不是它"。

画面上的点是现算的：按 code/_ch14.py 的同一套做法（同样的合成属性、同样的 InfoNCE、
同样的步长）就地训一遍，再投到两个主方向上。渲染服务只允许 manim、wq_anim、numpy、
math、random，所以不能 import 章内模块，代码在这里重写一遍。
"""
import numpy as np
from manim import *
from wq_anim import *

PARTS = ["SH-301 输出轴", "GH-12 主动齿轮", "XT-5 箱体"]
KINDS = ["划痕", "压痕", "锈斑"]
EN_PART = {"SH-301 输出轴": "SH-301 shaft", "GH-12 主动齿轮": "GH-12 gear", "XT-5 箱体": "XT-5 housing"}
EN_KIND = {"划痕": "scratch", "压痕": "dent", "锈斑": "rust"}
DIM, OUT, TEMP = 24, 2, 0.1


def l2(x):
    return x / np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12)


def data(n=600, seed=0):
    g = np.random.default_rng(14 + seed)
    a = np.c_[g.integers(0, len(PARTS), n), g.integers(0, len(KINDS), n)]
    gb = np.random.default_rng(777)
    bi = [gb.normal(0, 1, (len(PARTS), DIM)), gb.normal(0, 1, (len(KINDS), DIM))]   # 图像端的编码方式
    bt = [gb.normal(0, 1, (len(PARTS), DIM)), gb.normal(0, 1, (len(KINDS), DIM))]   # 文本端：另一套，与图像端无关
    xi = bi[0][a[:, 0]] + bi[1][a[:, 1]] + g.normal(0, 0.35, (n, DIM))
    xt = bt[0][a[:, 0]] + bt[1][a[:, 1]] + g.normal(0, 0.10, (n, DIM))
    return xi, xt, a


def infonce(zi, zt, temp):
    B = len(zi)
    s = zi @ zt.T / temp
    pi = np.exp(s - s.max(1, keepdims=True))
    pi /= pi.sum(1, keepdims=True)
    pt = np.exp(s - s.max(0, keepdims=True))
    pt /= pt.sum(0, keepdims=True)
    eye = np.eye(B)
    loss = -(np.log(np.maximum(np.diag(pi), 1e-12)).mean() + np.log(np.maximum(np.diag(pt), 1e-12)).mean()) / 2
    gs = ((pi - eye) + (pt - eye)) / (2 * B * temp)
    return loss, gs @ zt, gs.T @ zi


def train(xi, xt, steps=500, batch=64, lr=0.6, seed=0):
    g = np.random.default_rng(31 + seed)
    Wi = g.normal(0, 0.3, (DIM, OUT))
    Wt = g.normal(0, 0.3, (DIM, OUT))
    snaps, losses = [], []
    for t in range(steps):
        idx = g.choice(len(xi), batch, replace=False)
        hi, ht = xi[idx] @ Wi, xt[idx] @ Wt
        zi, zt = l2(hi), l2(ht)
        loss, gzi, gzt = infonce(zi, zt, TEMP)
        ghi = (gzi - zi * (gzi * zi).sum(1, keepdims=True)) / np.maximum(np.linalg.norm(hi, axis=1, keepdims=True), 1e-12)
        ght = (gzt - zt * (gzt * zt).sum(1, keepdims=True)) / np.maximum(np.linalg.norm(ht, axis=1, keepdims=True), 1e-12)
        Wi -= lr * xi[idx].T @ ghi
        Wt -= lr * xt[idx].T @ ght
        if t in (0, 30, 80, 200, steps - 1):
            snaps.append((Wi.copy(), Wt.copy()))
            losses.append(loss)
    return snaps, losses


XI, XT, A = data()
SNAPS, LOSSES = train(XI, XT)
SHOW = 90                                   # 画面上画这么多个点
COL = [BLUE, RED, YELLOW]


def coords(W, X, scale=1.9, shift=0.0):
    z = l2(X[:SHOW] @ W)
    return [np.array([z[i, 0] * scale + shift, z[i, 1] * scale - 0.3, 0]) for i in range(SHOW)]


class Lesson(Base):
    def construct(self):
        self.title("14.1", "把图和文放进同一个空间", "Putting images and text in one space")

        # 一、两个编码器各说各话
        left = VGroup(*[Dot(p, radius=0.055, color=COL[A[i, 1]]) for i, p in enumerate(coords(SNAPS[0][0], XI, 1.5, -3.4))])
        right = VGroup(*[Triangle(fill_opacity=1, color=COL[A[i, 1]]).scale(0.07).move_to(p)
                         for i, p in enumerate(coords(SNAPS[0][1], XT, 1.5, 3.4))])
        lab_l = Text("视觉编码器", font_size=26).move_to([-3.4, 2.1, 0])
        lab_r = Text("文本编码器", font_size=26).move_to([3.4, 2.1, 0])
        self.play(FadeIn(left), FadeIn(right), Write(lab_l), Write(lab_r), run_time=1.2)
        self.caption("两个编码器分别训练：同一件事在左边是一个点、在右边是另一个点，两者毫无关系",
                     "Two encoders trained separately: the same thing is one point on the left and another on the right")

        # 二、配对的那一对
        k = 3
        line = DashedLine(left[k].get_center(), right[k].get_center(), color=GREY, stroke_width=2)
        cap = Text(f"{PARTS[A[k, 0]]}的轴颈处有{KINDS[A[k, 1]]}", font_size=24).move_to([0, -2.6, 0])
        self.play(Create(line), Write(cap), run_time=1.0)
        self.caption("这条虚线连着的，是同一件事的照片与那句检验记录——我们要让它们靠在一起",
                     "The dashed line joins one photo and the sentence describing it — these should end up together")
        self.play(FadeOut(line), FadeOut(cap), run_time=0.5)

        # 三、训练：一步步投到同一个空间
        eq = MathTex(r"\mathcal{L} = -\frac{1}{B}\sum_i \log\frac{e^{\,z_i^{\top} t_i/\tau}}{\sum_j e^{\,z_i^{\top} t_j/\tau}}",
                     font_size=34).move_to([0, 2.2, 0])
        self.play(FadeOut(lab_l), FadeOut(lab_r), Write(eq), run_time=1.0)
        self.caption("InfoNCE：分子是配对的那一对，分母是这个批里全部候选——一步能比较多少个“不是它”，取决于批有多大",
                     "InfoNCE: the matching pair over every candidate in the batch — the batch size is how many negatives you get")
        for s, loss in zip(SNAPS[1:], LOSSES[1:]):
            nl = VGroup(*[Dot(p, radius=0.055, color=COL[A[i, 1]]) for i, p in enumerate(coords(s[0], XI))])
            nr = VGroup(*[Triangle(fill_opacity=1, color=COL[A[i, 1]]).scale(0.07).move_to(p)
                          for i, p in enumerate(coords(s[1], XT))])
            self.play(Transform(left, nl), Transform(right, nr), run_time=1.1)
        self.caption("同一个空间里：说的是同一件事的图（圆）与文（三角）落在一处，不同的事分开",
                     "In one space: image (circle) and text (triangle) describing the same thing land together")

        self.card([["对比学习学到了什么", "What contrastive learning gives you"],
                   ["两个编码器 + 两个投影，训练目标只有“配对的靠近、不配对的推开”",
                    "Two encoders and two projections, trained only to pull pairs together and push others apart"],
                   ["于是可以零样本分类：把类别写成一句话，看哪句话离这张图最近",
                    "Hence zero-shot classification: write each class as a sentence and see which is closest"],
                   ["也可以跨模态检索：以文搜图、以图搜文、以图搜图，都在同一个空间里比",
                    "And cross-modal retrieval: text-to-image, image-to-text, image-to-image, all in one space"]])
