"""算例 13.1.1—13.1.3：词怎样变成向量（13.1 节）。

（1）独热编码的账：词表有多大，一个词就占多少维；一句话变成矩阵有多大，里面有多少个零。
（2）中文怎样切：按字、按字二元组、按分词器，词元数与“同一个词是否对得上”的差别。
（3）在程序生成的小语料上训一个 skip-gram（`_ch13.skipgram`，NumPy 写的负采样），
    看三件事：同类词靠得近、类比关系真的成立（精轴 − 粗轴 + 粗齿轮 ≈ 精齿轮）、
    以及词向量的参数量比独热编码的字典小多少。
"""
import numpy as np

from _ch13 import BASE, GRADE, corpus, cos, nearest, skipgram, tokens
from bookout import out

v = {}
# ---------- （1）独热编码的账
V, DIM, SENT = 50_000, 300, 20            # 词表 5 万、词向量 300 维、一句话 20 个词
v["vocab"], v["dim"], v["sent_len"] = V, DIM, SENT
v["onehot_floats"] = V * SENT             # 一句话的独热矩阵有多少个数
v["onehot_MB"] = V * SENT * 4 / 1e6       # 按单精度存
v["onehot_nonzero"] = SENT                # 其中非零的只有 20 个
v["onehot_sparsity"] = (1 - SENT / (V * SENT)) * 100
v["dense_floats"] = DIM * SENT
v["dense_kB"] = DIM * SENT * 4 / 1e3
v["shrink"] = v["onehot_floats"] / v["dense_floats"]
v["table_M"] = V * DIM / 1e6              # 词向量表本身的参数量（百万）
v["table_MB"] = V * DIM * 4 / 1e6
# 独热编码还有一个更要紧的毛病：任何两个不同的词，内积都是 0——“轴”与“轴颈”和“轴”与“螺栓”一样远
v["onehot_cos_any"] = 0.0

# ---------- （2）中文怎样切
S = "SH-301 输出轴两端轴颈对公共基准的同轴度公差为 0.02 mm"
v["sample"] = S
v["n_char"] = sum(1 for c in S if "一" <= c <= "鿿")
tk = tokens(S)
v["n_token"] = len(tk)
v["n_bigram"] = v["n_token"] - v["n_char"] - len([w for w in tk if w[0].isascii()])
v["has_number"] = "0.02" in tk and "sh-301" in tk
# 分词器把“同轴度”切成一个词时，问句里写“同轴”就对不上；用字二元组时“同轴”与“轴度”都还在
v["bigram_covers"] = "同轴" in tk and "轴度" in tk

# ---------- （3）训一个词向量
sents = corpus()
v["corpus_sent"] = len(sents)
v["corpus_token"] = sum(len(s) for s in sents)
ix, W = skipgram(sents)
v["w_vocab"], v["w_dim"] = len(ix), W.shape[1]
v["w_params"] = W.size

same = [cos(W[ix[g + b]], W[ix[g2 + b]]) for b in BASE for g in GRADE for g2 in GRADE if g != g2]
diff = [cos(W[ix[g + b]], W[ix[g + b2]]) for g in GRADE for b in BASE for b2 in BASE if b != b2]
v["cos_same_part"] = float(np.mean(same))     # 同一个零件、不同等级
v["cos_same_grade"] = float(np.mean(diff))    # 同一个等级、不同零件
nb = nearest(ix, W, W[ix["精轴"]], skip={"精轴"}, n=1)[0]
v["near_jingzhou"], v["near_jingzhou_cos"] = nb[0], nb[1]

ok, tot, examples = 0, 0, []
for b1 in BASE:
    for b2 in BASE:
        if b1 == b2:
            continue
        tot += 1
        q = W[ix["精" + b1]] - W[ix["粗" + b1]] + W[ix["粗" + b2]]
        best = nearest(ix, W, q, skip={"精" + b1, "粗" + b1, "粗" + b2}, n=1)[0]
        ok += best[0] == "精" + b2
        if len(examples) < 1:
            examples.append((b1, b2, best[0]))
v["ana_total"], v["ana_ok"] = tot, ok
v["ana_pct"] = 100 * ok / tot
v["ana_b1"], v["ana_b2"], v["ana_got"] = examples[0]
assert ok == tot, "类比应当全对；不对就是训练发散或语料的结构被改坏了"
out(**v)
