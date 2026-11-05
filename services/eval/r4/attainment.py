"""第 4 轮 · 第 1 步：课程目标达成度计算样例（大学物理第 1 章，模拟班级 40 人）。
数据为模拟数据，结构与第 3 轮数据模型一致；正式运行时从问渠的作答、过程、报告、答辩记录取数。"""
import json, random, statistics as st
random.seed(20261101)
N = 40
THRESHOLD = 0.70          # 课程目标达成阈值（学校可配置）
STU_PASS = 0.60           # 学生个人达成线（学校可配置）

KPS = {"P1-1.1-a": "参考系与坐标系", "P1-1.1-b": "伽利略速度合成", "P1-1.2-a": "位矢、位移与速度",
       "P1-1.2-b": "数值微分与采样误差", "P1-1.3-a": "抛体运动方程", "P1-1.3-b": "按目标求初速度",
       "P1-1.3-c": "出手误差的灵敏度", "P1-1.4-a": "向心加速度", "P1-1.4-b": "侧翻与侧滑条件",
       "P1-1.5-a": "相对运动与航向修正"}
KP_OFFSET = {"P1-1.2-b": -1.4, "P1-1.3-c": -1.8}   # 模拟：这两个知识点全班偏弱
LABS = ["LAB-1.1", "LAB-1.2", "LAB-1.3", "LAB-1.4", "LAB-1.5"]

def theta_to_score(t):     # 第 3 轮 E10 折算
    pts = [(-3.5, 0), (-0.5, 60), (0.5, 80), (1.5, 90), (2.5, 100)]
    if t <= pts[0][0]: return 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if t <= x1: return y0 + (y1 - y0) * (t - x0) / (x1 - x0)
    return 100.0
clip = lambda v, lo, hi: max(lo, min(hi, v))

students = []
for i in range(N):
    g = random.gauss(0.6, 0.8)
    s = {"学号": f"S{i+1:03d}"}
    for k in KPS:   # 闭卷：各知识点掌握度折算的百分制分数
        s[k] = round(theta_to_score(0.8 * g + KP_OFFSET.get(k, 0) + random.gauss(0, 0.5)), 1)
    for L in LABS:  # 过程分项：结果 30、方法 35、建模 25、探索 10
        q = clip(0.72 + 0.12 * g + random.gauss(0, 0.08), 0.2, 1)
        model_q = clip(q - (0.30 if L == "LAB-1.2" else 0) + random.gauss(0, 0.06), 0, 1)
        s[f"{L}结果"] = round(30 * clip(q + 0.05, 0, 1)); s[f"{L}方法"] = round(35 * q)
        s[f"{L}建模"] = round(25 * model_q); s[f"{L}探索"] = round(10 * clip(q + random.gauss(0, .1), 0, 1))
    r = clip(0.74 + 0.11 * g + random.gauss(0, 0.07), 0.2, 1)   # 实验报告 R8 量规
    for item, full in (("原理", 20), ("数据", 25), ("分析", 25), ("实际问题", 20), ("规范", 10)):
        s[f"报告{item}"] = round(full * clip(r + random.gauss(0, .05), 0, 1))
    d = clip(0.70 + 0.13 * g + random.gauss(0, 0.08), 0.1, 1)   # 答辩量规（每项 10 分）
    for item in ("问题理解", "方法", "结果", "判断", "表达", "独立理解"):
        s[f"答辩{item}"] = round(10 * clip(d + random.gauss(0, .07) - (0.08 if item == "判断" else 0), 0, 1))
    for co, bias in (("CO1", 0.3), ("CO2", -0.1), ("CO3", 0.2), ("CO4", 0.0)):  # 学生自评（1–5 分）
        s[f"自评{co}"] = int(clip(round(3.6 + bias + 0.5 * g + random.gauss(0, .6)), 1, 5))
    students.append(s)

# 课程目标 → 考核环节（环节内各列求和后除以满分，得到 0–1 的得分率）
CO = {
 "CO1": {"名称": "理解并运用运动学的基本概念和规律", "环节": [
     ("闭卷：基础知识点", ["P1-1.1-a", "P1-1.1-b", "P1-1.2-a", "P1-1.3-a", "P1-1.4-a"], 500, 1.0)]},
 "CO2": {"名称": "能为机器人等工程问题建立运动学模型并求解", "环节": [
     ("闭卷：建模类知识点", ["P1-1.2-b", "P1-1.3-b", "P1-1.3-c", "P1-1.4-b", "P1-1.5-a"], 500, 0.5),
     ("实验过程：建模", [f"{L}建模" for L in LABS], 125, 0.3),
     ("答辩：方法", ["答辩方法"], 10, 0.2)]},
 "CO3": {"名称": "能用虚拟实验检验模型，处理数据并分析误差", "环节": [
     ("实验过程：结果、方法、探索", [f"{L}{x}" for L in LABS for x in ("结果", "方法", "探索")], 375, 0.5),
     ("实验报告：数据、分析", ["报告数据", "报告分析"], 50, 0.5)]},
 "CO4": {"名称": "能清楚表达工程判断，说明模型的适用范围", "环节": [
     ("实验报告：实际问题、规范", ["报告实际问题", "报告规范"], 30, 0.4),
     ("答辩：判断、表达、独立理解", ["答辩判断", "答辩表达", "答辩独立理解"], 30, 0.6)]},
}

