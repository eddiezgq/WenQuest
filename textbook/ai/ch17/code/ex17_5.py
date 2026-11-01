"""算例 17.5.1—17.5.3：工具一多会怎样（17.5 节）。

（1）工具定义吃掉的词元：官方只给了"启用工具"这一项固定开销，工具本身占多少没公布，
     本节的每工具词元数是假设值，正文要标明。
（2）在一堆工具里挑对的那个越来越难——这是极值统计，不是模型笨。
（3）两条出路：分组（先挑一类再挑具体工具）与按需加载。两条都能算出收益。
"""
import numpy as np

from _ch17 import tool_budget, tool_pick_accuracy
from agent_facts import CACHE, TOOLS
from bookout import out

v = {}
PER_TOOL = 120          # 假设：一个工具的名称 + 说明 + 入参 schema 约 120 词元
SYS_OVERHEAD = TOOLS["system_overhead"]["Claude Opus 5.5"][0]
v["per_tool_assumed"] = PER_TOOL
v["sys_overhead"] = SYS_OVERHEAD
v["per_tool_official"] = TOOLS["per_tool_tokens"] is not None
assert not v["per_tool_official"], "单个工具定义占多少词元，官方文档不给数字——这一项是假设值"
v["hard_limit_official"] = TOOLS["anthropic_hard_limit"] is not None
assert not v["hard_limit_official"], "工具数量的硬上限也不给"
v["soft_limit"] = TOOLS["openai_soft_limit"]
v["soft_is_soft"] = TOOLS["openai_soft_limit_is_soft"]
v["overhead_table"] = [(m, a, b) for m, (a, b) in TOOLS["system_overhead"].items()]
v["overhead_min"] = min(a for a, _ in TOOLS["system_overhead"].values())
v["overhead_max"] = max(a for a, _ in TOOLS["system_overhead"].values())

# ---------- （1）（2）工具一多，两件事同时变坏
v["rows"] = []
for m in (5, 10, 20, 50, 100, 200):
    acc = tool_pick_accuracy(m)
    tok = tool_budget(m, PER_TOOL, SYS_OVERHEAD)
    v["rows"].append((m, round(acc, 3), tok))
    v[f"acc_{m}"], v[f"tok_{m}"] = round(acc, 3), tok
assert v["acc_200"] < 0.5 * v["acc_5"], "工具越多越难挑——噪声里冒出更高分的机会变多了"
v["acc_drop_pts"] = (v["acc_5"] - v["acc_200"]) * 100
v["tok_growth"] = v["tok_200"] / v["tok_5"]
# 一个 20 轮的会话里，光工具定义就要重送多少次（缓存之前）
TURNS = 20
v["turns"] = TURNS
v["tok_200_20turns_w"] = v["tok_200"] * TURNS / 1e4
v["tools_cacheable"] = CACHE["tools_cacheable"]
assert v["tools_cacheable"], "工具定义是可以缓存的前缀——这正是它该被缓存的理由"

# ---------- （3）两条出路
# 甲：分组。先在 G 个大类里挑一类，再在类内 m/G 个工具里挑一个。两次都要挑对。
v["group_rows"] = []
M = 200
for G in (1, 5, 10, 20):
    per = max(2, M // G)
    acc = tool_pick_accuracy(G) * tool_pick_accuracy(per) if G > 1 else tool_pick_accuracy(M)
    v["group_rows"].append((G, per, round(acc, 3)))
    v[f"grp_{G}"] = round(acc, 3)
v["grp_best"] = max(v["grp_5"], v["grp_10"], v["grp_20"])
assert v["grp_best"] > v["grp_1"], "分两步挑，总的挑对率反而更高——两次小选择好过一次大选择"
v["group_gain_pts"] = (v["grp_best"] - v["grp_1"]) * 100

# 乙：按需加载。平时只挂 k 个常用工具，要别的再去找。
v["ondemand_rows"] = []
for k in (5, 10, 20):
    tok = tool_budget(k, PER_TOOL, SYS_OVERHEAD)
    v["ondemand_rows"].append((k, tok, round(tool_pick_accuracy(k), 3)))
    v[f"od_tok_{k}"], v[f"od_acc_{k}"] = tok, round(tool_pick_accuracy(k), 3)
v["od_save"] = v["tok_200"] - v["od_tok_10"]
assert v["od_save"] > 20000 - 1500, "按需加载省下的词元是实打实的"
v["od_save_w"] = v["od_save"] / 1e4

out(**v)
