"""算例 12.3.1—12.3.2：CTC 怎样绕开对齐（12.3 节）。

端到端识别的第一个难处：模型每 10 ms 输出一次，而标注只有一句话的文字——哪个字对应哪几帧，没人标。
CTC（连接时序分类）的办法是：不指定对齐，把所有能折叠成目标文字的路径的概率加起来，最大化这个和。
折叠规则两条：先去掉相邻的重复，再去掉空白符。

（1）前向算法与穷举求和核对（本章最值得自己写一遍的东西）：6 帧、3 个符号时，穷举全部 3⁶ 条路径，
    把能折叠成目标的挑出来求和，与前向算法的结果逐位比较；
（2）帧数增加时能折叠成同一目标的路径有多少条——这就是不能穷举的原因；
（3）贪心解码与折叠：模型每帧取最大的那个符号，再折叠；叠字必须在两个字之间留一帧空白，否则被并成一个。
"""
import itertools

import numpy as np

from _ch12 import ctc_forward, ctc_greedy
from bookout import out

BLANK = 0
rng = np.random.default_rng(123)
V, T = 3, 6                                                  # 符号表：0 空白、1 "开"、2 "停"
logp = np.log(rng.dirichlet(np.ones(V), T))
target = [1, 2]


def collapse(path):
    out_, prev = [], -1
    for c in path:
        if c != prev and c != BLANK:
            out_.append(c)
        prev = c
    return out_


# ---------- （1）穷举核对
tot, n_match = -np.inf, 0
for p in itertools.product(range(V), repeat=T):
    if collapse(list(p)) == target:
        n_match += 1
        tot = np.logaddexp(tot, sum(logp[t, c] for t, c in enumerate(p)))
fw = ctc_forward(logp, target, BLANK)
assert abs(fw - tot) < 1e-9, (fw, tot)
v = {"n_paths": V ** T, "n_match": n_match, "logp_fw": fw, "logp_enum": float(tot)}

# ---------- （2）路径数随帧数增长：帧数一加，路径数就炸，所以只能递推、不能穷举
for t in (6, 10):
    v[f"match_{t}"] = sum(1 for p in itertools.product(range(V), repeat=t) if collapse(list(p)) == target)

# ---------- （3）贪心解码与叠字
greedy = ctc_greedy(logp, BLANK)
v["greedy"] = "".join(str(c) for c in greedy)
# 叠字的例子：目标是“停停”（两个相同的符号），折叠会把它们并成一个——除非中间隔一个空白符
good = np.full((4, V), -9.0)
good[0, 2] = good[1, BLANK] = good[2, 2] = good[3, BLANK] = -0.01   # 停 空 停 空
bad = np.full((4, V), -9.0)
bad[0, 2] = bad[1, 2] = bad[2, 2] = bad[3, 2] = -0.01              # 停 停 停 停
v["good_out"] = "".join(str(c) for c in ctc_greedy(np.log(np.exp(good) / np.exp(good).sum(1, keepdims=True)), BLANK))
v["bad_out"] = "".join(str(c) for c in ctc_greedy(np.log(np.exp(bad) / np.exp(bad).sum(1, keepdims=True)), BLANK))
v["bad_len"] = len(ctc_greedy(np.log(np.exp(bad) / np.exp(bad).sum(1, keepdims=True)), BLANK))
out(**v)
