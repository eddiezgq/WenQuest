"""第 138 轮 G5.1 第 9 步：机壳三坐标检测计划，并接数字工厂质量模块（hub/eto_quality：检验计划的格式检查与逐项判定）。

    python3 tools/wqls/g5_cmm.py [<输出目录>]  → 三坐标检测计划.json

每个图纸特性：怎样建坐标系（基准）、测哪个要素、测点数与分布、评价方法（GB/T 1958 / ISO 1101、ISO 5459 公共基准）、
名义值与上下限、首件 / 终检。名义值、公差从工艺规程的 characteristics 读，与图纸一致。
测量不确定度按三坐标 MPE_E = 1.8 + L/300 μm 估，检查公差与不确定度之比（T/U ≥ 4）。
这里只出计划、检查格式；判定函数在没有测量值时给“未知”，不算合格（不编测量数据）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIG = ROOT / "factory" / "digital"
sys.path[:0] = [str(DIG), str(ROOT / "factory")]

ALIGN = {
    "HSG-LS-U": "坐标系 1（与加工基准一致）：接合面 C 扫描 4 条线约 300 点拟合平面（最小区域法）定 Z；工艺孔 1 两层各 12 点拟合圆柱定原点；"
                "工艺孔 2 定 X 轴方向（3-2-1）。坐标系 2（功能基准）：A–B = 前后轴承孔各 3 层 × 16 点拟合圆柱，公共轴线按 ISO 5459（最小区域）。",
    "HSG-LS-L": "坐标系：底面 A 扫描约 250 点拟合平面定 Z；两工艺孔 Ø10 H7（各两层 × 12 点）定原点和 X 轴。",
    "HSG-LS-P": "坐标系：下件底面 A ＋ 两工艺孔（同下件）；上件针杆孔、上轴两孔在这个坐标系里测。",
}

POINTS = {   # 特性号 → (要素与测点, 评价方法, 量程 L mm)
    ("HSG-LS-U", "C1"): ("前轴承孔：3 层（深 2、6.5、11）× 16 点", "最小二乘直径；生产中每件用气动量仪", 35),
    ("HSG-LS-U", "C2"): ("后轴承孔：3 层 × 16 点（长探针，经前孔伸入）", "最小二乘直径；生产中每件用气动量仪", 32),
    ("HSG-LS-U", "C3"): ("两孔各自的拟合轴线", "同轴度：各孔轴线对公共轴线 A–B 的最小区域圆柱直径（ISO 1101）", 345),
    ("HSG-LS-U", "C4"): ("针杆两孔：各 2 层 × 12 点", "最小二乘直径；塞规", 12),
    ("HSG-LS-U", "C5"): ("针杆孔公共轴线（两孔拟合）", "垂直度：轴线对 C 面，按 100 mm 长折算", 150),
    ("HSG-LS-U", "C6"): ("针杆孔公共轴线", "位置度：理论位置在 A–B 上、离前孔中心 37.5，轴线对理论位置的偏离 × 2", 200),
    ("HSG-LS-U", "C7"): ("止口外圆：2 层 × 24 点", "最小二乘直径；外径千分尺", 52),
    ("HSG-LS-U", "C8"): ("止口拟合轴线", "同轴度：对 A–B", 400),
    ("HSG-LS-U", "C9"): ("电机法兰端面：Ø40 圆上 16 点", "垂直度：端面对 A–B", 52),
    ("HSG-LS-U", "C10"): ("接合面 C：4 条线扫描约 300 点", "平面度（最小区域）", 180),
    ("HSG-LS-U", "C11"): ("C 面与 A–B", "距离：A–B 轴线（两孔中点处）到 C 面", 200),
    ("HSG-LS-U", "C12"): ("工艺孔：各 2 层 × 12 点", "直径（塞规）与位置度（对 C 与 A–B）", 75),
    ("HSG-LS-L", "C1"): ("底面 A：扫描约 250 点", "平面度（最小区域）", 520),
    ("HSG-LS-L", "C2"): ("机座顶面：扫描 6 条线约 600 点", "平面度；平行度对 A", 520),
    ("HSG-LS-L", "C3"): ("顶面与 A", "距离：顶面拟合平面到 A（最大、最小值）", 62),
    ("HSG-LS-L", "C4"): ("针板座底面：16 点", "深度（到顶面）、平面度、平行度对 A", 64),
    ("HSG-LS-L", "C5"): ("滑板座底面：9 点", "深度（到顶面）", 46),
    ("HSG-LS-L", "C6"): ("两工艺孔：各 2 层 × 12 点", "直径（塞规）", 10),
    ("HSG-LS-P", "P1"): ("针杆孔公共轴线（上件）与针板座中心（下件，由座的两侧边和 4 个 M3 孔拟合）", "位置：针杆轴线在针板座平面上的穿点到针板孔理论位置的距离", 300),
}


def build():
    plan, rows = [], []
    for item in ("HSG-LS-U", "HSG-LS-L", "HSG-LS-P"):
        p = yaml.safe_load((DIG / "std" / f"{item}_process.yaml").read_text(encoding="utf-8"))
        for c in p["characteristics"]:
            key = (item, c["id"])
            if key not in POINTS:
                continue
            feat, method, L = POINTS[key]
            mpe = (1.8 + L / 300) / 1000                      # mm
            U = 2 * mpe / 3 ** 0.5 * 1.2                      # 扩展不确定度的粗估（k = 2，含温度与探针，取 MPE 的 1.4 倍量级）
            T = (c["es"] - c["ei"]) if "es" in c else None
            code = f"{item.split('-')[-1].lower()}_{c['id'].lower()}"
            row = dict(code=code, name=c["name"], item=item, kind="both" if c.get("key") else "final",
                       nominal=c.get("nominal"), lo=(c["nominal"] + c["ei"]) if "es" in c else None,
                       hi=(c["nominal"] + c["es"]) if "es" in c else None, unit="mm", method=method, feature=feat, spec=c["spec"],
                       U_mm=round(U, 4), T_over_U=round(T / U, 1) if T else None)
            rows.append(row)
            if row["lo"] is not None:
                plan.append({k: row[k] for k in ("code", "name", "item", "kind", "nominal", "lo", "hi", "unit", "method")})
    return rows, plan


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "设计" / "WQ-LS" / "G5"
    from hub import eto_quality as Q
    rows, plan = build()
    errs = Q.check_plan(plan, ["HSG-LS-U", "HSG-LS-L", "HSG-LS-P"], "HSG-LS-P")
    res_unknown = Q.judge(plan, {}, "fai", "HSG-LS-U")[0]
    low = [r for r in rows if r["T_over_U"] is not None and r["T_over_U"] < 4]
    doc = dict(alignment=ALIGN, environment="恒温室 20 ± 1 ℃；工件在室内等温 ≥ 4 h；三坐标 MPE_E = 1.8 + L/300 μm，探针 Ø2 红宝石（后轴承孔用 L = 200 加长杆）",
               characteristics=rows, eto_quality_plan=plan, check_plan_errors=errs, judge_without_readings=res_unknown,
               T_over_U_below_4=[r["code"] for r in low])
    (out / "三坐标检测计划.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    print("检验项", len(rows), "，质量模块格式检查：", errs or "通过", "；没有测量值时判定：", res_unknown)
    for r in rows:
        print(f"  {r['code']:8s} {r['name'][:16]:16s} T/U = {r['T_over_U']}")
    if low:
        print("T/U < 4：", [r["code"] for r in low])


if __name__ == "__main__":
    main()
