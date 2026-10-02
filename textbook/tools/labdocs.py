"""实验指导书与实验报告模板（第 7 轮第 4 步补充）。

Each lab ``lab/NAME.js`` has a companion ``lab/NAME.yaml`` (principles, steps, data tables, cautions, extra
questions, all Chinese/English pairs). The title, goal, scenes, sliders, tasks and the first question come from the
lab program itself, so nothing is written twice. Both Word files use the platform's course layout
(services/gateway/app/production/docgen.py and docs.py).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
GATEWAY = ROOT / "services" / "gateway"

REQUIRED = ("原理", "步骤", "数据表", "注意")


def _pair(x) -> bool:
    return isinstance(x, list) and len(x) == 2 and all(isinstance(s, str) and s.strip() for s in x)


def meta(js: Path) -> dict:
    """The lab's data (functions dropped), read by running the program with a stand-in WQ.lab."""
    code = ("const fs=require('fs');let d=null;global.WQ={lab:x=>{d=x}};"
            f"eval(fs.readFileSync({json.dumps(str(js))},'utf8'));process.stdout.write(JSON.stringify(d));")
    r = subprocess.run(["node", "-e", code], capture_output=True, text=True, timeout=30)
    if r.returncode != 0 or not r.stdout:
        raise ValueError(f"读不出实验程序的定义：{(r.stderr or '').strip()[-300:]}")
    return json.loads(r.stdout)


def load(path: Path) -> tuple[dict | None, list[str]]:
    """The guide data and what is wrong with it (empty list = fine)."""
    if not path.exists():
        return None, [f"没有实验说明文件 {path.name}（写原理、步骤、数据表、注意，用来生成实验指导书和报告模板）"]
    try:
        g = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        return None, [f"{path.name} 格式错误：{str(e).splitlines()[0]}"]
    bad = [f"{path.name} 缺少“{k}”" for k in REQUIRED if not g.get(k)]
    for x in g.get("原理") or []:
        if not (_pair(x) or (isinstance(x, dict) and isinstance(x.get("式"), str))):
            bad.append(f"{path.name}“原理”中每项应为 [中文, English] 或 式: 公式")
    for key in ("步骤", "注意", "思考题"):
        for x in g.get(key) or []:
            if not _pair(x):
                bad.append(f"{path.name}“{key}”中每项应为 [中文, English]")
    for t in g.get("数据表") or []:
        if not (isinstance(t, dict) and _pair(t.get("标题")) and t.get("表头") and t.get("行") is not None):
            bad.append(f"{path.name}“数据表”每张表要有 标题（中英）、表头、行")
            continue
        n = len(t["表头"])
        for row in t["行"]:
            if len(row) != n:
                bad.append(f"{path.name}“{t['标题'][0]}”有一行 {len(row)} 格，表头是 {n} 格")
    return g, sorted(set(bad), key=bad.index)


def _docs():
    if str(GATEWAY) not in sys.path:
        sys.path.insert(0, str(GATEWAY))
    from app.production import docs, docgen
    return docs, docgen


def _env_rows(m: dict) -> list[list[str]]:
    rows = []
    for p in m.get("params") or []:
        unit = p.get("unit") or ""
        rows.append([f"{p['name'][0]}  {p['name'][1]}", f"{p['min']} ~ {p['max']} {unit}".strip(), f"{p.get('step', '')} {unit}".strip()])
    return rows


def _table(d, t: dict) -> None:
    d.p(f"{t['标题'][0]}  {t['标题'][1]}", indent=False)
    n = len(t["表头"])
    d.table([str(h) for h in t["表头"]], [[str(c) for c in r] for r in t["行"]], widths=[round(16.0 / n, 2)] * n, font_size=9.5)


