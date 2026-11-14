"""第 138 轮 G7.1：由设计生成 WQ-LS 8 种变型的物料清单（BOM），写进问渠缝纫机厂。

    python3 tools/wqls/g7_bom.py            → docs/设计/WQ-LS/G7/物料清单.json，并改 factory/plants/wenquest-sewing.yaml 里的生成段
    python3 tools/wqls/g7_bom.py --check    → 只核对：工厂清单里的生成段与设计一致吗（0 差异才通过；数字工厂测试调用它）

来源（都在仓库里）：
  - 三维零件和它们在哪些变型里：factory/digital/web/public/wqls/machine.json（g6_web.py 由 cad/mech.py 生成）
  - 物料号、名称、自制 / 外购：tools/wqls/part_codes.yaml
  - 三维里没有、整机要的（电控箱、针板、盖板、螺钉、包装、上轴后轴承……）：本文件 EXTRA，每一行写了理由
变型：T 自动剪线、E 电子针距、D 少油旋梭，型号 WQ-LS[-T][E][D]；D 只把旋梭 LS-301 换成镀 DLC 的 LS-301D。
旋梭外购（Eddie 11-13 定）：LS-301D 是新的外购件；工厂里 LS-301 现在还是自制件，G7.2 改成外购、去掉旋梭线。
单价是示例值（工厂清单本来就是示例数据）：外协件按质量粗估，见 price()。
工厂清单里由本程序写的段落夹在“# >>> g7_bom”和“# <<< g7_bom”之间，别手改；其余部分照旧手工维护。
"""
from __future__ import annotations

import itertools
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PLANT = ROOT / "factory" / "plants" / "wenquest-sewing.yaml"
MACHINE = ROOT / "factory" / "digital" / "web" / "public" / "wqls" / "machine.json"
OUT = ROOT / "docs" / "设计" / "WQ-LS" / "G7" / "物料清单.json"
ASSY = "RT-平缝机总装 LS assembly"
BASE_PRICE = 520                       # 工厂清单里 WQ-LS 原来的售价（示例）
OPT_PRICE = {"T": 90, "E": 70, "D": 15}   # 选项加价（示例）

# 三维里没有、整机要的物料（所有变型都有）：(物料号, 数量, 理由)
EXTRA = [
    ("BUY-BRG-6201", 1, "上轴后轴承 6201（spec.BRG；三维只画了前轴承 6202）"),
    ("BUY-CTRL-LS", 1, "电控箱（GC 设计，外购）"),
    ("BUY-PLATE-LS", 1, "针板与推板（三维没有画）"),
    ("BUY-OILPAN-LS", 1, "油盘"),
    ("BUY-COVERS-LS", 1, "面板、后盖、顶盖（G3 定了做法，三维没有画）"),
    ("BUY-SCREW-M5", 40, "内六角螺钉 M5（数量为示例）"),
    ("BUY-SCREW-M4", 20, "螺钉 M4（数量为示例）"),
    ("BUY-BOX-LS", 1, "包装箱与附件包"),
]
# 新物料（工厂清单里还没有的）的说明：编码 → (中英文名, 供应商, 示例单价 / None = 按质量估)
NEW_BUY = {
    "BUY-BRG-6201": ("深沟球轴承 6201 Ball bearing 12×32×10", "hardware", 1.2),
    "BUY-BRG-6202": ("深沟球轴承 6202 Ball bearing 15×35×11", "hardware", 1.5),
    "BUY-PLATE-LS": ("平缝机针板与推板（型号待确认） Throat plate & slide plate", "sewparts", 3.0),
    "BUY-SOL-TRIM": ("剪线电磁铁 24 V Ø22（型号待确认） Trimmer solenoid", "drive", 6.0),
    "BUY-SOL-WIPE": ("拨线电磁铁 24 V Ø16（型号待确认） Wiper solenoid", "drive", 4.5),
    "BUY-SOL-REL": ("松线电磁铁 24 V Ø16（型号待确认） Tension-release solenoid", "drive", 4.5),
    "BUY-STEP-42": ("42 步进电机 48 mm 带磁编码器（型号待确认） NEMA 17 stepper with encoder", "drive", 15.0),
    "BUY-BELT-E": ("同步带 HTD 3M 宽 9（型号待确认） Timing belt HTD 3M 9 mm", "sewparts", 1.5),
    "BUY-BTN-E": ("倒缝按钮（型号待确认） Reverse push-button", "drive", 1.0),
    "LS-301D": ("旋梭（少油型，梭床和梭尖镀 DLC；外购） Rotary hook, low-oil (DLC-coated, bought)", "sewparts", 8.0),
}
# 新的自制件：编码 → (中英文名, 工艺路线, 原材料, 用量)
NEW_MAKE = {
    "LS-402": ("抬牙偏心 Lift eccentric", "RT-偏心 Eccentric", "RM-20CRMNTI-D40", 0.2),
    "LS-710": ("剪线凸轮 Trimmer cam", "RT-偏心 Eccentric", "RM-20CRMNTI-D40", 0.3),
}
# 工厂清单里已有、名称要跟设计对上的物料（只改名称）
RENAME = {"LS-401": "送布偏心 Feed eccentric"}


