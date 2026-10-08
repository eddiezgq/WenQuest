"""算例 13.9.1—13.9.4：质量手册问答助手（13.9 节）。

把 13.6 节的零件装成一条完整的线：切片 → 检索（混合 + 同义词表 + 零件号加权）→ 覆盖率拒答 → 带出处作答。
衡量四件事，它们缺一不可：

（1）**答得对不对**：答案里该出现的关键事实（公差值、审批人、年限）在取回的片子里有没有；
（2）**出处对不对**：指到的条文号是不是标准答案那几条——答对了但指错页，车间照样不敢用；
（3）**该拒的拒不拒**：手册里没有规定的问题，要说"没有规定"，不能编；
（4）**旧版条文的陷阱**：附录里留着已废止的条文，字面上与新版矛盾。把它们一起索引，会答出早已作废的审批人与公差；
    把"版本"当作过滤条件（只索引现行版）就能挡住——这是数据治理问题，不是模型问题。

最后把这几项按代价合成一个账：答错一次的代价远高于拒答一次（与 11.8、12.7 节同一套做法）。
"""
import numpy as np

from _ch13 import chunks, expand, idf_coverage, manual, questions, retrieve
from bookout import out

v = {}
MAN = manual()
QS = questions()
ANS = [q for q in QS if q["answerable"]]
NOANS = [q for q in QS if not q["answerable"]]
K, HOW = 5, "hybrid+syn+part"
v["k"], v["how"] = K, HOW
v["n_clause"], v["n_page"] = len(MAN), MAN[-1]["page"]
v["n_ans"], v["n_noans"] = len(ANS), len(NOANS)


def run(skip_obsolete: bool, field: str = "q2", t_cover: float = 0.10, raw_cover: bool = False) -> dict:
    """跑一遍整条线，返回各项指标。skip_obsolete=True 表示只索引现行版条文；
    可答性用逆文档频率加权的手册覆盖率（13.6 节比较过三种信号，这个最好）。
    raw_cover=True 时覆盖率按问题的原话算（不先过同义词表），用来说明“阈值必须在真实问法上定”。"""
    ch = chunks(MAN, 300, 60, skip_obsolete=skip_obsolete)
    fact_ok = cite_ok = answered = 0
    rej_right = rej_wrong = 0
    stale = 0
    tok = 0
    for q in ANS:
        idx = retrieve(q[field], ch, K, HOW)
        cq = q[field] if raw_cover else expand(q[field])
        cov = idf_coverage(cq, ch)
        text = "".join(ch[i]["text"] for i in idx)
        tok += sum(len(ch[i]["text"]) for i in idx) / 1.5
        if cov < t_cover:                                   # 覆盖率不够：拒答
            rej_wrong += 1
            continue
        answered += 1
        fact_ok += all(f in text for f in q["facts"])       # 关键事实都在取回的片子里
        cite = {c.split("(")[0] for i in idx for c in ch[i]["srcs"]}
        cite_ok += any(g in cite for g in q["gold"])
        stale += any(ch[i]["obsolete"] for i in idx)        # 取回的片子里有没有已废止的条文
    for q in NOANS:
        idx = retrieve(q[field], ch, K, HOW)
        cq = q[field] if raw_cover else expand(q[field])
        cov = idf_coverage(cq, ch)
        tok += sum(len(ch[i]["text"]) for i in idx) / 1.5
        if cov < t_cover:
            rej_right += 1
    n_ans, n_no = len(ANS), len(NOANS)
    return {"chunks": len(ch), "answered": answered, "fact_pct": 100 * fact_ok / max(answered, 1),
            "cite_pct": 100 * cite_ok / max(answered, 1), "rej_right": rej_right,
            "rej_wrong": rej_wrong, "rej_right_pct": 100 * rej_right / n_no,
            "stale": stale, "stale_pct": 100 * stale / max(answered, 1),
            "tok_per_q": tok / (n_ans + n_no),
            "wrong": answered - fact_ok + (n_no - rej_right)}


