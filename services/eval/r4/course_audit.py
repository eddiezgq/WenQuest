"""第 4 轮 · 第 4 步：课程质量 AI 审核试跑（大学物理第 1 章）。
检查项：Q3 内容复算、Q4 中英文一致、Q1/Q2 对齐、题库答案复核、Q5 题目质量（作答数据为模拟）。"""
import json, re, math, random, statistics as st, sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import ch1_items as C
bank = json.load(open(os.path.join(os.path.dirname(HERE), "ch1_bank.json")))
mapping = json.load(open(os.path.join(HERE, "mapping.json")))
report = {}

# ---------- Q3 内容复算：课程文件中的参考数值 ----------
def disp_ok(shown, val):
    d = len(shown.split(".")[1]) if "." in shown else 0
    return round(val, d) == float(shown), round(val, d)
b = lambda th: C.t_basket({"h0": 0.8, "hoop": 2.43, "x": 4.0, "theta": th})["v0"]
agv = C.t_agv({"R": 1.5, "h": 0.6, "b": 0.5, "mu": 0.6}) if False else None
REF = [  # (出处, 项目, 文件中的写法, 程序值, 方向说明)
 ("帮助/虚拟实验与实验报告使用说明；第2轮细则", "1.3 投篮 45° 出手速度", "8.14", b(45), "所需速度，偏小不保守"),
 ("同上", "1.3 投篮 55° 出手速度", "7.64", b(55), ""),
 ("同上", "1.3 投篮 65° 出手速度", "7.95", b(65), ""),
]
# 其余参考值用第 3 轮第 1 步核对过的程序值
REF += [("同上", "1.1 传送带抓取 对地速度", "0.56", 0.559, ""), ("同上", "1.1 向下偏角", "26.6", 26.57, ""),
        ("同上", "1.2 里程计 最小采样间隔", "0.57", 0.566, "下限，向上取整是保守的"),
        ("同上", "1.4 AGV 侧翻临界速度", "2.47", 2.476, "限速，向下取整偏安全（N3 保留，并注明）"),
        ("同上", "1.4 AGV 侧滑临界速度", "2.97", 2.971, ""),
        ("同上", "1.5 无人机 偏航角", "24.6", 24.62, ""), ("同上", "1.5 地速", "10.9", 10.91, ""), ("同上", "1.5 用时", "91.7", 91.67, "")]
q3 = []
for src, item, shown, val, note in REF:
    ok, r = disp_ok(shown, val)
    if not ok: q3.append({"出处": src, "项目": item, "文件写法": shown, "程序值": round(val, 4), "四舍五入应为": r, "判断": note or "进位不一致"})
report["Q3 内容复算"] = {"核对条数": len(REF), "不一致": q3}

# ---------- 题库答案复核：用参数重新求解 ----------
import ch1_bank as BK
SOLVERS = {t["id"]: t["solver"] for t in BK.T}
bad_keys = []; checked = 0
for it in bank["items"]:
    ans = SOLVERS[it["template"]](it["params"]); checked += 1
    for k, v in it["answer"].items():
        if isinstance(v, (int, float)) and k in ans and abs(ans[k] - v) > max(1e-6, 0.005 * abs(ans[k])):
            bad_keys.append({"题号": it["id"], "量": k, "题库答案": v, "复算": ans[k]})
report["题库答案复核"] = {"题目数": len(bank["items"]), "已复算": checked, "不一致": bad_keys}

# ---------- Q4 中英文一致：题干中的数字逐一对照 ----------
num = re.compile(r"-?\d+(?:\.\d+)?")
q4 = []
for it in bank["items"]:
    a, e = sorted(num.findall(it["stem_zh"])), sorted(num.findall(it["stem_en"]))
    if a != e: q4.append({"题号": it["id"], "中文数字": a, "英文数字": e})
kp_missing_en = [k["id"] for k in bank["knowledge_points"] if not k.get("name_en")]
report["Q4 中英文一致"] = {"题目数": len(bank["items"]), "数字不一致": q4, "知识点缺英文名": kp_missing_en}

