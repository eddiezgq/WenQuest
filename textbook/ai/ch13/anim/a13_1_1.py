"""动画 13.1.1（配图 13.1.1）：词向量空间中的类比关系。

先看独热编码：任何两个词的内积都是 0，“轴”与“轴颈”和“轴”与“螺栓”一样远，这种表示里没有“像不像”。
再看训出来的词向量：同一类零件聚成一簇，“粗 → 精”这个等级在每一簇里都指同一个方向，
于是 `精轴 − 粗轴 + 粗齿轮` 落在 `精齿轮` 附近——类比成了向量的加减法。

画面上的点是真算出来的：动画里按 code/_ch13.py 的同一套做法（同一个语料生成规则、同样的
skip-gram 负采样、同样的批量与步长）就地训一遍，再用奇异值分解投到两个主方向上。
渲染服务只允许 manim、wq_anim、numpy、math、random，所以不能 import 章内模块，代码在这里重写一遍。
"""
import numpy as np
from manim import *
from wq_anim import *

BASE = ["轴", "齿轮", "轴承", "箱体", "螺栓"]
GRADE = ["粗", "精"]
EN_BASE = {"轴": "shaft", "齿轮": "gear", "轴承": "bearing", "箱体": "housing", "螺栓": "bolt"}
EN_GRADE = {"粗": "rough", "精": "fine"}
CTX_BASE = {"轴": ["车床", "顶尖", "轴颈"], "齿轮": ["滚齿", "齿形", "模数"],
            "轴承": ["压装", "游隙", "内圈"], "箱体": ["镗孔", "结合面", "铸件"],
            "螺栓": ["扭矩", "螺纹", "垫片"]}
CTX_GRADE = {"粗": ["留量", "粗加工", "大进给"], "精": ["终检", "精加工", "小进给"]}


def corpus(n_sent=6000, seed=13):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_sent):
        b = BASE[rng.integers(len(BASE))]
        g = GRADE[rng.integers(len(GRADE))]
        ctx = list(rng.choice(CTX_BASE[b], 2, replace=False)) + list(rng.choice(CTX_GRADE[g], 2, replace=False))
        rng.shuffle(ctx)
        out.append([ctx[0], ctx[1], g + b, ctx[2], ctx[3]])
    return out


def skipgram(sents, dim=24, epochs=10, window=2, neg=5, lr=0.025, batch=64, seed=0):
    vocab = sorted({w for s in sents for w in s})
    ix = {w: i for i, w in enumerate(vocab)}
    rng = np.random.default_rng(seed)
    W = rng.normal(0, 0.1, (len(vocab), dim))
    C = rng.normal(0, 0.1, (len(vocab), dim))
    freq = np.zeros(len(vocab))
    for s in sents:
        for w in s:
            freq[ix[w]] += 1
    p = freq ** 0.75
    p /= p.sum()
    pairs = np.array([(ix[s[i]], ix[s[j]]) for s in sents for i in range(len(s))
                      for j in range(max(0, i - window), min(len(s), i + window + 1)) if i != j])
    for _ in range(epochs):
        rng.shuffle(pairs)
        for b0 in range(0, len(pairs), batch):
            q = pairs[b0:b0 + batch]
            a, pos = q[:, 0], q[:, 1]
            negs = rng.choice(len(vocab), (len(q), neg), p=p)
            tgt = np.concatenate([pos[:, None], negs], axis=1)
            lab = np.zeros_like(tgt, dtype=float)
            lab[:, 0] = 1.0
            w, c = W[a], C[tgt]
            z = np.clip(np.einsum("bkd,bd->bk", c, w), -30, 30)
            g = lab - 1 / (1 + np.exp(-z))
            np.add.at(W, a, lr * np.einsum("bk,bkd->bd", g, c))
            np.add.at(C, tgt, lr * (g[:, :, None] * w[:, None, :]))
    return ix, W


IX, W = skipgram(corpus())
WORDS = [g + b for b in BASE for g in GRADE]
X = np.stack([W[IX[w]] for w in WORDS])
X = X - X.mean(0)
_, _, Vt = np.linalg.svd(X, full_matrices=False)
P = X @ Vt[:2].T
P = P / np.abs(P).max() * 3.0                      # 缩到画面里
POS = {w: np.array([P[i, 0], P[i, 1] - 0.4, 0.0]) for i, w in enumerate(WORDS)}


