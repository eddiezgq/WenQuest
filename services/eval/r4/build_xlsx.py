import json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L
from openpyxl.formatting.rule import CellIsRule
import attainment as A

S = A.students; M = json.load(open("mapping.json")); N = len(S)
F = "Arial"; blue = Font(name=F, color="0000FF"); bold = Font(name=F, bold=True); norm = Font(name=F)
green = Font(name=F, color="008000"); yel = PatternFill("solid", fgColor="FFFF00"); head = PatternFill("solid", fgColor="DDEBF7")
wb = Workbook()

ws0 = wb.active; ws0.title = "说明"
for r, t in enumerate([
    "课程目标达成度计算样例 · 大学物理（上）第 1 章 · 模拟班级 40 人（模拟数据）",
    "问渠 第 4 轮 · 本窗口第 1 步。全部结果由公式计算，修改输入后自动更新，可逐格手工复核。",
    "",
    "可以修改的单元格：",
    "  · 黄色单元格：达成阈值、学生个人达成线（在“达成度计算”表顶部）；环节权重（“对应关系”表）",
    "  · 蓝色数字：学生原始得分（“学生得分”表），正式运行时由问渠自动取数",
    "计算方法：",
    "  · 环节得分率 = 环节内各考核项全班平均分之和 ÷ 环节满分",
    "  · 课程目标达成度（直接评价）= Σ 环节权重 × 环节得分率；不低于阈值为“达成”",
    "  · 学生个人达成度 = 该生各环节得分率的加权和；个人达成比例 = 达到个人达成线的学生占比",
    "  · 间接评价 = 学生自评平均分 ÷ 5，与直接评价分开列出，不合成一个数",
    "  · 毕业要求汇总只作示范，由校情中枢完成；其他课程的数值为示例",
    "数据来源：闭卷分数为知识点掌握度按第 3 轮 E10 折算的百分制；实验过程分项（结果 30、方法 35、建模 25、探索 10）；"
    "实验报告 R8 量规（原理 20、数据 25、分析 25、实际问题 20、规范 10）；答辩六项各 10 分；自评 1–5 分。",
], 1):
    ws0.cell(r, 1, t).font = bold if r == 1 else norm
ws0.column_dimensions["A"].width = 120

# 学生得分
ws = wb.create_sheet("学生得分")
cols = list(S[0].keys()); colL = {c: L(i + 1) for i, c in enumerate(cols)}
for j, c in enumerate(cols, 1):
    x = ws.cell(1, j, A.KPS.get(c, c) if c in A.KPS else c); x.font = bold; x.fill = head; x.alignment = Alignment(wrap_text=True)
    ws.cell(2, j, c if c in A.KPS else "").font = Font(name=F, italic=True, size=8)
for i, s in enumerate(S, 3):
    for j, c in enumerate(cols, 1):
        ws.cell(i, j, s[c]).font = norm if c == "学号" else blue
R0, R1 = 3, N + 2
rng = lambda c: f"学生得分!${colL[c]}${R0}:${colL[c]}${R1}"
ws.freeze_panes = "B3"
for j in range(1, len(cols) + 1): ws.column_dimensions[L(j)].width = 11

# 对应关系
wm = wb.create_sheet("对应关系")
hdr = ["课程目标", "课程目标名称", "考核环节", "考核项", "环节满分", "环节权重"]
for j, h in enumerate(hdr, 1): c = wm.cell(1, j, h); c.font = bold; c.fill = head
rows = []; r = 2
for co, spec in M["CO"].items():
    for name, cl, full, w in spec["环节"]:
        wm.cell(r, 1, co); wm.cell(r, 2, spec["名称"]); wm.cell(r, 3, name); wm.cell(r, 4, "、".join(A.KPS.get(c, c) for c in cl))
        wm.cell(r, 5, f"=" + "+".join(str(A.col_full(c)) for c in cl)).font = norm
        x = wm.cell(r, 6, w); x.font = blue; x.fill = yel
        for k in range(1, 5): wm.cell(r, k).font = norm
        rows.append((co, name, cl, r)); r += 1
for k, wdt in zip("ABCDEF", (8, 34, 26, 60, 10, 10)): wm.column_dimensions[k].width = wdt

# 达成度计算
wc = wb.create_sheet("达成度计算")
wc["A1"] = "达成阈值"; wc["B1"] = A.THRESHOLD; wc["A2"] = "学生个人达成线"; wc["B2"] = A.STU_PASS
for a in ("B1", "B2"): wc[a].font = blue; wc[a].fill = yel; wc[a].number_format = "0.00"
for a in ("A1", "A2"): wc[a].font = bold
h = ["课程目标", "考核环节", "环节得分率", "环节权重", "贡献"]
for j, t in enumerate(h, 1): c = wc.cell(4, j, t); c.font = bold; c.fill = head
r = 5; co_rows = {}
for co, name, cl, mr in rows:
    wc.cell(r, 1, co).font = norm; wc.cell(r, 2, name).font = norm
    wc.cell(r, 3, "=(" + "+".join(f"AVERAGE({rng(c)})" for c in cl) + f")/对应关系!E{mr}").number_format = "0.000"
    wc.cell(r, 4, f"=对应关系!F{mr}").font = green
    wc.cell(r, 5, f"=C{r}*D{r}").number_format = "0.000"
    co_rows.setdefault(co, []).append(r); r += 1
