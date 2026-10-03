"""第 1 章实验指导书（R7）与实验报告模板（R8），中英对照。
排版代码沿用大学物理第 1 章（samples/大学物理/生成脚本/build_guides.py）；内容见 labs_ch1.py。
运行：python build_guides.py
"""
from pathlib import Path
from docgen import Doc
from labs_ch1 import LABS, LINK, H, HE

BASE = Path(__file__).resolve().parents[1] / "课程资料" / "第1章 CMOS反相器" / "虚拟实验"
GUIDES = BASE
REPORTS = BASE / "实验报告模板"
GUIDES.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)


def env_table(d, lab):
    d.table(["项目 Item", "范围 Range"], [[f"{a} {b}", f"{c}\n{e}"] for a, b, c, e in lab["env"]], widths=[4.5, 11.5], font_size=9.5)


def guide(lab):
    d = Doc()
    d.title(f"实验 {lab['no']}  {lab['zh']}", f"Lab {lab['no']}  {lab['en']}")
    d.en(f"{H}    {HE}", size=9)
    d.bh("一、实验目的", "1  Objectives")
    d.blist(lab["goal"], numbered=True)
    d.bh("二、实验原理", "2  Principles")
    for zh, en in lab["theory"]:
        d.bp(zh, en)
    d.bh("三、实验环境与参数范围", "3  Lab environment and parameter ranges")
    d.bp("本实验在问渠虚拟实验中完成，电脑和手机均可使用。", "The lab runs in the WenQuest virtual lab on a computer or phone.")
    d.en("入口 Access: " + LINK)
    env_table(d, lab)
    d.bh("四、实验步骤", "4  Procedure")
    d.blist(lab["steps"], numbered=True)
    d.bh("五、数据记录", "5  Data record")
    d.bp("以下表格同时出现在实验报告模板中，请在报告里填写。", "The same tables appear in the report template; fill them in there.")
    for cap, head, rows, widths in lab["tables"]:
        d.p(cap, indent=False)
        d.table(head, rows, widths=widths, font_size=9.5)
    d.bh("六、注意事项", "6  Notes")
    d.blist(lab["cautions"])
    d.bh("七、思考题", "7  Questions")
    d.blist(lab["questions"], numbered=True)
    t, te, q, qe = lab["problem"]
    d.bh("八、与实际问题的联系", "8  Connection to a real problem")
    d.p(f"机器人问题：{t}", indent=False).runs[0].bold = True
    d.en(f"Robot problem: {te}")
    d.bp(q, qe)
    d.bp("请在实验报告“实际问题的建模与求解”一栏中按五步完成：① 实际问题 ② 建立模型（写出简化假设）③ 求解 ④ 用虚拟实验检验 ⑤ 指出模型在哪里失效、怎样修正。",
         "In the report section “Modelling a real problem”, work through five steps: ① the problem ② the model (state your assumptions) ③ the solution ④ a check with the virtual lab ⑤ where the model fails and how to improve it.")
    d.p("生活中的例子：" + lab["everyday"][0], indent=False)
    d.en("Everyday example: " + lab["everyday"][1])
    d.save(GUIDES / f"{lab['file']} 实验指导书.docx")


SECTIONS = [
    ("一、实验目的", "1  Objectives", 3), ("二、实验原理（写出主要公式）", "2  Principles (key formulas)", 5),
    ("三、实验步骤（简要）", "3  Procedure (brief)", 4), ("四、数据记录与处理", "4  Data and processing", 0),
    ("五、结果与误差分析", "5  Results and error analysis", 6), ("六、实际问题的建模与求解", "6  Modelling a real problem", 0),
    ("七、结论", "7  Conclusion", 3), ("八、思考题", "8  Questions", 6),
]


