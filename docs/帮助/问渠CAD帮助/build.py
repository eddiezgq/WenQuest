# -*- coding: utf-8 -*-
"""问渠 CAD 的网页版帮助 = 培训课程（wenquest-cad 仓库《细则-帮助与培训》，21 课；先做第 1、3、4 课样课）。

  python3 docs/帮助/问渠CAD帮助/build.py          （要 pip install markdown）

生成：apps/web/src/static/help/wqcad/index.html（学习平台 /static/help/wqcad/，国内同步）；
     录屏、封面、字幕在 apps/web/src/static/help/wqcad/media/（tools/video/fcrec/make_all.sh 录的，真软件操作）。

文中零件的数一律取自 WQ-LS 整机的真零件（parts.json，由 tools/video/fcrec/part_data.py 从 STEP 量出来），写成 {{键}}，不手写。
"""
from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "_帮助生成"))
import helpgen as HG  # noqa: E402

OUT = ROOT / "apps/web/src/static/help/wqcad"
THREE = ROOT / "site/vendor/three/r128/three.min.js"
BRAND = "问渠 CAD"

# 课程目录：全部 21 课都列在第 0 节的表里；已经写成的课才有自己的一节
LESSONS = [
    ("一 入门", 1, "认识界面：工作台、模型树、属性、报告视图；鼠标导航；视图、选择；首选项、单位", "打开 WQ-LS 整机，转着看", "l01"),
    ("一 入门", 2, "文件与数据：新建、保存、撤销；导入导出 STEP / STL / DXF；对象和依赖关系", "导出一个零件给别人", "l02"),
    ("二 草图", 3, "草图入门：直线、圆、圆弧、矩形、多段线；构造线", "压脚杆套环；针夹轮廓", "l03"),
    ("二 草图", 4, "约束：几何约束、尺寸约束、完全约束、过约束怎么查", "针夹（完全约束）", "l04"),
    ("二 草图", 5, "草图技巧：镜像、阵列、修剪延伸、外部几何、表达式；电子表格驱动尺寸", "曲柄轮廓（表格驱动）", "l05"),
    ("三 零件建模", 6, "凸台、凹槽、旋转、挖槽旋转、孔（螺纹孔）", "针杆、曲柄销", "l06"),
    ("三 零件建模", 7, "倒角、圆角、拔模、抽壳、加厚", "针杆倒角；梭壳（抽壳）", "l07"),
    ("三 零件建模", 8, "扫掠、放样、螺旋", "压脚簧（螺旋）、挑线簧（扫掠）", "l08"),
    ("三 零件建模", 9, "阵列、镜像、多重变换", "手轮（减重孔、防滑槽）；针杆第二圈油槽", "l09"),
    ("三 零件建模", 10, "基准面、基准轴、附着方式；参数化设计", "针杆接头（改一个全跟着变）", "l10"),
    ("三 零件建模", 11, "Part 工作台：基本体、布尔运算、偏移、截面", "送布偏心轮", "l11"),
    ("四 曲线与曲面", 12, "曲线：B 样条、螺旋线、投影、相交线", "机头外形的特征曲线（照网格逆向）", "l12"),
    ("四 曲线与曲面", 13, "曲面：填充、扫掠、放样、延伸、修剪；连续性 G0/G1/G2", "机头的修剪和过渡曲面", "l13"),
    ("四 曲线与曲面", 14, "曲面到实体：缝合、成实体、加厚；检查几何", "机头外壳抽壳成铸件", "l14"),
    ("五 装配", 15, "装配工作台：插入零件、固定、关节、自由度", "针杆机构（曲柄滑块）", "l15"),
    ("五 装配", 16, "运动与检查：驱动关节、测距离、干涉、爆炸视图", "针杆机构转一圈、量行程", "l16"),
    ("六 工程图", 17, "TechDraw：图框、投影、剖视、局部放大、尺寸", "针杆零件图", "l17"),
    ("六 工程图", 18, "公差与技术要求、物料清单、导出 PDF / DXF", "针杆零件图加公差；针杆机构装配图", "l18"),
    ("七 进阶", 19, "有限元：问渠有限元（FEM 工作台手建分析 + 计算并核查 + 报告）", "针杆曲柄 5000 r/min 下的应力", "l19"),
    ("七 进阶", 20, "问渠 CAD 的不同：28 个补丁修了什么", "官方 FreeCAD 与问渠 CAD 对照", "l20"),
    ("八 AI", 21, "AI 工作台：零件选型与校验、企业零件库、AI 设计零件", "选一个轴承；上轴设计回放", None),
]

