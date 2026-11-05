"""第 5 轮 · 第 1 步：个性化学习路径（规则推荐）与模拟检验。
规则：先补掌握度最低的前置知识点，再练当前知识点；每次 3–5 项，每项附理由。
掌握度用第 3 轮的档位：θ<-0.5 未掌握，<0.5 基本掌握，<1.5 熟练，其余精通。"""
import json, math, random, statistics as st, os
HERE = os.path.dirname(os.path.abspath(__file__))
bank = json.load(open(os.path.join(os.path.dirname(HERE), "ch1_bank.json")))
KP = {k["id"]: k for k in bank["knowledge_points"]}
ORDER = [k["id"] for k in bank["knowledge_points"]]
ITEMS = {k: [it for it in bank["items"] if it["kp"] == k] for k in KP}
TIERS = [(-0.5, "未掌握"), (0.5, "基本掌握"), (1.5, "熟练"), (99, "精通")]
tier = lambda t: next(n for c, n in TIERS if t < c)
TARGET = 0.5                       # 目标：至少“熟练”
MEDIA = {"P1-1.1-a": "动画 1.1", "P1-1.1-b": "实验 1.1 传送带", "P1-1.2-a": "动画 1.2", "P1-1.2-b": "实验 1.2 里程计",
         "P1-1.3-a": "动画 1.3", "P1-1.3-b": "实验 1.3 投篮", "P1-1.3-c": "实验 1.3 投篮（偏差任务）", "P1-1.4-a": "动画 1.4",
         "P1-1.4-b": "实验 1.4 AGV", "P1-1.5-a": "实验 1.5 无人机"}

def recommend(theta, n_max=5, rng=None):
    """theta: {kp: 估计掌握度}。返回 3–5 项推荐，每项附理由。"""
    weak = sorted([k for k in ORDER if theta[k] < TARGET], key=lambda k: theta[k])
    picks, seen = [], set()
    for k in weak:
        # 沿前置链往上找：前置也没达标，先补前置
        chain, cur = [], k
        while True:
            pre = [p for p in KP[cur]["prerequisites"] if theta[p] < TARGET and p not in seen]
            if not pre: break
            cur = min(pre, key=lambda p: theta[p]); chain.append(cur)
        for p in reversed(chain):
            if p in seen: continue
            seen.add(p)
            picks.append({"知识点": p, "名称": KP[p]["name_zh"], "类型": "补前置",
                          "理由": f"“{KP[k]['name_zh']}”依赖“{KP[p]['name_zh']}”，你在这一项还是{tier(theta[p])}"})
        if k not in seen:
            seen.add(k)
            picks.append({"知识点": k, "名称": KP[k]["name_zh"], "类型": "练当前",
                          "理由": f"你在“{KP[k]['name_zh']}”是{tier(theta[k])}，是本章最需要加强的知识点之一"})
        if len(picks) >= n_max: break
    picks = picks[:n_max]
    if len(picks) < 3:   # 都已熟练：补足到 3 项，选掌握度最低的知识点做“挑战”，题目难度略高于当前水平
        for k in sorted(ORDER, key=lambda k: theta[k]):
            if k in seen: continue
            seen.add(k)
            picks.append({"知识点": k, "名称": KP[k]["name_zh"], "类型": "挑战",
                          "理由": f"你已经{tier(theta[k])}，做一道更难的题，向“精通”推进", "_up": 0.8})
            if len(picks) >= 3: break
    for p in picks:   # 配内容：难度最接近当前掌握度的题 + 对应动画或实验
        aim = theta[p["知识点"]] + p.pop("_up", 0)
        its = sorted(ITEMS[p["知识点"]], key=lambda it: abs(it["b"] - aim))
        p["练习题"] = its[0]["id"]; p["资源"] = MEDIA[p["知识点"]]
    return picks

