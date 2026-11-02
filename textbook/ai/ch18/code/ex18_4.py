"""算例 18.4.1—18.4.3：蛋白质设计——大多数形状根本没有序列能折成（18.4 节）。

格点上能把这件事**穷尽**：12 个残基有 4096 条序列、1113 个不同的结构。于是可以逐条问：
（1）有多少条序列真的有唯一的基态？
（2）这些序列落在多少个不同的结构上？——"可设计性"。
（3）反过来，给一个目标结构，随手挑一条序列能折成它的概率是多少，按结构去挑又是多少。
"""
import collections

import numpy as np

from _ch18 import (all_sequences, contacts, design_sequence, designability,
                   enumerate_folds, fold_energy, unique_structures)
from bio_facts import DESIGN
from bookout import out

N = 12
v = {"n_res": N}

folds_all = enumerate_folds(N)
reps, fc = unique_structures(folds_all, [contacts(f) for f in folds_all])
v["n_walks"] = len(folds_all)
v["n_structures"] = len(fc)
v["n_sequences"] = 2 ** N
assert v["n_structures"] < v["n_walks"] / 10, "按接触图去重之后，结构数比走法数少一个量级"

# ---------- （1）（2）可设计性
lo, deg, arg = designability(N, fc)
uniq = deg == 1
v["n_unique"] = int(uniq.sum())
v["unique_pct"] = float(uniq.mean() * 100)
cnt = collections.Counter(arg[uniq].tolist())
v["n_folded_structures"] = len(cnt)
v["folded_pct"] = len(cnt) / v["n_structures"] * 100
counts = np.array(sorted(cnt.values(), reverse=True))
v["top_designability"] = int(counts[0])
v["median_designability"] = float(np.median(counts))
v["only_one_pct"] = float((counts == 1).mean() * 100)
v["des_rows"] = [(int(c), int((counts == c).sum())) for c in sorted(set(counts.tolist()))]

assert v["unique_pct"] < 10, \
    "绝大多数序列根本没有唯一的基态——'随便一条链都会折成一个确定的形状'是不对的"
assert v["folded_pct"] < 10, \
    "有唯一基态的那些序列，还全挤在少数几个结构上——这就是'可设计性'"
assert v["top_designability"] > 3 * v["median_designability"], \
    "少数结构被很多条序列折成，大多数结构一条都没有"

# ---------- （3）反向折叠：给目标结构找序列
best_struct = cnt.most_common(1)[0][0]
v["best_struct_seqs"] = int(cnt[best_struct])
v["random_hit_pct"] = v["best_struct_seqs"] / v["n_sequences"] * 100

seqs = all_sequences(N)
designed = design_sequence(fc[best_struct], N)
v["designed_seq"] = designed
bits = np.array([1 if ch == "H" else 0 for ch in designed], dtype=np.int8)
row = int(np.where((seqs == bits).all(1))[0][0])
v["designed_deg"] = int(deg[row])
v["designed_hits"] = bool(deg[row] == 1 and arg[row] == best_struct)

# 按结构去挑，在全部 37 个"能被折成"的结构上试一遍，成功几个
ok = 0
for st in cnt:
    s = design_sequence(fc[st], N)
    b = np.array([1 if ch == "H" else 0 for ch in s], dtype=np.int8)
    r = int(np.where((seqs == b).all(1))[0][0])
    if deg[r] == 1 and arg[r] == st:
        ok += 1
v["design_tries"] = len(cnt)
v["design_ok"] = ok
v["design_ok_pct"] = ok / len(cnt) * 100
v["design_over_random"] = v["design_ok_pct"] / v["random_hit_pct"]      # 折算

assert v["design_ok_pct"] > 10 * v["random_hit_pct"], \
    "按结构去挑序列，比随手挑高出两三个量级——但也远不是百发百中"
assert v["design_ok_pct"] < 100, "就算按结构挑，也有相当一部分目标做不出来"

# ---------- 口径：真实论文的成功率怎么写
v["denominator_note"] = DESIGN["note"]

out(**v)
