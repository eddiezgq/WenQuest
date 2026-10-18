# -*- coding: utf-8 -*-
"""出件（第 39 轮）：设计计算书（Word）、调机卡（Word）、零件参数表（Excel）。只在网关里用（要 python-docx、openpyxl、matplotlib）。"""
import io
import math
from datetime import date

from .design import CHOICES, CHAIN, GROUPS, adjust_card, analyze

STATE = {"ok": ("合格", "Pass", "2E9E6A"), "warn": ("注意", "Check", "E8913A"), "bad": ("不合格", "Fail", "C0392B")}
FONT = "Noto Sans CJK SC"


def _t(zh, en, lang):
    return en if lang == "en" else zh


def _choice(k, v, lang):
    for c in CHOICES.get(k, []):
        if c[0] == v:
            return c[2] if lang == "en" else c[1]
    return v


def _fmt(v):
    if isinstance(v, float):
        return f"{v:g}" if abs(v) >= 1e-3 or v == 0 else f"{v:.4f}"
    return str(v)


# ---------- 图 ----------
def _mpl_cjk():
    """matplotlib 不一定认 .ttc 里的中文字体：按 fc-match 找到文件后手动登记"""
    import subprocess
    from matplotlib import font_manager
    try:
        path = subprocess.run(["fc-match", "-f", "%{file}", FONT + ":style=Regular"], capture_output=True, text=True, timeout=5).stdout.strip()
        if path:
            font_manager.fontManager.addfont(path)
            return font_manager.FontProperties(fname=path).get_name()
    except Exception:
        pass
    return FONT


def figures(R, lang="zh"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = [_mpl_cjk(), "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    C = R["curves"]
    phi = C["phi"]
    out = []

    def save(fig, title):
        b = io.BytesIO()
        fig.tight_layout()
        fig.savefig(b, format="png", dpi=150)
        plt.close(fig)
        out.append((title, b.getvalue()))

    # 1 针杆运动
    fig, axs = plt.subplots(3, 1, figsize=(7, 6), sharex=True)
    axs[0].plot(phi, C["needle_tip"], color="#2d6fb3")
    axs[0].axhline(0, color="#8a9aa8", lw=0.8)
    axs[0].set_ylabel(_t("针尖高出针板 mm", "Needle tip above plate, mm", lang))
    axs[1].plot(phi, C["needle_v"], color="#e8913a")
    axs[1].set_ylabel(_t("速度 m/s", "Velocity, m/s", lang))
    axs[2].plot(phi, C["needle_a"], color="#c0392b")
    axs[2].set_ylabel(_t("加速度 m/s²", "Acceleration, m/s²", lang))
    axs[2].set_xlabel(_t("主轴转角 °", "Main-shaft angle, °", lang))
    for a in axs:
        a.grid(alpha=0.3)
        a.set_xlim(0, 360)
    save(fig, _t("图 1 针杆位移、速度、加速度", "Fig. 1 Needle-bar displacement, velocity, acceleration", lang))
    # 2 供线与耗线
    if C["takeup_S"]:
        fig, ax = plt.subplots(figsize=(7, 3.4))
        ax.plot(phi, C["takeup_S"], label=_t("挑线杆供线量 S", "Take-up supply S", lang), color="#2d6fb3")
        ax.plot(phi, C["takeup_D"], label=_t("耗线量 D", "Thread demand D", lang), color="#c0392b")
        ax.set_xlabel(_t("主轴转角 °", "Main-shaft angle, °", lang))
        ax.set_ylabel("mm")
        ax.set_xlim(0, 360)
        ax.grid(alpha=0.3)
        ax.legend()
        save(fig, _t("图 2 挑线机构供线量与耗线量", "Fig. 2 Take-up supply and thread demand", lang))
    # 3 送布牙轨迹
    fig, ax = plt.subplots(figsize=(5, 3.4))
    ax.plot(C["feed_x"] + C["feed_x"][:1], C["feed_y"] + C["feed_y"][:1], color="#2e9e6a")
    ax.axhline(0, color="#8a9aa8", lw=0.8)
    ax.set_xlabel(_t("水平 mm", "Horizontal, mm", lang))
    ax.set_ylabel(_t("高出针板 mm", "Above plate, mm", lang))
    ax.grid(alpha=0.3)
    save(fig, _t("图 3 送布牙齿尖轨迹", "Fig. 3 Feed-dog tooth path", lang))
    # 4 时序图
    fig, ax = plt.subplots(figsize=(7, 2.8))
    rows = R["timing"]
    for i, t in enumerate(rows):
        a, b = t["a"], t["b"]
        segs = [(a, b - a)] if b >= a else [(a, 360 - a), (0, b)]
        if a == b:
            segs = [(a - 1, 2)]
        ax.broken_barh(segs, (i - 0.35, 0.7), color=["#2d6fb3", "#7d5ba6", "#c0392b", "#2e9e6a", "#e8913a"][i % 5])
        if "mark" in t:
            ax.plot([t["mark"]] * 2, [i - 0.45, i + 0.45], color="k", lw=1.2)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([t["en" if lang == "en" else "zh"] for t in rows], fontsize=8)
    ax.set_xlim(0, 360)
    ax.set_xticks(range(0, 361, 30))
    ax.grid(axis="x", alpha=0.3)
    ax.set_xlabel(_t("主轴转角 °", "Main-shaft angle, °", lang))
    save(fig, _t("图 4 全机运动时序", "Fig. 4 Machine timing diagram", lang))
    # 5 整机惯性力
    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(phi, C["force"], color="#7d5ba6")
    ax.axhline(550, color="#c0392b", lw=0.8, ls="--")
    ax.set_xlim(0, 360)
    ax.grid(alpha=0.3)
    ax.set_xlabel(_t("主轴转角 °", "Main-shaft angle, °", lang))
    ax.set_ylabel(_t("合力 N", "Resultant, N", lang))
    save(fig, _t("图 5 作用在机壳上的惯性合力", "Fig. 5 Resultant inertia force on the frame", lang))
    return out


# ---------- Word ----------
def _doc():
    from docx import Document
    from docx.oxml.ns import qn
    from docx.shared import Pt
    d = Document()
    st = d.styles["Normal"]
    st.font.name = FONT
    st.font.size = Pt(10.5)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    return d


def _shade(cell, hexcolor):
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), hexcolor)
    tcPr.append(sh)


