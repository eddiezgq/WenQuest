"""算例 17.2.1—17.2.3：仓库装不进上下文，怎么选（17.2 节）。

（1）先算一笔账：一个典型仓库有多大，上下文装得下多少。
（2）三种选法在同一个任务上的命中率：按最近编辑、按词面检索、按符号图扩展。
（3）预算一紧，差距更明显——而且"把能装的都装上"并不是最好的用法。
"""
import numpy as np

from _ch17 import (make_repo, make_task, recall, select_lexical, select_recent,
                   select_symbol_graph)
from agent_facts import SWEBENCH, TOOLS
from bookout import out

v = {}

# ---------- （1）仓库有多大
v["files"], v["lines_k"] = SWEBENCH["files_mean"], SWEBENCH["lines_mean_k"]
v["files_max"], v["lines_max_k"] = SWEBENCH["files_max"], SWEBENCH["lines_max_k"]
v["patch_files"], v["patch_lines"] = SWEBENCH["patch_files"], SWEBENCH["patch_lines"]
v["issue_words"] = SWEBENCH["issue_words_mean"]
v["pick_ratio"] = SWEBENCH["files_mean"] / SWEBENCH["patch_files"]      # 折算
v["repo_tokens_known"] = SWEBENCH["repo_tokens"] is not None
assert not v["repo_tokens_known"], "'典型仓库多少词元'没有任何论文给过，本书只写行数与文件数"
v["bm25_budgets"] = SWEBENCH["bm25_budgets_k"]
v["everything_counts"] = TOOLS["everything_counts"]

# ---------- （2）三种选法
BUDGETS = (10_000, 30_000, 100_000)
SEEDS = 12
v["n_seeds"] = SEEDS
v["rows"] = []
res: dict[tuple[str, int], float] = {}
for budget in BUDGETS:
    for name, fn, kw in (("按最近编辑", select_recent, {}),
                         ("按词面检索", select_lexical, {}),
                         ("符号图（一跳）", select_symbol_graph, {"hops": 1}),
                         ("符号图（两跳）", select_symbol_graph, {"hops": 2})):
        rc, nf = [], []
        for s in range(SEEDS):
            repo = make_repo(seed=s)
            task = make_task(repo, seed=s)
            sel, used = fn(repo, task, budget, **kw)
            rc.append(recall(sel, task))
            nf.append(len(sel))
        res[(name, budget)] = float(np.mean(rc))
        v["rows"].append((name, budget, round(float(np.mean(rc)), 3), int(np.mean(nf))))

for tag, name in (("recent", "按最近编辑"), ("lex", "按词面检索"),
                  ("g1", "符号图（一跳）"), ("g2", "符号图（两跳）")):
    for b in BUDGETS:
        v[f"r_{tag}_{b // 1000}k"] = round(res[(name, b)], 3)

assert v["r_recent_30k"] < 0.1, "按最近编辑等于没选——改动在哪与谁最近被改过没关系"
assert v["r_lex_30k"] > 0.5, "词面检索能找到定义处与直接调用方"
assert v["r_g2_30k"] > v["r_lex_30k"] + 0.2, \
    "两跳才跟得上'调用方自己又被谁用了'这条链——这正是真实改动的样子"
assert v["r_g1_30k"] <= v["r_g2_30k"], "一跳不够"
v["gain_g2_over_lex"] = (v["r_g2_30k"] - v["r_lex_30k"]) * 100

# ---------- （3）预算的影响
v["budget_small"], v["budget_big"] = BUDGETS[0], BUDGETS[-1]
v["g2_small"], v["g2_big"] = v["r_g2_10k"], v["r_g2_100k"]
v["lex_small"], v["lex_big"] = v["r_lex_10k"], v["r_lex_100k"]
assert v["g2_big"] > v["g2_small"], "预算大一点，链子跟得更全"
assert abs(v["lex_big"] - v["lex_small"]) < 0.1, \
    "选法不对时，预算加十倍也没用——这一条比'上下文越长越好'要紧"
v["lex_budget_gain"] = (v["lex_big"] - v["lex_small"]) * 100
v["g2_budget_gain"] = (v["g2_big"] - v["g2_small"]) * 100

out(**v)
