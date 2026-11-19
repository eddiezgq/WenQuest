# -*- coding: utf-8 -*-
"""问渠 CAD 的网页版帮助 = 培训课程（wenquest-cad 仓库《细则-帮助与培训》，21 课；先做第 1、3、4 课样课）。

  python3 docs/帮助/问渠CAD帮助/build.py          （要 pip install markdown）

生成：apps/web/src/static/help/wqcad/index.html（学习平台 /static/help/wqcad/，国内同步）；
     录屏、封面、字幕在 apps/web/src/static/help/wqcad/media/（tools/video/fcrec/make_all.sh 录的，真软件操作）。

文中零件的数一律取自 WQ-LS 整机的真零件（parts.json，由 tools/video/fcrec/part_data.py 从 STEP 量出来），写成 {{键}}，不手写。
"""
from __future__ import annotations

import json
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
    ("一 入门", 2, "文件与数据：新建、保存、撤销；导入导出 STEP / STL / DXF；对象和依赖关系", "导出一个零件给别人", None),
    ("二 草图", 3, "草图入门：直线、圆、圆弧、矩形、多段线；构造线", "压脚杆套环；针夹轮廓", "l03"),
    ("二 草图", 4, "约束：几何约束、尺寸约束、完全约束、过约束怎么查", "针夹（完全约束）", "l04"),
    ("二 草图", 5, "草图技巧：镜像、阵列、修剪延伸、外部几何、表达式；电子表格驱动尺寸", "曲柄轮廓（表格驱动）", None),
    ("三 零件建模", 6, "凸台、凹槽、旋转、挖槽旋转、孔（螺纹孔）", "针杆、曲柄销", None),
    ("三 零件建模", 7, "倒角、圆角、拔模、抽壳、加厚", "曲柄（带平衡块）", None),
    ("三 零件建模", 8, "扫掠、放样、螺旋", "拉簧、面线导线钩", None),
    ("三 零件建模", 9, "阵列、镜像、多重变换", "手轮（辐条阵列）", None),
    ("三 零件建模", 10, "基准面、基准轴、附着方式；参数化设计", "挑线杆（改一个全跟着变）", None),
    ("三 零件建模", 11, "Part 工作台：基本体、布尔运算、偏移、截面", "送布偏心轮", None),
    ("四 曲线与曲面", 12, "曲线：B 样条、螺旋线、投影、相交线", "机壳外形的特征曲线", None),
    ("四 曲线与曲面", 13, "曲面：填充、扫掠、放样、延伸、修剪；连续性 G0/G1/G2", "机头的过渡曲面", None),
    ("四 曲线与曲面", 14, "曲面到实体：缝合、成实体、加厚；检查几何", "一块外壳变实体", None),
    ("五 装配", 15, "装配工作台：插入零件、固定、关节、自由度", "曲柄滑块", None),
    ("五 装配", 16, "运动与检查：驱动关节、测距离、干涉、爆炸视图", "挑线四连杆转一圈", None),
    ("六 工程图", 17, "TechDraw：图框、投影、剖视、局部放大、尺寸", "针杆零件图", None),
    ("六 工程图", 18, "公差与技术要求、物料清单、导出 PDF / DXF", "挑线机构装配图", None),
    ("七 进阶", 19, "有限元（FEM + CalculiX）", "曲柄 5000 r/min 下的应力", None),
    ("七 进阶", 20, "问渠 CAD 的不同：27 个补丁修了什么", "补丁前后对比", None),
    ("八 AI", 21, "AI 工作台：零件选型与校验、企业零件库、AI 设计零件", "选一个轴承；上轴设计回放", None),
]

EDITION = dict(title="问渠 CAD · 帮助与培训课程", short="帮助与培训课程（样课：第 1、3、4 课）",
               other=("软件下载与安装", "https://wenquestrobotics.com/download/#tut-cad"),
               files=["00-course", "l01", "l03", "l04", "appA-install"])


def numbers():
    P = json.loads((HERE / "parts.json").read_text(encoding="utf-8"))
    pc, nc = P["presser_collar"], P["needle_clamp"]
    rows = []
    for mod, n, what, make, sec in LESSONS:
        link = f'<a href="#{sec}">第 {n} 课</a>' if sec else f"第 {n} 课"
        state = "样课" if sec else "制作中"
        rows.append(f"<tr><td>{mod}</td><td>{link}</td><td>{what}</td><td>{make}</td><td>{state}</td></tr>")
    return {
        "pc": {"od": f"{pc['od']:g}", "id": f"{pc['id']:g}", "t": f"{pc['t']:g}", "v": f"{pc['volume']:.1f}"},
        "nc": {"R": f"{nc['R']:g}", "d": f"{nc['R'] * 2:g}", "bore": f"{nc['bore']:g}", "w": f"{nc['tab_w']:g}", "dep": f"{nc['tab_d']:g}",
               "t": f"{nc['t']:g}", "v": f"{nc['volume']:.1f}"},
        "table": "<table class=\"plan\"><thead><tr><th>模块</th><th>课</th><th>内容</th><th>做出什么（WQ-LS 零件）</th><th>状态</th></tr></thead><tbody>"
                 + "".join(rows) + "</tbody></table>",
    }


def anim_data():
    P = json.loads((HERE / "parts.json").read_text(encoding="utf-8"))
    return {"parts": P, "three": "media/three.min.js"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "media").mkdir(exist_ok=True)
    shutil.copy2(THREE, OUT / "media" / "three.min.js")
    HG.build(HERE, BRAND, EDITION, "web", numbers(), anim_data(), OUT, "media/", lambda a, ed: "#",
             (HERE / "anim.js").read_text(encoding="utf-8"))
    print("wqcad help", (OUT / "index.html").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