def variants():
    for t, e, d in itertools.product((False, True), repeat=3):
        tag = ("T" if t else "") + ("E" if e else "") + ("D" if d else "")
        yield ("WQ-LS-" + tag if tag else "WQ-LS"), dict(T=t, E=e, D=d)


def present(need, o):
    return {None: True, "T": o["T"], "E": o["E"], "!E": not o["E"]}[need]


def price(kind_parts, mass_g):
    """外协按图的件：加工费按质量粗估（示例值）：1 美元起，每千克 30 美元。"""
    return round(1.0 + 0.03 * mass_g, 2)


def build():
    M = json.loads(MACHINE.read_text(encoding="utf-8"))
    C = yaml.safe_load((HERE / "part_codes.yaml").read_text(encoding="utf-8"))
    names = {k: f"{v[0]} {v[1]}" for k, v in C.get("assemblies", {}).items()}
    out = {}
    for model, o in variants():
        lines = {}
        for k, p in M["parts"].items():
            if not present(p.get("need"), o):
                continue
            code = p.get("of") or p["code"]
            if code == "LS-301" and o["D"]:
                code = "LS-301D"
            ln = lines.setdefault(code, dict(code=code, qty=0, parts=[], kind="make" if p.get("of") else p["kind"],
                                             name=names.get(code) or f"{p['name'][0]} {p['name'][1]}", mass_g=0.0))
            ln["parts"].append(k)
            ln["mass_g"] += p["mass_g"]
            if code.startswith("BUY-MOTOR") and len(ln["parts"]) > 1:
                continue                                     # 电机的 9 个零件是一台电机
            if p.get("of") and len(ln["parts"]) > 1:
                continue                                     # 机壳上下件合起来是一件 HSG-LS
            ln["qty"] += p.get("qty", 1)
        for code, q, why in EXTRA:
            if code in lines:
                lines[code]["qty"] += q
                lines[code]["extra"] = why
            else:
                lines[code] = dict(code=code, qty=q, parts=[], kind="buy", name=why, extra=why, mass_g=0.0)
        price_ = BASE_PRICE + sum(v for k, v in OPT_PRICE.items() if o[k])
        out[model] = dict(options=o, price=price_, lines=sorted(lines.values(), key=lambda x: x["code"]))
    return out


def plant_blocks(B):
    """工厂清单里的四段：物料、BOM、成品、期初库存。"""
    hand = re.sub(r"[ ]*" + re.escape(MARK[0]) + r".*?" + re.escape(MARK[1]) + r"[^\n]*\n", "", PLANT.read_text(encoding="utf-8"), flags=re.S)
    P = yaml.safe_load(hand)                                 # 只看手工维护的部分（生成段每次重写）
    have = {i["code"] for i in P["items"]}
    gen_codes = set()
    items = []
    seen = {}
    for b in B.values():
        for ln in b["lines"]:
            seen.setdefault(ln["code"], ln)
    for code, ln in sorted(seen.items()):
        if code in have and code not in RENAME:
            continue
        gen_codes.add(code)
        if code in NEW_MAKE:
            items.append(dict(code=code, name=NEW_MAKE[code][0], kind="make", uom="Nos"))
        elif code in NEW_BUY:
            nm, sup, pr = NEW_BUY[code]
            items.append(dict(code=code, name=nm, kind="buy", uom="Nos", price=pr, supplier=sup))
        elif code in RENAME:
            continue
        else:
            assert ln["kind"] == "buy" and code.startswith("LS-"), f"{code} 不知道怎么写进工厂清单"
            items.append(dict(code=code, name=f"{ln['name']}（按图外协）", kind="buy", uom="Nos",
                              price=price(ln["parts"], ln["mass_g"] / max(1, ln["qty"]) if ln["qty"] else ln["mass_g"]),
                              supplier="sewparts", note="WQ-LS 设计件，按我们的图纸外协加工或外购（单价按质量粗估，示例）"))
    boms = []
    for model, b in B.items():
        boms.append(dict(item=model, routing=ASSY, components=[[ln["code"], ln["qty"]] for ln in b["lines"]]))
    for code, (nm, rt, rm, q) in NEW_MAKE.items():
        boms.append(dict(item=code, routing=rt, components=[[rm, q]]))
    fgs = [dict(code=m, name=f"问渠工业直驱平缝机 {m}（示例）Direct-drive lockstitch machine {m}", kind="fg", uom="Nos")
           for m in B if m != "WQ-LS"]
    products = [dict(item=m, price=b["price"]) for m, b in B.items() if m != "WQ-LS"]
    opening = {}
    for code in sorted(gen_codes):
        it = next(i for i in items if i["code"] == code) if any(i["code"] == code for i in items) else None
        if it and it["kind"] == "buy":
            opening[code] = 20 * max(next((ln["qty"] for ln in b["lines"] if ln["code"] == code), 0) for b in B.values())
    return dict(items=fgs + items, boms=boms, products=products, opening=opening)