# ---------- Q1/Q2 对齐 ----------
kp_ids = [k["id"] for k in bank["knowledge_points"]]
per_kp = {k: sum(1 for it in bank["items"] if it["kp"] == k) for k in kp_ids}
mapped = {c for co in mapping["CO"].values() for _, cols, _, _ in co["环节"] for c in cols if c in kp_ids}
cos_without = [co for co, v in mapping["CO"].items() if not v["环节"]]
prereq_bad = [k["id"] for k in bank["knowledge_points"] for p in k.get("prerequisites", []) if p not in kp_ids]
report["Q1/Q2 对齐"] = {"Q1 目标覆盖率": round(1 - len(cos_without) / len(mapping["CO"]), 3),
    "Q2 知识点被课程目标覆盖": f"{len(mapped)}/{len(kp_ids)}", "未被覆盖的知识点": sorted(set(kp_ids) - mapped),
    "每个知识点题数": per_kp, "少于10题": [k for k, n in per_kp.items() if n < 10], "前置知识点不存在": prereq_bad}

# ---------- Q5 题目质量（模拟作答，埋入一道答案错误的题） ----------
random.seed(5)
quiz = [random.choice([it for it in bank["items"] if it["kp"] == k and it["id"].endswith("#1")] or
                      [it for it in bank["items"] if it["kp"] == k]) for k in kp_ids]
quiz += random.sample([it for it in bank["items"] if it not in quiz], 10)
WRONG_KEY = quiz[7]["id"]                     # 模拟：这道题的标准答案录错了
EASY_B = {quiz[3]["id"]: -4.0}                 # 模拟：一道题过于容易
thetas = [random.gauss(0.5, 1) for _ in range(300)]
resp = []
for th in thetas:
    row = []
    for it in quiz:
        bb = EASY_B.get(it["id"], it["b"]); p = 1 / (1 + math.exp(-(th - bb)))
        correct = random.random() < p
        if it["id"] == WRONG_KEY: correct = (not correct) if random.random() < 0.85 else correct  # 真会的人被判错
        row.append(int(correct))
    resp.append(row)
tot = [sum(r) for r in resp]; order = sorted(range(len(resp)), key=lambda i: tot[i]); g = int(0.27 * len(resp))
low, high = order[:g], order[-g:]
def pbis(j):
    x = [r[j] for r in resp]; rest = [tot[i] - x[i] for i in range(len(resp))]
    mx, mr = st.mean(x), st.mean(rest); sx, sr = st.pstdev(x), st.pstdev(rest)
    return 0 if sx == 0 or sr == 0 else sum((a - mx) * (c - mr) for a, c in zip(x, rest)) / len(x) / (sx * sr)
q5 = []
for j, it in enumerate(quiz):
    p = st.mean(r[j] for r in resp); d = pbis(j)
    ph, pl = st.mean(resp[i][j] for i in high), st.mean(resp[i][j] for i in low)
    why = []
    if p < 0.20: why.append("太难")
    if p > 0.95: why.append("太易")
    if d < 0.20: why.append("区分度低")
    if ph < pl: why.append("高分组反而答错更多：优先核查答案和题干")
    if why: q5.append({"题号": it["id"], "难度p": round(p, 3), "区分度": round(d, 3), "高分组": round(ph, 3), "低分组": round(pl, 3), "问题": why})
report["Q5 题目质量（模拟作答）"] = {"测验题数": len(quiz), "模拟人数": len(resp), "埋入：答案录错": WRONG_KEY,
    "埋入：过于容易": list(EASY_B), "检出": q5}
wr = os.path.join(HERE, "wording_review.json")
if os.path.exists(wr):   # AI 表述审核结果（由 AI 审核员生成、经人工核对），并入报告
    w = json.load(open(wr))
    report["AI 表述审核"] = {"条数": len(w), "高": sum(x["严重程度"] == "高" for x in w),
        "高-属实": sum(x["严重程度"] == "高" and x.get("核对") == "属实" for x in w),
        "误报": sum(x.get("核对") == "误报" for x in w), "明细": "wording_review.json"}
json.dump(report, open(os.path.join(HERE, "audit_ch1.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(report, ensure_ascii=False, indent=1)[:4000])
