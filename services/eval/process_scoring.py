"""过程考核（施工第4步）：从虚拟实验的过程记录自动生成过程评分建议和证据。
适用于第 1 章 5 个实验；换一个实验只需写一份“实验配置”（目标量怎么算、容差、参数范围、失败条件）。"""
import math, random, json, statistics as st
from ch1_items import t_conveyor, t_odometry, t_basket, t_agv, t_drone

# ---------- 实验配置：每个实验的目标量由程序按学生的随机参数算出 ----------
LABS = {
 "LAB-1.1": dict(name="传送带抓取：夹爪对准角度", param="aim_deg", lo=0, hi=60, tol=1.0,
                 gen=lambda r: {"u": r.choice([0.4,0.5,0.6,0.7]), "w": r.choice([0.2,0.25,0.3])},
                 target=lambda p: t_conveyor(p)["angle_below_horizontal_deg"], fail=None),
 "LAB-1.2": dict(name="里程计：选采样间隔", param="T", lo=0.05, hi=2.0, tol=0.03,
                 gen=lambda r: {"sigma": r.choice([0.005,0.01,0.015]), "v": r.choice([0.4,0.5,0.6]), "err": 0.05},
                 target=lambda p: t_odometry(p)["T_min"], fail=None),
 "LAB-1.3": dict(name="投篮：调出手速度", param="v0", lo=4, hi=14, tol=0.05,
                 gen=lambda r: {"h0": r.choice([0.7,0.8,0.9]), "hoop": 2.43, "x": r.choice([3.5,4.0,4.5]), "theta": r.choice([45,55,65])},
                 target=lambda p: t_basket(p)["v0"], fail=None),
 "LAB-1.4": dict(name="AGV：找侧翻临界速度", param="v", lo=0.5, hi=5.0, tol=0.05,
                 gen=lambda r: {"R": r.choice([1.0,1.5,2.0]), "h": r.choice([0.5,0.6,0.7]), "b": 0.5, "mu": 0.9},
                 target=lambda p: t_agv(p)["v_tip"], fail=lambda x, xs: x > xs),   # 超过临界即侧翻
 "LAB-1.5": dict(name="无人机：机头偏转角", param="heading_deg", lo=0, hi=60, tol=0.5,
                 gen=lambda r: {"va": r.choice([10,12,14]), "vw": r.choice([3,4,5]), "d": 1000},
                 target=lambda p: t_drone(p)["heading_deg"], fail=None),
}

# ---------- 过程事件（平台记录的格式）----------
# {"i":序号, "t":秒, "type":"predict"|"run"|"submit"|"report_value", "x":参数值, "signed":结果偏差(正=偏大), "outcome":"ok"/"high"/"low"/"fail"}

def run_result(lab, x, xs):
    if lab["fail"] and lab["fail"](x, xs): return "fail"
    d = x - xs
    return "ok" if abs(d) <= lab["tol"] else ("high" if d > 0 else "low")

# ---------- 特征提取 ----------
def features(lab, xs, events):
    runs = [e for e in events if e["type"] == "run"]
    preds = [e for e in events if e["type"] == "predict"]
    ok_i = next((k for k, e in enumerate(runs) if e["outcome"] == "ok"), None)
    f = {}
    f["success"] = ok_i is not None
    f["n_runs"] = len(runs)
    f["runs_to_success"] = (ok_i + 1) if ok_i is not None else None
    base = max(1, math.ceil(math.log2((lab["hi"] - lab["lo"]) / (2 * lab["tol"]))))   # 二分法需要的次数
    f["bisection_runs"] = base
    # 方向正确率：根据上一次结果（偏大/偏小/失败）调整方向是否正确
    good = tot = 0
    for a, b in zip(runs, runs[1:]):
        if a["outcome"] == "ok": break
        tot += 1
        want_down = a["outcome"] in ("high", "fail")
        good += (b["x"] < a["x"]) if want_down else (b["x"] > a["x"])
    f["direction_ok"] = good / tot if tot else None
    f["pred_first_err"] = abs(preds[0]["x"] - xs) / abs(xs) if preds and (not runs or preds[0]["i"] < runs[0]["i"]) else None
    f["explored_failure"] = any(e["outcome"] == "fail" for e in runs) if lab["fail"] else any(e["outcome"] == "high" for e in runs) and any(e["outcome"] == "low" for e in runs)
    f["duration_s"] = events[-1]["t"] - events[0]["t"] if events else 0
    rep = next((e for e in events if e["type"] == "report_value"), None)
    sub = next((e for e in events if e["type"] == "submit"), None)
    f["report_matches_log"] = None if not (rep and sub) else abs(rep["x"] - sub["x"]) <= lab["tol"]
    f["first_run_exact"] = bool(runs) and abs(runs[0]["x"] - xs) <= lab["tol"] / 4
    return f

