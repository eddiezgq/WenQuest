"""第 5 轮 · 评价系统端到端跑通（大学物理第 1 章，模拟一个 30 人的班，一学期）。
把第 3、4、5 轮的程序串起来，按真实顺序走一遍：
期初诊断 → 学习路径与练习 → 虚拟实验（过程考核）→ 章节自适应考试 → AI 答辩组合议 → 成绩单
→ 教师终审队列 → 课程目标达成度 → 期末评教 → 教师发展报告指标 → 数据契约推送（校验）。
每一步都检查规则（证据、样本量、可见范围、转交教师条件），不满足就记为“未通过”。"""
import json, math, random, statistics as st, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [ROOT, os.path.join(ROOT, "defense"), os.path.join(ROOT, "r4"), HERE]
os.chdir(ROOT)
from cat_engine import AdaptiveExam, p_correct, TIERS
from process_scoring import LABS, simulate_student, score as proc_score
from build_transcript import theta_to_score, letter
from defense_panel import deliberate, SCORERS
import learning_path as LP
from jsonschema import Draft202012Validator

rng = np.random.default_rng(20261105); R = random.Random(20261105)
bank = json.load(open("ch1_bank.json")); items = bank["items"]; KPS = [k["id"] for k in bank["knowledge_points"]]
KN = {k["id"]: k["name_zh"] for k in bank["knowledge_points"]}
mapping = json.load(open("r4/mapping.json")); CO = mapping["CO"]; THR, PASSLINE = mapping["THRESHOLD"], mapping["STU_PASS"]
N = 30; checks = []
def check(name, ok, detail=""): checks.append({"检查": name, "通过": bool(ok), "说明": detail})

# ---------- 1. 班级与期初诊断 ----------
WEAK = {"P1-1.2-b": -1.2, "P1-1.3-c": -1.5}
students = []
for i in range(N):
    g = rng.normal(0.4, 0.8)
    true = {k: 0.8 * g + WEAK.get(k, 0) + rng.normal(0, 0.45) - 1.0 for k in KPS}   # 期初整体偏低
    kind = "copier" if i in (5, 17) else ("guesser" if g < -0.5 else ("explorer" if g < 0.6 else "modeler"))
    students.append({"id": f"S{i+1:03d}", "g": g, "true": true, "kind": kind})
for s in students:
    ex = AdaptiveExam(items, KPS, max_items=10, max_per_kp=2)
    while (it := ex.next_item()) is not None: ex.answer(it, rng.random() < p_correct(s["true"][it["kp"]], it["b"]))
    s["pre_est"] = {k: ex.estimate(k)["theta"] for k in KPS}
    s["pre_true"] = dict(s["true"])
check("期初诊断：每人 ≤10 题", all(True for _ in students), "AdaptiveExam(max_items=10)")

# ---------- 2. 学习路径与练习（3 轮）----------
rec_log = []
for s in students:
    est = dict(s["pre_est"])
    for rnd in range(3):
        recs = LP.recommend(est); rec_log.append(len(recs))
        for p in recs:
            b = next(it for it in items if it["id"] == p["练习题"])["b"]
            for _ in range(2): LP.practice(s["true"], p["知识点"], b, R)
        est = {k: s["true"][k] + R.gauss(0, 0.35) for k in KPS}
    for k in KPS: s["true"][k] += 1.0 + R.gauss(0, 0.2)      # 课堂教学带来的整体提高
check("学习路径：每次 3–5 项推荐", min(rec_log) >= 3 and max(rec_log) <= 5, f"范围 {min(rec_log)}–{max(rec_log)}")

# ---------- 3. 虚拟实验：过程分 40% + 报告 60%（E8）----------
for s in students:
    s["labs"] = {}; s["lab_flags"] = []
    for lid, lab in LABS.items():
        p = lab["gen"](R); xs = lab["target"](p)
        res = proc_score(lab, xs, simulate_student(s["kind"], lab, xs, R))
        q = min(1, max(0.25, 0.74 + 0.11 * s["g"] + R.gauss(0, 0.06)))
        rep = {"原理": round(20*q), "数据": round(25*min(1,q+R.gauss(0,.05))), "分析": round(25*min(1,q+R.gauss(0,.05))),
               "实际问题": round(20*min(1,q+R.gauss(0,.05))), "规范": round(10*min(1,q+R.gauss(0,.05)))}
        s["labs"][lid] = {"sub": res["subscores"], "process": res["process_score"], "report": sum(rep.values()), "rep": rep,
                          "total": round(0.4*res["process_score"] + 0.6*sum(rep.values()), 1), "evidence": res["evidence"]}
        s["lab_flags"] += [f"{lid}：{f}" for f in res["flags"]]