with_old = run(skip_obsolete=False)
only_new = run(skip_obsolete=True)
for key, r in (("old", with_old), ("new", only_new)):
    for k2, x in r.items():
        v[f"{key}_{k2}"] = x
v["stale_blocked"] = with_old["stale"] - only_new["stale"]
v["cite_gain"] = only_new["cite_pct"] - with_old["cite_pct"]
v["fact_gain"] = only_new["fact_pct"] - with_old["fact_pct"]
assert with_old["stale"] >= only_new["stale"], "把旧版条文索引进去，取回旧版的次数不该更少"

# ---------- 阈值定在书面问法上、却用在口语问法上会怎样（原话不过同义词表）
raw = run(skip_obsolete=True, raw_cover=True)
for k2, x in raw.items():
    v[f"raw_{k2}"] = x
v["raw_over_reject"] = raw["rej_wrong"] - only_new["rej_wrong"]

# ---------- 书面问法与口语问法的差别（同一条线）
book = run(skip_obsolete=True, field="q")
for k2, x in book.items():
    v[f"book_{k2}"] = x
v["shop_fact_drop"] = book["fact_pct"] - only_new["fact_pct"]
v["shop_cite_drop"] = book["cite_pct"] - only_new["cite_pct"]

# ---------- 阈值按代价定
C_WRONG, C_REJECT = 50.0, 1.0                              # 答错一次 50、拒答一次 1（让人自己去翻手册）
v["c_wrong"], v["c_reject"] = C_WRONG, C_REJECT
best = None
for t in np.arange(0.0, 0.30, 0.02):
    r = run(skip_obsolete=True, t_cover=float(t))
    wrong = (r["answered"] - round(r["fact_pct"] / 100 * r["answered"])) + (len(NOANS) - r["rej_right"])
    rej = r["rej_wrong"] + r["rej_right"]
    cost = wrong * C_WRONG + rej * C_REJECT
    if best is None or cost < best[1]:
        best = (float(t), cost, wrong, rej)
    if abs(t - 0.0) < 1e-9:
        v["t0_cost"], v["t0_wrong"], v["t0_rej"] = cost, wrong, rej
v["t_best"], v["cost_best"], v["wrong_best"], v["rej_best"] = best
v["cost_saved"] = v["t0_cost"] - v["cost_best"]

# ---------- 代价与延迟
PRICE_IN, PRICE_OUT, ANSWER_TOK = 2.0, 8.0, 120            # 美元/百万词元（教材假设）；答案约 120 词元
v["price_in"], v["price_out"], v["answer_tok"] = PRICE_IN, PRICE_OUT, ANSWER_TOK
v["tok_in"] = only_new["tok_per_q"] + 200                  # 片子 + 提示
v["cost_per_1k_usd"] = (v["tok_in"] * PRICE_IN + ANSWER_TOK * PRICE_OUT) * 1000 / 1e6
v["cost_per_q_cent"] = v["cost_per_1k_usd"] / 1000 * 100
# 不检索、把整本手册塞进上下文
v["all_tok"] = sum(len(c["text"]) for c in MAN) / 1.5
v["all_cost_per_1k_usd"] = (v["all_tok"] * PRICE_IN + ANSWER_TOK * PRICE_OUT) * 1000 / 1e6
v["all_vs_rag"] = v["all_cost_per_1k_usd"] / v["cost_per_1k_usd"]
# 一年的账：车间 200 人，每人每天问 3 次
v["users"], v["per_day"] = 200, 3
v["q_per_year"] = v["users"] * v["per_day"] * 250
v["year_usd"] = v["q_per_year"] / 1000 * v["cost_per_1k_usd"]
v["year_all_usd"] = v["q_per_year"] / 1000 * v["all_cost_per_1k_usd"]
out(**v)