# ---------- 模拟检验 ----------
WEAK = {"P1-1.2-b": -1.4, "P1-1.3-c": -1.8}     # 与第 4 轮模拟一致的两个卡点
def make_students(n, seed):
    rnd = random.Random(seed); S = []
    for _ in range(n):
        g = rnd.gauss(0.6, 0.8)
        S.append({k: 0.8 * g + WEAK.get(k, 0) + rnd.gauss(0, 0.5) for k in ORDER})
    return S

def practice(true, k, b, rnd):
    """练一题：难度贴近当前水平时收获最大；前置未达标时收获减半（学不进去）。"""
    pre_ok = all(true[p] >= 0 for p in KP[k]["prerequisites"])
    gain = 0.35 * math.exp(-((b - true[k]) ** 2) / 2) * (1 if pre_ok else 0.5)
    true[k] += gain * (0.7 + 0.6 * rnd.random())

def run(policy, S, rounds=4, seed=1):
    rnd = random.Random(seed); out = []
    for s0 in S:
        true = dict(s0)
        for _ in range(rounds):
            est = {k: true[k] + rnd.gauss(0, 0.35) for k in ORDER}      # 掌握度估计有误差
            if policy == "推荐":
                ks = [(p["知识点"], next(it for it in ITEMS[p["知识点"]] if it["id"] == p["练习题"])["b"]) for p in recommend(est)]
            else:
                ks = []
                for k in rnd.sample(ORDER, 5): ks.append((k, rnd.choice(ITEMS[k])["b"]))
            for k, b in ks:
                for _ in range(2): practice(true, k, b, rnd)          # 每项练 2 题
        out.append(true)
    return out

if __name__ == "__main__":
    S = make_students(40, 20261105)
    est0 = [{k: s[k] + random.Random(i).gauss(0, 0.35) for k in ORDER} for i, s in enumerate(S)]
    # 1) 推荐是否集中在真实卡点
    cnt = {k: 0 for k in ORDER}; total = 0
    for e in est0:
        for p in recommend(e): cnt[p["知识点"]] += 1; total += 1
    weak_share = (cnt["P1-1.2-b"] + cnt["P1-1.3-c"]) / total
    students_hit = sum(any(p["知识点"] in WEAK for p in recommend(e)) for e in est0) / len(est0)
    sizes = [len(recommend(e)) for e in est0]
    # 2) 按推荐练 vs 随机练（每人 4 轮 × 5 项 × 2 题 = 40 题，题量相同）
    P = lambda t: 1 / (1 + math.exp(-t))
    res = {}
    for pol in ("推荐", "随机"):
        fin = run(pol, S)
        res[pol] = {"全章平均掌握概率提升": round(st.mean(st.mean(P(f[k]) - P(s[k]) for k in ORDER) for f, s in zip(fin, S)), 3),
                    "两个卡点平均提升": round(st.mean(st.mean(P(f[k]) - P(s[k]) for k in WEAK) for f, s in zip(fin, S)), 3),
                    "达到“熟练”及以上的知识点比例": round(st.mean(st.mean(f[k] >= 0.5 for k in ORDER) for f in fin), 3)}
    base = round(st.mean(st.mean(s[k] >= 0.5 for k in ORDER) for s in S), 3)
    examples = []
    for i in (0, 7):
        examples.append({"学生": f"S{i+1:03d}", "掌握度": {KP[k]["name_zh"]: f"{tier(est0[i][k])}（{est0[i][k]:+.2f}）" for k in ORDER},
                         "推荐": recommend(est0[i])})
    result = {"推荐分布（次数）": {KP[k]["name_zh"]: cnt[k] for k in ORDER}, "推荐落在两个卡点的比例": round(weak_share, 3),
              "至少有一项推荐落在卡点的学生比例": round(students_hit, 3), "每人推荐项数范围": [min(sizes), max(sizes)], "练习前达到熟练及以上的比例": base, "练习对比": res, "示例": examples}
    json.dump(result, open(os.path.join(HERE, "learning_path_results.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in result.items() if k != "示例"}, ensure_ascii=False, indent=1))
    for p in examples[0]["推荐"]: print(" ", p["类型"], p["名称"], "|", p["理由"], "|", p["练习题"], p["资源"])