def _table(d, head, rows, widths=None):
    t = d.add_table(rows=1, cols=len(head))
    t.style = "Table Grid"
    for i, h in enumerate(head):
        t.rows[0].cells[i].text = h
        _shade(t.rows[0].cells[i], "EAF2FA")
    for r in rows:
        cells = t.add_row().cells
        for i, v in enumerate(r):
            cells[i].text = _fmt(v)
    return t


def calc_report(params=None, lang="zh", project="", company=""):
    from docx.shared import Cm, RGBColor
    R = analyze(params)
    p, K = R["params"], R["key"]
    d = _doc()
    d.add_heading(_t("平缝机设计计算书", "Lockstitch Machine Design Calculation", lang), 0)
    d.add_paragraph(_t(f"项目：{project or '未命名'}　　单位：{company or '—'}　　日期：{date.today().isoformat()}　　计算核心版本：{R['version']}",
                       f"Project: {project or 'Untitled'}    Company: {company or '—'}    Date: {date.today().isoformat()}    Core version: {R['version']}", lang))
    d.add_paragraph(_t("本计算书由问渠缝纫机设计软件生成。模型与判据见教材《缝纫机设计与制造》第 3–8 讲与第 23 讲；"
                       "线环、送布、张力等为教材中的示意模型，结论用于设计比较和调机，不代替样机试验。",
                       "Generated by the WenQuest sewing-machine design software. Models and criteria follow the textbook "
                       "Sewing Machine Design and Manufacturing, lectures 3–8 and 23; loop, feed and tension models are the textbook's "
                       "schematic models — use the results to compare designs and to set up the machine, not in place of prototype tests.", lang))
    # 结论
    bad = [c for c in R["checks"] if c["state"] == "bad"]
    warn = [c for c in R["checks"] if c["state"] == "warn"]
    d.add_heading(_t("一、结论", "1 Conclusion", lang), 1)
    if not bad and not warn:
        d.add_paragraph(_t(f"全部 {len(R['checks'])} 项校核合格。", f"All {len(R['checks'])} checks pass.", lang))
    else:
        d.add_paragraph(_t(f"{len(R['checks'])} 项校核：不合格 {len(bad)} 项，需注意 {len(warn)} 项。",
                           f"{len(R['checks'])} checks: {len(bad)} fail, {len(warn)} need attention.", lang))
        for c in bad + warn:
            d.add_paragraph(f"{c['name'][lang]}：{c['value'][lang]}（{_t('判据', 'criterion', lang)} {c['limit'][lang]}）{c['advice'][lang]}", style="List Bullet")
    if "trial" in R:
        cn = R["trial"]["counts"]
        d.add_paragraph(_t(f"虚拟试缝 30 针：成缝 {cn['ok']}，跳针 {cn['skip']}，碰针 {cn['hit']}，划线 {cn['cut']}，断线 {cn['break']}。",
                           f"Virtual test seam, 30 stitches: good {cn['ok']}, skipped {cn['skip']}, needle hit {cn['hit']}, split {cn['cut']}, broken {cn['break']}.", lang))
    # 参数
    d.add_heading(_t("二、设计参数", "2 Design parameters", lang), 1)
    rows = []
    for gk, gzh, gen, items in GROUPS:
        for k, zh, en, unit, *_ in items:
            v = p[k]
            rows.append([_t(gzh, gen, lang), _t(zh, en, lang), _choice(k, v, lang) if k in CHOICES else v, unit])
    _table(d, [_t("部分", "Group", lang), _t("参数", "Parameter", lang), _t("取值", "Value", lang), _t("单位", "Unit", lang)], rows)
    # 主要计算结果
    d.add_heading(_t("三、主要计算结果", "3 Main results", lang), 1)
    res = [
        (_t("连杆比 λ = r/l", "Rod ratio λ = r/l", lang), f"{K['lam']:.4f}", ""),
        (_t("针杆行程 2r", "Needle-bar stroke 2r", lang), f"{K['stroke']:.1f}", "mm"),
        (_t("主轴角速度 ω", "Shaft speed ω", lang), f"{K['omega']:.1f}", "rad/s"),
        (_t("针杆最大速度（转角）", "Needle-bar peak velocity (angle)", lang), f"{K['vmax']:.3f}（{K['vmax_at']:.1f}°）", "m/s"),
        (_t("上止点 / 下止点加速度", "Acceleration at TDC / BDC", lang), f"{K['a_tdc']:.0f} / {K['a_bdc']:.0f}", "m/s²"),
        (_t("下止点 / 上止点惯性力", "Inertia force at BDC / TDC", lang), f"{K['F_bdc']:.0f} / {K['F_tdc']:.0f}", "N"),
        (_t("轴套载荷不超限的最高转速", "Top speed within the bushing limit", lang), f"{K['n_max_F']:.0f}", "r/min"),
        (_t("针尖入布 / 出布", "Needle point enters / leaves fabric", lang), f"{K['pin']:.1f} / {K['pout']:.1f}", "°"),
        (_t("机针回升 2 mm 的转角（标准钩线角）", "Angle at 2 mm rise (standard catch)", lang), f"{K['phc0']:.2f}", "°"),
        (_t("实际钩线角 / 回升量", "Actual catch angle / rise", lang), f"{K['fc']:.2f} / {K['rise_fc']:.2f}", "° / mm"),
        (_t("梭尖线速度（旋梭 2 倍速）", "Hook-point speed (hook at 2×)", lang), f"{K['hook_speed']:.2f}", "m/s"),
        (_t("挑线杆最大供线量", "Take-up maximum supply", lang), f"{K['takeup_Smax']:.1f}" if K["takeup_Smax"] is not None else "—", "mm"),
        (_t("挑线最大线加速度", "Peak thread acceleration", lang), f"{K['takeup_acc'] / 1000:.1f}" if K["takeup_acc"] else "—", "km/s²"),
        (_t("送布偏心行程 / 送布效率", "Feed stroke / efficiency", lang), f"{K['feed_S']:.3f} / {K['feed_eff']:.3f}", "mm / —"),
        (_t("整机惯性合力最大值", "Peak resultant inertia force", lang), f"{K['fmax']:.0f}", "N"),
        (_t("机壳振动速度 / 噪声估算", "Frame vibration / noise estimate", lang), f"{K['vib']:.1f} / {K['noise']:.1f}", "mm/s / dB(A)"),
        (_t("二阶共振转速", "2nd-order resonance speed", lang), f"{K['n_res']:.0f}", "r/min"),
    ]
    _table(d, [_t("项目", "Item", lang), _t("数值", "Value", lang), _t("单位", "Unit", lang)], res)
    # 校核
    d.add_heading(_t("四、校核", "4 Checks", lang), 1)
    t = _table(d, [_t("讲次", "Lecture", lang), _t("校核项", "Check", lang), _t("数值", "Value", lang), _t("判据", "Criterion", lang),
                   _t("结论", "Result", lang)],
               [[c["lecture"], c["name"][lang], c["value"][lang], c["limit"][lang], STATE[c["state"]][1 if lang == "en" else 0]] for c in R["checks"]])
    for i, c in enumerate(R["checks"]):
        cell = t.rows[i + 1].cells[4]
        for run in cell.paragraphs[0].runs:
            run.font.color.rgb = RGBColor.from_string(STATE[c["state"]][2])
            run.font.bold = True
    # 图
    d.add_heading(_t("五、运动曲线与时序", "5 Motion curves and timing", lang), 1)
    for title, png in figures(R, lang):
        d.add_picture(io.BytesIO(png), width=Cm(15))
        d.add_paragraph(title)
    # 零件
    d.add_heading(_t("六、零件参数", "6 Part parameters", lang), 1)
    rows = []
    for part in R["parts"]:
        for zh, en, v, unit in part["dims"]:
            rows.append([_t(part["zh"], part["en"], lang), _t(zh, en, lang), v, unit])
    _table(d, [_t("零件", "Part", lang), _t("尺寸", "Dimension", lang), _t("数值", "Value", lang), _t("单位", "Unit", lang)], rows)
    # 制造
    d.add_heading(_t("七、制造：梭尖间隙尺寸链与公差建议", "7 Manufacturing: hook-clearance chain and tolerances", lang), 1)
    CH = R["chain"]
    d.add_paragraph(_t(f"梭尖间隙 0.07 ± 0.03 mm 由八个环决定。极值法 ±{CH['worst']:.3f} mm；统计法 σ = {CH['sigma']:.4f} mm，"
                       f"完全互换装配合格率 {CH['y_int'] * 100:.1f}%。装配时调整旋梭位置吸收四个环后 σ = {CH['sigma_adj']:.4f} mm，"
                       f"合格率 {CH['y_adj'] * 100:.2f}%；用户换针后 σ = {CH['sigma_swap']:.4f} mm，合格率 {CH['y_swap'] * 100:.1f}%。"
                       "建议：机壳与针杆套、旋梭轴孔按下表公差加工，装配时必须调整梭尖间隙，不要靠零件精度保证。",
                       f"The 0.07 ± 0.03 mm hook clearance depends on eight links. Worst case ±{CH['worst']:.3f} mm; statistical σ = {CH['sigma']:.4f} mm, "
                       f"yield with full interchangeability {CH['y_int'] * 100:.1f}%. Adjusting the hook at assembly absorbs four links: σ = {CH['sigma_adj']:.4f} mm, "
                       f"yield {CH['y_adj'] * 100:.2f}%; after a needle change σ = {CH['sigma_swap']:.4f} mm, yield {CH['y_swap'] * 100:.1f}%. "
                       "Recommendation: machine the parts to the tolerances below and always set the clearance at assembly.", lang))
    _table(d, [_t("环", "Link", lang), _t("公差 ±mm", "Tolerance ±mm", lang), _t("装配调整吸收", "Absorbed by adjustment", lang),
               _t("换针时变化", "Changes with needle", lang)],
           [[_t(c[0], c[1], lang), c[2], "✓" if c[3] else "", "✓" if c[4] else ""] for c in CHAIN])
    # 调机
    d.add_heading(_t("八、装配调机顺序", "8 Assembly adjustment sequence", lang), 1)
    for i, s in enumerate(adjust_card(p), 1):
        d.add_paragraph(f"{i}. {_t(s['zh'], s['en'], lang)}：{_t(s['do_zh'], s['do_en'], lang)}")
    b = io.BytesIO()
    d.save(b)
    return b.getvalue()


