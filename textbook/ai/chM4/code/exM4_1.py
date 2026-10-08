"""算例 M4.1.1—M4.1.3：信息量与熵（M4.1 节）。

熵回答一个很具体的问题：平均每个符号至少要用多少比特才能存下来。
本程序在三个地方把它算出来：公平的硬币、车间的三类缺陷、一个小"语言模型"的词表；
最后用一段真实的编码（霍夫曼码）核对——熵确实是编码长度的下界。
"""
import heapq

import numpy as np

from _chM4 import toy_lm
from bookout import out

v = {}
LOG2 = np.log(2)


def H(p):
    p = np.asarray(p, dtype=float)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


# ---------- （1）几个最简单的例子
v["H_coin"] = H([0.5, 0.5])
v["H_biased"] = H([0.9, 0.1])
v["H_sure"] = abs(H([1.0, 0.0]))     # −0.0 也是 0
v["H_8"] = H([1 / 8] * 8)
assert abs(v["H_coin"] - 1) < 1e-12 and abs(v["H_8"] - 3) < 1e-12 and v["H_sure"] == 0

# ---------- （2）车间的三类缺陷
p = np.array([0.55, 0.30, 0.15])
v["p"] = [round(float(a), 2) for a in p]
v["H_defect"] = H(p)
v["H_defect_max"] = float(np.log2(3))                      # 三类等概率时最大
v["bits_each"] = [round(float(-np.log2(a)), 2) for a in p]  # 各自的信息量：越少见的事，信息量越大
v["eff"] = v["H_defect"] / v["H_defect_max"] * 100

# ---------- （3）霍夫曼码：熵是下界，而且差不到 1 比特
def huffman_len(probs):
    """构造霍夫曼码，返回平均码长（比特）。"""
    h = [(float(q), i, None, None) for i, q in enumerate(probs)]
    heapq.heapify(h)
    while len(h) > 1:
        a = heapq.heappop(h)
        b = heapq.heappop(h)
        heapq.heappush(h, (a[0] + b[0], -1, a, b))
    depth = {}

    def walk(node, d):
        if node[1] >= 0:
            depth[node[1]] = max(d, 1)
            return
        walk(node[2], d + 1)
        walk(node[3], d + 1)

    walk(h[0], 0)
    return float(sum(probs[i] * depth[i] for i in range(len(probs))))


v["huff_defect"] = huffman_len(p)
v["huff_gap"] = v["huff_defect"] - v["H_defect"]
assert v["H_defect"] <= v["huff_defect"] < v["H_defect"] + 1, "香农：熵 ≤ 平均码长 < 熵 + 1"

# ---------- （4）一个词表上的熵：长尾让熵变大
p_lm, q_lm, tokens = toy_lm()
v["vocab"] = len(p_lm)
v["H_lm"] = H(p_lm)
v["H_lm_max"] = float(np.log2(len(p_lm)))
v["H_lm_pct"] = v["H_lm"] / v["H_lm_max"] * 100
v["huff_lm"] = huffman_len(p_lm)
v["huff_lm_gap"] = v["huff_lm"] - v["H_lm"]
assert v["H_lm"] <= v["huff_lm"] < v["H_lm"] + 1
v["fixed_bits"] = int(np.ceil(np.log2(len(p_lm))))          # 定长编码要几位
v["save_pct"] = (v["fixed_bits"] - v["huff_lm"]) / v["fixed_bits"] * 100
out(**v)
