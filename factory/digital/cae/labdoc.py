# -*- coding: utf-8 -*-
"""实验 8 的 Word 文件（第 11 轮 F8）：指导书（由仓库里的 Markdown 转成 Word）和实验报告模板。"""
import io
import os
import re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDE_MD = os.path.join(HERE, "实验8_输出轴强度与疲劳校核.md")
GUIDES = {"lab8": GUIDE_MD, "lab9": os.path.join(HERE, "实验9_机械臂关节力矩与电机选型.md"),
          "lab10": os.path.join(HERE, "实验10_输出轴数控车削与键槽铣削编程.md")}


def _doc():
    from docx import Document
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt
    d = Document()
    st = d.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    for name in ("Title", "Heading 1", "Heading 2", "Heading 3"):
        d.styles[name].element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), "黑体")
    for sec in d.sections:
        sec.left_margin = sec.right_margin = Cm(2.2)
    return d


def _runs(p, text):
    """**粗体** 和 `代码` 两种行内格式"""
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if not part:
            continue
        if part.startswith("**"):
            p.add_run(part[2:-2]).bold = True
        elif part.startswith("`"):
            p.add_run(part[1:-1]).font.name = "Consolas"
        else:
            p.add_run(part)


def md_to_docx(md):
    """够用的 Markdown → Word：标题、段落、列表、表格、粗体"""
    d = _doc()
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln:
            i += 1
            continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            t = d.add_table(rows=len(rows), cols=max(len(r) for r in rows))
            t.style = "Table Grid"
            for r, row in enumerate(rows):
                for c, v in enumerate(row):
                    cell = t.cell(r, c)
                    cell.text = ""
                    _runs(cell.paragraphs[0], v)
                    if r == 0:
                        for run in cell.paragraphs[0].runs:
                            run.bold = True
            d.add_paragraph()
            continue
        m = re.match(r"(#{1,4})\s+(.*)", ln)
        if m:
            level = len(m.group(1))
            d.add_heading(m.group(2), 0 if level == 1 else level - 1)
        elif re.match(r"\s*\d+\.\s", ln):
            _runs(d.add_paragraph(style="List Number"), re.sub(r"^\s*\d+\.\s", "", ln))
        elif re.match(r"\s*[-*]\s", ln):
            _runs(d.add_paragraph(style="List Bullet 2" if ln.startswith("   ") else "List Bullet"), re.sub(r"^\s*[-*]\s", "", ln))
        else:
            _runs(d.add_paragraph(), ln.strip())
        i += 1
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


def guide_docx(lab="lab8"):
    return md_to_docx(open(GUIDES[lab], encoding="utf-8").read())


def report_template_docx(lab="lab8"):
    if lab == "lab9":
        return lab9_template()
    if lab == "lab10":
        return lab10_template()
    from docx.shared import Pt
    d = _doc()
    d.add_heading("实验 8　输出轴强度与疲劳校核　实验报告", 0)

    def table(rows, head=True):
        t = d.add_table(rows=len(rows), cols=len(rows[0]))
        t.style = "Table Grid"
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                t.cell(r, c).text = v
                if head and r == 0:
                    for run in t.cell(r, c).paragraphs[0].runs:
                        run.bold = True
        d.add_paragraph()

    def hint(text):
        p = d.add_paragraph(text)
        p.runs[0].italic = True
        p.runs[0].font.size = Pt(9)

    table([["班级", "", "组号", ""], ["姓名 / 学号", "", "日期", ""]], head=False)
    d.add_heading("一、实验目的", 1)
    hint("（用自己的话写 3–5 条）")
    for _ in range(3):
        d.add_paragraph("", style="List Number")

    d.add_heading("二、计算模型", 1)
    table([["项目", "设置", "理由"],
           ["零件与版本", "SH-301 rev __", ""],
           ["材料", "", ""],
           ["约束 1", "面 __：", ""],
           ["约束 2", "面 __：", ""],
           ["约束 3", "面 __：", ""],
           ["载荷", "面 __：", ""],
           ["网格", "单元尺寸 __ mm，__ 个单元", ""]])
    hint("贴设置截图（模型上的彩色面）。说明：为什么轴承只限制径向、联轴器只限制转动？试“左端面固定”时结果有什么不同？")

    d.add_heading("三、结果与手算核对", 1)
    table([["项目", "网格“中”", "网格“细”", "变化 %"],
           ["最大 Von Mises 应力 / MPa", "", "", ""],
           ["最大应力位置（面）", "", "", ""],
           ["安全系数", "", "", ""],
           ["最大位移 / mm", "", "", ""],
           ["Ø35 光滑段应力（平均）/ MPa", "", "", ""]])
    hint("手算：τ = 16T/(πd³) = ________ MPa；σ = √3·τ = ________ MPa；与有限元误差 ______ %。")
    hint("讨论：网格加密后光滑段与键槽根部的应力为什么变化不同？（应力集中、尖角奇异）")

    d.add_heading("四、疲劳寿命", 1)
    table([["载荷谱", "Miner 规则", "S_D / MPa", "每块循环数", "寿命 / h", "寿命 / 次"],
           ["恒幅 0～350 N·m", "Haibach", "", "", "", ""],
           ["恒幅 0～350 N·m", "原始（低于 S_D 不损伤）", "", "", "", ""],
           ["跑合试验台记录 ______", "Haibach", "", "", "", ""],
           ["跑合试验台记录 ______", "原始", "", "", "", ""]])
    hint("手算核对一个循环：σa = ____，σm = ____，σa,eq = σa/(1 − σm/σb) = ____ MPa；N = N_D·(S_D/σa,eq)^k = ____ 次；平台给出 ____ 次。")
    hint("讨论：损伤主要来自曲线的哪一段？两种 Miner 规则哪个偏安全，为什么？")

    d.add_heading("五、改进方案对比", 1)
    table([["方案", "改动", "安全系数", "疲劳寿命 / h", "下料重量 / kg", "评价（成本、加工）"],
           ["原设计", "45 钢，Ø40", "", "", "", ""],
           ["方案 A", "换 40Cr", "", "", "", ""],
           ["方案 B", "键槽轴段 Ø44", "", "", "", ""]])
    hint("AI 解释哪里说得对、哪里需要补充？你推荐哪个方案，理由是什么？")

    d.add_heading("六、结论", 1)
    d.add_paragraph("")
    d.add_heading("七、附件", 1)
    d.add_paragraph("平台生成的计算报告（Word）。", style="List Bullet")
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


