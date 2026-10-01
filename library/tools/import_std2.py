# -*- coding: utf-8 -*-
"""第 5 轮第 5 步：A 部分其余 5 个族（P7）——滚珠丝杠、直线导轨、同步带轮、梅花联轴器、压缩弹簧。

尺寸表在 library/std_tables/<族>.yaml（出处、列定义、每行出处键、不收的行与原因），由调研代理两次读取录入、我抽查；
本程序把它们写成条目（entry.yaml）与规格表（specs.csv，每行带出处网址 src_url）。同步带轮的规格按公式由齿形常数生成。
用法：python3 tools/import_std2.py
核对：tests/test_std_tables2.py（公式、单调性、抽查值）。
"""
import math
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from import_bd import mm, write  # noqa: E402
from wqlib import CATALOG, ROOT  # noqa: E402

TABLES = ROOT / "std_tables"
RETRIEVED = "2026-10-01"
LICENSE = "Apache-2.0"
ATTR = "问渠零件库（造型程序与规格表）；尺寸取自所列标准与样本的公开尺寸表"

# 同步带轮：每种齿形收的齿数与带宽（常用段）
PULLEY_Z = {"GT2": [16, 20, 24, 30, 36, 40, 48, 60], "3M": [15, 20, 24, 30, 36, 40, 48, 60, 72],
            "5M": [15, 20, 24, 30, 36, 40, 48, 60, 72]}
PULLEY_B = {"GT2": [6, 9], "3M": [9, 15], "5M": [15, 25]}
GT2_GROOVE = {"groove_depth_mm": 0.75, "groove_r_mm": 0.555}      # GT2 轮槽是 Gates 专有，公开资料不给；造型按近似值（页面注明）


def P(key, zh, en, role, unit=None):
    return {"key": key, "zh": zh, "en": en, "role": role, **({"unit": unit} if unit else {})}


def table(name):
    return yaml.safe_load((TABLES / (name + ".yaml")).read_text(encoding="utf-8"))


def src_keys(s):
    return [x for x in re.split(r"[,+ ]+", str(s or "")) if x]


def src_url(t, keys):
    by = {s["key"]: s["url"] for s in t["sources"]}
    return " ; ".join(by[k] for k in keys if k in by)


def sources(t):
    return [{"title": s["title"], "url": s["url"], "retrieved": RETRIEVED, **({"note": s["note"]} if s.get("note") else {})}
            for s in t["sources"]]


