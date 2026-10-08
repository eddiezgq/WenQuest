"""算例 13.6.1—13.6.4：检索增强（13.6 节）。

手册由程序生成（`_ch13.manual`：{条文数} 条、{页数} 页，其中几百条字面几乎一样、只是零件号与数值不同），
问答对与标准答案的出处也由程序给出。四件事：

（1）切多长、重叠多少：切片长度与重叠对召回率的影响，以及它同时带来的代价（送进模型的词元数）。
（2）三种检索与两种问法：按词频（BM25）、按向量、两者混合；问题用手册原词问，与工人在现场的口语问法。
    这里的"向量检索"是一个**没有语义**的哈希向量（`_ch13.embed`，不需要模型、在任何机器上结果相同），
    所以它在口语问法上反而更差——这正好说明：向量检索的本事来自模型，不来自"向量"这个形式。
    真的句向量模型在 GPU 实验 13.6 里测。
（3）工程上的两招：一张几十条的同义词表，和"问题里出现零件号就给含该号的片子加权"。
（4）答不出来要承认：手册里没有规定的问题，检索分数明显偏低——按分数设一个阈值就能拒答。
"""
import numpy as np

from _ch13 import (SYNONYMS, bm25, chunks, coverage, document, expand, idf_coverage, manual,
                   manual_coverage, questions, recall, retrieve, vector_scores)
from bookout import out

v = {}
man = manual()
qs = questions()
ANS = [q for q in qs if q["answerable"]]
NOANS = [q for q in qs if not q["answerable"]]
text, _ = document(man)
v["n_clause"], v["n_page"], v["n_char"] = len(man), man[-1]["page"], len(text)
v["n_q"], v["n_ans"], v["n_noans"] = len(qs), len(ANS), len(NOANS)
v["n_obsolete"] = sum(1 for c in man if c["obsolete"])

# ---------- （1）切多长、重叠多少
K = 5
v["k"] = K
for size, ov in ((150, 30), (300, 60), (600, 120), (1200, 240)):
    ch = chunks(man, size, ov)
    rc = np.mean([recall(retrieve(q["q"], ch, K, "bm25"), ch, q["gold"]) for q in ANS])
    key = f"s{size}"
    v[key + "_n"] = len(ch)
    v[key + "_recall"] = float(rc) * 100
    v[key + "_tok"] = size * K / 1.5                       # 送进模型的词元数（中文约 1.5 字一个词元）
v["size_best"] = max((v[f"s{s}_recall"], s) for s in (150, 300, 600, 1200))[1]
v["tok_ratio"] = v["s1200_tok"] / v["s150_tok"]
v["recall_gain_size"] = v["s1200_recall"] - v["s150_recall"]   # 切片放大 8 倍，召回只多这么几个点

CH = chunks(man, 300, 60)
v["chunks"] = len(CH)
v["chunk_chars"] = 300
v["overlap"] = 60
# 重叠的作用：条文被切断时，重叠能把编号与数值重新拼到一片里
for ov in (0, 60, 150):
    ch = chunks(man, 300, ov)
    rc = np.mean([recall(retrieve(q["q"], ch, K, "bm25"), ch, q["gold"]) for q in ANS])
    v[f"ov{ov}_recall"] = float(rc) * 100
    v[f"ov{ov}_n"] = len(ch)
v["ov_gain"] = v["ov150_recall"] - v["ov0_recall"]

# ---------- （2）三种检索 × 两种问法
METHODS = ("bm25", "vector", "hybrid")
for field, tag in (("q", "book"), ("q2", "shop")):
    for how in METHODS:
        hits, rcs = [], []
        for q in ANS:
            idx = retrieve(q[field], CH, K, how)
            got = {c.split("(")[0] for i in idx for c in CH[i]["srcs"]}
            hits.append(any(g in got for g in q["gold"]))
            rcs.append(recall(idx, CH, q["gold"]))
        v[f"{tag}_{how}_hit"] = 100 * sum(hits) / len(hits)
        v[f"{tag}_{how}_recall"] = 100 * float(np.mean(rcs))
v["drop_bm25"] = v["book_bm25_recall"] - v["shop_bm25_recall"]
v["drop_vector"] = v["book_vector_recall"] - v["shop_vector_recall"]
v["vector_worse"] = v["shop_bm25_recall"] - v["shop_vector_recall"]