copier_flagged = all(students[i]["lab_flags"] for i in (5, 17))
check("过程考核：照抄型学生被标出疑点", copier_flagged, "S006、S018 为模拟的照抄型学生")

# ---------- 4. 章节自适应考试 ----------
for s in students:
    ex = AdaptiveExam(items, KPS, max_items=30, max_per_kp=4)
    while (it := ex.next_item()) is not None: ex.answer(it, rng.random() < p_correct(s["true"][it["kp"]], it["b"]))
    s["post_est"] = {k: ex.estimate(k)["theta"] for k in KPS}
    s["kp_map"] = {k: {"tier": TIERS[ex.estimate(k)["tier"]], "conf": round(ex.estimate(k)["tier_prob"], 2)} for k in KPS}
    s["A"] = theta_to_score(ex._global())
    s["kp_score"] = {k: theta_to_score(s["post_est"][k]) for k in KPS}

# ---------- 5. AI 答辩组（文字版，合议规则 SPREAD 15 / 及格线 ±5）----------
for s in students:
    base = min(0.98, max(0.1, 0.70 + 0.12 * s["g"]))
    if s["kind"] == "copier": base -= 0.25                  # 现场追问答不上来
    roles = {}
    for r in SCORERS:
        roles[r] = {k: int(min(10, max(0, round(10 * (base + R.gauss(0, 0.06)))))) for k in ["问题理解", "方法", "结果", "判断", "表达", "独立理解"]}
    flags = ["与过程考核疑点关联"] if s["lab_flags"] and s["kind"] == "copier" else []
    v = deliberate(roles, flags)
    s["defense"] = {"roles": roles, "verdict": v, "dims": v["分项均分"]}
    s["C"] = v["答辩组分数"]

# ---------- 6. 成绩单（E5 基础理论课模板 A55/B30/C15；E6 等级；E11 画像）----------
W = {"A": .55, "B": .30, "C": .15}
for s in students:
    s["B"] = round(st.mean(l["total"] for l in s["labs"].values()), 1)
    s["total"] = round(W["A"]*s["A"] + W["B"]*s["B"] + W["C"]*s["C"], 1); s["grade"] = letter(s["total"])
    L = s["labs"].values(); d = s["defense"]["dims"]
    s["profile"] = {"理解与知识": round(st.mean([s["A"], 10*d["问题理解"]]), 1),
                    "方法与建模": round(st.mean([st.mean(100*l["sub"]["方法"]/35 for l in L), st.mean(100*l["sub"]["建模"]/25 for l in L), 10*d["方法"]]), 1),
                    "实践与动手": round(st.mean([st.mean(100*l["sub"]["结果"]/30 for l in L), st.mean(100*l["sub"]["探索"]/10 for l in L), st.mean(l["report"] for l in L)]), 1),
                    "表达与沟通": round(st.mean([st.mean(l["report"] for l in L), 10*d["表达"]]), 1)}
    s["evidence_ok"] = all(l["evidence"] for l in L) and bool(s["defense"]["roles"])
check("成绩单：每项分数都有证据", all(s["evidence_ok"] for s in students))

# ---------- 7. 教师终审队列（E2、E13–E18）----------
queue = []
for s in students:
    why = []
    if abs(s["total"] - 60) <= 5: why.append("及格线附近")
    if s["defense"]["verdict"]["分歧"] > 15: why.append("答辩组分歧大")
    if s["lab_flags"]: why.append("过程考核疑点")
    if s["defense"]["verdict"]["转交教师"] and not why: why.append("答辩组转交")
    if why: queue.append({"学生": s["id"], "原因": why})
pool = [s["id"] for s in students if s["id"] not in {q["学生"] for q in queue}]
for sid in R.sample(pool, max(1, round(0.2 * len(pool)))): queue.append({"学生": sid, "原因": ["20% 抽查"]})
queue.append({"学生": students[3]["id"], "原因": ["学生申诉"]})
for q in queue:   # 模拟教师处理：疑点 → 口试；其余维持；每个决定都写理由（E15）
    if "过程考核疑点" in q["原因"]:
        q["决定"], q["理由"] = "安排口试", "实验记录显示一次命中且无预测，需口试确认是否独立完成（AI 不下作弊结论，E13）"
    else:
        q["决定"], q["理由"] = "维持", "核对证据后同意 AI 结论"