def card_docx(params=None, lang="zh", project=""):
    from docx.shared import Pt
    R = analyze(params, trial=False)
    p = R["params"]
    d = _doc()
    d.add_heading(_t("平缝机调机卡", "Lockstitch Adjustment Card", lang), 0)
    d.add_paragraph(_t(f"项目：{project or '未命名'}　转速 {p['n']} r/min　针距 {p['s']} mm　面料 {_choice('fab', p['fab'], lang)}　缝线 {_choice('th', p['th'], lang)}　机针 Nm {round(p['d'] * 100)}",
                       f"Project: {project or 'Untitled'}  {p['n']} r/min  stitch {p['s']} mm  {_choice('fab', p['fab'], lang)}  {_choice('th', p['th'], lang)}  needle Nm {round(p['d'] * 100)}", lang))
    t = d.add_table(rows=1, cols=4)
    t.style = "Table Grid"
    for i, h in enumerate([_t("顺序", "Step", lang), _t("项目", "Item", lang), _t("怎么调、调到多少", "How and to what", lang), _t("确认", "Done", lang)]):
        t.rows[0].cells[i].text = h
        _shade(t.rows[0].cells[i], "EAF2FA")
    for i, s in enumerate(adjust_card(p), 1):
        c = t.add_row().cells
        c[0].text, c[1].text, c[2].text, c[3].text = str(i), _t(s["zh"], s["en"], lang), _t(s["do_zh"], s["do_en"], lang), "□"
    d.add_paragraph()
    d.add_paragraph(_t("试缝：用本卡的面料与缝线缝 30 cm，检查跳针、断线、浮线、起皱、针距。有问题按设计软件校核页的提示回到对应步骤。",
                       "Test seam: sew 30 cm with this fabric and thread; check for skips, breaks, loops, pucker and stitch length. "
                       "If anything is wrong, go back to the step named on the software's check page.", lang)).runs[0].font.size = Pt(9.5)
    b = io.BytesIO()
    d.save(b)
    return b.getvalue()