# 英文课表（美国版中英双语，11-19 Eddie 定；顺序、录屏同 LESSONS）
LESSONS_EN = [
    ("1 Getting started", "The window: workbenches, model tree, properties, report view; mouse navigation; views and selection; preferences and units", "Open the WQ-LS machine and look around"),
    ("1 Getting started", "Files and data: new, save, undo; import/export STEP / STL / DXF; objects and dependencies", "Export a part for someone else"),
    ("2 Sketching", "Sketching basics: line, circle, arc, rectangle, polyline; construction geometry", "Presser-bar collar; needle-clamp outline"),
    ("2 Sketching", "Constraints: geometric, dimensional, fully constrained, finding over-constraints", "Needle clamp (fully constrained)"),
    ("2 Sketching", "Sketch techniques: mirror, array, trim/extend, external geometry, expressions; spreadsheet-driven sizes", "Crank outline (spreadsheet driven)"),
    ("3 Part modelling", "Pad, pocket, revolve, groove, hole (threaded holes)", "Needle bar, crank pin"),
    ("3 Part modelling", "Chamfer, fillet, draft, thickness", "Needle-bar chamfers; bobbin case (thickness)"),
    ("3 Part modelling", "Sweep, loft, helix", "Presser spring (helix), check spring (sweep)"),
    ("3 Part modelling", "Patterns, mirror, multi-transform", "Handwheel (holes, grip grooves); needle-bar groove"),
    ("3 Part modelling", "Datum planes and axes, attachment; parametric design", "Needle-bar link (change one, all follow)"),
    ("3 Part modelling", "Part workbench: primitives, Booleans, offset, sections", "Feed eccentric"),
    ("4 Curves & surfaces", "Curves: B-splines, helices, projection, intersections", "Characteristic curves of the head (reverse-engineered from the mesh)"),
    ("4 Curves & surfaces", "Surfaces: filling, sweep, loft, extend, trim; G0/G1/G2 continuity", "Trimming and blends on the head"),
    ("4 Curves & surfaces", "Surfaces to solids: sew, make solid, thicken; check geometry", "The head shell hollowed into a casting"),
    ("5 Assembly", "Assembly workbench: insert parts, ground, joints, degrees of freedom", "Needle-bar mechanism (slider-crank)"),
    ("5 Assembly", "Motion and checks: drive joints, measure, interference, exploded views", "Needle-bar mechanism through one turn; stroke"),
    ("6 Drawings", "TechDraw: templates, projections, sections, details, dimensions", "Needle-bar part drawing"),
    ("6 Drawings", "Tolerances and notes, bill of materials, PDF / DXF export", "Tolerances on the needle-bar drawing; needle-bar mechanism assembly drawing"),
    ("7 Advanced", "FEA with WenQuest FEA (hand-built FEM analysis, compute and check, report)", "Needle-bar crank stress at 5000 rpm"),
    ("7 Advanced", "What is different in WenQuest CAD: the 28 patches", "Official FreeCAD versus WenQuest CAD"),
    ("8 AI", "AI workbench: part selection and checks, company parts library, AI part design", "Pick a bearing; replay the upper-shaft design"),
]

FILES = ["00-course", "l01", "l02", "l03", "l04", "l05", "l06", "l07", "l08", "l09", "l10", "l11", "l12", "l13", "l14", "l15", "l16", "l17", "l18", "l19", "l20", "appA-install"]
EDITION = dict(title="问渠 CAD · 帮助与培训课程", short="帮助与培训课程（已上线：第 1–20 课）", other=("English", "en/"), files=FILES)
EDITION_EN = dict(title="WenQuest CAD · Help and training course", short="Help and training course (online: lessons 1–20)",
                  other=("中文", "../"), files=FILES)