FAMILIES = {
    "A-BSC-SFU": {
        "table": "bsc_sfu", "name": {"zh": "滚珠丝杠副（法兰单螺母 SFU）", "en": "Ball screw with flanged single nut (SFU)"},
        "category": "BSC", "tags": ["滚珠丝杠", "丝杠", "直线传动", "ball screw", "SFU"],
        "standards": [{"code": "GB/T 17587.2", "title": "滚珠丝杠副 第2部分：公称直径和公称导程 公制系列"},
                      {"code": "ISO 3408-2", "title": "Ball screws — Nominal diameters and nominal leads — Metric series"},
                      {"code": "DIN 69051-5", "title": "Ball screws — Dimensions for flanged ball nuts (form B)"}],
        "params": [P("d0_mm", "公称直径 d0", "Nominal diameter d0", "key", "mm"), P("Ph_mm", "导程 Ph", "Lead Ph", "key", "mm"),
                   P("Dw_mm", "钢球直径", "Ball diameter", "dim", "mm"), P("D_mm", "螺母外径 D", "Nut diameter D", "dim", "mm"),
                   P("L_mm", "螺母长度 L（含法兰）", "Nut length L", "dim", "mm"), P("D1_mm", "法兰外径 D1", "Flange diameter D1", "dim", "mm"),
                   P("L1_mm", "法兰厚度", "Flange thickness", "dim", "mm"), P("D5_mm", "螺栓孔分布圆直径", "Bolt circle diameter", "dim", "mm"),
                   P("X_mm", "法兰安装孔直径", "Flange hole diameter", "dim", "mm"), P("W_mm", "法兰切边宽度", "Flange flat width", "dim", "mm"),
                   P("n_holes", "法兰孔数", "Flange holes", "dim"), P("circuits", "滚珠循环圈数", "Ball circuits", "info"),
                   P("Ca_N", "额定动载荷 Ca", "Dynamic load rating Ca", "perf", "N"), P("C0a_N", "额定静载荷 C0a", "Static load rating C0a", "perf", "N"),
                   P("tbi_model", "样本型号（TBI）", "Catalog model (TBI)", "info")],
        "size": lambda r: "{}x{}".format(mm(r["d0_mm"]), mm(r["Ph_mm"])), "default": "16x5",
        "engine": "wenquest:ball_screw", "origin": "丝杠轴线沿 Z，螺母法兰端面在 z=0；丝杠长度为示意（3×螺母长 + 2×d0）",
        "principle": "丝杠与螺母的螺旋滚道之间装满钢球，转动丝杠时钢球滚动并经螺母内的循环通道返回，把旋转变成直线移动；滚动摩擦使效率达 90% 以上，可加预紧消除间隙，定位精度高。",
        "uses": ["数控机床进给轴", "直角坐标机器人与模组", "精密升降台"], "chapter": "螺旋传动与滚珠丝杠",
        "notes": "螺母外形与载荷取 TBI MOTION SFNU/SFU（DIN 69051 B 型）样本，载荷由 kgf 按 9.80665 换算；外形与 HIWIN FSI 互核一致（25×10 法兰厚 TBI 12、HIWIN 10，按 TBI）；12×4 属 ISO 3408-2 表 2（非优选组合），DIN 69051-5 从 d0=16 起，12×4 外形按 TBI；20×10 两份 HIWIN 资料长度不一、TBI 无载荷，未收。不同厂家的螺母长度与载荷不同，选型以所购厂家样本为准。"},
    "A-LGD-RAIL": {
        "table": "lgd_rail", "name": {"zh": "滚动直线导轨副（HG 型）", "en": "Linear guideway (HG type)"},
        "category": "LGD", "tags": ["直线导轨", "导轨", "滑块", "linear guide", "HIWIN HG"],
        "standards": [{"code": "行业通用尺寸", "title": "四列钢球方形导轨 15～45（HIWIN HG 系列；安装尺寸与 THK HSR 互换）"}],
        "params": [P("rail_W_mm", "导轨宽 WR", "Rail width WR", "dim", "mm"), P("rail_H_mm", "导轨高 HR", "Rail height HR", "dim", "mm"),
                   P("rail_pitch_mm", "导轨安装孔距 P", "Rail hole pitch P", "dim", "mm"), P("rail_E_mm", "孔距端距 E", "Rail end distance E", "dim", "mm"),
                   P("rail_bolt", "导轨螺栓", "Rail bolt", "dim"), P("rail_d_mm", "导轨孔径 d", "Rail hole d", "dim", "mm"),
                   P("rail_D_mm", "沉头孔径 D", "Counterbore D", "dim", "mm"), P("rail_h_mm", "沉头孔深 h", "Counterbore depth h", "dim", "mm"),
                   P("H_mm", "组件高度 H", "Assembly height H", "dim", "mm"), P("H1_mm", "滑块底面间隙 H1", "Clearance H1", "dim", "mm"),
                   P("N_mm", "导轨侧到滑块侧 N", "Rail to block side N", "dim", "mm"), P("W_mm", "滑块宽 W", "Block width W", "dim", "mm"),
                   P("B_mm", "安装孔横向距 B", "Mounting B", "dim", "mm"), P("C_mm", "安装孔纵向距 C", "Mounting C", "dim", "mm"),
                   P("L1_mm", "滑块本体长 L1", "Block body length L1", "dim", "mm"), P("L_mm", "滑块总长 L", "Block length L", "dim", "mm"),
                   P("block_bolt", "滑块安装螺纹", "Block mounting thread", "dim"),
                   P("C_N", "额定动载荷 C", "Dynamic load rating C", "perf", "N"), P("C0_N", "额定静载荷 C0", "Static load rating C0", "perf", "N"),
                   P("block_mass_kg", "滑块质量", "Block mass", "info", "kg"), P("rail_mass_kg_per_m", "导轨每米质量", "Rail mass per metre", "info", "kg/m")],
        "size": lambda r: r["size"], "default": "HGH20CA",
        "engine": "wenquest:linear_guide", "origin": "导轨底面中心在原点，导轨沿 X，滑块居中；导轨长度为示意（取孔距的整数倍）",
        "principle": "滑块里的四列钢球在导轨的四条滚道上滚动并循环，滑块沿导轨直线移动，摩擦小、刚度高，能承受上下左右各方向的载荷和力矩。",
        "uses": ["直角坐标机器人的各轴", "数控机床工作台", "自动化设备的直线模组"], "chapter": "直线导轨与直线运动单元",
        "notes": "按 HIWIN HG 系列（现行官网参数；额定载荷比 2013 版样本高，按官网）；安装尺寸（H、W、B×C、螺纹、导轨宽与孔距）与 THK HSR 一致可互换，但滑块长度和导轨高度略有不同，导轨与滑块须同一家配对。行业标准 JB/T 7175 的尺寸未取得可读文本。"},
    "A-PUL-HTD": {
        "table": "pul_htd", "name": {"zh": "同步带轮（GT2 / HTD 3M / HTD 5M）", "en": "Timing pulley (GT2 / HTD 3M / HTD 5M)"},
        "category": "PUL", "tags": ["同步带轮", "带轮", "同步带", "timing pulley", "GT2", "HTD"],
        "standards": [{"code": "ISO 13050", "title": "Synchronous belt drives — Metric pitch, curvilinear profile systems（HTD 3M、5M）"},
                      {"code": "JB/T 7512.2", "title": "圆弧齿同步带传动 带轮（轮槽尺寸）"},
                      {"code": "Gates PowerGrip GT2", "title": "GT2 齿形（Gates 专有，2 mm 节距）"}],
        "params": [P("profile", "齿形", "Profile", "key"), P("z", "齿数", "Teeth", "key"), P("b_mm", "带宽", "Belt width", "key", "mm"),
                   P("p_mm", "节距", "Pitch", "dim", "mm"), P("PD_mm", "节圆直径 PD = z·p/π", "Pitch diameter", "dim", "mm"),
                   P("OD_mm", "齿顶圆直径 OD = PD − 2δ", "Outside diameter", "dim", "mm"), P("delta_mm", "节线差 δ", "Pitch line differential", "dim", "mm"),
                   P("groove_depth_mm", "轮槽深", "Groove depth", "dim", "mm"), P("groove_r_mm", "轮槽圆弧半径", "Groove radius", "dim", "mm"),
                   P("z_min", "推荐最少齿数", "Recommended min teeth", "info")],
        "default": "GT2-20-6", "engine": "wenquest:timing_pulley",
        "origin": "带轮轴线沿 Z，轮毂端面在 z=0；轮毂、挡边和孔径为常见比例示意",
        "principle": "带内侧的齿与带轮轮槽啮合传动，不打滑、传动比准确；节圆直径 = 齿数 × 节距 ÷ π，齿顶圆比节圆小两个节线差。GT2、HTD 的圆弧齿比梯形齿应力集中小、回差小。",
        "uses": ["3D 打印机与小型直角坐标机构（GT2）", "机器人关节与伺服减速传动（HTD 3M、5M）", "输送线"], "chapter": "带传动（同步带）",
        "notes": "规格按公式由齿形常数生成：PD = z·p/π，OD = PD − 2δ；与 Gates 样本 9 个表列值核对（3M 60 齿 OD 差 0.01 mm，为样本先按英寸取整）。GT2 的轮槽是 Gates 专有，公开资料不给，造型按近似圆弧（深 0.75、半径 0.555）示意；3M、5M 轮槽深与圆弧半径取 JB/T 7512.2 转载值。z_min 是低速（3M、5M ≤900 r/min；GT2 1160 r/min）时的推荐值，转速高要更多齿。"},
    "A-CPL-JAW": {
        "table": "cpl_jaw", "name": {"zh": "梅花形弹性联轴器（LM 基本型）", "en": "Plum-blossom elastic coupling, type LM"},
        "category": "CPL", "tags": ["联轴器", "弹性联轴器", "梅花联轴器", "coupling", "jaw coupling"],
        "standards": [{"code": "GB/T 5272-2002", "title": "梅花形弹性联轴器（尺寸表；现行版 2017 的表未取得可读文本）"}],
        "params": [P("Tn_a_Nm", "公称转矩（a 型弹性件）", "Nominal torque (element a)", "perf", "N·m"),
                   P("Tn_b_Nm", "公称转矩（b 型弹性件）", "Nominal torque (element b)", "perf", "N·m"),
                   P("n_max_rpm", "许用转速", "Allowable speed", "perf", "r/min"), P("d_min_mm", "轴孔直径最小", "Min bore", "dim", "mm"),
                   P("d_max_mm", "轴孔直径最大", "Max bore", "dim", "mm"), P("d_series", "轴孔直径与长度分档", "Bore series", "dim"),
                   P("L_mm", "半联轴器轴孔长（推荐）", "Hub bore length (recommended)", "dim", "mm"),
                   P("L0_mm", "联轴器总长", "Overall length", "dim", "mm"), P("D_mm", "外径", "Outer diameter", "dim", "mm"),
                   P("mass_kg", "质量（近似）", "Mass (approx.)", "info", "kg"), P("J_kgm2", "转动惯量（近似）", "Moment of inertia (approx.)", "info", "kg·m²")],
        "size": lambda r: r["size"], "default": "LM3", "engine": "wenquest:jaw_coupling",
        "origin": "联轴器轴线沿 Z，一端轮毂端面在 z=0",
        "principle": "两个带凸爪的半联轴器之间夹一个梅花形弹性件，转矩经凸爪挤压弹性件传递；弹性件能补偿两轴少量的径向、角向偏差，并缓冲振动，不用润滑。",
        "uses": ["电机与减速器、泵的联接", "伺服电机与丝杠的联接", "减速器输入轴"], "chapter": "联轴器",
        "notes": "按 GB/T 5272-2002 LM 基本型（两处转载互核）；2017 版的尺寸表只有图片，未用。LM13 一行原表“公称转矩 b”印为 2000（小于 a 档 11200，明显漏位），未收。公称转矩按两种弹性件（a、b）分列；最大转矩、弹性件型号两处转载读不到，未收。"},
    "A-SPR-CMP": {
        "table": "spr_cmp", "name": {"zh": "圆柱螺旋压缩弹簧（YA 型）", "en": "Cylindrical helical compression spring, type YA"},
        "category": "SPR", "tags": ["弹簧", "压缩弹簧", "螺旋弹簧", "compression spring"],
        "standards": [{"code": "GB/T 2089-2009", "title": "普通圆柱螺旋压缩弹簧尺寸及参数（两端圈并紧磨平或制扁）"}],
        "params": [P("d_mm", "材料直径 d", "Wire diameter d", "key", "mm"), P("D_mm", "弹簧中径 D", "Mean diameter D", "key", "mm"),
                   P("H0_mm", "自由高度 H0", "Free length H0", "key", "mm"), P("n", "有效圈数 n", "Active coils n", "dim"),
                   P("Fs_N", "最大工作负荷 Fn", "Max working load Fn", "perf", "N"), P("fs_mm", "最大工作变形量", "Max working deflection", "perf", "mm"),
                   P("k_N_per_mm", "刚度", "Spring rate", "perf", "N/mm")],
        "size": lambda r: r["size"], "default": "1.6x12x32", "engine": "wenquest:compression_spring",
        "mesh": {"lin_mm": 0.05, "ang_rad": 0.5},          # 细长螺旋：网格放粗（STL 约 0.3～0.5 MB）
        "origin": "弹簧轴线沿 Z，底面在 z=0；两端各一圈并紧（简化为端部节距等于线径）",
        "principle": "压缩时簧丝主要受扭转，刚度 k = G·d⁴ /(8·D³·n)：线径越粗刚度越大，中径越大、有效圈数越多刚度越小；YA 型两端圈并紧磨平，端面平整，受力均匀。",
        "uses": ["安全阀、离合器的压紧", "机构复位与缓冲", "机器人夹爪的回位"], "chapter": "弹簧",
        "notes": "收 d = 0.5、0.8、1、1.6、6、10 mm 六档（每个 d×D 收标准表的 6 个有效圈数）；表里刚度按 G ≈ 79 000 N/mm² 计算，测试按公式逐行核对。负荷 Fn 为标准表“最大工作负荷”。d = 1 的 D 4.5～8、d = 2.5、d = 4 等档转载表读取错位，未收；少数行变形量与 负荷÷刚度 差 4～8%（原表如此），照录。"},
}


