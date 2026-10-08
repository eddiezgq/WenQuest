"""13.1 节的示意图（数值同程序 13.1.1）。

图 13.1.1：（a）训出来的词向量投到两个主方向上：五类零件分成五簇，“粗/精”这个等级在每一簇里都指同一个方向；
（b）类比关系是一个平行四边形：精轴 − 粗轴 + 粗齿轮 落在精齿轮附近。词向量能做类比，靠的就是这种方向一致性。
"""
import numpy as np

from _ch13 import BASE, GRADE, corpus, skipgram
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
ix, W = skipgram(corpus())
words = [g + b for b in BASE for g in GRADE]
X = np.stack([W[ix[w]] for w in words])
X = X - X.mean(0)
U, S, Vt = np.linalg.svd(X, full_matrices=False)       # 取前两个主方向
P = X @ Vt[:2].T
EN = {"轴": "shaft", "齿轮": "gear", "轴承": "bearing", "箱体": "housing", "螺栓": "bolt"}
GE = {"粗": "rough", "精": "fine"}

fig, (a, b) = plt.subplots(1, 2, figsize=(12.0, 4.6))
for i, w in enumerate(words):
    g, base = w[0], w[1:]
    col = C["z"] if g == "精" else C["x"]
    a.plot(P[i, 0], P[i, 1], "o", ms=7, color=col)
    a.annotate(T(w, f"{GE[g]} {EN[base]}"), (P[i, 0], P[i, 1]), textcoords="offset points",
               xytext=(6, 4), fontsize=9)
for base in BASE:                                      # 把同一个零件的粗、精连起来：箭头方向一致
    i, j = words.index("粗" + base), words.index("精" + base)
    a.annotate("", xy=P[j], xytext=P[i], arrowprops=dict(arrowstyle="->", color=C["muted"], lw=1.2))
a.set_title(T("(a) 词向量的前两个主方向", "(a) First two principal directions"), fontsize=10)
a.set_xlabel(T("主方向 1", "component 1"))
a.set_ylabel(T("主方向 2", "component 2"))
a.grid(alpha=0.25, lw=0.5)

quad = ["粗轴", "精轴", "粗齿轮", "精齿轮"]
pos = {w: P[words.index(w)] for w in quad}
q = pos["精轴"] - pos["粗轴"] + pos["粗齿轮"]
for w in quad:
    col = C["z"] if w[0] == "精" else C["x"]
    b.plot(*pos[w], "o", ms=8, color=col)
    b.annotate(T(w, f"{GE[w[0]]} {EN[w[1:]]}"), pos[w], textcoords="offset points", xytext=(6, 4), fontsize=9)
b.plot(q[0], q[1], "*", ms=14, color=C["accent"])
b.annotate(T("精轴 − 粗轴 + 粗齿轮", "fine shaft − rough shaft + rough gear"), (q[0], q[1]),
           textcoords="offset points", xytext=(8, -14), fontsize=9, color=C["accent"])
for p0, p1 in ((pos["粗轴"], pos["精轴"]), (pos["粗齿轮"], q)):
    b.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="->", color=C["muted"], lw=1.2))
b.set_title(T("(b) 类比是一个平行四边形", "(b) An analogy is a parallelogram"), fontsize=10)
b.set_xlabel(T("主方向 1", "component 1"))
b.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
figure(fig, "fig13_1_1")