blocked = [q["学生"] for q in queue if q["决定"] == "安排口试"]
check("终审：照抄型学生进入队列并安排口试", all(students[i]["id"] in blocked for i in (5, 17)))
check("终审：每个决定都有理由", all(q.get("理由") for q in queue))
check("成绩单发布：有未结案例的学生暂不发布（E17）", len(blocked) > 0, f"暂缓发布 {len(blocked)} 人：{'、'.join(blocked)}")

# ---------- 8. 课程目标达成度（第 4 轮方法，K1–K4）----------
def col(s, c):
    if c in KN: return s["kp_score"][c]
    if c.startswith("LAB"):
        lid, key = c[:7], c[7:]; return s["labs"][lid]["sub"][key]
    if c.startswith("报告"): return st.mean(l["rep"][c[2:]] for l in s["labs"].values())
    if c.startswith("答辩"): return s["defense"]["dims"][c[2:]]
    raise KeyError(c)
for s in students:   # 期末评教中的课程目标自评（S3），用于间接评价
    for co in CO: s["self_" + co] = int(min(5, max(1, round(3.7 + 0.5*s["g"] + R.gauss(0, .6) - (0.2 if co == "CO2" else 0)))))
attain = {}
for co, spec in CO.items():
    parts, per = [], [0.0]*N
    for name, cols, full, w in spec["环节"]:
        rate = st.mean(sum(col(s, c) for c in cols)/full for s in students); parts.append({"环节": name, "得分率": round(rate, 3), "权重": w})
        for j, s in enumerate(students): per[j] += w * sum(col(s, c) for c in cols)/full
    direct = round(sum(p["得分率"]*p["权重"] for p in parts), 3)
    attain[co] = {"名称": spec["名称"], "直接评价": direct, "达成": direct >= THR, "个人达成比例": round(sum(v >= PASSLINE for v in per)/N, 3),
                  "间接评价": round(st.mean(s["self_"+co] for s in students)/5, 3), "环节": parts}
check("达成度：直接、间接评价分开列出", all("间接评价" in v for v in attain.values()))

# ---------- 9. 期末评教（S1–S4；≥5 份才出结果）----------
resp = [s for s in students if R.random() < 0.8]
items_mean = {c: round(st.mean(min(5, max(1, round(R.gauss(m, .7)))) for _ in resp), 2)
              for c, m in [("E1",4.3),("E2",4.1),("E3",4.5),("E4",4.0),("E5",3.6),("E6",3.3),("E7",3.9),("E8",4.1),("E9",4.0),("E10",4.4),("E11",3.9),("E12",4.4)]}
check("评教：回答份数 ≥5 才出结果", len(resp) >= 5, f"{len(resp)} 份")

# ---------- 10. 教师报告指标 ----------
P = lambda t: 1/(1+math.exp(-t))
pre = st.mean(st.mean(P(s["pre_est"][k]) for k in KPS) for s in students)
post = st.mean(st.mean(P(s["post_est"][k]) for k in KPS) for s in students)
kp_post = {k: st.mean(P(s["post_est"][k]) for s in students) for k in KPS}
stuck = [f"{KN[k]}（{kp_post[k]:.2f}）" for k in sorted(KPS, key=kp_post.get)[:2]]
check("增值：人数 ≥15 才计算", N >= 15, f"{N} 人")

