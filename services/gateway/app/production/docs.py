"""Lab guide, lab report template and lesson plan (Word), in the chapter-1 benchmark layout
(samples/大学物理/生成脚本/build_guides.py and build_ch1.py)."""
from __future__ import annotations

from pathlib import Path

from .docgen import Doc

LINK = ("问渠课程页“虚拟实验”，或课件实验页的“打开虚拟实验”按钮 / "
        "the Virtual Lab link on the course page or the “Open virtual lab” button in the slides")

REPORT_SECTIONS = [
    ("一、实验目的", "1  Objectives", 3), ("二、实验原理（写出主要公式）", "2  Principles (key formulas)", 5),
    ("三、实验步骤（简要）", "3  Procedure (brief)", 4), ("四、数据记录与处理", "4  Data and processing", 0),
    ("五、结果与误差分析", "5  Results and error analysis", 6), ("六、实际问题的建模与求解", "6  Modelling a real problem", 0),
    ("七、结论", "7  Conclusion", 3), ("八、思考题", "8  Questions", 6),
]
FIVE = [("① 实际问题（用自己的话描述，给出已知数据）", "① The problem (in your own words, with the given data)"),
        ("② 建立模型（写出简化假设）", "② The model (state your assumptions)"),
        ("③ 求解（公式与数值）", "③ Solution (formulas and numbers)"),
        ("④ 用虚拟实验检验（写出实验设置与结果）", "④ Check with the virtual lab (settings and results)"),
        ("⑤ 模型在哪里失效？怎样修正？", "⑤ Where does the model fail? How would you improve it?")]


def _widths(n: int, total: float = 16.0) -> list[float]:
    return [round(total / n, 2)] * n


def guide(spec: dict, gp: dict, out: Path, no: str) -> Path:
    g = gp["guide"]
    s = spec
    d = Doc()
    d.title(f"实验 {no}  {s['lab']['title'][0]}", f"Lab {no}  {s['lab']['title'][1]}")
    d.bh("一、实验目的", "1  Objectives")
    d.blist(g["goal"] or [s["goal"]], numbered=True)
    d.bh("二、实验原理", "2  Principles")
    for zh, en in g["theory"]:
        d.bp(zh, en)
    d.bh("三、实验环境", "3  The virtual lab")
    d.p(f"打开方式：{LINK}")
    d.bp(f"场景：{s['lab']['robot_scene'][0]}；{s['lab']['life_scene'][0]}", f"Scenes: {s['lab']['robot_scene'][1]}; {s['lab']['life_scene'][1]}")
    if g["env"]:
        both = lambda x: x[0] if x[0] == x[1] or not x[1] else f"{x[0]}\n{x[1]}"  # noqa: E731
        d.table(["项目 Item", "范围 Range"], [[f"{e['item'][0]} {e['item'][1]}", both(e["range"])] for e in g["env"]],
                widths=[4.5, 11.5], font_size=9.5)
    d.bh("四、实验步骤", "4  Procedure")
    d.blist(g["steps"], numbered=True)
    d.bh("五、数据记录", "5  Data record")
    d.bp("以下表格同时出现在实验报告模板中，请在报告里填写。", "The same tables appear in the report template; fill them in there.")
    for t in g["tables"]:
        d.p(f"{t['caption'][0]}  {t['caption'][1]}", indent=False)
        d.table(t["headers"], t["rows"], widths=_widths(len(t["headers"])), font_size=9.5)
    d.bh("六、注意事项", "6  Notes")
    d.blist(g["cautions"])
    d.bh("七、思考题", "7  Questions")
    d.blist(g["questions"], numbered=True)
    d.bh("八、与实际问题的联系", "8  Connection to a real problem")
    p = s["problem"]
    d.p(f"机器人问题：{p['title'][0]}", indent=False).runs[0].bold = True
    d.en(f"Robot problem: {p['title'][1]}")
    q = g["problem_question"] if g["problem_question"][0] else p["text"]
    d.bp(q[0], q[1])
    d.bp("请在实验报告“实际问题的建模与求解”一栏中按五步完成：① 实际问题 ② 建立模型（写出简化假设）③ 求解 ④ 用虚拟实验检验 ⑤ 指出模型在哪里失效、怎样修正。",
         "In the report section “Modelling a real problem”, work through five steps: ① the problem ② the model (state your assumptions) "
         "③ the solution ④ a check with the virtual lab ⑤ where the model fails and how to improve it.")
    d.p("生活中的例子：" + s["everyday"]["text"][0], indent=False)
    d.en("Everyday example: " + s["everyday"]["text"][1])
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save(str(out))
    return out