def col_full(c):   # 每个考核项的满分
    if c in KPS: return 100
    for k, f in (("结果", 30), ("方法", 35), ("建模", 25), ("探索", 10)):
        if c.startswith("LAB") and c.endswith(k): return f
    rep = {"报告原理": 20, "报告数据": 25, "报告分析": 25, "报告实际问题": 20, "报告规范": 10}
    if c in rep: return rep[c]
    if c.startswith("答辩"): return 10
    raise KeyError(c)
for _co in CO.values():   # 校验：环节满分 = 各项满分之和
    for _n, _cols, _full, _w in _co["环节"]: assert _full == sum(col_full(c) for c in _cols), _n
    assert abs(sum(x[3] for x in _co["环节"]) - 1) < 1e-9

def rate(s, cols, full): return sum(s[c] for c in cols) / full
result = {"说明": "模拟数据；达成阈值 %.2f，学生个人达成线 %.2f，均可由学校配置" % (THRESHOLD, STU_PASS), "课程目标": {}}
for co, spec in CO.items():
    parts = []
    for name, cols, full, w in spec["环节"]:
        m = st.mean(rate(s, cols, full) for s in students)
        parts.append({"环节": name, "权重": w, "得分率": round(m, 3), "贡献": round(w * m, 3)})
    direct = round(sum(p["贡献"] for p in parts), 3)
    per_stu = [sum(w * rate(s, cols, full) for _, cols, full, w in spec["环节"]) for s in students]
    indirect = round(st.mean(s[f"自评{co}"] for s in students) / 5, 3)
    item = {"名称": spec["名称"], "直接评价达成度": direct, "是否达成": direct >= THRESHOLD,
            "学生个人达成比例": round(sum(v >= STU_PASS for v in per_stu) / N, 3),
            "间接评价（学生自评）": indirect, "环节": parts}
    if True:   # 追溯：环节内逐列看得分率；未达成的目标必列，已达成的目标列出得分率低于 0.6 的项作为预警
        cols_rate = []
        for name, cols, full, w in spec["环节"]:
            for c in cols:
                cols_rate.append((round(st.mean(s[c] for s in students) / col_full(c), 3), name, c, KPS.get(c, c)))
        low = sorted(cols_rate)[:3] if direct < THRESHOLD else [x for x in sorted(cols_rate) if x[0] < 0.6]
        if low: item["追溯：得分率最低的考核项" if direct < THRESHOLD else "预警：得分率低于 0.6 的考核项"] = [{"得分率": r, "环节": n, "考核项": c, "说明": d} for r, n, c, d in low]
    result["课程目标"][co] = item

# 交给校情中枢的数据（按问渠数据契约草案）：毕业要求汇总由校情中枢完成，这里只示范算法
SUPPORT = {"1.2 工程知识（示例指标点）": [("本课程", "CO1", 0.3), ("示例：理论力学", None, 0.4), ("示例：高等数学", None, 0.3)],
           "2.1 问题分析（示例指标点）": [("本课程", "CO2", 0.4), ("示例：机器人学导论", None, 0.6)],
           "4.2 研究（示例指标点）": [("本课程", "CO3", 0.3), ("示例：控制工程实验", None, 0.7)],
           "10.1 沟通（示例指标点）": [("本课程", "CO4", 0.2), ("示例：毕业设计", None, 0.8)]}
OTHER = {"示例：理论力学": 0.76, "示例：高等数学": 0.81, "示例：机器人学导论": 0.72, "示例：控制工程实验": 0.78, "示例：毕业设计": 0.80}
gr = {}
for gp, sup in SUPPORT.items():
    rows = []
    for course, co, w in sup:
        v = result["课程目标"][co]["直接评价达成度"] if co else OTHER[course]
        rows.append({"课程": course, "课程目标": co, "支撑权重": w, "课程目标达成度": v})
    gr[gp] = {"加权和法": round(sum(r["支撑权重"] * r["课程目标达成度"] for r in rows), 3),
              "最小值法": round(min(r["课程目标达成度"] for r in rows), 3), "支撑课程": rows}
result["示范：毕业要求指标点汇总（由校情中枢完成；其他课程为示例数值）"] = gr

json.dump(students, open("class_ch1_scores.json", "w"), ensure_ascii=False, indent=1)
json.dump(result, open("attainment_ch1.json", "w"), ensure_ascii=False, indent=1)
json.dump({"CO": {k: {"名称": v["名称"], "环节": [list(x) for x in v["环节"]]} for k, v in CO.items()},
           "SUPPORT": SUPPORT, "OTHER": OTHER, "THRESHOLD": THRESHOLD, "STU_PASS": STU_PASS},
          open("mapping.json", "w"), ensure_ascii=False, indent=1)
if __name__ == "__main__":
    for co, it in result["课程目标"].items():
        print(co, it["直接评价达成度"], "达成" if it["是否达成"] else "未达成", "个人达成", it["学生个人达成比例"], "自评", it["间接评价（学生自评）"],
              [ (p["环节"], p["得分率"]) for p in it["环节"]])
        for t in it.get("追溯：得分率最低的考核项", []) + it.get("预警：得分率低于 0.6 的考核项", []): print("   ", t)
    for g, v in gr.items(): print(g, v["加权和法"], v["最小值法"])
