"""第 4 轮 · 第 6 步：教师发展报告的数据（大学物理第 1 章，模拟学期）。
达成度、审核结果取自第 1、4 步；评教、答疑、批改等为模拟数据。"""
import json, random, statistics as st, math
import attainment as A
random.seed(6)
S = A.students; N = len(S)
att = json.load(open("attainment_ch1.json")); audit = json.load(open("audit_ch1.json"))
inv = lambda sc: max(0.02, min(0.98, sc / 100))            # 期末分数近似为掌握概率
kp_gain = []
for k, name in A.KPS.items():
    post = st.mean(inv(s[k]) for s in S); pre = st.mean(max(0.02, min(0.6, inv(s[k]) * 0.25 + random.gauss(0.05, 0.03))) for s in S)
    kp_gain.append({"kp": k, "name": name, "pre": round(pre, 2), "post": round(post, 2), "gain": round(post - pre, 2)})
pre_all = round(st.mean(x["pre"] for x in kp_gain), 2); post_all = round(st.mean(x["post"] for x in kp_gain), 2)
stuck = [x for x in kp_gain if x["post"] < 0.5]
indep = round(st.mean(s["答辩独立理解"] for s in S), 1)

ITEMS = [("E1","每节课我都清楚要学什么、为什么学",4.3),("E2","考试、实验和答辩考的正是课程要求掌握的内容",4.2),
 ("E3","老师用实际问题引出概念",4.6),("E4","有机会提问或讨论，问题得到认真回应",4.1),("E5","反馈指出了我的具体错误",3.6),
 ("E6","反馈告诉我怎样改进",3.3),("E7","在合理的时间内收到反馈",3.9),("E8","课后提问能得到及时、有用的回答",4.2),
 ("E9","AI 助教的回答准确、有帮助",4.0),("E10","虚拟实验帮我理解模型和真实问题的联系",4.5),("E11","“运行前先预测”让我先思考再动手",3.8),("E12","评分标准事先公布，评分公正",4.4)]
R = 33
survey = []
for code, text, mu in ITEMS:
    ans = [max(1, min(5, round(random.gauss(mu, 0.75)))) for _ in range(R)]
    survey.append({"code": code, "text": text, "mean": round(st.mean(ans), 2), "n": R, "dist": [ans.count(v) for v in range(1, 6)]})
themes = [{"theme": "虚拟实验和机器人案例让概念变直观", "count": 14, "tone": "正面", "quote": "投篮机器人那个实验，调一次就懂了为什么要算出手速度。"},
          {"theme": "灵敏度分析（1.3 节偏差）讲得太快", "count": 9, "tone": "负面", "quote": "偏差那部分没跟上，不知道该代哪个速度。"},
          {"theme": "反馈指出了错，但没说怎么改", "count": 7, "tone": "建议", "quote": "报告批注写了“分析不足”，希望能说具体哪里不足。"},
          {"theme": "希望多给建模练习", "count": 6, "tone": "建议", "quote": "公式会套，但遇到新情境不知道怎么建模型。"}]
filtered = 1

data = {
 "meta": {"course": "大学物理（上）· 第 1 章 质点运动学", "course_code": "PHY1101-01", "term": "2026–2027 学年第一学期（模拟）",
          "teacher": "示例教师", "students": N, "snapshot": "snap-2026-2027-1-final", "generated": "2027-01-20",
          "note": "数据为模拟：达成度和审核结果来自第 4 轮第 1、4 步，其余为示例"},
 "Q": {"Q1": 1.0, "Q2": 1.0, "audit_high": audit["AI 表述审核"]["高"], "audit_true": audit["AI 表述审核"]["高-属实"],
       "audit_false": audit["AI 表述审核"]["误报"], "fixed_templates": 10, "q3_left": "1.4 侧翻速度 2.47（保守取值，已注明）",
       "q5": audit["Q5 题目质量（模拟作答）"]["检出"]},
 "P": {"P1": {"median_h": 6.5, "n": 48}, "P2": {"median_d": 4, "n": 6}, "P3": {"rate": 0.58, "n": 24},
       "P4": {"median_d": 1.5, "reason_ok": 1.0, "n": 7}, "P5": None},
 "O": {"gain": {"pre": pre_all, "post": post_all, "gain": round(post_all - pre_all, 2), "by_kp": kp_gain},
       "stuck": [{"kp": x["kp"], "name": x["name"], "post": x["post"]} for x in stuck],
       "attain": {k: {"name": v["名称"], "direct": v["直接评价达成度"], "achieved": v["是否达成"], "pass": v["学生个人达成比例"],
                      "indirect": v["间接评价（学生自评）"], "weak": v.get("追溯：得分率最低的考核项", [])} for k, v in att["课程目标"].items()},
       "indep": indep, "warn": {"n": 6, "resolved": 4}},
 "F": {"items": survey, "themes": themes, "filtered": filtered, "responses": R},
 "AI": {"A1": {"rate": 0.92, "n": 40}, "A2": {"rate": 0.07, "n": 612}, "A3": {"rate": 0.84, "n": 160}, "A4": {"appeal_changed": 1, "common_error": 1, "n": 12}},
}
json.dump(data, open("report_data.json", "w"), ensure_ascii=False, indent=1)
print("gain", pre_all, post_all, "stuck", [x["kp"] for x in stuck], "indep", indep)
for x in survey: print(x["code"], x["mean"])