def guide(m: dict, g: dict, out: Path, no: str, where: tuple[str, str]) -> Path:
    """《实验指导书》 for lab ``no`` (e.g. "4.3"); ``where`` says where the lab is in the book."""
    docs, docgen = _docs()
    d = docgen.Doc()
    d.title(m["title"][0], m["title"][1])
    d.en(f"配套教材：{where[0]}    Textbook: {where[1]}", size=9)
    d.bh("一、实验目的", "1  Objectives")
    d.bp(m["goal"][0], m["goal"][1])
    d.bh("二、实验原理", "2  Principles")
    for x in g["原理"]:
        if isinstance(x, dict):
            d.eq(x["式"])
        else:
            d.bp(x[0], x[1])
    d.bh("三、实验环境", "3  The virtual lab")
    d.bp(f"打开方式：在问渠“教材”中阅读{where[0]}，点“打开实验”按钮；实验在浏览器中运行，不需要安装软件。",
         "How to open: read the section in WenQuest Textbooks and press “Open lab”; it runs in the browser, nothing to install.")
    for s in m.get("scenes") or []:
        tag = ("机器人场景", "Robot scene") if s.get("robot") else ("生活场景", "Everyday scene")
        d.bp(f"{tag[0]}“{s['name'][0]}”：{s['problem']['text'][0]}", f"{tag[1]} “{s['name'][1]}”: {s['problem']['text'][1]}")
    rows = _env_rows(m)
    if rows:
        d.table(["可调参数 Control", "范围 Range", "步长 Step"], rows, widths=[8.0, 4.5, 3.5], font_size=9.5)
    if m.get("buttons"):
        d.bp("按钮：" + "、".join(b["name"][0] for b in m["buttons"]), "Buttons: " + ", ".join(b["name"][1] for b in m["buttons"]))
    d.bh("四、实验步骤", "4  Procedure")
    d.blist(g["步骤"], numbered=True)
    d.bp("实验页右侧列出以下任务，完成后自动打勾：", "The lab page lists these tasks and ticks them off as you complete them:")
    d.blist([t["text"] for t in m.get("tasks") or []], numbered=True)
    d.bh("五、数据记录", "5  Data record")
    d.bp("以下表格同时出现在实验报告模板中，请在报告里填写。", "The same tables appear in the report template; fill them in there.")
    for t in g["数据表"]:
        _table(d, t)
    d.bh("六、注意事项", "6  Notes")
    d.blist(g["注意"])
    d.bh("七、思考题", "7  Questions")
    d.blist(questions(m, g), numbered=True)
    d.bh("八、与实际问题的联系", "8  Connection to real problems")
    for s in m.get("scenes") or []:
        p = s["problem"]
        d.p(p["title"][0], indent=False).runs[0].bold = True
        d.en(p["title"][1])
        d.bp(p["text"][0], p["text"][1])
    d.bp("请在实验报告“实际问题的建模与求解”一栏中，以机器人问题为对象按五步完成：① 实际问题 ② 建立模型（写出简化假设）③ 求解 ④ 用虚拟实验检验 ⑤ 指出模型在哪里失效、怎样修正。",
         "In the report section “Modelling a real problem”, take the robot problem through five steps: ① the problem ② the model "
         "(state your assumptions) ③ the solution ④ a check with the virtual lab ⑤ where the model fails and how to improve it.")
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save(str(out))
    return out


def questions(m: dict, g: dict) -> list:
    th = m.get("think")
    return ([th] if _pair(th) else []) + list(g.get("思考题") or [])