def numbers(en=False):
    P = json.loads((HERE / "parts.json").read_text(encoding="utf-8"))
    pc, nc = P["presser_collar"], P["needle_clamp"]
    rows = []
    for (mod, n, what, make, sec), (mod_en, what_en, make_en) in zip(LESSONS, LESSONS_EN):
        if en:
            mod, what, make = mod_en, what_en, make_en
        name = f"Lesson {n}" if en else f"第 {n} 课"
        link = f'<a href="#{sec}">{name}</a>' if sec else name
        state = ("Online" if sec else "In progress") if en else ("已上线" if sec else "制作中")
        rows.append(f"<tr><td>{mod}</td><td>{link}</td><td>{what}</td><td>{make}</td><td>{state}</td></tr>")
    head = ("<th>Module</th><th>Lesson</th><th>Contents</th><th>What you make (WQ-LS part)</th><th>Status</th>" if en else
            "<th>模块</th><th>课</th><th>内容</th><th>做出什么（WQ-LS 零件）</th><th>状态</th>")
    return {
        "pc": {"od": f"{pc['od']:g}", "id": f"{pc['id']:g}", "t": f"{pc['t']:g}", "v": f"{pc['volume']:.1f}"},
        "nc": {"R": f"{nc['R']:g}", "d": f"{nc['R'] * 2:g}", "bore": f"{nc['bore']:g}", "w": f"{nc['tab_w']:g}", "dep": f"{nc['tab_d']:g}",
               "t": f"{nc['t']:g}", "v": f"{nc['volume']:.1f}"},
        "dep": {"v": f"{1000 - math.pi * 9 * 10:.2f}"},
        "cr": {"D": "33", "d": "22", "e": "15.5", "t": "10", "v1": "10710.93", "v2": "11360.1"},   # 录屏里软件算的（director.log：pad 10.0 10710.93；after 18 11360.1）
        "l12": {"dev_side": "1.19", "dev_side_mean": "0.51", "dev_front": "0.32"},   # 描出的轮廓到网格外形的距离（中文版录屏做完第 13 课的草图，程序量的）
        "l13": {"common": "1889045.8", "before": "29.2", "fillet": "1873384.8"} if en else
               {"common": "1902449.3", "before": "35.0", "fillet": "1887664.2"},   # 各自录屏的 director.log（中英描图点得不完全一样）
        "l16": {"stroke": "31.00"},   # 录屏里程序读 101 帧针杆位置算的（director.log：stroke 31.0）
        "l14": {"shell": "281291.4" if en else "282702.7", "mesh": "387738"},   # mesh：head.stl 的体积
        "l11": {"cut": "2638.94", "off": "4561.51"},   # 录屏里算的；整机 feed_ecc.step 也是 2638.94
        "l10": {"pin": "2364.42", "v22": "3070.82", "real": "2295.65"},   # 录屏里算的；real：整机 nb_link.step
        "l9": {"blank": "51845.70", "holes": "47133.31", "done": "46459.55", "real": "46381.01", "diff": "78.54"},   # 录屏里算的；real：整机 handwheel.step
        "l8": {"helix": "1678.82", "pipe": "22.36", "tube": "4971.25", "check_real": "27.37"},   # 录屏里算的；tube、check_real：整机 presser_spring.step、check_spring.step
        "l7": {"shell": "787.08", "real": "1104.77"},   # 录屏里抽壳 0.6 的体积（director.log）；real：整机 bobbin_case.step 杯体
        "nb": {"v": f"{P['needle_bar']['volume']:.2f}"},
        # 第 6 课：录屏里软件算的（director.log：rev 9047.79；groove 9045.34；hole 1926.68）；两圈槽、倒角按同样尺寸算
        "l6": {"v0": "9047.79", "v1": "9045.34", "v2": f"{math.pi * 16 * 180 - 2 * math.pi * (16 - 3.8 ** 2) * 0.5:.2f}",
               "v3": f"{math.pi * 16 * 180 - 2 * math.pi * (16 - 3.8 ** 2) * 0.5 - 2 * 2 * math.pi * (4 - 0.5 / 3) * 0.125:.2f}",
               "pin": "1926.68", "pin_real": "1912.23"},   # pin_real：整机 crank_pin.step 的体积,
        "table": f"<table class=\"plan\"><thead><tr>{head}</tr></thead><tbody>"
                 + "".join(rows) + "</tbody></table>",
    }


def anim_data(prefix="media/"):
    P = json.loads((HERE / "parts.json").read_text(encoding="utf-8"))
    return {"parts": P, "three": prefix + "three.min.js"}


# 国内学习平台只出中文：去掉“English”切换
HIDE_EN_CN = ('<script>if (location.hostname.endsWith("wenquestech.online")) '
              'document.querySelectorAll(".top-other").forEach(a => a.remove());</script>')

# 帮助模板里的中文按钮（英文页换掉）
UI_EN = [('<html lang="zh-CN">', '<html lang="en">'), ("☰ 目录", "☰ Contents"), ("搜索帮助…", "Search help…"),
         ("◐ 深浅色", "◐ Theme"), (">打印<", ">Print<"), ('b.textContent = "复制"', 'b.textContent = "Copy"'),
         ('"已复制"', '"Copied"'), ("/复制$|已复制$/", "/Copy$|Copied$/"),
         ('"✓ 对。" : "✗ 不对。"', '"✓ Correct. " : "✗ Not quite. "'), ("/^[✓✗] [^。]*。/", "/^[✓✗] [^.]*\\. /"),
         ('srclang="zh" label="中文"', 'srclang="en" label="English"')]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "media").mkdir(exist_ok=True)
    shutil.copy2(THREE, OUT / "media" / "three.min.js")
    js = (HERE / "anim.js").read_text(encoding="utf-8")
    HG.build(HERE, BRAND, EDITION, "web", numbers(), anim_data(), OUT, "media/", lambda a, ed: "#", js)
    p = OUT / "index.html"
    p.write_text(p.read_text(encoding="utf-8").replace(">看English<", ">English<").replace("</body>", HIDE_EN_CN + "\n</body>"), encoding="utf-8")
    # 英文页：sections_en/ 的课文 + 英文界面的录屏（-en）+ 英文字幕
    import tempfile
    src_en = Path(tempfile.mkdtemp())
    shutil.copytree(HERE / "sections_en", src_en / "sections")
    try:
        HG.build(src_en, "WenQuest CAD", EDITION_EN, "web", numbers(en=True), anim_data("../media/"), OUT / "en", "../media/",
                 lambda a, ed: "#", js)
    finally:
        shutil.rmtree(src_en)
    p = OUT / "en" / "index.html"
    t = p.read_text(encoding="utf-8").replace(">看中文<", ">中文<")
    for a, b in UI_EN:
        assert a in t, a
        t = t.replace(a, b)
    p.write_text(t, encoding="utf-8")
    print("wqcad help", (OUT / "index.html").stat().st_size // 1024, "KB; en", p.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