# ---------- 打分规则（满分 100）+ 证据 + 疑点 ----------
def score(lab, xs, events):
    f = features(lab, xs, events); s = {}; ev = []; flags = []
    runs = [e for e in events if e["type"] == "run"]
    # 结果 30
    s["结果"] = 30 if f["success"] else (10 if f["n_runs"] else 0)
    ev.append(f'结果：{"第 %d 次运行达到容差内" % f["runs_to_success"] if f["success"] else "未在容差内完成"}（目标 {xs:.3g}，容差 ±{lab["tol"]}）')
    # 方法 35：效率 + 方向
    if f["success"] and f["runs_to_success"] == 1 and f["pred_first_err"] is None:
        eff = 0.3                       # 一次命中但没有任何推理痕迹：方法分只给少量
    elif f["success"]:
        eff = min(1.0, (f["bisection_runs"] + 1) / f["runs_to_success"]) if f["runs_to_success"] > 1 else 1.0
    else:
        eff = 0.2
    d = f["direction_ok"] if f["direction_ok"] is not None else (eff if f["success"] else 0)
    s["方法"] = round(35 * (0.5 * eff + 0.5 * d))
    ev.append(f'方法：共 {f["n_runs"]} 次运行（二分法约需 {f["bisection_runs"]} 次）；根据上次结果调整方向正确率 {"—" if f["direction_ok"] is None else f"{100*f['direction_ok']:.0f}%"}（事件 #{runs[0]["i"] if runs else "-"}–#{runs[-1]["i"] if runs else "-"}）')
    # 建模 25：先预测再验证
    pe = f["pred_first_err"]
    s["建模"] = 0 if pe is None else round(25 * max(0.0, 1 - pe / 0.3))
    ev.append("建模：未先做预测" if pe is None else f"建模：运行前预测误差 {100*pe:.1f}%")
    # 探索 10
    s["探索"] = 10 if f["explored_failure"] else 0
    ev.append("探索：" + ("试到了失败/越界一侧，确认了边界" if f["explored_failure"] else "没有试越界一侧"))
    total = sum(s.values())
    # 疑点（只提示，不扣分，交教师复核）
    if f["first_run_exact"] and pe is None:
        flags.append("第一次运行就几乎精确命中，且运行前没有预测：可能事先拿到答案")
    if f["duration_s"] < 30 and f["success"]:
        flags.append(f'用时仅 {f["duration_s"]:.0f} 秒')
    if f["report_matches_log"] is False:
        flags.append("报告中的数值与实验记录不一致")
    return {"lab": lab["name"], "target": round(xs, 4), "subscores": s, "process_score": total, "features": f, "evidence": ev, "flags": flags}

# ---------- 四类虚拟学生，用来检验打分是否分得开 ----------
def simulate_student(kind, lab, xs, rng):
    ev = []; t = 0; i = 0
    def add(tp, x=None, extra=None):
        nonlocal t, i
        i += 1; t += rng.uniform(8, 40) if kind != "copier" else rng.uniform(2, 5)
        e = {"i": i, "t": round(t, 1), "type": tp}
        if x is not None: e["x"] = round(x, 4)
        if extra: e.update(extra)
        ev.append(e)
    def run(x):
        o = run_result(lab, x, xs); add("run", x, {"outcome": o, "signed": round(x - xs, 4)}); return o
    lo, hi = lab["lo"], lab["hi"]
    if kind == "modeler":
        p = xs * (1 + rng.uniform(-0.04, 0.04)); add("predict", p)
        x = p
        for _ in range(8):
            o = run(x)
            if o == "ok": break
            x = x - math.copysign(max(lab["tol"] * 0.8, abs(x - xs) * 0.7), x - xs)
        if lab["fail"]: run(xs * 1.06); run(xs)          # 确认越界一侧再回到临界
    elif kind == "explorer":
        add("predict", xs * (1 + rng.choice([-1, 1]) * rng.uniform(0.15, 0.4)))
        a, b = lo, hi
        for _ in range(14):
            x = (a + b) / 2; o = run(x)
            if o == "ok": break
            if o in ("high", "fail"): b = x
            else: a = x
    elif kind == "guesser":
        x = rng.uniform(lo, hi)
        for _ in range(15):
            o = run(x)
            if o == "ok": break
            x = min(hi, max(lo, x + rng.uniform(-1, 1) * (hi - lo) * 0.25))
    elif kind == "copier":
        x = xs + rng.uniform(-0.1, 0.1) * lab["tol"]; run(x)
    sub = next((e["x"] for e in reversed(ev) if e["type"] == "run" and e["outcome"] == "ok"), ev[-1].get("x"))
    add("submit", sub)
    rv = sub if kind != "guesser" or rng.random() < 0.7 else sub * 1.2
    add("report_value", rv)
    return ev

if __name__ == "__main__":
    rng = random.Random(29); kinds = ["modeler", "explorer", "guesser", "copier"]
    names = {"modeler": "先建模再验证", "explorer": "系统试探（二分）", "guesser": "乱试", "copier": "疑似抄答案"}
    table = {k: {"score": [], "flag": 0, "succ": 0} for k in kinds}; example = None
    for lab_id, lab in LABS.items():
        for kind in kinds:
            for _ in range(50):
                p = lab["gen"](rng); xs = lab["target"](p)
                r = score(lab, xs, simulate_student(kind, lab, xs, rng))
                table[kind]["score"].append(r["process_score"]); table[kind]["flag"] += bool(r["flags"]); table[kind]["succ"] += r["features"]["success"]
                if lab_id == "LAB-1.4" and kind == "explorer" and example is None: example = r
    print(f'{"学生类型":<10}{"过程分 平均":>10}{"最低–最高":>12}{"完成率":>8}{"标记疑点":>8}')
    for k in kinds:
        sc = table[k]["score"]; n = len(sc)
        print(f'{names[k]:<10}{st.mean(sc):>10.1f}{f"{min(sc)}–{max(sc)}":>12}{100*table[k]["succ"]/n:>7.0f}%{100*table[k]["flag"]/n:>7.0f}%')
    print("\n示例（AGV 实验，系统试探型）："); print(json.dumps({k: example[k] for k in ("lab", "target", "subscores", "process_score", "evidence", "flags")}, ensure_ascii=False, indent=1))
