"""算例 13.2.1—13.2.3：序列到序列、注意力与 BLEU（13.2 节）。

（1）定长向量的瓶颈：编码器把整句话压进一个固定长度的向量，句子越长、每个词摊到的位数越少——
    这是注意力出现之前的硬限制，也是 Bahdanau 那篇论文里“长句掉得最厉害”的原因。
（2）注意力的代价：源长 × 目标长 次打分与一个同样大小的权重矩阵（回扣 2.8 节与 9.4 节）。
（3）BLEU 怎么算、为什么换个切法分数就变：自己实现 BLEU（`_ch13.bleu`），
    先用一个手算得出的例子核对，再把同一对句子按词、按字切两遍，比较分数。
"""
import math

from _ch13 import bleu
from bookout import out
from llm_facts import ATTN_BLEU, SEQ2SEQ, SEQ2SEQ_PAIRS, SEQ2SEQ_PARAMS, TRANSFORMER

v = {}
# ---------- （1）定长向量的瓶颈
D, BITS = 1000, 32                        # Sutskever 等用的是 4 层 × 1000 单元；按单精度存
for L in (5, 20, 50):
    v[f"bits_per_word_{L}"] = D * BITS / L
v["d_state"] = D
v["bits_total"] = D * BITS
v["bits_ratio"] = (D * BITS / 5) / (D * BITS / 50)
# 论文给出的数字：加了注意力之后，长句的 BLEU 才追上统计机器翻译
v["rnnsearch_all"], v["rnnsearch_nounk"] = ATTN_BLEU["rnnsearch50"]
v["rnnencdec_all"], v["rnnencdec_nounk"] = ATTN_BLEU["rnnencdec50"]
v["moses_all"], v["moses_nounk"] = ATTN_BLEU["moses"]
v["attn_gain"] = v["rnnsearch_all"] - v["rnnencdec_all"]
v["unk_gap"] = v["rnnsearch_nounk"] - v["rnnsearch_all"]        # 同一个系统，换个子集差多少
v["s2s_single"], v["s2s_ens"] = SEQ2SEQ["single_lstm_beam12"], SEQ2SEQ["ensemble5_beam12"]
v["s2s_smt"], v["s2s_rerank"] = SEQ2SEQ["smt_baseline"], SEQ2SEQ["rerank_1000best"]
v["s2s_params_M"] = SEQ2SEQ_PARAMS / 1e6
v["s2s_pairs_M"] = SEQ2SEQ_PAIRS / 1e6

# ---------- （2）注意力的代价
T_SRC, T_TGT = 50, 60
v["t_src"], v["t_tgt"] = T_SRC, T_TGT
v["attn_scores"] = T_SRC * T_TGT                                # 打分次数 = 权重矩阵的元素个数
v["attn_flops_M"] = 2 * T_SRC * T_TGT * D / 1e6                 # 每次打分一个 d 维内积（乘加各算一次）
v["attn_vs_decode"] = (T_SRC * T_TGT) / T_TGT                   # 每生成一个词，要看源句的每个位置
# Transformer 把循环换成并行：同样的注意力，一层里所有位置一起算（2.8 节），论文给出的训练成本如下
v["tr_base_flops"], v["tr_big_flops"] = TRANSFORMER["base"]["flops"], TRANSFORMER["big"]["flops"]
v["tr_base_ende"], v["tr_big_ende"] = TRANSFORMER["base"]["ende"], TRANSFORMER["big"]["ende"]
v["tr_base_params_M"] = TRANSFORMER["base"]["params"] / 1e6
v["tr_big_params_M"] = TRANSFORMER["big"]["params"] / 1e6
v["tr_flops_ratio"] = TRANSFORMER["big"]["flops"] / TRANSFORMER["base"]["flops"]
v["tr_bleu_gain"] = TRANSFORMER["big"]["ende"] - TRANSFORMER["base"]["ende"]
v["tr_base_hours"], v["tr_big_hours"] = TRANSFORMER["base"]["hours"], TRANSFORMER["big"]["hours"]

# ---------- （3）BLEU
# 手算核对：参考 "a b c d"，译文 "a b c e"。1 元组 3/4，2 元组 2/3，3 元组 1/2，4 元组 0/1 → 分数为 0
ref_w = ["a", "b", "c", "d"]
hyp_w = ["a", "b", "c", "e"]
v["p1"], v["p2"], v["p3"] = 3 / 4, 2 / 3, 1 / 2
v["bleu_zero"] = bleu(ref_w, hyp_w)                             # 有一个 n 元组精确率为 0，几何平均就是 0
assert v["bleu_zero"] == 0.0
v["bleu3_hand"] = math.exp((math.log(3 / 4) + math.log(2 / 3) + math.log(1 / 2)) / 3)
v["bleu3_prog"] = bleu(ref_w, hyp_w, n_max=3)                   # 只算到 3 元组时与手算一致
assert abs(v["bleu3_hand"] - v["bleu3_prog"]) < 1e-12
# 长度惩罚：译文短了要罚
v["bleu_short"] = bleu(ref_w, ["a", "b"], n_max=2)
v["bp_short"] = math.exp(1 - 4 / 2)

# 同一对中文句子，按词切与按字切，分数差多少
REF_SEG = ["输出轴", "的", "同轴度", "公差", "为", "0.02", "毫米"]
HYP_SEG = ["输出轴", "的", "同轴度", "允许", "0.02", "毫米"]
v["bleu_word"] = bleu(REF_SEG, HYP_SEG, n_max=3)
ref_c = list("输出轴的同轴度公差为0.02毫米")
hyp_c = list("输出轴的同轴度允许0.02毫米")
v["bleu_char"] = bleu(ref_c, hyp_c, n_max=3)
v["bleu_gap"] = abs(v["bleu_char"] - v["bleu_word"])
v["bleu_ratio"] = max(v["bleu_char"], v["bleu_word"]) / max(min(v["bleu_char"], v["bleu_word"]), 1e-9)
out(**v)
