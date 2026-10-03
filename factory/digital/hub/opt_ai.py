# -*- coding: utf-8 -*-
"""设计优化的 AI（第 14 轮 H7）：一句话填优化设置、解释优化结果。规则兜底，有模型时由模型理解 / 改写。"""
import json
import re

NUM = r"(\d+(?:\.\d+)?)"
VAR_WORDS = {
    "shaft": [("齿轮位", "d_gear"), ("轴伸", "d_end"), ("轴端", "d_end")],
    "housing": [("筋数", "fins"), ("散热筋数", "fins"), ("筋高", "fin_h"), ("壁厚", "wall")],
    "heatsink": [("片数", "fins"), ("片高", "fin_h"), ("片厚", "fin_t")],
}


def rules_setup(text, problem, form):
    out, notes, miss = {"vars": {}}, [], []
    t = text.replace("～", "~").replace("—", "-").replace("（", "(").replace("）", ")").replace("℃", "度")
    for clause in [c.strip() for c in re.split(r"[，,；;。\n]", t) if c.strip()]:
        c = clause.replace(" ", "")
        hit = False
        m = re.search(r"安全系数(?:不小于|不低于|至少|≥|>=|大于)" + NUM, c)
        if m:
            out["sf_min"] = float(m.group(1))
            notes.append("“{}” → 安全系数 ≥ {}".format(clause, m.group(1)))
            hit = True
        if re.search(r"无限寿命|寿命无限", c):
            out["life"] = "infinite"
            notes.append("“{}” → 疲劳寿命：无限".format(clause))
            hit = True
        else:
            m = re.search(r"寿命(?:至少|不少于|≥)?" + NUM + r"(?:小时|h)", c)
            if m:
                out["life"], out["life_h"] = "hours", float(m.group(1))
                notes.append("“{}” → 疲劳寿命 ≥ {} 小时".format(clause, m.group(1)))
                hit = True
        m = re.search(r"(?:不超过|不高于|低于|≤|<=|最高温度)" + NUM + r"度?", c)
        if m and problem != "shaft" and ("度" in c or "温" in c):
            out["t_max"] = float(m.group(1))
            notes.append("“{}” → 最高温度 ≤ {} ℃".format(clause, m.group(1)))
            hit = True
        if re.search(r"越轻|最轻|轻量|省料|越少越好", c) and re.search(r"凉|温度最低|温度越低", c) and problem != "shaft":
            out["obj"] = "both"
            hit = True
        elif re.search(r"越轻|最轻|轻量|省料|越少越好", c):
            out["obj"] = "mass"
            notes.append("“{}” → 目标：最轻".format(clause))
            hit = True
        elif re.search(r"最凉|温度最低|温度越低|越凉", c) and problem != "shaft":
            out["obj"] = "t_max"
            notes.append("“{}” → 目标：最凉".format(clause))
            hit = True
        m = re.search(r"算" + NUM + r"次", c)
        if m:
            out["n"] = int(float(m.group(1)))
            notes.append("“{}” → 分析 {} 次".format(clause, out["n"]))
            hit = True
        for w, name in VAR_WORDS.get(problem, []):
            if w in c:
                m = re.search(NUM + r"(?:mm|毫米)?(?:到|~|-|至)" + NUM, c)
                if m:
                    out["vars"][name] = {"on": True, "low": float(m.group(1)), "high": float(m.group(2))}
                    notes.append("“{}” → {} 在 {}–{} 之间变".format(clause, w, m.group(1), m.group(2)))
                    hit = True
                elif re.search(r"不变|不动|固定", c):
                    out["vars"][name] = {"on": False}
                    notes.append("“{}” → {} 不参加优化".format(clause, w))
                    hit = True
                break
        if not hit:
            if re.search(r"优化|输出轴|箱体|散热片", c):
                continue
            miss.append(clause)
    return {"form": out, "notes": notes, "unmatched": miss}


SETUP_TOOL = {
    "name": "fill_opt_setup", "description": "把一句话变成优化设置",
    "input_schema": {"type": "object", "properties": {
        "form": {"type": "object", "description": "只填有把握的项：obj（mass / t_max / both）、sf_min、life（infinite / hours）、life_h、t_max、n（次数）、"
                                                   "vars（{变量名: {on, low, high}}，变量名只能用给出的）"},
        "notes": {"type": "array", "items": {"type": "string"}}, "unmatched": {"type": "array", "items": {"type": "string"}}}},
}