r += 1
h2 = ["课程目标", "直接评价达成度", "是否达成", "学生个人达成比例", "间接评价（学生自评）"]
for j, t in enumerate(h2, 1): c = wc.cell(r, j, t); c.font = bold; c.fill = head
r += 1; summary_row = {}
# 学生个人达成度表
wsd = wb.create_sheet("学生达成度")
wsd.cell(1, 1, "学号").font = bold
for k, co in enumerate(M["CO"], 2): c = wsd.cell(1, k, co); c.font = bold; c.fill = head
for i in range(N):
    rr = i + 2; src = i + R0
    wsd.cell(rr, 1, f"=学生得分!A{src}")
    for k, co in enumerate(M["CO"], 2):
        terms = [f"对应关系!$F${mr}*(" + "+".join(f"学生得分!{colL[c]}{src}" for c in cl) + f")/对应关系!$E${mr}"
                 for c0, name, cl, mr in rows if c0 == co]
        wsd.cell(rr, k, "=" + "+".join(terms)).number_format = "0.000"
for k, co in enumerate(M["CO"], 2):
    cr = co_rows[co]
    wc.cell(r, 1, co).font = norm
    wc.cell(r, 2, "=" + "+".join(f"E{x}" for x in cr)).number_format = "0.000"
    wc.cell(r, 3, f'=IF(B{r}>=$B$1,"达成","未达成")')
    wc.cell(r, 4, f"=COUNTIF(学生达成度!{L(k)}2:{L(k)}{N+1},\">=\"&$B$2)/{N}").number_format = "0.0%"
    wc.cell(r, 5, f"=AVERAGE({rng('自评' + co)})/5").number_format = "0.000"
    summary_row[co] = r; r += 1
wc.conditional_formatting.add(f"C{min(summary_row.values())}:C{max(summary_row.values())}",
                              CellIsRule(operator="equal", formula=['"未达成"'], font=Font(name=F, color="C00000", bold=True)))
for k, wdt in zip("ABCDE", (14, 30, 12, 18, 20)): wc.column_dimensions[k].width = wdt

# 考核项得分率（追溯）
wt = wb.create_sheet("考核项得分率")
for j, t in enumerate(["课程目标", "考核环节", "考核项", "满分", "全班平均", "得分率"], 1): c = wt.cell(1, j, t); c.font = bold; c.fill = head
r = 2
for co, name, cl, mr in rows:
    for c in cl:
        wt.cell(r, 1, co); wt.cell(r, 2, name); wt.cell(r, 3, A.KPS.get(c, c)); wt.cell(r, 4, A.col_full(c)).font = blue
        wt.cell(r, 5, f"=AVERAGE({rng(c)})").number_format = "0.00"; wt.cell(r, 6, f"=E{r}/D{r}").number_format = "0.000"; r += 1
wt.conditional_formatting.add(f"F2:F{r-1}", CellIsRule(operator="lessThan", formula=["0.6"], fill=PatternFill("solid", fgColor="F8CBAD")))
wt.cell(r + 1, 1, "红底：得分率低于 0.6，作为追溯和预警的线索。").font = norm
for k, wdt in zip("ABCDEF", (8, 26, 22, 8, 10, 10)): wt.column_dimensions[k].width = wdt

# 毕业要求汇总（示范）
wg = wb.create_sheet("毕业要求汇总_示范")
wg["A1"] = "示范：毕业要求指标点汇总。正式运行由校情中枢完成；“示例”课程的达成度为示例数值，非真实数据。"; wg["A1"].font = bold
for j, t in enumerate(["指标点", "支撑课程", "课程目标", "支撑权重", "课程目标达成度", "加权和法", "最小值法"], 1):
    c = wg.cell(3, j, t); c.font = bold; c.fill = head
r = 4
for gp, sup in M["SUPPORT"].items():
    start = r
    for course, co, w in sup:
        wg.cell(r, 1, gp); wg.cell(r, 2, course); wg.cell(r, 3, co or "")
        x = wg.cell(r, 4, w); x.font = blue; x.fill = yel
        if co: wg.cell(r, 5, f"=达成度计算!B{summary_row[co]}").font = green
        else: x = wg.cell(r, 5, M["OTHER"][course]); x.font = blue
        wg.cell(r, 5).number_format = "0.000"; r += 1
    wg.cell(start, 6, f"=SUMPRODUCT(D{start}:D{r-1},E{start}:E{r-1})").number_format = "0.000"
    wg.cell(start, 7, f"=MIN(E{start}:E{r-1})").number_format = "0.000"
wg.cell(r + 1, 1, "两种汇总方法学校任选其一（待确认）。最小值法更严格：任何一门支撑课程未达成，该指标点即未达成。").font = norm
for k, wdt in zip("ABCDEFG", (26, 22, 10, 10, 14, 10, 10)): wg.column_dimensions[k].width = wdt

for sh in wb.worksheets:
    for row in sh.iter_rows():
        for c in row:
            if c.font is None or c.font.name != F: c.font = Font(name=F, bold=c.font.bold, color=c.font.color, italic=c.font.italic, size=c.font.size)
wb.save("attainment_ch1.xlsx")
print("saved")
