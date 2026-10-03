# -*- coding: utf-8 -*-
"""热分析的 AI 解释（第 14 轮 H7）：规则先写，有模型时由模型改写（国内 DeepSeek，美国 Claude）。"""
import json


def rules_explain(job):
    st, setup = job["stats"], job["setup"]
    f = setup.get("formula") or {}
    lines, actions = [], []
    tin, tout = st.get("heat_in_w", 0), st.get("heat_out_convection_w", 0)
    lines.append("最高温度 {:.1f} ℃，最低 {:.1f} ℃，表面平均 {:.1f} ℃。".format(st["t_max_c"], st["t_min_c"], st["t_surface_mean_c"]))
    if tin and not setup.get("transient"):
        lines.append("热平衡：进来 {:.1f} W，经对流散走 {:.1f} W{}。".format(tin, tout, "，两者相等，说明计算收敛" if abs(tin - tout) < 0.02 * tin
                                                                         else "，差的部分从固定温度的面流走"))
    groups = st.get("film_groups") or []
    tinf = next((l["t_inf_c"] for l in setup.get("thermal") or [] if l["type"] == "convection"), None)
    if groups and tinf is not None:
        g = max(groups, key=lambda x: x["heat_w"])
        lines.append("散热主要靠对流面：面积 {:.4f} m²，平均比环境高 {:.1f} ℃，散走 {:.1f} W。温升 ≈ 发热 ÷（散热系数 × 面积），"
                     "要降温就三条路：减少发热、加大散热面积（散热筋、散热片）、提高散热系数（风扇、改善通风）。".format(
                         g["area_m2"], g["mean_c"] - tinf, g["heat_w"]))
    lim = f.get("limit_c")
    if f.get("t_oil_c") is not None:
        lines.append("教材公式油温 {} ℃（K_s = {}、A = {} m²），有限元外表面平均 {:.1f} ℃：公式把整个箱体当成一个温度，有限元能看出底部、角落更热、上部更凉。".format(
            f["t_oil_c"], f["K_s"], f["A_m2"], groups[0]["mean_c"] if groups else st["t_surface_mean_c"]))
    if lim is not None:
        if st["t_max_c"] > lim:
            lines.append("最高温度超过限值约 {} ℃：".format(lim) + ("加散热筋（每侧 6–10 条，筋高 20–30 mm）或在输入轴端装风扇（散热系数从 17 提到 30 以上）再算。" if f.get("t_oil_c") is not None
                                                          else "装风扇（散热系数 50 以上）、加片数或片高再算。"))
            actions.append({"kind": "example", "label": "加 8 条散热筋重算" if f.get("t_oil_c") is not None else "片数加到 13 片重算",
                            "params": {"fins": 8} if f.get("t_oil_c") is not None else {"fins": 13}})
        else:
            lines.append("最高温度低于限值约 {} ℃，满足要求，还有 {:.0f} ℃ 余量。".format(lim, lim - st["t_max_c"]))
    if setup.get("analysis") == "thermo_mech":
        lines.append("热应力最大 {:.1f} MPa（安全系数 {}），热变形最大 {:.4g} mm。热应力来自膨胀受约束：约束越死、温差越大，热应力越大；能让零件自由伸长（一端游动支承、留膨胀间隙）就能大幅减小。".format(
            st.get("vm_max_mpa", 0), st.get("safety_factor", "—"), st.get("u_max_mm", 0)))
    if setup.get("transient") and st.get("series"):
        s = st["series"]
        lines.append("瞬态：{:.0f} 秒内平均温度从 {:.1f} ℃ 变到 {:.1f} ℃。".format(s[-1][0], s[0][2], s[-1][2]))
    return {"text": "\n".join(lines), "actions": actions, "engine": "rules"}


EXPLAIN_TOOL = {
    "name": "explain",
    "description": "解释温度场计算结果并给建议",
    "input_schema": {"type": "object", "required": ["text"], "properties": {
        "text": {"type": "string", "description": "3–6 句中文：最热在哪里、为什么（发热、散热面积、散热系数、导热路径）、和公式估算差在哪、是否超限、怎么改；不要编造没给的数字"}}},
}


def explain(llm, job):
    base = rules_explain(job)
    if llm is None or not llm.available():
        return base
    got = {}

    def call_tool(name, args):
        got.update(args)
        return {"ok": True}
    ctx = {"setup": {k: v for k, v in job["setup"].items() if k != "material"}, "stats": job["stats"], "rule_notes": base["text"]}
    try:
        llm.run("你是传热学和机械设计课的老师，给学生解释有限元温度场结果。只根据给出的数据；调用 explain 一次。",
                [{"role": "user", "content": json.dumps(ctx, ensure_ascii=False, default=str)[:12000]}], [EXPLAIN_TOOL], call_tool, max_turns=2)
    except Exception:  # noqa: BLE001
        return base
    if not got.get("text"):
        return base
    return {"text": got["text"].strip(), "actions": base["actions"], "engine": llm.name}