def setup(llm, text, problem, form, var_names):
    text = (text or "").strip()[:500]
    if not text:
        raise ValueError("请写一句话描述目标和要求")
    if llm is not None and llm.available():
        got = {}

        def call_tool(name, args):
            got.update(args)
            return {"ok": True}
        try:
            llm.run("你是结构 / 热设计优化助手。把用户的一句话变成优化设置，调用 fill_opt_setup 一次；不确定的写进 unmatched。",
                    [{"role": "user", "content": json.dumps({"sentence": text, "problem": problem, "variables": var_names,
                                                             "current_form": form}, ensure_ascii=False)}], [SETUP_TOOL], call_tool, max_turns=2)
            f = got.get("form") or {}
            f["vars"] = {k: v for k, v in (f.get("vars") or {}).items() if k in var_names and isinstance(v, dict)}
            if f.get("obj") not in (None, "mass", "t_max", "both") or (problem == "shaft" and f.get("obj") in ("t_max", "both")):
                f.pop("obj", None)
            if f:
                return {"form": f, "notes": got.get("notes") or [], "unmatched": got.get("unmatched") or [], "engine": llm.name}
        except Exception as e:  # noqa: BLE001
            return dict(rules_setup(text, problem, form), engine="rules", note="模型暂时不可用（{}），已用规则理解".format(str(e)[:60]))
    return dict(rules_setup(text, problem, form), engine="rules")


def rules_explain(job, res):
    trials = res.get("trials") or []
    spec = job["spec"]
    cons = res.get("constraints") or {}
    base = res.get("base") or {}
    best = (res.get("best") or [None])[0]
    ok = [t for t in trials if t["ok"]]
    lines = ["共分析 {} 次（{} 秒），{} 次满足全部要求。".format(len(trials), res.get("seconds"), len(ok))]
    if base:
        lines.append("现行设计：" + ("满足要求。" if base["ok"] else "不满足（{}）。".format("；".join(base["violation"]))))
    if not best:
        lines.append("没有找到满足要求的方案：放宽要求（安全系数、温度上限），或把尺寸范围放大再算。")
        return {"text": "\n".join(lines), "engine": "rules"}
    if base.get("mass_kg") and best.get("mass_kg"):
        lines.append("最好的一组质量 {:.3f} kg，比现行 {:+.1f}%。".format(best["mass_kg"], (best["mass_kg"] / base["mass_kg"] - 1) * 100))
    if cons.get("sf_min") is not None and best.get("sf") is not None:
        tight = best["sf"] < cons["sf_min"] * 1.08
        lines.append("最好的一组安全系数 {:.2f}（要求 ≥ {}）：{}".format(best["sf"], cons["sf_min"],
                     "已经贴着要求，是强度卡住了它，再细就不够强。" if tight else "离要求还有余量，卡住它的是尺寸范围下限或其他要求。"))
    if cons.get("t_max") is not None and best.get("t_max") is not None:
        tight = best["t_max"] > cons["t_max"] - 3
        lines.append("最好的一组最高温度 {:.1f} ℃（要求 ≤ {}）：{}".format(best["t_max"], cons["t_max"],
                     "贴着温度上限，是散热卡住了它。" if tight else "温度还有余量。"))
    if res.get("pareto"):
        lines.append("两个目标互相矛盾：帕累托前沿上的 {} 组方案，越轻的越热；按工厂更看重哪个来选。".format(len(res["pareto"])))
    if spec.get("problem") == "shaft":
        lines.append("注意：键槽底角是尖角，最大应力随网格变化，安全系数有几个百分点的“噪声”；选定方案后在“仿真与分析”用细网格复核，并按 GB/T 1095 核对键的尺寸（设计台会提示）。")
    lines.append("优化结果没有直接改设计：点“送到设计台”（或“到仿真与分析”），确认后再发布、审批。")
    return {"text": "\n".join(lines), "engine": "rules"}


EXPLAIN_TOOL = {"name": "explain", "description": "解释优化结果",
                "input_schema": {"type": "object", "required": ["text"], "properties": {"text": {
                    "type": "string", "description": "3–6 句中文：找到了什么、比现行好多少、哪个要求卡住了最优解、两个目标怎么取舍、下一步做什么；不要编造数字"}}}}


def explain(llm, job, res):
    base = rules_explain(job, res)
    if llm is None or not llm.available():
        return base
    got = {}

    def call_tool(name, args):
        got.update(args)
        return {"ok": True}
    ctx = {"problem": job["spec"].get("problem"), "constraints": res.get("constraints"), "objectives": res.get("objectives"),
           "base": res.get("base"), "best": (res.get("best") or [])[:3], "pareto": (res.get("pareto") or [])[:6],
           "n_trials": len(res.get("trials") or []), "rule_notes": base["text"]}
    try:
        llm.run("你是机械设计课的老师，给学生解释设计优化（Optuna）的结果。只根据给出的数据；调用 explain 一次。",
                [{"role": "user", "content": json.dumps(ctx, ensure_ascii=False, default=str)[:12000]}], [EXPLAIN_TOOL], call_tool, max_turns=2)
    except Exception:  # noqa: BLE001
        return base
    return {"text": got["text"].strip(), "engine": llm.name} if got.get("text") else base