def report(m: dict, g: dict, out: Path, no: str, where: tuple[str, str]) -> Path:
    """《实验报告模板》: the platform's eight sections, AI statement and rubric, with this lab's tables and questions."""
    docs, docgen = _docs()
    d = docgen.Doc()
    d.title(f"实验报告  {m['title'][0]}", f"Lab Report  {m['title'][1]}")
    d.table(["姓名 Name", "", "学号 ID", "", "日期 Date", ""], [["班级 Class", "", "同组 Partner", "", "成绩 Score", ""]],
            widths=[2.4, 3.2, 2.2, 2.8, 2.2, 3.2], font_size=10)
    d.en(f"配套教材：{where[0]}。填写本模板后在问渠“作业”中上传。  Textbook: {where[1]}. Submit this file in WenQuest Assignments.", size=9)
    robot = next((s for s in m.get("scenes") or [] if s.get("robot")), (m.get("scenes") or [{}])[0])
    for zh, en, n in docs.REPORT_SECTIONS:
        d.bh(zh, en)
        if zh.startswith("四"):
            for t in g["数据表"]:
                _table(d, t)
            d.bp("数据处理：写出计算过程，与理论值比较，至少完成一张图。", "Processing: show your calculations, compare with theory, include at least one graph.")
            d.lines(4)
        elif zh.startswith("六") and robot.get("problem"):
            p = robot["problem"]
            d.p(p["title"][0], indent=False).runs[0].bold = True
            d.bp(p["text"][0], p["text"][1])
            for step, en_step in docs.FIVE:
                d.p(step, indent=False)
                d.en(en_step)
                d.lines(3)
        elif zh.startswith("八"):
            for zq, eq in questions(m, g):
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
            [["原理 Principles", "20", "公式正确、说明其含义 / correct formulas with their meaning"],
             ["数据 Data", "25", "数据完整、单位与有效数字规范 / complete data, correct units and significant figures"],
             ["分析 Analysis", "25", "理论与测量比较、误差来源分析 / theory vs measurement, sources of error"],
             ["实际问题 Real problem", "20", "五步完整，假设清楚，指出模型局限 / all five steps, clear assumptions, limits named"],
             ["规范 Presentation", "10", "书写清楚、图表规范、AI 使用如实声明 / clear writing and graphs, honest AI statement"]],
            widths=[4.0, 2.2, 9.8], font_size=9.5)
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save(str(out))
    return out


# ---------------------------------------------------------------- English edition (第 8 轮 2.2)

import re as _re

_CJK = _re.compile(r"[一-鿿]")


def _en_table(t: dict) -> tuple[list[str], list[list[str]]]:
    head = [str(h) for h in (t.get("表头英文") or t["表头"])]
    rows = [[str(c) for c in r] for r in (t.get("行英文") or t["行"])]
    return head, rows


def english_problems(g: dict) -> list[str]:
    """What the English lab documents would still show in Chinese: table headers and cells need 表头英文 / 行英文."""
    bad = []
    for t in g.get("数据表") or []:
        head, rows = _en_table(t)
        if any(_CJK.search(h) for h in head):
            bad.append(f"“{t['标题'][0]}”的表头有中文：加上 表头英文")
        if any(_CJK.search(c) for r in rows for c in r):
            bad.append(f"“{t['标题'][0]}”的表格内容有中文：加上 行英文")
        if t.get("行英文") and len(t["行英文"]) != len(t["行"]):
            bad.append(f"“{t['标题'][0]}”的 行英文 与 行 的行数不同")
    return bad


def _en_tab(d, t: dict) -> None:
    d.p(t["标题"][1], indent=False)
    head, rows = _en_table(t)
    n = len(head)
    d.table(head, rows, widths=[round(16.0 / n, 2)] * n, font_size=9.5)


def _second(items) -> list[str]:
    return [x[1] if _pair(x) else str(x) for x in items]