# ---------- （3）工程上的两招
v["n_syn"] = len(SYNONYMS)
for how in ("bm25+syn", "bm25+part", "bm25+syn+part", "hybrid+syn+part"):
    rcs = [recall(retrieve(q["q2"], CH, K, how), CH, q["gold"]) for q in ANS]
    v["shop_" + how.replace("+", "_") + "_recall"] = 100 * float(np.mean(rcs))
v["syn_gain"] = v["shop_bm25_syn_part_recall"] - v["shop_bm25_recall"]
v["combo_gain"] = v["shop_hybrid_syn_part_recall"] - v["shop_bm25_recall"]
v["combo_best"] = v["shop_hybrid_syn_part_recall"] >= v["shop_bm25_recall"]
assert v["combo_best"], "组合手段应当不差于单一的词频检索"

# ---------- （4）答不出来要承认：三种信号哪个管用
def split_quality(a, b):
    """扫一个阈值，返回（最优阈值, 判对的个数, 两类的重叠宽度）：该答的答、该拒的拒。"""
    cands = np.unique(np.concatenate([a, b]))
    best_t, best_ok = 0.0, -1
    for t in cands:
        ok = int((a >= t).sum() + (b < t).sum())
        if ok > best_ok:
            best_ok, best_t = ok, float(t)
    return best_t, best_ok, float(max(b) - min(a))


SIGNALS = {
    "score": lambda q: float(np.max(bm25(q, CH))),                                   # 检索分数
    "cover": lambda q: max(coverage(expand(q), CH[i]) for i in retrieve(q, CH, K, "bm25")),   # 片内覆盖率
    "idf": lambda q: idf_coverage(expand(q), CH),                                    # 逆文档频率加权的手册覆盖率
}
v["reject_total"] = len(ANS) + len(NOANS)
for name, fn in SIGNALS.items():
    for field, tag in (("q", "book"), ("q2", "shop")):
        a = np.array([fn(q[field]) for q in ANS])
        b = np.array([fn(q[field]) for q in NOANS])
        t, ok, ovl = split_quality(a, b)
        v[f"{tag}_{name}_t"] = t
        v[f"{tag}_{name}_acc"] = 100 * ok / v["reject_total"]
        v[f"{tag}_{name}_overlap"] = ovl                      # > 0 表示两类的取值范围有重叠，一个阈值分不干净
        v[f"{tag}_{name}_ans_min"] = float(a.min())
        v[f"{tag}_{name}_noans_max"] = float(b.max())
v["best_signal_book"] = max(SIGNALS, key=lambda nm: v[f"book_{nm}_acc"])
v["best_signal_shop"] = max(SIGNALS, key=lambda nm: v[f"shop_{nm}_acc"])
v["book_idf_better"] = v["book_idf_acc"] >= v["book_score_acc"]
v["shop_all_overlap"] = all(v[f"shop_{nm}_overlap"] > 0 for nm in SIGNALS)
assert v["book_idf_better"], "按逆文档频率加权的覆盖率应当不差于只看检索分数"
v["noans_total"] = len(NOANS)
v["manual_cover_ans"] = float(np.mean([manual_coverage(expand(q["q"]), CH) for q in ANS]))
v["manual_cover_noans"] = float(np.mean([manual_coverage(expand(q["q"]), CH) for q in NOANS]))

# 代价：按 k 片 × 每片 300 字折成词元，再按一个常见的接口价格折成钱（单价是教材假设）
PRICE_PER_MTOK = 2.0
v["price_per_Mtok"] = PRICE_PER_MTOK
for k in (3, 5, 10, 20):
    rcs = [recall(retrieve(q["q2"], CH, k, "hybrid+syn+part"), CH, q["gold"]) for q in ANS]
    v[f"k{k}_recall"] = 100 * float(np.mean(rcs))
    v[f"k{k}_tok"] = k * 300 / 1.5 + 200                   # 片子 + 问题与提示
    v[f"k{k}_cost_per_1k"] = v[f"k{k}_tok"] * 1000 / 1e6 * PRICE_PER_MTOK
v["k_gain_3_20"] = v["k20_recall"] - v["k3_recall"]
v["k_cost_ratio"] = v["k20_cost_per_1k"] / v["k3_cost_per_1k"]
# 把整本手册塞进上下文要多少词元（与检索比）
v["all_tok"] = v["n_char"] / 1.5
v["all_cost_per_1k"] = v["all_tok"] * 1000 / 1e6 * PRICE_PER_MTOK
v["all_vs_k5"] = v["all_cost_per_1k"] / v["k5_cost_per_1k"]
out(**v)