MARK = ("# >>> g7_bom：tools/wqls/g7_bom.py 生成（第 138 轮 G7.1），别手改", "# <<< g7_bom")


def dump_list(lst, indent=""):
    s = yaml.safe_dump(lst, allow_unicode=True, sort_keys=False, width=200, default_flow_style=None)
    return "".join(indent + ln + "\n" for ln in s.splitlines())


def render(text, blocks):
    """把四段写进工厂清单的文字（保留其余内容和注释）。"""
    def put(text, section, body, anchor_before, indent=""):
        tag0, tag1 = f"{indent}{MARK[0]}（{section}）", f"{indent}{MARK[1]}（{section}）"
        blk = tag0 + "\n" + body + tag1 + "\n"
        pat = re.compile(re.escape(tag0) + r".*?" + re.escape(tag1) + r"\n", re.S)
        if pat.search(text):
            return pat.sub(lambda _: blk, text)
        i = text.index(anchor_before) + (1 if anchor_before.startswith("\n") else 0)
        return text[:i] + blk + text[i:]
    # 原来手写的 WQ-LS BOM（示意）拿掉，由生成段代替
    text = re.sub(r"^- item: WQ-LS\n  routing: RT-平缝机总装 LS assembly\n  components:\n(?:  - - .*\n    - .*\n)+", "", text, flags=re.M)
    for code, nm in RENAME.items():
        text = re.sub(rf"^(- code: {re.escape(code)}\n  name: ).*$", lambda m: m.group(1) + nm, text, flags=re.M)
    text = put(text, "物料", dump_list(blocks["items"]), "\nroutings:\n")
    text = put(text, "BOM", dump_list(blocks["boms"]), "\nproducts:\n")
    text = put(text, "成品", dump_list(blocks["products"]), "\nstock:\n")
    op = "".join(f"    {k}: {v}\n" for k, v in blocks["opening"].items())
    text = put(text, "期初库存", op, "  safety:\n", indent="    ")
    return text


def check():
    """工厂清单与设计的差异（空 = 一致）。"""
    B = build()
    P = yaml.safe_load(PLANT.read_text(encoding="utf-8"))
    boms = {b["item"]: {c[0]: c[1] for c in b["components"]} for b in P["boms"]}
    items = {i["code"] for i in P["items"]}
    diff = []
    for model, b in B.items():
        want = {ln["code"]: ln["qty"] for ln in b["lines"]}
        got = boms.get(model)
        if got is None:
            diff.append(f"{model}：工厂清单里没有 BOM")
            continue
        for c in sorted(set(want) | set(got)):
            if want.get(c) != got.get(c):
                diff.append(f"{model} {c}：设计 {want.get(c)}，工厂 {got.get(c)}")
        diff += [f"{model}：{c} 不在工厂物料里" for c in want if c not in items]
    # 三维零件都进了 BOM：每个零件至少在一种变型里出现
    M = json.loads(MACHINE.read_text(encoding="utf-8"))
    used = {k for b in B.values() for ln in b["lines"] for k in ln["parts"]}
    diff += [f"三维零件 {k} 不在任何一份 BOM 里" for k in M["parts"] if k not in used]
    return diff


def main():
    if "--check" in sys.argv:
        d = check()
        print("\n".join(d) if d else "0 差异")
        sys.exit(1 if d else 0)
    B = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(dict(note="WQ-LS 8 种变型的物料清单，由 tools/wqls/g7_bom.py 从设计生成；单价、选项加价是示例值",
                                   variants=B), ensure_ascii=False, indent=1), encoding="utf-8")
    PLANT.write_text(render(PLANT.read_text(encoding="utf-8"), plant_blocks(B)), encoding="utf-8")
    for m, b in B.items():
        print(m, len(b["lines"]), "行", sum(1 for ln in b["lines"] if ln["kind"] == "make"), "种自制", b["price"], "美元")
    d = check()
    print("核对：", "0 差异" if not d else d)


if __name__ == "__main__":
    main()