def lab9_template():
    from docx.shared import Pt
    d = _doc()
    d.add_heading("实验 9　机械臂关节力矩与电机选型　实验报告", 0)

    def table(rows, head=True):
        t = d.add_table(rows=len(rows), cols=len(rows[0]))
        t.style = "Table Grid"
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                t.cell(r, c).text = v
                if head and r == 0:
                    for run in t.cell(r, c).paragraphs[0].runs:
                        run.bold = True
        d.add_paragraph()

    def hint(text):
        p = d.add_paragraph(text)
        p.runs[0].italic = True
        p.runs[0].font.size = Pt(9)

    table([["班级", "", "组号", ""], ["姓名 / 学号", "", "日期", ""]], head=False)
    d.add_heading("一、静态重力矩（任务 1）", 1)
    table([["关节", "平台 3 kg / N·m", "平台 5 kg / N·m", "手算 3 kg / N·m", "误差 %"],
           ["J2 大臂", "", "", "", ""], ["J3 小臂", "", "", "", ""], ["J4 腕 1", "", "", "", ""]])
    hint("手算过程：J2 之后各构件的质量、质心到 J2 轴线的水平距离，τ = Σ m·g·r = …")
    d.add_heading("二、搬运结果（任务 2、3）", 1)
    table([["方案", "J1 峰值 N·m", "J2 峰值 N·m", "J1 峰值功率 W", "J2 平均功率 W", "峰值时刻 s"],
           ["1.2 秒，加速段 25%", "", "", "", "", ""],
           ["1.8 秒（放长 1.5 倍）", "", "", "", "", ""],
           ["1.2 秒，加速段 40%", "", "", "", "", ""]])
    hint("贴驱动力矩、速度曲线。说明峰值出现在梯形速度的哪一段；J2 平均功率为负的原因；重力部分与惯性部分各占多少。")
    d.add_heading("三、电机选型（任务 4）", 1)
    table([["关节", "峰值 N·m", "均方根 N·m", "最高 r/min", "推荐（安全系数 1.2）", "最紧的一项", "安全系数 1.5 时"]] +
          [[j, "", "", "", "", "", ""] for j in ("J1", "J2", "J3", "J4", "J5", "J6")])
    hint("手算核对 J2：电机侧均方根力矩 τ_rms/(i·η) = ____ N·m（额定 ____）；电机转速 ω_max·i = ____ r/min（上限 ____）。")
    d.add_heading("四、曲柄滑块（任务 5）", 1)
    table([["项目", "600 r/min", "60 r/min"], ["驱动力矩峰值 N·m", "", ""], ["θ = 90° 时平台值 N·m", "", ""],
           ["θ = 90° 时虚功原理手算 N·m", "", ""], ["连杆最大受力 N", "", ""], ["连杆安全系数", "", ""], ["连杆疲劳寿命", "", ""]])
    d.add_heading("五、结论与讨论", 1)
    d.add_paragraph("")
    d.add_heading("六、附件", 1)
    d.add_paragraph("平台生成的动力学报告、有限元报告（Word）。", style="List Bullet")
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()