class Lesson(Base):
    def construct(self):
        self.title("13.1", "词向量空间中的类比", "Analogies in word-vector space")

        # 独热编码：三个词，两两内积都是 0
        rows = VGroup()
        labels = [("轴", "shaft"), ("轴颈", "journal"), ("螺栓", "bolt")]
        for r, (zh_t, en_t) in enumerate(labels):
            for c in range(8):
                on = c == r
                rows.add(Square(side_length=0.36, stroke_width=1.2, stroke_color=GREY,
                                fill_color=BLUE if on else BLACK,
                                fill_opacity=0.9 if on else 0.0).move_to([-4.6 + c * 0.38, 1.9 - r * 0.42, 0]))
            rows.add(bi([zh_t, en_t], 16).move_to([-5.9, 1.9 - r * 0.42, 0]))
        self.play(FadeIn(rows), run_time=0.9)
        self.caption("独热编码：每个词占一维，任何两个词的内积都是 0——这种表示里没有“像不像”",
                     "One-hot: one dimension per word, every pair has inner product 0 — no notion of similarity")
        self.play(FadeOut(rows), run_time=0.5)

        # 训出来的词向量：五簇，等级方向一致
        dots, texts, arrows = VGroup(), VGroup(), VGroup()
        for w in WORDS:
            col = BLUE if w[0] == "精" else RED
            dots.add(Dot(POS[w], radius=0.07, color=col))
            texts.add(bi([w, f"{EN_GRADE[w[0]]} {EN_BASE[w[1:]]}"], 15, color=col).next_to(POS[w], UR, buff=0.05))
        self.play(FadeIn(dots), FadeIn(texts), run_time=1.0)
        self.caption("训出来的词向量：同一类零件聚成一簇",
                     "Trained vectors: each kind of part forms its own cluster")
        for b in BASE:
            arrows.add(Arrow(POS["粗" + b], POS["精" + b], buff=0.06, stroke_width=2.4,
                             max_tip_length_to_length_ratio=0.18, color=GREY_B))
        self.play(LaggedStart(*[Create(x) for x in arrows], lag_ratio=0.2), run_time=1.4)
        self.caption("“粗 → 精”在每一簇里都指同一个方向：这个方向就是“等级”这件事",
                     "“rough → fine” points the same way in every cluster: that direction *is* the grade")

        # 类比：平行四边形
        self.play(FadeOut(arrows), run_time=0.4)
        q = POS["精轴"] - POS["粗轴"] + POS["粗齿轮"]
        a1 = Arrow(POS["粗轴"], POS["精轴"], buff=0.06, stroke_width=3, color=YELLOW,
                   max_tip_length_to_length_ratio=0.18)
        a2 = Arrow(POS["粗齿轮"], q, buff=0.06, stroke_width=3, color=YELLOW,
                   max_tip_length_to_length_ratio=0.18)
        star = Star(outer_radius=0.14, color=YELLOW, fill_opacity=1).move_to(q)
        self.play(Create(a1))
        self.play(TransformFromCopy(a1, a2), run_time=1.0)
        self.play(FadeIn(star), run_time=0.4)
        self.caption("精轴 − 粗轴 + 粗齿轮，落在精齿轮旁边：类比变成了向量的加减法",
                     "fine shaft − rough shaft + rough gear lands next to fine gear: analogy as vector arithmetic")
        self.card([["词的表示", "Representing words"],
                   MathTex(r"\vec{v}_{\text{精轴}}-\vec{v}_{\text{粗轴}}+\vec{v}_{\text{粗齿轮}}"
                           r"\approx \vec{v}_{\text{精齿轮}}", font_size=36),
                   ["独热编码：维数 = 词表大小，两个词之间没有远近",
                    "One-hot: as many dimensions as words, no notion of distance"],
                   ["词向量：几百维，方向有含义——但含义来自语料，语料里的偏见也一起学了进去",
                    "Embeddings: a few hundred dimensions with meaningful directions — including the corpus's biases"]])
