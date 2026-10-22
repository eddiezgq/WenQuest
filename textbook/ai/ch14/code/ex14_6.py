"""算例 14.6.1—14.6.4：读图纸与检验报告（14.6 节的案例）。

（1）单个字段读对的比例，与"整份报告七个字段全对"的比例——后者是前者的七次方，这是本案例的要害。
（2）清晰度决定正确率：手机斜着拍的、有折痕的那一批，错得多得多。
（3）按模型自己给出的置信度拒答：覆盖率与正确率的那条曲线（与 11.8、12.7 节同一套做法）。
（4）代价账：自动放行一条错记录要付多少，人工复核一条要付多少，阈值定在哪里总代价最小。
"""
import numpy as np

from _ch14 import FIELDS, read_fields, reports
from bookout import out
from mm_facts import CHARTQA, DOCVQA

v = {}
N = 4000
recs, qual = reports(N, seed=0)
correct, conf = read_fields(recs, qual, seed=0)
v["n_reports"], v["n_fields"] = N, len(FIELDS)
v["field_acc"] = float(correct.mean() * 100)
v["all_ok"] = float(correct.all(1).mean() * 100)
v["pow7"] = float((correct.mean() ** len(FIELDS)) * 100)
assert v["all_ok"] < v["field_acc"], "单字段很准，整份全对就低得多"
v["acc_needed_for_95"] = float(0.95 ** (1 / len(FIELDS)) * 100)   # 想让整份 95% 全对，单字段要多准

# ---------- （2）清晰度分档
rows = []
for lo, hi, name in ((0.0, 0.55, "手机拍的（斜、暗、有折痕）"), (0.55, 1.01, "扫描件")):
    m = (qual >= lo) & (qual < hi)
    if m.sum() == 0:
        continue
    rows.append((name, int(m.sum()), round(float(correct[m].mean() * 100), 1),
                 round(float(correct[m].all(1).mean() * 100), 1)))
v["quality_rows"] = rows
v["acc_bad"], v["acc_good"] = rows[0][2], rows[-1][2]
v["allok_bad"], v["allok_good"] = rows[0][3], rows[-1][3]
assert v["acc_good"] > v["acc_bad"], "清晰度越低，读错得越多"

# ---------- （3）按置信度拒答
rep_conf = conf.prod(1)                                  # 一份报告的把握 = 七个字段的把握相乘（七个都对才算对）
rep_ok = correct.all(1)
rows_t = []
for th in (0.0, 0.4, 0.6, 0.7, 0.8, 0.9):
    take = rep_conf >= th
    cov = float(take.mean() * 100)
    acc = float(rep_ok[take].mean() * 100) if take.any() else float("nan")
    rows_t.append((th, round(cov, 1), round(acc, 1)))
v["thresh_rows"] = rows_t
v["cov_0"], v["acc_0"] = rows_t[0][1], rows_t[0][2]
v["cov_9"], v["acc_9"] = rows_t[-1][1], rows_t[-1][2]
assert v["acc_9"] > v["acc_0"] and v["cov_9"] < v["cov_0"], "拒答能把正确率提上去，代价是覆盖率下降"

# ---------- （4）代价账
C_ERR, C_REVIEW = 20.0, 3.0                              # 放行一条错记录后来要返工的工时；人工复核一条的工时（分钟）
v["c_err"], v["c_review"] = C_ERR, C_REVIEW
ths = np.linspace(0, 0.995, 200)
cost = []
for th in ths:
    take = rep_conf >= th
    wrong = int((take & ~rep_ok).sum())
    cost.append(wrong * C_ERR + int((~take).sum()) * C_REVIEW)
cost = np.array(cost)
best = int(cost.argmin())
v["th_best"] = float(ths[best])
v["cost_best_min"] = float(cost[best]) / 60                 # 换成小时
v["cost_all_auto_min"] = float(cost[0]) / 60                # 全自动放行
v["cost_all_human_min"] = N * C_REVIEW / 60                 # 全人工
v["save_vs_auto"] = v["cost_all_auto_min"] - v["cost_best_min"]
v["save_vs_human"] = v["cost_all_human_min"] - v["cost_best_min"]
take = rep_conf >= v["th_best"]
v["cov_best"] = float(take.mean() * 100)
v["acc_best"] = float(rep_ok[take].mean() * 100)
v["review_best"] = int((~take).sum())
v["wrong_best"] = int((take & ~rep_ok).sum())
assert v["cost_best_min"] < min(v["cost_all_auto_min"], v["cost_all_human_min"]), "带拒答的方案比两个极端都便宜"
# 代价之比变了，阈值跟着变（与 11.8、12.7 节同一条结论）
alt = []
for ce in (10.0, 20.0, 40.0):
    c = np.array([int(((rep_conf >= t) & ~rep_ok).sum()) * ce + int((rep_conf < t).sum()) * C_REVIEW for t in ths])
    alt.append((ce, round(float(ths[int(c.argmin())]), 3), round(float((rep_conf >= ths[int(c.argmin())]).mean() * 100), 1)))
v["cost_rows"] = alt
for (ce, th, cov), tag in zip(alt, ("10", "20", "40")):
    v[f"th{tag}"], v[f"cov{tag}"] = th, cov
assert alt[0][1] < alt[-1][1], "错一条的代价越高，阈值定得越严、自动放行的越少"

# ---------- 公开基准的口径（放在一起提醒：别拿不同指标比）
v["docvqa_q"] = DOCVQA["questions"]
v["docvqa_human_anls"], v["docvqa_human_acc"] = DOCVQA["human_anls"], DOCVQA["human_acc"]
v["docvqa_bert_anls"], v["docvqa_bert_acc"] = DOCVQA["bert_anls"], DOCVQA["bert_acc"]
v["chartqa_tol"] = CHARTQA["tolerance_pct"]
v["chartqa_best"] = CHARTQA["best_all"]
out(**v)