def params_xlsx(params=None, lang="zh", project=""):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    R = analyze(params, trial=False)
    p = R["params"]
    wb = Workbook()
    ws = wb.active
    ws.title = _t("设计参数", "Parameters", lang)
    ws.append([_t("键", "Key", lang), _t("部分", "Group", lang), _t("参数", "Parameter", lang), _t("取值", "Value", lang), _t("单位", "Unit", lang)])
    for gk, gzh, gen, items in GROUPS:
        for k, zh, en, unit, *_ in items:
            ws.append([k, _t(gzh, gen, lang), _t(zh, en, lang), p[k], unit])
    ws2 = wb.create_sheet(_t("零件参数", "Parts", lang))
    ws2.append([_t("零件", "Part", lang), _t("尺寸", "Dimension", lang), _t("数值", "Value", lang), _t("单位", "Unit", lang)])
    for part in R["parts"]:
        for zh, en, v, unit in part["dims"]:
            ws2.append([_t(part["zh"], part["en"], lang), _t(zh, en, lang), v, unit])
    ws3 = wb.create_sheet(_t("校核", "Checks", lang))
    ws3.append([_t("讲次", "Lecture", lang), _t("校核项", "Check", lang), _t("数值", "Value", lang), _t("判据", "Criterion", lang), _t("结论", "Result", lang)])
    for c in R["checks"]:
        ws3.append([c["lecture"], c["name"][lang], c["value"][lang], c["limit"][lang], STATE[c["state"]][1 if lang == "en" else 0]])
        ws3.cell(ws3.max_row, 5).font = Font(bold=True, color=STATE[c["state"]][2])
    ws4 = wb.create_sheet(_t("运动曲线", "Curves", lang))
    C = R["curves"]
    cols = ["phi", "needle_tip", "needle_v", "needle_a", "takeup_S", "takeup_D", "feed_x", "feed_y", "force"]
    ws4.append(cols)
    for i in range(len(C["phi"])):
        ws4.append([C[k][i] if C[k] else None for k in cols])
    for w in (ws, ws2, ws3, ws4):
        for cell in w[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill("solid", fgColor="EAF2FA")
        for col in w.columns:
            w.column_dimensions[col[0].column_letter].width = max(10, min(40, max(len(str(c.value or "")) for c in col) * 1.6))
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()