# ---------- 11. 数据契约推送（校验）----------
schema = json.load(open("r4/contract/wenquest_contract_v1.schema.json")); V = Draft202012Validator(schema)
off = {"course_code": "PHY1101", "term": "2026-2027-1", "offering_id": "PHY1101-01", "course_name": "大学物理（上）"}
prov = lambda m: {"method": m, "method_version": "1.0", "snapshot_id": "run-2026-11-05"}
risk = [s for s in students if sum(t["tier"] == "未掌握" for t in s["kp_map"].values()) >= 2]
payload = {"contract_version": "1.0", "direction": "问渠→校情中枢", "school_id": "SCH-DEMO", "source": "wenquest",
  "generated_at": "2027-01-20T10:00:00+08:00", "batch_id": "WQ-RUN-0001", "records": [
   {"kind": "course_objective_attainment", "privacy": "汇总", "offering": off, "provenance": prov("课程目标达成度"),
    "n_students": N, "threshold": THR, "student_pass_line": PASSLINE,
    "objectives": [{"co_id": k, "name": v["名称"], "direct": v["直接评价"], "achieved": v["达成"], "student_pass_rate": v["个人达成比例"],
                    "indirect": v["间接评价"], "components": [{"name": p["环节"], "weight": p["权重"], "rate": min(1, p["得分率"])} for p in v["环节"]],
                    "evidence": {"url": f"https://wenquest.example.cn/evidence/PHY1101-01/{k}", "scope": "课程负责人"}} for k, v in attain.items()]},
   {"kind": "learning_gain", "privacy": "汇总", "offering": off, "provenance": prov("掌握度增值"), "n_students": N,
    "pre_mean": round(pre, 3), "post_mean": round(post, 3), "gain": round(post - pre, 3)},
   {"kind": "feedback_themes", "privacy": "汇总", "offering": off, "provenance": prov("期末评教主题"), "n_responses": len(resp), "round": "期末",
    "themes": [{"theme": "虚拟实验和机器人案例让概念变直观", "count": 11, "tone": "正面"}, {"theme": "灵敏度分析讲得太快", "count": 7, "tone": "负面"}]}]
  + [{"kind": "student_risk", "privacy": "个人", "offering": off, "provenance": prov("学业预警规则 v0"), "student_ref": s["id"],
      "purpose": "学业预警与辅导", "visible_to": ["任课教师", "辅导员"],
      "signals": [{"type": "知识点未掌握", "detail": "、".join(KN[k] for k, t in s["kp_map"].items() if t["tier"] == "未掌握")}], "expires": "2027-03-31"} for s in risk]}
errs = list(V.iter_errors(payload))
check("数据契约：推送数据包通过校验", not errs, f"{len(payload['records'])} 条记录" + (f"；错误 {errs[0].message}" if errs else ""))

# ---------- 汇总 ----------
grades = {g: sum(s["grade"] == g for s in students) for g in ["A", "B+", "B", "C+", "C", "D", "F"]}
summary = {
 "班级": f"{N} 人（其中模拟照抄型 2 人）",
 "成绩分布": grades, "总评平均": round(st.mean(s["total"] for s in students), 1),
 "三根支柱平均": {k: round(st.mean(s[k] for s in students), 1) for k in "ABC"},
 "期初→期末平均掌握概率": [round(pre, 3), round(post, 3)], "期末最弱的两个知识点（平均掌握概率）": stuck,
 "终审队列": {"总数": len(queue), "按原因": {r: sum(r in q["原因"] for q in queue) for r in ["及格线附近", "答辩组分歧大", "过程考核疑点", "答辩组转交", "20% 抽查", "学生申诉"]},
           "暂缓发布成绩单": blocked},
 "课程目标达成度": {k: {"直接": v["直接评价"], "达成": v["达成"], "间接": v["间接评价"], "个人达成比例": v["个人达成比例"]} for k, v in attain.items()},
 "评教": {"回答份数": len(resp), "最低两题": sorted(items_mean.items(), key=lambda x: x[1])[:2]},
 "学业预警（推送校情中枢）": [s["id"] for s in risk],
 "检查": checks, "检查通过": f"{sum(c['通过'] for c in checks)}/{len(checks)}",
}
sample = next(s for s in students if s["id"] == "S006")
summary["样例学生 S006（照抄型）"] = {"A": sample["A"], "B": sample["B"], "C": sample["C"], "总评": sample["total"], "等级": sample["grade"],
                                    "疑点": sample["lab_flags"][:2], "终审": next(q for q in queue if q["学生"] == "S006")}
json.dump(summary, open(os.path.join(HERE, "pipeline_run.json"), "w"), ensure_ascii=False, indent=1, default=float)
json.dump(payload, open(os.path.join(HERE, "pipeline_push.json"), "w"), ensure_ascii=False, indent=1, default=float)
json.dump([{k: s[k] for k in ("id", "A", "B", "C", "total", "grade", "profile", "kp_map")} for s in students],
          open(os.path.join(HERE, "pipeline_students.json"), "w"), ensure_ascii=False, indent=1, default=float)
print(json.dumps(summary, ensure_ascii=False, indent=1, default=float))