def report(lab=None):
    d = Doc()
    if lab:
        d.title(f"实验报告  实验 {lab['no']}  {lab['zh']}", f"Lab Report  Lab {lab['no']}  {lab['en']}")
    else:
        d.title("虚拟实验报告（通用模板）", "Virtual Lab Report (general template)")
    d.table(["姓名 Name", "", "学号 ID", "", "日期 Date", ""], [["班级 Class", "", "同组 Partner", "", "成绩 Score", ""]],
            widths=[2.4, 3.2, 2.2, 2.8, 2.2, 3.2], font_size=10)
    d.en("提交方式：填写本模板后在问渠“作业”中上传；也可在问渠中在线填写同样的栏目。  Submit this file in WenQuest Assignments, or fill in the same sections online.", size=9)
    for zh, en, n in SECTIONS:
        d.bh(zh, en)
        if zh.startswith("四") and lab:
            for cap, head, rows, widths in lab["tables"]:
                d.p(cap, indent=False)
                d.table(head, rows, widths=widths, font_size=9.5)
            d.bp("数据处理：写出计算过程，至少完成一张图（如“误差—参数”或“测量值—理论值”）。", "Processing: show your calculations and include at least one graph (e.g. error vs parameter, or measured vs theory).")
            d.lines(4)
        elif zh.startswith("四"):
            d.bp("按实验指导书中的表格记录数据；写出计算过程，至少完成一张图。", "Record data in the tables from the lab guide; show your calculations and include at least one graph.")
            d.lines(8)
        elif zh.startswith("六"):
            if lab:
                t, te, q, qe = lab["problem"]
                d.p(f"问题：{t}", indent=False).runs[0].bold = True
                d.bp(q, qe)
            for step, en in [("① 实际问题（用自己的话描述，给出已知数据）", "① The problem (in your own words, with the given data)"),
                             ("② 建立模型（写出简化假设）", "② The model (state your assumptions)"),
                             ("③ 求解（公式与数值）", "③ Solution (formulas and numbers)"),
                             ("④ 用虚拟实验检验（写出实验设置与结果）", "④ Check with the virtual lab (settings and results)"),
                             ("⑤ 模型在哪里失效？怎样修正？", "⑤ Where does the model fail? How would you improve it?")]:
                d.p(step, indent=False)
                d.en(en)
                d.lines(3)
        elif zh.startswith("八") and lab:
            for zhq, enq in lab["questions"]:
                d.p(zhq, indent=False); d.en(enq); d.lines(3)
        else:
            d.lines(n)
    d.bh("九、AI 使用声明", "9  AI use statement")
    d.p("□ 未使用 AI　　□ 用 AI 解释概念　　□ 用 AI 检查计算　　□ 其他：____________", indent=False)
    d.en("□ No AI used   □ AI to explain concepts   □ AI to check calculations   □ Other: ____________")
    d.p("如使用了 AI，请写明用在哪里：", indent=False); d.lines(2)
    d.bh("评分量规", "Rubric")
    d.table(["项目 Criterion", "分值 Points", "要求 What earns full marks"],
            [["原理 Principles", "20", "公式正确、说明物理意义 / correct formulas with physical meaning"],
             ["数据 Data", "25", "数据完整、单位与有效数字规范 / complete data, correct units and significant figures"],
             ["分析 Analysis", "25", "理论与测量比较、误差来源分析 / theory vs measurement, sources of error"],
             ["实际问题 Real problem", "20", "五步完整，假设清楚，指出模型局限 / all five steps, clear assumptions, limits named"],
             ["规范 Presentation", "10", "书写清楚、图表规范、AI 使用如实声明 / clear writing and graphs, honest AI statement"]],
            widths=[4.0, 2.2, 9.8], font_size=9.5)
    d.en("AI 按本量规给出评分建议，教师复核后发布。  AI suggests a score against this rubric; the teacher reviews it before release.", size=9)
    name = f"实验{lab['no']} 实验报告模板.docx" if lab else "虚拟实验报告 通用模板.docx"
    d.save(REPORTS / name)


for lab in LABS:
    guide(lab)
    report(lab)
report(None)
print("guides and report templates written")
