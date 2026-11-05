"""施工第6步：成绩单数据生成（样例学生 S-0001，大学物理（上）第 1 章，基础理论课模板）。
A：自适应期末 + 3 次平时小测，按全章总体能力折算（E7）；B：5 个实验，过程 40% + 报告 60%（E8）；
C：答辩组分数；等级按 E6 七档；能力画像四维由各项分数按映射表合成。报告分为样例值（真实使用时来自 R8 量规评分）。"""
import json, random, numpy as np
from cat_engine import AdaptiveExam, p_correct, TIERS
from process_scoring import LABS, simulate_student, score

rng = np.random.default_rng(2026); random.seed(2026)
bank = json.load(open("ch1_bank.json")); items = bank["items"]; kps = [k["id"] for k in bank["knowledge_points"]]
kpname = {k["id"]: (k["name_zh"], k["name_en"]) for k in bank["knowledge_points"]}

# ---- 学生真实能力（模拟）----
g = 0.7; true = {k: g + rng.normal(0, 0.6) for k in kps}
ex = AdaptiveExam(items, kps, max_items=60, max_per_kp=7)
for k in kps:                                    # 3 次平时小测，每次每个知识点 1 题
    for it in random.sample([i for i in items if i["kp"] == k], 3): ex.answer(it, rng.random() < p_correct(true[k], it["b"]))
n_quiz = len(ex.resp)
while (it := ex.next_item()) is not None: ex.answer(it, rng.random() < p_correct(true[it["kp"]], it["b"]))
theta = ex._global()
def theta_to_score(t):
    """总体能力 → 百分制：与掌握档位对齐。θ=−0.5（基本掌握下限）→60，θ=0.5（熟练下限）→80，θ=1.5（精通下限）→90；
    两端按同样斜率外推，限定在 0–100。"""
    pts = [(-3.5, 0), (-0.5, 60), (0.5, 80), (1.5, 90), (2.5, 100)]
    if t <= pts[0][0]: return 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if t <= x1: return round(y0 + (y1 - y0) * (t - x0) / (x1 - x0), 1)
    return 100.0
A_score = theta_to_score(theta)
kp_map = []
for k in kps:
    e = ex.estimate(k)
    kp_map.append({"id": k, "name_zh": kpname[k][0], "name_en": kpname[k][1], "tier": TIERS[e["tier"]], "tier_idx": e["tier"],
                   "confidence": round(e["tier_prob"], 2), "pending": e["tier_prob"] < 0.5, "n_items": e["n"],
                   "theta": round(e["theta"], 2), "sd": round(e["sd"], 2)})

# ---- B：5 个实验 ----
report_scores = {"LAB-1.1": 86, "LAB-1.2": 78, "LAB-1.3": 90, "LAB-1.4": 88, "LAB-1.5": 82}   # 样例值（R8 量规）
kinds = {"LAB-1.1": "modeler", "LAB-1.2": "explorer", "LAB-1.3": "modeler", "LAB-1.4": "modeler", "LAB-1.5": "explorer"}
labs = []; r2 = random.Random(7)
for lid, lab in LABS.items():
    p = lab["gen"](r2); xs = lab["target"](p); res = score(lab, xs, simulate_student(kinds[lid], lab, xs, r2))
    total = round(0.4 * res["process_score"] + 0.6 * report_scores[lid], 1)
    labs.append({"id": lid, "name": lab["name"], "process": res["process_score"], "sub": res["subscores"],
                 "report": report_scores[lid], "total": total, "evidence": res["evidence"], "flags": res["flags"]})
B_score = round(float(np.mean([l["total"] for l in labs])), 1)

# ---- C：答辩（样例）----
defense = {"panel": {"领域专家甲": 84, "领域专家乙": 80, "质疑者": 78, "应用评委": 82, "表达与规范评委": 86},
           "dims": {"问题理解": 8.4, "方法": 8.2, "结果": 8.6, "判断": 7.6, "表达": 8.4, "独立理解": 8.0}}
C_score = round(float(np.mean(list(defense["panel"].values()))), 1)

W = {"A": 0.55, "B": 0.30, "C": 0.15}
total = round(W["A"] * A_score + W["B"] * B_score + W["C"] * C_score, 1)
def letter(x): return "A" if x >= 90 else "B+" if x >= 85 else "B" if x >= 80 else "C+" if x >= 75 else "C" if x >= 70 else "D" if x >= 60 else "F"

# ---- 能力画像四维（映射表）----
avg = lambda xs: round(float(np.mean(xs)), 1)
proc = lambda key, mx: avg([100 * l["sub"][key] / mx for l in labs])
profile = {
 "理解与知识 Understanding": avg([A_score, 10 * defense["dims"]["问题理解"]]),
 "方法与建模 Methods & modeling": avg([proc("方法", 35), proc("建模", 25), 10 * defense["dims"]["方法"]]),
 "实践与动手 Hands-on practice": avg([proc("结果", 30), proc("探索", 10), avg([l["report"] for l in labs])]),
 "表达与沟通 Communication": avg([avg([l["report"] for l in labs]), 10 * defense["dims"]["表达"]]),
}
evidence = [
 {"id": "EV-A1", "pillar": "A", "title": "期末自适应考试", "detail": f"平时小测 {n_quiz} 题 + 期末 {len(ex.resp)-n_quiz} 题；全章总体能力估计 θ = {theta:.2f}，按档位对齐的折算表得 {A_score} 分"},
] + [{"id": f"EV-{l['id']}", "pillar": "B", "title": l["name"], "detail": "；".join(l["evidence"]) + f"；实验报告 {l['report']} 分（样例值）"} for l in labs] + [
 {"id": "EV-C1", "pillar": "C", "title": "综合项目答辩（文字版）", "detail": "五位评委独立评分 78–86，分歧 8 分，未超过 15 分；第 7–9 问：质疑者把转弯半径减半，学生当场重算并解释"},
]
out = {"student": {"id": "S-0001", "name": "样例学生 Sample Student"}, "course": {"zh": "大学物理（上）· 第 1 章 质点运动学", "en": "University Physics I · Ch. 1 Kinematics"},
       "template": "基础理论课 Foundational theory", "weights": W, "scores": {"A": A_score, "B": B_score, "C": C_score}, "total": total, "letter": letter(total),
       "kp_map": kp_map, "profile": profile, "labs": labs, "defense": defense, "evidence": evidence, "issued": "2026-10-30",
       "note": "本成绩单为样例：考生、作答和实验报告分为模拟数据。"}
json.dump(out, open("transcript_S0001.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ("scores", "total", "letter", "profile")}, ensure_ascii=False, indent=1))
print([(k["name_zh"], k["tier"], k["confidence"], "待确认" if k["pending"] else "") for k in kp_map])