def lab10_template():
    from docx.shared import Pt
    d = _doc()
    d.add_heading("实验 10　输出轴数控车削与键槽铣削编程　实验报告", 0)

    def table(rows, head=True):
        t = d.add_table(rows=len(rows), cols=len(rows[0]))
        t.style = "Table Grid"
        for r, row in enumerate(rows):
            for c, v in enumerate(row):
                t.cell(r, c).text = v
                if head and r == 0:
                    for run in t.cell(r, c).paragraphs[0].runs:
                        run.bold = True
        d.add_paragraph()

    def hint(text):
        p = d.add_paragraph(text)
        p.runs[0].italic = True
        p.runs[0].font.size = Pt(9)

    table([["班级", "", "组号", ""], ["姓名 / 学号", "", "日期", ""]], head=False)
    d.add_heading("一、粗车编程单（任务 1）", 1)
    table([["部位", "图纸尺寸", "粗车工序尺寸", "编程直径（平台）", "编程直径（手算）", "说明"],
           ["轴承位", "Ø35 k6", "Ø36.5 0/−0.25", "", "", ""], ["齿轮位", "Ø40 k6", "Ø41.5 0/−0.25", "", "", ""],
           ["轴伸", "Ø30", "（未列）", "", "", "其余直径加的余量 ="]])
    table([["项目", "平台", "手算"], ["端面余量（每端）mm", "", ""], ["车端面刀数", "", ""], ["Ø50 处转速 r/min", "", ""],
           ["Ø31.09 处转速 r/min", "", ""], ["G50 限速什么时候起作用", "", ""]])
    hint("说明为什么编程直径取公差带中间；为什么一道粗车工序要两次装夹、两个程序。")
    d.add_heading("二、程序读懂（任务 1、3、4）", 1)
    table([["程序段（行号）", "在干什么", "关键指令和参数"], ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""], ["", "", ""]])
    hint("至少说明：安全行、换刀与主轴（G50、G96）、分层粗车、沿轮廓去台阶、精车轮廓、键槽斜线下刀、程序结尾。")
    d.add_heading("三、试切检查（任务 2）", 1)
    table([["项目", "O1201 右端", "O1202 左端", "合计"], ["仿真与本工序尺寸的差 mm", "", "", ""], ["切削时间", "", "", ""],
           ["快移时间", "", "", ""], ["换刀时间", "", "", ""], ["程序合计", "", "", ""]])
    table([["对比", "分钟"], ["程序合计", ""], ["基本时间公式 t_b = L·i/(n·f)", ""], ["工艺规程工时", "18"], ["差值主要来自", ""]])
    table([["功率", "ap 2.5、f 0.3", "ap 6、f 0.5"], ["F_c = k_c1.1·a_p·f^(1−m_c)  N", "", ""], ["P_c = F_c·v_c/60000  kW", "", ""],
           ["P_c / 0.8  kW（机床 11 kW）", "", ""], ["平台检查结果", "", ""]])
    d.add_heading("四、精车与一句话编程（任务 3）", 1)
    table([["项目", "结果"], ["精车毛坯从哪来", ""], ["精车编程直径", ""], ["仿真差 mm", ""], ["一句话：AI 改了哪几项", ""],
           ["多留 0.3 后粗车目标直径", ""], ["提交审批时的提示", ""]])
    d.add_heading("五、铣键槽（任务 4）", 1)
    table([["项目", "平台", "手算"], ["槽深 mm", "", ""], ["主轴转速 S r/min", "", ""], ["进给 F mm/min", "", ""],
           ["加工时间（默认参数）", "", "—"], ["加工时间（分 4 层、fz 0.04）", "", "—"], ["工艺规程工时", "10 分", "—"]])
    hint("哪组参数更合理？为什么键槽在磨削前铣、却按磨削后的尺寸 d − t₁ 控制？斜线下刀的好处？")
    d.add_heading("六、下发（任务 5）", 1)
    table([["项目", "记录"], ["提交号 / 工艺规程版本", ""], ["AI 评审意见与处理", ""], ["批准人", ""], ["下发的程序号", ""],
           ["ERPNext 附件 / 3D 回放 / 派工指令（贴图）", ""]])
    d.add_heading("七、结论与讨论", 1)
    d.add_paragraph("")
    d.add_heading("八、附件", 1)
    d.add_paragraph("平台生成的程序（.nc）、截图。", style="List Bullet")
    buf = io.BytesIO()
    d.save(buf)
    return buf.getvalue()
