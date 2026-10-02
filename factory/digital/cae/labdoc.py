# -*- coding: utf-8 -*-
"""实验 8 的 Word 文件（第 11 轮 F8）：指导书（由仓库里的 Markdown 转成 Word）和实验报告模板。"""
import io
import os
import re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDE_MD = os.path.join(HERE, "实验8_输出轴强度与疲劳校核.md")


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


def guide_docx():
    return md_to_docx(open(GUIDE_MD, encoding="utf-8").read())


def report_template_docx():
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
