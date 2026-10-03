"""工程任务单（第 11 轮 2.7（3）5a 的格式；第 13 轮做成各书共用的构建功能）。

每张任务单是一个说明文件 ``chNN/task/tsNN_k.yaml``，正文用

    ::: 任务 50.1
    src: ts50_1
    说明: SH-301 输出轴机械加工工艺规程
    :::

引用。构建时检查格式，生成中英对照的 Word：《工程任务单》、《评分量规》，以及（写了“计算书”时）发给学生的
《空白计算书》——由书里的程序建出 CalcSheet，再用 ``docx(blank=True)`` 导出，公式和出处已填、结果留空。

说明文件的字段（中英成对的写成 [中文, English]）：

    编号: TS-50-1
    标题: [..., ...]
    角色: [工艺员, process engineer]
    背景: [..., ...]
    输入: [{名称: [..], 来源: [..]}]                  # 图纸、订单、工厂数据……
    交付物: [{名称: [..], 验收: [..]}]                # 每项要有验收标准
    工位: [CAD, PLM, ERP, MES, QMS]                   # 见提纲第一节第 11 条的工具链标注
    步骤: [[..], [..]]
    评审要点: [[..], [..]]                            # AI 评审员逐条检查的内容
    评分: [{项: [..], 分: 30, 标准: [..]}]            # 合计 100
    学时: 4
    计算书: {程序: code/ts50_1_calc.py, 函数: sheet}  # 可选

交付物每项还可以写（第 11 轮 2.7（5），平台流程用；都不写就是“上传文件”）：
    类型: 文件 | 设计发布 | 分析 | 工艺规程 | 更改单
    格式: [docx, pdf]                                 # 上传文件允许的格式
    必列: [GR-302, 键]                                # 只用于“更改单”：AI 评审员核对必须列出的物料关键词（可写 a|b 表示任一）
    零件: SH-301                                      # 设计发布、工艺规程、分析：对哪个物料
    轴承: [6207]                                      # 可选，设计发布：AI 评审员核对轴承位长度
构建时另存 build/<书>/task/tsNN_k.json（说明文件的内容），学习平台下达任务单时发给数字工厂。
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
GATEWAY = ROOT / "services" / "gateway"
STATIONS = {"CAD", "PLM", "ERP", "MES", "QMS", "FEA", "FAT", "MBD", "CAM", "PY", "THM", "CFD", "CNC", "AM", "SPC"}
STATION_ZH = {"CAD": "三维建模与出图", "PLM": "发布与审批", "ERP": "物料、BOM、工艺路线与成本", "MES": "派工与车间执行",
              "QMS": "检验与质量", "FEA": "有限元分析", "FAT": "疲劳寿命", "MBD": "多体动力学", "CAM": "数控编程",
              "PY": "计算书与实验台", "THM": "热与非线性分析", "CFD": "充型流动", "CNC": "虚拟数控机床", "AM": "增材切片",
              "SPC": "质量统计"}
STATION_EN = {"CAD": "3D modeling and drawings", "PLM": "release and approval", "ERP": "items, BOM, routing and cost",
              "MES": "dispatch and shop floor", "QMS": "inspection and quality", "FEA": "finite element analysis",
              "FAT": "fatigue life", "MBD": "multibody dynamics", "CAM": "NC programming", "PY": "calculation sheets and lab benches",
              "THM": "thermal and nonlinear analysis", "CFD": "mold filling", "CNC": "virtual CNC machine", "AM": "AM slicing",
              "SPC": "quality statistics"}
DELIVERABLE_KINDS = ("文件", "设计发布", "分析", "工艺规程", "更改单")   # 第 11 轮 2.7（5）：交付物在数字工厂里怎样交
FORMATS = ("docx", "pdf", "xlsx", "step", "png", "jpg", "zip", "txt")
REQUIRED = ("编号", "标题", "角色", "背景", "输入", "交付物", "工位", "步骤", "评审要点", "评分", "学时")


def _pair(x) -> bool:
    return isinstance(x, list) and len(x) == 2 and all(isinstance(s, str) and s.strip() for s in x)


def load(path: Path) -> tuple[dict | None, list[str]]:
    """The task data and what is wrong with it (empty list = fine)."""
    if not path.exists():
        return None, [f"没有任务单说明文件 {path.name}（放在本章 task/ 文件夹里）"]
    try:
        t = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        return None, [f"{path.name} 格式错误：{str(e).splitlines()[0]}"]
    n = path.name
    bad = [f"{n} 缺少“{k}”" for k in REQUIRED if t.get(k) in (None, "", [])]
    for k in ("标题", "角色", "背景"):
        if t.get(k) is not None and not _pair(t[k]):
            bad.append(f"{n}“{k}”应为 [中文, English]")
    for k in ("步骤", "评审要点"):
        for x in t.get(k) or []:
            if not _pair(x):
                bad.append(f"{n}“{k}”中每项应为 [中文, English]")
    for x in t.get("输入") or []:
        if not (isinstance(x, dict) and _pair(x.get("名称")) and _pair(x.get("来源"))):
            bad.append(f"{n}“输入”每项要有 名称、来源（中英）")
    for x in t.get("交付物") or []:
        if not (isinstance(x, dict) and _pair(x.get("名称")) and _pair(x.get("验收"))):
            bad.append(f"{n}“交付物”每项要有 名称、验收（中英）")
            continue
        kind = x.get("类型", "文件")           # 平台上怎样交（第 11 轮 2.7（5））；不写就是上传文件
        if kind not in DELIVERABLE_KINDS:
            bad.append(f"{n}“交付物”的类型 {kind} 不对（可用：{'、'.join(DELIVERABLE_KINDS)}）")
        if x.get("格式") is not None and not (isinstance(x["格式"], list) and all(f in FORMATS for f in x["格式"])):
            bad.append(f"{n}“交付物”的格式写成列表，可用：{'、'.join(FORMATS)}")
        if kind in ("设计发布", "工艺规程", "分析") and not (isinstance(x.get("零件"), str) and x["零件"].strip()):
            bad.append(f"{n}“交付物”类型为 {kind} 时要写“零件”（物料编号，如 SH-301）")
        if x.get("必列") is not None and (kind != "更改单" or not (isinstance(x["必列"], list) and all(isinstance(k, str) and k.strip() for k in x["必列"]))):
            bad.append(f"{n}“交付物”的“必列”只用于类型“更改单”，写成关键词列表（如 [GR-302, 键]）")
    for s in t.get("工位") or []:
        if s not in STATIONS:
            bad.append(f"{n}“工位”里的 {s} 不是工具链标注（{'、'.join(sorted(STATIONS))}）")
    total = 0
    for x in t.get("评分") or []:
        if not (isinstance(x, dict) and _pair(x.get("项")) and _pair(x.get("标准")) and isinstance(x.get("分"), (int, float))):
            bad.append(f"{n}“评分”每项要有 项、分、标准（中英）")
            continue
        total += x["分"]
    if t.get("评分") and abs(total - 100) > 1e-9:
        bad.append(f"{n}“评分”合计 {total:g} 分，应为 100 分")
    c = t.get("计算书")
    if c is not None and not (isinstance(c, dict) and c.get("程序") and c.get("函数")):
        bad.append(f"{n}“计算书”要写 程序、函数")
    if isinstance(c, dict) and c.get("程序") and not (path.parent.parent / c["程序"]).exists():
        bad.append(f"{n}“计算书”的程序 {c['程序']} 不存在")
    return t, sorted(set(bad), key=bad.index)


def _docgen():
    if str(GATEWAY) not in sys.path:
        sys.path.insert(0, str(GATEWAY))
    from app.production import docgen
    return docgen


def task_doc(t: dict, out: Path, no: str, where: tuple[str, str]) -> Path:
    """《工程任务单》（中英对照）。"""
    d = _docgen().Doc()
    d.title(f"工程任务单 {t['编号']}  {t['标题'][0]}", f"Engineering Task {t['编号']}  {t['标题'][1]}")
    d.en(f"配套教材：{where[0]}    Textbook: {where[1]}", size=9)
    d.table(["角色 Role", "建议学时 Hours", "经过的工位 Stations"],
            [[f"{t['角色'][0]}  {t['角色'][1]}", str(t["学时"]), "、".join(f"〔{s}〕{STATION_ZH[s]}" for s in t["工位"])]],
            widths=[4.5, 3.0, 9.0], font_size=9.5)
    d.bh("一、背景与要求", "1  Background and requirements")
    d.bp(t["背景"][0], t["背景"][1])
    d.bh("二、输入资料", "2  Inputs")
    d.table(["资料 Input", "来源 Where to find it"], [[f"{x['名称'][0]}\n{x['名称'][1]}", f"{x['来源'][0]}\n{x['来源'][1]}"] for x in t["输入"]],
            widths=[6.5, 10.0], font_size=9.5)
    d.bh("三、交付物与验收标准", "3  Deliverables and acceptance")
    d.table(["交付物 Deliverable", "验收标准 Acceptance"], [[f"{x['名称'][0]}\n{x['名称'][1]}", f"{x['验收'][0]}\n{x['验收'][1]}"] for x in t["交付物"]],
            widths=[6.0, 10.5], font_size=9.5)
    d.bh("四、工作步骤", "4  Procedure")
    d.blist(t["步骤"], numbered=True)
    d.bh("五、提交与评审", "5  Submission and review")
    d.bp("在数字工厂工作台提交交付物后，AI 评审员先按下列要点逐条检查，只提意见、不打分；你逐条处理（修改或说明理由），老师批准后生效。",
         "After you submit in the digital-factory workbench, the AI reviewer checks the points below one by one; it comments but does not "
         "approve or grade. Address every comment (change the work or explain why not); the teacher's approval makes it effective.")
    d.blist(t["评审要点"], numbered=True)
    d.bh("六、评分", "6  Grading")
    d.bp("老师按《评分量规》给分；AI 评审员可以给建议分，供老师参考。", "The teacher grades with the rubric; the AI reviewer may suggest a score.")
    d.table(["评分项 Item", "分值 Points"], [[f"{x['项'][0]}  {x['项'][1]}", f"{x['分']:g}"] for x in t["评分"]], widths=[13.0, 3.5], font_size=9.5)
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save(str(out))
    return out


def rubric_doc(t: dict, out: Path, no: str, where: tuple[str, str]) -> Path:
    """《评分量规》（中英对照）：每项的分值与达到满分的标准，留出得分与评语栏。"""
    d = _docgen().Doc()
    d.title(f"评分量规 {t['编号']}  {t['标题'][0]}", f"Rubric {t['编号']}  {t['标题'][1]}")
    d.en(f"配套教材：{where[0]}    Textbook: {where[1]}", size=9)
    d.table(["评分项 Item", "分值 Pts", "满分标准 Full marks when", "得分 Score", "评语 Comments"],
            [[f"{x['项'][0]}\n{x['项'][1]}", f"{x['分']:g}", f"{x['标准'][0]}\n{x['标准'][1]}", "", ""] for x in t["评分"]]
            + [["合计 Total", "100", "", "", ""]], widths=[3.6, 1.4, 7.0, 1.6, 3.0], font_size=9)
    d.bp("AI 评审员建议分：______    老师：______    日期：______", "AI reviewer's suggested score ______    Teacher ______    Date ______")
    out.parent.mkdir(parents=True, exist_ok=True)
    d.save(str(out))
    return out


def blank_calc(t: dict, chapter_dir: Path, out: Path, conventions: Path) -> Path | None:
    """《空白计算书》：调用任务单指定的程序函数得到 CalcSheet，导出 blank=True 的 Word。"""
    c = t.get("计算书")
    if not c:
        return None
    src = chapter_dir / c["程序"]
    tools = str(Path(__file__).resolve().parent)
    for p in (tools, str(conventions), str(src.parent)):
        if p not in sys.path:
            sys.path.insert(0, p)
    old = os.environ.get("WQ_BOOK_OUT")
    os.environ["WQ_BOOK_OUT"] = str(out.with_suffix(".values.json"))       # the program's out() must not print here
    try:
        spec = importlib.util.spec_from_file_location(f"wqtask_{src.stem}", src)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        cs = getattr(m, c["函数"])()
    finally:
        if old is None:
            os.environ.pop("WQ_BOOK_OUT", None)
        else:
            os.environ["WQ_BOOK_OUT"] = old
        out.with_suffix(".values.json").unlink(missing_ok=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    cs.docx(str(out), blank=True)
    return out