def guide_en(m: dict, g: dict, out: Path, no: str, where: str) -> Path:
    """The lab guide in English only, for the English edition."""
    docs, docgen = _docs()
    d = docgen.Doc()
    d.title(m["title"][1])
    d.p(f"Textbook: {where}", indent=False)
    d.h("1  Objectives")
    d.p(m["goal"][1])
    d.h("2  Principles")
    for x in g["原理"]:
        if isinstance(x, dict):
            d.eq(x["式"])
        else:
            d.p(x[1])
    d.h("3  The virtual lab")
    d.p("How to open: read the section in WenQuest Textbooks (English) and press “Open lab”; it runs in the browser, nothing to install.")
    for s in m.get("scenes") or []:
        tag = "Robot scene" if s.get("robot") else "Everyday scene"
        d.p(f"{tag} “{s['name'][1]}”: {s['problem']['text'][1]}")
    rows = [[p["name"][1], f"{p['min']} ~ {p['max']} {p.get('unit') or ''}".strip(), f"{p.get('step', '')} {p.get('unit') or ''}".strip()]
            for p in m.get("params") or []]
    if rows:
        d.table(["Control", "Range", "Step"], rows, widths=[8.0, 4.5, 3.5], font_size=9.5)
    if m.get("buttons"):
        d.p("Buttons: " + ", ".join(b["name"][1] for b in m["buttons"]))
    d.h("4  Procedure")
    d.bullets(_second(g["步骤"]), numbered=True)
    d.p("The lab page lists these tasks and ticks them off as you complete them:")
    d.bullets(_second([t["text"] for t in m.get("tasks") or []]), numbered=True)
    d.h("5  Data record")
    d.p("The same tables appear in the report template; fill them in there.")
    for t in g["数据表"]:
        _en_tab(d, t)
    d.h("6  Notes")
    d.bullets(_second(g["注意"]))
    d.h("7  Questions")
    d.bullets(_second(questions(m, g)), numbered=True)
    d.h("8  Connection to real problems")
    for s in m.get("scenes") or []:
        p = s["problem"]
        d.p(p["title"][1], indent=False).runs[0].bold = True
        d.p(p["text"][1])
    d.p("In the report section “Modelling a real problem”, take the robot problem through five steps: ① the problem ② the model "
        "(state your assumptions) ③ the solution ④ a check with the virtual lab ⑤ where the model fails and how to improve it.")
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save(str(out))
    return out


def report_en(m: dict, g: dict, out: Path, no: str, where: str) -> Path:
    """The lab report template in English only, for the English edition."""
    docs, docgen = _docs()
    d = docgen.Doc()
    d.title(f"Lab Report  {m['title'][1]}")
    d.table(["Name", "", "ID", "", "Date", ""], [["Class", "", "Partner", "", "Score", ""]],
            widths=[2.4, 3.2, 2.2, 2.8, 2.2, 3.2], font_size=10)
    d.p(f"Textbook: {where}. Submit this file in WenQuest Assignments.", indent=False)
    robot = next((s for s in m.get("scenes") or [] if s.get("robot")), (m.get("scenes") or [{}])[0])
    for zh, en, n in docs.REPORT_SECTIONS:
        d.h(en)
        if zh.startswith("四"):
            for t in g["数据表"]:
                _en_tab(d, t)
            d.p("Processing: show your calculations, compare with theory, include at least one graph.")
            d.lines(4)
        elif zh.startswith("六") and robot.get("problem"):
            p = robot["problem"]
            d.p(p["title"][1], indent=False).runs[0].bold = True
            d.p(p["text"][1])
            for _, en_step in docs.FIVE:
                d.p(en_step, indent=False)
                d.lines(3)
        elif zh.startswith("八"):
            for _, eq in questions(m, g):
                d.p(eq, indent=False)
                d.lines(3)
        else:
            d.lines(n)
    d.h("9  AI use statement")
    d.p("□ No AI used   □ AI to explain concepts   □ AI to check calculations   □ Other: ____________", indent=False)
    d.p("If you used AI, say where:", indent=False)
    d.lines(2)
    d.h("Rubric")
    d.table(["Criterion", "Points", "What earns full marks"],
            [["Principles", "20", "correct formulas with their meaning"],
             ["Data", "25", "complete data, correct units and significant figures"],
             ["Analysis", "25", "theory vs measurement, sources of error"],
             ["Real problem", "20", "all five steps, clear assumptions, limits named"],
             ["Presentation", "10", "clear writing and graphs, honest AI statement"]],
            widths=[4.0, 2.2, 9.8], font_size=9.5)
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save(str(out))
    return out