def report(spec: dict, gp: dict, out: Path, no: str) -> Path:
    g, s = gp["guide"], spec
    d = Doc()
    d.title(f"实验报告  实验 {no}  {s['lab']['title'][0]}", f"Lab Report  Lab {no}  {s['lab']['title'][1]}")
    d.table(["姓名 Name", "", "学号 ID", "", "日期 Date", ""], [["班级 Class", "", "同组 Partner", "", "成绩 Score", ""]],
            widths=[2.4, 3.2, 2.2, 2.8, 2.2, 3.2], font_size=10)
    d.en("提交方式：填写本模板后在问渠“作业”中上传；也可在问渠中在线填写同样的栏目。  Submit this file in WenQuest Assignments, or fill in the same sections online.", size=9)
    for zh, en, n in REPORT_SECTIONS:
        d.bh(zh, en)
        if zh.startswith("四"):
            for t in g["tables"]:
                d.p(f"{t['caption'][0]}  {t['caption'][1]}", indent=False)
                d.table(t["headers"], t["rows"], widths=_widths(len(t["headers"])), font_size=9.5)
            d.bp("数据处理：写出计算过程，至少完成一张图（如“误差—参数”或“测量值—理论值”）。",
                 "Processing: show your calculations and include at least one graph (e.g. error vs parameter, or measured vs theory).")
            d.lines(4)
        elif zh.startswith("六"):
            q = g["problem_question"] if g["problem_question"][0] else s["problem"]["text"]
            d.p(f"问题：{s['problem']['title'][0]}", indent=False).runs[0].bold = True
            d.bp(q[0], q[1])
            for step, en_step in FIVE:
                d.p(step, indent=False)
                d.en(en_step)
                d.lines(3)
        elif zh.startswith("八") and g["questions"]:
            for zq, eq in g["questions"]:
                d.p(zq, indent=False)
                d.en(eq)
                d.lines(3)
        else:
            d.lines(n)
    d.bh("九、AI 使用声明", "9  AI use statement")
    d.p("□ 未使用 AI　　□ 用 AI 解释概念　　□ 用 AI 检查计算　　□ 其他：____________", indent=False)
    d.en("□ No AI used   □ AI to explain concepts   □ AI to check calculations   □ Other: ____________")
    d.p("如使用了 AI，请写明用在哪里：", indent=False)
    d.lines(2)
    d.bh("评分量规", "Rubric")
    d.table(["项目 Criterion", "分值 Points", "要求 What earns full marks"],
            [["原理 Principles", "20", "公式正确、说明物理意义 / correct formulas with physical meaning"],
             ["数据 Data", "25", "数据完整、单位与有效数字规范 / complete data, correct units and significant figures"],
             ["分析 Analysis", "25", "理论与测量比较、误差来源分析 / theory vs measurement, sources of error"],
             ["实际问题 Real problem", "20", "五步完整，假设清楚，指出模型局限 / all five steps, clear assumptions, limits named"],
             ["规范 Presentation", "10", "书写清楚、图表规范、AI 使用如实声明 / clear writing and graphs, honest AI statement"]],
            widths=[4.0, 2.2, 9.8], font_size=9.5)
    d.en("AI 按本量规给出评分建议，教师复核后发布。  AI suggests a score against this rubric; the teacher reviews it before release.", size=9)
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save(str(out))
    return out


def plan(spec: dict, gp: dict, out: Path, no: str, course: str, chapter: str, teacher: str = "") -> Path:
    pl, s = gp["plan"], spec
    d = Doc()
    d.title(f"{course}教案", f"{chapter}  ·  {no} {s['title'][0]}" + (f"  ·  授课教师：{teacher}" if teacher else ""))
    d.table(["课题", "授课对象", "学时", "授课方式"],
            [[f"{no} {s['title'][0]}", pl["audience"] or "—", pl["hours"] or "2 学时", pl["method"] or "讲授 + 动画 + 虚拟实验 + 课堂练习"]],
            widths=[5.5, 4, 3, 4])
    d.h("一、教学目标")
    o = pl["objectives"]
    d.bullets([("知识目标：", o["knowledge"] or s["goal"][0]), ("能力目标：", o["ability"] or "能针对实际问题建立模型并求解。"),
               ("素养目标：", o["literacy"] or "体会“建立模型—求解—检验—修正”的科学方法。")])
    d.h("二、教学重点与难点")
    d.kv("重点", pl["key"] or "；".join(p[0] for p in s["concept"]["points"][:2]))
    d.kv("难点", pl["difficult"] or "—")
    d.h("三、教学方法")
    d.p("以机器人实际问题驱动：先提出问题，再讲概念，用动画建立直观，用虚拟实验验证，最后回到问题按五步建模求解。")
    d.h("四、教学过程")
    rows = [[x["phase"], f"{x['minutes']} min" if x["minutes"] else "", x["content"], x["activity"]] for x in pl["process"]]
    if not rows:
        rows = [["导入", "10 min", s["problem"]["text"][0], "提出机器人问题，学生讨论"],
                ["新课", "40 min", "；".join(p[0] for p in s["concept"]["points"]), "讲授 + 板书"],
                ["动画", "10 min", s["animation"]["question"][0], "播放并暂停提问"],
                ["实验", "15 min", "；".join(t[0] for t in s["lab"]["tasks"]), "课堂演示"],
                ["建模", "15 min", s["model"]["solve"][0], "师生共同完成五步"],
                ["小结", "10 min", "；".join(x[0] for x in s["summary"]), "布置练习和实验报告"]]
    d.table(["环节", "时间", "教学内容", "师生活动"], rows, widths=[1.8, 1.8, 7.5, 5])
    d.h("五、板书设计")
    d.p(pl["board"] or "—", indent=False)
    d.h("六、课后作业")
    d.p(pl["homework"] or "完成本节练习；完成虚拟实验任务并按实验指导书写实验报告。", indent=False)
    d.h("七、教学反思")
    d.p(pl["reflection"] or "（课后填写）", indent=False)
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save(str(out))
    return out