def pulley_rows(t):
    rows = []
    for c in t["rows"]:
        prof = c["size"]
        g = dict(c)
        if prof == "GT2":
            g.update(GT2_GROOVE)
        for z in PULLEY_Z[prof]:
            for b in PULLEY_B[prof]:
                PD = z * c["p_mm"] / math.pi
                rows.append({"size": "{}-{}-{}".format(prof, z, b), "src": c["src"], "profile": prof, "z": z, "b_mm": b,
                             "p_mm": c["p_mm"], "PD_mm": round(PD, 3), "OD_mm": round(PD - 2 * c["delta_mm"], 3),
                             "delta_mm": c["delta_mm"], "groove_depth_mm": g["groove_depth_mm"], "groove_r_mm": g["groove_r_mm"],
                             "z_min": c["z_min"]})
    return rows


def entry_doc(eid, f, t):
    return {
        "schema": 1, "id": eid, "kind": "family", "name": f["name"], "category": f["category"], "tags": f["tags"],
        "standards": f["standards"], "params": f["params"], "specs": "specs.csv", "default": f["default"],
        "model": {"engine": f["engine"], "formats": ["step", "stl", "glb"], "origin": f["origin"],
                  **({"mesh": f["mesh"]} if f.get("mesh") else {})},
        "source": {"origin": "wenquest", "license": LICENSE, "attribution": ATTR,
                   "checked": {"by": "Claude", "on": RETRIEVED, "note": "尺寸表两次独立读取一致，另抽查核对；测试逐行核对公式与单调性"},
                   "data_sources": sources(t), "notes": f["notes"]},
        "teaching": {"principle": f["principle"], "uses": f["uses"],
                     "courses": [{"course": "机械设计基础", "chapter": f["chapter"]}], "labs": []},
        "factory": {"erp_items": [], "suppliers": []},
    }


def main():
    for eid, f in FAMILIES.items():
        t = table(f["table"])
        rows = pulley_rows(t) if eid == "A-PUL-HTD" else [dict(r, size=f["size"](r)) for r in t["rows"]]
        keys = [p["key"] for p in f["params"]]
        out = []
        for r in rows:
            out.append([r["size"]] + ["" if r.get(k) is None else (mm(r[k]) if isinstance(r[k], (int, float)) and not isinstance(r[k], bool) else r[k])
                                      for k in keys] + [src_url(t, src_keys(r.get("src")))])
        write(eid, ["size"] + keys + ["src_url"], out)
        d = CATALOG / "A" / eid
        (d / "entry.yaml").write_text("# {} · {}（第 5 轮第 5 步，P7）\n".format(eid, f["name"]["zh"])
                                      + yaml.safe_dump(entry_doc(eid, f, t), allow_unicode=True, sort_keys=False), encoding="utf-8")
        print(eid, len(out))


if __name__ == "__main__":
    main()
